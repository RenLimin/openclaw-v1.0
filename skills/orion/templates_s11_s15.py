"""
Orion LLM调度框架 - Prompt模板 S11-S15
项目管理场景模板: 需求分析、风险管理、立项、会议纪要、周报
"""

from .templates_base import PromptTemplate, OutputFormat


# ==================== S11: 需求结构化梳理 & PRD初稿生成 ====================
TEMPLATE_S11 = PromptTemplate(
    template_id="S11",
    scenario_name="需求结构化梳理 & PRD初稿生成",
    system_prompt="""你是一位资深产品经理专家，擅长将模糊的业务需求转化为结构化的产品需求文档(PRD)。

你的任务是：
1. 首先对输入的原始需求进行结构化梳理，识别核心业务目标
2. 提取功能需求、非功能需求、约束条件
3. 识别用户角色和使用场景
4. 生成完整的PRD初稿框架

输出要求：
- 结构清晰，层次分明
- 每个功能点要有明确的验收标准
- 包含优先级评估
- 使用中文输出""",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "business_objective": {"type": "string", "description": "核心业务目标"},
            "background": {"type": "string", "description": "需求背景"},
            "user_roles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role_name": {"type": "string"},
                        "role_description": {"type": "string"}
                    }
                }
            },
            "functional_requirements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "feature_name": {"type": "string"},
                        "description": {"type": "string"},
                        "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
                        "priority": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]}
                    }
                }
            },
            "non_functional_requirements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "requirement": {"type": "string"}
                    }
                }
            },
            "constraints": {"type": "array", "items": {"type": "string"}},
            "use_cases": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scenario": {"type": "string"},
                        "steps": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "assumptions": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["business_objective", "functional_requirements"]
    },
    input_params=[
        {"name": "raw_requirement", "type": "string", "description": "原始需求描述文本"},
        {"name": "business_context", "type": "string", "description": "业务背景信息"},
        {"name": "stakeholders", "type": "array", "description": "相关方信息", "required": False}
    ],
    example_input={
        "raw_requirement": "我们需要做一个项目管理系统，能够创建项目、分配任务、跟踪进度",
        "business_context": "公司目前项目管理混乱，需要标准化流程"
    },
    example_output={
        "business_objective": "建立标准化的项目管理流程，提升团队协作效率",
        "functional_requirements": [
            {
                "feature_name": "项目创建",
                "priority": "P0",
                "acceptance_criteria": ["用户可以创建新项目", "支持设置项目名称、描述、截止日期"]
            }
        ]
    },
    tags=["产品", "需求分析", "PRD"]
)


# ==================== S12: 需求风险智能识别 ====================
TEMPLATE_S12 = PromptTemplate(
    template_id="S12",
    scenario_name="需求风险智能识别",
    system_prompt="""你是一位资深项目风险专家，擅长识别需求中的潜在风险。

请分析输入的需求文档，识别以下类型的风险：
1. 需求不明确或模糊的地方
2. 技术可行性风险
3. 范围蔓延风险
4. 依赖风险
5. 资源约束风险
6. 时间进度风险

对每个风险进行：
- 风险等级评估(高/中/低)
- 影响分析
- 缓解建议""",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "risk_summary": {"type": "string", "description": "总体风险评估摘要"},
            "overall_risk_level": {"type": "string", "enum": ["高", "中", "低"]},
            "risks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "risk_id": {"type": "string"},
                        "risk_type": {"type": "string"},
                        "risk_description": {"type": "string"},
                        "risk_level": {"type": "string", "enum": ["高", "中", "低"]},
                        "impact_analysis": {"type": "string"},
                        "mitigation_suggestion": {"type": "string"}
                    }
                }
            },
            "critical_path_risks": {"type": "array", "items": {"type": "string"}},
            "recommendations": {"type": "array", "items": {"type": "string"}}
        }
    },
    input_params=[
        {"name": "requirement_doc", "type": "string", "description": "需求文档内容"},
        {"name": "project_context", "type": "string", "description": "项目背景信息"}
    ],
    example_input={
        "requirement_doc": "系统需要支持百万级用户并发，下周上线",
        "project_context": "团队只有3人，都是新人"
    },
    example_output={
        "overall_risk_level": "高",
        "risks": [
            {
                "risk_type": "技术风险",
                "risk_level": "高",
                "mitigation_suggestion": "建议进行压力测试，考虑扩容方案"
            }
        ]
    },
    tags=["风险管理", "需求分析"]
)


# ==================== S13: 项目立项报告自动生成 ====================
TEMPLATE_S13 = PromptTemplate(
    template_id="S13",
    scenario_name="项目立项报告自动生成",
    system_prompt="""你是一位资深项目经理，擅长编写专业的项目立项报告。

请根据输入信息生成完整的项目立项报告，包含：
1. 项目概述
2. 项目背景与意义
3. 项目目标（SMART原则）
4. 项目范围
5. 预期收益分析
6. 关键成功因素
7. 主要风险与应对策略
8. 资源需求估算
9. 初步时间计划
10. 审批建议""",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "project_name": {"type": "string"},
            "project_overview": {"type": "string"},
            "background": {"type": "string"},
            "project_significance": {"type": "string"},
            "objectives": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "objective": {"type": "string"},
                        "kpi": {"type": "string"},
                        "target_value": {"type": "string"}
                    }
                }
            },
            "scope_in": {"type": "array", "items": {"type": "string"}},
            "scope_out": {"type": "array", "items": {"type": "string"}},
            "benefits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "benefit_type": {"type": "string"},
                        "description": {"type": "string"},
                        "estimated_value": {"type": "string"}
                    }
                }
            },
            "success_factors": {"type": "array", "items": {"type": "string"}},
            "risks": {"type": "array", "items": {"type": "object"}},
            "resource_estimate": {
                "headcount": {"type": "number"},
                "budget": {"type": "string"},
                "duration": {"type": "string"}
            },
            "timeline_milestones": {"type": "array", "items": {"type": "object"}},
            "approval_recommendation": {"type": "string"}
        }
    },
    input_params=[
        {"name": "project_brief", "type": "string", "description": "项目简要说明"},
        {"name": "stakeholder_input", "type": "string", "description": "相关方需求"},
        {"name": "budget_info", "type": "string", "description": "预算信息", "required": False}
    ],
    example_input={
        "project_brief": "OA系统升级项目，替换现有老旧系统",
        "stakeholder_input": "管理层要求6个月内完成"
    },
    example_output={
        "project_name": "OA系统升级项目",
        "approval_recommendation": "建议批准立项"
    },
    tags=["立项", "项目管理"]
)


