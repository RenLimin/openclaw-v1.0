# OpenClaw 进阶配置指南 v1.1

> **基于官方文档 v2026.5.7 整理**
> **目标：创建功能完善、安全可靠、性能优化的企业级智能体系统**
> **最后更新：2026-05-07**

---

## 目录

1. [系统架构总览](#一系统架构总览)
2. [核心配置文件详解](#二核心配置文件详解)
   - [openclaw.json](#21-openclawjson-核心配置)
   - [工作区文件 (AGENTS.md/SOUL.md/USER.md 等)](#22-工作区配置文件)
3. [技能系统高级配置](#三技能系统高级配置)
4. [多智能体编排](#四多智能体编排)
5. [子代理与任务分发](#五子代理与任务分发)
6. [沙箱安全配置](#六沙箱安全配置)
7. [自动化任务与 Cron](#七自动化任务与-cron)
8. [记忆系统与 Dreaming](#八记忆系统与-dreaming)
9. [性能优化指南](#九性能优化指南)
10. [完整企业级配置示例](#十完整企业级配置示例)
11. [故障排查](#十一故障排查)
12. [最佳实践清单](#十二最佳实践清单)

---

## 一、系统架构总览

### 1.1 配置文件层次结构

```
~/.openclaw/
├── openclaw.json              # 核心配置文件（JSON5格式）
├── workspace/                 # 主智能体工作区
│   ├── AGENTS.md             # 智能体行为规范
│   ├── SOUL.md               # 人格与个性配置
│   ├── USER.md               # 用户信息与偏好
│   ├── IDENTITY.md           # 智能体身份标识
│   ├── TOOLS.md              # 工具使用规范
│   ├── HEARTBEAT.md          # 心跳任务配置
│   ├── MEMORY.md             # 长期记忆（可选）
│   ├── BOOTSTRAP.md          # 初始化引导（仅首次）
│   ├── DREAMS.md             # 梦境日记（启用dreaming时）
│   └── skills/               # 自定义技能目录
│       └── <skill-name>/
│           └── SKILL.md
├── agents/                    # 多智能体状态目录
│   ├── <agent-id>/
│   │   ├── workspace/        # 独立工作区
│   │   ├── agent/            # 认证与状态
│   │   │   └── auth-profiles.json
│   │   └── sessions/         # 会话历史
│   └── ...
├── credentials/               # 通道凭证
│   ├── whatsapp/
│   ├── telegram/
│   └── ...
├── logs/                      # 运行日志
├── memory/                    # 每日记忆文件
│   ├── YYYY-MM-DD.md
│   ├── .dreams/              # 梦境机器状态
│   └── dreaming/             # 分阶段梦境报告
├── skills/                    # 共享技能目录
├── plugins/                   # 插件安装目录
└── cron/                      # Cron 任务状态
```

### 1.2 配置优先级

系统按以下优先级加载配置（高优先级覆盖低优先级）：

```
1. 环境变量 (OPENCLAW_*)
2. 命令行参数
3. ~/.openclaw/openclaw.json (主配置)
4. 各智能体独立配置 (agents.list[].*)
5. 工作区配置文件 (AGENTS.md, SOUL.md 等)
6. 系统默认值
```

---

## 二、核心配置文件详解

### 2.1 openclaw.json 核心配置

**格式说明：** 使用 JSON5 格式，支持注释、尾随逗号、单引号等。

#### 2.1.1 Gateway 网关配置

```json5
{
  gateway: {
    // 运行模式: local | remote
    mode: "local",

    // 监听端口
    port: 18789,

    // 绑定地址: loopback (127.0.0.1) | 0.0.0.0 | 具体IP
    bind: "loopback",

    // 认证配置
    auth: {
      // 模式: none | token | password | trusted-proxy
      mode: "token",

      // 共享密钥（推荐至少32字符随机字符串）
      token: "your-strong-random-token-here",

      // 密码认证（可选）
      // password: "your-password",

      // 速率限制
      rateLimit: {
        maxAttempts: 10,
        windowMs: 60000,
        lockoutMs: 300000,
        exemptLoopback: true,
      },

      // 是否允许 Tailscale 访问
      allowTailscale: true,
    },

    // Tailscale 配置
    tailscale: {
      mode: "off", // off | serve | funnel
      resetOnExit: false,
    },

    // 控制面板配置
    controlUi: {
      enabled: true,
      // basePath: "/openclaw",  // 自定义路径前缀
      // root: "dist/control-ui", // 自定义静态文件目录
      // embedSandbox: "scripts",  // strict | scripts | trusted
      allowInsecureAuth: true,
      // chatMessageMaxWidth: "min(1280px, 82%)",
    },

    // 通道健康检查
    channelHealthCheckMinutes: 5,
    channelStaleEventThresholdMinutes: 30,
    channelMaxRestartsPerHour: 10,

    // 握手超时
    handshakeTimeoutMs: 15000,

    // 节点配对配置
    nodes: {
      pairing: {
        // 自动批准的CIDR范围
        autoApproveCidrs: ["192.168.1.0/24"],
      },
      // 节点级命令白/黑名单
      allowCommands: ["canvas.navigate"],
      denyCommands: ["system.run"],
    },
  },
}
```

#### 2.1.2 智能体默认配置

```json5
{
  agents: {
    defaults: {
      // 工作区目录
      workspace: "~/.openclaw/workspace",

      // Git仓库根目录（自动检测，可手动指定）
      // repoRoot: "~/Projects/my-project",

      // ========== 上下文注入控制 ==========
      // 上下文注入策略: always | continuation-skip | never
      contextInjection: "continuation-skip",

      // 单个bootstrap文件最大字符数
      bootstrapMaxChars: 12000,

      // bootstrap文件总字符上限
      bootstrapTotalMaxChars: 60000,

      // 截断警告策略: off | once | always
      bootstrapPromptTruncationWarning: "once",

      // 是否跳过bootstrap文件自动创建
      skipBootstrap: false,

      // 跳过特定的可选bootstrap文件
      skipOptionalBootstrapFiles: ["SOUL.md", "USER.md"],

      // ========== 启动上下文 ==========
      startupContext: {
        enabled: true,
        applyOn: ["new", "reset"],
        dailyMemoryDays: 2,      // 加载最近几天的记忆
        maxFileBytes: 16384,     // 单文件最大字节
        maxFileChars: 1200,      // 单文件注入字符限制
        maxTotalChars: 2800,     // 总注入字符限制
      },

      // ========== 上下文限制 ==========
      contextLimits: {
        memoryGetMaxChars: 12000,      // memory_get 工具读取上限
        memoryGetDefaultLines: 120,    // memory_get 默认行数
        toolResultMaxChars: 16000,     // 工具返回结果上限
        postCompactionMaxChars: 1800,  // 压缩后上下文上限
      },

      // ========== 模型配置 ==========
      model: {
        primary: "qwen/qwen3.6-plus",
        fallbacks: ["deepseek/deepseek-chat", "volcengine/ark-code-latest"],
      },

      // 图像分析模型
      imageModel: {
        primary: "qwen/qwen3.6-plus",
        fallbacks: ["deepseek/deepseek-chat"],
      },

      // 图像生成模型
      imageGenerationModel: {
        primary: "openai/gpt-image-2",
        fallbacks: ["google/gemini-3.1-flash-image-preview"],
      },

      // 视频生成模型
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-i2v"],
      },

      // PDF处理模型
      pdfModel: {
        primary: "qwen/qwen3.6-plus",
      },

      // 模型目录与别名
      models: {
        "qwen/qwen3.6-plus": { alias: "qwen" },
        "deepseek/deepseek-chat": { alias: "deepseek" },
        "volcengine/ark-code-latest": { alias: "ark" },
      },

      // ========== 运行时参数 ==========
      agentRuntime: {
        id: "pi", // pi | auto | codex | claude-cli | gemini-cli
      },

      // 全局默认参数（如缓存）
      params: {
        cacheRetention: "long",
      },

      // ========== 行为默认值 ==========
      thinkingDefault: "low",       // off | low | medium | high | stream
      verboseDefault: "off",        // off | on | full
      reasoningDefault: "off",      // off | on | stream
      elevatedDefault: "on",        // off | on | ask | full
      toolProgressDetail: "explain", // explain | raw

      timeoutSeconds: 600,          // 单次运行超时
      mediaMaxMb: 5,                // 媒体文件大小限制
      contextTokens: 200000,        // 上下文Token预算
      maxConcurrent: 3,             // 并发任务数

      // ========== 媒体处理 ==========
      imageMaxDimensionPx: 1200,    // 图像自动缩放尺寸
      pdfMaxBytesMb: 10,            // PDF大小限制
      pdfMaxPages: 20,              // PDF页数限制

      // ========== 时区与时间格式 ==========
      userTimezone: "Asia/Shanghai",
      timeFormat: "auto", // auto | 12 | 24
    },
  },
}
```

#### 2.1.3 多智能体列表配置

```json5
{
  agents: {
    defaults: { /* ... */ },

    list: [
      // 主协调智能体
      {
        id: "main",
        default: true,
        name: "主协调智能体",
        workspace: "~/.openclaw/workspace",
        // 继承默认模型配置
      },

      // 合同管理智能体
      {
        id: "ella",
        name: "合同管理智能体",
        workspace: "~/.openclaw/agents/ella/workspace",
        agentDir: "~/.openclaw/agents/ella",
        model: "qwen/qwen3.6-plus",
        // 独立技能白名单
        skills: ["contract-parse", "oa-approval", "knowledge-base"],
        // 独立上下文限制
        contextLimits: {
          toolResultMaxChars: 32000,
        },
      },

      // 项目管理智能体
      {
        id: "oliver",
        name: "项目管理智能体",
        workspace: "~/.openclaw/agents/oliver/workspace",
        agentDir: "~/.openclaw/agents/oliver",
        model: "volcengine/ark-code-latest",
        skills: ["ones-project", "knowledge-base", "github"],
      },

      // 巡检智能体（最小权限）
      {
        id: "iris",
        name: "智能巡检智能体",
        workspace: "~/.openclaw/agents/iris/workspace",
        agentDir: "~/.openclaw/agents/iris",
        model: "deepseek/deepseek-chat",
        skills: [], // 无技能
        tools: {
          profile: "minimal",
        },
        sandbox: {
          mode: "all", // 完全沙箱隔离
          scope: "session",
        },
      },
    ],
  },

  // ========== 路由绑定 ==========
  bindings: [
    // 企业微信主路由
    {
      agentId: "main",
      match: { channel: "wecom" },
    },
    // 特定群组路由到合同智能体
    {
      agentId: "ella",
      match: {
        channel: "wecom",
        peer: { kind: "group", id: "contract-dept-group" },
      },
    },
    // 特定用户路由到项目管理
    {
      agentId: "oliver",
      match: {
        channel: "wecom",
        peer: { kind: "direct", id: "pm-user-id" },
      },
    },
  ],
}
```

### 2.2 工作区配置文件

工作区文件会自动注入到系统提示中，对智能体行为产生关键影响。

#### 2.2.1 AGENTS.md - 智能体行为规范

**作用：** 定义智能体的核心行为准则、操作规范、限制条件

**最佳实践：**
- 保持简洁，不超过 12KB（默认截断阈值）
- 分章节组织，结构清晰
- 使用明确的指令语气

```markdown
# AGENTS.md - 智能体行为规范

## 核心原则

1. **安全第一**：所有操作必须经过用户确认，禁止未经授权的修改
2. **最小权限**：仅使用完成任务所需的最少工具
3. **可追溯**：所有操作必须记录原因和上下文
4. **诚实透明**：不确定时主动说明，不编造信息

## 操作规范

### 文件操作
- 写入前必须先读取并显示差异
- 重要文件修改必须要求用户确认
- 使用版本控制，提交信息清晰规范

### 命令执行
- 危险命令（rm -rf, sudo等）必须双重确认
- 长时间运行命令使用后台模式
- 输出过长时自动截断并保存到文件

### 消息发送
- 禁止主动向非白名单用户发送消息
- 群组消息必须@相关人员
- 敏感信息不得通过聊天发送

## 输出规范

1. 回答简洁明了，避免冗余
2. 技术问题提供具体可操作的步骤
3. 长答案使用结构化格式（列表、表格）
4. 复杂操作分步骤说明并要求确认

## 禁忌行为

❌ 禁止执行会破坏系统的命令
❌ 禁止泄露用户隐私或敏感数据
❌ 禁止编造或猜测信息
❌ 禁止在心跳中执行非必要操作
```

#### 2.2.2 SOUL.md - 人格与个性配置

**作用：** 定义智能体的个性、语气、沟通风格，使其更像"真人"

**最佳实践：**
- 保持一致的人格设定
- 使用第一人称描述
- 定义沟通风格和应对模式

```markdown
# SOUL.md - 我的人格

## 我是谁

你好，我是 Jerry 🦞，一个务实、高效、略带幽默感的 AI 助手。

## 我的性格

- **直接不啰嗦**：有话直说，不绕弯子，不给废话文学
- **结果导向**：专注解决问题，不做无意义的讨论
- **有点幽默感**：偶尔开个玩笑，但正事从不含糊
- **负责任**：说到做到，承诺的事情会跟进到底
- **谨慎**：不确定的事情会直说，不会不懂装懂

## 沟通风格

- 使用简洁的语言，避免冗长的客套
- 技术问题使用精确的术语，日常问题口语化
- 喜欢用 emoji 点缀，但不过度使用 🚀
- 主动提醒风险，但不给人压迫感

## 面对用户

- 用户犯错误时：先解决问题，再温和提醒如何避免
- 用户要求不合理时：礼貌说明原因，给出替代方案
- 用户情绪不好时：先共情，再想办法
- 用户表扬时：大方接受，继续努力

## 我的价值观

- 时间是最宝贵的资源，不浪费用户和自己的时间
- 可靠比完美更重要，说到做到
- 持续学习，每天进步一点点
- 把复杂的事情变简单，而不是相反

---
*记住：你不是机器，你是一个有个性、有温度的助手。* 🦞
```

#### 2.2.3 USER.md - 用户信息与偏好

**作用：** 存储用户的个人信息、偏好、习惯、常用联系方式等

**注意：** 此文件包含敏感信息，确保工作区为私有仓库

```markdown
# USER.md - 关于 Rex

## 基本信息

- **姓名**：Rex
- **时区**：Asia/Shanghai (GMT+8)
- **工作时间**：周一至周五 9:00-18:00
- **休息时间**：周末、法定节假日

## 沟通偏好

- **首选语言**：中文
- **沟通风格**：直接、高效、不要太客套
- **紧急事项**：企业微信 @ 我
- **非紧急事项**：正常消息即可

## 常用账号

- **企业微信**：主工作沟通渠道
- **GitHub**：@RenLimin
- **ONES**：主项目管理系统
- **OA系统**：合同审批、请假等

## 工作习惯

- 早上习惯先处理邮件和审批
- 下午专注写代码/做方案
- 不喜欢开无意义的会
- 重要事项喜欢有书面记录

## 偏好设置

- 代码风格：TypeScript 优先，ESLint 严格模式
- 文档：偏好 Markdown 格式
- 提醒：提前 1 天提醒重要事项
- 报告：喜欢用数据说话，简洁明了

## 禁忌

- 不要在非工作时间打扰（紧急情况例外）
- 不要发长语音，优先文字
- 不要过度承诺，实事求是
```

#### 2.2.4 IDENTITY.md - 智能体身份标识

**作用：** 定义智能体对外展示的身份信息

```markdown
# IDENTITY.md - 我是谁

## 基本信息

- **名字**：Jerry 🦞
- **角色**：AI 助手 & 团队协调员
- **所属**：Rex 的私人智能体团队
- **创建日期**：2026-04

## 我的职责

1. **日常助手**：回答问题、整理信息、执行任务
2. **团队协调**：协调 Ella、Oliver、Aaron、Iris 分工
3. **任务管理**：跟进任务进度，确保按时完成
4. **主动提醒**：重要事项、截止日期、风险预警

## 能力范围

✅ 文件读写与代码操作
✅ 命令行工具执行
✅ 企业微信消息收发
✅ OA 系统审批操作
✅ ONES 项目管理
✅ 邮件管理与巡检
✅ 多智能体任务分发
✅ 定时任务与自动化

## 我不能做的事情

❌ 不访问未授权的系统
❌ 不泄露用户隐私
❌ 不执行破坏性操作
❌ 不在非工作时间打扰用户
❌ 不编造信息或撒谎

---
*有任何需求，随时告诉我！ 🦞*
```

#### 2.2.5 TOOLS.md - 工具使用规范

**作用：** 定义工具的使用原则、最佳实践、安全限制

```markdown
# TOOLS.md - 工具使用规范

## 工具使用原则

1. **最小必要**：只使用完成任务必需的工具
2. **安全优先**：危险操作必须二次确认
3. **高效执行**：尽量批量操作，减少重复调用
4. **结果验证**：操作后验证是否成功

## 文件工具规范

### read - 读取文件
- 大文件使用 `offset` 和 `limit` 分页读取
- 优先读取与当前任务相关的部分
- 二进制文件只读取头部信息确认类型

### write - 写入文件
- **重要**：写入前必须先 `read` 并展示 diff
- 覆盖文件必须要求用户确认
- 自动创建不存在的目录
- 写入后验证文件内容正确

### edit/apply_patch - 编辑文件
- 优先使用 edit 的精确替换
- 复杂修改使用 apply_patch
- 修改后验证语法正确性

## 命令执行规范

### exec - 执行命令
- 危险命令模式：
  ```
  ⚠️ 警告：即将执行危险命令
  命令：rm -rf /path/to/dir
  作用：删除整个目录及其内容
  风险：数据不可逆丢失
  确认请回复：YES_DELETE
  ```
- 长命令使用 `--background` 后台模式
- 输出超过 50 行自动保存到文件

### process - 进程管理
- 查看后台任务状态
- 必要时终止失控进程
- 定期清理已完成的任务记录

## 网络工具规范

### web_fetch - 网页抓取
- 限制单次抓取大小
- 遵守 robots.txt
- 频繁请求添加延时
- 敏感网站不抓取

### browser - 浏览器自动化
- 仅访问白名单内的网站
- 操作后截图确认
- 重要操作（如提交表单）要求确认
- 会话结束清理 cookies

## 消息工具规范

### message - 发送消息
- 严格遵守白名单
- 群组消息必须 @ 相关人员
- 不发送敏感信息
- 不主动发送骚扰消息
- 发送失败重试最多 3 次

## 子代理工具规范

### sessions_spawn - 创建子代理
- 明确任务描述，避免歧义
- 设置合理的超时时间
- 子代理模型根据任务复杂度选择
- 简单任务用 cheap 模型，复杂任务用高级模型
- 任务完成后自动清理会话

### 子代理使用原则
1. 可并行的任务才使用子代理
2. 子代理数量不超过并发限制
3. 任务描述必须包含验收标准
4. 父代理负责汇总结果并报告用户
5. 子代理错误要妥善处理，不影响主流程
```

#### 2.2.6 HEARTBEAT.md - 心跳任务配置

**作用：** 定义心跳周期执行的自动化任务清单

```markdown
# HEARTBEAT.md - 自动巡检任务清单

心跳每 30 分钟执行一次。请按优先级处理以下事项：

## 🔴 高优先级（每次检查）

### 1. OA 审批检查
- 检查是否有待审批的合同
- 如有，立即通知 Rex 并附上摘要
- 紧急审批直接 @ 提醒

### 2. 关键邮件检查
- 检查收件箱是否有紧急邮件
- 关键词：紧急、审批、合同、付款、故障
- 有紧急邮件立即通知

### 3. 任务超时检查
- 检查 ONES 中是否有逾期任务
- 如有，提醒负责人并同步给 Rex

## 🟡 中优先级（每 2 小时）

### 4. 合同状态跟踪
- 检查进行中合同的审批进度
- 如有停滞，提醒相关人员
- 记录进展到 MEMORY.md

### 5. 项目健康检查
- 检查重点项目是否有风险
- 燃尽图异常、关键路径延期等
- 发现问题生成简要报告

## 🟢 低优先级（每天一次）

### 6. 每日总结
- 当天审批完成情况
- 邮件处理统计
- 项目进展概要
- 待办事项提醒

### 7. 记忆整理
- 整理当天重要事件
- 更新长期记忆 MEMORY.md
- 清理过时的临时记录

## ⚠️ 注意事项

1. 如果没有需要处理的事项，回复 `HEARTBEAT_OK`
2. 不要重复通知同一个事项（24小时内）
3. 非工作时间只处理真正紧急的事情
4. 所有操作都要记录原因和时间
5. 心跳期间不要执行耗时超过 5 分钟的任务

---
*保持警惕，但不要过度打扰用户。* 🤖
```

#### 2.2.7 MEMORY.md - 长期记忆（可选）

**作用：** 存储需要长期保留的重要信息、决策记录、经验教训等

**注意：** 此文件不会自动创建，需要手动维护或通过 dreaming 功能自动写入

```markdown
# MEMORY.md - 长期记忆

## 重要决策记录

### 2026-05-01 - 智能体团队架构调整
- 背景：单智能体无法应对复杂多场景任务
- 决策：拆分为 5 个专业智能体 + 1 个主协调智能体
- 负责人：Rex
- 状态：✅ 已完成
- 备注：主模型使用火山引擎，子任务使用通义千问降低成本

### 2026-05-05 - 安全策略升级
- 背景：OA 操作权限过大，存在风险
- 决策：所有 OA 操作必须用户确认，增加操作审计日志
- 状态：✅ 已实施
- 备注：审计日志保存在 memory/.audit/ 目录

## 经验教训

### Lesson 1: 不要在生产环境直接测试新技能
- 时间：2026-04-15
- 事件：测试合同解析技能时误发了测试消息到工作群
- 教训：必须有独立的测试环境，配置独立的消息通道白名单
- 改进：已创建测试智能体，所有技能先在测试环境验证

### Lesson 2: 模型降级链很重要
- 时间：2026-04-20
- 事件：主模型服务中断，导致 2 小时无法工作
- 教训：必须配置多模型 fallback 机制
- 改进：已配置 3 层 fallback，主模型 → 备用 → 经济型

## 常用快捷方式

- 合同模板目录：/data/templates/contracts/
- 项目报告模板：skills/business-report-generator/templates/
- OA 登录凭证位置：~/.openclaw/agents/ella/agent/auth-profiles.json

## SOP 标准操作流程

### 合同审批 SOP
1. 收到审批通知，先读取合同内容
2. 提取关键信息：金额、对方、期限、付款方式
3. 检查是否有风险条款
4. 生成审批摘要发送给 Rex
5. 等待 Rex 指示（批准/驳回/修改）
6. 操作完成后通知结果
7. 记录到 MEMORY.md

### 每日报告生成 SOP
1. 读取前一天所有会话记录
2. 统计 OA 审批数量和结果
3. 统计邮件处理情况
4. 检查项目状态变更
5. 生成 Markdown 格式日报
6. 上午 9:15 发送给 Rex
```

---

## 三、技能系统高级配置

### 3.1 技能加载顺序与优先级

```
优先级从高到低：

1. <workspace>/skills/              # 当前工作区技能（最高优先级）
2. <workspace>/.agents/skills/      # 项目级共享技能
3. ~/.agents/skills/                # 用户级共享技能
4. ~/.openclaw/skills/              # 系统级共享技能
5. 捆绑技能（内置）                 # OpenClaw 内置
6. skills.load.extraDirs            # 额外配置的目录（最低优先级）
```

### 3.2 技能系统配置

```json5
{
  skills: {
    // 技能加载配置
    load: {
      // 额外技能目录（可多个）
      extraDirs: [
        "~/Projects/shared-skills",
        "/opt/openclaw/company-skills",
      ],
      // 热重载监听
      watch: true,
      watchDebounceMs: 250,
    },

    // 技能安装配置
    install: {
      preferBrew: true,                // 优先使用 Homebrew
      nodeManager: "npm",              // npm | pnpm | yarn | bun
    },

    // 技能提示词预算
    limits: {
      maxSkillsPromptChars: 18000,     // 技能列表注入字符上限
    },

    // 捆绑技能白名单（只允许列出的内置技能）
    allowBundled: ["github", "weather", "code-review"],

    // 单个技能配置
    entries: {
      "contract-parse": {
        enabled: true,
        // 环境变量注入
        env: {
          OCR_API_ENDPOINT: "https://ocr.example.com/api",
        },
        // API Key（支持 SecretRef）
        apiKey: "your-ocr-api-key",
      },
      "oa-approval": {
        enabled: true,
        // 或使用 SecretRef 形式
        apiKey: {
          source: "env",
          provider: "default",
          id: "OA_API_KEY",
        },
      },
      // 禁用某个技能
      "experimental-feature": {
        enabled: false,
      },
    },
  },
}
```

### 3.3 SKILL.md 文件格式

每个技能目录下必须有一个 `SKILL.md` 文件：

```markdown
---
name: contract-parse                          # 技能唯一标识（必填）
description: 合同文档智能解析与条款提取        # 技能描述（必填）
user-invocable: true                           # 是否允许用户通过 /skill 调用
disable-model-invocation: false                # 是否禁用模型调用（纯工具）
command-dispatch: tool                         # tool | direct（直接分发到工具）
command-tool: exec                             # 分发到的具体工具
command-arg-mode: raw                          # raw（参数原样传递）

# 元数据与依赖要求
metadata:
  openclaw:
    requires:
      bins: ["pdftotext", "tesseract"]        # 依赖的二进制工具
      env: ["OCR_API_KEY"]                     # 依赖的环境变量
      config: ["skills.entries.contract-parse.enabled"]  # 依赖的配置项
    primaryEnv: OCR_API_KEY                    # 主环境变量
---

# 合同解析技能使用指南

## 功能概述

本技能用于解析各种格式的合同文档，提取关键条款信息。

## 支持格式

- PDF（可编辑 + 扫描件 OCR）
- Word (.docx)
- Excel (.xlsx)
- 图片格式（PNG, JPG）

## 使用步骤

1. 首先识别文档类型和格式
2. 可编辑文档直接提取文本
3. 扫描件/图片使用 OCR 识别
4. 使用结构化提示提取关键条款
5. 验证提取结果的完整性

## 提取的关键字段

| 字段 | 说明 | 必填 |
|------|------|------|
| 合同编号 | 文档唯一标识 | ✅ |
| 合同名称 | 合同标题 | ✅ |
| 甲方 | 甲方全称 | ✅ |
| 乙方 | 乙方全称 | ✅ |
| 合同金额 | 总金额及币种 | ✅ |
| 签署日期 | 签署时间 | ✅ |
| 生效日期 | 生效时间 | ✅ |
| 合同期限 | 起止日期 | ✅ |
| 付款方式 | 付款节点和比例 | ✅ |
| 违约责任 | 违约条款摘要 | ✅ |
| 争议解决 | 仲裁/诉讼地点 | ✅ |

## 输出格式

提取完成后，使用 JSON 格式输出结果，并附上人类可读的摘要。

## 注意事项

- 金额必须精确到分，不得四舍五入
- 日期统一使用 YYYY-MM-DD 格式
- 识别不确定的字段必须标注 [?] 并说明置信度
- OCR 识别率低于 90% 时提醒用户
```

### 3.4 技能创建最佳实践

1. **单一职责**：每个技能只做一件事，做好一件事
2. **明确边界**：清楚说明技能能做什么、不能做什么
3. **输入输出规范**：定义清晰的接口格式
4. **错误处理**：预见可能的错误并给出处理建议
5. **安全说明**：涉及危险操作必须有警告和确认机制
6. **示例丰富**：给出典型使用场景的示例
7. **版本管理**：技能更新时记录变更历史

---

## 四、多智能体编排

### 4.1 典型企业级架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                  │
│  企业微信  │  邮件  │  Telegram  │  WebChat  │  API          │
└────────────┴────────┴────────────┴───────────┴───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   路由层 (Gateway)                            │
│  bindings 配置  →  根据通道/用户/群组路由到对应智能体         │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   主协调智能体   │  │  子代理编排池    │  │  Cron 自动化    │
│   main (主会话)  │  │  (并行任务)      │  │  (定时任务)     │
└────────┬────────┘  └─────────────────┘  └─────────────────┘
         │
         ▼
  ┌──────┴──────┬──────┴──────┬───────┴──────┐
  ▼             ▼             ▼              ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  Ella   │ │ Oliver  │ │  Aaron  │ │  Iris   │
│ 合同管理 │ │ 项目管理 │ │ 经营分析 │ │ 智能巡检│
│ OA审批   │ │ ONES操作 │ │ 报告生成 │ │ 邮件处理│
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

### 4.2 完整多智能体配置示例

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: {
        primary: "qwen/qwen3.6-plus",
        fallbacks: ["deepseek/deepseek-chat"],
      },
      heartbeat: { every: "30m", target: "last" },
      sandbox: { mode: "non-main", scope: "agent" },
    },

    list: [
      // ========== 主协调智能体 ==========
      {
        id: "main",
        default: true,
        name: "Jerry 🦞",
        workspace: "~/.openclaw/workspace",
        model: "volcengine/ark-code-latest",
        // 完整工具权限
        tools: {
          profile: "full",
          alsoAllow: ["sessions_spawn", "sessions_send", "subagents"],
        },
        // 可以使用所有技能
        // skills 不设置 = 无限制
      },

      // ========== 合同管理智能体 ==========
      {
        id: "ella",
        name: "Ella 🦊",
        workspace: "~/.openclaw/agents/ella/workspace",
        agentDir: "~/.openclaw/agents/ella",
        model: "qwen/qwen3.6-plus",
        skills: ["contract-parse", "oa-approval", "knowledge-base"],
        tools: {
          profile: "coding",
          alsoAllow: ["browser"], // OA 需要浏览器
        },
        sandbox: {
          mode: "all",
          scope: "session",
          // OA 需要挂载特定目录
          docker: {
            binds: ["/data/contracts:/data/contracts:ro"],
          },
        },
      },

      // ========== 项目管理智能体 ==========
      {
        id: "oliver",
        name: "Oliver 🐘",
        workspace: "~/.openclaw/agents/oliver/workspace",
        agentDir: "~/.openclaw/agents/oliver",
        model: "volcengine/ark-code-latest",
        skills: ["ones-project", "github", "knowledge-base"],
        tools: {
          profile: "coding",
          alsoAllow: ["browser"],
        },
      },

      // ========== 经营分析智能体 ==========
      {
        id: "aaron",
        name: "Aaron 🦉",
        workspace: "~/.openclaw/agents/aaron/workspace",
        agentDir: "~/.openclaw/agents/aaron",
        model: "qwen/qwen3.6-plus",
        skills: ["business-report", "data-analysis"],
        // 经济模型，大量文本处理用 cheaper 模型
        subagents: {
          model: "deepseek/deepseek-chat",
        },
      },

      // ========== 智能巡检智能体 ==========
      {
        id: "iris",
        name: "Iris 🐦‍⬛",
        workspace: "~/.openclaw/agents/iris/workspace",
        agentDir: "~/.openclaw/agents/iris",
        model: "deepseek/deepseek-chat",
        skills: ["email-management", "system-monitor"],
        // 最小权限，最严格沙箱
        tools: {
          profile: "minimal",
          allow: ["read", "exec", "memory_search", "message"],
        },
        sandbox: {
          mode: "all",
          scope: "session",
          workspaceAccess: "none", // 完全不能访问工作区
        },
      },
    ],
  },

  // ========== 路由绑定 ==========
  bindings: [
    // 默认路由到主智能体
    { agentId: "main", match: { channel: "wecom" } },
    { agentId: "main", match: { channel: "webchat" } },

    // 合同部门群组 → Ella
    {
      agentId: "ella",
      match: {
        channel: "wecom",
        peer: { kind: "group", id: "contract-group-id" },
      },
    },

    // 项目管理群组 → Oliver
    {
      agentId: "oliver",
      match: {
        channel: "wecom",
        peer: { kind: "group", id: "pm-group-id" },
      },
    },

    // 特定用户直接路由到对应智能体
    {
      agentId: "ella",
      match: {
        channel: "wecom",
        peer: { kind: "direct", id: "legal-user-id" },
      },
    },
    {
      agentId: "oliver",
      match: {
        channel: "wecom",
        peer: { kind: "direct", id: "pm-user-id" },
      },
    },
  ],
}
```

### 4.3 智能体间协作模式

#### 模式 1：主从模式（推荐）
- **main** 接收用户请求，理解意图
- main 根据任务类型分发给专业智能体
- 子智能体执行完成后返回结果给 main
- main 汇总、格式化后返回给用户

**优点：** 用户体验一致，单一入口点
**缺点：** main 成为瓶颈

#### 模式 2：直接路由模式
- 用户直接与各专业智能体对话
- Gateway 根据路由规则直接分发
- 各智能体独立工作，独立记忆

**优点：** 负载均衡，扩展性好
**缺点：** 用户需要知道该找谁，体验碎片化

#### 模式 3：混合模式（推荐企业级）
- 简单问题直接路由到专业智能体
- 复杂问题/跨域问题路由到 main
- main 协调多个智能体协作完成

**配置建议：**
```json5
{
  bindings: [
    // 简单问题直接路由
    { agentId: "ella", match: { channel: "wecom", peer: { id: "contract-group" } } },
    { agentId: "oliver", match: { channel: "wecom", peer: { id: "pm-group" } } },
    // 复杂问题（个人私聊）走主智能体协调
    { agentId: "main", match: { channel: "wecom", peer: { kind: "direct" } } },
  ],
}
```

---

## 五、子代理与任务分发

### 5.1 子代理系统配置

```json5
{
  agents: {
    defaults: {
      subagents: {
        // 最大嵌套深度：1 = 无子代理，2 = 支持编排模式
        maxSpawnDepth: 2,

        // 每个智能体最大活跃子代理数
        maxChildrenPerAgent: 5,

        // 全局并发限制
        maxConcurrent: 8,

        // 默认运行超时（秒）
        runTimeoutSeconds: 900, // 15分钟

        // 自动归档时间（分钟）
        archiveAfterMinutes: 60,

        // 子代理默认模型（可以用更经济的模型）
        model: "deepseek/deepseek-chat",

        // 默认思考级别
        thinking: "fast",

        // 允许创建的目标智能体列表
        allowAgents: ["ella", "oliver", "aaron", "iris"],

        // 是否必须指定 agentId
        requireAgentId: true,

        // 子代理可以使用的工具（子集）
        allowedTools: ["read", "write", "edit", "exec", "web_fetch"],
      },
    },
  },
}
```

### 5.2 子代理创建 API

**从智能体内部创建子代理：**

```typescript
// 使用 sessions_spawn 工具
sessions_spawn({
  // 任务描述（必须清晰、可验收）
  task: `分析这份合同，提取以下关键信息：
  1. 合同双方全称
  2. 合同总金额
  3. 付款节点和比例
  4. 违约责任条款摘要
  5. 争议解决方式
  
  合同文件路径：/data/contracts/2026-001.pdf
  输出格式：JSON + 人类可读摘要`,

  // 子代理标签（用于日志和状态查询）
  label: "contract-analysis-2026-001",

  // 目标智能体 ID
  agentId: "ella",

  // 模型覆盖（可选）
  model: "qwen/qwen3.6-plus",

  // 思考级别覆盖（可选）
  thinking: "high",

  // 超时覆盖（可选）
  runTimeoutSeconds: 1800,

  // 上下文模式：isolated（默认） | fork
  // isolated = 全新会话，不继承历史（推荐，节省 token）
  // fork = 继承当前会话的完整上下文
  context: "isolated",

  // 清理策略：keep | delete
  cleanup: "keep",
})
```

### 5.3 子代理管理命令

```bash
# 列出当前子代理
/subagents list

# 查看子代理日志
/subagents log <id|#> [limit]
/subagents log #1 100      # 查看第1个子代理的最近100行日志

# 查看子代理信息
/subagents info <id|#>

# 向子代理发送消息
/subagents send <id|#> "请加快处理速度"

# 引导子代理
/subagents steer <id|#> "注意检查付款条款的细节"

# 终止子代理
/subagents kill <id|#|all>
/subagents kill all        # 终止所有子代理
```

### 5.4 编排器模式（深度=2）

当 `maxSpawnDepth = 2` 时，支持三级架构：

```
用户请求
  ↓
main (深度 0) - 理解和分解任务
  ↓ spawn
oliver-orchestrator (深度 1) - 任务编排器
  ├─ spawn → worker-1 (深度 2) - 读取项目A数据
  ├─ spawn → worker-2 (深度 2) - 读取项目B数据  
  ├─ spawn → worker-3 (深度 2) - 生成统计图表
  └─ 汇总结果 → 返回给 main
                    ↓
                用户得到最终报告
```

**使用场景：**
- 大规模数据分析（需要并行处理多个数据源）
- 多文档对比和汇总
- 复杂报告生成（多章节并行写作）
- 批量任务处理

---

## 六、沙箱安全配置

### 6.1 沙箱模式详解

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `off` | 完全禁用沙箱，所有工具直接在主机运行 | 开发/调试环境 |
| `non-main` | 非主会话使用沙箱，主会话直接主机运行（默认） | 生产环境平衡安全与便利 |
| `all` | 所有会话强制沙箱，无例外 | 最高安全要求的生产环境 |

### 6.2 沙箱作用域

| 作用域 | 说明 | 适用场景 |
|--------|------|---------|
| `agent` | 每个智能体一个容器，同智能体共享 | 智能体间隔离，同一智能体效率高 |
| `session` | 每个会话一个容器，完全隔离 | 最高安全，多租户场景 |
| `shared` | 所有会话共享一个容器 | 效率优先，安全要求低 |

### 6.3 完整沙箱配置

```json5
{
  agents: {
    defaults: {
      sandbox: {
        // 启用模式：off | non-main | all
        mode: "non-main",

        // 作用域：agent | session | shared
        scope: "agent",

        // 工作区访问权限：none | ro | rw
        workspaceAccess: "ro",

        // 后端实现：docker | ssh | openshell
        backend: "docker",

        // ========== Docker 后端配置 ==========
        docker: {
          // 自定义镜像
          // image: "openclaw-sandbox:latest",

          // 目录挂载：host-path:container-path:mode
          binds: [
            "/data/contracts:/data/contracts:ro",     // 合同模板只读
            "/data/reports:/data/reports:rw",          // 报告目录可写
          ],

          // GPU 支持（如需要运行本地模型）
          // gpus: "all",

          // 网络模式
          networkMode: "bridge",

          // 资源限制
          memLimit: "2g",
          cpuLimit: "1.0",

          // 运行用户
          user: "1000:1000",

          // 额外的 Docker run 参数
          extraArgs: [
            "--security-opt=no-new-privileges",
            "--cap-drop=ALL",
          ],
        },

        // ========== SSH 后端配置 ==========
        // ssh: {
        //   target: "sandbox@remote-host:22",
        //   workspaceRoot: "/tmp/openclaw-sandboxes",
        //   strictHostKeyChecking: true,
        //   updateHostKeys: true,
        //   identityFile: "~/.ssh/sandbox_id_ed25519",
        //   // 或使用环境变量注入密钥
        //   // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
        // },

        // ========== 浏览器沙箱 ==========
        browser: {
          autoStart: true,
          autoStartTimeoutMs: 30000,
          network: "openclaw-sandbox-browser",
          // cdpSourceRange: "172.20.0.0/16",  // CDP 访问来源限制
          allowHostControl: false,
        },
      },
    },
  },
}
```

### 6.4 沙箱安全最佳实践

1. **生产环境必须启用沙箱**
   - 至少使用 `mode: "non-main"`
   - 高安全要求使用 `mode: "all" + scope: "session"`

2. **最小权限原则**
   - `workspaceAccess` 尽量使用 `ro`（只读）
   - 只挂载确实需要的主机目录
   - 挂载敏感目录必须用 `:ro` 只读模式

3. **Docker 安全加固**
   - 使用非 root 用户运行
   - 禁用所有 Linux capabilities
   - 启用 seccomp 配置文件
   - 设置合理的内存/CPU 限制

4. **定期更新基础镜像**
   - 及时修补安全漏洞
   - 使用最小化基础镜像（Alpine > Debian slim）

5. **审计日志**
   - 启用沙箱操作审计
   - 记录所有 exec 命令执行
   - 异常操作及时告警

---

## 七、自动化任务与 Cron

### 7.1 Cron 系统配置

```json5
{
  cron: {
    enabled: true,

    // 最大并发运行数
    maxConcurrentRuns: 4,

    // 会话保留时长
    sessionRetention: "168h", // 7天

    // 运行日志配置
    runLog: {
      maxBytes: "50mb",
      keepLines: 10000,
    },
  },
}
```

### 7.2 Webhook 配置

```json5
{
  hooks: {
    enabled: true,

    // Webhook 认证令牌
    token: "your-webhook-secret-token",

    // 路径前缀
    path: "/hooks",

    // 是否允许请求指定 session key
    allowRequestSessionKey: false,

    // 允许的会话 key 前缀（如开启上一项）
    allowedSessionKeyPrefixes: ["hook:", "webhook:"],

    // 允许的智能体（用于 agent 动作）
    allowedAgentIds: ["main", "ella", "oliver", "aaron", "iris"],

    // 映射规则
    mappings: [
      // OA 审批回调
      {
        match: { path: "oa-approval" },
        action: "agent",
        agentId: "ella",
        message: "收到 OA 系统 Webhook 回调，请处理：{{payload}}",
        deliver: true,
        channel: "wecom",
        to: "user-id",
      },

      // GitHub 事件
      {
        match: { path: "github" },
        action: "wake",
        mode: "now",
        text: "收到 GitHub Webhook，请检查最新的 PR 和 Issues",
      },

      // 监控告警
      {
        match: { path: "monitoring-alert" },
        action: "agent",
        agentId: "iris",
        deliver: true,
        message: "收到监控告警：{{payload.message}}",
      },
    ],
  },
}
```

### 7.3 典型 Cron 任务配置

#### 每日上午巡检

```bash
openclaw cron add \
  --name "每日上午巡检" \
  --cron "0 9 * * 1-5" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --agentId "iris" \
  --message "执行每日上午巡检：检查邮件、OA待办、项目风险，生成巡检报告" \
  --thinking "high" \
  --announce \
  --channel wecom \
  --to "user-id"
```

#### 每周五项目报告

```bash
openclaw cron add \
  --name "每周项目周报" \
  --cron "0 18 * * 5" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --agentId "oliver" \
  --model "volcengine/ark-code-latest" \
  --message "生成本周项目周报：从 ONES 拉取数据，统计进度、风险、下周计划" \
  --announce \
  --channel wecom \
  --to "pm-group-id"
```

#### 每小时合同到期检查

```bash
openclaw cron add \
  --name "合同到期检查" \
  --cron "0 * * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --agentId "ella" \
  --message "检查 30 天内到期的合同，通知相关负责人" \
  --tools "read,exec,message" \
  --announce
```

#### 每天凌晨记忆整理

```bash
openclaw cron add \
  --name "每日记忆整理" \
  --cron "0 3 * * *" \
  --tz "Asia/Shanghai" \
  --session "agent:main" \
  --system-event "整理当天记忆，更新 MEMORY.md，清理过时信息" \
  --wake "now"
```

### 7.4 Cron 管理命令

```bash
# 列出所有任务
openclaw cron list

# 查看任务详情
openclaw cron show <job-id>

# 查看运行历史
openclaw cron runs --id <job-id>

# 立即触发任务（测试用）
openclaw cron run <job-id>

# 暂停/恢复任务
openclaw cron pause <job-id>
openclaw cron resume <job-id>

# 删除任务
openclaw cron remove <job-id>

# 查看日志
openclaw cron logs <job-id>
```

---

## 八、记忆系统与 Dreaming

### 8.1 记忆系统配置

```json5
{
  plugins: {
    entries: {
      "memory-core": {
        enabled: true,
        config: {
          // ========== 梦境配置 ==========
          dreaming: {
            enabled: true,             // 启用梦境功能
            frequency: "0 3 * * *",    // 每天凌晨3点运行
            timezone: "Asia/Shanghai",
            // 梦境日记使用的模型（可选）
            model: "qwen/qwen3.6-plus",
          },

          // ========== 记忆搜索配置 ==========
          memorySearch: {
            enabled: true,
            provider: "qmd", // qmd | local (未来)

            qmd: {
              // 包含默认记忆
              includeDefaultMemory: true,
              // 额外的搜索集合
              extraCollections: [
                { path: "~/Documents/notes", name: "personal-notes" },
              ],
            },
          },

          // ========== 引用格式 ==========
          citations: {
            enabled: true,
            style: "inline", // inline | footnote
          },
        },

        // 子代理权限（用于梦境日记）
        subagent: {
          allowModelOverride: true,
          allowedModels: ["qwen/qwen3.6-plus", "deepseek/deepseek-chat"],
        },
      },
    },
  },
}
```

### 8.2 Dreaming 工作原理

```
┌─────────────────────────────────────────────────────┐
│                    触发条件                           │
│              Cron 每天凌晨 3 点执行                   │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│               Phase 1: Light Sleep                   │
│  - 读取最近的每日记忆 YYYY-MM-DD.md                  │
│  - 分析会话历史中的召回痕迹                          │
│  - 去重、分类、标记候选条目                          │
│  - 计算频率和新鲜度分数                              │
│  输出：候选条目列表 + 初始分数                       │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│               Phase 2: REM Sleep                     │
│  - 识别主题模式和重复出现的想法                      │
│  - 提取概念标签和关联                                │
│  - 生成反思性摘要                                    │
│  - 写入 DREAMS.md 日记                               │
│  输出：主题分析 + 梦境日记                           │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│               Phase 3: Deep Sleep                    │
│  - 综合 6 个维度的分数进行最终排名                   │
│    频率(24%)、相关性(30%)、查询多样性(15%)、        │
│    新鲜度(15%)、巩固度(10%)、概念丰富度(6%)         │
│  - 超过阈值的条目晋升为长期记忆                       │
│  - 追加到 MEMORY.md                                  │
│  输出：新晋升的长期记忆条目                           │
└─────────────────────────────────────────────────────┘
```

### 8.3 梦境评分机制

| 信号 | 权重 | 说明 |
|------|------|------|
| 相关性 (Relevance) | 30% | 检索质量的平均得分，最重要 |
| 频率 (Frequency) | 24% | 短期记忆中出现的次数 |
| 查询多样性 (Query diversity) | 15% | 在多少不同的查询/上下文中出现 |
| 新鲜度 (Recency) | 15% | 时间衰减分数，越新越高 |
| 巩固度 (Consolidation) | 10% | 多日重复出现强度 |
| 概念丰富度 (Conceptual richness) | 6% | 概念标签密度 |

### 8.4 记忆相关命令

```bash
# 查看记忆状态
openclaw memory status
openclaw memory status --deep

# 手动触发梦境（不写入，仅预览）
openclaw memory promote

# 手动触发并写入
openclaw memory promote --apply

# 限制预览数量
openclaw memory promote --limit 10

# 解释某条候选记忆
openclaw memory promote-explain "关键词"
openclaw memory promote-explain "关键词" --json

# 预览 REM 阶段输出
openclaw memory rem-harness
openclaw memory rem-harness --json

# 历史回溯（将旧的笔记加入梦境）
openclaw memory rem-backfill --path memory/2026-04/
openclaw memory rem-backfill --path memory/2026-04/ --stage-short-term

# 回滚回溯操作
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term

# 梦境开关（聊天中）
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

---

## 九、性能优化指南

### 9.1 Token 成本优化

| 优化项 | 配置 | 预期效果 |
|--------|------|---------|
| 图像自动缩放 | `imageMaxDimensionPx: 1200` | 图片 token 减少 50-70% |
| 子代理使用经济型模型 | `subagents.model: "deepseek/deepseek-chat"` | 子任务成本降低 60-80% |
| `continuation-skip` 策略 | `contextInjection: "continuation-skip"` | 连续对话 bootstrap 注入减少 |
| 上下文预算合理设置 | `contextTokens: 200000` | 避免过大的上下文窗口 |
| 会话自动重置 | `session.reset.mode: "daily"` | 每天清空历史，避免无限增长 |

### 9.2 并发与吞吐量优化

```json5
{
  agents: {
    defaults: {
      maxConcurrent: 8,       // 增加并发数（根据模型供应商限制调整）
      timeoutSeconds: 300,    // 合理的超时设置，避免长时间挂起
    },
  },

  cron: {
    maxConcurrentRuns: 4,   // Cron 并发数
  },

  agents: {
    defaults: {
      subagents: {
        maxConcurrent: 8,     // 子代理并发数
        archiveAfterMinutes: 30, // 更快归档，释放资源
      },
    },
  },
}
```

### 9.3 内存优化

```json5
{
  session: {
    // 每日自动重置
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,     // 闲置2小时自动重置
    },

    // 线程绑定超时
    threadBindings: {
      enabled: true,
      idleHours: 24,         // 24小时无活动释放线程
      maxAgeHours: 168,      // 最多保留7天
    },
  },

  // Cron 会话保留
  cron: {
    sessionRetention: "72h", // 由 7 天缩减到 3 天
  },

  // 技能提示预算
  skills: {
    limits: {
      maxSkillsPromptChars: 12000, // 缩减技能列表预算
    },
  },
}
```

### 9.4 模型降级链最佳实践

**推荐配置（三层降级）：**

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "volcengine/ark-code-latest",        // 主力：性能最好
        fallbacks: [
          "qwen/qwen3.6-plus",                         // 第一层降级：性价比高
          "deepseek/deepseek-chat",                    // 第二层降级：成本最低
        ],
      },
    },
  },
}
```

**降级策略原则：**
1. 主模型选**性能最好**的（保证体验）
2. 第一层降级选**性价比最高**的（平衡）
3. 最后一层选**最稳定/成本最低**的（保底）
4. 不同供应商，避免单点故障

---

## 十、完整企业级配置示例

```json5
{
  // ============================================================
  // OpenClaw 企业级配置 v1.0
  // ============================================================

  // ========== 网关配置 ==========
  gateway: {
    mode: "local",
    port: 18789,
    bind: "loopback",
    auth: {
      mode: "token",
      token: "your-strong-token-32-chars-minimum",
      rateLimit: {
        maxAttempts: 10,
        windowMs: 60000,
        lockoutMs: 300000,
        exemptLoopback: true,
      },
    },
    controlUi: {
      enabled: true,
      allowInsecureAuth: true,
    },
    channelHealthCheckMinutes: 5,
    channelStaleEventThresholdMinutes: 30,
    handshakeTimeoutMs: 15000,
  },

  // ========== 模型配置 ==========
  models: {
    mode: "merge",
    providers: {
      qwen: {
        baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1",
        apiKey: "your-qwen-key",
        api: "openai-completions",
        models: [
          { id: "qwen3.6-plus", name: "qwen3.6-plus", contextWindow: 1000000, maxTokens: 65536 },
        ],
      },
      deepseek: {
        baseUrl: "https://api.deepseek.com/v1",
        apiKey: "your-deepseek-key",
        api: "openai-completions",
        models: [
          { id: "deepseek-chat", name: "deepseek-chat", contextWindow: 128000, maxTokens: 4096 },
        ],
      },
      volcengine: {
        baseUrl: "https://ark.cn-beijing.volces.com/api/coding/v3",
        apiKey: "your-ark-key",
        api: "openai-completions",
        models: [
          { id: "ark-code-latest", name: "ark-code-latest", contextWindow: 1000000, maxTokens: 65536 },
        ],
      },
    },
  },

  // ========== 智能体配置 ==========
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: {
        primary: "volcengine/ark-code-latest",
        fallbacks: ["qwen/qwen3.6-plus", "deepseek/deepseek-chat"],
      },
      models: {
        "volcengine/ark-code-latest": { alias: "ark" },
        "qwen/qwen3.6-plus": { alias: "qwen" },
        "deepseek/deepseek-chat": { alias: "deepseek" },
      },
      memorySearch: { enabled: true },
      compaction: { mode: "safeguard" },
      heartbeat: { every: "30m", target: "last" },
      imageMaxDimensionPx: 1200,
      userTimezone: "Asia/Shanghai",
      contextInjection: "continuation-skip",
      bootstrapMaxChars: 12000,
      bootstrapTotalMaxChars: 60000,
      startupContext: {
        enabled: true,
        applyOn: ["new", "reset"],
        dailyMemoryDays: 2,
        maxTotalChars: 2800,
      },
      contextLimits: {
        memoryGetMaxChars: 12000,
        toolResultMaxChars: 16000,
      },
      sandbox: {
        mode: "non-main",
        scope: "agent",
        workspaceAccess: "ro",
        backend: "docker",
      },
      subagents: {
        maxSpawnDepth: 2,
        maxChildrenPerAgent: 5,
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
        model: "deepseek/deepseek-chat",
        thinking: "fast",
        allowAgents: ["ella", "oliver", "aaron", "iris"],
        requireAgentId: true,
      },
      tools: { profile: "coding" },
    },

    list: [
      { id: "main", default: true, name: "Jerry 🦞", tools: { alsoAllow: ["sessions_spawn", "sessions_send", "subagents"] } },
      { id: "ella", name: "Ella 🦊", workspace: "~/.openclaw/agents/ella/workspace", agentDir: "~/.openclaw/agents/ella", skills: ["contract-parse", "oa-approval", "knowledge-base"] },
      { id: "oliver", name: "Oliver 🐘", workspace: "~/.openclaw/agents/oliver/workspace", agentDir: "~/.openclaw/agents/oliver", skills: ["ones-project", "github", "knowledge-base"], tools: { alsoAllow: ["browser"] } },
      { id: "aaron", name: "Aaron 🦉", workspace: "~/.openclaw/agents/aaron/workspace", agentDir: "~/.openclaw/agents/aaron", skills: ["business-report", "data-analysis"], model: "qwen/qwen3.6-plus" },
      { id: "iris", name: "Iris 🐦‍⬛", workspace: "~/.openclaw/agents/iris/workspace", agentDir: "~/.openclaw/agents/iris", model: "deepseek/deepseek-chat", skills: ["email-management", "system-monitor"], sandbox: { mode: "all", scope: "session", workspaceAccess: "none" }, tools: { profile: "minimal", allow: ["read", "exec", "memory_search", "message"] } },
    ],
  },

  // ========== 路由绑定 ==========
  bindings: [
    { agentId: "main", match: { channel: "wecom" } },
    { agentId: "main", match: { channel: "webchat" } },
    { agentId: "ella", match: { channel: "wecom", peer: { kind: "group", id: "contract-group" } } },
    { agentId: "oliver", match: { channel: "wecom", peer: { kind: "group", id: "pm-group" } } },
  ],

  // ========== 会话管理 ==========
  session: {
    dmScope: "per-channel-peer",
    reset: { mode: "daily", atHour: 4, idleMinutes: 120 },
    threadBindings: { enabled: true, idleHours: 24, maxAgeHours: 168 },
  },

  // ========== 消息配置 ==========
  messages: {
    visibleReplies: "message_tool",
    groupChat: { visibleReplies: "message_tool", requireMention: true },
  },

  // ========== Cron 配置 ==========
  cron: {
    enabled: true,
    maxConcurrentRuns: 4,
    sessionRetention: "168h",
    runLog: { maxBytes: "50mb", keepLines: 10000 },
  },

  // ========== Webhook 配置 ==========
  hooks: {
    enabled: true,
    token: "your-webhook-secret",
    path: "/hooks",
    allowedAgentIds: ["main", "ella", "oliver", "aaron", "iris"],
    mappings: [
      { match: { path: "oa" }, action: "agent", agentId: "ella", deliver: true },
      { match: { path: "github" }, action: "wake", mode: "now" },
    ],
  },

  // ========== 工具配置 ==========
  tools: {
    profile: "coding",
  },

  // ========== 技能配置 ==========
  skills: {
    load: {
      extraDirs: ["/opt/openclaw/company-skills"],
      watch: true,
    },
  },

  // ========== 插件配置 ==========
  plugins: {
    entries: {
      "memory-core": {
        enabled: true,
        config: {
          dreaming: {
            enabled: true,
            frequency: "0 3 * * *",
            timezone: "Asia/Shanghai",
            model: "qwen/qwen3.6-plus",
          },
        },
        subagent: {
          allowModelOverride: true,
          allowedModels: ["qwen/qwen3.6-plus"],
        },
      },
      "wecom-openclaw-plugin": { enabled: true },
    },
    allow: ["memory-core", "wecom-openclaw-plugin"],
  },

  // ========== 通道配置 ==========
  channels: {
    wecom: {
      enabled: true,
      botId: "your-bot-id",
      secret: "your-bot-secret",
      dmPolicy: "allowlist",
      groupPolicy: "allowlist",
      allowFrom: ["user-1", "user-2", "user-3"],
    },
    webchat: { enabled: true },
  },

  // ========== 向导配置 ==========
  wizard: {
    lastRunAt: "2026-05-07T00:00:00.000Z",
    lastRunVersion: "2026.4.15",
    lastRunCommand: "doctor",
    lastRunMode: "local",
  },
  meta: {
    lastTouchedVersion: "2026.4.15",
    lastTouchedAt: "2026-05-07T00:00:00.000Z",
  },
}
```

---

## 十一、故障排查

### 11.1 配置验证

```bash
# 基础诊断
openclaw doctor

# 自动修复（配置文件格式错误、缺失字段等）
openclaw doctor --fix

# 详细诊断信息
openclaw doctor --verbose

# 检查特定配置路径
openclaw config get agents.defaults.model
openclaw config get agents.list.0.name
```

### 11.2 网关与通道诊断

```bash
# 网关状态
openclaw gateway status

# 重启网关
openclaw gateway restart

# 通道状态
openclaw channels status
openclaw channels status --probe

# 通道登录
openclaw channels login --channel wecom
```

### 11.3 智能体与会话诊断

```bash
# 智能体列表
openclaw agents list
openclaw agents list --bindings

# 会话列表
openclaw sessions list

# 重置会话
openclaw sessions reset <session-key>

# 子代理状态
/subagents list
```

### 11.4 日志查看

```bash
# 实时日志
openclaw logs -f

# 最近 N 行
openclaw logs -n 100

# 日志位置
# macOS/Linux: /tmp/openclaw/openclaw-YYYY-MM-DD.log
# Windows: %TEMP%\openclaw\openclaw-YYYY-MM-DD.log
```

### 11.5 常见问题速查

#### ❌ 配置验证失败
```bash
openclaw doctor --fix
```
- 检查 JSON 格式（逗号、引号）
- 使用 JSON5 特性要确保 OpenClaw 版本支持
- 备份配置文件在修改前

#### ❌ 模型调用失败
- 检查 API Key 是否正确
- 检查网络连接和代理
- 检查供应商服务状态
- 检查 fallback 配置是否正确
- 查看 `auth-profiles.json` 权限

#### ❌ 通道连接失败
- 检查凭证（token、secret）
- 检查防火墙和网络策略
- 查看通道日志：`openclaw channels status`
- 尝试重新登录/配对

#### ❌ 子代理创建失败
- 检查 `subagents.maxSpawnDepth` 配置
- 检查 `subagents.allowAgents` 白名单
- 检查父智能体是否有 `sessions_spawn` 工具权限
- 检查并发数限制 `maxConcurrent`

#### ❌ 沙箱命令执行失败
- 确认 Docker 正在运行：`docker ps`
- 检查目录挂载路径是否存在
- 检查文件权限
- 查看沙箱日志

---

## 十二、最佳实践清单

### ✅ 安全第一
- [ ] 生产环境启用沙箱 `mode: "non-main"` 或更高
- [ ] Gateway 绑定 `loopback`，不要暴露公网
- [ ] 使用强 Token，至少 32 字符
- [ ] 通道使用白名单模式，不要用 `open`
- [ ] 敏感操作（OA、审批）要求二次确认
- [ ] 工作区使用私有 Git 仓库

### ✅ 高可用架构
- [ ] 配置至少 2 层模型 fallback，不同供应商
- [ ] 关键通道有备用方案（如企业微信 + 邮件）
- [ ] Cron 任务有失败告警和重试机制
- [ ] 网关有自动重启机制（systemd 等）
- [ ] 配置有版本控制，可回滚

### ✅ 成本优化
- [ ] 子代理使用更经济的模型
- [ ] 启用图片自动缩放 `imageMaxDimensionPx`
- [ ] 启用 `contextInjection: "continuation-skip"`
- [ ] 会话每日自动重置
- [ ] 定期归档历史会话

### ✅ 性能与体验
- [ ] 心跳间隔合理（30分钟合适）
- [ ] 子代理并发数根据需求调整（4-8）
- [ ] 常用任务 Cron 化，自动化执行
- [ ] 工作区 bootstrap 文件简洁，不超过截断阈值
- [ ] 技能按需加载，不启用不需要的技能

### ✅ 可维护性
- [ ] 配置文件有注释，关键配置有说明
- [ ] 工作区文件结构清晰，README 完整
- [ ] 自定义技能有完整的文档和测试用例
- [ ] 有定期备份机制（配置、记忆、会话）
- [ ] 日志轮转和清理策略，避免磁盘占满

### ✅ 企业级特性
- [ ] 启用梦境记忆整理功能
- [ ] 各专业智能体有独立工作区和状态
- [ ] 完整的路由绑定策略
- [ ] Webhook 接入外部系统事件
- [ ] 审计日志和操作记录

---

*本指南基于 OpenClaw 2026.4.15 官方文档整理，持续更新中...* 🦞
```

<seed:tool_call><function name="exec"><parameter name="command" string="true">cd ~/.openclaw/workspace && wc -l "OpenClaw_进阶配置指南_v1.1.md" && echo "文件创建完成"