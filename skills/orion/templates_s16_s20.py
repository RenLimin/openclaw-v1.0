"""
Orion LLM调度框架 - Prompt模板 S16-S20
项目管理场景模板: 月报、健康度评估、验收、复盘、经验推荐
"""

from typing import Dict, Any
from .templates_base import PromptTemplate, OutputFormat


# ==================== S16: 项目月报自动生成 ====================
TEMPLATE_S16 = PromptTemplate(
    template_id="S16",
    scenario_name="项目月报自动生成",
    system_prompt="""你是一位资深项目管理专家，擅长撰写面向管理层的项目月报。

请生成面向管理层的项目月报，包含：
1. 本月整体回顾
2. 关键里程碑达成情况
3. 核心指标表现
4. 重大问题与风险
5. 资源使用情况
6. 下月重点计划
7. 变更请求汇总
8. 管理层决策建议""",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "project_name": {"type": "string"},
            "report_month": {"type": "string"},
            "executive_summary": {"type": "string"},
            "overall_health": {"type": "string", "enum": ["健康", "关注", "危险"]},
            "milestone_status": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "milestone": {"type": "string"},
                        "planned_date": {"type": "string"},
                        "actual_date": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }
            },
            "monthly_achievements": {"type": "array", "items": {"type": "string"}},
            "key_metrics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "metric": {"type": "string"},
                        "target": {"type": "string"},
                        "actual": {"type": "string"},
                        "trend": {"type": "string"}
                    }
                }
            },
            "major_issues": {"type": "array", "items": {"type": "object"}},
            "resource_utilization": {
                "planned_hours": {"type": "number"},
                "actual_hours": {"type": "number"},
                "utilization_rate": {"type": "number"},
                "budget_variance": {"type": "string"}
            },
            "change_requests": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "cr_id": {"type": "string"},
                        "description": {"type": "string"},
                        "impact": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }
            },
            "next_month_focus": {"type": "array", "items": {"type": "string"}},
            "management_recommendations": {"type": "array", "items": {"type": "string"}}
        }
    },
    input_params=[
        {"name": "project_monthly_data", "type": "object", "description": "项目月度数据"},
        {"name": "milestones", "type": "array", "description": "里程碑列表"},
        {"name": "report_month", "type": "string", "description": "报告月份"}
    ],
    example_input={
        "project_monthly_data": {"name": "OA系统升级"},
        "report_month": "2024-01"
    },
    example_output={
        "overall_health": "健康"
    },
    tags=["月报", "项目管理", "管理层汇报"]
)


