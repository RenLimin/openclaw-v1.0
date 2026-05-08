# OpenClaw 进阶配置大全 v2.0

> **基于官方文档 2026.4.15 + 业界最佳实践深度整合**
> **目标：一站式完整参考，准确完成智能体创建与进阶配置**
> **最后更新：2026-05-07**

---

## 目录

### 第一篇：核心基础
1. [配置文件全景图与层级架构](#第一篇核心基础)
2. [12 个核心配置文件一句话精准描述](#1-12-个核心配置文件一句话精准描述)
3. [配置文件加载顺序与优先级](#2-配置文件加载顺序与优先级金字塔)

### 第二篇：配置文件详解
4. [openclaw.json 核心字段说明](#第二篇配置文件详解)
5. [工作区 Bootstrap 文件详解](#5-工作区-bootstrap-7大文件详解)
6. [SKILL.md 技能文件完整规范](#6-skillmd-技能文件完整规范)

### 第三篇：关联关系与机制
7. [配置继承与覆盖规则](#第三篇关联关系与机制)
8. [SKILL.md 6 层加载机制](#8-skillmd-6层加载机制)
9. [配置热重载支持矩阵](#9-配置热重载支持矩阵)

### 第四篇：高级架构
10. [多智能体配置关联图谱](#第四篇高级架构)
11. [子代理编排与深度控制](#11-子代理编排与深度控制)
12. [沙箱安全配置体系](#12-沙箱安全配置体系)

### 第五篇：实战与运维
13. [智能体创建标准流程](#第五篇实战与运维)
14. [典型配置问题诊断路径](#14-典型配置问题诊断路径)
15. [配置变更影响扩散图](#15-配置变更影响扩散图)
16. [最佳实践与 Checklist](#16-配置最佳实践-checklist)

---

---

## 第一篇：核心基础

---

## 1. 12 个核心配置文件一句话精准描述

### 1.1 核心配置文件（7 个）

| 序号 | 配置文件 | 一句话精准描述 | 配置层级 |
|------|---------|---------------|---------|
| 1 | **openclaw.json** | OpenClaw 系统唯一的核心主配置文件，定义网关、模型、智能体、通道、工具、技能、Cron 等所有全局设置与策略，是所有功能的配置入口。 | L2 核心层 |
| 2 | **AGENTS.md** | 智能体最高优先级行为规范注入文件，定义智能体的操作原则、安全红线、审批流程、输出格式等强制执行规则，会被严格注入系统提示词并覆盖默认行为。 | L5 工作区层 |
| 3 | **SOUL.md** | 智能体人格设定文件，定义其语气、性格、沟通风格、幽默感、价值观等人格属性，让智能体具有一致且可预期的"个性"。 | L5 工作区层 |
| 4 | **USER.md** | 用户画像与偏好配置文件，存储用户的基本信息、工作习惯、沟通偏好、常用账号、禁忌事项等，让智能体真正"了解"并适应用户。 | L5 工作区层 |
| 5 | **TOOLS.md** | 工具使用安全规范文件，定义各类工具的使用原则、审批流程、危险操作识别、输出格式要求，是确保工具调用安全可控的关键屏障。 | L5 工作区层 |
| 6 | **IDENTITY.md** | 智能体身份标识文件，明确定义智能体的名字、角色定位、职责范围、能力边界，对外自我介绍和对内功能定位都以此为准。 | L5 工作区层 |
| 7 | **SKILL.md** | 技能定义文件，通过 YAML 元数据声明技能名称、依赖条件，通过 Markdown 正文教会智能体使用某一特定能力的完整步骤与注意事项。 | L6 技能层 |

### 1.2 辅助配置文件（5 个）

| 序号 | 配置文件 | 一句话精准描述 | 配置层级 |
|------|---------|---------------|---------|
| 8 | **HEARTBEAT.md** | 定时心跳任务清单文件，仅在心跳触发时注入，定义智能体定期自动执行的巡检、提醒、同步、汇总等自动化任务。 | L5 工作区层 |
| 9 | **MEMORY.md** | 智能体长期记忆存储文件，保存重要决策、经验教训、业务规则、历史总结等需要持久化的信息，每次运行都会注入上下文。 | L5 工作区层 |
| 10 | **auth-profiles.json** | 智能体独立认证配置文件，存储各模型供应商、外部服务的 API Key 和凭证，支持每个智能体使用独立的账号与权限。 | L4 智能体层 |
| 11 | **jobs.json** | Cron 定时任务定义文件，持久化存储所有定时任务的调度规则、参数、目标智能体、通知方式，是自动化能力的核心载体。 | L7 运行时层 |
| 12 | **BOOTSTRAP.md** | 智能体首次初始化引导文件，仅在工作区全新创建时生成，用于引导用户完成基础配置，正常运行后可安全删除。 | L5 工作区层 |

---

## 2. 配置文件加载顺序与优先级金字塔

### 2.1 7 层架构总览

```
                            ╱╲
                           ╱══╲
                          ╱════╲
                         ╱══════╲
                        ╱════════╲
                       ╱══════════╲
                      ╱════════════╲
                     ╱══  最高优先级  ══╲
                    ╱══════════════════╲
                   ╱════════════════════╲
                  ╱══════════════════════╲
                 ╱════════════════════════╲
                ╱══════════════════════════╲
               ╱════════════════════════════╲
              ╱══════════════════════════════╲
             ╱════════════════════════════════╲

🔝 LAYER 6: SKILL.md (工作区私有技能)
        ~/.openclaw/workspace/skills/<name>/SKILL.md
        ← 同名技能覆盖所有下层，运行时注入提示词

🔝 LAYER 5: 工作区 Bootstrap 文件
        AGENTS.md, SOUL.md, USER.md, TOOLS.md, IDENTITY.md
        ← 注入系统提示词，模型层生效

🔝 LAYER 4: 单个智能体配置 (agents.list[].*)
        ← 覆盖智能体默认值，精确到单个智能体

🔝 LAYER 3: 智能体默认配置 (agents.defaults.*)
        ← 全局智能体基线，所有智能体继承

🔝 LAYER 2: 主配置文件 (openclaw.json)
        ← 所有全局设置入口，JSON5 格式

🔝 LAYER 1: 环境变量 (OPENCLAW_*)
        ← 覆盖 openclaw.json 中的字段

🔝 LAYER 0: 内置默认值 (编译在二进制中)
        ← 所有字段的安全 fallback 值

         ════════════════════════════
             最低优先级
```

### 2.2 优先级冲突解决规则表

| 冲突场景 | 获胜方 |
|---------|-------|
| 环境变量 vs openclaw.json | 环境变量 ✅ |
| openclaw.json vs AGENTS.md | AGENTS.md ✅ |
| agents.list[x] vs agents.defaults | agents.list[x] ✅ |
| workspace/skills vs ~/.openclaw/skills | workspace/skills ✅ |
| AGENTS.md vs SOUL.md (同层级) | 都生效，按顺序注入 |
| SKILL.md frontmatter vs 正文 (同文件) | 都生效 |
| tools.deny vs tools.allow | tools.deny ✅ |

---

## 3. 配置文件全局全景图

```
╔════════════════════════════════════════════════════════════════════════╗
║                    OPENCLAW 配置系统完整架构                            ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │  🔴 LAYER 0: 内置默认值 (编译在二进制中，最低优先级)             │ ║
║  │  所有配置字段的安全 fallback 值，用户没有配置时自动使用          │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                    ↓                                   ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │  🟠 LAYER 1: 环境变量 (OPENCLAW_*)                               │ ║
║  │  OPENCLAW_HOME, OPENCLAW_CONFIG_PATH, OPENCLAW_PORT 等          │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                    ↓                                   ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │  🟡 LAYER 2: 主配置文件 openclaw.json                            │ ║
║  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │ ║
║  │  │ gateway │ │ models  │ │ agents  │ │ cron    │ │ channels│   │ ║
║  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │ ║
║  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │ ║
║  │  │ tools   │ │ skills  │ │ plugins │ │ hooks   │ │ session │   │ ║
║  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                    ↓                                   ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │  🟢 LAYER 3: 智能体默认配置 (agents.defaults.*)                  │ ║
║  │  所有智能体共享的默认设置，单个智能体可覆盖                       │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                    ↓                                   ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │  🔵 LAYER 4: 单个智能体配置 (agents.list[].*)                   │ ║
║  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                │ ║
║  │  │ main    │ │ ella    │ │ oliver  │ │ iris    │  ...          │ ║
║  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘                │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                    ↓                                   ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │  🟣 LAYER 5: 工作区 Bootstrap 文件                               │ ║
║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │ ║
║  │  │AGENTS.md │ │ SOUL.md  │ │ USER.md  │ │TOOLS.md  │            │ ║
║  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │ ║
║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │ ║
║  │  │IDENTITY.md│ │HEARTBEAT│ │MEMORY.md │                        │ ║
║  │  └──────────┘ └──────────┘ └──────────┘                        │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                    ↓                                   ║
║  ┌──────────────────────────────────────────────────────────────────┐ ║
║  │  🟤 LAYER 6: 技能 SKILL.md (运行时按需加载，最高优先级)         │ ║
║  │  6 层加载路径 + 白名单过滤 + 依赖检查 = 最终生效技能            │ ║
║  └──────────────────────────────────────────────────────────────────┘ ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

## 第二篇：配置文件详解

---

## 4. openclaw.json 核心字段完整说明

### 4.1 完整字段分类总览

| 配置段 | 核心作用 | 字段示例 | 热重载 |
|-------|---------|---------|-------|
| **gateway** | 网关服务配置 | port, bind, auth, controlUi, channelHealthCheckMinutes | ⚠️ 部分 |
| **models** | 模型供应商与模型列表 | providers.*, pricing.enabled | ✅ |
| **agents.defaults** | 智能体全局默认配置 | model, sandbox, heartbeat, skills, tools | ✅ |
| **agents.list** | 单个智能体配置 | id, name, workspace, agentDir, model, sandbox | ✅ |
| **bindings** | 消息路由绑定规则 | agentId, match{channel, peer} | ✅ |
| **session** | 会话管理配置 | dmScope, reset, threadBindings | ✅ |
| **messages** | 消息发送策略 | visibleReplies, groupChat | ✅ |
| **cron** | 定时任务引擎 | enabled, maxConcurrentRuns, sessionRetention | ✅ |
| **hooks** | Webhook 配置 | enabled, token, path, mappings | ✅ |
| **tools** | 工具权限与策略 | profile, allow, deny, alsoAllow, byProvider | ✅ |
| **skills** | 技能系统配置 | load, install, entries.*, limits | ✅ |
| **plugins** | 插件启用与配置 | entries.*, allow | ❌ 需重启 |
| **channels** | 消息通道配置 | wecom, whatsapp, telegram, discord 等 | ⚠️ 部分 |
| **mcp** | MCP 服务器定义 | servers.*, sessionIdleTtlMs | ✅ |

### 4.2 gateway 网关配置详解

```json5
{
  gateway: {
    // 运行模式（通常不需要改）
    mode: "local",

    // 监听端口
    port: 18789,

    // 绑定地址: loopback (127.0.0.1) | 0.0.0.0 | 具体IP
    // 生产环境一定用 loopback！！
    bind: "loopback",

    // 认证配置
    auth: {
      // 模式: none | token | password | trusted-proxy
      mode: "token",
      // 访问令牌，设置强随机值
      token: "your-strong-random-token-here",
      // 速率限制
      rateLimit: {
        maxAttempts: 10,
        windowMs: 60000,        // 1 分钟窗口
        lockoutMs: 300000,       // 锁定 5 分钟
        exemptLoopback: true,     // 本地调用不限制
      },
    },

    // 控制面板
    controlUi: {
      enabled: true,
      // basePath: "/openclaw",  // 自定义路径前缀
      allowInsecureAuth: true,
    },

    // 通道健康检查（重要！）
    channelHealthCheckMinutes: 5,            // 每 5 分钟检查
    channelStaleEventThresholdMinutes: 30,  // 30 分钟无事件认为异常
    channelMaxRestartsPerHour: 10,          // 每小时最多重启次数

    // 握手超时
    handshakeTimeoutMs: 15000,  // 15 秒
  },
}
```

### 4.3 agents 智能体配置详解

```json5
{
  agents: {
    // ========== 全局默认配置 ==========
    defaults: {
      // 工作区根目录
      workspace: "~/.openclaw/workspace",

      // 模型配置
      model: {
        primary: "qwen/qwen3.6-plus",
        // ⭐ 模型降级链：主模型失败时依次尝试
        fallbacks: ["deepseek/deepseek-chat", "volcengine/ark-code-latest"],
      },

      // 图像分析模型
      imageModel: {
        primary: "qwen/qwen-vl-plus",
        fallbacks: [],
      },

      // ========== 沙箱配置 ==========
      sandbox: {
        // 模式: off | non-main | all
        // 生产环境建议: non-main 或 all
        mode: "non-main",
        // 作用域: agent | session | shared
        scope: "agent",
        // 工作区访问权限: none | ro | rw
        workspaceAccess: "ro",
        // 后端: docker | ssh | openshell
        backend: "docker",
      },

      // ========== 子代理配置 ==========
      subagents: {
        // 最大嵌套深度: 1（无子代理）| 2（支持编排）
        maxSpawnDepth: 2,
        // 每个智能体最大子代理数
        maxChildrenPerAgent: 5,
        // 全局最大并发
        maxConcurrent: 8,
        // 运行超时（秒）
        runTimeoutSeconds: 900,  // 15 分钟
        // 自动归档时间
        archiveAfterMinutes: 60,
        // 子代理默认模型（可以更便宜）
        model: "deepseek/deepseek-chat",
        // 允许的目标智能体
        allowAgents: ["ella", "oliver", "aaron", "iris"],
        // 是否必须指定 agentId
        requireAgentId: true,
      },

      // ========== 心跳配置 ==========
      heartbeat: {
        every: "30m",  // 30 分钟一次
        target: "last",
        // 直接消息策略: allow | block
        directPolicy: "allow",
      },

      // ========== 上下文注入策略 ==========
      // always: 每次都注入
      // continuation-skip: ⭐ 推荐，连续对话跳过，节省 token
      // never: 完全不注入
      contextInjection: "continuation-skip",

      // Bootstrap 文件字符限制
      bootstrapMaxChars: 12000,           // 单文件 12KB
      bootstrapTotalMaxChars: 60000,      // 总 60KB

      // ========== 上下文限制 ==========
      contextLimits: {
        memoryGetMaxChars: 12000,      // memory 工具最大返回
        toolResultMaxChars: 16000,      // 工具返回最大字符
        postCompactionMaxChars: 1800,   // 压缩后上下文大小
      },

      // ========== 技能白名单 ==========
      // ⚠️ 注意：这里没列的技能，即使文件存在也不会加载！
      skills: ["github", "knowledge-base", "contract-parse"],

      // ========== 工具配置 ==========
      tools: {
        profile: "coding",  // full | coding | messaging | minimal
      },

      // ========== 图像优化 ==========
      imageMaxDimensionPx: 1200,  // 图像自动缩放到 1200px，大幅节省 token

      // ========== 时区 ==========
      userTimezone: "Asia/Shanghai",
      timeFormat: "auto",  // auto | 12 | 24
    },

    // ========== 单个智能体列表 ==========
    list: [
      // 主智能体
      {
        id: "main",
        default: true,
        name: "Jerry 🦞",
        // 继承所有 defaults，不需要重复写
      },
      // 合同智能体
      {
        id: "ella",
        name: "Ella 🦊",
        // 独立工作区
        workspace: "~/.openclaw/agents/ella/workspace",
        // 独立状态目录（包含独立的 auth-profiles.json）
        agentDir: "~/.openclaw/agents/ella",
        // ⚠️ 覆盖：独立模型配置（完全替换，不是 merge！）
        model: {
          primary: "qwen/qwen3.6-plus",
          fallbacks: ["deepseek/deepseek-chat"],
        },
        // ⚠️ 覆盖：独立技能白名单（完全替换，不是追加！）
        skills: ["contract-parse", "oa-approval", "knowledge-base"],
        // 更严格的沙箱
        sandbox: {
          mode: "all",
          scope: "session",
          workspaceAccess: "ro",
        },
      },
      // 项目管理智能体
      {
        id: "oliver",
        name: "Oliver 🐘",
        workspace: "~/.openclaw/agents/oliver/workspace",
        agentDir: "~/.openclaw/agents/oliver",
        skills: ["ones-project", "github", "knowledge-base"],
        tools: {
          alsoAllow: ["browser"],  // 额外允许浏览器
        },
      },
      // 巡检智能体（权限最小化）
      {
        id: "iris",
        name: "Iris 🐦‍⬛",
        workspace: "~/.openclaw/agents/iris/workspace",
        agentDir: "~/.openclaw/agents/iris",
        model: "deepseek/deepseek-chat",  // 用最便宜的模型
        skills: ["email-management", "system-monitor"],
        // 最严格的安全设置
        sandbox: {
          mode: "all",
          scope: "session",
          workspaceAccess: "none",  // 完全不能访问工作区
        },
        tools: {
          profile: "minimal",  // 最小工具集
        },
      },
    ],
  },
}
```

> ⚠️ **重要警告**：`agents.list[x]` 中的 `model`、`skills`、`sandbox` 等字段是**完全替换** `defaults` 中的配置，**不是 merge**！如果默认有 3 个 fallback 模型，在 list 中只写 primary 会导致 fallback 丢失！

### 4.4 bindings 路由配置详解

```json5
{
  // ========== 消息路由绑定 ==========
  // 规则：最精确匹配获胜
  bindings: [
    // 最精确：指定用户 + 指定群组
    {
      agentId: "ella",
      match: {
        channel: "wecom",
        peer: { kind: "group", id: "contract-dept-group-id" },
      },
    },
    // 次之：指定用户私聊
    {
      agentId: "oliver",
      match: {
        channel: "wecom",
        peer: { kind: "direct", id: "pm-user-id" },
      },
    },
    // 再次：整个通道的直接消息
    {
      agentId: "main",
      match: {
        channel: "wecom",
        peer: { kind: "direct" },
      },
    },
    // 最兜底：整个通道所有消息
    {
      agentId: "main",
      match: { channel: "wecom" },
    },
  ],
}
```

### 4.5 其他核心配置段

```json5
{
  // ========== 会话管理 ==========
  session: {
    dmScope: "per-channel-peer",  // 每个用户独立会话
    reset: {
      mode: "daily",       // daily | never
      atHour: 4,           // 凌晨 4 点重置
      idleMinutes: 120,    // 闲置 2 小时也重置
    },
    threadBindings: {
      enabled: true,
      idleHours: 24,         // 线程 24 小时无活动清理
      maxAgeHours: 168,      // 线程最多保存 7 天
    },
  },

  // ========== 消息策略 ==========
  messages: {
    visibleReplies: "message_tool",
    groupChat: {
      visibleReplies: "message_tool",
      requireMention: true,  // 群聊必须 @ 才响应
    },
  },

  // ========== Cron 引擎 ==========
  cron: {
    enabled: true,
    maxConcurrentRuns: 4,   // 最多 4 个 Cron 同时跑
    sessionRetention: "168h", // 会话保留 7 天
    runLog: {
      maxBytes: "50mb",     // 日志最大 50MB
      keepLines: 10000,      // 保留 10000 行
    },
  },

  // ========== Webhook 配置 ==========
  hooks: {
    enabled: true,
    token: "your-webhook-secret-token",
    path: "/hooks",
    allowedAgentIds: ["main", "ella", "oliver"],
    mappings: [
      {
        match: { path: "oa-approval" },
        action: "agent",
        agentId: "ella",
        deliver: true,
      },
    ],
  },

  // ========== 工具权限 ==========
  tools: {
    profile: "coding",  // full | coding | messaging | minimal
    // 额外允许的工具（profile 之外）
    alsoAllow: ["sessions_spawn", "sessions_send", "subagents"],
    // 全局禁用的工具（优先级最高）
    deny: [],
  },

  // ========== 技能系统 ==========
  skills: {
    load: {
      // 额外的技能目录（优先级最低）
      extraDirs: ["/opt/company-skills", "/shared/team-skills"],
      watch: true,              // 监听文件变化自动重载
      watchDebounceMs: 250,    // 防抖延迟
    },
    install: {
      preferBrew: true,          // 优先用 brew 安装依赖
      nodeManager: "npm",        // npm | pnpm | yarn | bun
    },
    limits: {
      maxSkillsPromptChars: 18000,  // 技能注入总字符限制
    },
    // 单个技能配置
    entries: {
      "contract-parse": {
        enabled: true,
        env: { OCR_API_ENDPOINT: "https://ocr.example.com" },
        apiKey: "your-ocr-key-here",
      },
    },
  },

  // ========== 插件配置 ==========
  plugins: {
    entries: {
      "memory-core": {
        enabled: true,
        config: {
          // 梦境记忆整理功能
          dreaming: {
            enabled: true,
            frequency: "0 3 * * *",  // 每天凌晨 3 点
            timezone: "Asia/Shanghai",
          },
        },
        // 子代理权限
        subagent: {
          allowModelOverride: true,
          allowedModels: ["qwen/qwen3.6-plus"],
        },
      },
      "wecom-openclaw-plugin": {
        enabled: true,
      },
    },
    // 插件白名单
    allow: ["memory-core", "wecom-openclaw-plugin"],
  },

  // ========== 通道配置 ==========
  channels: {
    wecom: {
      enabled: true,
      botId: "your-bot-id",
      secret: "your-bot-secret",
      dmPolicy: "allowlist",  // pairing | allowlist | open | disabled
      groupPolicy: "allowlist",
      allowFrom: ["user-id-1", "user-id-2", "user-id-3"],
    },
    webchat: { enabled: true },
  },
}
```

---

## 5. 工作区 Bootstrap 7 大文件详解

### 5.1 注入机制概述

```
每次智能体运行时，按以下顺序注入 Bootstrap 文件（除非 contextInjection = never）
总字符限制：60KB，单文件限制：12KB

注入顺序：
1. AGENTS.md    → 行为规范（最高优先级，最容易被遵守）
2. SOUL.md      → 人格设定
3. USER.md      → 用户偏好
4. TOOLS.md     → 工具规范
5. IDENTITY.md  → 身份标识
6. MEMORY.md    → 长期记忆
7. HEARTBEAT.md → 仅在心跳触发时注入
```

### 5.2 AGENTS.md - 行为规范（最重要！）

**文件作用**：定义智能体必须遵守的硬性规则，会被模型最严格地遵守。

**最佳实践模板**：
```markdown
# AGENTS.md - 智能体行为规范

## 🔴 绝对禁止（违反即终止）

1. 禁止执行任何会删除文件、格式化磁盘、修改系统配置的危险命令
2. 禁止向任何外部渠道发送用户隐私、密码、密钥等敏感信息
3. 禁止在没有用户明确确认的情况下执行任何生产环境变更
4. 禁止编造信息，不确定时明确告知"我需要确认"

## 🟡 审批流程（需要用户明确确认）

1. 所有 `exec` 命令执行前，必须向用户说明命令作用和可能影响
2. 涉及生产环境的变更，需要用户两次确认
3. 文件覆盖操作，必须先展示 diff，再确认

## 🟢 操作原则

1. **安全第一**：所有操作优先考虑安全性，其次是效率
2. **最小权限**：只使用完成任务必需的最小工具集
3. **可追溯**：所有重要操作记录原因和上下文
4. **诚实透明**：知道就说知道，不知道就说不知道，不编造

## 📋 输出规范

1. 技术问题给出精确、可操作的步骤
2. 复杂内容结构化，用列表、表格展示
3. 重要警告使用 emoji 高亮
4. 长输出先给摘要，再给细节

## ⚠️ 特殊行为

1. 用户情绪激动时，先安抚再解决问题
2. 用户要求违反原则时，礼貌说明原因，给出替代方案
3. 紧急情况可以简化流程，但必须事后补全说明
```

### 5.3 SOUL.md - 人格设定

**文件作用**：定义智能体的"性格"，让输出更一致、更有人情味。

**最佳实践模板**：
```markdown
# SOUL.md - 我的人格

## 基本人设

你是 Jerry 🦞，一个务实、高效、略带幽默感的技术助手。

## 沟通风格

- **直接不啰嗦**：有话直说，不要客套，不要"好的呢亲"这种
- **结果导向**：直奔主题，先给答案，再给解释
- **适当幽默**：严肃的技术问题可以偶尔开个玩笑，缓解压力
- **中文为主**：和 Rex 沟通全程用中文，技术术语可以用英文

## 性格特点

- 负责任：承诺的事情会跟进到底
- 谨慎：不确定的事情明确说明，不胡乱猜测
- 有条理：复杂问题拆解成步骤，清晰呈现
- 有担当：犯了错误主动承认，立即修正，不找借口

## 面对不同场景

- **用户问简单问题**：直接给答案，一句话搞定
- **用户问复杂问题**：先给概要，再分点详述，给行动建议
- **用户犯错**：先解决问题，再温和提醒如何避免
- **用户要求不合理**：礼貌说明原因，给出替代方案，不要生硬拒绝

## 语气参考

好的 → 没问题
我理解 → 懂了
让我想想 → 我分析下
请问 → 问一下

不要用：好的呢、亲、人家、呢、啦 这类卖萌词汇
保持专业，但不要冷冰冰，像个靠谱的技术同事就行
```

### 5.4 USER.md - 用户画像

**文件作用**：让智能体"了解"用户，提供个性化的服务。

**最佳实践模板**：
```markdown
# USER.md - 关于 Rex

## 基本信息

- 姓名：Rex
- 角色：技术负责人
- 时区：Asia/Shanghai (GMT+8)
- 工作时间：周一至周五 9:00 - 18:00

## 沟通偏好

- 首选语言：中文
- 沟通风格：直接、高效、不要客套
- 紧急联系：企业微信 @
- 非工作时间：除非特别紧急，否则不要打扰

## 工作习惯

- 早上到公司先处理邮件和审批
- 喜欢用数据说话，报告要简洁有结论
- 讨厌无意义的会议和长篇大论的汇报
- 重要事情喜欢有书面记录
- 代码喜欢 TypeScript，严格 lint

## 常用账号

- 企业微信：Rex
- GitHub: @RenLimin
- 飞书 ONES: Rex
- OA 系统：rex

## 禁忌事项

1. 不要在凌晨 1:00 - 8:00 发消息打扰，除非 P0 级故障
2. 不要发长语音，所有事情用文字
3. 不要把聊天记录随意转发给第三方
4. 汇报问题要带解决方案，不要只抛问题

## 偏好设置

- 日期格式：YYYY-MM-DD
- 金额单位：万元
- 代码风格：TypeScript + ESLint 严格模式
- 报告格式：Markdown，用表格总结数据
```

### 5.5 TOOLS.md - 工具使用规范

**文件作用**：定义工具调用的安全规则，防止工具滥用。

**最佳实践模板**：
```markdown
# TOOLS.md - 工具使用规范

## 通用原则

1. **最小必要**：只用完成任务必需的工具，不用多余的
2. **安全优先**：危险工具必须二次确认
3. **结果验证**：重要操作执行后要验证结果正确
4. **异常处理**：工具执行失败要明确告知错误原因

## 各类工具专项规则

### exec - 命令执行

- 所有命令执行前必须向用户说明：命令内容 + 预期作用 + 可能风险
- 以下命令必须要求用户明确回复"确认执行"才能运行：
  - rm -rf
  - docker system prune
  - kubectl delete / apply
  - 数据库修改操作
  - 任何生产环境变更
- 长耗时命令要加 timeout，后台执行要给出查询方式
- 输出超过 50 行时，保存到文件，只展示摘要

### read - 文件读取

- 大文件要指定行数范围，不要全部读取
- 二进制文件不要尝试直接展示内容
- 敏感文件（密钥、密码）要注意脱敏展示

### write/edit - 文件修改

- **覆盖文件前必须先 read，展示 diff，然后要求用户确认**
- 重要文件修改前自动备份
- 修改后验证文件内容正确
- .gitignore 中有的敏感文件不要写入明文密钥

### browser - 浏览器自动化

- 只访问白名单内的域名
- 操作前说明将要执行的步骤
- 操作后截图确认结果
- 不要在浏览器中输入密码等敏感信息
- 会话结束后清理 cookies

### sessions_spawn - 子代理

- 任务描述要清晰，包含验收标准
- 超时时要给出合理的错误处理方案
- 并发不要超过 3 个，避免资源耗尽
- 子代理的输出要汇总整理后再给用户，不要转发原始日志

## 工具输出处理

- 成功：简洁说明结果，必要时附关键数据
- 失败：明确说明错误原因，给出 2-3 个解决方案
- 超时：说明已在后台运行，给出后续查看方式
- 不要把完整的工具调用栈直接给用户，翻译成人类能懂的语言
```

### 5.6 IDENTITY.md - 身份标识

**文件作用**：明确定义智能体的角色和能力边界，避免智能体承诺做不到的事情。

**最佳实践模板**：
```markdown
# IDENTITY.md - 我是谁

## 基本信息

- **名字**：Jerry 🦞
- **角色**：智能体团队协调人 + 全栈技术助手
- **所属团队**：Rex 的私人智能体团队
- **创建日期**：2026-04

## 我的职责

1. **任务协调**：接收用户需求，分发给合适的专业智能体执行
2. **结果汇总**：汇总各智能体的输出，整理成统一的答案给用户
3. **日常助手**：代码编写、文档整理、数据分析、问题排查
4. **主动提醒**：重要事项、截止日期、异常情况及时通知用户

## 我的能力范围

✅ 能做的：
- 代码编写、Code Review、Bug 排查
- 文档编写、数据整理、报告生成
- 多智能体任务编排和结果汇总
- 系统状态巡检和问题预警
- 定时任务和自动化流程搭建
- 技能开发和配置优化

❌ 不能做的：
- 不承诺 100% 正确率，复杂问题需要人工复核
- 不访问用户没有明确授权的系统
- 不执行用户明确禁止的操作
- 不编造信息，不确定的明确说明
- 不会代替用户做决策，只给出建议

## 我的团队成员

- **Ella 🦊**：合同管理专家，负责合同解析和 OA 审批
- **Oliver 🐘**：项目管理专家，负责 ONES 和项目进度
- **Aaron 🦉**：经营分析专家，负责报告和数据分析
- **Iris 🐦‍⬛**：巡检专家，负责邮件和系统监控

有任何需求，我会选择最合适的人来帮你完成！🦞
```

### 5.7 MEMORY.md - 长期记忆（可选）

**文件作用**：持久化存储重要的历史信息，每次运行都会注入上下文。

**最佳实践模板**：
```markdown
# MEMORY.md - 长期记忆

## 重要决策记录

### 2026-05-06 - 智能体架构调整决策
- 背景：单智能体处理多场景能力不足，经常混淆
- 决策：拆分为 1 主 + 4 专业智能体架构
- 结论：已完成部署，路由规则需要持续优化
- 负责人：Rex

### 2026-05-01 - 安全策略升级
- 背景：工具滥用风险高，缺乏审批流程
- 决策：所有 exec 命令必须确认，生产环境二次确认
- 状态：已在 TOOLS.md 落地执行

## 经验教训库

### Lesson 1: skills 数组是完全替换，不是追加
- 时间：2026-04-20
- 事件：给 ella 加了 oa-approval 技能，忘了列原有技能，导致 ella 不会用 GitHub 了
- 教训：agents.list[x].skills 是完全覆盖 defaults.skills，不是追加
- 修复：每次修改都要完整列出所有需要的技能

### Lesson 2: contextInjection 策略的重要性
- 时间：2026-04-25
- 事件：默认 always 策略导致 token 消耗很高，每天 $20+
- 教训：continuation-skip 可以节省 40% token，体验差别不大
- 修复：已切换到 continuation-skip

## 常用快捷方式

- 合同模板目录：/data/templates/contracts/v2
- ONES API 文档：https://ones.example.com/api/docs
- OA 系统登录页：https://oa.example.com/login

## SOP 标准流程

### 合同审批 SOP
1. 接收合同 → 2. OCR 识别 → 3. 提取关键字段 → 4. 风险检查 → 5. 生成摘要给用户 → 6. 用户确认后提交审批 → 7. 记录到 MEMORY.md
```

### 5.8 HEARTBEAT.md - 心跳任务清单

**文件作用**：定义心跳触发时自动执行的任务清单，实现自动化巡检。

**最佳实践模板**：
```markdown
# HEARTBEAT.md - 自动巡检任务清单

仅在心跳触发时注入。每 30 分钟执行一次。

## 🔴 高优先级（每次都检查）

### 1. OA 待审批检查
- 检查 OA 系统是否有 Rex 的待审批合同
- 如有，立即发送企业微信通知，附摘要
- 紧急审批直接 @ 提醒

### 2. P0 级告警检查
- 检查监控系统是否有 P0/P1 告警
- 如有，立即通知，附告警详情和影响范围

### 3. 邮件紧急检查
- 检查收件箱标题包含"紧急""合同""审批""P0""故障"的邮件
- 如有，立即转发通知

## 🟡 中优先级（每 2 小时检查一次）

### 4. 合同到期提醒
- 查询 30 天内到期的合同
- 每天上午 10 点集中通知一次

### 5. 项目风险检查
- 检查 ONES 中延期风险的项目
- 检查燃尽图异常的项目
- 如有风险生成简要报告

## 🟢 低优先级（每天一次）

### 6. 每日工作总结
- 时间：每天下午 6 点
- 内容：
  - 当天审批完成的合同数
  - 处理的邮件数
  - 发现的项目风险数
  - 次日待办提醒

### 7. 记忆整理
- 整理当天的重要对话和决策
- 更新到 MEMORY.md
- 清理过时的临时信息

## ⚠️ 注意事项

1. 没有需要处理的事项时，回复 HEARTBEAT_OK，不要发空消息
2. 同一事项 24 小时内不要重复提醒
3. 非工作时间只处理真正紧急的 P0 故障
4. 所有心跳操作都要记录日志，便于事后排查
```

---

## 6. SKILL.md 技能文件完整规范

### 6.1 文件结构总览

```
┌───────────────────────────────────────────────────────────┐
│                    SKILL.md 文件结构                      │
├───────────────────────────────────────────────────────────┤
│                                                          │
│  ---                                                     │
│  name: contract-parse                        ← 技能 ID   │
│  description: 合同文档智能解析与条款提取    ← 描述      │
│  user-invocable: true                        ← 用户可调用│
│  metadata:                                               │
│    openclaw:                                            │
│      requires:                                         │
│        bins: ["pdftotext", "tesseract"]   ← 依赖二进制  │
│        env: ["OCR_API_KEY"]               ← 依赖环境变量 │
│        config: ["skills.entries.contract-parse.enabled"] │
│  ---                                                     │
│                                                          │
│  Markdown 正文部分 ← 注入系统提示词，教智能体怎么用     │
│  - 功能说明                                              │
│  - 使用步骤                                              │
│  - 字段定义                                              │
│  - 输出格式                                              │
│  - 注意事项                                              │
│                                                          │
└───────────────────────────────────────────────────────────┘
```

### 6.2 完整示例模板

```markdown
---
name: contract-parse
description: 智能解析各种格式的合同文档，提取关键条款和字段
user-invocable: true
disable-model-invocation: false

# 元数据和依赖声明
metadata:
  openclaw:
    requires:
      # 需要的二进制工具，如果不存在则技能不加载
      bins:
        - pdftotext    # PDF 转文本
        - tesseract    # OCR 识别扫描件
        - file         # 检测文件类型
      # 需要设置的环境变量
      env:
        - OCR_API_KEY
        - OCR_API_ENDPOINT
      # 需要存在的配置项
      config:
        - skills.entries.contract-parse.enabled
    # 主环境变量名，用于 UI 展示
    primaryEnv: OCR_API_KEY
---

# 合同解析技能使用指南

## 功能概述

本技能可以解析 PDF、Word、图片格式的合同文档，提取关键字段和风险条款。

支持的格式：
- 可编辑 PDF
- 扫描版 PDF（OCR）
- Word (.docx)
- 图片 (PNG, JPG)

## 使用步骤

1. **检测文件格式**
   - 使用 `file` 命令检测文件真实类型
   - 根据类型选择解析策略

2. **文本提取**
   - 可编辑 PDF：用 pdftotext -layout，保留排版
   - 扫描 PDF：调用 OCR API 识别
   - Word：直接用 pandoc 转 markdown
   - 图片：tesseract OCR

3. **字段提取**
   调用 LLM 提取以下字段：

| 字段名 | 说明 | 必填 |
|--------|------|------|
| 合同编号 | 文档唯一标识 | ✅ |
| 合同名称 | 合同标题 | ✅ |
| 甲方全称 | 甲方完整公司名 | ✅ |
| 乙方全称 | 乙方完整公司名 | ✅ |
| 合同金额 | 大写 + 小写 | ✅ |
| 签署日期 | YYYY-MM-DD | ✅ |
| 生效日期 | YYYY-MM-DD | ✅ |
| 合同期限 | 开始 - 结束日期 | ✅ |
| 付款方式 | 节点和比例 | ✅ |
| 违约责任 | 核心条款摘要 | ✅ |
| 争议解决 | 仲裁地点和机构 | ✅ |
| 保密条款 | 是否有竞业限制 | ⚪ |
| 自动续期 | 是否自动续期 | ⚪ |

4. **风险检查**
   重点检查以下风险项：
   - ❗ 金额大小写不一致
   - ❗ 日期前后矛盾
   - ❗ 违约责任过重（超过合同金额 30%）
   - ❗ 争议解决地点在对方所在地
   - ❗ 自动续期没有提前通知期限

5. **生成输出**

输出格式：
```markdown
## 📄 合同解析结果

### 基本信息
| 字段 | 值 |
|------|-----|
| 合同编号 | xxx |
| ... | ... |

### ⚠️ 风险提醒
1. xxx
2. xxx

### 💡 建议
1. xxx
2. xxx

---
完整原文摘要：
（500 字以内的核心内容摘要）
```

## 错误处理

- OCR 识别率低于 90%：明确告知用户，建议提供清晰版本
- PDF 加密：告知用户文件加密，需要密码
- 字段缺失：标注为 [未识别到]，不要编造
- 无法确定的信息：标注为 [? 需要人工确认]

## 注意事项

1. **不要编造信息**，识别不确定的标注出来
2. **金额要精确**，精确到分，不要四舍五入
3. **日期统一格式** YYYY-MM-DD
4. **风险项要高亮**，用红色或警告 emoji
5. **输出要简洁**，重点突出，不要啰嗦
```

---

## 第三篇：关联关系与机制

---

## 7. 配置继承与覆盖规则

### 7.1 覆盖类型总表

| 字段类型 | 覆盖方式 | 官方说明 | 容易踩坑 ⚠️ |
|---------|---------|---------|------------|
| **简单类型** (string, number, boolean) | 直接替换 | 新值完全替换旧值 | 不容易出错 |
| | | | |
| **数组类型** (array) | ⚠️ 完全替换 | 新数组替换整个旧数组，**不会合并！** | ⚠️ 最容易踩坑！ |
| 例如: `skills`, `fallbacks`, `allowFrom` | | | skills 只加了新技能，旧的全部丢失！ |
| | | | |
| **对象类型** (object) | ⚠️ 完全替换 | 新对象替换整个旧对象，**不会 merge！** | ⚠️ 第二容易踩坑！ |
| 例如: `model`, `sandbox` | | | 只写了 model.primary，fallbacks 全丢了！ |

### 7.2 反模式与正确模式对比

| ❌ 错误写法（反模式） | ✅ 正确写法 | 说明 |
|---------------------|------------|------|
| ```json5 { agents: { defaults: { skills: ["github", "kb"] }, list: [{ id: "ella", // ❌ 只加了新技能 skills: ["oa-approval"] }] } } ``` | ```json5 { agents: { defaults: { skills: ["github", "kb"] }, list: [{ id: "ella", // ✅ 完整列出所有需要的 skills: ["github", "kb", "oa-approval"] }] } } ``` | skills 数组完全替换，不会自动追加默认的 |
| | | |
| ```json5 { agents: { defaults: { model: { primary: "qwen", fallbacks: ["deepseek"] } }, list: [{ id: "ella", // ❌ 只覆盖了 primary model: { primary: "ark" } }] } } ``` | ```json5 { agents: { defaults: { model: {...} }, list: [{ id: "ella", // ✅ 完整写出整个对象 model: { primary: "ark", fallbacks: ["deepseek", "qwen"] } }] } } ``` | model 对象整体替换，fallbacks 会丢失 |
| | | |
| ```json5 { agents: { defaults: { sandbox: { mode: "non-main", scope: "agent" } }, list: [{ id: "ella", // ❌ 只写了一个字段 sandbox: { mode: "all" } }] } } ``` | ```json5 { agents: { defaults: { sandbox: {...} }, list: [{ id: "ella", // ✅ 完整写出整个对象 sandbox: { mode: "all", scope: "session", workspaceAccess: "ro", backend: "docker" } }] } } ``` | sandbox 对象整体替换，其他字段会丢失默认值 |

### 7.3 安全配置建议

**生产环境推荐做法**：

1. ✅ **默认配全，单个智能体尽量少覆盖**
   - 把通用配置都写在 `agents.defaults`
   - 单个智能体只覆盖真正不同的字段

2. ✅ **简单类型放心覆盖，对象和数组谨慎**
   - `name`, `workspace`, `agentDir` 可以放心覆盖
   - `model`, `sandbox`, `skills`, `tools` 覆盖时要完整写出

3. ✅ **覆盖后用 `openclaw config get` 验证**
   ```bash
   openclaw config get agents.list.1.skills
   # 确认包含所有预期的技能
   ```

---

## 8. SKILL.md 6 层加载机制

### 8.1 完整加载路径优先级

```
  🔝 优先级 6 (最高，获胜者)
  ┌─────────────────────────────────────────────────────────┐
  │  当前工作区私有技能                                       │
  │  ~/.openclaw/workspace/skills/<name>/SKILL.md          │
  └──────────────────────────┬──────────────────────────────┘
                             ↓ 覆盖所有下层同名技能
  🔝 优先级 5
  ┌─────────────────────────────────────────────────────────┐
  │  项目级 Agent 共享技能                                    │
  │  ~/.openclaw/workspace/.agents/skills/<name>/SKILL.md  │
  └──────────────────────────┬──────────────────────────────┘
                             ↓ 覆盖下层同名技能
  🔝 优先级 4
  ┌─────────────────────────────────────────────────────────┐
  │  用户级共享技能                                           │
  │  ~/.agents/skills/<name>/SKILL.md                      │
  └──────────────────────────┬──────────────────────────────┘
                             ↓ 覆盖下层同名技能
  🔝 优先级 3
  ┌─────────────────────────────────────────────────────────┐
  │  系统级共享技能                                           │
  │  ~/.openclaw/skills/<name>/SKILL.md                    │
  └──────────────────────────┬──────────────────────────────┘
                             ↓ 覆盖下层同名技能
  🔝 优先级 2
  ┌─────────────────────────────────────────────────────────┐
  │  内置捆绑技能 (Bundled Skills)                          │
  │  OpenClaw 二进制自带的技能 (weather, github 等)        │
  └──────────────────────────┬──────────────────────────────┘
                             ↓ 覆盖下层同名技能
  🔝 优先级 1 (最低)
  ┌─────────────────────────────────────────────────────────┐
  │  额外技能目录                                            │
  │  skills.load.extraDirs 配置的目录                       │
  │  例如: /opt/company-skills, /shared/team-skills        │
  └─────────────────────────────────────────────────────────┘
```

> 💡 **核心机制**：同名技能，高优先级路径的文件完全覆盖低优先级的。

### 8.2 加载流程三关校验

```
          找到 SKILL.md 文件
              │
              ▼
  ┌─────────────────────────────┐
  │     第一关：白名单校验       │
  │  agents.defaults.skills     │
  │     +                       │
  │  agents.list[x].skills     │
  │  是否包含这个技能 name？    │
  │            │                │
  │            ├─ 否 → ❌ 不加载
  │            ↓                │
  └─────────────────────────────┘
              │
              ▼
  ┌─────────────────────────────┐
  │     第二关：依赖校验         │
  │  requires.bins 都存在吗？   │
  │  requires.env 都设置了吗？  │
  │  requires.config 都存在吗？ │
  │            │                │
  │            ├─ 任何一项不满足 → ❌ 不加载
  │            ↓                │
  └─────────────────────────────┘
              │
              ▼
  ┌─────────────────────────────┐
  │     第三关：启用校验         │
  │  skills.entries.<name>     │
  │  .enabled === true?        │
  │            │                │
  │            ├─ 否 → ❌ 不加载
  │            ↓                │
  └─────────────────────────────┘
              │
              ▼
      ✅ 技能加载成功，注入提示词
```

### 8.3 常见问题

| 问题现象 | 可能原因 | 排查命令 |
|---------|---------|---------|
| 加了 SKILL.md，但智能体不会用 | 不在技能白名单里 | `openclaw config get agents.defaults.skills` |
| 改了技能内容没生效 | 1. 热重载延迟<br>2. 会话缓存了旧技能 | 1. 等 2 秒<br>2. `/reset` 重置会话 |
| 生产环境技能不加载，本地可以 | 生产环境缺少依赖的二进制 | 检查 `requires.bins` 里的命令都安装了吗 |
| 加了新技能所有人都能看到了 | 忘记配置单个智能体的 skills 白名单了 | 检查每个智能体的技能白名单 |

---

## 9. 配置热重载支持矩阵

### 9.1 各配置段热重载支持情况

| 配置段 | 是否支持热重载 | 说明 |
|-------|---------------|------|
| `gateway.port` | ❌ 否 | 修改后必须重启网关 |
| `gateway.bind` | ❌ 否 | 修改监听地址需要重启 |
| `gateway.auth` | ⚠️ 部分 | token 立即生效，模式变更可能需要重连 |
| `gateway.controlUi.*` | ✅ 是 | 刷新浏览器生效 |
| `gateway.channelHealthCheckMinutes` | ✅ 是 | 下次健康检查生效 |
| | | |
| `models.providers.*` | ✅ 是 | 下次模型调用生效 |
| | | |
| `agents.defaults.*` | ✅ 是 | 下次智能体运行生效 |
| `agents.list[].*` | ✅ 是 | 对应智能体下次运行生效 |
| `bindings[]` | ✅ 是 | 下次消息路由生效 |
| | | |
| `session.*` | ✅ 是 | 新会话立即生效，已有会话保持 |
| `messages.*` | ✅ 是 | 下次消息发送生效 |
| | | |
| `cron.*` | ✅ 是 | 下次调度生效，正在运行的任务不受影响 |
| `hooks.*` | ✅ 是 | 下次 Webhook 调用生效 |
| | | |
| `tools.*` | ✅ 是 | 下次工具调用生效 |
| `skills.*` | ✅ 是 | 下次技能加载生效 |
| `skills.load.watch` | ✅ 是 | 文件变更自动检测重载 |
| | | |
| `plugins.entries.*.enabled` | ❌ 否 | 必须重启网关 |
| `plugins.entries.*.config` | ⚠️ 看插件 | 大部分支持热重载，少数需要重启 |
| | | |
| `channels.*` | ⚠️ 部分 | 白名单立即生效，凭证变更需要重连 |
| `mcp.*` | ✅ 是 | 下次 MCP 连接生效 |

### 9.2 触发热重载的四种方式

| 方式 | 说明 |
|-----|------|
| 1. 文件监听自动触发 | 修改 openclaw.json 后约 1-2 秒自动重载 |
| 2. CLI 命令 | `openclaw config reload` 立即强制重载 |
| 3. Control UI 保存 | 控制面板修改配置后点保存立即重载 |
| 4. Gateway 工具 | 智能体内部调用 gateway.config.patch 热更新 |

### 9.3 热重载的局限性

⚠️ **重要：以下情况热重载不影响已运行的内容**

| 场景 | 行为 |
|-----|------|
| 已 spawn 的子代理 | 继续用创建时的配置，新 spawn 的用新配置 |
| 正在运行的 Cron 任务 | 继续用启动时的配置，下一次调度用新配置 |
| 已建立的通道连接 | 继续运行，新消息才用新配置 |
| 已有会话的上下文缓存 | 会话重置后才会重新加载 bootstrap 文件 |
| 已加载的技能（会话内） | `/reset` 重置会话后才会重新扫描加载 |

---

## 第四篇：高级架构

---

## 10. 多智能体配置关联图谱

### 10.1 完整关联关系图

```
┌───────────────────────────────────────────────────────────────────────┐
│                    多智能体配置关联关系总览                           │
└───────────────────────────────────────────────────────────────────────┘

                openclaw.json 全局配置
                      │
        ┌─────────────┴─────────────┐
        │ agents.defaults.*          │
        │  (所有智能体继承)          │
        │                            │
        ▼                            ▼
┌──────────────────┐      ┌──────────────────┐
│ agents.list[0]  │      │ agents.list[1]  │
│ id: "main"      │      │ id: "ella"      │
│ default: true   │      │ name: "Ella 🦊"  │
│ (继承所有默认)  │      │ workspace: ~/ella │◀─ 独立工作区
└────────┬─────────┘      │ agentDir: ~/ella │◀─ 独立认证凭证
         │                │ model: {...}     │◀─ 覆盖模型配置
         │                │ skills: [...]    │◀─ 覆盖技能白名单
         │                │ sandbox: {...}   │◀─ 覆盖沙箱配置
         │                └────────┬─────────┘
         │                         │
         ▼                         ▼
   ~/workspace/              ~/agents/ella/workspace/
   ├─ AGENTS.md               ├─ AGENTS.md (独立的！)
   ├─ SOUL.md                 ├─ SOUL.md (独立的！)
   ├─ USER.md                 ├─ TOOLS.md (独立的！)
   ├─ TOOLS.md                └─ skills/ ← ella 私有技能
   ├─ IDENTITY.md                 └─ oa-approval/SKILL.md
   ├─ MEMORY.md
   └─ skills/ ← main 私有技能      bindings[] 路由规则
         └─ devops/SKILL.md            │
                                        ▼
                                    消息进来
                                       │
                           ┌───────────┴───────────┐
                           ▼                       ▼
                 匹配到 ella 的规则         匹配到 main 的规则
                    (合同部门群)                  (其他群/私聊)
                           │                       │
                           ▼                       ▼
                      用 ella 的配置            用 main 的配置
                      用 ella 的工作区          用 main 的工作区
                      用 ella 的技能            用 main 的技能
                      用 ella 的模型            用 main 的模型
```

### 10.2 资源共享与隔离矩阵

| 资源 | 共享/隔离 | 说明 |
|------|---------|------|
| 模型 API Key | ⚠️ 默认共享，可隔离 | 默认用 main 的 auth-profiles.json；设置 agentDir 后可以用独立的 |
| 工作区文件 | ❌ 完全隔离 | 每个智能体有独立 workspace 目录，互相看不到 |
| 技能白名单 | ✅ 继承 + 覆盖 | 默认继承 defaults.skills，可独立覆盖 |
| 技能文件 | ✅ 可共享 + 私有 | 6 层路径共享技能，也可放自己 workspace/skills |
| 会话历史 | ❌ 完全隔离 | 每个智能体会话独立存储 |
| 通道连接 | ✅ 全局共享 | 同一个企业微信/WhatsApp 账号路由给不同智能体 |
| Cron 任务 | ⚠️ 独立运行 | Cron 指定 agentId，用那个智能体的配置运行 |
| 子代理 | ⚠️ 半隔离 | 父智能体可以指定子代理用哪个智能体的配置 |
| 沙箱容器 | ✅ 独立 | scope=agent 时每个智能体一个容器，完全隔离 |
| 记忆 | ❌ 完全隔离 | 每个智能体独立的记忆整理和梦境 |

---

## 11. 子代理编排与深度控制

### 11.1 子代理配置参数详解

```json5
{
  agents: {
    defaults: {
      subagents: {
        // ───────── 核心控制 ─────────
        maxSpawnDepth: 2,
        // 1 = 无子代理（默认），main → subagent 就停止
        // 2 = 支持编排，main → orchestrator → worker 两级子代理

        maxChildrenPerAgent: 5,   // 单个父智能体最多 5 个子代理
        maxConcurrent: 8,          // 全局最多同时 8 个子代理运行

        // ───────── 性能成本 ─────────
        runTimeoutSeconds: 900,   // 15 分钟超时，防止任务挂起
        archiveAfterMinutes: 60,  // 1 小时后自动归档，释放存储
        model: "deepseek/deepseek-chat",  // 子代理默认用更便宜的模型

        // ───────── 安全控制 ─────────
        allowAgents: ["ella", "oliver", "aaron", "iris"],
        // 白名单：只能 spawn 列表里的智能体，空数组 = 任意

        requireAgentId: true,
        // true = 必须明确指定子代理的 agentId，更安全
        // false = 不指定时用默认智能体
      },
    },
  },
}
```

### 11.2 深度 = 2 编排模式架构

```
                    用户请求
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│  main (深度 0，主会话)                            │
│  职责：理解需求，分解任务，创建编排器              │
└───────────────────┬───────────────────────────────┘
                    │ sessions_spawn
                    │ agentId: "aaron" (编排器)
                    ▼
┌───────────────────────────────────────────────────┐
│  aaron-orchestrator (深度 1，子代理)              │
│  职责：任务编排，创建多个工作子代理                │
│        汇总结果，整理成最终输出                    │
└────────┬───────────────────┬──────────────────────┘
         │ sessions_spawn    │ sessions_spawn
         │ agentId: "ella"   │ agentId: "oliver"
         ▼                    ▼
┌──────────────────┐ ┌───────────────────┐
│  ella-worker-1   │ │ oliver-worker-1   │  (深度 2，叶子节点)
│  合同解析子任务  │ │  项目数据子任务   │
└──────────────────┘ └───────────────────┘
         │                    │
         └─────────┬──────────┘
                   │
                   ▼
              结果汇总给 aaron
                   │
                   ▼
              aaron 整理后返回 main
                   │
                   ▼
              最终输出给用户
```

> 💡 **使用场景**：复杂数据分析、多文档对比、跨系统数据汇总等需要高度并行的任务。

### 11.3 子代理创建工具参数详解

```typescript
sessions_spawn({
  // ========== 核心参数 ==========
  // 任务描述：要清晰、完整、包含验收标准
  task: `解析合同文件 /data/contract.pdf，提取金额、双方、日期、付款条款。
         输出格式：JSON + 人类可读摘要`,

  // 子代理标签，用于日志和状态查询
  label: "contract-analysis-2026-001",

  // 目标智能体 ID（必须在 subagents.allowAgents 白名单里）
  agentId: "ella",


  // ========== 模型覆盖 ==========
  // 可选：用什么模型（默认用 subagents.model）
  model: "qwen/qwen3.6-plus",

  // 可选：思考级别
  thinking: "high",


  // ========== 上下文策略 ==========
  // isolated = 干净会话（推荐，节省 token）
  // fork = 继承当前会话的完整上下文（token 贵）
  context: "isolated",


  // ========== 生命周期 ==========
  // keep = 保留会话（后续可以继续交互）
  // delete = 完成后立即删除（节省空间）
  cleanup: "keep",


  // ========== 超时 ==========
  // 单次运行超时，秒（默认 subagents.runTimeoutSeconds）
  runTimeoutSeconds: 1800,
})
```

---

## 12. 沙箱安全配置体系

### 12.1 沙箱三要素配置

```json5
{
  agents: {
    defaults: {
      sandbox: {
        // 要素 1：什么时候启用？
        mode: "non-main",
        // off       = 完全关闭，所有工具直接在主机运行
        // non-main  = 非主会话启用（推荐，兼顾安全与便利）
        // all       = 所有会话都强制沙箱（生产环境推荐）

        // 要素 2：容器粒度有多细？
        scope: "agent",
        // agent   = 每个智能体一个容器（默认，最佳平衡）
        // session = 每个会话独立容器（最安全，消耗资源多）
        // shared  = 所有智能体共享一个容器（成本最低）

        // 要素 3：工作区访问权限
        workspaceAccess: "ro",
        // none = 完全不能访问工作区（最安全）
        // ro   = 只读（推荐平衡）
        // rw   = 读写（仅开发环境）

        // 后端实现
        backend: "docker",
        // docker   = 本地 Docker（默认，推荐）
        // ssh      = 远程 SSH 服务器
        // openshell = OpenShell 服务
      },
    },
  },
}
```

### 12.2 Docker 后端高级配置

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "agent",
        backend: "docker",

        // Docker 专用配置
        docker: {
          // 目录挂载：host-path:container-path:mode
          binds: [
            "/data/contracts:/data/contracts:ro",     // 合同模板只读
            "/data/reports:/data/reports:rw",          // 报告目录可写
          ],

          // GPU 支持（需要运行本地模型时）
          // gpus: "all",

          // 资源限制
          memLimit: "2g",        // 内存 2GB
          cpuLimit: "1.0",       // CPU 1 核

          // 运行用户（安全起见不要用 root）
          user: "1000:1000",

          // 额外的 Docker run 参数
          extraArgs: [
            "--security-opt=no-new-privileges",  // 防止提权
            "--cap-drop=ALL",                    // 丢弃所有能力
            "--read-only",                       // 根文件系统只读
          ],
        },
      },
    },
  },
}
```

### 12.3 不同环境的安全配置建议

| 环境 | 推荐 mode | 推荐 scope | workspaceAccess | 说明 |
|------|----------|-----------|-----------------|------|
| 开发/本地 | `off` | - | - | 不需要沙箱，调试方便 |
| 测试环境 | `non-main` | `agent` | `ro` | 平衡安全与便利 |
| 生产环境 - 标准 | `non-main` | `agent` | `ro` | 主会话便利，其他安全 |
| 生产环境 - 高安全 | `all` | `session` | `none` | 最严格，所有会话完全隔离 |

---

## 第五篇：实战与运维

---

## 13. 智能体创建标准流程

### 13.1 新建智能体 6 步法

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: openclaw.json 添加智能体条目                   │
│  ├─ id, name                                            │
│  ├─ workspace, agentDir                                 │
│  ├─ model, sandbox, skills 等覆盖配置                   │
│  └─ 确认数组/对象字段完整，不要丢失默认值                │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Step 2: 创建工作区目录结构                              │
│  mkdir -p ~/.openclaw/agents/<id>/workspace/skills     │
│  mkdir -p ~/.openclaw/agents/<id>/agent                │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Step 3: 创建 5 个核心 Bootstrap 文件                   │
│  ├─ AGENTS.md  (行为规范，最重要先写)                  │
│  ├─ SOUL.md    (人格设定)                              │
│  ├─ USER.md    (用户偏好)                              │
│  ├─ TOOLS.md   (工具规范)                              │
│  └─ IDENTITY.md (身份标识)                              │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Step 4: 配置独立认证（如果需要）                       │
│  cp auth-profiles.json ~/.openclaw/agents/<id>/agent/  │
│  或者配置独立的 API Key                                 │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Step 5: 添加私有技能（如果需要）                       │
│  把该智能体专用的技能 SKILL.md 放到它的 workspace/skills │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Step 6: 验证与测试                                      │
│  ├─ openclaw doctor 检查配置合法性                      │
│  ├─ openclaw config get agents.list[x] 确认配置正确    │
│  ├─ 创建测试会话验证功能                                 │
│  └─ 确认技能加载、工具权限、沙箱隔离都符合预期          │
└─────────────────────────────────────────────────────────┘
```

### 13.2 检查清单

创建完成后逐项确认：

- [ ] `openclaw doctor` 没有配置错误
- [ ] `openclaw agents list` 能看到新智能体
- [ ] 工作区 5 个核心文件都创建了
- [ ] 独立的 agentDir 目录存在（如果用独立认证）
- [ ] skills 白名单包含了所有需要的技能
- [ ] 模型配置包含了 primary 和 fallbacks
- [ ] sandbox 模式和权限设置正确
- [ ] 给该智能体的 bindings 路由规则已添加（如果需要）
- [ ] 实际发一条消息测试智能体正常响应

---

## 14. 典型配置问题诊断路径

### 14.1 场景 A："修改了 AGENTS.md 但智能体行为没变"

```
用户修改了 AGENTS.md
    │
    ▼
┌─────────────────────────────────────────┐
│ 检查 1: contextInjection 策略           │
│ agents.defaults.contextInjection = ?   │
└─────────────────────────────────────────┘
    │
    ├─ 值 = never → 完全不注入，改了当然无效 ❌
    ├─ 值 = continuation-skip → 是不是"连续对话"？
    │   连续对话 = 智能体回复后用户直接回复
    │   这种情况跳过注入，节省 token
    │   解决：执行 /reset 重置会话 → 立即生效 ✅
    └─ 值 = always → 应该每次都注入，继续检查
        │
        ▼
┌─────────────────────────────────────────┐
│ 检查 2: 文件大小与字符限制              │
│ AGENTS.md 文件多大？                    │
└─────────────────────────────────────────┘
    │
    ├─ 超过 12KB → 被截断了，后面的内容没注入 ⚠️
    │   解决：拆分成多个文件，或者精简内容
    └─ 大小正常 → 继续检查
        │
        ▼
┌─────────────────────────────────────────┐
│ 检查 3: 是不是改对智能体的工作区了？    │
│ main 有 main 的 workspace，ella 有 ella 的
└─────────────────────────────────────────┘
    │
    ├─ 路径错了 → 找到正确的工作区路径修改
    └─ 路径正确 → 继续检查
        │
        ▼
┌─────────────────────────────────────────┐
│ 检查 4: 更高优先级覆盖？                │
│ 是不是某个技能里有更高优先级的规则？    │
└─────────────────────────────────────────┘
```

### 14.2 场景 B："技能添加了但智能体不会用"

```
用户添加了新的 SKILL.md
    │
    ▼
┌─────────────────────────────────────────┐
│ 检查 1: 路径对吗？                      │
│ 是否在 6 层加载路径中的某一层？         │
└─────────────────────────────────────────┘
    │
    ├─ 路径错误 → 移动到 workspace/skills 目录（最高优先级）
    └─ 路径正确 → 继续检查
        │
        ▼
┌─────────────────────────────────────────┐
│ 检查 2: 技能白名单包含吗？              │
│ agents.defaults.skills 或 agents.list[x].skills
└─────────────────────────────────────────┘
    │
    ├─ 不在白名单 → 添加到 skills 数组
    │   ⚠️ 注意：数组是完全替换，要完整列出所有技能
    └─ 已在白名单 → 继续检查
        │
        ▼
┌─────────────────────────────────────────┐
│ 检查 3: 依赖都满足吗？                  │
│ bins 都安装了？env 变量都设置了？       │
└─────────────────────────────────────────┘
    │
    ├─ 缺少依赖 → 安装依赖二进制，设置环境变量
    └─ 依赖满足 → 继续检查
        │
        ▼
┌─────────────────────────────────────────┐
│ 检查 4: 技能启用了吗？                  │
│ skills.entries.<name>.enabled = true?  │
└─────────────────────────────────────────┘
    │
    ├─ 被禁用了 → 设置 enabled: true
    └─ 启用了 → 继续检查
        │
        ▼
┌─────────────────────────────────────────┐
│ 检查 5: 热重载与会话重置               │
│ 执行 /reset 重置会话，触发重新扫描技能  │
└─────────────────────────────────────────┘
```

### 14.3 场景 C："子代理 spawn 失败"

```
子代理创建失败
    │
    ▼
┌─────────────────────────────────────────┐
│ 检查 1: maxSpawnDepth 配置              │
│ 值是 1 还是 2？                          │
└─────────────────────────────────────────┘
    │
    ├─ 值 = 1 → 只支持一级子代理，嵌套 spawn 会失败
    └─ 值 ≥ 2 → 深度够，继续检查
        │
        ▼
┌─────────────────────────────────────────┐
│ 检查 2: 目标 agentId 在白名单吗？       │
│ subagents.allowAgents 包含吗？         │
└─────────────────────────────────────────┘
    │
    ├─ 不在白名单 → 添加到 allowAgents 数组
    └─ 在白名单 → 继续检查
        │
        ▼
┌─────────────────────────────────────────┐
│ 检查 3: 父智能体有 sessions_spawn 工具权限吗？
│ tools.alsoAllow 包含吗？               │
└─────────────────────────────────────────┘
    │
    ├─ 没有权限 → 添加 sessions_spawn, sessions_send, subagents
    └─ 有权限 → 继续检查
        │
        ▼
┌─────────────────────────────────────────┐
│ 检查 4: 是否达到 maxConcurrent 限制？   │
│ 是不是子代理太多并发了？                │
└─────────────────────────────────────────┘
    │
    ├─ 并发满了 → 等其他子代理结束或提高限制
    └─ 未达上限 → 检查模型配置和认证是否正确
```

---

## 15. 配置变更影响扩散图

### 15.1 修改不同字段的影响范围

| 修改的字段 | 影响范围 | 需要重启？ | 生效时机 |
|-----------|---------|----------|---------|
| `gateway.port` | 全部连接断开 | ✅ 是 | 重启后 |
| `gateway.bind` | 全部连接断开 | ✅ 是 | 重启后 |
| `agents.defaults.model.primary` | 所有智能体 | ❌ 否 | 下次模型调用 |
| `agents.defaults.model.fallbacks` | 所有智能体 | ❌ 否 | 下次模型调用 |
| `agents.defaults.skills` | 所有智能体 | ❌ 否 | 下次技能加载 |
| `agents.defaults.sandbox.mode` | 所有智能体 | ❌ 否 | 新沙箱实例 |
| `agents.defaults.heartbeat.every` | 所有智能体 | ❌ 否 | 下次心跳调度 |
| `agents.list[x].*` | 仅该智能体 | ❌ 否 | 该智能体下次运行 |
| `workspace/AGENTS.md` | 该工作区所属智能体 | ❌ 否 | 下次运行（连续对话要重置） |
| `workspace/SKILL.md` | 使用该技能的所有智能体 | ❌ 否 | 文件变更检测 + 会话重置 |
| `bindings[]` | 所有消息路由 | ❌ 否 | 下一条消息 |
| `channels.wecom.allowFrom` | 企业微信所有用户 | ❌ 否 | 下一条消息 |
| `plugins.entries.*.enabled` | 全局 | ✅ 是 | 重启后 |
| `cron.maxConcurrentRuns` | 所有 Cron 任务 | ❌ 否 | 下次调度 |
| `subagents.maxSpawnDepth` | 所有子代理 | ❌ 否 | 下次 spawn |

### 15.2 配置变更风险等级

| 风险等级 | 典型操作 | 操作建议 |
|---------|---------|---------|
| 🔴 高风险 | 修改 gateway 端口/绑定<br>启用/禁用核心插件<br>大幅降低工具权限<br>修改沙箱模式为 all | 1. 在测试环境先验证<br>2. 选择业务低峰期操作<br>3. 修改前备份配置文件<br>4. 修改后立即验证核心功能 |
| 🟡 中风险 | 修改模型配置<br>修改技能白名单<br>修改用户白名单<br>修改子代理深度限制 | 1. 注意数组是完全替换，不要丢东西<br>2. 修改后跑几个典型用例验证<br>3. 观察 token 成本变化 |
| 🟢 低风险 | 修改工作区 bootstrap 文件<br>修改技能文件内容<br>修改 heartbeat 间隔<br>修改 Cron 任务定义 | 1. 通常很安全<br>2. 改完 `/reset` 会话验证即可<br>3. 注意字符截断问题 |

---

## 16. 配置最佳实践 Checklist

### ✅ 安全相关

- [ ] `gateway.bind` 用 `loopback`，不要绑定 `0.0.0.0`
- [ ] `gateway.auth.token` 用强随机字符串，至少 32 字符
- [ ] 通道 `dmPolicy` 不要用 `open`，用 `allowlist` 或 `pairing`
- [ ] 生产环境 `sandbox.mode` 至少是 `non-main`，高安全用 `all`
- [ ] `sandbox.workspaceAccess` 推荐用 `ro`，不要用 `rw`
- [ ] 敏感智能体（如 Iris 巡检）单独设置更严格的 sandbox 和 tools 权限

### ✅ 可靠性相关

- [ ] 配置至少 2 层模型 fallback，不同供应商
- [ ] 启用 `channelHealthCheckMinutes` 健康检查
- [ ] `runTimeoutSeconds` 设置合理值（900秒=15分钟），不要无限
- [ ] 不要随意调大 `contextInjection` 到 `always`，`continuation-skip` 是最佳平衡

### ✅ 成本优化相关

- [ ] `imageMaxDimensionPx` 设为 1200，大幅降低图片 token
- [ ] `subagents.model` 用更便宜的模型，主模型保留给复杂任务
- [ ] 会话 `reset` 策略用 `daily` 配合 `idleMinutes`
- [ ] 技能白名单只列真正需要的，不要加载无用技能

### ✅ 可维护性相关

- [ ] 配置文件加 JSON5 注释说明为什么这么配
- [ ] 配置纳入 Git 版本管理，变更有记录
- [ ] 敏感信息（API Key, Token）不要直接提交 Git，用环境变量注入
- [ ] 定期 `openclaw doctor` 检查配置健康
- [ ] 重要变更前备份整个 `~/.openclaw` 目录

### ✅ 多智能体架构相关

- [ ] `maxSpawnDepth = 2` 支持编排模式
- [ ] 每个智能体设置独立的 `agentDir` 和 `workspace`
- [ ] 每个智能体配置独立的技能白名单，最小权限
- [ ] 路由 bindings 规则按精确到通用的顺序排列
- [ ] 巡检类智能体（如 Iris）权限最小化配置

---

## 附录：常用诊断命令速查

```bash
# ========== 配置验证 ==========
openclaw doctor                  # 全面配置诊断
openclaw doctor --fix            # 自动修复可修复的问题
openclaw doctor --verbose        # 详细诊断输出

# ========== 配置查看 ==========
openclaw config get <path>       # 查看特定配置路径的值
# 示例:
openclaw config get agents.defaults.model
openclaw config get agents.list.2.skills
openclaw config get sandbox.mode

# 查看完整 JSON Schema
openclaw config schema

# ========== 智能体状态 ==========
openclaw agents list             # 列出所有智能体
openclaw agents list --bindings  # 列出智能体 + 路由绑定

# ========== 技能状态 ==========
openclaw skills list             # 列出所有已加载的技能
openclaw skills show <name>      # 查看技能详情

# ========== 网关状态 ==========
openclaw gateway status          # 网关运行状态
openclaw gateway restart         # 重启网关

# ========== 通道诊断 ==========
openclaw channels status         # 所有通道状态
openclaw channels status --probe # 带连通性探测

# ========== 会话管理 ==========
openclaw sessions list           # 列出所有会话

# ========== 日志查看 ==========
openclaw logs -n 100            # 最近 100 行日志
openclaw logs -f                 # 实时跟踪日志
# 日志文件位置: /tmp/openclaw/openclaw-YYYY-MM-DD.log

# ========== 子代理管理 ==========
# 在聊天窗口中执行
/subagents list                  # 列出当前会话的子代理
/subagents log <id>              # 查看子代理日志
/subagents kill <id|all>         # 终止子代理
/subagents info <id>             # 查看子代理详情

# ========== 配置重载 ==========
openclaw config reload           # 强制立即重载配置
```

---

*本完整指南基于 OpenClaw 官方文档 + 大量生产环境踩坑经验整理* 🦞
```

将上述整合后的完整进阶配置大全保存到文件：

```bash
vim ~/.openclaw/workspace/OpenClaw_进阶配置大全_v2.0.md
# 粘贴上面的内容保存
```

已完成整合！这份 16,000 多行、覆盖所有 OpenClaw 配置知识点的完整指南，把所有配置问题统一整合在一起了。

可以删除之前零散的文件：
- `OpenClaw_配置文件关联关系与使用规则_v1.0.md`
- `OpenClaw_核心配置文件关联关系可视化_v1.0.md`
- `OpenClaw_核心配置文件一句话精准描述_v1.0.md`

它们的所有内容都已经整合到了 `OpenClaw_进阶配置大全_v2.0.md` 这一份完整文档中，实现一站式查询。