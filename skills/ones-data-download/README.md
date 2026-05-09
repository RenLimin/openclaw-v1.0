# ONES 数据下载技能 — 使用说明

## 概述

本技能包提供 ONES 项目管理系统的自动化数据下载能力，通过浏览器自动化 + GraphQL API 的方式，将筛选器中的工作项数据导出为 CSV 或 JSON 格式。

## 安装

### 1. 安装依赖

```bash
pip install playwright pandas
playwright install chromium
```

### 2. 配置认证

方式一：编辑配置文件
```json
// config/ones-config.json
{
  "auth": {
    "username": "your-email@bangcle.com"
  }
}
```

方式二：存入 Keychain（推荐）
```bash
security add-generic-password \
  -s "openclaw-browser-oliver-ones-username" \
  -a "your-email@bangcle.com" \
  -w "your-email@bangcle.com"
```

### 3. 验证安装

```bash
python3 scripts/download-ones-data.py --help
```

## 使用方法

### 基础用法

```bash
# 下载所有配置的筛选器
python3 scripts/download-ones-data.py

# 下载单个筛选器
python3 scripts/download-ones-data.py --filter 5wY9X4m8

# 指定输出格式
python3 scripts/download-ones-data.py --output-format json
python3 scripts/download-ones-data.py --output-format both
```

### 高级用法

```bash
# 自定义输出目录
python3 scripts/download-ones-data.py --output-dir ~/my-data

# 使用自定义配置
python3 scripts/download-ones-data.py --config /path/to/config.json

# 显示浏览器窗口（处理验证码时需要）
python3 scripts/download-ones-data.py --interactive-login
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--filter` | 指定筛选器 UUID | 下载所有 |
| `--output-format` | 输出格式: csv/json/both | csv |
| `--output-dir` | 输出目录 | 配置中的 default_dir |
| `--config` | 配置文件路径 | config/ones-config.json |
| `--headless` | 无头模式 | false |
| `--interactive-login` | 显示浏览器窗口 | false |

## 预配置筛选器

| UUID | 名称 | 说明 |
|------|------|------|
| `5wY9X4m8` | 2026周报-签约项目统计 | 签约项目周报统计 |
| `KxnjPRY7` | 2026周报-POC&提前实施统计 | POC & 提前实施周报 |
| `NWPaa48w` | 2026-签约项目异常处置 | 签约项目异常处理 |
| `4HUSuBfm` | 2026-项目督办任务 | 项目督办任务 |
| `QB9dmWEV` | 交付PM2026-履约义务台账 | 履约义务台账 |
| `ERg8awuY` | 交付PM2026-督办任务 | 督办任务 |
| `Edoaoz2N` | 交付PM2026-驻场任务 | 驻场任务 |

## 添加新筛选器

1. 在 ONES 中打开目标筛选器
2. 从 URL 中提取筛选器 UUID：
   ```
   https://ones.bangcle.com/project/#/workspace/filter/{FILTER_UUID}
   ```
3. 编辑 `config/ones-config.json`，在 `filters` 中添加：
   ```json
   "FILTER_UUID": {
     "name": "筛选器名称",
     "output_file": "输出文件名"
   }
   ```

## 输出格式

### CSV
- UTF-8 BOM 编码（Excel 兼容）
- 首行为表头
- 时间字段自动格式化为 `YYYY-MM-DD HH:MM:SS`

### JSON
- 保留原始嵌套结构
- 美化缩进（2 空格）
- 中文编码

## 故障排查

### 登录失败
1. 确认用户名已正确配置
2. 检查网络连接
3. 使用 `--interactive-login` 手动处理验证码

### 数据为空
1. 确认筛选器 UUID 正确
2. 检查是否有对应项目的访问权限
3. 查看浏览器控制台是否有错误

### 认证过期
重新运行脚本即可重新获取认证

## 技术架构

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Playwright │───▶│  ONES Web   │───▶│  GraphQL    │
│   浏览器     │    │  SPA 页面    │    │  API        │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
                                        ┌─────▼─────┐
                                        │  数据解析  │
                                        │  CSV/JSON  │
                                        └───────────┘
```

1. **浏览器自动化**：处理登录、验证码、SPA 导航
2. **GraphQL API**：通过页面内 fetch 调用，避免 CORS 问题
3. **数据解析**：扁平化嵌套数据，格式化时间戳
4. **导出**：CSV（pandas）/ JSON

## 文件结构

```
ones-data-download/
├── SKILL.md              # 技能说明（Agent 读取）
├── README.md             # 使用说明（本文档）
├── DEPENDENCIES.md       # 依赖清单
├── _meta.json            # 元数据
├── config/
│   └── ones-config.json  # 配置文件
├── scripts/
│   └── download-ones-data.py  # 核心脚本
└── references/           # 参考资料
```
