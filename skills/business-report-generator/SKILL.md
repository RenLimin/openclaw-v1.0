# 经营报告生成技能

> 自动化生成各类经营报告，包括周报、月报、项目进度报告、数据统计报告等。
> ⚠️ **安全规则**: 必须由用户主动触发，禁止任何自动化/定时调用！

---

## 👤 负责 Agent

**Aaron 🦉** (经营计划专家)

---

## 🚀 触发条件

当用户需要：
- 生成每周/每月经营报告
- 生成项目进度报告
- 生成数据统计分析报告
- 从 Excel/CSV 数据生成可视化报告
- 生成 Word 格式的正式报告
- 报告模板定制和优化

---

## ⚠️ 大模型使用安全规则

| 规则 | 要求 |
|------|------|
| **触发方式** | ✅ **必须用户主动发起**，禁止自动触发 |
| **推荐 Provider** | 🟢 **DeepSeek**（文档生成/数据处理场景） |
| **数据量限制** | 单次处理 ≤ 10MB 数据，≤ 10000 行 |
| **调用间隔** | 每个章节生成间隔 3-10 秒（模拟人类写作） |
| **并行处理** | 同时最多生成 1 份报告 |
| **工作时间** | 建议 9:00-18:00 执行，符合人类办公规律 |
| **数据安全** | 敏感经营数据不上传到第三方模型服务（本地处理优先） |

---

## 📋 功能清单

| 功能 | 说明 |
|------|------|
| 📅 **周报生成** | 自动汇总每周数据生成周报 |
| 📊 **月报生成** | 生成月度经营分析报告 |
| 📈 **项目报告** | 生成项目进度、里程碑、风险报告 |
| 📉 **数据统计报告** | 从 Excel/CSV 数据分析并生成报告 |
| 📝 **Word 格式输出** | 生成带格式的正式 Word 文档 |
| 📑 **多格式导出** | 支持 Word/Markdown/HTML/PDF 输出 |
| 🎨 **报告模板** | 内置多种报告模板，支持自定义 |
| 📊 **图表生成** | 自动生成趋势图、对比图、饼图等 |
| 🔗 **数据联动** | 支持从多个数据源汇总数据 |
| ✍️ **智能润色** | 自动优化报告语言，使其专业、规范 |

---

## 🔧 使用方法

### 📊 模式一：交付中心月报（2种数据来源方式）

#### 方式 1: 使用本地已下载的数据（推荐，当前稳定可用）

手动从 ONES 系统和企业微信微盘下载 CSV 文件到本地目录，然后运行：

```bash
cd /Users/bangcle/.openclaw/workspace/skills/business-report-generator/scripts/

python3 delivery_monthly_report.py \
  --mode local \
  --data-dir /path/to/your/csv/files/ \
  --template /Users/bangcle/Downloads/report/2026交付月报-20260130.xlsx \
  --output /Users/bangcle/.openclaw/workspace/training-reports/交付中心项目报告-202602.xlsx \
  --month 202602
```

**准备工作:**
1. 登录 ONES 系统 → 我的工作台 → 筛选器
   - 导出「签约项目统计」→ 保存为 `202602_签约项目统计.csv`
   - 导出「POC&提前实施统计」→ 保存为 `202602_POC提前实施.csv`
   - 导出「签约项目异常处置」→ 保存为 `202602_异常处置.csv`
2. 登录企业微信微盘 → 交付中心财务数据交接
   - 下载 `202602确收凭证交接.xlsx` → 导出「确收」Sheet 为 `202602_确收.csv`
   - 下载 `202602验收凭证交接.xlsx` → 导出「验收」Sheet 为 `202602_验收.csv`
3. 将以上 5 个 CSV 文件放到同一个目录（即 `--data-dir` 参数）

#### 方式 2: 自动从 ONES + 企业微信下载（开发中）

```bash
cd /Users/bangcle/.openclaw/workspace/skills/business-report-generator/scripts/

python3 delivery_monthly_report.py \
  --mode auto \
  --ones-config ../config/ones-config.json \
  --wecom-config ../config/wecom-config.json \
  --template /Users/bangcle/Downloads/report/2026交付月报-20260130.xlsx \
  --output /Users/bangcle/.openclaw/workspace/training-reports/交付中心项目报告-202602.xlsx \
  --month 202602 \
  --download-dir /tmp/delivery-report-data
```

**配置文件准备:**
- 复制 `config/ones-config.json.template` → `config/ones-config.json` 并填写 ONES 账号配置
- 复制 `config/wecom-config.json.template` → `config/wecom-config.json` 并填写企业微信配置

**可选参数:**
- `--test`: 测试模式，只写入前 100 行数据，快速验证流程
- `--expected-rows 13000`: 校验签约项目统计的预期行数，不匹配则告警
- `--report-json generation-report.json`: 输出详细的生成过程报告（JSON 格式）

---

### 通用报告生成（周报/月报/经营分析）

#### 1. 生成周报

```bash
python3 scripts/generate_report.py --type weekly --date 2026-04-23 --output report.docx
```

#### 2. 生成月报

```bash
python3 scripts/generate_report.py --type monthly --month 2026-04 --output 4月经营报告.docx
```

#### 3. 从数据文件生成报告

```bash
python3 scripts/generate_report.py --type data --data sales_data.xlsx --sheet Sheet1 --output 销售分析报告.md
```

#### 4. 指定模板生成

