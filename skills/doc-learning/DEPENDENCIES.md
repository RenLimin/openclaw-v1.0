# doc-learning Dependencies

## 二进制依赖
- `python3`: 3.10.6 ✅ 已安装
- `pandoc`: 文档格式转换 (可选，未安装)

## Python 包依赖
| 包 | 版本 | 状态 | 用途 |
|----|------|------|------|
| pdfminer.six | 20251230 | ✅ 已安装 | PDF 文本提取 |
| cryptography | 46.0.6 | ✅ 已安装 (pdfminer 依赖) | PDF 加密支持 |

## 支持格式
- Markdown (.md) — 原生支持
- 纯文本 (.txt) — 原生支持
- PDF (.pdf) — 纯文本 PDF (非扫描件)

## 注意事项
- 扫描件 PDF 需要 OCR 服务（不在本技能范围）
- 大型文档建议分段处理

## 安装日期
- 2026-04-12
