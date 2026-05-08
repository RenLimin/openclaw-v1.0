# OpenClaw 进阶配置指南 v1.0

> **目标**：创建功能完善、安全可靠、性能优化的企业级智能体系统
> **基于官方文档版本**：2026.4.15
> **最后更新**：2026-05-07

---

## 目录

1. [智能体架构设计](#一智能体架构设计)
2. [技能系统配置](#二技能系统配置)
3. [工具权限与沙箱](#三工具权限与沙箱)
4. [子代理编排](#四子代理编排)
5. [自动化任务](#五自动化任务)
6. [通道集成](#六通道集成)
7. [性能优化](#七性能优化)
8. [完整配置示例](#八完整配置示例)
9. [故障排查与监控](#九故障排查与监控)

---

## 一、智能体架构设计

### 1.1 企业级智能体架构参考

```
┌─────────────────────────────────────────────────────────────┐
│                     协调智能体 (main)                        │
│              任务分发、结果汇总、用户交互                     │
└────────────────┬────────────────┬───────────────────────────┘
                 │                │
    ┌────────────▼────────┐   ┌───▼─────────────────┐
    │ 合同智能体 (ella)   │   │ 项目智能体 (oliver) │
    │ OA审批、合同解析     │   │ 项目管理、ONES操作   │
    └─────────────────────┘   └─────────────────────┘
                 │                │
    ┌────────────▼────────┐   ┌───▼─────────────────┐
    │ 经营智能体 (aaron)  │   │ 巡检智能体 (iris)   │
    │ 报告生成、数据分析    │   │ 邮件管理、自动巡检  │
    └─────────────────────┘   └─────────────────────┘
```

### 1.2 智能体配置规范

每个智能体应具备独立的：
- **工作区** (`workspace`) - 文件操作隔离
- **状态目录** (`agentDir`) - 会话、认证隔离
- **模型配置** - 根据任务选择合适模型
- **工具权限** - 最小权限原则
- **技能集** - 任务专用技能

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "主协调智能体",
        workspace: "/Users/bangcle/.openclaw/workspace",
        model: "Volcengine/ark-code-latest",
        tools: {
          profile: "coding",
          alsoAllow: ["sessions_spawn", "sessions_send", "subagents"],
        },
      },
      {
        id: "ella",
        name: "合同管理智能体",
        workspace: "/Users/bangcle/.openclaw/agents/ella/workspace",
        agentDir: "/Users/bangcle/.openclaw/agents/ella",
        model: "Volcengine/ark-code-latest",
        skills: ["oa-approval", "contract-parse"],
        tools: { profile: "coding" },
      },
      // ... 更多智能体
    ],
  },
}
```

### 1.3 路由绑定配置

```json5
{
  bindings: [
    // 企业微信消息路由到主智能体
    { agentId: "main", match: { channel: "wecom" } },
    // 特定用户的合同审批请求路由到ella
    {
      agentId: "ella",
      match: {
        channel: "wecom",
        peer: { kind: "direct", id: "1313" },
      },
    },
  ],
}
```

---

## 二、技能系统配置

### 2.1 技能优先级与加载顺序

技能加载优先级（从高到低）：
1. 工作区技能 (`<workspace>/skills`)
2. 项目智能体技能 (`<workspace>/.agents/skills`)
3. 个人智能体技能 (`~/.agents/skills`)
4. 托管/本地技能 (`~/.openclaw/skills`)
5. 捆绑技能（内置）
6. 额外技能目录（最低）

### 2.2 技能配置示例

```json5
{
  skills: {
    // 技能加载配置
    load: {
      watch: true, // 热重载
      watchDebounceMs: 250,
      extraDirs: ["/opt/openclaw/shared-skills"],
    },

    // 单个技能配置
    entries: {
      "oa-approval": {
        enabled: true,
        config: {
          oaServer: "https://oa.example.com",
          timeoutSeconds: 30,
        },
      },
      "contract-parse": {
        enabled: true,
        env: {
          OCR_API_KEY: "your-ocr-key",
        },
      },
    },
  },
}
```

### 2.3 每个智能体独立技能集

```json5
{
  agents: {
    defaults: {
      // 默认继承所有技能
    },
    list: [
      {
        id: "ella",
        // 仅加载合同相关技能
        skills: ["oa-approval", "contract-parse", "memory-search"],
      },
      {
        id: "oliver",
        // 仅加载项目管理相关技能
        skills: ["ones-project", "knowledge-base", "memory-search"],
      },
      {
        id: "iris",
        // 无技能权限 - 纯巡检
        skills: [],
      },
    ],
  },
}
```

---

## 三、工具权限与沙箱

### 3.1 工具权限层级

工具权限应用顺序（从宽到严）：
1. `tools.profile` - 基础配置文件
2. `tools.allow` / `tools.deny` - 全局白/黑名单
3. `agents.defaults.tools.*` - 智能体默认
4. `agents.list[].tools.*` - 单个智能体覆盖
5. `tools.byProvider` - 按提供商限制

### 3.2 工具配置文件详解

| 配置文件 | 包含工具 | 适用场景 |
|---------|---------|---------|
| `full` | 所有核心和可选插件工具 | 全能智能体，无限制 |
| `coding` | 文件系统、运行时、Web、会话、内存、媒体等 | 代码开发、通用任务 |
| `messaging` | 消息发送、会话查询 | 纯消息路由、通知机器人 |
| `minimal` | 仅 session_status | 只读、监控用途 |

```json5
{
  tools: {
    // 基础配置文件
    profile: "coding",

    // 额外允许的工具
    alsoAllow: ["browser", "sessions_spawn", "subagents"],

    // 明确禁止的工具
    deny: ["gateway"],

    // 按提供商限制
    byProvider: {
      "third-party-plugin": { profile: "minimal" },
    },
  },
}
```

### 3.3 沙箱安全配置

```json5
{
  agents: {
    defaults: {
      sandbox: {
        // 模式: off | non-main | all
        mode: "non-main",

        // 范围: agent | session | shared
        scope: "agent",

        // 工作区访问: none | ro | rw
        workspaceAccess: "ro",

        // 后端: docker | ssh | openshell
        backend: "docker",

        // Docker 特定配置
        docker: {
          // 自定义挂载（只读）
          binds: ["/opt/shared-data:/data:ro"],

          // GPU 支持
          // gpus: "all",
        },
      },
    },
  },
}
```

### 3.4 沙箱模式选择指南

| 场景 | 推荐模式 | 说明 |
|------|---------|------|
| 开发/测试环境 | `off` | 便于调试，全主机访问 |
| 生产环境 - 主智能体 | `non-main` | 主会话在主机，其他隔离 |
| 生产环境 - 高安全 | `all` | 所有会话完全隔离 |
| 多租户场景 | `session` | 每个用户独立容器 |
| 团队共享 | `shared` | 团队成员共享一个容器 |

---

## 四、子代理编排

### 4.1 子代理配置

```json5
{
  agents: {
    defaults: {
      subagents: {
        // 子代理默认模型（可以更便宜）
        model: "qwen/qwen-plus",

        // 默认思考级别
        thinking: "fast",

        // 最大嵌套深度: 1 (默认) | 2 (编排器模式)
        maxSpawnDepth: 2,

        // 每个智能体最大子代理数
        maxChildrenPerAgent: 5,

        // 全局并发限制
        maxConcurrent: 8,

        // 默认运行超时（秒）
        runTimeoutSeconds: 900,

        // 自动归档时间（分钟）
        archiveAfterMinutes: 60,

        // 允许的目标智能体
        allowAgents: ["ella", "oliver", "aaron"],

        // 是否强制指定 agentId
        requireAgentId: true,
      },
    },
  },
}
```

### 4.2 编排器模式（深度=2）

当 `maxSpawnDepth = 2` 时支持三级架构：
- **深度 0**：主智能体（用户交互）
- **深度 1**：编排器子智能体（任务分解）
- **深度 2**：工作者子智能体（实际执行）

```
用户 → main (深度0)
  ↓ spawn
  ella-orchestrator (深度1, 编排器)
    ↓ spawn (深度1可再创建子代理)
    worker-1 (深度2, OCR)
    worker-2 (深度2, 数据提取)
    worker-3 (深度2, 审批提交)
```

### 4.3 子代理创建方式

#### 方式1：工具调用（推荐）

```javascript
// 从智能体内部创建子代理
sessions_spawn({
  task: "分析这份合同中的履约义务条款",
  label: "contract-analysis-001",
  agentId: "ella",
  model: "Volcengine/ark-code-latest",
  thinking: "high",
  runTimeoutSeconds: 1800,
  context: "fork", // 继承当前会话上下文 | isolated
  cleanup: "keep",
})
```

#### 方式2：命令行

```bash
# 列出当前子代理
/subagents list

# 杀死子代理
/subagents kill <id>

# 查看子代理日志
/subagents log <id> [limit]

# 发送消息给子代理
/subagents send <id> "请加快进度"

# 引导子代理
/subagents steer <id> "注意检查第5条条款"

# 手动创建
/subagents spawn ella "处理OA审批" --model Volcengine/ark-code-latest
```

---

## 五、自动化任务

### 5.1 Cron 配置

```json5
{
  cron: {
    enabled: true,

    // 最大并发运行数
    maxConcurrentRuns: 4,

    // 会话保留时间
    sessionRetention: "168h", // 7天

    // 运行日志配置
    runLog: {
      maxBytes: "10mb",
      keepLines: 5000,
    },

    // 全局失败通知目标
    failureDestination: {
      mode: "announce",
      channel: "wecom",
      to: "1313",
    },
  },
}
```

### 5.2 常见任务类型

#### 每日巡检

```bash
openclaw cron add \
  --name "每日系统巡检" \
  --cron "0 9 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "执行每日系统巡检：检查OA待办、ONES任务、邮件未读，并生成汇总报告" \
  --agentId "iris" \
  --thinking "high" \
  --announce \
  --channel wecom \
  --to "1313"
```

#### 每周报告

```bash
openclaw cron add \
  --name "每周项目报告" \
  --cron "0 18 * * 5" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "生成本周项目进度报告，从ONES获取数据，分析风险点" \
  --agentId "oliver" \
  --model "Volcengine/ark-code-latest" \
  --announce
```

#### 合同到期提醒

```bash
openclaw cron add \
  --name "合同到期检查" \
  --cron "0 10 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "查询30天内到期的合同，发送提醒通知" \
  --agentId "ella" \
  --tools "read,exec" \
  --announce
```

### 5.3 Webhook 集成

```json5
{
  hooks: {
    enabled: true,
    token: "your-secure-webhook-token",
    path: "/hooks",

    // 允许的智能体ID
    allowedAgentIds: ["main", "ella", "oliver"],

    // 自定义映射
    mappings: [
      {
        match: { path: "oa-approval" },
        action: "agent",
        agentId: "ella",
        message: "收到OA审批webhook，请处理",
        deliver: true,
      },
      {
        match: { path: "ones-webhook" },
        action: "agent",
        agentId: "oliver",
        deliver: false,
      },
    ],
  },
}
```

使用示例：

```bash
# 触发智能体运行
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H "Authorization: Bearer your-secure-webhook-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "新的合同审批请求已到达",
    "name": "OA审批Webhook",
    "agentId": "ella",
    "deliver": true
  }'
```

---

## 六、通道集成

### 6.1 企业微信配置

```json5
{
  channels: {
    wecom: {
      enabled: true,
      botId: "your-bot-id",
      secret: "your-bot-secret",

      // DM 策略: pairing | allowlist | open | disabled
      dmPolicy: "allowlist",

      // 群组策略
      groupPolicy: "allowlist",

      // 允许的用户列表
      allowFrom: ["1313", "1314", "1315"],

      // 允许的群组
      groupAllowFrom: ["group-123", "group-456"],
    },
  },
}
```

### 6.2 多通道策略

| 通道 | 推荐用途 | 安全策略 |
|------|---------|---------|
| 企业微信 | 内部团队协作 | allowlist + 群组需@ |
| WebChat | 管理后台调试 | loopback 仅本地 |
| Telegram | 外部通知 | pairing 模式 |
| Discord | 社区支持 | 群组 mention 模式 |

### 6.3 群组消息最佳实践

```json5
{
  messages: {
    visibleReplies: "message_tool",
    groupChat: {
      visibleReplies: "message_tool",
      requireMention: true, // 必须@才响应
    },
  },
}
```

---

## 七、性能优化

### 7.1 内存优化

```json5
{
  session: {
    // 会话隔离模式
    dmScope: "per-channel-peer",

    // 每日自动重置（凌晨4点）
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,
    },

    // 线程绑定超时
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 168, // 7天
    },
  },
}
```

### 7.2 Token 使用优化

```json5
{
  agents: {
    defaults: {
      // 图片自动缩放降低Token
      imageMaxDimensionPx: 1200,

      // 模型降级链
      model: {
        primary: "Volcengine/ark-code-latest",
        fallbacks: ["qwen/qwen-plus", "deepseek/deepseek-chat"],
      },

      // 子代理使用更经济的模型
      subagents: {
        model: "qwen/qwen-plus",
        thinking: "fast",
      },
    },
  },
}
```

### 7.3 网关健康检查

```json5
{
  gateway: {
    // 通道健康检查间隔（分钟）
    channelHealthCheckMinutes: 5,

    // 通道事件超时（分钟）
    channelStaleEventThresholdMinutes: 30,

    // 单通道最大重启次数/小时
    channelMaxRestartsPerHour: 10,

    // 握手超时
    handshakeTimeoutMs: 15000,
  },
}
```

---

## 八、完整配置示例

### 8.1 企业级生产配置

```json5
{
  // ============================================
  // 模型提供商配置
  // ============================================
  models: {
    mode: "merge",
    providers: {
      Volcengine: {
        baseUrl: "https://ark.cn-beijing.volces.com/api/coding/v3",
        apiKey: "your-ark-key",
        api: "openai-completions",
        models: [
          {
            id: "ark-code-latest",
            name: "ark-code-latest",
            contextWindow: 1000000,
            maxTokens: 65536,
          },
        ],
      },
      qwen: {
        baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1",
        apiKey: "your-qwen-key",
        api: "openai-completions",
        models: [
          {
            id: "qwen-plus",
            name: "qwen-plus",
            contextWindow: 131072,
            maxTokens: 65536,
          },
        ],
      },
    },
  },

  // ============================================
  // 智能体配置
  // ============================================
  agents: {
    defaults: {
      model: {
        primary: "Volcengine/ark-code-latest",
        fallbacks: ["qwen/qwen-plus"],
      },
      models: {
        "Volcengine/ark-code-latest": {},
        "qwen/qwen-plus": {},
      },
      memorySearch: { enabled: true },
      compaction: { mode: "safeguard" },
      heartbeat: { every: "30m", target: "last" },
      imageMaxDimensionPx: 1200,
      sandbox: {
        mode: "non-main",
        scope: "agent",
        workspaceAccess: "ro",
        backend: "docker",
      },
      subagents: {
        model: "qwen/qwen-plus",
        thinking: "fast",
        maxSpawnDepth: 2,
        maxChildrenPerAgent: 5,
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
        allowAgents: ["*"],
        requireAgentId: true,
      },
      tools: { profile: "coding" },
    },

    list: [
      {
        id: "main",
        default: true,
        name: "主协调智能体",
        workspace: "/Users/bangcle/.openclaw/workspace",
        tools: {
          alsoAllow: ["sessions_spawn", "sessions_send", "subagents"],
        },
      },
      {
        id: "ella",
        name: "合同管理智能体",
        workspace: "/Users/bangcle/.openclaw/agents/ella/workspace",
        agentDir: "/Users/bangcle/.openclaw/agents/ella",
        skills: ["oa-approval", "contract-parse", "knowledge-base"],
      },
      {
        id: "oliver",
        name: "项目管理智能体",
        workspace: "/Users/bangcle/.openclaw/agents/oliver/workspace",
        agentDir: "/Users/bangcle/.openclaw/agents/oliver",
        skills: ["ones-project", "knowledge-base"],
      },
      {
        id: "aaron",
        name: "经营管理智能体",
        workspace: "/Users/bangcle/.openclaw/agents/aaron/workspace",
        agentDir: "/Users/bangcle/.openclaw/agents/aaron",
        skills: ["business-report"],
      },
      {
        id: "iris",
        name: "智能巡检智能体",
        workspace: "/Users/bangcle/.openclaw/agents/iris/workspace",
        agentDir: "/Users/bangcle/.openclaw/agents/iris",
        tools: { allow: ["read", "exec", "memory_search"] },
      },
    ],
  },

  // ============================================
  // 路由绑定
  // ============================================
  bindings: [
    { agentId: "main", match: { channel: "wecom" } },
    { agentId: "ella", match: { channel: "wecom", peer: { id: "contract-group" } } },
    { agentId: "oliver", match: { channel: "wecom", peer: { id: "project-group" } } },
  ],

  // ============================================
  // 网关配置
  // ============================================
  gateway: {
    mode: "local",
    auth: { mode: "token", token: "your-gateway-token" },
    port: 18789,
    bind: "loopback",
    tailscale: { mode: "off" },
    controlUi: { allowInsecureAuth: true },
    channelHealthCheckMinutes: 5,
    channelStaleEventThresholdMinutes: 30,
    handshakeTimeoutMs: 15000,
  },

  // ============================================
  // 会话管理
  // ============================================
  session: {
    dmScope: "per-channel-peer",
    reset: { mode: "daily", atHour: 4, idleMinutes: 120 },
    threadBindings: { enabled: true, idleHours: 24, maxAgeHours: 168 },
  },

  // ============================================
  // 消息策略
  // ============================================
  messages: {
    visibleReplies: "message_tool",
    groupChat: { visibleReplies: "message_tool", requireMention: true },
  },

  // ============================================
  // Cron 定时任务
  // ============================================
  cron: {
    enabled: true,
    maxConcurrentRuns: 4,
    sessionRetention: "168h",
    runLog: { maxBytes: "10mb", keepLines: 5000 },
  },

  // ============================================
  // Webhook
  // ============================================
  hooks: {
    enabled: true,
    token: "your-webhook-token",
    path: "/hooks",
    allowedAgentIds: ["main", "ella", "oliver", "aaron", "iris"],
  },

  // ============================================
  // 通道配置
  // ============================================
  channels: {
    wecom: {
      enabled: true,
      botId: "your-bot-id",
      secret: "your-bot-secret",
      dmPolicy: "allowlist",
      groupPolicy: "allowlist",
      allowFrom: ["1313", "1314", "1315"],
    },
    webchat: { enabled: true },
  },

  // ============================================
  // 插件配置
  // ============================================
  plugins: {
    entries: {
      "wecom-openclaw-plugin": { enabled: true },
      "openclawwechat": { enabled: true },
    },
    allow: ["wecom-openclaw-plugin", "memory-core", "volcengine", "deepseek"],
  },

  // ============================================
  // 向导配置
  // ============================================
  wizard: {
    lastRunAt: "2026-04-15T11:24:04.637Z",
    lastRunVersion: "2026.4.14",
    lastRunCommand: "doctor",
    lastRunMode: "local",
  },
  meta: {
    lastTouchedVersion: "2026.4.15",
    lastTouchedAt: "2026-05-07T03:56:00.000Z",
  },
}
```

---

## 九、故障排查与监控

### 9.1 常用诊断命令

```bash
# 配置验证
openclaw doctor
openclaw doctor --fix

# 网关状态
openclaw gateway status
openclaw gateway restart

# 通道状态
openclaw channels status
openclaw channels status --probe

# 智能体列表
openclaw agents list
openclaw agents list --bindings

# 会话列表
openclaw sessions list

# Cron 任务
openclaw cron list
openclaw cron show <job-id>
openclaw cron runs --id <job-id>

# 工具列表
openclaw tools list

# 查看日志
openclaw logs
tail -f ~/.openclaw/logs/gateway.log
```

### 9.2 常见问题

#### 问题1：智能体无法加载技能

**排查步骤：**
1. 检查技能目录权限
2. 检查 `skills.entries.<name>.enabled`
3. 检查智能体 `skills` 白名单
4. 运行 `openclaw skills list` 查看已加载技能

#### 问题2：沙箱命令执行失败

**排查步骤：**
1. 确认 Docker 正在运行：`docker ps`
2. 检查工作区挂载权限
3. 查看沙箱日志：`openclaw sandbox logs`
4. 尝试临时关闭沙箱测试

#### 问题3：模型调用频繁失败

**排查步骤：**
1. 检查 API Key 有效性
2. 检查网络连接和代理设置
3. 检查 Token 配额
4. 配置 fallback 模型链

#### 问题4：子代理创建失败

**排查步骤：**
1. 检查 `subagents.maxConcurrent` 限制
2. 检查 `subagents.allowAgents` 白名单
3. 检查父智能体是否有 `sessions_spawn` 工具权限
4. 检查嵌套深度限制

### 9.3 监控建议

**建议监控指标：**
1. 网关进程健康状态
2. 各通道连接状态
3. 模型 API 调用成功率/延迟
4. 子代理并发数/队列长度
5. Cron 任务成功率
6. 内存/CPU 使用情况

**告警阈值建议：**
- 模型调用成功率 < 95% → 警告
- 模型调用成功率 < 80% → 严重
- Cron 任务连续失败 3 次 → 警告
- 网关内存 > 80% → 警告

---

## 附录

### A. 配置文件参考路径

| 文件 | 路径 |
|------|------|
| 主配置 | `~/.openclaw/openclaw.json` |
| 工作区 | `~/.openclaw/workspace/` |
| 智能体状态 | `~/.openclaw/agents/<id>/` |
| 会话记录 | `~/.openclaw/agents/<id>/sessions/` |
| 凭证 | `~/.openclaw/credentials/` |
| 日志 | `~/.openclaw/logs/` |
| Cron 任务 | `~/.openclaw/cron/jobs.json` |

### B. 官方文档参考

- 主文档：https://docs.openclaw.ai/
- 技能：https://docs.openclaw.ai/tools/skills
- 沙箱：https://docs.openclaw.ai/gateway/sandboxing
- 子代理：https://docs.openclaw.ai/tools/subagents
- Cron：https://docs.openclaw.ai/automation/cron-jobs
- 工具：https://docs.openclaw.ai/tools

---

*本配置指南基于 OpenClaw 官方文档和业界最佳实践整理，适用于企业级生产环境部署*
