# Orion 场景化 Prompt 模板库 v1.0

> **版本**: v1.0  
> **日期**: 2026-05-06  
> **场景总数**: 16个（原10个 + Rex补充6个）  
> **负责人**: 🌌 Orion

---

## 📋 模板库总览

| 编号 | 场景名称 | 所属Agent | 优先级 | 预期提升 |
|------|---------|----------|--------|---------|
| S01 | 合同风险条款识别 | Ella | 🔴 最高 | 风险遗漏率从20% → <1% |
| S02 | 合同结构化字段抽取 | Ella | 🔴 最高 | 效率提升90%，准确率>98% |
| S03 | 交付月报经营洞察生成 | Aaron | 🔴 最高 | 从3天 → 3分钟 |
| S04 | 项目健康度评估 | Oliver | 🟠 高 | 风险识别提前1-2周 |
| S05 | 异常成本识别与根因分析 | Aaron | 🟠 高 | 成本超支减少40% |
| S06 | 履约义务拆分 | Ella | 🟠 高 | 拆分效率提升70% |
| S07 | 会议纪要与任务提取 | Luna | 🟡 中 | 效率提升80%，闭环率100% |
| S08 | 项目复盘经验提取 | Iris | 🟡 中 | 知识沉淀100%自动化 |
| S09 | 客户邮件自动回复 | Iris | 🟡 中 | 响应时间从4小时 → 1分钟 |
| S10 | 风险预警通知生成 | Luna | 🟡 中 | 通知质量标准化 |
| --- | --- | --- | --- | --- |
| S11 | ✅ 需求结构化梳理 & PRD初稿生成 | Oliver | 🔴 最高 | Rex补充 |
| S12 | ✅ 需求风险智能识别 | Oliver | 🔴 最高 | Rex补充 |
| S13 | ✅ 测试用例批量生成 | Oliver | 🟠 高 | Rex补充 |
| S14 | ✅ 会议纪要 & 待办自动生成 | Luna | 🟠 高 | Rex补充 |
| S15 | ✅ 项目周报/月报自动生成 | Oliver | 🟠 高 | Rex补充 |
| S16 | ✅ 日志故障智能诊断 | Luna | 🟠 高 | Rex补充 |

---

## 📝 Rex补充6个场景详细说明

---

### S11: 需求结构化梳理 & PRD初稿生成

**场景描述**：
从客户口头需求、邮件、会议记录等非结构化输入，自动梳理成结构化的PRD（产品需求文档）初稿。

**预期输入**：
```text
客户需求原文（可能是聊天记录、邮件、会议录音转写等）
```

**预期输出**（JSON结构化）：
```json
{
  "requirement_id": "REQ-2026-001",
  "title": "需求标题",
  "background": "需求背景与业务目标",
  "user_stories": [
    {
      "role": "用户角色",
      "action": "用户行为",
      "benefit": "业务价值"
    }
  ],
  "functional_requirements": [
    {
      "module": "功能模块",
      "description": "详细描述",
      "acceptance_criteria": ["验收标准1", "验收标准2"]
    }
  ],
  "non_functional_requirements": [
    {
      "type": "性能/安全/可用性等",
      "description": "详细描述"
    }
  ],
  "mockup_notes": "原型建议",
  "priority_assessment": {
    "business_value": "高/中/低",
    "urgency": "高/中/低",
    "complexity": "高/中/低"
  }
}
```

**Few-shot示例数**: 3个

**置信度要求**: ≥ 85%，低于此标记人工复核

---

### S12: 需求风险智能识别

**场景描述**：
对梳理后的需求进行风险扫描，识别隐含的技术风险、业务风险、交付风险。

**预期输入**：
```text
结构化需求文档（S11的输出）
历史类似项目数据
当前团队资源情况
```

