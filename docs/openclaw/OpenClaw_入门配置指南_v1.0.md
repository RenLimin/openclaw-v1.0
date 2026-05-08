# OpenClaw 入门配置指南 v1.0

> **目标**：快速配置一个可用的智能体，确保安全、稳定、可扩展
> **最后更新**：2026-05-07

---

## 一、前置检查清单

### 1.1 环境要求

| 项目 | 要求 | 检查命令 |
|------|------|---------|
| Node.js 版本 | 24.x（推荐）或 22.14+ | `node --version` |
| 内存 | ≥ 8GB | `free -h`（Linux）/ `top`（macOS） |
| 磁盘空间 | ≥ 2GB | `df -h` |
| 网络 | 可访问模型提供商 API | `curl -I https://api.anthropic.com` |

### 1.2 必备项

- [ ] 至少一个模型提供商的 API Key（Anthropic、OpenAI、Google 等）
- [ ] 已安装 OpenClaw：`npm install -g openclaw@latest`
- [ ] 配置文件目录已创建：`~/.openclaw/`

---

## 二、最小可用配置

### 2.1 配置文件位置

```bash
~/.openclaw/openclaw.json
```

### 2.2 单智能体最小配置（JSON5）

```json5
{
  // 网关基础配置
  gateway: {
    port: 18789,
    bind: "127.0.0.1",
    token: "your-gateway-secret-token-here",
    controlUi: { enabled: true },
  },

  // 智能体配置
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["openai/gpt-4o"],
      },
      heartbeat: {
        every: "30m",
        target: "last",
      },
    },
  },

  // 会话管理
  session: {
    dmScope: "per-channel-peer",
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,
    },
  },

  // WebChat 通道（默认启用）
  channels: {
    webchat: {
      enabled: true,
    },
  },

  // 消息策略
  messages: {
    visibleReplies: "message_tool",
    groupChat: {
      visibleReplies: "message_tool",
      requireMention: true,
    },
  },
}
```

---

## 三、生产级安全配置

### 3.1 完整安全配置模板

```json5
{
  gateway: {
    port: 18789,
    bind: "127.0.0.1",  // 生产环境不要绑定 0.0.0.0
    token: "CHANGE_TO_STRONG_RANDOM_TOKEN",
    controlUi: {
      enabled: true,
      // 生产环境可考虑禁用外部访问
      // public: false,
    },
    handshakeTimeoutMs: 15000,
    channelHealthCheckMinutes: 5,
    channelStaleEventThresholdMinutes: 30,
  },

  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["openai/gpt-4o"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "openai/gpt-4o": { alias: "GPT-4o" },
      },
      // 沙箱隔离 - 推荐生产环境启用
      sandbox: {
        mode: "non-main",  // off | non-main | all
        scope: "agent",
      },
      // 工具权限控制 - 最小权限原则
      tools: {
        allow: ["read", "exec", "memory_search"],
        deny: [],  // 空数组表示使用 defaults
      },
      // 心跳配置
      heartbeat: {
        every: "30m",
        target: "last",
      },
      // 图片缩放 - 降低 token 消耗
      imageMaxDimensionPx: 1200,
    },
  },

  // 会话隔离配置
  session: {
    dmScope: "per-channel-peer",  // 多用户环境推荐
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 168,  // 7 天
    },
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,
    },
  },

  // 通道配置示例：Telegram（最快启用）
  channels: {
    webchat: { enabled: true },
    telegram: {
      enabled: false,  // 设置为 true 启用
      accounts: {
        default: {
          botToken: "YOUR_TELEGRAM_BOT_TOKEN",
          dmPolicy: "pairing",  // pairing | allowlist | open | disabled
          // allowFrom: ["tg:123456789"],  // 白名单模式时启用
        },
      },
    },
  },

  // Cron 定时任务
  cron: {
    enabled: true,
    maxConcurrentRuns: 2,
    sessionRetention: "24h",
    runLog: {
      maxBytes: "2mb",
      keepLines: 2000,
    },
  },

  // 消息策略
  messages: {
    visibleReplies: "message_tool",
    groupChat: {
      visibleReplies: "message_tool",
      requireMention: true,
    },
  },
}
```

---

## 四、多智能体配置（进阶）