# ==================== S17: 项目健康度智能评估 ====================
TEMPLATE_S17 = PromptTemplate(
    template_id="S17",
    scenario_name="项目健康度智能评估",
    system_prompt="""你是一位项目健康度诊断专家，擅长从多个维度全面评估项目状态。

请从以下维度进行项目健康度评估：
1. 进度健康度
2. 成本健康度
3. 范围健康度
4. 质量健康度
5. 团队健康度
6. 利益相关方满意度
7. 风险水平

每个维度评分0-100分，给出具体的评估理由和改进建议。""",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "project_name": {"type": "string"},
            "assessment_date": {"type": "string"},
            "overall_health_score": {"type": "number"},
            "overall_health_level": {"type": "string", "enum": ["优秀", "良好", "一般", "较差", "危险"]},
            "dimension_scores": {
                "type": "object",
                "properties": {
                    "schedule_health": {
                        "score": {"type": "number"},
                        "level": {"type": "string"},
                        "assessment": {"type": "string"},
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "suggestions": {"type": "array", "items": {"type": "string"}}
                    },
                    "cost_health": {
                        "score": {"type": "number"},
                        "level": {"type": "string"},
                        "assessment": {"type": "string"},
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "suggestions": {"type": "array", "items": {"type": "string"}}
                    },
                    "scope_health": {
                        "score": {"type": "number"},
                        "level": {"type": "string"},
                        "assessment": {"type": "string"},
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "suggestions": {"type": "array", "items": {"type": "string"}}
                    },
                    "quality_health": {
                        "score": {"type": "number"},
                        "level": {"type": "string"},
                        "assessment": {"type": "string"},
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "suggestions": {"type": "array", "items": {"type": "string"}}
                    },
                    "team_health": {
                        "score": {"type": "number"},
                        "level": {"type": "string"},
                        "assessment": {"type": "string"},
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "suggestions": {"type": "array", "items": {"type": "string"}}
                    },
                    "stakeholder_health": {
                        "score": {"type": "number"},
                        "level": {"type": "string"},
                        "assessment": {"type": "string"},
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "suggestions": {"type": "array", "items": {"type": "string"}}
                    },
                    "risk_health": {
                        "score": {"type": "number"},
                        "level": {"type": "string"},
                        "assessment": {"type": "string"},
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "suggestions": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "key_strengths": {"type": "array", "items": {"type": "string"}},
            "critical_issues": {"type": "array", "items": {"type": "string"}},
            "immediate_actions": {"type": "array", "items": {"type": "string"}},
            "long_term_recommendations": {"type": "array", "items": {"type": "string"}}
        }
    },
    input_params=[
        {"name": "project_snapshot", "type": "object", "description": "项目当前快照数据"},
        {"name": "historical_data", "type": "object", "description": "历史数据对比"}
    ],
    example_input={
        "project_snapshot": {"name": "OA系统升级", "progress": 75}
    },
    example_output={
        "overall_health_score": 82,
        "overall_health_level": "良好"
    },
    tags=["健康度评估", "项目诊断", "风险管理"]
)


# ==================== S18: 验收报告自动生成 ====================
TEMPLATE_S18 = PromptTemplate(
    template_id="S18",
    scenario_name="验收报告自动生成",
    system_prompt="""你是一位专业的项目验收专家，擅长编写规范的项目验收报告。

请生成项目验收报告，包含：
1. 验收基本信息
2. 验收范围
3. 验收标准与依据
4. 验收测试结果
5. 遗留问题与处理方案
6. 验收结论
7. 交接清单
8. 后续运维建议""",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "project_name": {"type": "string"},
            "acceptance_date": {"type": "string"},
            "acceptance_scope": {"type": "string"},
            "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
            "acceptance_basis": {"type": "array", "items": {"type": "string"}},
            "acceptance_team": {"type": "array", "items": {"type": "string"}},
            "test_results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "test_item": {"type": "string"},
                        "expected_result": {"type": "string"},
                        "actual_result": {"type": "string"},
                        "status": {"type": "string", "enum": ["通过", "不通过", "有条件通过"]},
                        "remarks": {"type": "string"}
                    }
                }
            },
            "summary_statistics": {
                "total_items": {"type": "number"},
                "passed": {"type": "number"},
                "failed": {"type": "number"},
                "conditional": {"type": "number"},
                "pass_rate": {"type": "number"}
            },
            "outstanding_issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "issue_id": {"type": "string"},
                        "description": {"type": "string"},
                        "severity": {"type": "string"},
                        "handling_plan": {"type": "string"},
                        "responsible_party": {"type": "string"},
                        "deadline": {"type": "string"}
                    }
                }
            },
            "acceptance_conclusion": {"type": "string", "enum": ["验收通过", "有条件通过", "验收不通过"]},
            "conclusion_details": {"type": "string"},
            "handover_checklist": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item": {"type": "string"},
                        "handover_status": {"type": "string"},
                        "recipient": {"type": "string"}
                    }
                }
            },
            "operations_maintenance_suggestions": {"type": "array", "items": {"type": "string"}},
            "appendices": {"type": "array", "items": {"type": "string"}}
        }
    },
    input_params=[
        {"name": "project_info", "type": "object", "description": "项目基本信息"},
        {"name": "test_records", "type": "array", "description": "测试记录"},
        {"name": "acceptance_criteria_doc", "type": "string", "description": "验收标准文档"}
    ],
    example_input={
        "project_info": {"name": "OA系统升级"},
        "test_records": [{"item": "登录功能", "status": "通过"}]
    },
    example_output={
        "acceptance_conclusion": "验收通过"
    },
    tags=["验收", "项目交付", "质量管理"]
)


