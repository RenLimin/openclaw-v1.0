---
name: agent-team-creator
description: 智能体团队创建专家 - 从0到1设计并创建完整的多智能体团队。支持多行业模板、角色专业化定义、标准通信协议、质量验证体系。使用场景：(1) 需要为特定业务领域创建智能体团队时，(2) 需要设计多智能体协作架构时，(3) 需要验证智能体团队质量时。
---

# 智能体团队创建专家

> **核心能力：** 从0到1创建完整的多智能体团队，遵循行业最佳实践

## 快速开始

### 生成智能体团队

```bash
# 生成软件研发行业完整团队
python scripts/generate_agent.py --industry software

# 生成金融服务行业团队
python scripts/generate_agent.py --industry finance

# 生成法律服务行业团队
python scripts/generate_agent.py --industry legal

# 输出到JSON文件
python scripts/generate_agent.py --industry software --output team_software.json
```

### 验证智能体团队质量

```bash
# 验证团队质量
python scripts/validate_agent.py --input team_software.json

# 输出验证报告
python scripts/validate_agent.py --input team_software.json --output validation_report.json
```

## 支持的行业模板

| 行业 | 预置角色 | 基础设施层 |
|------|---------|-----------|
| 软件研发 | 产品经理、架构师、开发工程师 | ✅ Nova/Orion/Luna |
| 金融服务 | 风控专家、财务分析师 | ✅ Nova/Orion/Luna |
| 法律服务 | 合同专家 | ✅ Nova/Orion/Luna |

## 标准三层架构

所有生成的团队都遵循标准三层架构：

```
协调层（1个）: 🦞 Jerry - 全局协调、质量管控、架构治理
    ↓
业务层（N个领域专家）: 根据行业配置4-8个专业Agent
    ↓
基础设施层（3个支撑Agent）: 🌟 Nova + 🌌 Orion + 🌙 Luna
```

## 质量验证体系

四重验证，交付前必须100%通过：

| 维度 | 权重 | 核心检查项 |
|------|------|---------|
| 🔐 安全闸门 | 75分 | 权限边界、通信协议、协调层审批 |
| 💰 成本控制 | 70分 | Orion调度、专业化分工 |
| ⚡ 性能指标 | 70分 | Luna监控、Nova技能管理 |
| 🧠 协作能力 | 85分 | 三层架构、12种消息类型、5种协作模式 |
| **总分** | **300分** | |

## 评级标准

- **S级（≥270分）**：完美！可以直接上线
- **A级（≥240分）**：优秀！可以上线
- **B级（≥210分）**：良好！建议修复后上线
- **C级（≥180分）**：及格！需要修复问题
- **D级（<180分）**：不合格！需要重大改进

## 脚本说明

### scripts/generate_agent.py
智能体生成器核心脚本，包含：
- 行业模板库（3个行业，10+预置角色）
- 基础设施Agent模板（Nova/Orion/Luna）
- 标准通信协议生成
- JSON格式输出

### scripts/validate_agent.py
质量验证器核心脚本，包含：
- 四重验证逻辑
- 五级评级体系
- 详细的验证报告生成
- 改进建议输出

## 扩展指南

### 添加新的行业模板

在 `generate_agent.py` 的 `INDUSTRY_TEMPLATES` 字典中添加新行业：

```python
"new_industry": {
    "roles": {
        "role_name": {
            "name": "角色名称",
            "emoji": "🎭",
            "goal": "核心目标",
            "background": "背景故事",
            "skills": ["技能1", "技能2"],
            "tools": ["工具1", "工具2"],
            "decision_authority": "决策权限"
        }
    }
}
```

### 添加新的验证规则

在 `validate_agent.py` 的对应验证方法中添加检查项。
