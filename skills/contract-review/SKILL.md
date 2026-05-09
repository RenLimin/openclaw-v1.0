# 合同审核业务技能

> 打通 OCR 识别 → 专项审核 → 风险分级 → 法条关联 → 审核报告生成的完整业务流程。
> ⚠️ **安全规则**: 必须由用户主动触发，禁止任何自动化/定时调用！

---

## 👤 负责 Agent

**Ella 🦊** (合同管理专家)

---

## 🚀 触发条件

当用户需要：
- 完整审核一份合同的法律风险
- 专项审核合同的标的/交付/验收/售后条款
- 生成合同审核报告和风险明细表
- 合同风险分级和评分
- 合同条款的法律依据查询

---

## ⚠️ 大模型使用安全规则

| 规则 | 要求 |
|------|------|
| **触发方式** | ✅ **必须用户主动发起**，禁止自动触发 |
| **推荐 Provider** | 🟢 **DeepSeek**（合同审核/法律分析场景） |
| **文件大小限制** | 单次处理 ≤ 10MB，超过需拆分 |
| **调用间隔** | 每条条款审核间隔 2-5 秒（模拟人类阅读） |
| **并行处理** | 同时最多审核 1 份合同 |
| **工作时间** | 建议 9:00-18:00 执行 |

---

## 📋 功能清单

| 功能 | 说明 |
|------|------|
| 📄 **多格式支持** | 支持 PDF（文本版/扫描版）、Word、图片格式合同 |
| 🔍 **OCR 集成** | 自动调用 ocr-engine 进行智能识别、噪音清理、纠错 |
| ✂️ **条款智能拆分** | 自动识别并拆分独立条款，按类型分类 |
| 🔬 **四大专项审核** | 标的条款、交付条款、验收条款、售后/维保条款 |
| 📝 **通用规则检查** | 条款完整性、歧义表述、免责条款审查 |
| ⚠️ **风险三色分级** | 🔴 高风险 / 🟡 中风险 / 🟢 低风险 |
| 📊 **风险评分** | 自动计算风险评分，给出总体审核结论 |
| ⚖️ **法条自动关联** | 每条风险自动关联对应法律条文依据 |
| 💡 **改进建议生成** | 基于风险类型自动生成专业改进建议 |
| 📑 **双格式输出** | Markdown 审核报告 + Excel 风险明细表 |
| 👁️ **预览模式** | 控制台实时预览审核进度和结果 |

---

## 🔧 使用方法

### 1. 完整审核流程（输出双格式）

```bash
python3 scripts/contract_review_engine.py --input 合同文件.pdf --output 审核报告
```

### 2. 指定审核专项（只审指定类型）

```bash
# 只审核标的和交付条款
python3 scripts/contract_review_engine.py --input 合同.pdf --types 标的,交付

# 可选类型：标的、交付、验收、售后、全部
```

### 3. 仅输出高/中风险（过滤低风险）

```bash
python3 scripts/contract_review_engine.py --input 合同.pdf --min-risk 中
```

### 4. 预览模式（控制台输出，不生成文件）

```bash
python3 scripts/contract_review_engine.py --input 合同.pdf --preview
```

### 5. 自定义配置文件

```bash
python3 scripts/contract_review_engine.py --input 合同.pdf --config config/my-config.yaml
```

---

## 📑 四大专项审核体系

### RVW-01：标的条款审核

| 检查项 | 风险等级 | 说明 |
|--------|---------|------|
| 标的描述不清晰 | 🔴 高 | 无法明确合同指向的具体产品/服务 |
| 数量/规格缺失 | 🔴 高 | 缺少具体数量、规格、型号 |
| 质量标准不明确 | 🟡 中 | 质量标准模糊或引用失效标准 |
| 知识产权归属不明 | 🟡 中 | 标的相关知识产权归属未约定 |

### RVW-02：交付条款审核

| 检查项 | 风险等级 | 说明 |
|--------|---------|------|
| 交付时间不明确 | 🔴 高 | 缺少具体交付期限或时间节点 |
| 交付地点缺失 | 🟡 中 | 未约定具体交付地点 |
| 运输责任不清 | 🟡 中 | 运输方式、费用、风险承担未约定 |
| 逾期交付无违约责任 | 🔴 高 | 未约定逾期交付的违约责任 |

