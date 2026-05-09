# 履约义务拆分业务技能

> 打通OCR识别 → 条款拆分 → 义务提取 → 标准比对 → Excel导出的完整业务流程。
> ⚠️ **安全规则**: 必须由用户主动触发，禁止任何自动化/定时调用！

---

## 👤 负责 Agent

**Ella 🦊** (合同管理专家)

---

## 🚀 触发条件

当用户需要：
- 从合同中提取履约义务明细
- 对比合同义务与标准产品定义
- 评估履约风险等级
- 生成履约义务明细表和审核报告

---

## 📋 功能清单

| 功能 | 说明 |
|------|------|
| 📄 **多格式支持** | 自动识别 PDF / Word / 图片格式合同 |
| 🔍 **OCR 智能识别** | 调用 ocr-engine，支持扫描版合同识别 |
| ✂️ **条款边界识别** | 调用已有条款拆分逻辑，智能合并跨页/跨行内容 |
| 🎯 **义务类型识别** | 自动识别付款、交付、验收、质保、保密等义务类型 |
| 📦 **标准产品匹配** | 从合同文本自动识别产品编码/名称，匹配标准义务库 |
| ⚖️ **义务比对** | 自动比对合同义务与标准定义差异，红色高亮标注 |
| 📊 **风险等级评估** | 自动评估高/中/低风险等级，标注法条依据 |
| 🔄 **义务去重合并** | 同类型义务智能整合，避免重复 |
| 📑 **Excel 多 Sheet 导出** | 履约义务汇总 + 差异比对报告 + 合同条款原文 |
| 📋 **审核报告生成** | Markdown 格式审核报告 |

---

## 🔧 使用方法

### 1. 完整拆分流程（推荐）

```bash
python3 skills/contract-obligation-split/scripts/obligation_splitter.py --input 合同文件.pdf --output 义务明细表.xlsx
```

### 2. 指定产品编码（跳过自动匹配）

```bash
python3 skills/contract-obligation-split/scripts/obligation_splitter.py --input 合同.pdf --product-code AS-XXX-001
```

### 3. 仅拆分预览（不导出 Excel）

```bash
python3 skills/contract-obligation-split/scripts/obligation_splitter.py --input 合同.pdf --preview
```

### 4. Python 模块调用

```python
import sys
sys.path.append('skills/contract-obligation-split/scripts')

from obligation_splitter import ObligationSplitter

# 初始化
splitter = ObligationSplitter(config_path='skills/contract-obligation-split/config')

# 完整流程
result = splitter.run_full_pipeline(
    input_file='合同文件.pdf',
    output_file='义务明细表.xlsx',
    product_code='AS-XXX-001'  # 可选，跳过自动匹配
)

# 查看结果
print(f"提取义务数量: {len(result['obligations'])}")
print(f"匹配风险等级: {result['risk_summary']}")
```

---

## 📁 目录结构

```
skills/contract-obligation-split/
├── SKILL.md                               # 技能说明 + 使用文档
├── DEPENDENCIES.md                       # 完整依赖清单
├── config/
│   └── config.yaml                       # 运行配置（义务类型、风险规则、产品库）
├── scripts/
│   ├── __init__.py
│   └── obligation_splitter.py            # 主流程引擎
├── templates/
│   └── 义务明细表模板.xlsx                # Excel 输出模板
└── tests/
    └── test_obligation_split.py          # 测试用例
```

---

## 🔄 标准处理流程 (SOP)

```
1. 输入文件（PDF/Word/JPG）
    │
    ▼
2. 文件格式自动识别
    │  ├─ PDF/Word → 直接解析
    │  └─ 图片/扫描版 PDF → 调用【ocr-engine】
    │
    ▼
3. 条款边界识别与拆分
    │  └─ 调用已有条款拆分逻辑
    │  └─ 跨页/跨行内容智能合并
    │
    ▼
4. 义务类型识别与字段提取
    │  └─ 调用【obligation_query】规则引擎
    │  └─ 提取：义务类型、履行时间、责任方、金额/比例
    │
    ▼
5. 标准产品自动匹配
    │  ├─ 从合同文本识别产品编码/名称
    │  └─ 调用【product_query】匹配标准产品义务库
    │
    ▼
6. 义务比对与差异标注
    │  ├─ 对比合同义务与标准定义
    │  └─ 红色高亮显示差异内容
    │
    ▼
7. 风险等级自动评估
    │  └─ 依据差异类型、法条依据评估高/中/低风险
    │
    ▼
8. 义务去重与合并
    │  └─ 同类型义务智能整合
    │
    ▼
9. Excel 模板导出
    │  └─ 调用【excel-engine】
    │
    ▼
10. 输出：履约义务明细表.xlsx + 审核报告.md
```