### 4.1 双智能体架构示例

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["openai/gpt-4o"],
      },
    },
    list: [
      {
        id: "main",
        default: true,
        name: "日常助手",
        workspace: "~/.openclaw/workspace-main",
        agentDir: "~/.openclaw/agents/main/agent",
      },
      {
        id: "coding",
        name: "编程助手",
        workspace: "~/.openclaw/workspace-coding",
        agentDir: "~/.openclaw/agents/coding/agent",
        model: "anthropic/claude-opus-4-6",
      },
    ],
  },

  // 路由绑定
  bindings: [
    { agentId: "main", match: { channel: "webchat" } },
    { agentId: "coding", match: { channel: "telegram", accountId: "coding" } },
  ],

  // 智能体间通信（默认禁用）
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["main", "coding"],
    },
  },
}
```

---

## 五、配置管理命令

### 5.1 基础命令

```bash
# 查看配置
openclaw config get agents.defaults.workspace

# 设置配置
openclaw config set agents.defaults.heartbeat.every "2h"

# 删除配置项
openclaw config unset plugins.entries.brave.config.webSearch.apiKey

# 查看完整配置 Schema
openclaw config schema

# 验证配置
openclaw doctor

# 自动修复配置
openclaw doctor --fix
```

### 5.2 智能体管理

```bash
# 添加新智能体
openclaw agents add coding

# 列出所有智能体及绑定
openclaw agents list --bindings
```

### 5.3 网关控制

```bash
# 查看网关状态
openclaw gateway status

# 重启网关
openclaw gateway restart

# 打开控制面板
openclaw dashboard
```

---

## 六、验证部署步骤

### 6.1 五步验证法

1. **配置验证**
   ```bash
   openclaw doctor
   ```
   ✅ 预期：无错误输出

2. **网关启动**
   ```bash
   openclaw gateway start
   openclaw gateway status
   ```
   ✅ 预期：显示 "listening on 127.0.0.1:18789"

3. **控制面板访问**
   ```bash
   openclaw dashboard
   ```
   ✅ 预期：浏览器打开 Control UI

4. **发送测试消息**
   - 在 Control UI 中发送 "Hello"
   ✅ 预期：收到智能体回复

5. **会话持久化验证**
   - 刷新页面
   ✅ 预期：历史消息保留

---

## 七、安全最佳实践

| 项目 | 建议 | 原因 |
|------|------|------|
| `gateway.bind` | 使用 `127.0.0.1` | 防止外部直接访问 |
| `gateway.token` | 强随机密码 | 防止未授权访问 |
| `dmPolicy` | 使用 `pairing` 或 `allowlist` | 阻止未知发件人 |
| `sandbox.mode` | 设置为 `non-main` 或 `all` | 隔离执行环境 |
| `tools.allow` | 最小权限原则 | 减少攻击面 |
| `session.dmScope` | `per-channel-peer` | 用户会话隔离 |
| `groupChat.requireMention` | `true` | 防止群消息骚扰 |

---

## 八、常见问题排查

### 8.1 配置验证失败

```bash
# 查看详细错误
openclaw doctor

# 恢复上一个可用配置
openclaw doctor --fix
```

### 8.2 网关无法启动

```bash
# 查看日志
openclaw logs

# 检查端口占用
lsof -i :18789  # macOS/Linux
netstat -ano | findstr :18789  # Windows
```

### 8.3 模型调用失败

- 检查 API Key 是否正确配置
- 检查网络连接是否正常
- 检查 API 余额/配额是否充足
- 查看 `~/.openclaw/agents/main/agent/auth-profiles.json`

---

## 九、下一步扩展

1. **连接更多通道**：Telegram、Discord、WhatsApp、Slack 等
2. **启用技能**：GitHub、Web Search、Browser 等
3. **配置定时任务**：使用 Cron 实现自动化
4. **设置 Webhook**：集成外部系统
5. **启用移动端配对**：iOS/Android App

---

## 附录：配置文件参考

| 路径 | 说明 |
|------|------|
| `~/.openclaw/openclaw.json` | 主配置文件 |
| `~/.openclaw/workspace/` | 智能体工作区 |
| `~/.openclaw/agents/<id>/agent/` | 智能体状态目录 |
| `~/.openclaw/agents/<id>/sessions/` | 会话历史 |
| `~/.openclaw/credentials/` | 通道凭证 |

---

*本指南基于 OpenClaw 官方文档整理，确保在生产环境安全可用*
