# 合同条款拆分技能 v2.0

100% Python 脚本实现，无需调用大模型

---

## ✨ 功能特性

| 功能 | 状态 |
|------|------|
| Word 文档解析 | ✅ |
| 文本版 PDF 解析 | ✅ |
| 扫描版 PDF OCR 识别 | ✅（需部署 OCR 服务） |
| 智能按条款拆分 | ✅ |
| 10 大分类自动匹配 | ✅（可配置） |
| 风险条款识别（高/中/低） | ✅（可配置） |
| 关键信息提取（编号/金额/甲乙双方） | ✅（可配置） |
| Excel 多 Sheet 导出 | ✅ |
| 规则配置化（YAML） | ✅ |

---

## 🚀 快速开始

### 基础用法（Word / 文本版 PDF）

```bash
cd ~/.openclaw/workspace/skills/contract-clause-split/scripts

# 处理 Word 合同（秒出结果）
python3 split_contract.py --input 合同.docx --preview

# 处理文本版 PDF（秒出结果）
python3 split_contract.py --input 合同.pdf --preview

# 指定输出文件
python3 split_contract.py --input 合同.docx --output ~/Downloads/结果.xlsx
```

### 扫描版 PDF（需 OCR）

#### 方案 A：Docker 微服务（推荐）
```bash
# 一键启动 OCR 服务
cd .. && docker-compose up -d

# 使用 OCR 服务处理扫描件 PDF
python3 split_contract.py --input 扫描件.pdf --ocr-service http://localhost:9998 --preview
```

#### 方案 B：本地安装
```bash
# macOS
brew install ocrmypdf tesseract tesseract-lang

# 直接使用
python3 split_contract.py --input 扫描件.pdf --preview
```

---

## 📁 目录结构

```
contract-clause-split/
├── scripts/
│   ├── split_contract.py      # 主脚本
│   ├── ocr_client.py          # OCR 客户端
│   └── ocr_easyocr.py         # EasyOCR 备用方案
├── config/
│   ├── classification-rules.yaml   # 分类规则
│   ├── risk-keywords.yaml          # 风险关键词
│   └── extract-rules.yaml          # 提取规则
├── deploy/
│   ├── ocr-service.Dockerfile      # OCR 服务镜像
│   └── ocr-server.py               # OCR API 服务
├── docker-compose.yml              # 一键部署
├── README.md
├── PDF_OCR部署指南.md
└── 验证清单.md
```

---

## 🔧 配置说明

所有规则均可通过 `config/*.yaml` 人工调整，无需修改代码。

### 调整分类规则
编辑 `config/classification-rules.yaml`，增加/修改关键词即可优化分类准确率。

### 调整风险规则
编辑 `config/risk-keywords.yaml`，补充您关注的风险关键词。

### 新增提取字段
编辑 `config/extract-rules.yaml`，增加新的正则匹配规则。

---

## 📊 Excel 输出说明

| Sheet | 内容 |
|-------|------|
| 全部条款 | 完整条款列表 + 分类 + 风险等级 + 关键词 |
| 分类视图 | 按 10 大分类分组展示 |
| 风险条款汇总 | 仅含高/中风险条款，重点关注 |
| 关键信息 | 合同编号、甲乙双方、金额、交付地点等 |
| 原始文本 | 全文本（用于核对提取完整性） |

---

## ✅ 验证清单

请参考 `验证清单.md` 进行人工验证，确认所有功能符合预期。

---

## 🎯 验收标准

- Word 合同解析 100% 准确
- 条款拆分边界清晰合理
- 分类准确率 ≥ 85%（可通过配置优化到 95%+）
- 风险条款识别无重大遗漏
- 关键信息提取准确
- Excel 输出格式整洁可直接使用