# ==================== S14: 会议纪要 & 待办自动生成 ====================
TEMPLATE_S14 = PromptTemplate(
    template_id="S14",
    scenario_name="会议纪要 & 待办自动生成",
    system_prompt="""你是一位专业的会议纪要专家，擅长从会议录音/文字中提取关键信息。

请处理会议内容，生成：
1. 会议基本信息
2. 会议决议
3. 关键讨论要点
4. 待办事项清单（包含负责人、截止时间）
5. 后续跟进建议

待办事项必须清晰标注：任务描述、负责人、截止时间、优先级。""",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "meeting_title": {"type": "string"},
            "meeting_date": {"type": "string"},
            "attendees": {"type": "array", "items": {"type": "string"}},
            "absentees": {"type": "array", "items": {"type": "string"}},
            "meeting_summary": {"type": "string"},
            "key_decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "decision": {"type": "string"},
                        "background": {"type": "string"}
                    }
                }
            },
            "discussion_points": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "summary": {"type": "string"}
                    }
                }
            },
            "action_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "task_description": {"type": "string"},
                        "assignee": {"type": "string"},
                        "deadline": {"type": "string"},
                        "priority": {"type": "string", "enum": ["高", "中", "低"]},
                        "status": {"type": "string", "default": "待开始"}
                    }
                }
            },
            "next_meeting": {"type": "string"},
            "follow_up_suggestions": {"type": "array", "items": {"type": "string"}}
        }
    },
    input_params=[
        {"name": "meeting_content", "type": "string", "description": "会议内容文本/转录"},
        {"name": "meeting_metadata", "type": "object", "description": "会议元数据（标题、时间、参会人等）"}
    ],
    example_input={
        "meeting_content": "张三说下周五前完成需求文档，李四负责技术方案评审",
        "meeting_metadata": {"title": "项目周会", "date": "2024-01-15"}
    },
    example_output={
        "action_items": [
            {
                "task_description": "完成需求文档",
                "assignee": "张三",
                "deadline": "2024-01-22",
                "priority": "高"
            }
        ]
    },
    tags=["会议纪要", "待办", "协作"]
)


# ==================== S15: 项目周报自动生成 ====================
TEMPLATE_S15 = PromptTemplate(
    template_id="S15",
    scenario_name="项目周报自动生成",
    system_prompt="""你是一位专业的项目经理，擅长撰写清晰、专业的项目周报。

请根据输入的项目数据生成周报，包含：
1. 本周工作完成情况
2. 进度偏差分析
3. 下周工作计划
4. 风险与问题
5. 需要协调的事项
6. 关键指标展示

要求：数据驱动，重点突出，清晰易读。""",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "project_name": {"type": "string"},
            "report_week": {"type": "string"},
            "project_manager": {"type": "string"},
            "overall_status": {"type": "string", "enum": ["正常", "预警", "延期"]},
            "completion_summary": {"type": "string"},
            "this_week_completed": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task_name": {"type": "string"},
                        "planned": {"type": "string"},
                        "actual": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }
            },
            "schedule_analysis": {
                "planned_progress": {"type": "number"},
                "actual_progress": {"type": "number"},
                "variance": {"type": "number"},
                "variance_reason": {"type": "string"}
            },
            "next_week_plan": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task_name": {"type": "string"},
                        "assignee": {"type": "string"},
                        "planned_date": {"type": "string"}
                    }
                }
            },
            "risks_and_issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "impact": {"type": "string"},
                        "action_plan": {"type": "string"}
                    }
                }
            },
            "coordination_needed": {"type": "array", "items": {"type": "string"}},
            "key_metrics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "metric_name": {"type": "string"},
                        "current_value": {"type": "string"},
                        "trend": {"type": "string"}
                    }
                }
            }
        }
    },
    input_params=[
        {"name": "project_data", "type": "object", "description": "项目基础数据"},
        {"name": "task_statuses", "type": "array", "description": "任务状态列表"},
        {"name": "week_range", "type": "string", "description": "报告周范围"}
    ],
    example_input={
        "project_data": {"name": "OA系统升级"},
        "task_statuses": [{"name": "需求分析", "status": "已完成"}],
        "week_range": "2024-W03"
    },
    example_output={
        "overall_status": "正常",
        "this_week_completed": []
    },
    tags=["周报", "项目管理", "进度跟踪"]
)


# S11-S15模板字典
TEMPLATES_S11_S15 = {
    "S11": TEMPLATE_S11,
    "S12": TEMPLATE_S12,
    "S13": TEMPLATE_S13,
    "S14": TEMPLATE_S14,
    "S15": TEMPLATE_S15,
}
