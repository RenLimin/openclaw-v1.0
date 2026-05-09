#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同法规知识库 - 查询接口
=========================
独立固化的法律法规查询系统，与业务逻辑完全解耦

功能:
  - 按ID查询单条法条
  - 按分类查询法条列表
  - 关键词语义查询
  - 合同条款合规性审查（评分+风险提示+法条依据）

作者: Jerry 🦞
版本: v1.0
日期: 2026-04-24
"""

import os
import re
import sys
import argparse
import yaml
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass

# 颜色输出定义
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# 审查结果数据结构
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


class LawQuery:
    """合同法规知识库查询类"""
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        初始化查询接口
        
        Args:
            base_path: 知识库根目录路径，默认使用脚本所在目录的上级目录
        """
        if base_path is None:
            # 默认使用脚本所在目录的上级目录
            base_path = Path(__file__).parent.parent
        
        self.base_path = Path(base_path)
        self.config = self._load_config()
        self.articles = self._load_all_articles()
        
    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = self.base_path / 'config' / 'query-config.yaml'
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_all_articles(self) -> List[Dict]:
        """加载所有法条数据"""
        articles = []
        
        # 加载民法典合同编通则
        general_path = self.base_path / 'data' / 'civil-code' / 'contract-general.yaml'
        if general_path.exists():
            with open(general_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                articles.extend(data.get('articles', []))
        
        # 加载民法典买卖合同
        sale_path = self.base_path / 'data' / 'civil-code' / 'contract-sale.yaml'
        if sale_path.exists():
            with open(sale_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                articles.extend(data.get('articles', []))
        
        return articles
    
    # =========================================================================
    # 核心查询方法
    # =========================================================================
    
    def get_by_id(self, article_id: str) -> Optional[Dict]:
        """
        按ID查询单条法条
        
        Args:
            article_id: 法条ID，如 CC-577
            
        Returns:
            法条字典，未找到返回None
        """
        for article in self.articles:
            if article.get('id') == article_id:
                return article
        return None
    
    def get_by_category(self, category: str) -> List[Dict]:
        """
        按分类查询法条列表
        
        Args:
            category: 分类名称，如 "违约责任"、"合同解除"
            
        Returns:
            匹配的法条列表
        """
        return [
            article for article in self.articles
            if article.get('category') == category
        ]
    
    def query_by_keywords(self, keywords: Union[str, List[str]], top_n: int = 10) -> List[Dict]:
        """
        关键词语义查询
        
        Args:
            keywords: 关键词（字符串或列表）
            top_n: 返回前N条结果
            
        Returns:
            按匹配度排序的法条列表，每条包含 match_score 字段
        """
        if isinstance(keywords, str):
            keywords = [keywords]
        
        # 预处理关键词为小写
        keywords = [kw.lower() for kw in keywords if kw.strip()]
        
        if not keywords:
            return []
        
        # 计算每条法条的匹配分数
        scored_articles = []
        weights = self.config.get('keyword_weights', {
            'exact_match': 100,
            'partial_match': 50,
            'title_bonus': 15
        })
        
        for article in self.articles:
            score = 0
            matched_keywords = []
            
            # 搜索范围：标题、原文、关键词、解读
            search_fields = [
                article.get('title', ''),
                article.get('original_text', ''),
                ' '.join(article.get('keywords', [])),
                article.get('interpretation', {}).get('core_principle', ''),
                ' '.join(article.get('interpretation', {}).get('key_points', []))
            ]
            
            search_text = ' '.join(search_fields).lower()
            
            for keyword in keywords:
                # 精确匹配
                if keyword in search_text:
                    score += weights.get('exact_match', 100)
                    matched_keywords.append(keyword)
                    
                    # 标题匹配额外加分
                    if keyword in article.get('title', '').lower():
                        score += weights.get('title_bonus', 15)
                
                # 部分匹配（关键词的子串）
                elif len(keyword) > 2:
                    parts = [keyword[:i] for i in range(max(2, len(keyword)-2), len(keyword))]
                    for part in parts:
                        if part in search_text:
                            score += weights.get('partial_match', 50) // len(parts)
                            break
            
            if score > 0:
                article_copy = article.copy()
                article_copy['match_score'] = score
                article_copy['matched_keywords'] = matched_keywords
                scored_articles.append(article_copy)
        
        # 按分数降序排序
        scored_articles.sort(key=lambda x: x['match_score'], reverse=True)
        
        return scored_articles[:top_n]
    
    def review_clause(self, clause_text: str) -> ReviewResult:
        """
        合同条款合规性审查
        
        Args:
            clause_text: 合同条款文本
            
        Returns:
            审查结果对象，包含评分、风险等级、风险列表、匹配法条等
        """
        # 风险关键词模式
        risk_patterns = {
            '违约金': {
                'patterns': [r'违约金.*%', r'违约金.*[零一二三四五六七八九十百千万\d]+', r'%.*违约金'],
                'risk_type': '违约金约定审查',
                'article_id': 'CC-585',
                'severity': '中',
                'checks': [self._check_penalty_rate]
            },
            '解除权': {
                'patterns': [r'解除合同', r'有权解除', r'单方解除', r'解除权'],
                'risk_type': '合同解除约定审查',
                'article_id': 'CC-563',
                'severity': '中',
                'checks': [self._check_termination_rights]
            },
            '定金': {
                'patterns': [r'定金', r'订金'],
                'risk_type': '定金条款审查',
                'article_id': 'CC-586',
                'severity': '中',
                'checks': [self._check_deposit]
            },
            '质量责任': {
                'patterns': [r'质量.*问题', r'质量.*不符', r'质量异议', r'验收'],
                'risk_type': '质量责任条款审查',
                'article_id': 'CC-617',
                'severity': '中',
                'checks': [self._check_quality_terms]
            },
            '风险转移': {
                'patterns': [r'风险', r'灭失', r'毁损'],
                'risk_type': '风险转移条款审查',
                'article_id': 'CC-604',
                'severity': '低',
                'checks': [self._check_risk_transfer]
            },
            '付款期限': {
                'patterns': [r'付款', r'支付', r'货款', r'价款'],
                'risk_type': '付款条款审查',
                'article_id': 'CC-628',
                'severity': '中',
                'checks': [self._check_payment_terms]
            },
            '所有权保留': {
                'patterns': [r'所有权保留', r'保留所有权'],
                'risk_type': '所有权保留条款审查',
                'article_id': 'CC-641',
                'severity': '高',
                'checks': [self._check_title_retention]
            }
        }
        
        risks = []
        matched_articles = []
        base_score = 100
        
        text_lower = clause_text.lower()
        
        # 检查每种风险模式
        for risk_name, config in risk_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, text_lower):
                    # 执行具体检查
                    for check_func in config['checks']:
                        result = check_func(clause_text)
                        if result:
                            risks.append(RiskItem(
                                type=config['risk_type'],
                                description=result['description'],
                                severity=result.get('severity', config['severity']),
                                law_basis=self.get_by_id(config['article_id']),
                                suggestion=result['suggestion']
                            ))
                            matched_articles.append(config['article_id'])
                            base_score -= result.get('penalty', 10)
                    break
        
        # 去重匹配的法条
        matched_articles = list(set(matched_articles))
        
        # 确定风险等级
        risk_scoring = self.config.get('risk_scoring', {
            'high_risk_threshold': 40,
            'medium_risk_threshold': 70
        })
        
        if base_score <= risk_scoring.get('high_risk_threshold', 40):
            risk_level = '高'
        elif base_score <= risk_scoring.get('medium_risk_threshold', 70):
            risk_level = '中'
        else:
            risk_level = '低'
        
        # 生成摘要
        summary = self._generate_summary(risks, base_score)
        
        return ReviewResult(
            score=max(0, base_score),
            risk_level=risk_level,
            risks=risks,
            matched_articles=matched_articles,
            summary=summary
        )
    
    # =========================================================================
    # 具体检查函数
    # =========================================================================
    
    def _check_penalty_rate(self, text: str) -> Optional[Dict]:
        """检查违约金比例"""
        # 查找百分比数字
        percent_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
        
        for match in percent_matches:
            try:
                rate = float(match)
                if rate >= 30:
                    return {
                        'description': f'违约金约定为{rate}%，超过法定的合理范围（一般不超过损失的30%），可能被法院调低',
                        'severity': '高',
                        'suggestion': '建议将违约金调整至合理范围（如不超过合同金额的20%），或明确约定损失计算方式和违约金适用条件',
                        'penalty': 20
                    }
                elif rate >= 20:
                    return {
                        'description': f'违约金约定为{rate}%，接近30%的上限，存在被调低的风险',
                        'severity': '中',
                        'suggestion': '建议评估合理性，必要时调低违约金比例或增加损失计算条款',
                        'penalty': 10
                    }
            except ValueError:
                pass
        
        # 检查是否有固定金额违约金
        fixed_matches = re.findall(r'违约金[^\d]*(\d+[零一二三四五六七八九十百千万]*)', text)
        if fixed_matches and not percent_matches:
            return {
                'description': '约定了固定金额违约金，未明确比例或计算方式',
                'severity': '低',
                'suggestion': '建议明确违约金计算方式或合理比例，避免争议',
                'penalty': 5
            }
        
        return None
    
    def _check_termination_rights(self, text: str) -> Optional[Dict]:
        """检查解除权约定"""
        # 检查是否约定了解除条件
        has_condition = re.search(r'如果.*解除|若.*解除|当.*时.*解除|解除.*条件', text)
        has_procedure = re.search(r'通知.*解除|书面.*解除|解除.*期限', text)
        
        if not has_condition and not has_procedure:
            return {
                'description': '提到了解除权，但未明确约定解除条件和行使程序',
                'severity': '中',
                'suggestion': '建议明确约定解除合同的具体条件、通知方式、行使期限和后续处理',
                'penalty': 10
            }
        
        # 检查是否有任意解除权
        has_arbitrary = re.search(r'随时解除|任意解除|单方解除', text)
        if has_arbitrary:
            return {
                'description': '约定了任意解除权，可能导致合同稳定性不足',
                'severity': '中',
                'suggestion': '建议对任意解除权加以适当限制，如提前通知期、损失赔偿范围等',
                'penalty': 8
            }
        
        return None
    
    def _check_deposit(self, text: str) -> Optional[Dict]:
        """检查定金条款"""
        # 区分定金和订金
        if '订金' in text and '定金' not in text:
            return {
                'description': '使用的是"订金"而非"定金"，不适用定金罚则',
                'severity': '中',
                'suggestion': '如需适用双倍返还等定金罚则，应改为"定金"，并明确约定定金性质',
                'penalty': 10
            }
        
        # 检查定金金额限制
        amount_matches = re.findall(r'定金[^\d]*(\d+(?:\.\d+)?)\s*%', text)
        for match in amount_matches:
            try:
                rate = float(match)
                if rate > 20:
                    return {
                        'description': f'定金约定为{rate}%，超过法定20%的上限，超过部分不产生定金效力',
                        'severity': '高',
                        'suggestion': '建议将定金比例调整至20%以内，超过部分可约定为预付款或违约金',
                        'penalty': 20
                    }
            except ValueError:
                pass
        
        return None
    
    def _check_quality_terms(self, text: str) -> Optional[Dict]:
        """检查质量责任条款"""
        has_standard = re.search(r'标准|规范|GB|ISO', text)
        has_test_period = re.search(r'检验|验收|异议.*期|质保期|保修期', text)
        
        if not has_standard:
            return {
                'description': '提到了质量责任，但未明确约定质量标准',
                'severity': '中',
                'suggestion': '建议明确约定质量标准（如国家标准、行业标准或双方约定的具体标准）',
                'penalty': 10
            }
        
        if not has_test_period:
            return {
                'description': '提到了质量责任，但未明确约定检验期限或质量异议期限',
                'severity': '中',
                'suggestion': '建议明确约定检验期限、质量异议期限和质量保证期',
                'penalty': 8
            }
        
        return None
    
    def _check_risk_transfer(self, text: str) -> Optional[Dict]:
        """检查风险转移条款"""
        has_transfer_point = re.search(r'交付|验收|到货|签收', text)
        
        if not has_transfer_point:
            return {
                'description': '提到了风险承担，但未明确约定风险转移的具体时点',
                'severity': '低',
                'suggestion': '建议明确约定风险转移时点（如交付时、验收合格后等）',
                'penalty': 5
            }
        
        return None
    
    def _check_payment_terms(self, text: str) -> Optional[Dict]:
        """检查付款条款"""
        has_time = re.search(r'日|天|工作日|发货前|到货后|验收后|月结', text)
        has_method = re.search(r'转账|汇款|电汇|支票|承兑|汇票', text)
        
        if not has_time:
            return {
                'description': '提到了付款，但未明确约定付款时间节点',
                'severity': '中',
                'suggestion': '建议明确约定具体的付款时间节点（如到货后X天、验收合格后X天）',
                'penalty': 10
            }
        
        return None
    
    def _check_title_retention(self, text: str) -> Optional[Dict]:
        """检查所有权保留条款"""
        has_registration = re.search(r'登记|备案|登记对抗', text)
        
        if not has_registration:
            return {
                'description': '约定了所有权保留，但未提及登记事宜，未经登记不得对抗善意第三人',
                'severity': '高',
                'suggestion': '建议明确约定所有权保留的登记义务，重要标的物应办理登记以获得对抗效力',
                'penalty': 20
            }
        
        return None
    
    def _generate_summary(self, risks: List[RiskItem], score: int) -> str:
        """生成审查摘要"""
        if not risks:
            return "条款未发现明显法律风险，基本符合民法典的相关规定。"
        
        high_risks = [r for r in risks if r.severity == '高']
        medium_risks = [r for r in risks if r.severity == '中']
        low_risks = [r for r in risks if r.severity == '低']
        
        parts = []
        if high_risks:
            parts.append(f"发现{len(high_risks)}项高风险问题")
        if medium_risks:
            parts.append(f"{len(medium_risks)}项中风险问题")
        if low_risks:
            parts.append(f"{len(low_risks)}项低风险提示")
        
        risk_desc = "、".join(parts)
        
        if score >= 80:
            conclusion = "整体合规性较好，建议关注提示事项"
        elif score >= 60:
            conclusion = "存在一定法律风险，建议修改完善"
        else:
            conclusion = "存在重大法律风险，务必修改完善"
        
        return f"条款共{risk_desc}。合规评分{score}/100。{conclusion}。"

    # =========================================================================
    # 辅助方法
    # =========================================================================
    
    def get_all_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for article in self.articles:
            category = article.get('category')
            if category:
                categories.add(category)
        return sorted(list(categories))
    
    def get_statistics(self) -> Dict:
        """获取知识库统计信息"""
        category_count = {}
        for article in self.articles:
            category = article.get('category', '未分类')
            category_count[category] = category_count.get(category, 0) + 1
        
        return {
            'total_articles': len(self.articles),
            'category_count': category_count,
            'categories': len(category_count)
        }


# =============================================================================
# 命令行接口
# =============================================================================

def print_article(article: Dict, show_detail: bool = True):
    """打印法条信息"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}[{article['id']}] {article['name']}{Colors.ENDC}")
    print(f"分类: {article['category']}")
    print(f"风险等级: {article['risk_level']}")
    print(f"\n{Colors.BLUE}核心要点:{Colors.ENDC}")
    print(f"  {article['title']}")
    
    if show_detail:
        print(f"\n{Colors.BLUE}法规原文:{Colors.ENDC}")
        print(f"  {article['original_text'].strip()}")
        
        print(f"\n{Colors.BLUE}解读:{Colors.ENDC}")
        print(f"  核心原则: {article['interpretation']['core_principle']}")
        print(f"  关键要点:")
        for point in article['interpretation']['key_points']:
            print(f"    - {point}")
        
        print(f"\n{Colors.BLUE}合同审查提示:{Colors.ENDC}")
        print(f"  {article['contract_review_tips']}")
        
        print(f"\n{Colors.BLUE}关键词:{Colors.ENDC}")
        print(f"  {', '.join(article['keywords'])}")
    
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")


def print_review_result(result: ReviewResult):
    """打印审查结果"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}📋 合同条款合规性审查报告{Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
    
    # 评分显示
    if result.score >= 80:
        score_color = Colors.GREEN
    elif result.score >= 60:
        score_color = Colors.YELLOW
    else:
        score_color = Colors.RED
    print(f"\n{Colors.BOLD}合规评分: {score_color}{result.score}/100{Colors.ENDC}")
    
    # 风险等级
    risk_colors = {'高': Colors.RED, '中': Colors.YELLOW, '低': Colors.GREEN}
    print(f"{Colors.BOLD}风险等级: {risk_colors.get(result.risk_level, Colors.WHITE)}{result.risk_level}{Colors.ENDC}")
    
    print(f"\n{Colors.BLUE}📝 摘要:{Colors.ENDC}")
    print(f"  {result.summary}")
    
    # 风险列表
    if result.risks:
        print(f"\n{Colors.BLUE}⚠️  风险详情:{Colors.ENDC}")
        for i, risk in enumerate(result.risks, 1):
            sev_color = risk_colors.get(risk.severity, Colors.WHITE)
            print(f"\n  {i}. [{sev_color}{risk.severity}风险{Colors.ENDC}] {risk.type}")
            print(f"     描述: {risk.description}")
            print(f"     建议: {risk.suggestion}")
            if risk.law_basis:
                print(f"     法条依据: {risk.law_basis['id']} - {risk.law_basis['name']}")
    
    # 匹配法条
    if result.matched_articles:
        print(f"\n{Colors.BLUE}📚 相关法条:{Colors.ENDC}")
        for aid in result.matched_articles:
            article = LawQuery().get_by_id(aid)
            if article:
                print(f"  - {aid}: {article['title']}")
    
    print(f"\n{Colors.CYAN}{'='*60}{Colors.ENDC}\n")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='合同法规知识库查询工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python law_query.py --id CC-577                    # 按ID查询
  python law_query.py --category 违约责任             # 按分类查询
  python law_query.py --keyword 违约金                # 关键词查询
  python law_query.py --review clause.txt            # 审查条款文件
  python law_query.py --categories                   # 列出所有分类
  python law_query.py --stats                        # 统计信息
        """
    )
    
    parser.add_argument('--id', help='按法条ID查询，如 CC-577')
    parser.add_argument('--category', help='按分类查询')
    parser.add_argument('--keyword', help='关键词查询')
    parser.add_argument('--review', help='审查合同条款文件')
    parser.add_argument('--categories', action='store_true', help='列出所有分类')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--brief', action='store_true', help='简要输出')
    
    args = parser.parse_args()
    
    query = LawQuery()
    
    if args.stats:
        stats = query.get_statistics()
        print(f"\n{Colors.CYAN}📊 知识库统计信息{Colors.ENDC}")
        print(f"  法条总数: {stats['total_articles']} 条")
        print(f"  分类数量: {stats['categories']} 个")
        print(f"\n  分类统计:")
        for category, count in sorted(stats['category_count'].items()):
            print(f"    - {category}: {count} 条")
        print()
        return
    
    if args.categories:
        print(f"\n{Colors.CYAN}📋 所有分类:{Colors.ENDC}")
        for cat in query.get_all_categories():
            articles = query.get_by_category(cat)
            print(f"  - {cat} ({len(articles)} 条)")
        print()
        return
    
    if args.id:
        article = query.get_by_id(args.id)
        if article:
            print_article(article, show_detail=not args.brief)
        else:
            print(f"\n{Colors.RED}❌ 未找到ID为 {args.id} 的法条{Colors.ENDC}\n")
        return
    
    if args.category:
        articles = query.get_by_category(args.category)
        if articles:
            print(f"\n{Colors.CYAN}📚 分类「{args.category}」共 {len(articles)} 条法规:{Colors.ENDC}")
            for article in articles:
                print_article(article, show_detail=not args.brief)
        else:
            print(f"\n{Colors.YELLOW}⚠️  未找到分类为「{args.category}」的法条{Colors.ENDC}\n")
        return
    
    if args.keyword:
        articles = query.query_by_keywords(args.keyword)
        if articles:
            print(f"\n{Colors.CYAN}🔍 关键词「{args.keyword}」搜索结果 (Top {len(articles)}):{Colors.ENDC}")
            for article in articles:
                print(f"  [{article['match_score']}分] {article['id']} - {article['name']}")
                if not args.brief:
                    print(f"      {article['title']}\n")
            print()
        else:
            print(f"\n{Colors.YELLOW}⚠️  未找到包含关键词「{args.keyword}」的法条{Colors.ENDC}\n")
        return
    
    if args.review:
        try:
            with open(args.review, 'r', encoding='utf-8') as f:
                clause_text = f.read()
            result = query.review_clause(clause_text)
            print_review_result(result)
        except FileNotFoundError:
            print(f"\n{Colors.RED}❌ 文件不存在: {args.review}{Colors.ENDC}\n")
        return
    
    # 无参数时显示帮助
    parser.print_help()


if __name__ == '__main__':
    main()
