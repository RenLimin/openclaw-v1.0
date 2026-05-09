# OCR 文档识别引擎

> 通用 OCR 文档识别底层技能，支持多引擎调度、噪音清理、质量评估。
> 可被所有需要 OCR 能力的智能体/业务技能调用。

---

## 👤 负责 Agent

**通用底层技能** - 所有 Agent 均可调用

---

## 🚀 技能定位

| 维度 | 说明 |
|------|------|
| **层级** | 通用能力层 |
| **依赖方向** | 业务技能 → 调用本技能 |
| **调用方式** | 脚本调用 / Python 模块导入 |
| **并发支持** | 单进程串行，不支持并行 |

---

## 📋 功能清单

| 功能 | 说明 |
|------|------|
| 🔄 **多引擎调度** | 支持 Tesseract（当前）、PaddleOCR（预留）、EasyOCR（预留） |
| 🧹 **智能噪音清理** | 公章干扰清理、表格乱码清理、通用垃圾字符清理 |
| ✅ **自动纠错** | 60+ 条通用 OCR 错误修正规则 |
| 📊 **质量评估** | 中文识别率估算、噪音等级评估、表格完整性检测 |
| 📋 **表格识别** | 表格边框检测、单元格重建、表格结构还原 |
| 📄 **多格式支持** | PDF（文本版/扫描版）、图片（PNG/JPG）、批量处理 |
| 🧪 **标准化输出** | 统一 JSON 格式，包含文本、位置、置信度信息 |

---

## 🔧 引擎选型对比

| 引擎 | 准确率 | 速度 | 内存占用 | 中文支持 | 安装难度 | 推荐场景 |
|------|-------|------|---------|---------|---------|---------|
| **Tesseract 5.x** | ⭐⭐⭐ | ⚡⚡⚡ | 低 | 一般 | 简单 | 通用场景、大批量、服务器部署 |
| **PaddleOCR** | ⭐⭐⭐⭐⭐ | ⚡⚡ | 中 | 优秀 | 中等 | 高精度需求、中文文档 |
| **EasyOCR** | ⭐⭐⭐⭐ | ⚡ | 高 | 良好 | 简单 | 小批量、多语言混合 |

### 💡 选型建议

1. **默认推荐**：Tesseract 5.x（部署简单、速度快、资源占用低）
2. **中文文档优先**：PaddleOCR（中文识别准确率领先）
3. **开发/测试**：EasyOCR（pip 一键安装，开箱即用）

---

## 📁 目录结构

```
skills/ocr-engine/
├── SKILL.md                               # 技能说明 + 调用接口文档
├── DEPENDENCIES.md                       # 完整依赖说明
├── config/
│   ├── engine-config.yaml                 # 多引擎配置
│   ├── correction-dict.yaml              # OCR 错误修正字典（60+ 条）
│   └── table-detection.yaml              # 表格检测配置
└── scripts/
    ├── ocr_runner.py                     # 统一入口，多引擎调度
    ├── table_extractor.py                # 表格识别与重建
    ├── noise_reducer.py                  # 公章/噪音清理
    └── quality_assess.py                 # OCR 质量评估
```

---

## 🔧 使用方法

### 1. 命令行调用（推荐）

```bash
# 基本用法 - 自动检测 PDF 类型
python3 skills/ocr-engine/scripts/ocr_runner.py --input document.pdf

# 指定引擎
python3 skills/ocr-engine/scripts/ocr_runner.py --input document.pdf --engine tesseract

# 启用质量评估
python3 skills/ocr-engine/scripts/ocr_runner.py --input document.pdf --assess-quality

# 输出到文件
python3 skills/ocr-engine/scripts/ocr_runner.py --input document.pdf --output result.json

# 批量处理
python3 skills/ocr-engine/scripts/ocr_runner.py --batch ./pdf_folder/
```

### 2. Python 模块调用

```python
from pathlib import Path
import sys
sys.path.append('skills/ocr-engine/scripts')

from ocr_runner import OCRRunner

# 初始化
ocr = OCRRunner(engine='tesseract', config_path='skills/ocr-engine/config')

# 识别单个文件
result = ocr.run('document.pdf')
print(f"识别文本长度: {len(result['text'])} 字符")
print(f"质量评分: {result['quality_score']:.1f}/100")

# 带噪音清理和纠错
result = ocr.run('document.pdf', clean_noise=True, auto_correct=True)

# 获取质量评估详情
quality = result['quality_assessment']
print(f"中文识别率估算: {quality['chinese_recognition_rate']:.2%}")
print(f"噪音等级: {quality['noise_level']} (1-5)")
```

### 3. 噪音清理模块单独调用

```python
from noise_reducer import NoiseReducer

reducer = NoiseReducer('skills/ocr-engine/config/correction-dict.yaml')

# 完整清理流程
cleaned_text = reducer.full_clean(raw_ocr_text)

# 单项清理
cleaned = reducer.remove_seal_interference(text)      # 清理公章干扰
cleaned = reducer.remove_table_garbage(text)          # 清理表格乱码
cleaned = reducer.apply_corrections(text)             # 应用纠错字典
```

