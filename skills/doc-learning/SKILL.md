---
name: doc-learning
description: >
  Batch import and learn from PDF, Markdown, and text documents.
  Use when: (1) reading PDF documents, (2) processing Markdown files,
  (3) extracting text from documents, (4) knowledge ingestion for training,
  (5) document summarization preparation.
  NOT for: web page extraction (use websearch), real-time search (use tavily).
metadata:
  openclaw:
    requires:
      bins: [python3, pandoc]
---

# Doc Learning

PDF / Markdown / 文本批量文档学习技能。用于知识导入、文档提取、训练数据准备。

## 能力

- PDF 文本提取（纯文本 PDF）
- Markdown 文件读取与解析
- 纯文本文件批量导入
- 文档结构化解析（标题、列表、代码块）
- 知识库批量导入

## 使用方式

### Markdown / 文本

```bash
# 直接读取
cat /path/to/document.md

# 批量处理
for f in /path/to/docs/*.md; do
    echo "=== $f ==="
    cat "$f"
done
```

### PDF（纯文本）

```bash
# 使用 python3 提取
python3 -c "
import subprocess
result = subprocess.run(['python3', '-c', '''
import sys
try:
    from pdfminer.high_level import extract_text
    text = extract_text(sys.argv[1])
    print(text)
except ImportError:
    print(\"pdfminer not installed: pip3 install pdfminer.six\")
''', '$PDF_PATH'], capture_output=True, text=True)
print(result.stdout)
"
```

## 注意事项

- 扫描件 PDF 需要 OCR（非本技能范围）
- 大型文档分段处理，避免超出上下文
- 提取后配合 summarize 技能压缩

## 自动化

```bash
# scripts/import-docs.sh
#!/bin/bash
set -euo pipefail
INPUT_DIR="${1:?Usage: import-docs.sh <directory>}"
OUTPUT_DIR="${2:-/tmp/doc-extracts}"
mkdir -p "$OUTPUT_DIR"

for f in "$INPUT_DIR"/*.{md,txt} 2>/dev/null; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    cp "$f" "$OUTPUT_DIR/${base%.md}.txt" 2>/dev/null || cp "$f" "$OUTPUT_DIR/"
    echo "Extracted: $base"
done
```
