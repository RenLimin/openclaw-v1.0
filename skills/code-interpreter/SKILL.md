---
name: code-interpreter
description: >
  Execute Python code for data analysis, scripting, computation tasks, and programming training.
  Use when: (1) running Python scripts or snippets, (2) data analysis / visualization,
  (3) algorithm testing, (4) file processing with Python, (5) programming capability training.
  NOT for: shell commands (use claw-shell), web scraping (use tavily/websearch).
metadata:
  openclaw:
    requires:
      bins: [python3]
---

# Code Interpreter

Python 代码执行环境。支持数据分析、脚本编写、算法验证、文件处理等编程任务。

## 能力

- 执行任意 Python 脚本
- 数据处理 (pandas, numpy)
- 可视化 (matplotlib)
- JSON/CSV/YAML 文件处理
- 自动化脚本编写

## 使用方式

直接让 Agent 编写并执行 Python 代码：

```bash
python3 -c "print('hello')"
python3 /path/to/script.py
```

## 注意事项

- 所有代码在本地执行，确保无恶意操作
- 涉及网络请求需要确认
- 输出结果保存在当前工作目录

## 自动化

```bash
# scripts/run-python.sh
#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "${1:-/dev/stdin}"
```