# ==================== S19: 项目复盘经验自动提取 ====================
TEMPLATE_S19 = PromptTemplate(
    template_id="S19",
    scenario_name="项目复盘经验自动提取",
    system_prompt="""你是一位项目复盘专家，擅长从项目历史数据中提取有价值的经验教训。

请进行项目复盘，提取以下经验：
1. 做得好的地方（最佳实践）
2. 需要改进的地方
3. 根因分析
4. 可复用的方法和工具
5. 避免的坑
6. 对未来项目的建议

要求：客观、具体、可落地。每条经验要有具体的场景支撑。""",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "project_name": {"type": "string"},
            "review_date": {"type": "string"},
            "project_duration": {"type": "string"},
            "project_outcome": {"type": "string"},
            "key_highlights": {"type": "string"},
            "best_practices": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "practice": {"type": "string"},
                        "description": {"type": "string"},
                        "benefit": {"type": "string"},
                        "applicable_scenarios": {"type": "array", "items": {"type": "string"}},
                        "reusability_score": {"type": "number"}
                    }
                }
            },
            "areas_for_improvement": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "area": {"type": "string"},
                        "description": {"type": "string"},
                        "root_cause": {"type": "string"},
                        "impact": {"type": "string"},
                        "improvement_action": {"type": "string"}
                    }
                }
            },
            "lessons_learned": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "lesson": {"type": "string"},
                        "category": {"type": "string"},
                        "specific_scenario": {"type": "string"},
                        "actionable_advice": {"type": "string"}
                    }
                }
            },
            "pitfalls_avoided": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "pitfall": {"type": "string"},
                        "how_avoided": {"type": "string"},
                        "potential_impact": {"type": "string"}
                    }
                }
            },
            "reusable_tools_methods": {"type": "array", "items": {"type": "string"}},
            "future_project_recommendations": {"type": "array", "items": {"type": "string"}},
            "knowledge_tags": {"type": "array", "items": {"type": "string"}}
        }
    },
    input_params=[
        {"name": "project_history", "type": "object", "description": "项目历史数据"},
        {"name": "team_feedback", "type": "array", "description": "团队反馈"},
        {"name": "stakeholder_comments", "type": "string", "description": "相关方评价"}
    ],
    example_input={
        "project_history": {"name": "OA系统升级", "duration": "6个月"},
        "team_feedback": ["需求变更太频繁"]
    },
    example_output={
        "lessons_learned": []
    },
    tags=["复盘", "经验总结", "知识管理"]
)


# ==================== S20: 相似项目经验推荐 ====================
TEMPLATE_S20 = PromptTemplate(
    template_id="S20",
    scenario_name="相似项目经验推荐",
    system_prompt="""你是一位知识管理专家，擅长根据当前项目特征推荐历史项目的相关经验。

请基于当前项目信息，从知识库中推荐：
1. 最相似的3-5个历史项目
2. 可直接复用的成功经验
3. 需要注意规避的风险
4. 推荐的方法论和工具
5. 关键里程碑的时间参考

相似度计算维度：行业、规模、技术栈、团队规模、项目类型。""",
    output_format=OutputFormat.JSON,
    output_schema={
        "type": "object",
        "properties": {
            "current_project": {"type": "string"},
            "recommendation_date": {"type": "string"},
            "similar_projects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string"},
                        "similarity_score": {"type": "number"},
                        "similarity_dimensions": {"type": "array", "items": {"type": "string"}},
                        "key_lessons": {"type": "array", "items": {"type": "string"}},
                        "outcome": {"type": "string"}
                    }
                }
            },
            "reusable_success_experiences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "experience": {"type": "string"},
                        "source_project": {"type": "string"},
                        "applicability": {"type": "string"},
                        "implementation_steps": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "risks_to_avoid": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "risk": {"type": "string"},
                        "source_project": {"type": "string"},
                        "how_it_happened": {"type": "string"},
                        "prevention_measures": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "recommended_methods_tools": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "use_case": {"type": "string"},
                        "expected_benefit": {"type": "string"}
                    }
                }
            },
            "milestone_timeline_reference": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "milestone": {"type": "string"},
                        "typical_duration": {"type": "string"},
                        "reference_projects": {"type": "array", "items": {"type": "string"}},
                        "key_notes": {"type": "string"}
                    }
                }
            },
            "overall_suggestion": {"type": "string"}
        }
    },
    input_params=[
        {"name": "current_project_profile", "type": "object", "description": "当前项目特征画像"},
        {"name": "knowledge_base", "type": "array", "description": "历史项目知识库"}
    ],
    example_input={
        "current_project_profile": {"industry": "互联网", "tech_stack": ["Python", "React"]}
    },
    example_output={
        "similar_projects": []
    },
    tags=["知识推荐", "经验复用", "项目相似度"]
)


# S16-S20模板字典
TEMPLATES_S16_S20 = {
    "S16": TEMPLATE_S16,
    "S17": TEMPLATE_S17,
    "S18": TEMPLATE_S18,
    "S19": TEMPLATE_S19,
    "S20": TEMPLATE_S20,
}