### RVW-03：验收条款审核

| 检查项 | 风险等级 | 说明 |
|--------|---------|------|
| 验收标准不明确 | 🔴 高 | 缺少具体验收标准和方法 |
| 验收期限缺失 | 🟡 中 | 未约定验收期限和异议期 |
| 验收流程不清晰 | 🟡 中 | 验收流程、参与方、验收文件未约定 |
| 不合格处理无约定 | 🔴 高 | 验收不合格的处理方式未约定 |

### RVW-04：售后/维保审核

| 检查项 | 风险等级 | 说明 |
|--------|---------|------|
| 质保期限不明确 | 🔴 高 | 质保期起止时间、期限未约定 |
| 质保范围缺失 | 🟡 中 | 质保覆盖的具体范围未清晰约定 |
| 维保响应时间无约定 | 🟡 中 | 故障响应、修复时间未约定 |
| 维保费用不清晰 | 🟡 中 | 免费/收费维保范围、费用标准不明确 |

---

## ⚙️ 配置说明

### 配置文件位置

`config/config.yaml`

| 配置项 | 说明 | 默认值 |
|--------|------|-------|
| `review.risk_threshold.high` | 高风险阈值（分数） | `≥ 80` |
| `review.risk_threshold.medium` | 中风险阈值（分数） | `40-79` |
| `review.risk_threshold.low` | 低风险阈值（分数） | `< 40` |
| `review.enable_general_check` | 启用通用规则检查 | `true` |
| `review.enable_law_reference` | 启用法条自动关联 | `true` |
| `review.enable_suggestions` | 启用改进建议生成 | `true` |
| `ocr.engine` | OCR 引擎选择 | `tesseract` |
| `ocr.clean_noise` | OCR 噪音清理 | `true` |
| `ocr.auto_correct` | OCR 自动纠错 | `true` |
| `output.default_format` | 默认输出格式 | `['markdown', 'excel']` |
| `output.highlight_high_risk` | 高亮高风险条款 | `true` |

---

## 🔄 标准审核流程 (SOP)

```
1. 输入文件检测与格式识别
   │  └─ 检测文件是否存在
   │  └─ 识别文件格式（PDF/Word/图片）
   │  └─ 文件大小和权限检查
   │
   ▼
2. OCR 识别与文本结构化
   │  └─ 调用 ocr-engine 执行识别
   │  └─ 噪音清理 + 自动纠错
   │  └─ 质量评估
   │  └─ 异常处理（OCR 失败回退机制）
   │
   ▼
3. 条款智能拆分与分类
   │  └─ 按条款边界智能拆分
   │  └─ 自动归类（标的/交付/验收/售后/其他）
   │  └─ 条款位置记录（页码/行号）
   │
   ▼
4. 四大专项审核
   │  ├─ RVW-01：标的条款审核
   │  ├─ RVW-02：交付条款审核
   │  ├─ RVW-03：验收条款审核
   │  └─ RVW-04：售后/维保条款审核
   │
   ▼
5. 通用规则检查
   │  ├─ 条款完整性检查
   │  ├─ 歧义表述识别
   │  └─ 免责条款审查
   │
   ▼
6. 风险分级与评分
   │  └─ 每条风险计算风险分值
   │  └─ 三色分级（🔴高/🟡中/🟢低）
   │  └─ 总体风险评分计算
   │
   ▼
7. 法条依据自动关联
   │  └─ 基于风险类型匹配对应法条
   │  └─ 法条编号、名称、内容关联
   │
   ▼
8. 改进建议生成
   │  └─ 基于风险类型和法条生成建议
   │  └─ 模板化 + 个性化定制
   │
   ▼
9. 双格式输出
   │  ├─ Markdown 审核报告
   │  └─ Excel 风险明细表
   │
   ▼
10. 审核完成，输出总结
```

---

## 📑 输出报告格式

### Markdown 审核报告结构

