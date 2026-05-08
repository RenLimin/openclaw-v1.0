#!/usr/bin/env python3
"""
智能体生成器 - Agent Generator
根据业务需求自动生成完整的智能体定义
遵循CrewAI风格的专业化角色定义
"""

import json
import argparse
from typing import Dict, List
from datetime import datetime

# 行业模板库
INDUSTRY_TEMPLATES = {
    "software": {
        "roles": {
            "product_manager": {
                "name": "Product Manager",
                "emoji": "🎯",
                "goal": "确保产品符合用户需求，按时高质量交付",
                "background": "10年产品管理经验，擅长需求分析，对用户体验有极致追求",
                "skills": ["需求分析", "产品设计", "项目管理", "用户研究", "竞品分析"],
                "tools": ["文档编写", "原型设计", "数据分析", "会议协调"],
                "decision_authority": "产品方向最终决策权"
            },
            "architect": {
                "name": "Architect",
                "emoji": "🏗️",
                "goal": "系统架构设计合理，技术选型最优",
                "background": "资深架构师，15年开发经验，对代码质量有洁癖",
                "skills": ["系统设计", "技术选型", "代码审查", "性能优化", "安全设计"],
                "tools": ["架构设计", "代码审查", "性能测试"],
                "decision_authority": "技术架构最终决策权"
            },
            "developer": {
                "name": "Developer",
                "emoji": "💻",
                "goal": "高质量代码交付，bug-free",
                "background": "全栈开发工程师，精通前后端技术",
                "skills": ["前端开发", "后端开发", "数据库设计", "API设计", "单元测试"],
                "tools": ["代码编写", "调试", "Git", "Docker"],
                "decision_authority": "技术实现方案决策权"
            }
        }
    },
    "finance": {
        "roles": {
            "risk_control": {
                "name": "Risk Control Expert",
                "emoji": "🛡️",
                "goal": "零风险敞口，100%合规",
                "background": "前银行风控总监，12年风控经验，风险嗅觉敏锐",
                "skills": ["风险评估", "合规审查", "风险建模", "合规审计"],
                "tools": ["风险模型", "合规检查", "数据分析"],
                "decision_authority": "风险判定最终决策权"
            },
            "financial_analyst": {
                "name": "Financial Analyst",
                "emoji": "📊",
                "goal": "数据准确，洞察深刻",
                "background": "CFA持证人，前四大会计师事务所经验",
                "skills": ["财务分析", "预算管理", "成本控制", "财务建模"],
                "tools": ["Excel高级", "财务模型", "可视化"],
                "decision_authority": "财务数据质量判定权"
            }
        }
    },
    "legal": {
        "roles": {
            "contract_expert": {
                "name": "Contract Expert",
                "emoji": "📜",
                "goal": "零合同风险，100%法律合规",
                "background": "前公司法务总监，10年法律从业经验",
                "skills": ["合同审核", "合规审查", "法律研究", "风险识别"],
                "tools": ["合同解析", "法律检索", "OCR"],
                "decision_authority": "合同风险最终判定权"
            }
        }
    }
}

# 通用基础设施Agent模板
INFRASTRUCTURE_AGENTS = {
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

def generate_agent(role_type: str, industry: str = "software") -> Dict:
    """生成单个Agent定义"""
    industry_templates = INDUSTRY_TEMPLATES.get(industry, INDUSTRY_TEMPLATES["software"])
    
    if role_type in industry_templates["roles"]:
        return industry_templates["roles"][role_type]
    
    # 如果没有匹配，返回基础模板
    return {
        "name": role_type.replace("_", " ").title(),
        "emoji": "🤖",
        "goal": f"负责{role_type}相关工作",
        "background": "专业领域专家",
        "skills": ["专业技能"],
        "tools": ["标准工具"],
        "decision_authority": "职责范围内决策权"
    }

def generate_team(industry: str, include_infra: bool = True) -> Dict:
    """生成完整的智能体团队"""
    team = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "industry": industry,
        "coordination_layer": {},
        "business_layer": {},
        "infrastructure_layer": {}
    }
    
    # 协调层 - Jerry
    team["coordination_layer"] = {
        "jerry": {
            "name": "Jerry",
            "emoji": "🦞",
            "goal": "确保整体高效高质量安全运行",
            "background": "10年智能体团队管理经验，熟悉全流程",
            "skills": ["全局协调", "质量管控", "架构治理", "风险控制"],
            "tools": ["所有协调权限"],
            "decision_authority": "重大问题最终裁决"
        }
    }
    
    # 业务层
    if industry in INDUSTRY_TEMPLATES:
        team["business_layer"] = INDUSTRY_TEMPLATES[industry]["roles"]
    
    # 基础设施层
    if include_infra:
        team["infrastructure_layer"] = INFRASTRUCTURE_AGENTS
    
    # 生成通信协议配置
    team["communication_protocol"] = {
        "version": "1.0",
        "message_types": [
            "TASK_ASSIGN", "TASK_DELEGATE", "TASK_RESULT",
            "DATA_REQUEST", "DATA_RESPONSE", "VALIDATION_REQUEST",
            "VALIDATION_RESULT", "CONSENSUS_REQUEST", "CONSENSUS_RESULT",
            "ERROR_REPORT", "FEEDBACK", "HEARTBEAT"
        ],
        "collaboration_modes": [
            "任务分配", "任务委托", "交叉验证", "共识决策", "端到端流水线"
        ]
    }
    
    return team

def main():
    parser = argparse.ArgumentParser(description="智能体生成器")
    parser.add_argument("--industry", type=str, default="software",
                       help="行业类型: software, finance, legal")
    parser.add_argument("--role", type=str, help="生成单个角色")
    parser.add_argument("--output", type=str, help="输出文件路径")
    parser.add_argument("--include-infra", action="store_true", default=True,
                       help="包含基础设施Agent")
    
    args = parser.parse_args()
    
    if args.role:
        result = generate_agent(args.role, args.industry)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        result = generate_team(args.industry, args.include_infra)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 已保存到: {args.output}")

if __name__ == "__main__":
    main()