**预期输出**（JSON结构化）：
```json
{
  "risk_scan_summary": {
    "total_risks": 5,
    "high_risk": 2,
    "medium_risk": 2,
    "low_risk": 1
  },
  "risks": [
    {
      "risk_id": "RISK-001",
      "type": "技术风险/业务风险/交付风险",
      "level": "🔴高/🟠中/🟡低",
      "description": "风险描述",
      "root_cause": "根因分析",
      "impact_assessment": "影响评估",
      "mitigation_suggestion": "规避建议",
      "confidence": 0.92
    }
  ],
  "overall_risk_level": "🔴高",
  "delivery_impact": "可能延期X天/成本增加Y万",
  "recommendations": ["建议1", "建议2"]
}
```

**Few-shot示例数**: 5个（覆盖不同类型风险）

**置信度要求**: ≥ 80%

---

### S13: 测试用例批量生成

**场景描述**：
基于PRD需求，自动生成完整的测试用例集，覆盖功能、边界、异常、性能等场景。

**预期输入**：
```text
PRD需求文档（结构化）
历史测试用例库（可选）
```

**预期输出**（JSON结构化，可直接导出Excel）：
```json
{
  "module": "登录功能",
  "test_cases": [
    {
      "case_id": "TC-LOGIN-001",
      "case_type": "功能测试/边界测试/异常测试/性能测试",
      "title": "用例标题",
      "preconditions": ["前置条件1", "前置条件2"],
      "steps": ["步骤1", "步骤2", "步骤3"],
      "expected_result": "预期结果",
      "priority": "P0/P1/P2/P3",
      "estimated_time": "30分钟",
      "test_data": "测试数据建议"
    }
  ],
  "coverage_analysis": {
    "functional_coverage": "95%",
    "boundary_coverage": "80%",
    "exception_coverage": "75%"
  },
  "automation_suggestions": ["可自动化用例列表"]
}
```

**Few-shot示例数**: 4个

**置信度要求**: ≥ 90%

---

### S14: 会议纪要 & 待办自动生成

**场景描述**：
从会议录音转写文字，自动生成结构化会议纪要，提取决议事项、待办任务、责任人、截止时间。

**预期输入**：
```text
会议录音转写原文（可能口语化、有重复、有打断）
参会人员名单
会议主题
```

**预期输出**（JSON结构化）：
```json
{
  "meeting_summary": {
    "topic": "会议主题",
    "date": "2026-05-06",
    "attendees": ["张三", "李四"],
    "duration_minutes": 60
  },
  "key_points": [
    "核心讨论要点1",
    "核心讨论要点2"
  ],
  "decisions": [
    {
      "decision": "决议内容",
      "decided_by": "决策人",
      "background": "决策背景"
    }
  ],
  "action_items": [
    {
      "task_id": "TASK-001",
      "description": "任务描述",
      "assignee": "责任人",
      "due_date": "2026-05-10",
      "priority": "高/中/低",
      "dependencies": ["依赖的其他任务"]
    }
  ],
  "open_issues": [
    "待跟进问题1",
    "待跟进问题2"
  ],
  "next_meeting": {
    "suggested_date": "2026-05-13",
    "topics": ["议题1", "议题2"]
  }
}
```

**Few-shot示例数**: 3个（不同会议类型：项目例会/需求评审/故障复盘）

**置信度要求**: ≥ 85%

---

### S15: 项目周报/月报自动生成

**场景描述**：
从ONES项目数据、工时数据、任务完成情况，自动生成结构化项目周报/月报。

**预期输入**：
```text
项目ID + 时间范围
ONES原始数据（任务完成情况、燃尽图、缺陷数据）
工时统计数据
风险事项记录
```