```
📄 合同审核报告.md
├── 📌 合同基本信息
│   ├── 合同名称
│   ├── 合同编号
│   ├── 甲方/乙方
│   ├── 签订日期
│   └── 审核日期
├── 🎯 审核结论
│   ├── 总体评分
│   ├── 风险等级
│   └── 审核建议
├── 📊 风险发现总览（统计表格）
├── 🔴 高风险条款详审
│   ├── 风险描述
│   ├── 法条依据
│   └── 改进建议
├── 🟡 中风险条款详审
├── 🟢 低风险条款汇总
├── ✅ 条款完整性检查结果
├── ❓ 歧义表述问题清单
├── ⚖️ 免责条款审查结果
└── 📋 审核总结与后续建议
```

### Excel 风险明细表结构

```
📊 风险明细表.xlsx
├── Sheet1: 风险明细总表
│   ├── 序号
│   ├── 条款类型
│   ├── 风险等级
│   ├── 风险描述
│   ├── 位置（页码/行号）
│   ├── 法条依据（编号+名称）
│   ├── 改进建议
│   ├── 责任人
│   ├── 处理时限
│   └── 状态
├── Sheet2: 统计汇总
│   ├── 风险等级分布
│   ├── 条款类型分布
│   └── 关键指标统计
```

---

## 📦 核心依赖

- Python 3.8+
- `skills/ocr-engine` (OCR 识别引擎)
- `skills/contract-clause-split` (条款拆分与分类)
- `pandas` (数据处理)
- `openpyxl` (Excel 文件生成)
- `python-docx` (Word 文档解析)
- `PyYAML` (配置文件解析)
- `jinja2` (模板渲染)

```bash
pip install pandas openpyxl python-docx pyyaml jinja2
```

---

## 🔗 跨技能调用接口

### 调用 OCR 引擎

```python
sys.path.append('../ocr-engine/scripts')
from ocr_runner import OCRRunner

ocr = OCRRunner()
result = ocr.run(input_file, clean_noise=True, auto_correct=True)
```

### 调用条款拆分

```python
sys.path.append('../contract-clause-split/scripts')
from split_contract import ContractSplitter

splitter = ContractSplitter()
clauses = splitter.split(ocr_result['text'])
```

### 法条查询接口（预留）

```python
from law_query import LawQuerier

querier = LawQuerier()
law_refs = querier.query(risk_type='delivery_issue')
```

---

## 🧪 测试命令

```bash
# 基础功能测试
python3 scripts/contract_review_engine.py --test

# 使用测试合同预览审核
python3 scripts/contract_review_engine.py --input test_data/sample_contract.pdf --preview

# 生成完整审核报告
python3 scripts/contract_review_engine.py --input test_data/sample_contract.pdf --output test_report

# 专项审核测试
python3 scripts/contract_review_engine.py --input test_data/sample_contract.pdf --types 标的,验收 --preview
```

---

## ⚠️ 注意事项

1. **用户确认原则**：审核结论仅供参考，重要合同建议法务专业人士审核
2. **数据保护**：合同内容全部本地处理，不上传到第三方模型服务
3. **异常处理**：文件不存在、OCR 失败、条款过少等异常均有完善处理
4. **接口稳定**：跨技能调用通过标准接口，不直接依赖实现细节
5. **可扩展性**：审核规则、风险阈值全部通过配置文件管理，便于扩展
6. **法律声明**：本技能生成的审核意见为 AI 辅助分析，不构成法律意见

---

## 📁 目录结构

```
skills/contract-review/
├── SKILL.md                               # 技能说明 + 使用文档 + 调用接口
├── DEPENDENCIES.md                       # 完整依赖清单
├── IMPLEMENTATION_SUMMARY.md             # 实现总结报告
├── config/
│   └── config.yaml                       # 审核配置（风险阈值、开关等）
├── scripts/
│   ├── __init__.py
│   └── contract_review_engine.py         # 主审核引擎
├── templates/
│   ├── 审核报告模板.md                    # Markdown 报告模板
│   └── 风险明细模板.xlsx                  # Excel 明细模板
└── test_data/
    └── sample_contract.pdf               # 测试合同文件
```

---

_创建时间: 2026-04-24 | 版本: v1.0 | 作者: Ella 🦊_