### 4. 质量评估单独调用

```python
from quality_assess import QualityAssessor

assessor = QualityAssessor()

# 完整评估
result = assessor.assess_full(ocr_text, original_image_path)
print(f"综合评分: {result['overall_score']}/100")

# 单项评估
chinese_rate = assessor.estimate_chinese_recognition_rate(text)
noise_level = assessor.assess_noise_level(text)
```

---

## 📋 输出格式（标准化）

```json
{
  "input_file": "document.pdf",
  "engine_used": "tesseract",
  "total_pages": 5,
  "processing_time": 12.34,
  "text": "完整识别文本...",
  "pages": [
    {
      "page_num": 1,
      "text": "第1页文本...",
      "confidence": 0.87,
      "boxes": [{"text": "...", "bbox": [x1, y1, x2, y2], "conf": 0.92}]
    }
  ],
  "quality_assessment": {
    "overall_score": 85.5,
    "chinese_recognition_rate": 0.92,
    "noise_level": 2,
    "table_integrity": 0.88,
    "issues_found": ["公章干扰 detected", "部分表格边框识别异常"]
  },
  "corrections_applied": 23,
  "noise_removed": 45
}
```

---

## ⚙️ 配置说明

### engine-config.yaml - 引擎配置

| 配置项 | 说明 | 默认值 |
|--------|------|-------|
| `default_engine` | 默认使用的 OCR 引擎 | `tesseract` |
| `tesseract.path` | Tesseract 可执行文件路径 | 自动检测 |
| `tesseract.languages` | 默认语言模型 | `chi_sim+eng` |
| `tesseract.dpi` | 渲染 DPI | `300` |
| `batch.max_workers` | 批量处理最大并发 | `1` |

### correction-dict.yaml - 纠错字典

包含 6 大类共 60+ 条修正规则：
1. 数字序号修正
2. 形近字修正（通用，非合同特定）
3. 公章干扰修正
4. 表格边框/乱码修正
5. 金额格式修正
6. 括号识别修正

---

## 🔄 标准处理流程 (SOP)

```
1. 输入文件检测
   │
   ▼
2. 文件类型判断（PDF/图片）
   │  └─ PDF → 检测文本版/扫描版
   │  └─ 图片 → 直接 OCR
   │
   ▼
3. 多引擎调度
   │  └─ 根据配置选择引擎
   │  └─ 引擎可用性自动 fallback
   │
   ▼
4. 执行 OCR 识别
   │
   ▼
5. 噪音清理（可选）
   │  ├─ 公章干扰清理
   │  ├─ 表格乱码清理
   │  └─ 垃圾字符清理
   │
   ▼
6. 自动纠错（可选）
   │  └─ 应用 60+ 条修正规则
   │
   ▼
7. 质量评估（可选）
   │
   ▼
8. 标准化输出
```

---

## ⚠️ 性能/准确率权衡说明

| 模式 | 速度 | 准确率 | 适用场景 |
|------|------|-------|---------|
| **快速模式** | ⚡⚡⚡ | 75-85% | 预览、大批量筛选 |
| **标准模式** | ⚡⚡ | 85-92% | 日常处理（默认） |
| **高精度模式** | 🐢 | 90-97% | 重要文档、合同、法律文件 |

### 配置切换

```bash
# 快速模式（低 DPI，单语言）
python ocr_runner.py --input doc.pdf --dpi 150 --l eng

# 高精度模式（高 DPI，多语言，启用所有后处理）
python ocr_runner.py --input doc.pdf --dpi 400 --clean-noise --auto-correct --assess-quality
```

---

## 🔗 业务技能集成示例

### 合同条款拆分技能调用

```python
# 在 contract-clause-split 中调用 OCR 引擎
sys.path.append('../ocr-engine/scripts')
from ocr_runner import OCRRunner

ocr = OCRRunner()
result = ocr.run(contract_pdf, clean_noise=True, auto_correct=True)

# 使用识别结果进行条款拆分
clauses = split_contract_text(result['text'])
```

---

## 🧪 测试命令

```bash
# 基础功能测试
python3 skills/ocr-engine/scripts/ocr_runner.py --test

# 测试噪音清理
python3 skills/ocr-engine/scripts/noise_reducer.py --test

# 测试质量评估
python3 skills/ocr-engine/scripts/quality_assess.py --test

# 引擎可用性检测
python3 skills/ocr-engine/scripts/ocr_runner.py --check-engines
```

---

## ⚠️ 注意事项

1. **仅通用能力**：不包含任何业务逻辑（合同条款拆分、风险识别等）
2. **配置驱动**：所有规则通过配置文件管理，不硬编码
3. **接口稳定**：输出格式标准化，确保向上兼容
4. **资源限制**：单进程设计，避免资源竞争
5. **扩展性**：预留 PaddleOCR/EasyOCR 引擎接口，可随时启用

---

_创建时间: 2026-04-24 | 版本: v1.0 | 从 contract-clause-split 独立固化_
