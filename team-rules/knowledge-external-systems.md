# 知识库与外部系统 v1.0

> **目的**: 集中管理知识库和外部系统接入文档
> **维护者**: Jerry (定期更新)

---

## 一、知识库结构

```
knowledge-base/
├── README.md                    # 知识库说明
├── glossary.md                  # 术语表
├── sop/                         # 标准操作流程
│   ├── contract-approval.md     # 合同审批流程
│   ├── project-tracking.md      # 项目跟踪流程
│   ├── email-processing.md      # 邮件处理流程
│   └── report-generation.md     # 报表生成流程
├── api-docs/                    # API 文档
│   ├── oa-api.md                # 泛微 OA API
│   ├── ones-api.md              # 万事 ONES API
│   └── email-api.md             # 邮件 API
├── training/                    # 培训资料
│   ├── agent-onboarding.md      # Agent 入职指南
│   └── skill-tutorials/         # 技能教程
└── lessons-learned/             # 经验教训
    └── YYYY-MM-DD.md            # 按日期记录
```

---

## 二、术语表

| 术语 | 全称 | 说明 |
|------|------|------|
| OA | Office Automation | 办公自动化系统 (泛微) |
| ONES | 万事 ONES | 项目管理系统 |
| KPI | Key Performance Indicator | 关键绩效指标 |
| SOP | Standard Operating Procedure | 标准操作流程 |
| API | Application Programming Interface | 应用程序接口 |
| OAuth | Open Authorization | 开放授权协议 |
| IMAP | Internet Message Access Protocol | 邮件访问协议 |
| SMTP | Simple Mail Transfer Protocol | 简单邮件传输协议 |

---

## 三、外部系统清单

| 系统 | 负责 Agent | 用途 | 接入方式 | 状态 |
|------|-----------|------|---------|------|
| 泛微 OA | Ella 🦊 | 合同审批流程 | API | ⏳ 待配置 |
| 万事 ONES | Oliver 🐘 | 项目管理 | API | ⏳ 待配置 |
| 网易邮箱 | Iris 🐦‍⬛ | 邮件收发 | IMAP/SMTP | ⏳ 待配置 |
| Office 365 | Iris 🐦‍⬛ | 邮件/日历 | OAuth | ⏳ 待配置 |
| 企业微信 | Jerry 🦞 | 消息通道 | WebSocket | ✅ 已接入 |
| ClawChat | Jerry 🦞 | 消息通道 | HTTP Polling | ✅ 已接入 |
| 百炼 API | 全局 | AI 模型 | REST API | ✅ 已接入 |
| GitHub | 全局 | 代码备份 | PAT | ✅ 已接入 |
| Tavily API | 全局 | 搜索服务 | REST API | ✅ 已接入 |

---

## 四、待配置系统详情

### 4.1 泛微 OA

| 配置项 | 值 | 说明 |
|--------|-----|------|
| API 地址 | 待提供 | OA 系统 API 端点 |
| 认证方式 | 待确认 | Token / OAuth |
| 负责 Agent | Ella | 合同审批操作 |

### 4.2 万事 ONES

| 配置项 | 值 | 说明 |
|--------|-----|------|
| API 地址 | 待提供 | ONES 系统 API 端点 |
| 认证方式 | 待确认 | Token / OAuth |
| 负责 Agent | Oliver | 项目操作 |

### 4.3 网易邮箱

| 配置项 | 值 | 说明 |
|--------|-----|------|
| IMAP 服务器 | 待确认 | 如 imap.163.com |
| SMTP 服务器 | 待确认 | 如 smtp.163.com |
| 负责 Agent | Iris | 邮件收发 |

### 4.4 Office 365

| 配置项 | 值 | 说明 |
|--------|-----|------|
| OAuth 端点 | 待确认 | Microsoft 认证端点 |
| Client ID | 待提供 | Azure AD 应用 ID |
| 负责 Agent | Iris | 邮件/日历 |

---

## 五、凭证管理

所有外部系统凭证存储在 macOS Keychain 中：

```bash
# 存储凭证
security add-generic-password \
    -s "openclaw-{system}-{credential}" \
    -a "{agent}" \
    -w "{value}" \
    -U

# 读取凭证
security find-generic-password \
    -s "openclaw-{system}-{credential}" \
    -w
```

---

_创建时间: 2026-04-12 15:45 | 版本: v1.0 | 作者: Jerry 🦞_
