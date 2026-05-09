# Word 文档智能分析工具包

通用的 Word 文档处理能力层，为所有需要 Word 处理的智能体提供底层支持。

## 功能模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 文档解析 | `word_parser.py` | 完整解析文档结构、标题、段落、样式 |
| 表格提取 | `table_extractor.py` | 智能提取表格，支持合并单元格、跨页合并 |
| 格式比对 | `style_comparator.py` | 文档与模板格式一致性校验 |
| 目录管理 | `toc_generator.py` | 目录生成、校验、更新 |

## 快速使用

### 1. 文档解析
```bash
python scripts/word_parser.py --input document.docx --output result.json
```

### 2. 表格提取
```bash
python scripts/table_extractor.py --input document.docx --table-index 0 --format csv
```

### 3. 格式比对
```bash
python scripts/style_comparator.py --template template.docx --target document.docx
```

### 4. 目录管理
```bash
python scripts/toc_generator.py --input document.docx --validate
python scripts/toc_generator.py --input document.docx --generate
```

## Python API 调用

```python
from skills.word_analyzer.scripts.word_parser import WordParser
from skills.word_analyzer.scripts.table_extractor import TableExtractor
from skills.word_analyzer.scripts.style_comparator import StyleComparator
from skills.word_analyzer.scripts.toc_generator import TOCGenerator

# 解析文档
parser = WordParser("document.docx")
result = parser.parse()
print(f"标题数: {len(result['headings'])}")

# 提取表格
extractor = TableExtractor("document.docx")
df = extractor.get_table(0, format="dataframe")

# 格式比对
comparator = StyleComparator("template.docx")
report = comparator.compare("document.docx")
print(f"匹配度: {report['match_rate'] * 100:.1f}%")

# 生成目录
toc = TOCGenerator("document.docx")
toc.generate_toc("output.docx")
```

## 配置文件

所有规则可通过 `config/structure-rules.yaml` 自定义：
- 标题识别正则
- 字体格式规则
- 表格解析规则
- 目录生成规则

## 依赖

```bash
pip install python-docx pandas pyyaml
```

---

*通用底层能力，无业务逻辑，专注文档处理本身*
