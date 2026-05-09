# OCR 文档识别引擎 - 依赖说明

---

## 📦 Python 依赖包

| 包名 | 版本要求 | 用途 | 必选 | 引擎 |
|------|---------|------|------|------|
| `pytesseract` | ≥ 0.3.10 | Tesseract OCR Python 绑定 | ✅ 是 | Tesseract |
| `pdf2image` | ≥ 1.16.0 | PDF 转图片（扫描件必需） | ✅ 是 | 全部 |
| `PyMuPDF` (fitz) | ≥ 1.23.0 | 文本版 PDF 提取 | ✅ 是 | 全部 |
| `Pillow` | ≥ 10.0 | 图像处理 | ✅ 是 | 全部 |
| `PyYAML` | ≥ 6.0 | YAML 配置文件解析 | ✅ 是 | 全部 |
| `numpy` | ≥ 1.24.0 | 数值计算（质量评估） | ✅ 是 | 全部 |
| `paddlepaddle` | ≥ 2.5.0 | PaddlePaddle 深度学习框架 | ⭕ 否 | PaddleOCR |
| `paddleocr` | ≥ 2.7.0 | PaddleOCR 引擎 | ⭕ 否 | PaddleOCR |
| `easyocr` | ≥ 1.7.0 | EasyOCR 引擎 | ⭕ 否 | EasyOCR |
| `opencv-python` | ≥ 4.8 | 图像预处理（表格检测增强） | ⭕ 否（可选增强） | 全部 |
| `pandas` | ≥ 2.0.0 | 表格数据结构化输出 | ⭕ 否（可选增强） | 全部 |

---

## 🌐 系统依赖

| 依赖 | 说明 | 必选 | 平台 |
|------|------|------|------|
| **Python 3.8+** | 最低版本要求 | ✅ 是 | 全部 |
| **Tesseract OCR 5.x** | OCR 核心引擎 | ✅ 是 | 全部 |
| **Tesseract Chinese Language Pack** | 中文语言包 `chi_sim.traineddata` | ✅ 是 | 全部 |
| **Poppler** | PDF 渲染库（pdf2image 必需） | ✅ 是 | 全部 |
| **足够内存** | 处理扫描件建议 ≥ 4GB | ⭕ 推荐 | 全部 |

---

## 🚀 安装命令

### 基础安装（Tesseract 引擎，推荐）

#### macOS
```bash
# 安装系统依赖
brew install tesseract tesseract-lang poppler

# 安装 Python 依赖
pip install pytesseract pdf2image pymupdf pillow pyyaml numpy
```

#### Ubuntu/Debian
```bash
# 安装系统依赖
sudo apt install tesseract-ocr tesseract-ocr-chi-sim poppler-utils

# 安装 Python 依赖
pip install pytesseract pdf2image pymupdf pillow pyyaml numpy
```

#### Windows
```bash
# 1. 下载安装 Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# 2. 安装中文语言包: chi_sim.traineddata
# 3. 安装 Poppler: http://blog.alivate.com.au/poppler-windows/
# 4. 安装 Python 依赖
pip install pytesseract pdf2image pymupdf pillow pyyaml numpy
```

### EasyOCR 引擎安装（备选）

```bash
pip install easyocr
```

### PaddleOCR 引擎安装（高精度中文推荐）

```bash
# CPU 版本
pip install paddlepaddle paddleocr

# GPU 版本（推荐，快 5-10 倍）
pip install paddlepaddle-gpu paddleocr
```

### 完整安装（所有引擎 + 增强功能）

```bash
pip install pytesseract pdf2image pymupdf pillow pyyaml numpy easyocr opencv-python pandas
```

---

## 🔍 Tesseract 语言包说明

| 语言包 | 文件名 | 用途 |
|--------|--------|------|
| 简体中文 | `chi_sim.traineddata` | 简体中文识别 |
| 繁体中文 | `chi_tra.traineddata` | 繁体中文识别 |
| 英文 | `eng.traineddata` | 英文识别（默认自带） |
| 中英文混合 | `chi_sim+eng` | 中英文混合文档（推荐配置） |

### 语言包安装位置

- **macOS (Homebrew)**: `/usr/local/share/tessdata/` 或 `/opt/homebrew/share/tessdata/`
- **Linux**: `/usr/share/tesseract-ocr/5/tessdata/`
- **Windows**: `C:\Program Files\Tesseract-OCR\tessdata\`

### 验证安装

```bash
tesseract --list-langs
# 应包含: chi_sim, eng
```

---

## ⚙️ 引擎可用性自动检测

`ocr_runner.py` 启动时会自动检测引擎可用性：

```
✅ Tesseract: 可用 (v5.3.4)
   语言包: chi_sim, eng
⚠️ PaddleOCR: 未安装
   执行: pip install paddleocr
⚠️ EasyOCR: 未安装
   执行: pip install easyocr
```

自动 fallback 规则：
1. 优先使用用户指定的引擎
2. 不可用时 → 尝试 Tesseract
3. 仍不可用 → 抛出明确错误和安装指引

---

## 📊 性能/准确率权衡矩阵

| 引擎 | 安装时间 | 首次启动 | 每页处理时间 | 中文准确率 | 内存占用 |
|------|---------|---------|------------|-----------|---------|
| **Tesseract** | 30 秒 | < 1 秒 | 1-2 秒 | 80-88% | ~200MB |
| **EasyOCR** | 5 分钟 | 10-30 秒 | 3-5 秒 | 85-92% | ~1.5GB |
| **PaddleOCR** | 10 分钟 | 15-40 秒 | 2-4 秒 | 90-97% | ~2GB |

### 💡 部署建议

- **开发环境**：EasyOCR（安装简单，开箱即用）
- **生产环境**：Tesseract（稳定，资源占用低，可横向扩展）
- **中文优先场景**：PaddleOCR（准确率领先，对公章/表格鲁棒性更好）

---

## 🔗 依赖关系图

```
ocr-engine (本技能)
   ├─ 被依赖: contract-clause-split (合同条款拆分)
   ├─ 被依赖: pdf-ocr-extraction (PDF OCR 提取)
   └─ 被依赖: [其他需要 OCR 的业务技能]
```

---

## ⚙️ 前置配置检查清单

✅ 配置文件存在：`config/engine-config.yaml`  
✅ 配置文件存在：`config/correction-dict.yaml`  
✅ 配置文件存在：`config/table-detection.yaml`  
✅ Tesseract 可执行文件在 PATH 中  
✅ Tesseract 中文语言包已安装  
✅ Poppler (pdftoppm) 可执行  
✅ 输入文件路径可访问  
✅ 输出目录有写入权限  
✅ 至少 2GB 可用内存（处理扫描件时建议 ≥ 4GB）

---

## 🧪 依赖验证命令

```bash
# 完整依赖检查
python3 skills/ocr-engine/scripts/ocr_runner.py --check-deps

# 快速验证
python3 -c "import pytesseract; import fitz; from pdf2image import convert_from_path; print('✅ 核心依赖验证通过')"
```

---

_版本: v1.0 | 创建时间: 2026-04-24 | 从 contract-clause-split 独立固化_