```bash
python3 scripts/generate_report.py --type custom --template templates/project-report.md --data project_data.json --output 项目A进度报告.docx
```

#### 5. 仅生成 Markdown 预览

```bash
python3 scripts/generate_report.py --type weekly --format markdown --preview
```

---

## 📑 报告类型体系

| 报告类型 | 模板 | 典型使用场景 |
|---------|------|------------|
| 📅 **周报** | `weekly-report.md` | 每周工作总结、下周计划 |
| 📊 **月报** | `monthly-report.md` | 月度经营分析、KPI 达成情况 |
| 📈 **项目报告** | `project-report.md` | 项目进度、里程碑、风险、资源 |
| 💰 **财务报告** | `financial-report.md` | 收支分析、预算执行、成本控制 |
| 👥 **人力报告** | `hr-report.md` | 人员统计、招聘进度、考勤分析 |
| 📉 **数据分析报告** | `data-report.md` | 通用数据统计、趋势分析 |

---

## ⚙️ 配置说明

### 配置文件位置

`config/report-config.json`

| 配置项 | 说明 |
|--------|------|
| `templates.dir` | 报告模板存放目录 |
| `templates.default_format` | 默认输出格式 (word/markdown) |
| `data_sources.excel.sheet_names` | Excel 数据表名映射 |
| `report_styles.company_name` | 公司名称（报告页眉） |
| `report_styles.logo_path` | 公司 Logo 路径 |
| `report_styles.font` | 默认字体 |
| `report_styles.toc` | 是否自动生成目录 |
| `processing.section_delay_min` | 每个章节生成间隔最小值（秒） |
| `processing.section_delay_max` | 每个章节生成间隔最大值（秒） |
| `output.default_dir` | 默认输出目录 |
| `security.sanitize_sensitive_data` | 敏感数据脱敏开关 |
| `security.local_processing_only` | 强制本地处理开关 |

---

## 📝 标准生成流程 (SOP)

### 报告生成流程

```
1. 用户发起报告生成请求，指定类型和时间范围
   │
   ▼
2. 数据收集与预处理
   │  └── 读取 Excel/CSV/数据库数据
   │  └── 数据清洗、格式统一
   │  └── 敏感数据自动脱敏（可选）
   │
   ▼
3. 数据分析与统计
   │  └── 计算关键指标、同比环比
   │  └── 识别异常数据和趋势
   │  └── 每部分分析间隔 3-10 秒（模拟人类思考）
   │
   ▼
4. 按章节生成报告内容
   │  └── 执行摘要
   │  └── 关键指标概览
   │  └── 详细数据分析
   │  └── 问题与风险
   │  └── 下一步计划
   │  └── 每个章节间隔 3-10 秒（模拟人类写作）
   │
   ▼
5. 生成图表（趋势图、对比图、饼图等）
   │
   ▼
6. 格式美化与排版
   │  └── 统一字体、字号、颜色
   │  └── 插入页眉页脚、页码
   │  └── 自动生成目录
   │
   ▼
7. 导出为指定格式（Word/Markdown/PDF）
   │
   ▼
8. 展示给用户确认
```

---

## ⚠️ 注意事项

1. **用户确认原则**: 报告内容生成后需用户确认，重要报告建议人工审核
2. **敏感数据保护**: 经营数据不上传到第三方模型服务，全部本地处理
3. **数据校验**: 生成前自动校验数据完整性和合理性，异常数据提示用户
4. **版本控制**: 每次生成报告自动备份，支持历史版本追溯
5. **图表质量**: 生成的图表分辨率 ≥ 300 DPI，适合打印
6. **格式兼容**: 生成的 Word 文档兼容 Microsoft Word 2016+

---

## 📦 依赖

- Python 3.8+
- `python-docx` (Word 文档生成)
- `pandas` (数据处理和分析)
- `openpyxl` (Excel 文件读写)
- `matplotlib` / `seaborn` (图表生成)
- `jinja2` (模板渲染)
- `markdown` (Markdown 解析)
- `python-dotenv` (环境变量加载)

```bash
pip install python-docx pandas openpyxl matplotlib seaborn jinja2 markdown python-dotenv
```

---

## 🧪 测试命令

```bash
# 测试模板系统
python3 scripts/generate_report.py --test-template

# 生成示例周报（使用模拟数据）
python3 scripts/generate_report.py --type weekly --sample --preview

# 测试数据解析
python3 scripts/generate_report.py --test-data sample_data.xlsx
```

---

## 📁 输出示例

### 经营报告结构（Word 格式）

```
📄 2026年4月经营分析报告.docx
├── 📌 封面（公司Logo、报告名称、日期）
├── 📑 目录（自动生成页码）
├── 📊 执行摘要
│   ├── 本月关键指标概览
│   ├── 重要亮点
│   └── 主要问题
├── 📈 经营数据分析
│   ├── 销售收入分析
│   ├── 成本分析
│   ├── 利润分析
│   └── 同比环比对比（含图表）
├── 👥 人力情况
│   ├── 人员统计
│   ├── 招聘进度
│   └── 考勤分析
├── 🎯 项目进度
│   ├── 里程碑完成情况
│   └── 项目风险
├── ⚠️ 问题与风险
├── 📋 下月计划与重点
└── 📎 附录（详细数据表格）
```

---

_创建时间: 2026-04-23 | 版本: v1.0 | 作者: Aaron 🦉_
