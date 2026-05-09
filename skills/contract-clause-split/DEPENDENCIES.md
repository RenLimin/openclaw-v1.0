# 合同条款拆分技能 - 依赖说明

---

## 📦 Python 依赖包

| 包名 | 版本要求 | 用途 | 必选 |
|------|---------|------|------|
| `python-docx` | ≥ 0.8.11 | Word (.docx) 文档解析 | ✅ 是 |
| `pypdf` | ≥ 3.0.0 | PDF 基础解析 | ✅ 是 |
| `pdfplumber` | ≥ 0.10.0 | PDF 高级解析 + 签署页图片渲染 | ✅ 是 |
| `pyyaml` | ≥ 6.0 | YAML 配置文件解析 | ✅ 是 |
| `openpyxl` | ≥ 3.1.0 | Excel 输出 + 图片插入 | ✅ 是 |
| `pillow` | ≥ 10.0 | 图像处理 + 签署页图片缩放插入 Excel | ✅ 是（签署页功能必需） |
| `pytesseract` | ≥ 0.3.10 | OCR 文字识别（扫描件 PDF） | ⭕ 否 |
| `jinja2` | ≥ 3.1.0 | 报告模板渲染 | ✅ 是 |
| `pandas` | ≥ 2.0.0 | 数据处理和 CSV 输出 | ⭕ 否（可选增强） |
| `opencv-python` | ≥ 4.8 | 图像预处理（OCR 增强） | ⭕ 否（可选增强） |
| `python-dotenv` | ≥ 1.0.0 | 环境变量加载 | ⭕ 否 |

---

## 🌐 系统依赖

| 依赖 | 说明 |
|------|------|
| **Python 3.8+** | 最低版本要求 |
| **足够内存** | 处理大文件时建议 ≥ 4GB |

---

## 🚀 安装命令

### 基础安装（含签署页功能）

```bash
pip install python-docx pypdf pdfplumber pyyaml jinja2 openpyxl pillow
```

### 完整安装（含可选依赖）

```bash
pip install python-docx pypdf pdfplumber pyyaml jinja2 openpyxl pytesseract pillow pandas opencv-python python-dotenv
```

---

## 🔗 依赖技能

| 技能名称 | 用途 | 必须 |
|---------|------|------|
| `pdf-ocr-extraction` | 扫描件 PDF OCR 识别 | ⭕ 否（仅扫描件需要） |
| `summarize-pro` | 条款摘要生成 | ⭕ 否（可选增强功能） |

---

## ⚙️ 前置配置检查清单

✅ 配置文件存在：`config/contract-split-config.json`  
✅ 输入文件路径可访问  
✅ 输出目录有写入权限  
✅ 至少 2GB 可用内存  
✅ 用户已明确授权处理合同

---

_版本: v1.1 | 更新时间: 2026-04-24_

**更新记录:**
- v1.1 (2026-04-24): 修正依赖清单，补充 pyyaml/pytesseract/pillow，标记 pandas/opencv-python 为可选增强
