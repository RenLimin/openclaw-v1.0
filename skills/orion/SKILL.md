# SKILL.md - Orion LLM调度框架

## 技能概述

**技能名称**: Orion - 项目管理AI辅助工具集
**技能版本**: 1.0.0
**技能类型**: 工具框架 - 项目管理

## 功能描述

Orion 是专为项目管理场景设计的LLM调度框架，提供从需求分析到项目复盘的全流程AI辅助能力。包含10个核心Prompt模板，覆盖项目全生命周期管理。

## 核心能力

### 1. 需求管理 (S11-S12)
- **S11**: 需求结构化梳理 & PRD初稿生成
- **S12**: 需求风险智能识别

### 2. 项目启动 (S13)
- **S13**: 项目立项报告自动生成

### 3. 团队协作 (S14)
- **S14**: 会议纪要 & 待办事项自动生成

### 4. 项目跟踪与汇报 (S15-S17)
- **S15**: 项目周报自动生成
- **S16**: 项目月报自动生成
- **S17**: 项目健康度智能评估

### 5. 项目交付 (S18)
- **S18**: 验收报告自动生成

### 6. 知识沉淀与复用 (S19-S20)
- **S19**: 项目复盘经验自动提取
- **S20**: 相似项目经验推荐

## 模块结构

```
orion/
├── templates_base.py       # 基础类和表结构定义
├── templates_s11_s15.py  # S11-S15项目管理模板
├── templates_s16_s20.py  # S16-S20项目管理模板
├── templates.py          # 统一入口和注册表
├── validator.py          # JSON Schema验证器
├── cost_tracker.py     # 成本追踪器
├── client.py          # API客户端
├── example.py         # 使用示例
├── requirements.txt   # 依赖声明
├── README.md          # 详细文档
└── SKILL.md           # 本文件
```

## 适用场景

- **研发项目管理
- IT项目交付
- 跨团队协作项目
- 需要标准化项目流程的团队
- 需要沉淀项目经验的组织

## 使用方法

### 基本使用
```python
from skills.orion.templates import get_template, build_prompt

# 获取模板
template = get_template("S15")  # 项目周报模板

# 构建Prompt
prompt = build_prompt("S15", {
    "project_data": {"name": "OA系统升级"},
    "task_statuses": [...]
})
```

### 获取所有模板
```python
from skills.orion.templates import get_all_templates

templates = get_all_templates()
for template_id, template in templates.items():
    print(f"{template_id}: {template.scenario_name}")
```

### 验证输出
```python
from skills.orion.validator import OutputValidator

validator = OutputValidator()
result = validator.validate_output("S15", llm_output)
```

## 依赖项

- `jsonschema>=4.0.0` - JSON Schema验证
- `pydantic>=2.0.0` - 数据验证

## 扩展新模板

1. 在对应模板文件中添加新的`PromptTemplate`实例
2. 在模板字典中注册新模板
3. 编写对应的JSON Schema
4. 添加输入输出示例

## 版本历史

### v1.0.0 (2026-05-06)
- 完成S11-S20共10个项目管理模板
- 实现模板拆分（S11-S15, S16-S20）
- 集成JSON Schema验证器
- 实现成本追踪器
