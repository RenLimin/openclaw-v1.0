# OpenClaw 配置文件关联关系与使用规则 v1.0

> **基于官方文档 2026.4.15 深度整理**
> **目标：清晰理解配置文件之间的关系、优先级与使用规则**
> **最后更新：2026-05-07**

---

## 目录

1. [配置文件全景图](#一配置文件全景图)
2. [配置文件详细说明](#二配置文件详细说明)
3. [优先级与覆盖规则](#三优先级与覆盖规则)
4. [配置热重载机制](#四配置热重载机制)
5. [多智能体配置关联](#五多智能体配置关联)
6. [典型问题与故障排查](#六典型问题与故障排查)
7. [配置最佳实践](#七配置最佳实践)
8. [完整关系图谱](#八完整关系图谱)

---

## 一、配置文件全景图

### 1.1 配置文件分类体系

```
OpenClaw 配置文件可以分为 5 大类：

┌─────────────────────────────────────────────────────────────────┐
│                     配置文件 5 层架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔹 第 1 层 - 核心配置 (Core)                                   │
│     ~/.openclaw/openclaw.json                                  │
│     └─ 网关、模型、智能体、通道、工具、技能、Cron 等所有全局配置  │
│                                                                 │
│  🔹 第 2 层 - 工作区配置 (Workspace Bootstrap)                  │
│     ~/.openclaw/workspace/                                      │
│     ├─ AGENTS.md         # 智能体行为规范                       │
│     ├─ SOUL.md           # 人格与个性                           │
│     ├─ USER.md           # 用户信息与偏好                        │
│     ├─ IDENTITY.md       # 智能体身份标识                        │
│     ├─ TOOLS.md          # 工具使用规范                         │
│     ├─ HEARTBEAT.md      # 心跳任务清单                         │
│     ├─ MEMORY.md         # 长期记忆（可选）                      │
│     └─ BOOTSTRAP.md      # 初始化引导（仅首次）                  │
│                                                                 │
│  🔹 第 3 层 - 技能配置 (Skills)                                 │
│     ~/.openclaw/skills/                                         │
│     ~/.openclaw/workspace/skills/                               │
│     └─ <skill-name>/SKILL.md                                    │
│                                                                 │
│  🔹 第 4 层 - 智能体私有配置 (Per-Agent)                        │
│     ~/.openclaw/agents/<agent-id>/                              │
│     ├─ workspace/        # 独立工作区（含独立 bootstrap 文件）  │
│     ├─ agent/            # 认证与状态                           │
│     │   └─ auth-profiles.json  # 模型认证凭证                  │
│     └─ sessions/        # 会话历史与状态                        │
│                                                                 │
│  🔹 第 5 层 - 运行时状态 (Runtime State)                        │
│     ~/.openclaw/                                                 │
│     ├─ credentials/     # 通道凭证（WhatsApp/Telegram 等）     │
│     ├─ cron/            # Cron 任务状态与日志                   │
│     ├─ logs/            # 运行日志                              │
│     ├─ memory/          # 每日记忆与梦境状态                     │
│     └─ plugins/         # 插件配置与数据                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 配置文件加载顺序

```
系统启动时的加载顺序（后面的覆盖前面的）：

1. 🔴 内置默认值（编译在二进制中）
   ↓
2. 🟠 环境变量（OPENCLAW_* 前缀）
   ↓
3. 🟡 ~/.openclaw/openclaw.json（主配置文件）
   ↓
4. 🟢 agents.defaults.*（智能体默认配置）
   ↓
5. 🔵 agents.list[].*（单个智能体配置）
   ↓
6. 🟣 工作区 bootstrap 文件（AGENTS.md、SOUL.md 等）
   ↓
7. 🟤 技能 SKILL.md（运行时按需加载）
```

---

## 二、配置文件详细说明

### 2.1 openclaw.json - 核心配置文件

#### 文件位置
```
~/.openclaw/openclaw.json
```

#### 作用
系统唯一的核心配置文件，包含所有全局配置。

#### 格式
JSON5 格式（支持注释、尾随逗号、单引号）。

#### 根节点说明

| 根节点 | 作用 | 热重载 |
|--------|------|---------|
| `gateway` | 网关服务配置 | ✅ 部分支持 |
| `models` | 模型提供商与模型列表 | ✅ |
| `agents` | 智能体默认配置与列表 | ✅ |
| `session` | 会话管理配置 | ✅ |
| `messages` | 消息发送策略 | ✅ |
| `cron` | 定时任务引擎配置 | ✅ |
| `hooks` | Webhook 配置 | ✅ |
| `tools` | 工具权限与策略 | ✅ |
| `skills` | 技能加载与配置 | ✅ |
| `plugins` | 插件启用与配置 | ❌ 需重启 |
| `channels` | 消息通道配置 | ✅ 部分支持 |
| `mcp` | MCP 服务器定义 | ✅ |
| `wizard` | 向导状态（自动维护） | - |
| `meta` | 元数据（自动维护） | - |

#### 关键注意事项
1. **格式校验严格**：JSON 语法错误会导致网关无法启动
2. **Schema 验证**：所有字段必须符合官方 Schema，未知字段会报错
3. **敏感信息**：API Key、Token 等直接存储在文件中，注意权限保护
4. **备份重要**：修改前建议备份，可使用 `openclaw doctor --fix` 恢复
5. **版本兼容**：升级 OpenClaw 版本后可能需要新增配置字段

---

### 2.2 工作区 Bootstrap 文件详解

#### 文件位置
```
~/.openclaw/workspace/          # 主智能体工作区
~/.openclaw/agents/<id>/workspace/  # 其他智能体独立工作区
```

#### 加载机制
```
每次智能体运行前注入到系统提示词中：

┌───────────────────────────────────────────────┐
│         系统提示词构建流程                      │
├───────────────────────────────────────────────┤
│                                               │
│  1. 读取 AGENTS.md    → 行为规范              │
│  2. 读取 SOUL.md      → 人格个性              │
│  3. 读取 USER.md      → 用户偏好              │
│  4. 读取 IDENTITY.md  → 智能体身份            │
│  5. 读取 TOOLS.md     → 工具使用规范          │
│  6. 读取 MEMORY.md    → 长期记忆（可选）      │
│                                               │
│  ──────────────────────────────────────       │
│  总字符限制：bootstrapTotalMaxChars           │
│  默认值：60,000 字符                          │
│  超过部分截断并警告                            │
│                                               │
└───────────────────────────────────────────────┘
```

#### 各文件具体作用与优先级

| 文件名 | 注入时机 | 必选 | 作用 | 典型大小 |
|--------|---------|------|------|---------|
| **AGENTS.md** | 每次运行 | ✅ | 最高优先级的行为规范，会被严格遵守 | 2-5 KB |
| **SOUL.md** | 每次运行 | ✅ | 定义智能体人格、语气、沟通风格 | 1-3 KB |
| **USER.md** | 每次运行 | ✅ | 用户信息、偏好、习惯、联系方式 | 1-2 KB |
| **IDENTITY.md** | 每次运行 | ✅ | 智能体自我介绍、职责范围 | 0.5-1 KB |
| **TOOLS.md** | 每次运行 | ✅ | 工具使用原则、安全规范、SOP | 2-4 KB |
| **HEARTBEAT.md** | 仅心跳运行 | ❌ | 心跳任务清单、自动化流程 | 1-3 KB |
| **MEMORY.md** | 每次运行 | ❌ | 长期记忆、重要决策、经验教训 | 5-20 KB |
| **BOOTSTRAP.md** | 仅首次 | ❌ | 初始化引导（创建后可删除） | - |

#### 上下文注入策略配置

```json5
{
  agents: {
    defaults: {
      // 注入策略：always | continuation-skip | never
      contextInjection: "continuation-skip",

      // 单个文件最大字符（默认 12000）
      bootstrapMaxChars: 12000,

      // 所有文件总字符上限（默认 60000）
      bootstrapTotalMaxChars: 60000,

      // 截断警告策略：off | once | always
      bootstrapPromptTruncationWarning: "once",

      // 跳过 bootstrap 文件创建（自己维护时）
      skipBootstrap: false,

      // 跳过特定的可选文件
      skipOptionalBootstrapFiles: ["SOUL.md", "USER.md"],
    },
  },
}
```

#### 注入策略详解

| 策略 | 说明 | 适用场景 | Token 节省 |
|------|------|---------|-----------|
| `always` | 每次运行都完整注入所有 bootstrap 文件 | 开发调试、需要严格一致性 | 0%（基准） |
| `continuation-skip` | ⭐ 推荐：用户直接回复的"连续对话"跳过注入，其他情况都注入 | 生产环境（最佳平衡） | 约 30-50% |
| `never` | 完全禁用 bootstrap 注入 | 极端 token 敏感场景、自有上下文管理 | 约 80-90% |

---

### 2.3 SKILL.md - 技能配置文件

#### 文件位置
```
# 按优先级从高到低
1. ~/.openclaw/workspace/skills/<skill-name>/SKILL.md    # 当前工作区（最高优先级）
2. ~/.openclaw/workspace/.agents/skills/<skill-name>/SKILL.md
3. ~/.agents/skills/<skill-name>/SKILL.md
4. ~/.openclaw/skills/<skill-name>/SKILL.md              # 系统级共享
5. skills.load.extraDirs 配置的额外目录
```

#### 加载机制

```
技能加载 = 前端元数据解析 + 后端条件检查 + 运行时注入

┌─────────────────────────────────────────────┐
│         技能加载检查流程                     │
├─────────────────────────────────────────────┤
│                                             │
│  1. 读取 SKILL.md 的 YAML frontmatter       │
│     ├─ name: 技能唯一标识                    │
│     ├─ description: 描述                     │
│     └─ metadata.openclaw: 元数据             │
│                                             │
│  2. 依赖检查                                │
│     ├─ requires.bins → 检查二进制存在        │
│     ├─ requires.env → 检查环境变量           │
│     └─ requires.config → 检查配置项          │
│                                             │
│  3. 白名单检查                              │
│     ├─ skills.allowBundled（内置技能）       │
│     ├─ agents.defaults.skills（默认）        │
│     └─ agents.list[].skills（单个智能体）    │
│                                             │
│  4. 启用检查                                │
│     └─ skills.entries.<name>.enabled        │
│                                             │
│  5. 运行时注入（字符限制 maxSkillsPromptChars）│
│                                             │
└─────────────────────────────────────────────┘
```

#### 元数据字段说明

```yaml
---
# ========== 基础字段（必填） ==========
name: contract-parse                    # 技能唯一 ID（kebab-case）
description: 合同文档智能解析与条款提取

# ========== 调用控制 ==========
user-invocable: true                    # 用户是否可通过 /skill 手动调用
disable-model-invocation: false         # 禁用模型调用（纯工具技能）
command-dispatch: tool                  # direct 直接执行 | tool 通过工具分发
command-tool: exec                      # 分发到的具体工具
command-arg-mode: raw                   # raw（原始参数）

# ========== 依赖与条件 ==========
metadata:
  openclaw:
    requires:
      bins: ["pdftotext", "tesseract"]  # 需要的二进制工具
      env: ["OCR_API_KEY"]              # 需要的环境变量
      config: ["skills.entries.contract-parse.enabled"]  # 依赖的配置项
    primaryEnv: OCR_API_KEY             # 主环境变量（用于配置 UI）
---

# 技能使用说明（Markdown，注入到系统提示词）
```

---

### 2.4 智能体私有配置

#### 目录结构
```
~/.openclaw/agents/<agent-id>/
├── workspace/               # 独立工作区
│   ├── AGENTS.md           # 可独立配置，继承 main + 覆盖
│   ├── SOUL.md             # 可独立配置
│   ├── USER.md             # 可独立配置
│   ├── ...
│   └── skills/             # 该智能体私有的技能
│
├── agent/                  # 智能体状态
│   └── auth-profiles.json  # 独立的模型认证凭证（重要！）
│
└── sessions/               # 独立的会话历史
    ├── sessions.json       # 会话索引
    └── *.jsonl            # 具体会话内容
```

#### 关键机制：认证凭证隔离

```json5
// auth-profiles.json 的作用
{
  // 每个智能体可以有独立的 API Key
  // 例如：ella 用专门的 OCR 模型 Key
  //       oliver 用专门的 ONES API Key
  //       iris 用专门的邮件 Key

  "qwen": {
    "apiKey": "sk-ella-special-key-for-ocr",  // ella 专用
    "baseUrl": "..."
  },
  "ones-api": {
    "apiKey": "sk-oliver-special-key"         // oliver 专用
  }
}
```

**重要：** 这意味着不同智能体可以使用不同的供应商账号，实现成本和权限的精细化控制。

---

### 2.5 运行时状态文件

| 文件 | 作用 | 手动修改 | 备份建议 |
|------|------|---------|---------|
| `credentials/<channel>/<account>/` | 通道登录凭证（WhatsApp 等） | ❌ 不要修改 | ✅ 必须备份（重新登录会丢失历史） |
| `cron/jobs.json` | Cron 任务定义 | ⚠️ 建议用 CLI 修改 | ✅ 备份 |
| `cron/jobs-state.json` | Cron 运行状态 | ❌ 系统维护 | ⭕ 可选 |
| `cron/runs/<job-id>.jsonl` | Cron 运行日志 | ❌ 系统维护 | ⭕ 可选 |
| `memory/YYYY-MM-DD.md` | 每日记忆 | ✅ 可编辑 | ✅ 建议备份 |
| `memory/.dreams/` | 梦境索引与状态 | ❌ 系统维护 | ⭕ 可选 |
| `memory/dreaming/` | 分阶段梦境报告 | ✅ 可查看 | ⭕ 可选 |
| `agents/<id>/sessions/` | 会话历史 | ⚠️ 谨慎修改 | ✅ 重要数据备份 |

---

## 三、优先级与覆盖规则

### 3.1 配置覆盖总原则

```
核心原则："越具体，优先级越高"

┌─────────────────────────────────────────────────────────┐
│                    优先级金字塔                           │
│                                                         │
│        🔺 最高优先级                                     │
│       ┌─────────────────────────────────────┐          │
│       │  1. 命令行参数 (--port, --mode 等)  │          │
│       ├─────────────────────────────────────┤          │
│       │  2. 环境变量 (OPENCLAW_*)          │          │
│       ├─────────────────────────────────────┤          │
│       │  3. openclaw.json 精确配置          │          │
│       │     (agents.list[x].field)          │          │
│       ├─────────────────────────────────────┤          │
│       │  4. openclaw.json 默认配置          │          │
│       │     (agents.defaults.field)         │          │
│       ├─────────────────────────────────────┤          │
│       │  5. 工作区 bootstrap 文件           │          │
│       │     (AGENTS.md, SOUL.md 等)        │          │
│       ├─────────────────────────────────────┤          │
│       │  6. 内置默认值                      │          │
│       └─────────────────────────────────────┘          │
│        🔻 最低优先级                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 智能体配置：defaults vs list[]

```
配置继承关系示例：

┌─────────────────────────────────────────────────────────────┐
│  agents.defaults.* (基类)                                   │
│  ├─ model.primary = "qwen/qwen3.6-plus"                    │
│  ├─ heartbeat.every = "30m"                                 │
│  ├─ sandbox.mode = "non-main"                              │
│  └─ skills = ["github", "knowledge-base"]                  │
│                              │                              │
│           ┌──────────────────┼───────────────┐             │
│           ▼                  ▼               ▼             │
│  ┌──────────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ agents.list[0]   │  │ agents.list[1]│  │ agents.list[2]│ │
│  │ id: "main"       │  │ id: "ella"    │  │ id: "iris"   │ │
│  │ (继承所有默认值) │  │ model: ark   │  │ sandbox: all │ │
│  │                  │  │ skills: +oa  │  │ skills: []   │ │
│  └──────────────────┘  └──────────────┘  └───────────────┘ │
│        无覆盖                部分覆盖          完全覆盖     │
│                                                             │
└─────────────────────────────────────────────────────────────┘

规则：
  - 不设置的字段 = 继承 defaults
  - 设置了字段 = 完全覆盖（注意：对象是整体覆盖，不是 merge！）
  - skills 数组：不继承 = 完全替换（重要！）
```

**⚠️ 重要陷阱：**

```json5
{
  agents: {
    defaults: {
      skills: ["github", "knowledge-base"],
      model: { primary: "qwen/qwen3.6-plus", fallbacks: ["deepseek"] }
    },
    list: [
      {
        id: "ella",
        // ❌ 错误：skills 被完全替换，只剩下 oa-approval
        // "github", "knowledge-base" 丢失了！
        skills: ["oa-approval"]

        // ✅ 正确：需要完整列出
        skills: ["github", "knowledge-base", "oa-approval"]
      },
      {
        id: "oliver",
        model: { primary: "volcengine/ark-code-latest" }
        // ❌ 危险！model.fallbacks 也丢失了
        // 需要完整写出 model 对象
      }
    ]
  }
}
```

**覆盖类型总结：**

| 字段类型 | 覆盖方式 | 示例 |
|---------|---------|------|
| 简单类型（字符串、数字、布尔） | 直接替换 | `heartbeat.every` |
| 数组 | **完全替换**（不合并） | `skills`, `fallbacks` |
| 对象 | **完全替换**（不 merge） | `model`, `sandbox` |
| 嵌套对象字段 | 也是完全替换 | `model.primary` 会覆盖整个 model 对象 |

### 3.3 技能优先级与覆盖

```
技能冲突处理：同名技能，高优先级路径覆盖低优先级

优先级从高到低：

1. <workspace>/skills/<name>/SKILL.md          # 当前工作区
   ↓
2. <workspace>/.agents/skills/<name>/SKILL.md  # 项目级
   ↓
3. ~/.agents/skills/<name>/SKILL.md            # 用户级
   ↓
4. ~/.openclaw/skills/<name>/SKILL.md          # 系统级
   ↓
5. 内置捆绑技能（OpenClaw 自带）
   ↓
6. skills.load.extraDirs 配置的额外目录        # 最低

实际效果：你可以在自己的工作区放一个同名的 SKILL.md
         来"重载"系统内置的技能，实现自定义行为
```

### 3.4 工具权限叠加规则

```
工具权限检查顺序（所有条件都必须满足）：

1. tools.profile (基础配置文件) → full / coding / messaging / minimal
   ↓
2. tools.allow (全局白名单)
   ↓
3. tools.deny (全局黑名单，优先于 allow)
   ↓
4. agents.defaults.tools.allow (智能体默认)
   ↓
5. agents.list[].tools.allow (单个智能体，优先级最高)
   ↓
6. tools.byProvider (按模型提供商限制)
   ↓
7. 🔒 沙箱权限检查（最后一道防线）
```

**示例：**

```json5
{
  tools: {
    profile: "coding",              // 基础：文件 + 执行 + Web
    deny: ["browser"],              // 全局禁用浏览器
    alsoAllow: ["sessions_spawn"],  // 额外允许子代理
  },

  agents: {
    list: [
      {
        id: "ella",
        tools: {
          alsoAllow: ["browser"],   // ✅ ella 可以使用浏览器
        }                            // 覆盖了全局的 deny
      },
      {
        id: "iris",
        tools: {
          deny: ["exec"],           // ❌ iris 额外禁用 exec
        }                            // 即使 coding profile 包含 exec
      }
    ]
  }
}
```

---

## 四、配置热重载机制

### 4.1 热重载支持矩阵

| 配置区域 | 热重载支持 | 说明 |
|---------|-----------|------|
| `agents.defaults.*` | ✅ 完全支持 | 修改后下次智能体运行生效 |
| `agents.list[].*` | ✅ 完全支持 | 对已有会话的智能体下次运行生效 |
| `models.providers.*` | ✅ 完全支持 | 下次模型调用生效 |
| `skills.load.*` | ✅ 完全支持 | 下次技能加载生效 |
| `skills.entries.*` | ✅ 完全支持 | 下次技能加载生效 |
| `tools.*` | ✅ 完全支持 | 下次工具调用生效 |
| `session.*` | ✅ 完全支持 | 新会话立即生效 |
| `messages.*` | ✅ 完全支持 | 下次消息发送生效 |
| `cron.*` | ✅ 完全支持 | 下次调度生效 |
| `hooks.*` | ✅ 完全支持 | 下次 Webhook 调用生效 |
| `mcp.*` | ✅ 完全支持 | 下次 MCP 连接生效 |
| `gateway.*` | ⚠️ 部分支持 | port、bind 等需要重启 |
| `channels.*` | ⚠️ 部分支持 | 部分通道需要重新登录 |
| `plugins.*` | ❌ 不支持 | 必须重启网关 |
| `plugins.entries.*.config` | ✅ 大部分支持 | 插件自身支持热配置 |

### 4.2 热重载触发方式

```
触发配置热重载的 4 种方式：

┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. 📁 文件监听（默认开启）                                  │
│     修改 ~/.openclaw/openclaw.json 后自动检测               │
│     延迟：~1-2 秒（文件系统事件 + debounce）                │
│                                                             │
│  2. 💻 CLI 触发                                             │
│     openclaw config reload                                  │
│     立即重载，适合脚本自动化                                │
│                                                             │
│  3. 🌐 Control UI                                           │
│     Config 页面点击"保存并重载"按钮                         │
│                                                             │
│  4. 🔧 Gateway 工具                                         │
│     从智能体内部调用 gateway.config.patch 热更新           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 热重载验证

修改配置后，通过以下方式验证是否生效：

```bash
# 1. 查看当前配置值
openclaw config get agents.defaults.heartbeat.every

# 2. 查看智能体状态
openclaw agents list

# 3. 查看网关状态
openclaw gateway status

# 4. 检查 doctor 输出（确认无配置错误）
openclaw doctor

# 5. 查看日志确认重载事件
openclaw logs | grep "config"
```

### 4.4 热重载的局限性

⚠️ **重要注意事项：**

1. **运行中的子代理不受影响**
   - 已经 spawn 的子代理会继续使用旧配置
   - 新 spawn 的子代理才会使用新配置

2. **运行中的 Cron 任务不受影响**
   - 正在执行的 Cron 任务继续使用旧配置
   - 下次调度的任务使用新配置

3. **已连接的通道会话**
   - 已建立的连接继续使用旧参数
   - 新消息/新连接使用新配置

4. **插件相关的所有变更**
   - 启用/禁用插件、修改插件配置 → **必须重启**

---

## 五、多智能体配置关联

### 5.1 多智能体完整关联图

```
┌─────────────────────────────────────────────────────────────────────┐
│                      多智能体配置关联关系                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  openclaw.json                                                      │
│  ├─ agents.defaults.*  ───────────┐                                 │
│  │                                ↓ 继承                           │
│  ├─ agents.list[0].main ────→ 主工作区 ~/.openclaw/workspace/      │
│  │     (default: true)               ├─ AGENTS.md                   │
│  │                                    ├─ SOUL.md                     │
│  │                                    ├─ ...                        │
│  │                                    └─ skills/                   │
│  │                                                               │
│  ├─ agents.list[1].ella ────→ 独立工作区                           │
│  │     ├─ workspace: ~/agents/ella/workspace/                      │
│  │     ├─ agentDir: ~/agents/ella/ ←──────┐                       │
│  │     │     └─ auth-profiles.json         │ 独立认证              │
│  │     └─ sandbox: 配置                    │                       │
│  │                                         │                       │
│  ├─ agents.list[2].oliver ──→ 独立工作区  │                       │
│  │     ├─ workspace: ~/agents/oliver/workspace/                   │
│  │     └─ agentDir: ~/agents/oliver/ ←────┤                       │
│  │                                         │                       │
│  └─ bindings[] ────────────────→ 路由规则                         │
│       ├─ match: channel + peer                                 │
│       └→ route to agentId                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 bindings 路由匹配优先级

```
路由匹配规则："最具体的规则胜出"

┌─────────────────────────────────────────────────────────┐
│                    匹配优先级（高→低）                   │
│                                                         │
│  1. peer.id + channel + accountId  ⭐ 最精确            │
│  2. peer.id + channel                                   │
│  3. peer.kind (group/direct) + channel                  │
│  4. accountId + channel                                 │
│  5. channel only（整通道默认）                          │
│  6. 无匹配 → 使用 default=true 的智能体                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**示例：**

```json5
{
  bindings: [
    // 规则 1: 法务部门群 → ella
    { agentId: "ella", match: { channel: "wecom", peer: { id: "legal-group" } } },

    // 规则 2: Rex 的私聊 → main
    { agentId: "main", match: { channel: "wecom", peer: { kind: "direct", id: "rex" } } },

    // 规则 3: 其他所有私聊 → main（兜底）
    { agentId: "main", match: { channel: "wecom", peer: { kind: "direct" } } },

    // 规则 4: 企业微信的所有其他消息 → main
    { agentId: "main", match: { channel: "wecom" } },
  ],
}
```

### 5.3 智能体间的资源共享与隔离

| 资源 | 共享/隔离 | 说明 |
|------|----------|------|
| 模型认证 | ⚠️ 默认共享，可隔离 | 默认使用 main 的 auth-profiles.json；设置 agentDir 后可独立 |
| 工作区文件 | ❌ 完全隔离 | 每个智能体有独立的 workspace 目录 |
| 技能 | ✅ 可共享 + 可私有 | 按技能路径优先级加载，也可在私有 workspace/skills 放私有技能 |
| 会话历史 | ❌ 完全隔离 | 每个智能体的 sessions 目录独立 |
| 通道连接 | ✅ 共享 | 通道是全局的，消息路由到不同智能体 |
| Cron 任务 | ⚠️ 独立运行 | Cron 的 --agentId 指定哪个智能体运行 |
| 子代理 | ⚠️ 半隔离 | 子代理归属父智能体，但可跨智能体创建（需配置） |
| 沙箱容器 | ✅ 独立 | scope=agent 时每个智能体一个容器 |
| 记忆 | ❌ 完全隔离 | 每个智能体的记忆独立存储和整理 |

---

## 六、典型问题与故障排查

### 6.1 配置相关常见问题

#### ❌ 问题 1：修改了配置但没生效
**可能原因：**
1. 需要重启网关（plugins、gateway.port 等）
2. 热重载有延迟（通常 1-2 秒）
3. 配置写在了错误的位置（defaults vs list[]）
4. JSON 语法错误，导致整个配置加载失败回退

**排查步骤：**
```bash
# 1. 先检查配置是否有语法错误
openclaw doctor

# 2. 检查实际生效的配置值
openclaw config get agents.list.0.name

# 3. 如果 doctor 报错，尝试自动修复
openclaw doctor --fix

# 4. 仍不行，手动重启
openclaw gateway restart
```

#### ❌ 问题 2：智能体的技能不见了
**可能原因：**
- 配置了 `agents.list[].skills`，但没列全所有需要的技能
- **注意：skills 数组是完全覆盖，不是追加！**

**解决：**
```json5
{
  agents: {
    defaults: {
      skills: ["github", "knowledge-base"]
    },
    list: [
      {
        id: "ella",
        // ❌ 错误：丢失了 github 和 knowledge-base
        skills: ["oa-approval"]

        // ✅ 正确：完整列出
        skills: ["github", "knowledge-base", "oa-approval"]
      }
    ]
  }
}
```

#### ❌ 问题 3：模型 fallback 不工作
**可能原因：**
- `fallbacks` 写在了错误的层级
- 模型 ID 格式不对（需要 `provider/model` 格式）

**正确格式：**
```json5
{
  agents: {
    defaults: {
      model: {
        primary: "volcengine/ark-code-latest",
        // ✅ 正确：完整的 provider/model 格式
        fallbacks: ["qwen/qwen3.6-plus", "deepseek/deepseek-chat"]
      }
    }
  }
}
```

#### ❌ 问题 4：AGENTS.md 的修改没有生效
**可能原因：**
1. `contextInjection: "continuation-skip"`，连续对话跳过注入
2. 会话还在使用旧的上下文缓存
3. 文件超过了 `bootstrapMaxChars` 被截断

**验证：**
```bash
# 1. 检查注入策略配置
openclaw config get agents.defaults.contextInjection

# 2. 重置会话（会重新加载 bootstrap）
# 聊天中执行 /reset

# 3. 检查文件大小
wc -c ~/.openclaw/workspace/AGENTS.md
# 默认单文件限制 12KB，总限制 60KB
```

### 6.2 诊断工具命令清单

```bash
# ========== 配置诊断 ==========
openclaw doctor                  # 全面诊断 + 自动修复建议
openclaw doctor --fix            # 自动修复可修复的问题
openclaw doctor --verbose        # 详细诊断输出

# ========== 配置查看 ==========
openclaw config get <path>       # 查看特定配置路径
openclaw config schema           # 输出完整的 JSON Schema

# 示例：
openclaw config get agents.defaults.model.primary
openclaw config get agents.list
openclaw config get skills.load.extraDirs

# ========== 智能体状态 ==========
openclaw agents list             # 列出所有智能体
openclaw agents list --bindings  # 列出智能体 + 路由绑定

# ========== 技能状态 ==========
openclaw skills list             # 列出已加载的所有技能
openclaw skills show <name>      # 查看技能详情

# ========== 网关状态 ==========
openclaw gateway status          # 网关运行状态
openclaw status --deep           # 深度健康检查
openclaw health --json           # 结构化健康状态

# ========== 日志查看 ==========
openclaw logs -n 100            # 最近 100 行日志
openclaw logs -f                # 实时跟踪日志

# 搜索配置相关日志
openclaw logs | grep -i "config\|reload\|error"
```

---

## 七、配置最佳实践

### 7.1 Git 版本控制

```
✅ 建议纳入 Git 版本控制的文件：

~/.openclaw/
├── openclaw.json              ✅ 核心配置（脱敏！）
├── workspace/                 ✅ 所有工作区文件
│   ├── AGENTS.md
│   ├── SOUL.md
│   ├── USER.md
│   ├── TOOLS.md
│   ├── HEARTBEAT.md
│   ├── MEMORY.md
│   └── skills/               ✅ 自定义技能
│
├── skills/                    ✅ 系统级共享技能
│
└── agents/<id>/workspace/     ✅ 各智能体独立工作区文件


❌ 绝对不要提交到 Git 的文件：

~/.openclaw/
├── credentials/              ❌ 通道登录凭证（隐私）
├── agents/*/agent/auth-profiles.json  ❌ API Key
├── agents/*/sessions/        ❌ 会话历史（隐私）
├── memory/.dreams/           ❌ 梦境索引（自动生成）
├── cron/jobs-state.json      ❌ 运行时状态
└── logs/                     ❌ 日志文件


⚠️ 注意：提交前要脱敏！
- 所有 API Key、Token、Secret 要替换成环境变量引用
- 不要包含真实的用户 ID、手机号等隐私信息
- 使用 .gitignore 排除敏感文件
```

### 7.2 配置分层管理策略

```
建议的配置管理架构（中大型团队）：

┌─────────────────────────────────────────────────────────┐
│                   配置分层架构                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🔵 Layer 1 - 基础配置层（Infra 团队维护）              │
│     ~/.openclaw/openclaw.base.json                     │
│     ├─ 网关、网络、安全基线、全局工具策略              │
│     └─ 所有环境通用，变更需要审批                      │
│                                                         │
│  🟢 Layer 2 - 环境配置层（DevOps 维护）                │
│     ~/.openclaw/openclaw.dev.json / prod.json          │
│     ├─ 环境特有配置：模型供应商、通道白名单            │
│     └─ 不同环境使用不同的 API Key、沙箱策略           │
│                                                         │
│  🟡 Layer 3 - 业务配置层（业务团队维护）                │
│     ~/.openclaw/workspace/AGENTS.md                    │
│     ~/.openclaw/workspace/TOOLS.md                     │
│     ├─ 业务规则、SOP、审批流程                        │
│     └─ 各团队可自行管理自己的部分                      │
│                                                         │
│  🟣 Layer 4 - 技能层（各团队贡献）                     │
│     ~/.openclaw/skills/<team>/                         │
│     └─ 各业务团队贡献的技能，统一审核后发布           │
│                                                         │
└─────────────────────────────────────────────────────────┘

实现方式：使用 JSON5 的 import 特性，或外部配置管理工具
```

### 7.3 配置变更 Checklist

**每次修改配置前确认：**

- [ ] **已备份当前配置**（`cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak`）
- [ ] **理解修改的影响范围**（全局 / 单个智能体 / 所有环境）
- [ ] **检查是否需要重启网关**（plugins、gateway、channels 通常需要）
- [ ] **数组类型字段是完全替换，不是追加**（skills、fallbacks）
- [ ] **对象类型字段是完全替换，不是 merge**（model、sandbox）
- [ ] **修改后执行 `openclaw doctor` 验证**
- [ ] **验证功能实际生效**（不要只看配置值）
- [ ] **记录变更原因和版本，提交到 Git**

### 7.4 敏感信息管理最佳实践

```
方案 1：使用环境变量注入（推荐）
┌─────────────────────────────────────────────┐
│ export OPENCLAW_QWEN_API_KEY=sk-xxx        │
│ export OPENCLAW_WECOM_SECRET=xxx           │
│                                             │
│ 在 openclaw.json 中使用 ${VAR} 引用         │
│ 或直接使用插件的 env 配置支持               │
└─────────────────────────────────────────────┘

方案 2：使用密钥管理服务
┌─────────────────────────────────────────────┐
│ 集成 HashiCorp Vault / AWS Secrets Manager  │
│ 通过 plugins 动态注入配置                    │
└─────────────────────────────────────────────┘

方案 3：Git 加密存储
┌─────────────────────────────────────────────┐
│ 使用 git-crypt / blackbox                   │
│ 敏感字段提交时自动加密，检出时解密          │
└─────────────────────────────────────────────┘

⚠️ 不要：直接把明文密钥提交到公开的 Git 仓库！
```

---

## 八、完整关系图谱

### 8.1 所有配置文件的关联总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  OpenClaw 配置文件完整关系图谱 v1.0                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                     1. 核心配置层                                │  │
│  │              ~/.openclaw/openclaw.json                         │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │  gateway.*    →  网关服务、认证、控制UI、健康检查               │  │
│  │  models.*     →  模型提供商、模型列表、参数配置                 │  │
│  │  agents.*     →  智能体默认配置 + 智能体列表 → 见下            │  │
│  │  session.*    →  会话管理、重置策略、线程绑定                   │  │
│  │  messages.*   →  消息发送策略、可见性                           │  │
│  │  cron.*       →  定时任务引擎、并发、日志                       │  │
│  │  hooks.*      →  Webhook 端点、认证、映射                       │  │
│  │  tools.*      →  工具配置文件、白名单、权限策略                 │  │
│  │  skills.*     →  技能加载路径、安装、各技能单独配置 → 见下    │  │
│  │  plugins.*    →  插件启用、配置、子代理权限 → 见下             │  │
│  │  channels.*   →  消息通道配置、白名单、策略 → 见下             │  │
│  │  mcp.*        →  MCP 服务器定义                                │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    2. 智能体配置层                              │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │  agents.defaults.*                                              │  │
│  │    ├─ workspace       →  工作区根路径                          │  │
│  │    ├─ model.*         →  主模型 + fallback                    │  │
│  │    ├─ sandbox.*       →  沙箱模式 + Docker 配置               │  │
│  │    ├─ subagents.*     →  子代理深度、并发、超时               │  │
│  │    ├─ heartbeat.*     →  心跳间隔、目标                       │  │
│  │    ├─ skills          →  技能白名单（默认）                   │  │
│  │    ├─ tools.*         →  工具权限                              │  │
│  │    └─ contextLimits.* →  上下文预算控制                        │  │
│  │                                                                   │  │
│  │  agents.list[] (每个智能体独立配置，覆盖 defaults)             │  │
│  │    ├─ id                    →  唯一标识                         │  │
│  │    ├─ name                  →  显示名称                        │  │
│  │    ├─ default: true/false  →  是否默认智能体                  │  │
│  │    ├─ workspace             →  独立工作区路径                   │  │
│  │    ├─ agentDir              →  独立状态目录（含认证）         │  │
│  │    ├─ model                 →  覆盖模型配置                    │  │
│  │    ├─ skills                →  覆盖技能白名单                 │  │
│  │    ├─ sandbox               →  覆盖沙箱配置                    │  │
│  │    ├─ tools                 →  覆盖工具权限                    │  │
│  │    └─ ...                   →  所有 defaults 字段都可覆盖     │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    3. 工作区 Bootstrap 层                       │  │
│  │        {workspace}/AGENTS.md, SOUL.md, USER.md...             │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │  注入时机：每次智能体运行前（受 contextInjection 策略影响）   │  │
│  │  注入方式：拼接到系统提示词的最前面                            │  │
│  │  字符限制：bootstrapMaxChars（单文件）+ bootstrapTotalMaxChars │  │
│  │                                                                   │  │
│  │  AGENTS.md     →  最高优先级行为规范，强制执行                 │  │
│  │  SOUL.md       →  人格、语气、沟通风格                          │  │
│  │  USER.md       →  用户信息、偏好、习惯、联系方式                │  │
│  │  IDENTITY.md   →  智能体自我介绍、职责范围                     │  │
│  │  TOOLS.md      →  工具使用原则、安全规范、SOP                  │  │
│  │  HEARTBEAT.md  →  仅心跳运行：自动化任务清单                   │  │
│  │  MEMORY.md     →  长期记忆、重要决策、经验教训                 │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                       4. 技能配置层                             │  │
│  │               {workspace}/skills/<name>/SKILL.md               │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │  加载时机：会话启动时扫描 + 文件变更热重载                     │  │
│  │  注入方式：有界列表拼接到系统提示词（maxSkillsPromptChars）   │  │
│  │  白名单控制：agents.defaults.skills + agents.list[].skills    │  │
│  │                                                                   │  │
│  │  frontmatter 元数据                                              │  │
│  │    ├─ name                    →  唯一技能ID                     │  │
│  │    ├─ description             →  描述                           │  │
│  │    ├─ user-invocable          →  用户可手动调用                 │  │
│  │    ├─ command-dispatch        →  工具分发策略                  │  │
│  │    └─ metadata.openclaw.*     →  依赖检查（bins、env、config） │  │
│  │                                                                   │  │
│  │  Markdown 正文                                                  │  │
│  │    └─ 技能使用说明、SOP、示例、注意事项 → 注入提示词          │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                       5. 运行时状态层                           │  │
│  │               ~/.openclaw/{credentials,cron,memory,...}       │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │  credentials/   →  通道登录凭证（WhatsApp等）、配对白名单     │  │
│  │  cron/          →  jobs.json(任务定义) + jobs-state.json(状态)│  │
│  │  memory/        →  每日记忆 YYYY-MM-DD.md + 梦境整理          │  │
│  │  agents/<id>/   →  每个智能体独立的认证 + 会话                 │  │
│  │  logs/          →  运行日志                                   │  │
│  │  plugins/       →  插件私有数据存储                           │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────────┘

                                 配
                                 置
                                 优
                                 先
                                 级
                                 ▼

         命令行参数 > 环境变量 > openclaw.json > 工作区文件 > 内置默认
```

### 8.2 配置修改影响范围速查表

| 修改区域 | 影响范围 | 需要重启 | 生效时间 |
|---------|---------|---------|---------|
| `gateway.port` | 全局 | ✅ 是 | 重启后 |
| `gateway.auth.token` | 全局 | ⚠️ 建议重启 | 新连接生效 |
| `agents.defaults.model.primary` | 所有智能体 | ❌ 否 | 下次运行 |
| `agents.list[x].model` | 单个智能体 | ❌ 否 | 下次运行 |
| `agents.defaults.skills` | 所有智能体 | ❌ 否 | 下次技能加载 |
| `agents.list[x].skills` | 单个智能体 | ❌ 否 | 下次技能加载 |
| `agents.defaults.sandbox` | 所有智能体 | ❌ 否 | 新沙箱实例 |
| `subagents.maxSpawnDepth` | 所有智能体 | ❌ 否 | 下次 spawn |
| `cron.*` | 定时任务 | ❌ 否 | 下次调度 |
| `hooks.*` | Webhook | ❌ 否 | 下次调用 |
| `skills.entries.*` | 技能 | ❌ 否 | 下次加载 |
| `plugins.entries.*.enabled` | 插件 | ✅ 是 | 重启后 |
| `channels.*.allowFrom` | 消息通道 | ❌ 否 | 下次消息 |
| 工作区 AGENTS.md | 智能体行为 | ❌ 否 | 下次运行 |
| 工作区 SKILL.md | 技能 | ❌ 否 | 文件变更检测后 |

---

## 附录：配置路径快速索引

| 功能 | 配置路径 |
|------|---------|
| 主模型 | `agents.defaults.model.primary` |
| 模型降级 | `agents.defaults.model.fallbacks` |
| 心跳间隔 | `agents.defaults.heartbeat.every` |
| 沙箱模式 | `agents.defaults.sandbox.mode` |
| 子代理深度 | `agents.defaults.subagents.maxSpawnDepth` |
| 技能白名单 | `agents.defaults.skills` |
| 图片缩放 | `agents.defaults.imageMaxDimensionPx` |
| 上下文注入 | `agents.defaults.contextInjection` |
| 会话重置 | `session.reset.mode` |
| Cron 并发 | `cron.maxConcurrentRuns` |
| 工具配置文件 | `tools.profile` |
| 技能额外目录 | `skills.load.extraDirs` |
| 绑定路由 | `bindings` |
| 企业微信白名单 | `channels.wecom.allowFrom` |
| 梦境启用 | `plugins.entries.memory-core.config.dreaming.enabled` |
| 梦境 Cron | `plugins.entries.memory-core.config.dreaming.frequency` |

---

*本文档基于 OpenClaw 2026.4.15 官方文档深度整理* 🦞
