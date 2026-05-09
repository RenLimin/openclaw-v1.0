# OA 审批技能 - 依赖说明

---

## 📦 Python 依赖包

| 包名 | 版本要求 | 用途 | 必选 |
|------|---------|------|------|
| `playwright` | ≥ 1.40.0 | 浏览器自动化 | ✅ 是 |
| `beautifulsoup4` | ≥ 4.12.0 | HTML 页面解析（高级解析场景） | ⭕ 可选 |
| `pyobjc` | ≥ 9.2 | macOS Keychain 密码访问（仅限 macOS 系统） | ⭕ 可选 |
| `pandas` | ≥ 2.0.0 | 数据处理（可选） | ⭕ 否 |
| `python-dotenv` | ≥ 1.0.0 | 环境变量加载 | ⭕ 否 |

---

## 🌐 系统依赖

| 依赖 | 说明 |
|------|------|
| **Chromium 浏览器** | Playwright 会自动安装 |
| **macOS 12+** | Keychain API 要求 |
| **网络连接** | 能访问 OA 系统地址 |

---

## 🚀 安装命令

### 基础安装

```bash
pip install playwright
playwright install chromium
```

### 完整安装（含可选依赖）

```bash
pip install playwright beautifulsoup4 pyobjc pandas python-dotenv
playwright install chromium
```

### macOS 用户（启用 Keychain 支持）

```bash
pip install playwright pyobjc
playwright install chromium
```

---

## 🔑 权限要求

| 权限 | 用途 |
|------|------|
| **Keychain 读取** | 获取 OA 登录密码 |
| **网络出站** | 访问 OA 系统 |
| **屏幕截图** | 错误时保存页面状态（可选） |

---

## ⚙️ 前置配置检查清单

✅ 配置文件存在：`config/oa-config.json`  
✅ OA 系统地址可访问  
✅ Keychain 中已存储密码  
✅ Playwright Chromium 已安装  
✅ 用户已明确授权执行操作

---

_版本: v1.0 | 更新时间: 2026-04-23_
