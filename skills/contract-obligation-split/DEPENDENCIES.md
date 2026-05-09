# 履约义务拆分技能 - 依赖清单

## 📦 Python 包依赖

| 包名 | 版本要求 | 用途 | 必需 |
|------|---------|------|------|
| `python-docx` | ≥ 0.8.11 | Word 文档解析 | ✅ |
| `pypdf` | ≥ 3.0.0 | PDF 基础解析 | ✅ |
| `pdfplumber` | ≥ 0.9.0 | 高级 PDF 解析（推荐） | ✅ |
| `pyyaml` | ≥ 6.0 | YAML 配置文件解析 | ✅ |
| `openpyxl` | ≥ 3.0.10 | Excel 文件读写 | ✅ |
| `pillow` | ≥ 9.0.0 | 图片处理 | ✅ |
| `pandas` | ≥ 1.5.0 | 数据处理 | ✅ |
| `numpy` | ≥ 1.21.0 | 数值计算 | ✅ |

### 安装命令

```bash
pip install python-docx pypdf pdfplumber pyyaml openpyxl pillow pandas numpy
```

---

## 🔗 技能依赖

| 技能名称 | 技能路径 | 用途 | 必需 |
|----------|---------|------|------|
| **ocr-engine** | `skills/ocr-engine/` | OCR 文档识别，支持扫描版合同 | ✅ |
| **contract-clause-split** | `skills/contract-clause-split/` | 合同条款边界识别与拆分 | ✅ |
| **excel-engine** | `skills/excel-engine/` | Excel 高性能读写与格式化 | ✅ |

### 依赖说明

1. **ocr-engine**: 提供多引擎 OCR 能力，支持 PDF/图片识别、噪音清理、自动纠错
2. **contract-clause-split**: 提供条款边界识别、智能分句、条款分类能力
3. **excel-engine**: 提供高性能 Excel 读写、公式保护、样式批量应用能力

---

## 🖥️ 系统依赖（OCR 相关）

### macOS

```bash
# Tesseract OCR 引擎（必需）
brew install tesseract tesseract-lang

# 验证安装
tesseract --version
# 应显示: tesseract 5.x.x
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

### Windows

从 [GitHub](https://github.com/UB-Mannheim/tesseract/wiki) 下载安装包，安装后添加到 PATH。

---

## 📁 目录依赖

运行时需要以下目录结构存在：

```
skills/contract-obligation-split/
├── config/config.yaml       # 配置文件
├── templates/               # Excel 模板目录
└── tests/                   # 测试用例目录
```

---

## ✅ 依赖检查

### 运行依赖检查

```bash
python3 skills/contract-obligation-split/scripts/obligation_splitter.py --check-deps
```

### 预期输出

```
📦 Python 包依赖检查...
  ✅ python-docx
  ✅ pypdf
  ✅ pdfplumber
  ✅ pyyaml
  ✅ openpyxl
  ✅ pillow
  ✅ pandas
  ✅ numpy

🔗 技能依赖检查...
  ✅ ocr-engine
  ✅ contract-clause-split
  ✅ excel-engine

🖥️ 系统依赖检查...
  ✅ Tesseract OCR (版本: 5.3.x)

✅ 所有依赖检查通过！
```

---

## ⚠️ 常见问题

### Q: Tesseract 未找到？
A: 确保 Tesseract 已安装并在 PATH 中，或在 config.yaml 中指定 `tesseract_path`。

### Q: 中文识别效果差？
A: 确保安装了中文语言包（tesseract-ocr-chi-sim），可以在 config.yaml 中配置语言参数。

### Q: 大 PDF 处理慢？
A: 可以在 config.yaml 中调整 `ocr.dpi` 参数降低分辨率，或使用快速模式。

---

_版本: v1.0 | 更新时间: 2026-04-24_
