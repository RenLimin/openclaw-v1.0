# Orion LLM调度框架 v1.0

企业级LLM应用编排框架，专为项目管理场景设计。

## 功能特性

### 1. Prompt模板管理
- **10个项目管理场景模板** (S11-S20)
- 每个模板包含：系统提示词 + 输出格式定义 + 输入参数说明 + 示例
- 数据库表结构定义 (prompt_templates)

### 2. 统一调用接口 (LLMClient)
```python
from orion import LLMClient

client = LLMClient()
result = client.call(scenario="S11", data={...}, enable_llm=False)
```

- **enable_llm=False** (默认): 规则生成模式，返回模板化占位数据
- **enable_llm=True**: 真实LLM调用模式
- 内置结构化输出校验
- 自动Token成本统计

### 3. 结构化输出校验
- JSON Schema完整校验
- 业务规则校验（日期格式、邮箱格式、枚举值等）
- 错误详情和修复建议
- 支持严格/警告/宽松三种校验级别

### 4. Token成本统计
- 多模型定价支持 (OpenAI、通义千问、豆包、DeepSeek等)
- 实时成本估算
- 按场景/日期/模型维度统计
- 预算控制与超支检查

## 项目管理场景模板 (S11-S20)

| ID | 场景名称 | 说明 |
|----|---------|------|
| S11 | 需求结构化梳理 & PRD初稿生成 | 将模糊需求转化为结构化PRD |
| S12 | 需求风险智能识别 | 识别需求中的潜在风险点 |
| S13 | 项目立项报告自动生成 | 生成专业的项目立项报告 |
| S14 | 会议纪要 & 待办自动生成 | 提取会议决议和待办事项 |
| S15 | 项目周报自动生成 | 生成数据驱动的项目周报 |
| S16 | 项目月报自动生成 | 生成面向管理层的月报 |
| S17 | 项目健康度智能评估 | 多维度评估项目健康状况 |
| S18 | 验收报告自动生成 | 生成规范的项目验收报告 |
| S19 | 项目复盘经验自动提取 | 从项目中提取经验教训 |
| S20 | 相似项目经验推荐 | 基于相似度推荐历史经验 |

## 快速开始

### 安装依赖
```bash
pip install jsonschema
```

### 基本使用

```python
from orion import LLMClient

# 初始化客户端
client = LLMClient(model_name="gpt-3.5-turbo")

# 1. 规则模式 (不调用LLM)
result = client.call(
    scenario="S11",
    data={
        "raw_requirement": "我们需要做一个项目管理系统",
        "project_data": {"name": "项目管理系统V1.0"}
    },
    enable_llm=False
)

print(result.data)  # 结构化输出
```

### 成本预估

```python
# 预估调用成本
estimate = client.estimate_cost("S11", {"raw_requirement": "测试需求"})
print(f"预估成本: ¥{estimate['estimated_total_cost']:.4f}")
```

### 输出校验

```python
from orion import validate_output, get_template

template = get_template("S11")
result = validate_output(data, template.output_schema)

if result.is_valid:
    print("校验通过")
else:
    for error in result.errors:
        print(f"{error.field_path}: {error.message}")
```

## 文件结构

```
orion/
├── __init__.py      # 包导出文件
├── client.py        # LLM统一调用客户端
├── templates.py     # Prompt模板管理
├── validator.py     # 结构化输出校验
├── cost_tracker.py  # Token成本统计
├── example.py       # 使用示例
└── README.md        # 本文档
```

## 数据库表结构

prompt_templates表（MySQL）：

```sql
CREATE TABLE prompt_templates (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    template_id VARCHAR(32) UNIQUE NOT NULL COMMENT '模板ID: S11, S12等',
    scenario_name VARCHAR(128) NOT NULL COMMENT '场景名称',
    system_prompt TEXT NOT NULL COMMENT '系统提示词',
    output_format VARCHAR(32) DEFAULT 'json' COMMENT '输出格式',
    output_schema JSON COMMENT '输出格式定义(JSON Schema)',
    input_params JSON COMMENT '输入参数说明列表',
    example_input JSON COMMENT '示例输入',
    example_output JSON COMMENT '示例输出',
    version VARCHAR(16) DEFAULT '1.0' COMMENT '版本号',
    tags JSON COMMENT '标签列表',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用',
    token_cost_estimate INTEGER DEFAULT 0 COMMENT '预估Token消耗',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_template_id (template_id),
    INDEX idx_scenario (scenario_name)
) COMMENT='Prompt模板表';
```

## 运行示例

```bash
cd orion
python3 example.py
```

## 版本历史

- **v1.0.0** (2024-05-06): 初始版本，包含完整的框架实现和10个场景模板
