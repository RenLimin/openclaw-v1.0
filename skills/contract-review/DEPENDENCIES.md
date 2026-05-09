# 合同审核业务技能 - 依赖说明

---

## 📦 Python 依赖包

| 包名 | 版本要求 | 用途 | 必选 |
|------|---------|------|------|
| `pandas` | ≥ 2.0.0 | 数据处理和表格生成 | ✅ 是 |
| `openpyxl` | ≥ 3.1.0 | Excel 文件读写 | ✅ 是 |
| `python-docx` | ≥ 0.8.11 | Word 文档解析 | ✅ 是 |
| `PyYAML` | ≥ 6.0 | 配置文件解析 | ✅ 是 |
| `jinja2` | ≥ 3.1.0 | 模板渲染引擎 | ✅ 是 |
| `PyPDF2` | ≥ 3.0.0 | PDF 文本提取（文本版） | ⭕ 否 |
| `python-dotenv` | ≥ 1.0.0 | 环境变量加载 | ⭕ 否 |

---

## 🌐 系统依赖

| 依赖 | 说明 |
|------|------|
| **Python 3.8+** | 最低版本要求 |
| **中文字体支持** | 生成的报告需正确显示中文 |
| **足够内存** | 处理大合同和 OCR 时建议 ≥ 4GB |

---

## 🔗 依赖技能

| 技能名称 | 路径 | 用途 | 必须 |
|---------|------|------|------|
| `ocr-engine` | `skills/ocr-engine/` | OCR 识别、噪音清理、质量评估 | ✅ 是 |
| `contract-clause-split` | `skills/contract-clause-split/` | 条款智能拆分与分类 | ✅ 是 |
| `contract_reviewer` | `skills/contract_reviewer/` | 风险分级与评分（预留） | ⭕ 否 |
| `law_query` | `skills/law_query/` | 法条依据自动关联（预留） | ⭕ 否 |

---

## 🚀 安装命令

### 基础安装

```bash
pip install pandas openpyxl python-docx pyyaml jinja2
```

### 完整安装（含可选依赖）

```bash
pip install pandas openpyxl python-docx pyyaml jinja2 PyPDF2 python-dotenv
```

### 依赖技能检查

```bash
# 检查 ocr-engine 是否存在
ls skills/ocr-engine/scripts/ocr_runner.py

# 检查 contract-clause-split 是否存在
ls skills/contract-clause-split/scripts/split_contract.py
```

---

## 🔐 安全依赖

| 项目 | 说明 |
|------|------|
| **本地处理** | 所有合同内容必须本地处理，禁止上传到第三方模型服务 |
| **数据保密** | 审核过程中的临时文件需加密存储，审核完成后自动清理 |
| **权限控制** | 输出目录需有写入权限，合同文件需有读取权限 |

---

## ⚙️ 前置配置检查清单

✅ 配置文件存在：`config/config.yaml`  
✅ 审核报告模板存在：`templates/审核报告模板.md`  
✅ 风险明细模板存在：`templates/风险明细模板.xlsx`  
✅ OCR 引擎技能可用：`skills/ocr-engine/scripts/ocr_runner.py`  
✅ 条款拆分技能可用：`skills/contract-clause-split/scripts/split_contract.py`  
✅ Python 依赖包已安装  
✅ 输入合同文件路径可访问  
✅ 输出目录有写入权限  
✅ 用户已明确授权访问合同数据

---

## 📋 运行时依赖检测

技能启动时会自动检测以下依赖：

```python
# 依赖检查示例
def check_dependencies():
    checks = {
        'ocr_engine': os.path.exists('../ocr-engine/scripts/ocr_runner.py'),
        'clause_split': os.path.exists('../contract-clause-split/scripts/split_contract.py'),
        'pandas': importlib.util.find_spec('pandas') is not None,
        'openpyxl': importlib.util.find_spec('openpyxl') is not None,
        'yaml': importlib.util.find_spec('yaml') is not None,
        'jinja2': importlib.util.find_spec('jinja2') is not None,
    }
    
    missing = [k for k, v in checks.items() if not v]
    if missing:
        raise RuntimeError(f"缺少依赖: {', '.join(missing)}")
```

---

## ⚠️ 常见依赖问题

| 问题 | 解决方案 |
|------|---------|
| `ModuleNotFoundError: No module named 'yaml'` | `pip install pyyaml` |
| `ModuleNotFoundError: No module named 'openpyxl'` | `pip install openpyxl` |
| OCR 引擎找不到 | 检查 `skills/ocr-engine/` 目录是否存在 |
| 条款拆分技能找不到 | 检查 `skills/contract-clause-split/` 目录 |
| 中文字体显示乱码 | 安装系统中文字体（如 SimSun、PingFang） |

---

_版本: v1.0 | 更新时间: 2026-04-24_
