# 履约义务拆分业务技能

> 打通 OCR 识别 → 条款拆分 → 义务提取 → 标准比对 → Excel 导出的完整业务流程

## 📋 功能概述

| 阶段 | 功能 | 说明 |
|------|------|------|
| 1 | 文件解析 | 自动识别 PDF / Word / 图片格式 |
| 2 | OCR 智能识别 | 调用 ocr-engine，支持扫描版合同 |
| 3 | 条款边界识别 | 智能合并跨页/跨行内容 |
| 4 | 义务类型识别 | 自动识别 6 大类履约义务 |
| 5 | 字段自动提取 | 履行时间、责任方、金额/比例 |
| 6 | 标准产品匹配 | 从合同文本自动识别产品编码 |
| 7 | 义务比对 | 自动比对合同义务与标准定义差异 |
| 8 | 风险等级评估 | 自动评估高/中/低风险，标注法条依据 |
| 9 | Excel 导出 | 3 个 Sheet 结构化输出 |
| 10 | 审核报告 | Markdown 格式审核报告 |

## 📁 目录结构

```
contract-obligation-split/
├── README.md                           # 本文档
├── SKILL.md                            # 技能说明文档
├── DEPENDENCIES.md                     # 依赖清单
├── config/
│   └── config.yaml                     # 运行配置
├── scripts/
│   ├── __init__.py
│   └── obligation_splitter.py          # 主流程引擎
├── templates/                          # Excel 模板（动态生成）
└── tests/
    ├── sample_contract.md              # 测试用合同文本
    └── test_obligation_split.py        # 测试脚本
```

## 🚀 快速开始

### 1. 检查依赖

```bash
python3 skills/contract-obligation-split/scripts/obligation_splitter.py --check-deps
```

### 2. 运行测试

```bash
python3 skills/contract-obligation-split/tests/test_obligation_split.py
```

### 3. 完整拆分流程

```bash
# 完整拆分 + 导出 Excel
python3 skills/contract-obligation-split/scripts/obligation_splitter.py \
    --input 合同文件.pdf \
    --output 义务明细表.xlsx

# 指定产品编码（跳过自动匹配）
python3 skills/contract-obligation-split/scripts/obligation_splitter.py \
    --input 合同文件.pdf \
    --product-code AS-SERVER-001 \
    --output 义务明细表.xlsx

# 仅预览结果，不导出文件
python3 skills/contract-obligation-split/scripts/obligation_splitter.py \
    --input 合同文件.pdf \
    --preview
```

## 📊 输出说明

### Excel 文件包含 3 个 Sheet

**Sheet1: 履约义务汇总**
- 序号、义务类型、义务内容、履行时间、责任方、金额/比例、风险等级、法条依据、备注

**Sheet2: 差异比对报告**
- 标准义务、合同义务、差异类型、差异说明、建议处理

**Sheet3: 合同条款原文**
- 条款编号、分类标签、完整条款内容

### Markdown 审核报告
- 风险概览（整体风险等级 + 明细）
- 履约义务汇总表
- 差异比对详情
- 处理建议
- 相关法条依据

## ⚙️ 配置说明

编辑 `config/config.yaml` 可以自定义：

### 义务类型定义
```yaml
obligation_types:
  - code: "payment"
    name: "付款义务"
    keywords: ["支付", "付款", "款项", ...]
    core_features: ["甲方应在", "支付方式", ...]
```

预置 6 种义务类型：
- 付款义务
- 交付义务
- 验收义务
- 质保义务
- 保密义务
- 违约责任

### 字段提取规则
```yaml
extraction_rules:
  performance_time:
    - pattern: "([0-9]{1,2})[个]?工作日内"
      desc: "X个工作日内"
```

### 风险评估规则
```yaml
risk_assessment:
  high_risk:
    threshold: 80
    conditions: ["缺失核心付款义务条款", ...]
    legal_basis: ["民法典第509条", ...]
```

### 标准产品库
```yaml
product_library:
  - product_code: "AS-SERVER-001"
    product_name: "标准服务器交付"
    obligations:
      - type: "delivery"
        content: "乙方应在合同生效后30个工作日内完成交付"
        ...
```

## 🔗 依赖技能

本技能依赖以下底层能力：

| 技能 | 用途 |
|------|------|
| **ocr-engine** | OCR 文档识别，扫描版 PDF 处理 |
| **contract-clause-split** | 合同条款边界识别逻辑 |
| **excel-engine** | Excel 高性能读写与格式化 |

## 🧪 测试覆盖

- ✅ 依赖检查
- ✅ 条款拆分
- ✅ 义务类型识别
- ✅ 字段提取（履行时间、责任方、金额）
- ✅ 产品匹配
- ✅ 义务比对
- ✅ 风险评估
- ✅ 审核报告生成

## 📝 使用示例

### Python 模块调用

```python
import sys
sys.path.append('skills/contract-obligation-split/scripts')

from obligation_splitter import ObligationSplitter

# 初始化
splitter = ObligationSplitter()

# 运行完整流程
result = splitter.run_full_pipeline(
    input_file='合同.pdf',
    output_file='义务明细表.xlsx',
    product_code='AS-SERVER-001'
)

# 查看结果
print(f"提取义务: {len(result['obligations'])} 项")
print(f"发现差异: {len(result['differences'])} 处")
print(f"整体风险: {result['risk_summary']['overall_level']}")
```

## ⚠️ 注意事项

1. **扫描版 PDF**: 自动检测并调用 OCR 引擎，识别精度依赖 Tesseract
2. **产品匹配**: 自动匹配不到时需手动指定 `--product-code`
3. **风险评估**: 基于规则的初步评估，重要合同建议人工复核
4. **大文件**: 超过 50 页的合同建议分段处理

## 📈 版本历史

- **v1.0** (2026-04-24) - 初始版本，完整实现 10 阶段业务流程

---

**负责 Agent**: Ella 🦊 (合同管理专家)
**技能类型**: 业务技能
