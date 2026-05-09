# ONES 数据下载技能

> 通过浏览器自动化 + GraphQL API 下载 ONES 筛选器中的工作项数据，支持 CSV/JSON 导出。

## 触发条件

当需要：
- 从 ONES 系统下载筛选器数据
- 导出项目/工作项统计数据
- 生成周报/月报数据
- 批量获取工作项信息

## 快速使用

```bash
# 下载所有配置的筛选器（CSV 格式）
python3 scripts/download-ones-data.py

# 下载指定筛选器
python3 scripts/download-ones-data.py --filter 5wY9X4m8

# JSON 格式输出
python3 scripts/download-ones-data.py --output-format json

# 显示浏览器窗口（处理验证码）
python3 scripts/download-ones-data.py --interactive-login
```

## 配置

编辑 `config/ones-config.json`：

| 字段 | 说明 |
|------|------|
| `ones_url` | ONES 系统地址 |
| `team_uuid` | 团队 UUID |
| `auth.username` | 登录用户名（邮箱） |
| `filters` | 筛选器配置（UUID → 名称映射） |
| `field_mapping` | 字段名 ↔ 字段 UUID 映射 |
| `graphql_fields` | GraphQL 查询字段列表 |

## 认证

- 首次使用需配置 `auth.username`
- 密码通过 macOS Keychain 存储（服务名: `openclaw-browser-oliver-ones-username`）
- 如遇验证码，脚本会等待手动完成登录

## 输出

- 默认输出目录: `~/.openclaw/workspace/output/ones-data/`
- CSV 文件带 UTF-8 BOM（Excel 兼容）
- 同时保存认证状态供后续使用

## 注意事项

1. ONES 前端为 SPA，需等待页面加载完成
2. 图形验证码需手动处理
3. 大型筛选器可能需要较长时间
4. 认证 token 会过期，需定期重新登录

## 依赖

- Python 3.8+
- `playwright` (浏览器自动化)
- `pandas` (可选，CSV 处理)

```bash
pip install playwright pandas
playwright install chromium
```
