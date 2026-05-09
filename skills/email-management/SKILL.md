# 邮件管理技能

> 通过 IMAP/SMTP 协议管理企业邮箱，支持邮件检查、分类、发送等操作。
> ⚠️ **安全规则**: 必须由用户主动触发，禁止任何自动化/定时调用！

---

## 👤 负责 Agent

**Iris 🐦‍⬛** (辅助工作专家)

---

## 🚀 触发条件

当用户需要：
- 检查收件箱最新邮件
- 按规则分类整理邮件
- 搜索特定邮件内容
- 发送/回复邮件
- 导出邮件附件
- 生成邮件摘要报告

---

## ⚠️ 大模型使用安全规则

| 规则 | 要求 |
|------|------|
| **触发方式** | ✅ **必须用户主动发起**，禁止自动触发 |
| **推荐 Provider** | 🟢 **DeepSeek**（邮件处理场景） |
| **邮件数量限制** | 单次检查 ≤ 50 封邮件，避免频繁调用 |
| **调用间隔** | 每封邮件分析间隔 1-3 秒（模拟人类阅读） |
| **并行处理** | 同时最多分析 1 封邮件 |
| **工作时间** | 建议 9:00-18:00 执行，符合人类查邮件规律 |
| **内容安全** | 敏感邮件内容不上传到第三方模型服务（本地处理优先） |

---

## 📋 功能清单

| 功能 | 说明 |
|------|------|
| 📥 **邮件检查** | 获取最新邮件列表（支持按时间、发件人筛选） |
| 🗂️ **智能分类** | 按规则自动分类（审批提醒、工作邮件、广告等） |
| 🔍 **邮件搜索** | 按主题、发件人、时间、关键词搜索邮件 |
| 📄 **邮件摘要** | 生成长邮件的简洁摘要 |
| 📎 **附件导出** | 批量导出邮件附件到指定目录 |
| ✉️ **发送邮件** | 编写并发送新邮件（支持附件） |
| ↩️ **回复邮件** | 回复或转发邮件 |
| 📊 **统计报告** | 生成邮件统计报告（收发量、分类统计等） |
| ⭕ **待办提取** | 从邮件中自动提取待办事项 |

---

## 🔧 使用方法

### 1. 检查最新邮件

```bash
python3 scripts/email_manager.py --action check --limit 10
```

### 2. 检查特定文件夹邮件

```bash
python3 scripts/email_manager.py --action check --folder "INBOX" --limit 20
```

### 3. 按规则分类并输出报告

```bash
python3 scripts/email_manager.py --action classify --output report.md
```

### 4. 搜索邮件

```bash
python3 scripts/email_manager.py --action search --keyword "审批" --from "oa@company.com"
```

### 5. 导出附件

```bash
python3 scripts/email_manager.py --action export-attachments --output-dir "~/Downloads/email-attachments/"
```

### 6. 发送邮件

```bash
python3 scripts/email_manager.py --action send --to "recipient@company.com" --subject "邮件主题" --body "邮件内容" --attach "文件.pdf"
```

---

## 📑 邮件分类规则体系

| 类别 | 规则 | 优先级 |
|------|------|-------|
| 🔴 **P0 审批提醒** | 发件人含 oa@* 且主题含「审批」「待审批」「请审批」 | 最高 |
| 🟡 **P1 工作邮件** | 公司内部域、项目相关关键词 | 高 |
| 🟢 **P2 普通邮件** | 外部客户、合作伙伴邮件 | 中 |
| ⚪ **P3 通知广告** | 系统通知、营销邮件、订阅邮件 | 低 |

---

## ⚙️ 配置说明

### 配置文件位置

`config/email-config.json`

| 配置项 | 说明 |
|--------|------|
| `imap.server` | IMAP 服务器地址（如 imap.qiye.163.com） |
| `imap.port` | IMAP 端口（通常 993 SSL） |
| `imap.username` | 邮箱账号 |
| `imap.keychain_service` | Keychain 服务名，用于存储密码 |
| `smtp.server` | SMTP 服务器地址 |
| `smtp.port` | SMTP 端口（通常 465 SSL） |
| `smtp.username` | SMTP 账号（通常同 IMAP） |
| `folders.monitor` | 需要监控的文件夹列表 |
| `classification.rules` | 分类规则定义 |
| `security.local_processing` | 敏感内容本地处理开关 |

### 凭证管理

密码存储在 macOS Keychain 中：

```bash
# 服务名: openclaw-email-iris-password
# 读取密码
security find-generic-password -s "openclaw-email-iris-password" -w
```

---

## 📝 标准处理流程 (SOP)

### 邮件检查与分类流程

```
1. 用户发起邮件检查请求
   │
   ▼
2. 连接 IMAP 服务器并登录
   │
   ▼
3. 获取指定文件夹的邮件列表
   │  └── 按时间倒序，最多 50 封
   │  └── 每获取 10 封间隔 1 秒
   │
   ▼
4. 遍历邮件进行分类
   │  └── 每封邮件分析间隔 1-3 秒（模拟人类阅读）
   │  └── 敏感邮件跳过 LLM 分析，仅进行本地规则匹配
   │
   ▼
5. 提取 P0/P1 级关键邮件信息
   │
   ▼
6. 生成汇总报告并展示给用户
```

---

## ⚠️ 注意事项

1. **用户确认原则**: 发送/回复邮件前必须获得用户明确确认
2. **敏感数据保护**: 涉密邮件内容不上传到任何第三方模型服务
3. **附件安全**: 下载附件前进行文件类型和大小校验，禁止下载可执行文件
4. **频率限制**: 两次邮件检查间隔不小于 5 分钟（防止触发风控）
5. **删除操作**: 默认不删除邮件，移动到「已处理」文件夹需用户确认
6. **批量限制**: 单次批量操作不超过 10 封邮件

---

## 📦 依赖

- Python 3.8+
- `imaplib` (IMAP 协议支持，Python 内置，当前使用)
- `imaplib2` (可选，增强版 IMAP 协议支持)
- `smtplib` (SMTP 协议支持，Python 内置)
- `email` (邮件解析，Python 内置)
- `beautifulsoup4` (HTML 邮件解析)
- `chardet` (编码自动检测)
- `pytz` (时区处理)
- `pypdf` / `python-docx` (附件内容预览，可选)
- `python-dotenv` (环境变量加载，可选)

```bash
pip install beautifulsoup4 chardet pytz
```

---

## 🧪 测试命令

```bash
# 测试 IMAP 连接
python3 scripts/email_manager.py --action test-connection

# 测试获取 5 封邮件
python3 scripts/email_manager.py --action check --limit 5

# 测试分类规则
python3 scripts/email_manager.py --action test-classification --sample "邮件主题"
```

---

## 📁 输出示例

### 邮件检查报告

```markdown
# 📧 邮件检查报告（2026-04-23 14:30）

## 🔴 P0 待审批邮件（2 封）
1. 【OA 审批提醒】采购合同 HT-2024-001 待审批
   - 发件人: oa@company.com
   - 时间: 2026-04-23 10:15
   - 链接: https://oa.company.com/...

2. 【紧急】合同盖章审批申请
   - 发件人: manager@company.com
   - 时间: 2026-04-23 11:30

## 🟡 P1 工作邮件（5 封）
1. 项目周报 - 项目A
2. 会议邀请: 项目评审会 4/25 14:00
...

## 📊 统计
- 总计检查: 20 封
- P0: 2 封, P1: 5 封, P2: 8 封, P3: 5 封
```

---

_创建时间: 2026-04-23 | 版本: v1.0 | 作者: Iris 🐦‍⬛_
