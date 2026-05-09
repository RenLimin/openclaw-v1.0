# 依赖说明

## Python 依赖包

| 包名 | 版本 | 用途 | 安装命令 |
|------|------|------|---------|
| python-docx | >= 0.8.11 | Word 文档核心处理库 | `pip install python-docx` |
| pandas | >= 1.5.0 | 表格数据结构化 | `pip install pandas` |
| PyYAML | >= 6.0 | 配置文件解析 | `pip install pyyaml` |
| lxml | >= 4.9.0 | XML 底层解析（增强） | `pip install lxml` |

## 快速安装

### 全部安装
```bash
pip install python-docx pandas pyyaml lxml
```

### 最小安装（仅基础解析）
```bash
pip install python-docx pyyaml
```

## 模块依赖关系

```
word_parser.py ─── python-docx
               └── pyyaml

table_extractor.py ─── python-docx
                   ├── pandas (可选，DataFrame 输出)
                   └── word_parser.py

style_comparator.py ─── python-docx
                     └── word_parser.py

toc_generator.py ─── python-docx
                 └── word_parser.py
```

## 兼容性

- Python 版本: 3.8+
- 支持文档格式: .docx (Word 2007+)
- 不支持: .doc 二进制格式（需先转 .docx）

## 注意事项

1. **python-docx** 是核心依赖，所有模块都需要
2. **pandas** 为可选依赖，仅在需要 DataFrame/CSV 输出时安装
3. **lxml** 为可选依赖，用于增强复杂文档的解析稳定性
4. 处理 .doc 格式建议先使用 libreoffice 转换：
   ```bash
   libreoffice --headless --convert-to docx input.doc
   ```
