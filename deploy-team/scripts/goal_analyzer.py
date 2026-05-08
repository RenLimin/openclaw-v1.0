#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务目标深度分析器 - Goal Analyzer
深度研究、拆解并整合智能体团队所需完成的业务目标
输出完整的团队创建方案
"""

import json
import argparse
from typing import Dict, List
from datetime import datetime
import os


class GoalAnalyzer:
    def __init__(self):
        self.results = {
            "version": "1.0",
            "analyzed_at": datetime.now().isoformat(),
            "goal": {},
            "stakeholders": [],
            "risks": [],
            "capabilities": [],
            "roles": {},
            "kpis": [],
            "roadmap": [],
            "roi": {}
        }
        
        # 通用角色模板库
        self.ROLE_TEMPLATES = {
            "document_management": {
                "name": "文档管理专家",
                "emoji": "📄",
                "goal": "确保所有文档规范、准确、可追溯",
                "background": "资深文档管理专家，有10年文档处理经验，对文档质量和规范有极致追求",
                "skills": ["文档起草", "格式规范", "版本管理", "内容审核", "模板设计"],
                "tools": ["文档编辑器", "版本控制系统", "模板库", "OCR识别"],
                "decision_authority": "文档格式和规范最终决策权"
            },
            "compliance": {
                "name": "合规专家",
                "emoji": "⚖️",
                "goal": "确保所有操作100%符合法律法规和内部规定",
                "background": "前合规总监，熟悉各类监管要求，风险嗅觉敏锐",
                "skills": ["合规审查", "风险识别", "法规研究", "合规培训", "审计准备"],
                "tools": ["法规数据库", "合规检查清单", "风险评估工具"],
                "decision_authority": "合规问题最终否决权"
            },
            "data_analyst": {
                "name": "数据分析专家",
                "emoji": "📊",
                "goal": "从数据中挖掘洞察，支撑决策",
                "background": "资深数据分析师，精通各类数据分析方法和工具",
                "skills": ["数据清洗", "统计分析", "数据可视化", "趋势预测", "报告撰写"],
                "tools": ["Python/R", "SQL", "BI工具", "数据可视化库"],
                "decision_authority": "数据分析方法和结论的决策权"
            },
            "project_manager": {
                "name": "项目经理",
                "emoji": "🎯",
                "goal": "确保项目按时、按质、在预算内完成",
                "background": "PMP认证项目经理，10年项目管理经验，擅长复杂项目协调",
                "skills": ["计划制定", "进度跟踪", "风险管理", "资源协调", "沟通汇报"],
                "tools": ["项目管理软件", "甘特图", "风险管理工具"],
                "decision_authority": "项目计划和资源调配的决策权"
            },
            "content_creator": {
                "name": "内容创作专家",
                "emoji": "✍️",
                "goal": "产出高质量、有影响力的内容",
                "background": "资深内容创作者，擅长多种文体，对内容质量有极高要求",
                "skills": ["文案写作", "内容策划", "SEO优化", "受众分析", "品牌调性把控"],
                "tools": ["内容管理系统", "SEO工具", "排版工具"],
                "decision_authority": "内容质量和风格的最终决策权"
            },
            "customer_service": {
                "name": "客户服务专家",
                "emoji": "💬",
                "goal": "提供卓越的客户体验，高满意度",
                "background": "资深客户服务经理，擅长处理复杂客户问题，同理心强",
                "skills": ["问题解答", "投诉处理", "客户关系维护", "满意度提升", "服务流程优化"],
                "tools": ["客服系统", "知识库", "CRM系统"],
                "decision_authority": "客户问题处理方案的决策权"
            },
            "quality_assurance": {
                "name": "质量保障专家",
                "emoji": "✅",
                "goal": "确保所有产出物达到质量标准",
                "background": "资深QA专家，擅长建立质量体系，对零缺陷有执着追求",
                "skills": ["质量标准制定", "过程审核", "缺陷识别", "质量改进", "测试设计"],
                "tools": ["质量管理工具", "测试框架", "缺陷跟踪系统"],
                "decision_authority": "质量标准制定和质量问题最终判定权"
            }
        }
        
        # 通用KPI库
        self.COMMON_KPIS = [
            {"name": "任务完成率", "category": "效能", "unit": "%", "baseline": "80%", "target": "95%"},
            {"name": "平均响应时间", "category": "效能", "unit": "分钟", "baseline": "30", "target": "10"},
            {"name": "处理准确率", "category": "质量", "unit": "%", "baseline": "90%", "target": "99%"},
            {"name": "月运行成本", "category": "成本", "unit": "元", "baseline": "10000", "target": "5000"},
            {"name": "系统可用性", "category": "技术", "unit": "%", "baseline": "99%", "target": "99.5%"},
            {"name": "错误率", "category": "质量", "unit": "%", "baseline": "5%", "target": "0.5%"},
            {"name": "用户满意度", "category": "业务", "unit": "分", "baseline": "3.5", "target": "4.5"},
            {"name": "人力节省", "category": "业务", "unit": "人月", "baseline": "0", "target": "3"}
        ]
        
        # 通用风险检查清单
        self.RISK_CHECKLIST = [
            {"category": "合规", "question": "是否有明确的监管要求？", "default_severity": "高"},
            {"category": "成本", "question": "预算是否充足且明确？", "default_severity": "中"},
            {"category": "时间", "question": "时间要求是否紧张？", "default_severity": "中"},
            {"category": "技术", "question": "技术方案是否可行？", "default_severity": "高"},
            {"category": "数据", "question": "需要的数据是否可获取？", "default_severity": "高"},
            {"category": "人员", "question": "是否有人员依赖？", "default_severity": "中"},
            {"category": "变更", "question": "需求是否可能频繁变更？", "default_severity": "中"},
            {"category": "安全", "question": "是否涉及敏感数据或操作？", "default_severity": "高"},
            {"category": "集成", "question": "是否需要与现有系统集成？", "default_severity": "中"},
            {"category": "培训", "question": "用户是否需要培训？", "default_severity": "低"}
        ]

    def analyze_goal(self, goal_text: str) -> Dict:
        """
        深度分析业务目标文本
        """
        print(f"🔍 正在分析业务目标: {goal_text[:50]}...")
        
        self.results["goal"] = {
            "original_text": goal_text,
            "summary": self._extract_summary(goal_text),
            "problem_statement": self._extract_problem(goal_text),
            "target_users": self._extract_users(goal_text),
            "expected_benefits": self._extract_benefits(goal_text),
            "time_constraints": self._extract_time_constraints(goal_text),
            "budget_constraints": self._extract_budget_constraints(goal_text)
        }
        
        return self.results["goal"]

    def _extract_summary(self, text: str) -> str:
        """提取目标摘要"""
        # 简化实现 - 取前100字
        return text[:100] + "..." if len(text) > 100 else text

    def _extract_problem(self, text: str) -> str:
        """提取问题陈述"""
        # 关键词匹配
        keywords = ["解决", "问题", "痛点", "难点", "挑战", "改进", "优化"]
        for keyword in keywords:
            if keyword in text:
                idx = text.find(keyword)
                end = text.find("。", idx)
                if end == -1:
                    end = len(text)
                return text[idx:end]
        return "需要通过智能体团队提升效率和质量"

    def _extract_users(self, text: str) -> List[str]:
        """提取目标用户"""
        # 简化实现
        users = ["业务部门", "管理层", "最终用户"]
        if "合同" in text:
            users = ["法务部", "业务部门", "管理层"]
        elif "财务" in text:
            users = ["财务部", "管理层", "业务部门"]
        elif "客服" in text or "客户" in text:
            users = ["客户", "客服部", "管理层"]
        return users

    def _extract_benefits(self, text: str) -> List[str]:
        """提取预期收益"""
        benefits = ["提升效率", "降低成本", "提高质量", "减少错误"]
        
        # 从文本中提取具体数字
        if "%" in text:
            import re
            numbers = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
            for num in numbers:
                benefits.append(f"提升/降低 {num}%")
        
        return benefits

    def _extract_time_constraints(self, text: str) -> str:
        """提取时间约束"""
        time_keywords = ["天", "周", "月", "年", "小时", "分钟"]
        for kw in time_keywords:
            if kw in text:
                idx = text.find(kw)
                start = max(0, idx - 10)
                return text[start:idx + 2]
        return "无明确时间约束"

    def _extract_budget_constraints(self, text: str) -> str:
        """提取预算约束"""
        budget_keywords = ["预算", "元", "万", "钱", "成本"]
        for kw in budget_keywords:
            if kw in text:
                idx = text.find(kw)
                start = max(0, idx - 10)
                end = min(len(text), idx + 10)
                return text[start:end]
        return "无明确预算约束"

    def analyze_stakeholders(self) -> List[Dict]:
        """分析利益相关者"""
        print("👥 正在分析利益相关者...")
        
        stakeholders = [
            {
                "name": "最终用户",
                "role": "使用者",
                "interest": "高",
                "influence": "中",
                "core_needs": ["易用", "高效", "准确"],
                "success_metrics": ["满意度", "效率提升", "错误率"]
            },
            {
                "name": "业务负责人",
                "role": "决策者",
                "interest": "高",
                "influence": "高",
                "core_needs": ["ROI", "可控", "合规"],
                "success_metrics": ["成本节约", "效率提升", "合规率"]
            },
            {
                "name": "技术团队",
                "role": "维护者",
                "interest": "中",
                "influence": "中",
                "core_needs": ["稳定", "可维护", "可扩展"],
                "success_metrics": ["可用性", "故障率", "维护成本"]
            }
        ]
        
        self.results["stakeholders"] = stakeholders
        return stakeholders

    def analyze_risks(self) -> List[Dict]:
        """分析风险"""
        print("⚠️  正在分析风险...")
        
        risks = []
        for risk_item in self.RISK_CHECKLIST:
            risks.append({
                "category": risk_item["category"],
                "description": risk_item["question"],
                "severity": risk_item["default_severity"],
                "probability": "中",
                "impact": "待评估",
                "mitigation": "制定应对方案"
            })
        
        self.results["risks"] = risks
        return risks

    def analyze_capabilities(self, goal_text: str) -> List[Dict]:
        """分析核心能力需求"""
        print("🔧 正在分析核心能力需求...")
        
        capabilities = []
        
        # 基于关键词匹配能力
        if "合同" in goal_text or "文档" in goal_text:
            capabilities.extend([
                {"name": "文档起草", "priority": "必须", "category": "核心业务"},
                {"name": "文档审核", "priority": "必须", "category": "核心业务"},
                {"name": "合规检查", "priority": "必须", "category": "风险控制"},
                {"name": "版本管理", "priority": "应该", "category": "基础能力"},
                {"name": "归档管理", "priority": "应该", "category": "基础能力"}
            ])
        elif "数据" in goal_text or "分析" in goal_text:
            capabilities.extend([
                {"name": "数据采集", "priority": "必须", "category": "核心业务"},
                {"name": "数据清洗", "priority": "必须", "category": "核心业务"},
                {"name": "统计分析", "priority": "必须", "category": "核心业务"},
                {"name": "可视化报表", "priority": "应该", "category": "输出能力"},
                {"name": "趋势预测", "priority": "可以", "category": "高级能力"}
            ])
        elif "客服" in goal_text or "客户" in goal_text:
            capabilities.extend([
                {"name": "问题解答", "priority": "必须", "category": "核心业务"},
                {"name": "投诉处理", "priority": "必须", "category": "核心业务"},
                {"name": "知识库维护", "priority": "应该", "category": "基础能力"},
                {"name": "满意度调查", "priority": "应该", "category": "质量保障"}
            ])
        else:
            # 通用能力
            capabilities.extend([
                {"name": "任务处理", "priority": "必须", "category": "核心业务"},
                {"name": "质量审核", "priority": "必须", "category": "质量保障"},
                {"name": "数据统计", "priority": "应该", "category": "基础能力"},
                {"name": "报告生成", "priority": "应该", "category": "输出能力"}
            ])
        
        self.results["capabilities"] = capabilities
        return capabilities

    def recommend_roles(self, goal_text: str, capabilities: List[Dict]) -> Dict:
        """推荐角色配置"""
        print("👤 正在推荐角色配置...")
        
        roles = {
            "coordination_layer": {
                "jerry": {
                    "name": "Jerry",
                    "emoji": "🦞",
                    "goal": "全局协调、质量管控、架构治理",
                    "background": "10年智能体团队管理经验，熟悉全流程",
                    "skills": ["全局协调", "质量管控", "架构治理", "风险控制"],
                    "tools": ["所有协调权限"],
                    "decision_authority": "重大问题最终裁决"
                }
            },
            "business_layer": {},
            "infrastructure_layer": {
                "nova": {
                    "name": "Nova",
                    "emoji": "🌟",
                    "goal": "所有工具技能稳定安全高质量可复用",
                    "background": "资深架构师，对代码质量、依赖治理有洁癖",
                    "skills": ["技能管理", "质量保障", "工具集成", "依赖治理"],
                    "tools": ["skill-vetting全套工具"],
                    "decision_authority": "技能质量否决权"
                },
                "orion": {
                    "name": "Orion",
                    "emoji": "🌌",
                    "goal": "最优成本获得最高质量输出",
                    "background": "前OpenAI工程师，熟悉各种模型特性",
                    "skills": ["模型调度", "Prompt优化", "成本控制", "质量评估"],
                    "tools": ["所有大模型API", "Prompt模板库"],
                    "decision_authority": "模型路由策略制定权"
                },
                "luna": {
                    "name": "Luna",
                    "emoji": "🌙",
                    "goal": "系统100%可用，异常早发现",
                    "background": "资深运维SRE，7x24值守",
                    "skills": ["监控运维", "异常检测", "故障自愈", "性能优化"],
                    "tools": ["全链路监控", "告警渠道", "自愈脚本"],
                    "decision_authority": "告警级别定义权"
                }
            }
        }
        
        # 根据目标文本匹配合适的业务角色
        if "合同" in goal_text or "文档" in goal_text:
            roles["business_layer"]["document_expert"] = self.ROLE_TEMPLATES["document_management"].copy()
            roles["business_layer"]["compliance_expert"] = self.ROLE_TEMPLATES["compliance"].copy()
            roles["business_layer"]["qa_expert"] = self.ROLE_TEMPLATES["quality_assurance"].copy()
        elif "数据" in goal_text or "分析" in goal_text:
            roles["business_layer"]["data_analyst"] = self.ROLE_TEMPLATES["data_analyst"].copy()
            roles["business_layer"]["qa_expert"] = self.ROLE_TEMPLATES["quality_assurance"].copy()
        elif "客服" in goal_text or "客户" in goal_text:
            roles["business_layer"]["customer_service"] = self.ROLE_TEMPLATES["customer_service"].copy()
            roles["business_layer"]["qa_expert"] = self.ROLE_TEMPLATES["quality_assurance"].copy()
        else:
            roles["business_layer"]["content_creator"] = self.ROLE_TEMPLATES["content_creator"].copy()
            roles["business_layer"]["qa_expert"] = self.ROLE_TEMPLATES["quality_assurance"].copy()
        
        self.results["roles"] = roles
        return roles

    def generate_kpis(self, goal_text: str) -> List[Dict]:
        """生成KPI指标体系"""
        print("📊 正在生成KPI指标体系...")
        
        kpis = self.COMMON_KPIS.copy()
        
        # 根据目标文本添加特定KPI
        if "合同" in goal_text:
            kpis.extend([
                {"name": "合同审核周期", "category": "效能", "unit": "天", "baseline": "7", "target": "1"},
                {"name": "合规通过率", "category": "质量", "unit": "%", "baseline": "85%", "target": "99%"}
            ])
        elif "客服" in goal_text:
            kpis.extend([
                {"name": "首次响应时间", "category": "效能", "unit": "分钟", "baseline": "15", "target": "3"},
                {"name": "问题一次解决率", "category": "质量", "unit": "%", "baseline": "70%", "target": "90%"}
            ])
        
        self.results["kpis"] = kpis
        return kpis

    def generate_roadmap(self) -> List[Dict]:
        """生成实施路线图"""
        print("🗺️  正在生成实施路线图...")
        
        roadmap = [
            {
                "phase": "种子期 (Seed)",
                "duration": "0-7天",
                "goal": "验证核心假设，建立最小可行团队",
                "milestones": ["MVP团队跑通核心流程", "首次验证通过(B级以上)"],
                "deliverables": ["v0.1团队架构", "验证报告v0.1"]
            },
            {
                "phase": "生长期 (Growth)",
                "duration": "7-30天",
                "goal": "完善团队能力，建立质量体系",
                "milestones": ["覆盖所有核心能力", "知识库v1.0完成", "验证达到A级"],
                "deliverables": ["v1.0完整团队", "知识库v1.0", "验证报告v1.0"]
            },
            {
                "phase": "成熟期 (Mature)",
                "duration": "30-90天",
                "goal": "优化性能，建立自进化能力",
                "milestones": ["性能优化30%+", "自监控系统部署", "验证达到S级"],
                "deliverables": ["v2.0优化团队", "监控仪表盘", "自进化引擎"]
            },
            {
                "phase": "卓越期 (Excellent)",
                "duration": "90天+",
                "goal": "持续进化，成为行业标杆",
                "milestones": ["月度持续优化", "知识库深度治理"],
                "deliverables": ["月度优化报告", "行业最佳实践"]
            }
        ]
        
        self.results["roadmap"] = roadmap
        return roadmap

    def calculate_roi(self) -> Dict:
        """计算ROI"""
        print("💰 正在计算ROI...")
        
        roi = {
            "cost_estimation": {
                "development_cost": "10-20人天",
                "monthly_running_cost": "3000-8000元",
                "maintenance_cost": "1-2人月/月"
            },
            "benefit_estimation": {
                "labor_savings": "2-5人月/月",
                "efficiency_improvement": "50-80%",
                "error_reduction": "70-90%"
            },
            "payback_period": "1-3个月",
            "annual_roi": "200-400%"
        }
        
        self.results["roi"] = roi
        return roi

    def analyze_full(self, goal_text: str) -> Dict:
        """执行完整的业务目标分析"""
        print("=" * 60)
        print("🔍 业务目标深度分析引擎 v1.0")
        print("=" * 60)
        print()
        
        self.analyze_goal(goal_text)
        self.analyze_stakeholders()
        self.analyze_risks()
        self.analyze_capabilities(goal_text)
        self.recommend_roles(goal_text, self.results["capabilities"])
        self.generate_kpis(goal_text)
        self.generate_roadmap()
        self.calculate_roi()
        
        print()
        print("=" * 60)
        print("✅ 分析完成！")
        print("=" * 60)
        
        return self.results

    def generate_report(self, output_dir: str = "./analysis_result") -> str:
        """生成完整的分析报告"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成JSON格式结果
        json_path = os.path.join(output_dir, "analysis_result.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # 生成Markdown报告
        md_path = os.path.join(output_dir, "业务目标分析报告.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report())
        
        # 生成YAML角色定义
        yaml_path = os.path.join(output_dir, "团队架构蓝图.yaml")
        with open(yaml_path, 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(self.results["roles"], f, allow_unicode=True, default_flow_style=False)
        
        print(f"📄 分析报告已保存到: {output_dir}/")
        print(f"   - {json_path}")
        print(f"   - {md_path}")
        print(f"   - {yaml_path}")
        
        return output_dir

    def _generate_markdown_report(self) -> str:
        """生成Markdown格式的报告"""
        md = f"""# 📊 业务目标深度分析报告

**生成时间：** {self.results['analyzed_at']}
**版本：** v1.0

---

## 🎯 一、业务目标概述

### 原始描述
{self.results['goal']['original_text']}

### 问题陈述
> {self.results['goal']['problem_statement']}

### 目标用户
"""
        for user in self.results['goal']['target_users']:
            md += f"- {user}\n"
        
        md += f"""
### 预期收益
"""
        for benefit in self.results['goal']['expected_benefits']:
            md += f"- ✅ {benefit}\n"
        
        md += f"""
### 约束条件
- ⏰ 时间约束: {self.results['goal']['time_constraints']}
- 💰 预算约束: {self.results['goal']['budget_constraints']}

---

## 👥 二、利益相关者分析

| 角色 | 利益相关度 | 影响力 | 核心需求 | 成功指标 |
|------|-----------|-------|---------|---------|
"""
        for stakeholder in self.results['stakeholders']:
            md += f"| {stakeholder['name']} | {stakeholder['interest']} | {stakeholder['influence']} | {', '.join(stakeholder['core_needs'])} | {', '.join(stakeholder['success_metrics'])} |\n"
        
        md += f"""
---

## ⚠️ 三、风险评估

| 风险类别 | 风险描述 | 严重程度 | 应对措施 |
|---------|---------|---------|---------|
"""
        for risk in self.results['risks']:
            md += f"| {risk['category']} | {risk['description']} | {risk['severity']} | {risk['mitigation']} |\n"
        
        md += f"""
---

## 🔧 四、核心能力需求矩阵

| 能力名称 | 优先级 | 类别 |
|---------|-------|------|
"""
        for cap in self.results['capabilities']:
            priority_emoji = "🔴" if cap['priority'] == "必须" else ("🟡" if cap['priority'] == "应该" else "🟢")
            md += f"| {priority_emoji} {cap['name']} | {cap['priority']} | {cap['category']} |\n"
        
        md += f"""
---

## 👤 五、建议团队架构

### 协调层 (1人)
- **Jerry 🦞**: 全局协调、质量管控、架构治理

### 业务层 ({len(self.results['roles'].get('business_layer', {}))}人)
"""
        for role_id, role in self.results['roles'].get('business_layer', {}).items():
            md += f"- **{role['name']} {role['emoji']}**: {role['goal']}\n"
        
        md += f"""
### 基础设施层 (3人)
- **Nova 🌟**: 技能管理、质量保障
- **Orion 🌌**: 模型调度、成本优化
- **Luna 🌙**: 监控运维、异常检测

---

## 📊 六、成功指标体系 (KPI)

| 指标名称 | 类别 | 单位 | 基线值 | 目标值 |
|---------|------|------|-------|-------|
"""
        for kpi in self.results['kpis']:
            md += f"| {kpi['name']} | {kpi['category']} | {kpi['unit']} | {kpi['baseline']} | {kpi['target']} |\n"
        
        md += f"""
---

## 🗺️ 七、实施路线图

"""
        for phase in self.results['roadmap']:
            md += f"""### {phase['phase']} ({phase['duration']})

**目标：** {phase['goal']}

**里程碑：**
"""
            for m in phase['milestones']:
                md += f"- ✅ {m}\n"
            md += "\n**交付物：**\n"
            for d in phase['deliverables']:
                md += f"- 📦 {d}\n"
            md += "\n"
        
        md += f"""---

## 💰 八、ROI预估

### 成本预估
- 🔧 开发成本: {self.results['roi']['cost_estimation']['development_cost']}
- 📅 月运行成本: {self.results['roi']['cost_estimation']['monthly_running_cost']}
- 🔧 维护成本: {self.results['roi']['cost_estimation']['maintenance_cost']}

### 收益预估
- 👥 人力节省: {self.results['roi']['benefit_estimation']['labor_savings']}
- ⚡ 效率提升: {self.results['roi']['benefit_estimation']['efficiency_improvement']}
- ✅ 错误减少: {self.results['roi']['benefit_estimation']['error_reduction']}

### 投资回报
- ⏰ 投资回收期: {self.results['roi']['payback_period']}
- 📈 年化ROI: {self.results['roi']['annual_roi']}

---

## ✅ 九、结论与建议

1. **项目可行性：** ✅ 可行，建议立即启动
2. **团队规模：** {1 + len(self.results['roles'].get('business_layer', {})) + 3} 人智能体团队
3. **预期周期：** 30天内完成v1.0，90天达到成熟期
4. **投资回报：** 预计{self.results['roi']['payback_period']}收回成本，年化ROI {self.results['roi']['annual_roi']}

---

**报告生成：** 业务目标深度分析引擎 v1.0
**时间：** {self.results['analyzed_at']}
"""
        return md

    def print_summary(self):
        """打印分析摘要"""
        print("\n" + "=" * 60)
        print("📋 分析摘要")
        print("=" * 60)
        
        print(f"\n🎯 核心问题: {self.results['goal']['problem_statement']}")
        
        print(f"\n👥 建议团队规模: {1 + len(self.results['roles'].get('business_layer', {})) + 3} 人")
        print(f"   - 协调层: 1人 (Jerry)")
        print(f"   - 业务层: {len(self.results['roles'].get('business_layer', {}))} 人")
        print(f"   - 基础设施层: 3人 (Nova, Orion, Luna)")
        
        print(f"\n🔧 核心能力需求: {len(self.results['capabilities'])} 项")
        for cap in self.results['capabilities'][:5]:
            emoji = "🔴" if cap['priority'] == "必须" else ("🟡" if cap['priority'] == "应该" else "🟢")
            print(f"   {emoji} {cap['name']}")
        
        print(f"\n📊 KPI指标: {len(self.results['kpis'])} 项")
        
        print(f"\n💰 投资回收期: {self.results['roi']['payback_period']}")
        print(f"📈 年化ROI: {self.results['roi']['annual_roi']}")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="业务目标深度分析器")
    parser.add_argument("--goal", type=str, help="业务目标描述文本")
    parser.add_argument("--file", type=str, help="从文件读取业务目标描述")
    parser.add_argument("--output", type=str, default="./analysis_result",
                       help="输出目录路径")
    
    args = parser.parse_args()
    
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            goal_text = f.read()
    elif args.goal:
        goal_text = args.goal
    else:
        print("❌ 请提供 --goal 或 --file 参数")
        print("\n使用示例:")
        print("  python goal_analyzer.py --goal \"我们需要智能体团队管理合同...\"")
        print("  python goal_analyzer.py --file business_goal.txt")
        return
    
    analyzer = GoalAnalyzer()
    analyzer.analyze_full(goal_text)
    analyzer.print_summary()
    analyzer.generate_report(args.output)


if __name__ == "__main__":
    main()
