# ONES 数据下载 — 依赖清单

## Python 依赖

| 包名 | 版本 | 用途 | 是否必须 |
|------|------|------|---------|
| `playwright` | >=1.40 | 浏览器自动化 | ✅ 必须 |
| `pandas` | >=2.0 | CSV 数据处理 | ⚠️ 推荐（有内置替代） |

## 系统依赖

| 依赖 | 用途 | 安装方式 |
|------|------|---------|
| Chromium | Playwright 浏览器引擎 | `playwright install chromium` |
| Python 3.8+ | 运行环境 | 系统自带或 pyenv |

## 安装命令

```bash
# 1. 安装 Python 包
pip install playwright pandas

# 2. 安装 Chromium 浏览器
playwright install chromium

# 3. 验证安装
python3 -c "from playwright.async_api import async_playwright; print('✅ playwright OK')"
python3 -c "import pandas; print('✅ pandas OK')"
```

## macOS Keychain

用于安全存储 ONES 登录凭证：

```bash
# 存储用户名
security add-generic-password \
  -s "openclaw-browser-oliver-ones-username" \
  -a "your-email@bangcle.com" \
  -w "your-email@bangcle.com"

# 查看已存储
security find-generic-password -s "openclaw-browser-oliver-ones-username"
```

## 网络要求

| 目标 | 端口 | 说明 |
|------|------|------|
| `ones.bangcle.com` | 443 | ONES 系统（HTTPS） |

## 可选依赖

| 工具 | 用途 |
|------|------|
| `jq` | JSON 数据查看 |
| `csvkit` | CSV 数据处理 |
