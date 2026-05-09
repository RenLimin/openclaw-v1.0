# Word 文档智能分析工具 v1.0

## 技能定位

**通用能力层** - 为所有需要 Word 文档处理的智能体提供底层能力支持。

## 功能概览

| 模块 | 功能 | 脚本 |
|------|------|------|
| 文档解析 | 完整解析 Word 文档结构、样式、内容 | `word_parser.py` |
| 表格提取 | 智能提取表格并转为结构化数据 | `table_extractor.py` |
| 格式比对 | 文档与模板格式一致性校验 | `style_comparator.py` |
| 目录管理 | 自动生成/校验目录 (TOC) | `toc_generator.py` |

## 调用接口

### 1. word_parser.py - 文档解析

```python
from scripts.word_parser import WordParser

parser = WordParser("document.docx")
result = parser.parse()

# 结果结构
{
    "metadata": {...},          # 文档元数据
    "structure_tree": [...],    # 文档结构树
    "paragraphs": [...],        # 所有段落
    "headings": [...],          # 标题层级
    "styles": {...}            # 样式信息
}
```

**命令行调用:**
```bash
python scripts/word_parser.py --input document.docx --output result.json
python scripts/word_parser.py --input document.docx --extract-by-heading "第一章"
```

### 2. table_extractor.py - 表格提取

```python
from scripts.table_extractor import TableExtractor

extractor = TableExtractor("document.docx")
tables = extractor.extract_all()

# 单表提取
table_data = extractor.get_table(0, format="dataframe")  # dataframe/list/json
```

**命令行调用:**
```bash
python scripts/table_extractor.py --input document.docx --output tables.json
python scripts/table_extractor.py --input document.docx --table-index 0 --format csv
```

### 3. style_comparator.py - 格式比对

```python
from scripts.style_comparator import StyleComparator

comparator = StyleComparator(template_path="template.docx")
report = comparator.compare("document.docx")

# 结果包含
{
    "match_rate": 0.95,         # 匹配度
    "differences": [...],       # 差异列表
    "font_check": {...},        # 字体检查结果
    "paragraph_check": {...},   # 段落格式结果
    "heading_check": {...}     # 标题层级检查
}
```

**命令行调用:**
```bash
python scripts/style_comparator.py --template template.docx --target document.docx
```

### 4. toc_generator.py - 目录管理

```python
from scripts.toc_generator import TOCGenerator

generator = TOCGenerator("document.docx")

# 校验目录
validation = generator.validate_toc()

# 生成目录
generator.generate_toc(output_path="with_toc.docx")

# 更新目录页码
generator.update_page_numbers(output_path="updated.docx")
```

**命令行调用:**
```bash
python scripts/toc_generator.py --input document.docx --validate
python scripts/toc_generator.py --input document.docx --generate --output with_toc.docx
```

## 配置驱动

所有解析规则可通过 `config/structure-rules.yaml` 自定义：

```yaml
heading_patterns:
  - "第[一二三四五六七八九十\\d]+章"
  - "第[一二三四五六七八九十\\d]+条"
  - "^\\d+\\.\\s"

font_rules:
  body:
    name: ["宋体", "SimSun"]
    size: 12
  heading_1:
    name: ["黑体", "SimHei"]
    size: 16
    bold: true
```

## 数据结构统一

所有模块输出遵循统一的 JSON 格式，方便上下游集成。

---

*通用底层能力，无业务逻辑，专注文档处理本身*