**预期输出**（JSON结构化，可直接导出Word）：
```json
{
  "report_period": "2026年第18周",
  "project_name": "项目名称",
  "overall_status": "🟢正常/🟡留意/🔴风险",
  "progress_summary": {
    "planned": "计划完成X个故事点",
    "actual": "实际完成Y个故事点",
    "completion_rate": "85%",
    "trend": "⬆️提升/➡️持平/⬇️下降"
  },
  "key_milestones": [
    {
      "name": "里程碑名称",
      "planned_date": "2026-05-15",
      "actual_date": "2026-05-14",
      "status": "✅已完成/🚧进行中/❌延期"
    }
  ],
  "risk_and_issues": [
    {
      "risk": "风险描述",
      "level": "🔴高/🟠中/🟡低",
      "mitigation": "应对措施",
      "owner": "责任人"
    }
  ],
  "team_performance": {
    "total_hours": 120,
    "average_utilization": "85%",
    "overload_person": ["人员A", "人员B"]
  },
  "next_week_plan": ["计划1", "计划2"],
  "needs_support": ["需要管理层协调的事项"]
}
```

**Few-shot示例数**: 4个（不同状态项目：正常/有风险/严重延期/刚启动）

**置信度要求**: ≥ 90%

---

### S16: 日志故障智能诊断

**场景描述**：
从系统日志、错误堆栈、监控告警等信息，自动分析故障根因，给出排查路径和解决方案。

**预期输入**：
```text
错误日志原文
异常堆栈信息
监控指标快照
发生时间线
```

**预期输出**（JSON结构化）：
```json
{
  "error_summary": {
    "error_type": "数据库连接超时/空指针异常/OOM等",
    "severity": "🔴P0/🟠P1/🟡P2",
    "occurrence_time": "2026-05-06 10:30:00",
    "impact_scope": "影响范围描述"
  },
  "symptom_analysis": [
    "症状1",
    "症状2"
  ],
  "root_cause_hypothesis": [
    {
      "hypothesis_id": "H1",
      "description": "根因假设1",
      "probability": "85%",
      "evidence": ["证据1", "证据2"]
    },
    {
      "hypothesis_id": "H2",
      "description": "根因假设2",
      "probability": "60%",
      "evidence": ["证据1"]
    }
  ],
  "troubleshooting_path": [
    {
      "step": 1,
      "action": "首先检查什么",
      "expected_result": "预期结果",
      "if_ok": "下一步",
      "if_not_ok": "排查方向"
    }
  ],
  "suggested_solution": [
    {
      "priority": 1,
      "solution": "解决方案1",
      "estimated_time": "30分钟",
      "risk": "操作风险说明"
    }
  ],
  "related_knowledge": ["关联的历史类似故障", "相关文档链接"]
}
```

**Few-shot示例数**: 5个（不同故障类型：数据库/网络/应用/资源/依赖）

**置信度要求**: ≥ 75%

---

## 🔧 模板库技术实现规范

### 统一存储结构
```python
# prompt_templates.py 统一入口
PROMPT_TEMPLATES = {
    "S11_requirement_prd": {
        "name": "需求结构化梳理&PRD初稿生成",
        "system_prompt": """系统Prompt...""",
        "few_shot_examples": [
            {"input": "...", "output": "..."},
            # 3-5个示例
        ],
        "output_schema": {...},  # JSON Schema
        "confidence_threshold": 0.85
    },
    # ... 其他15个场景
}
```

### 统一调用接口
```python
from orion import prompt_templates

# 获取模板
template = prompt_templates.get("S11_requirement_prd")

# 渲染Prompt
full_prompt = template.render(user_input=input_text)

# 调用大模型 + 结构化校验
result = template.execute(input_text, enable_llm=True)
```

---

## 📅 开发计划

| 阶段 | 内容 | 完成时间 |
|------|------|---------|
| Phase 0-1 | S01-S06（6个核心业务场景） | 5月7日 |
| Phase 0-2 | S11-S16（Rex补充6个研发场景） | 5月7日 |
| Phase 0-3 | S07-S10（剩余4个通用场景） | 5月8日 |

---

**版本**: v1.0 | **状态**: 🚀 开发中
