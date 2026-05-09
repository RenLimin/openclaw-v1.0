# 邮件管理技能 - 依赖说明

---

## 📦 Python 依赖包

| 包名 | 版本要求 | 用途 | 必选 |
|------|---------|------|------|
| `imaplib2` | ≥ 3.0 | IMAP 协议邮件接收 | ✅ 是 |
| `beautifulsoup4` | ≥ 4.12.0 | HTML 邮件内容解析 | ✅ 是 |
| `pypdf` | ≥ 3.0.0 | PDF 附件内容预览 | ⭕ 否 |
| `python-docx` | ≥ 0.8.11 | Word 附件内容预览 | ⭕ 否 |
| `python-dotenv` | ≥ 1.0.0 | 环境变量加载 | ⭕ 否 |
| `chardet` | ≥ 5.0.0 | 编码自动检测 | ✅ 是 |
| `pytz` | ≥ 2023.3 | 时区处理 | ✅ 是 |

---

## 🌐 系统依赖

| 依赖 | 说明 |
|------|------|
| **Python 3.8+** | 最低版本要求 |
| **网络连接** | 能访问 IMAP/SMTP 服务器 |
| **macOS Keychain** | 用于安全存储邮箱密码 |

---

## 🚀 安装命令

### 基础安装

```bash
pip install imaplib2 beautifulsoup4 chardet pytz
```

### 完整安装（含可选依赖）

```bash
pip install imaplib2 beautifulsoup4 chardet pytz pypdf python-docx python-dotenv
```

---

## 🔗 依赖技能

| 技能名称 | 用途 | 必须 |
|---------|------|------|
| `summarize-pro` | 长邮件摘要生成 | ⭕ 否（可选增强功能） |
| `contract-clause-split` | 合同附件自动处理 | ⭕ 否（可选增强功能） |

---

## 🔐 安全依赖

| 项目 | 说明 |
|------|------|
| **macOS Keychain** | 所有密码必须存储在 Keychain 中，禁止明文存储在配置文件 |
| **TLS/SSL** | 强制使用 SSL 加密连接 IMAP/SMTP，禁止明文传输 |

---

## ⚙️ 前置配置检查清单

✅ 配置文件存在：`config/email-config.json`  
✅ IMAP/SMTP 服务器地址可访问  
✅ Keychain 中已存储邮箱密码  
✅ 网络防火墙允许 993/465 端口出站  
✅ 用户已明确授权访问邮箱

---

_版本: v1.0 | 更新时间: 2026-04-23_