---

## 📑 输出格式

### Sheet1: 履约义务汇总

| 列名 | 说明 |
|------|------|
| 序号 | 义务编号 |
| 义务类型 | 付款义务 / 交付义务 / 验收义务 / 质保义务 / 保密义务 / 违约责任 / 其他 |
| 义务内容 | 义务具体描述 |
| 履行时间 | 约定的履行期限 |
| 责任方 | 甲方 / 乙方 / 双方 |
| 金额/比例 | 涉及的金额或比例 |
| 风险等级 | 🔴 高 / 🟡 中 / 🟢 低 |
| 法条依据 | 相关法条（如民法典第X条） |
| 备注 | 补充说明 |

### Sheet2: 差异比对报告

| 列名 | 说明 |
|------|------|
| 标准义务 | 产品标准定义的义务内容 |
| 合同义务 | 合同中约定的义务内容 |
| 差异类型 | 新增义务 / 删除义务 / 内容变更 / 期限变更 / 金额变更 |
| 差异说明 | 具体差异描述（差异内容红色高亮） |
| 建议处理 | 处理建议（接受 / 协商 / 拒签） |

### Sheet3: 合同条款原文

| 列名 | 说明 |
|------|------|
| 条款编号 | 原始条款序号 |
| 分类标签 | 条款分类（同 contract-clause-split） |
| 条款内容 | 完整条款原文 |

---

## ⚙️ 配置说明

### config.yaml 配置项

| 配置项 | 说明 | 默认值 |
|--------|------|-------|
| `obligation_types` | 义务类型定义列表 | 付款/交付/验收/质保/保密/违约等 |
| `risk_assessment_rules` | 风险评估规则 | 高/中/低风险判定条件 |
| `product_library` | 标准产品义务库（可扩展） | 内置常见产品模板 |
| `obligation_extraction_rules` | 义务字段提取规则 | 正则表达式列表 |
| `deduplication_rules` | 义务去重合并规则 | 相似度阈值等 |
| `ocr_engine.path` | OCR 引擎路径 | `../ocr-engine/scripts` |
| `excel_engine.path` | Excel 引擎路径 | `../excel-engine/scripts` |
| `clause_split.path` | 条款拆分路径 | `../contract-clause-split/scripts` |

---

## 📦 依赖

### Python 包依赖

```bash
pip install python-docx pypdf pdfplumber pyyaml openpyxl pillow pandas
```

### 技能依赖

- **ocr-engine** - OCR 文档识别引擎
- **contract-clause-split** - 合同条款拆分技能
- **excel-engine** - Excel 处理引擎

### 系统依赖（OCR）

- Tesseract 5.x（macOS: `brew install tesseract tesseract-lang`）

---

## ⚠️ 注意事项

1. **用户确认原则**: 拆分结果仅供参考，重要合同建议人工复核
2. **敏感数据保护**: 合同内容不上传到第三方服务，全部本地处理
3. **扫描件支持**: 扫描版 PDF 和图片自动调用 OCR 引擎
4. **产品匹配**: 自动匹配不到时，提示用户手动指定产品编码
5. **异常处理**: 完整的异常捕获和错误提示（文件不存在、OCR失败等）

---

## 🧪 测试验证

```bash
# 完整流程测试
python3 skills/contract-obligation-split/scripts/obligation_splitter.py --test

# 使用测试合同验证
python3 skills/contract-obligation-split/scripts/obligation_splitter.py --input tests/sample_contract.pdf --preview
```

---

_创建时间: 2026-04-24 | 版本: v1.0 | 作者: Ella 🦊_
