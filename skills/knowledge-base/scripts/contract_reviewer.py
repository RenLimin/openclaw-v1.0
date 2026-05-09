#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同审核引擎 - 专项规则审核接口
================================
基于合同审核专项规则库，实现合同条款的自动审核

功能:
  - 单条款专项审核
  - 全合同批量审核
  - 自动关联法条依据
  - 生成结构化审核报告
  - 风险分级统计

依赖:
  - law_query.py: 法条查询引擎
  - product_query.py: 产品匹配引擎

作者: Jerry 🦞
版本: v1.0
日期: 2026-04-24
"""

import os
import re
import sys
import json
import argparse
import yaml
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# 添加当前目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent))

try:
    from law_query import LawQuery, RiskItem, ReviewResult, Colors
except ImportError:
    # 定义本地数据结构
    @dataclass
    class RiskItem:
        type: str
        description: str
        severity: str
        law_basis: Dict
        suggestion: str

    @dataclass
    class ReviewResult:
        score: int
        risk_level: str
        risks: List[RiskItem]
        matched_articles: List[str]
        summary: str

    class Colors:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'


@dataclass
class ReviewIssue:
    """审核发现的问题"""
    rule_id: str
    rule_name: str
    severity: str
    description: str
    location: str
    law_basis: List[Dict]
    suggestion: str
    matched_text: str


@dataclass
class ReviewReport:
    """审核报告"""
    contract_name: str
    review_date: str
    total_score: int
    conclusion: str
    conclusion_label: str
    risk_summary: Dict[str, int]
    issues: List[ReviewIssue]
    statistics: Dict[str, Any]
    recommendations: List[str]


class ContractReviewer:
    """合同审核引擎类"""
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        初始化审核引擎
        
        Args:
            base_path: 知识库根目录路径
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent
        
        self.base_path = Path(base_path)
        self.rules = self._load_rules()
        self.law_query = self._init_law_query()
        self.scoring_config = self.rules.get('risk_scoring', {})
        self.report_spec = self.rules.get('report_spec', {})
        
    def _load_rules(self) -> Dict:
        """加载审核规则库"""
        rules_path = self.base_path / 'data' / 'review-rules' / 'contract-review-rules.yaml'
        if not rules_path.exists():
            raise FileNotFoundError(f"规则文件不存在: {rules_path}")
        
        with open(rules_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _init_law_query(self) -> Optional[Any]:
        """初始化法条查询引擎"""
        try:
            return LawQuery(self.base_path)
        except Exception as e:
            print(f"警告: 法条查询引擎初始化失败 ({e})，将使用基础法条映射")
            return None
    
    def _get_severity_score(self, severity: str) -> int:
        """获取风险等级对应的分数"""
        levels = self.scoring_config.get('levels', {})
        for level_name, level_config in levels.items():
            if level_name == severity or level_config.get('label') == severity:
                return level_config.get('score', 0)
        return 0
    
    def _determine_conclusion(self, total_score: int) -> Tuple[str, str]:
        """根据总分确定审核结论"""
        thresholds = self.scoring_config.get('thresholds', {})
        reject_threshold = thresholds.get('reject_threshold', 20)
        attention_threshold = thresholds.get('attention_threshold', 10)
        
        if total_score >= reject_threshold:
            return "REJECT", "建议退回修改"
        elif total_score >= attention_threshold:
            return "ATTENTION", "需重点关注"
        else:
            return "PASS", "审核通过"
    
    def _get_law_articles(self, article_ids: List[str]) -> List[Dict]:
        """获取法条详情"""
        if not article_ids:
            return []
        
        if self.law_query:
            articles = []
            for article_id in article_ids:
                try:
                    article = self.law_query.query_by_id(article_id)
                    if article:
                        articles.append({
                            'id': article_id,
                            'title': article.get('title', ''),
                            'content': article.get('content', '')[:100] + '...' if article.get('content') else ''
                        })
                except Exception:
                    articles.append({'id': article_id, 'title': '', 'content': '法条详情需查询'})
            return articles
        else:
            return [{'id': aid, 'title': '民法典相关条款', 'content': ''} for aid in article_ids]
    
    def _apply_pattern_check(self, text: str, check: Dict) -> Optional[ReviewIssue]:
        """应用正则模式检查"""
        pattern = check.get('pattern')
        negative_pattern = check.get('negative_pattern')
        
        if not pattern:
            return None
        
        try:
            # 查找匹配
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if not match:
                return None
            
            # 检查排除模式
            if negative_pattern:
                neg_match = re.search(negative_pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                if neg_match:
                    return None
            
            # 构造问题
            severity = check.get('severity', 'low')
            law_articles = self._get_law_articles(check.get('law_articles', []))
            
            # 获取建议模板
            suggestion_templates = self.report_spec.get('suggestion_template', {})
            template = suggestion_templates.get(severity, '{suggestion}')
            formatted_suggestion = template.format(suggestion=check.get('suggestion', ''))
            
            return ReviewIssue(
                rule_id=check.get('id', ''),
                rule_name=check.get('name', ''),
                severity=severity,
                description=check.get('description', ''),
                location=match.group(0)[:50] + '...' if len(match.group(0)) > 50 else match.group(0),
                law_basis=law_articles,
                suggestion=formatted_suggestion,
                matched_text=match.group(0)
            )
            
        except re.error as e:
            print(f"正则表达式错误: {check.get('id')} - {e}")
            return None
    
    def review_clause(self, clause_text: str, clause_type: str = "general") -> List[ReviewIssue]:
        """
        单条款专项审核
        
        Args:
            clause_text: 条款文本内容
            clause_type: 条款类型 (RVW-01, RVW-02, RVW-03, RVW-04, general)
        
        Returns:
            发现的问题列表
        """
        issues = []
        
        # 确定需要应用的规则
        special_rules = self.rules.get('special_rules', {})
        general_rules = self.rules.get('general_rules', {})
        
        # 专项规则审核
        if clause_type in special_rules:
            rule_config = special_rules[clause_type]
            checks = rule_config.get('checks', [])
            for check in checks:
                issue = self._apply_pattern_check(clause_text, check)
                if issue:
                    issues.append(issue)
        
        # 通用规则审核
        if clause_type == 'general' or True:  # 始终应用通用规则
            # RVW-98 歧义表述检查
            rvw98 = general_rules.get('RVW-98', {})
            for pattern_check in rvw98.get('ambiguity_patterns', []):
                issue = self._apply_pattern_check(clause_text, pattern_check)
                if issue:
                    issues.append(issue)
            
            # RVW-97 免责条款检查
            rvw97 = general_rules.get('RVW-97', {})
            for disclaimer_check in rvw97.get('disclaimer_checks', []):
                issue = self._apply_pattern_check(clause_text, disclaimer_check)
                if issue:
                    issues.append(issue)
        
        return issues
    
    def review_contract(self, contract_text: str, contract_name: str = "未命名合同") -> ReviewReport:
        """
        全合同批量审核
        
        Args:
            contract_text: 完整合同文本
            contract_name: 合同名称
        
        Returns:
            结构化审核报告
        """
        all_issues = []
        
        # 对四大专项规则分别进行审核
        special_rules = self.rules.get('special_rules', {})
        for rule_id, rule_config in special_rules.items():
            checks = rule_config.get('checks', [])
            for check in checks:
                issue = self._apply_pattern_check(contract_text, check)
                if issue:
                    all_issues.append(issue)
        
        # 应用通用规则
        general_rules = self.rules.get('general_rules', {})
        
        # RVW-98 歧义表述检查
        rvw98 = general_rules.get('RVW-98', {})
        for pattern_check in rvw98.get('ambiguity_patterns', []):
            issue = self._apply_pattern_check(contract_text, pattern_check)
            if issue:
                all_issues.append(issue)
        
        # RVW-97 免责条款检查
        rvw97 = general_rules.get('RVW-97', {})
        for disclaimer_check in rvw97.get('disclaimer_checks', []):
            issue = self._apply_pattern_check(contract_text, disclaimer_check)
            if issue:
                all_issues.append(issue)
        
        # RVW-99 条款完整性检查
        rvw99 = general_rules.get('RVW-99', {})
        for clause in rvw99.get('essential_clauses', []):
            pattern = clause.get('pattern', '')
            if pattern:
                match = re.search(pattern, contract_text, re.IGNORECASE)
                if not match:
                    law_articles = self._get_law_articles(clause.get('law_articles', []))
                    issue = ReviewIssue(
                        rule_id=f"RVW-99-{clause.get('name', '')}",
                        rule_name=f"必备条款缺失: {clause.get('name', '')}",
                        severity=clause.get('severity', 'high'),
                        description=f"合同中缺少'{clause.get('name', '')}'条款: {clause.get('description', '')}",
                        location="全文",
                        law_basis=law_articles,
                        suggestion=f"建议补充{clause.get('name', '')}相关条款",
                        matched_text=""
                    )
                    all_issues.append(issue)
        
        # 计算总分
        total_score = sum(self._get_severity_score(issue.severity) for issue in all_issues)
        
        # 确定结论
        conclusion_code, conclusion_label = self._determine_conclusion(total_score)
        
        # 风险统计
        risk_summary = {
            'high': sum(1 for issue in all_issues if issue.severity == 'high'),
            'medium': sum(1 for issue in all_issues if issue.severity == 'medium'),
            'low': sum(1 for issue in all_issues if issue.severity == 'low')
        }
        
        # 生成改进建议
        recommendations = self._generate_recommendations(all_issues)
        
        # 统计信息
        statistics = {
            'total_rules_triggered': len(all_issues),
            'review_duration': 'N/A',
            'special_rule_coverage': {
                'RVW-01': sum(1 for i in all_issues if i.rule_id.startswith('RVW-01')),
                'RVW-02': sum(1 for i in all_issues if i.rule_id.startswith('RVW-02')),
                'RVW-03': sum(1 for i in all_issues if i.rule_id.startswith('RVW-03')),
                'RVW-04': sum(1 for i in all_issues if i.rule_id.startswith('RVW-04'))
            }
        }
        
        return ReviewReport(
            contract_name=contract_name,
            review_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_score=total_score,
            conclusion=conclusion_code,
            conclusion_label=conclusion_label,
            risk_summary=risk_summary,
            issues=all_issues,
            statistics=statistics,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, issues: List[ReviewIssue]) -> List[str]:
        """生成审核改进建议"""
        recommendations = []
        
        # 按严重程度分类建议
        high_count = sum(1 for issue in issues if issue.severity == 'high')
        medium_count = sum(1 for issue in issues if issue.severity == 'medium')
        
        if high_count > 0:
            recommendations.append(
                f"发现 {high_count} 项高风险问题，必须在签署前完成修改"
            )
        
        if medium_count > 3:
            recommendations.append(
                f"发现 {medium_count} 项中等风险问题，建议逐一落实修改"
            )
        
        # 专项建议
        subject_issues = [i for i in issues if i.rule_id.startswith('RVW-01')]
        delivery_issues = [i for i in issues if i.rule_id.startswith('RVW-02')]
        acceptance_issues = [i for i in issues if i.rule_id.startswith('RVW-03')]
        warranty_issues = [i for i in issues if i.rule_id.startswith('RVW-04')]
        
        if len(subject_issues) >= 3:
            recommendations.append("标的条款问题较多，建议重点完善产品名称、规格、技术参数等核心要素")
        
        if len(delivery_issues) >= 3:
            recommendations.append("交付条款存在多处风险，建议明确交付时间、地点、运输责任及逾期责任")
        
        if len(acceptance_issues) >= 3:
            recommendations.append("验收条款不够完善，建议细化验收标准、流程、时限及不合格处理方式")
        
        if len(warranty_issues) >= 3:
            recommendations.append("售后维保条款需完善，建议明确维保期限、范围、响应时间及质保金条款")
        
        return recommendations
    
    def print_report(self, report: ReviewReport, detailed: bool = True):
        """打印审核报告到控制台"""
        # 标题
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}                  合 同 审 核 报 告{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
        
        # 基本信息
        print(f"{Colors.BOLD}合同名称:{Colors.ENDC} {report.contract_name}")
        print(f"{Colors.BOLD}审核时间:{Colors.ENDC} {report.review_date}")
        print()
        
        # 审核结论
        conclusion_colors = {
            'PASS': Colors.GREEN,
            'ATTENTION': Colors.YELLOW,
            'REJECT': Colors.RED
        }
        color = conclusion_colors.get(report.conclusion, '')
        print(f"{Colors.BOLD}审核结论:{Colors.ENDC} {color}{report.conclusion_label}{Colors.ENDC}")
        print(f"{Colors.BOLD}风险评分:{Colors.ENDC} {report.total_score} 分")
        print()
        
        # 风险统计
        print(f"{Colors.BOLD}{'风险统计:'}{Colors.ENDC}")
        print(f"  🔴 高风险: {report.risk_summary['high']} 项")
        print(f"  🟡 中风险: {report.risk_summary['medium']} 项")
        print(f"  🔵 低风险: {report.risk_summary['low']} 项")
        print()
        
        # 改进建议
        if report.recommendations:
            print(f"{Colors.BOLD}{'核心建议:'}{Colors.ENDC}")
            for rec in report.recommendations:
                print(f"  • {rec}")
            print()
        
        # 详细问题列表
        if detailed and report.issues:
            print(f"{Colors.BOLD}{'问题详情:'}{Colors.ENDC}")
            print("-" * 70)
            
            # 按严重程度排序
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            sorted_issues = sorted(report.issues, key=lambda x: severity_order.get(x.severity, 99))
            
            for idx, issue in enumerate(sorted_issues, 1):
                severity_color = {
                    'high': Colors.RED,
                    'medium': Colors.YELLOW,
                    'low': Colors.BLUE
                }.get(issue.severity, Colors.WHITE)
                
                severity_label = {
                    'high': '高风险',
                    'medium': '中风险',
                    'low': '低风险'
                }.get(issue.severity, '未知')
                
                print(f"\n{idx}. [{severity_color}{severity_label}{Colors.ENDC}] {issue.rule_id} - {issue.rule_name}")
                print(f"   描述: {issue.description}")
                
                if issue.location and issue.location != "全文":
                    print(f"   位置: ...{issue.location}...")
                
                if issue.law_basis:
                    law_refs = ", ".join([law['id'] for law in issue.law_basis])
                    print(f"   法条: {law_refs}")
                
                print(f"   建议: {issue.suggestion}")
            
            print()
        
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")
    
    def export_report_json(self, report: ReviewReport, output_path: str):
        """导出审核报告为JSON格式"""
        report_dict = {
            'contract_name': report.contract_name,
            'review_date': report.review_date,
            'total_score': report.total_score,
            'conclusion': report.conclusion,
            'conclusion_label': report.conclusion_label,
            'risk_summary': report.risk_summary,
            'statistics': report.statistics,
            'recommendations': report.recommendations,
            'issues': [
                {
                    'rule_id': issue.rule_id,
                    'rule_name': issue.rule_name,
                    'severity': issue.severity,
                    'description': issue.description,
                    'location': issue.location,
                    'law_basis': issue.law_basis,
                    'suggestion': issue.suggestion
                }
                for issue in report.issues
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
        
        print(f"报告已导出: {output_path}")
    
    def export_report_markdown(self, report: ReviewReport, output_path: str):
        """导出审核报告为Markdown格式"""
        severity_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🔵'
        }
        
        md_lines = [
            "# 合同审核报告\n",
            f"**合同名称:** {report.contract_name}\n",
            f"**审核时间:** {report.review_date}\n",
            f"\n## 审核结论\n",
            f"- **结论:** {report.conclusion_label}\n",
            f"- **风险评分:** {report.total_score} 分\n",
            f"\n## 风险统计\n",
            f"- 🔴 高风险: {report.risk_summary['high']} 项\n",
            f"- 🟡 中风险: {report.risk_summary['medium']} 项\n",
            f"- 🔵 低风险: {report.risk_summary['low']} 项\n",
        ]
        
        if report.recommendations:
            md_lines.append("\n## 核心建议\n")
            for rec in report.recommendations:
                md_lines.append(f"- {rec}\n")
        
        if report.issues:
            md_lines.append("\n## 问题详情\n")
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            sorted_issues = sorted(report.issues, key=lambda x: severity_order.get(x.severity, 99))
            
            for issue in sorted_issues:
                emoji = severity_emoji.get(issue.severity, '⚪')
                md_lines.append(f"\n### {emoji} {issue.rule_id} - {issue.rule_name}\n")
                md_lines.append(f"- **风险等级:** {issue.severity}\n")
                md_lines.append(f"- **问题描述:** {issue.description}\n")
                if issue.location != "全文":
                    md_lines.append(f"- **位置:** ...{issue.location}...\n")
                if issue.law_basis:
                    law_refs = "; ".join([f"{law['id']}" for law in issue.law_basis])
                    md_lines.append(f"- **法条依据:** {law_refs}\n")
                md_lines.append(f"- **优化建议:** {issue.suggestion}\n")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(md_lines)
        
        print(f"报告已导出: {output_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="合同审核引擎")
    parser.add_argument('input', help='待审核合同文件路径')
    parser.add_argument('--output', '-o', help='输出报告文件路径')
    parser.add_argument('--format', '-f', choices=['json', 'md', 'both'], default='md',
                        help='输出格式 (json/md/both)')
    parser.add_argument('--name', '-n', help='合同名称')
    parser.add_argument('--no-detail', action='store_true', help='不显示问题详情')
    parser.add_argument('--clause-type', default='general',
                        choices=['RVW-01', 'RVW-02', 'RVW-03', 'RVW-04', 'general'],
                        help='条款类型（专项审核时使用）')
    parser.add_argument('--clause-only', action='store_true', help='仅审核单条款（输入为条款文本而非文件）')
    
    args = parser.parse_args()
    
    # 初始化审核引擎
    try:
        reviewer = ContractReviewer()
    except Exception as e:
        print(f"{Colors.RED}错误: 审核引擎初始化失败 - {e}{Colors.ENDC}")
        sys.exit(1)
    
    # 审核模式
    if args.clause_only:
        # 单条款审核模式
        clause_text = args.input
        issues = reviewer.review_clause(clause_text, args.clause_type)
        
        print(f"\n{Colors.BOLD}条款审核结果:{Colors.ENDC}")
        print(f"发现 {len(issues)} 个问题\n")
        
        for issue in issues:
            severity_color = {
                'high': Colors.RED,
                'medium': Colors.YELLOW,
                'low': Colors.BLUE
            }.get(issue.severity, Colors.WHITE)
            
            print(f"[{severity_color}{issue.severity}{Colors.ENDC}] {issue.rule_id}: {issue.description}")
            print(f"  建议: {issue.suggestion}\n")
    
    else:
        # 全合同审核模式
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"{Colors.RED}错误: 文件不存在 - {args.input}{Colors.ENDC}")
            sys.exit(1)
        
        with open(input_path, 'r', encoding='utf-8') as f:
            contract_text = f.read()
        
        contract_name = args.name or input_path.stem
        
        # 执行审核
        report = reviewer.review_contract(contract_text, contract_name)
        
        # 打印报告
        reviewer.print_report(report, detailed=not args.no_detail)
        
        # 导出报告
        if args.output:
            output_path = Path(args.output)
            if args.format in ['json', 'both']:
                json_path = output_path.with_suffix('.json') if output_path.suffix != '.json' else output_path
                reviewer.export_report_json(report, str(json_path))
            
            if args.format in ['md', 'both']:
                md_path = output_path.with_suffix('.md') if output_path.suffix != '.md' else output_path
                reviewer.export_report_markdown(report, str(md_path))


if __name__ == "__main__":
    main()
