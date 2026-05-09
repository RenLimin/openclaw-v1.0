# PDF OCR 部署指南

## 🔍 快速判断 PDF 类型

| 类型 | 特征 | 处理速度 |
|------|------|---------|
| **文本版 PDF** | 可选中复制文字 | 秒级 |
| **扫描版 PDF** | 页面是整张图片，不可选中文本 | 需 OCR，30-60 秒/份 |

---

## 🚀 方案 A：Docker 微服务部署（生产环境推荐）⭐

### 优势
- ✅ 与主脚本完全解耦
- ✅ 中文准确率 ≥ 95%
- ✅ 可分布式扩展
- ✅ 支持批量处理

### 部署步骤

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/contract-clause-split

# 一键启动 OCR 服务
docker-compose up -d

# 验证服务
curl http://localhost:9998/health
# 返回: {"status":"ok","service":"ocr-service"}
```

### 使用方法

```bash
# 使用远程 OCR 服务处理 PDF
python3 scripts/split_contract.py \
  --input 合同.pdf \
  --ocr-service http://localhost:9998 \
  --preview
```

---

## 💻 方案 B：本地 OCR 安装（开发/小规模）

### macOS 安装

```bash
# 安装 OCRmyPDF + Tesseract + 中文语言包
brew install ocrmypdf tesseract tesseract-lang

# 验证
ocrmypdf --version
```

### 使用方法

```bash
# 直接使用本地 OCR
python3 scripts/split_contract.py --input 合同.pdf --preview
```

---

## 📋 当前状态说明

| 模块 | 状态 |
|------|------|
| ✅ Word 解析 | **完美可用** |
| ✅ 条款拆分/分类/风险识别 | **完美可用** |
| ✅ Excel 导出 | **完美可用** |
| ✅ 文本版 PDF 解析 | **完美可用** |
| ⏳ 扫描版 PDF OCR | 需部署方案 A 或 B |

---

## 🎯 建议使用流程

### 阶段 1：开发验证
- 使用 **Word 版** 合同进行人工验证
- 确认条款拆分逻辑、分类规则、风险识别准确性
- 调整 `config/*.yaml` 优化识别效果

### 阶段 2：生产部署
- 部署 **Docker OCR 微服务**（方案 A）
- 主脚本配置 OCR 服务地址
- 扫描版 PDF 自动 OCR 识别

### 阶段 3：批量处理
- OCR 服务分布式扩展
- 批量目录监控 + 自动处理

---

## 🔧 配置文件说明

| 文件 | 作用 |
|------|------|
| `config/classification-rules.yaml` | 条款分类关键词（可人工调整优化准确率） |
| `config/risk-keywords.yaml` | 风险等级关键词（可人工补充） |
| `config/extract-rules.yaml` | 关键信息提取规则（新增字段只需加配置） |
