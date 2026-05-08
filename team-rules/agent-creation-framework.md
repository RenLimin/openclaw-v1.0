# Agent 创建框架 v3.0

> **设计原则**：标准化、自动化、可复用、可验证
> 
> **适用范围**：智能体团队的完整生命周期管理（业务目标分析 → 创建 → 训练 → 部署 → 运维 → 持续进化）
>
> **版本升级**：v2.0 → v3.0 (2026-05-08) | Jerry v2.0 角色升级：智能体团队创建者
>
> **核心变更**：新增 **L0 层 - 业务目标深度分析阶段**（所有智能体团队创建的前置强制阶段）
>
> **参考**：技能训练框架 (`skill-training-framework.md`) | 业务目标分析技能 (`business-goal-analyzer`)

---

## 一、智能体团队生命周期 (v3.0)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              智能体团队完整生命周期 (Jerry v2.0 - 7阶段)                      │
│                                                                               │
│  🔴 L0层: 业务目标深度分析    Phase 0: 规划       Phase 1: 创建                 │
│  ┌─────────────────────┐   ┌────────────┐   ┌────────────┐                    │
│  │ 1. 目标解构         │ → │ 需求定义   │ → │ 目录结构   │                    │
│  │ 2. 利益相关者映射   │   │ 角色定位   │   │ 文件生成   │                    │
│  │ 3. 风险与约束识别   │   │ 职责划分   │   │ 系统注册   │                    │
│  │ 4. 能力需求矩阵     │   │ 技能规划   │   │ 路由配置   │                    │
│  └─────────────────────┘   └────────────┘   └────────────┘                    │
│         │                      │              │                               │
│         ✅ 必须用户确认         ▼              ▼                               │
│         ──────────────     Phase 2: 训练     Phase 3: 验证                    │
│                            ┌────────────┐   ┌────────────┐                    │
│                            │ 环境熟悉   │ → │ 功能验证   │                    │
│                            │ 技能测试   │   │ 安全扫描   │                    │
│                            │ 领域训练   │   │ 性能测试   │                    │
│                            │ 实战演练   │   │ 文档完善   │                    │
│                            └────────────┘   └────────────┘                    │
│                                   │              │                               │
│                                   ▼              ▼                               │
│                               Phase 4: 部署     Phase 5: 运维                    │
│                               ┌────────────┐   ┌────────────┐                    │
│                               │ 正式上线   │ → │ 健康监控   │                    │
│                               │ 消息路由   │   │ 日志审计   │                    │
│                               │ 外部接入   │   │ 策略优化   │                    │
│                               │ 备份配置   │   │ 版本管理   │                    │
│                               └────────────┘   └────────────┘                    │
│                                      │                                           │
│                                      ▼                                           │
│                               Phase 6: 自进化                                    │
│                               ┌────────────┐                                    │
│                               │ 持续监控   │                                    │
│                               │ 问题识别   │                                    │
│                               │ 自动优化   │                                    │
│                               │ 知识沉淀   │                                    │
│                               └────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

> 🔴 **L0 层强制规则**：创建任何智能体团队之前，必须先完成业务目标深度分析并获得用户确认！
> 严禁跳过 L0 层直接进入 Phase 0！

---

---

## 🔴 L0 层：业务目标深度分析阶段（强制前置！）

> **执行角色**：Jerry 🦞
> **使用工具**：`goal_analyzer.py`
> **验收标准**：≥ 90分 + 用户明确确认

### L0.1 阶段一：目标解构（必须完成）

**5个核心问题必须获得明确答案：**

| 序号 | 问题 | 输出物 | 验证标准 |
|------|------|--------|---------|
| 1 | 要解决的核心问题是什么？ | 问题陈述文档 | 用一句话能清晰说明，无歧义 |
| 2 | 谁是最终受益者/用户？ | 利益相关者映射矩阵 | 覆盖所有关键角色 |
| 3 | 成功的具体衡量标准是什么？ | KPI指标体系 | 量化、可测量、可验证 |
| 4 | 有什么时间限制/里程碑要求？ | 项目时间线 | 明确的里程碑节点 |
| 5 | 有什么预算/资源约束？ | 资源约束清单 | 成本估算在预算范围内 |

### L0.2 阶段二：能力映射（必须完成）

**输出：核心能力需求矩阵**

| 能力类别 | 能力项 | 优先级 | 对应角色 |
|---------|--------|--------|---------|
| 核心业务能力 | {能力项} | 🔴必须/🟡应该/🟢可以 | {角色名} |
| 基础支撑能力 | {能力项} | 🔴必须/🟡应该/🟢可以 | {角色名} |
| 基础设施能力 | {能力项} | 🔴必须/🟡应该/🟢可以 | Nova/Orion/Luna |

### L0.3 阶段三：方案输出（必须完成）

**7份标准交付物（缺一不可）：**

| 序号 | 交付物 | 说明 | 格式 |
|------|--------|------|------|
| 1 | 业务目标分析报告 | 完整的目标解构与分析 | Markdown |
| 2 | 团队架构蓝图 | 三层架构设计图 | YAML + 图 |
| 3 | 角色定义集 | 每个角色的CrewAI风格定义 | YAML |
| 4 | 成功指标体系 | 三层KPI（业务+效能+技术） | Excel/Markdown |
| 5 | 实施路线图 | 四阶段成长计划 | Markdown |
| 6 | ROI分析报告 | 成本收益、投资回收期、年化ROI | Markdown |
| 7 | 风险评估与应对 | 10项通用风险 + 应对措施 | Markdown |

### L0.4 用户确认流程（强制执行）

```
完成全部分析并生成7份交付物
    │
    ▼
向用户展示完整方案
    │
    ▼
根据意见迭代修改（可多轮）
    │
    ▼
用户明确表示「确认」「同意」「可以开始」
    │
    ▼
✅ 记录确认信息（时间、用户、确认内容）
    │
    ▼
进入 Phase 0: 规划阶段
```

### L0.5 质量评分标准（100分制）

| 检查项 | 权重 | 验收标准 |
|--------|------|---------|
| 目标清晰度 | 20% | 核心目标能用一句话说清楚，没有歧义 |
| 可衡量性 | 20% | 所有成功指标都是可量化、可测量的 |
| 完整性 | 15% | 覆盖了所有核心能力需求，没有遗漏 |
| 合理性 | 15% | 目标在给定的时间和资源约束下是可行的 |
| 一致性 | 15% | 角色职责没有重叠，也没有遗漏 |
| 风险识别 | 10% | 识别了所有主要风险，并有应对措施 |
| 用户确认 | 5% | 用户明确签字确认 |

- **≥ 90分**：优秀，可直接进入 Phase 0
- **≥ 70分**：良好，需要补充细节后确认
- **< 70分**：不合格，需要重新分析

---

## 二、Phase 0: 规划阶段

### 2.1 需求定义模板（基于 L0 层分析结果）

```markdown
# Agent 需求文档: {AgentName}

## 基本信息
- **名称**: {AgentName}
- **Emoji**: {Emoji}
- **角色**: {角色描述}
- **优先级**: P0/P1/P2

## 核心职责
1. {职责 1}
2. {职责 2}
3. {职责 3}

## 外部系统依赖
| 系统 | 用途 | 接入方式 | 状态 |
|------|------|---------|------|
| {系统名} | {用途} | {API/SDK/人工} | ⏳/✅ |

## 专属技能规划
| 技能 | 来源 | 依赖 | 优先级 |
|------|------|------|--------|
| {技能名} | ClawHub/手动 | {依赖项} | P0/P1/P2 |

## 协作关系
- **上游**: 从哪个 Agent 接收任务
- **下游**: 向哪个 Agent 传递结果
- **协调**: Jerry (主代理)

## 验收标准
- [ ] 标准 1
- [ ] 标准 2
- [ ] 标准 3
```

### 2.2 职责划分原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **高内聚** | 每个 Agent 专注一个领域 | Ella 只做合同相关 |
| **低耦合** | Agent 间通过 Jerry 协调 | 不直接互相调用 |
| **可替代** | 职责可独立替换 | 换人不换流程 |
| **可扩展** | 预留技能扩展接口 | 新技能可随时添加 |

---

## 三、Phase 1: 创建阶段

### 3.1 标准目录结构

```
~/.openclaw/agents/{name}/
├── agent/
│   └── config.json              # Agent 配置（必填）
├── memory/
│   ├── training-memory.md       # 训练记忆
│   ├── 2026-04-12.md           # 每日日志
│   └── heartbeat-state.json    # 心跳状态 (可选)
└── workspace/
    ├── SOUL.md                  # 角色定义
    ├── USER.md                  # 用户信息
    ├── AGENTS.md                # 团队架构
    ├── TOOLS.md                 # 工具配置
    ├── MEMORY.md                # 长期记忆
    ├── IDENTITY.md              # 身份标识 (自动生成)
    ├── HEARTBEAT.md             # 心跳配置 (自动生成)
    ├── skills/                  # 专属技能目录
    │   ├── <skill-name>/
    │   │   ├── SKILL.md
    │   │   ├── _meta.json
    │   │   └── ...
    │   └── ...
    └── scripts/                 # 自动化脚本
        └── *.sh / *.py
```

### 3.2 文件模板库

所有模板存放在 `team-rules/templates/agent/` 目录下。

#### config.json
```json
{
  "name": "{AgentName}",
  "emoji": "{Emoji}",
  "role": "{角色描述}",
  "description": "{详细职责描述}",
  "workspace": "~/.openclaw/agents/{name}/workspace",
  "sessions": "~/.openclaw/agents/{name}/sessions",
  "memory": "~/.openclaw/agents/{name}/memory",
  "teamRules": "~/.openclaw/workspace/team-rules/",
  "model": "bailian/qwen3.6-plus"
}
```

#### SOUL.md
```markdown
# SOUL.md - {AgentName} {Emoji}

## 身份
- **名字**: {AgentName}
- **角色**: {角色}
- **Emoji**: {Emoji}

## 核心职责
1. {职责 1}
2. {职责 2}
3. {职责 3}

## 工作原则
- {原则 1}
- {原则 2}
- {原则 3}

## 外部系统
- **系统名称** — 用途

## 升级规则
- P0（紧急）: 立即上报 Jerry
- P1（24h）: 24h 内处理
- P2（常规）: 按常规流程处理
```

#### USER.md
```markdown
# USER.md - About Rex

- **Name**: Rex
- **GitHub**: RenLimin
- **Timezone**: Asia/Shanghai (GMT+8)
- **语言**: 中文

## 对 {AgentName} 的期望
- 工作准确及时
- 异常情况及时上报
- 保密原则
```

#### AGENTS.md
```markdown
# AGENTS.md - {AgentName} 工作区

## 团队架构

| 智能体 | 职责 | Emoji |
|--------|------|-------|
| Jerry | 主代理 & 团队协调员 | 🦞 |
| Ella | 合同管理 (含 OA 审批) | 🦊 |
| Oliver | 项目管理 (含 ONES 操作) | 🐘 |
| Aaron | 经营计划 | 🦉 |
| Iris | 辅助工作 (含 邮件管理) | 🐦‍⬛ |

## 技能清单
| 技能 | 版本 | 状态 |
|------|------|------|
| {技能名} | {版本} | ✅/⏳ |

## 工作区路径
- 技能: `~/.openclaw/agents/{name}/workspace/skills/`
- 脚本: `~/.openclaw/agents/{name}/workspace/scripts/`
- 记忆: `~/.openclaw/agents/{name}/memory/`

## 团队规则
遵守 `~/.openclaw/workspace/team-rules/` 下所有规则。
```

#### TOOLS.md
```markdown
# TOOLS.md - {AgentName} 工具配置

## Python 环境
| 包 | 版本 | 状态 |
|----|------|------|
| python3 | 3.10.6 | ✅ |

## 外部系统
| 系统 | 状态 | 配置项 |
|------|------|--------|
| {系统名} | ⏳/✅ | {配置项} |

## 笔记
- {备注信息}
```

#### MEMORY.md
```markdown
# MEMORY.md - {AgentName} 长期记忆

## 训练状态
- {日期}: 基础架构搭建完成
- 待完成: Phase 2 技能训练

## 关键事件
- {事件记录}

## 经验教训
- {经验记录}
```

### 3.3 自动化创建脚本

```bash
#!/bin/bash
# scripts/agent-creator.sh
# 自动化 Agent 创建脚本 v2.0

set -euo pipefail

AGENT_NAME="${1:?Usage: agent-creator.sh <name> <emoji> <role>}"
AGENT_EMOJI="${2:?Emoji}"
AGENT_ROLE="${3:?Role}"
MODEL="${4:-bailian/qwen3.6-plus}"

AGENT_DIR="$HOME/.openclaw/agents/$AGENT_NAME"
WORKSPACE_DIR="$AGENT_DIR/workspace"
MEMORY_DIR="$AGENT_DIR/memory"
SKILLS_DIR="$WORKSPACE_DIR/skills"
SCRIPTS_DIR="$WORKSPACE_DIR/scripts"
TEMPLATES_DIR="$HOME/.openclaw/workspace/team-rules/templates/agent"

echo "🤖 创建 Agent: $AGENT_NAME ($AGENT_EMOJI)"

# 1. 创建目录结构
echo "📁 创建目录结构..."
mkdir -p "$AGENT_DIR/agent"
mkdir -p "$WORKSPACE_DIR"
mkdir -p "$MEMORY_DIR"
mkdir -p "$SKILLS_DIR"
mkdir -p "$SCRIPTS_DIR"

# 2. 从模板生成文件
echo "📝 生成配置文件..."

# config.json
cat > "$AGENT_DIR/agent/config.json" << EOF
{
  "name": "$AGENT_NAME",
  "emoji": "$AGENT_EMOJI",
  "role": "$AGENT_ROLE",
  "description": "Auto-generated agent",
  "workspace": "$WORKSPACE_DIR",
  "sessions": "$AGENT_DIR/sessions",
  "memory": "$MEMORY_DIR",
  "teamRules": "~/.openclaw/workspace/team-rules/",
  "model": "$MODEL"
}
EOF

# SOUL.md
cat > "$WORKSPACE_DIR/SOUL.md" << EOF
# SOUL.md - $AGENT_NAME $AGENT_EMOJI

## 身份
- **名字**: $AGENT_NAME
- **角色**: $AGENT_ROLE
- **Emoji**: $AGENT_EMOJI

## 核心职责
1. 待定义

## 工作原则
- 准确性优先
- 及时通知
- 保密原则

## 升级规则
- P0: 立即上报 Jerry
- P1: 24h 内处理
- P2: 常规处理
EOF

# USER.md
cat > "$WORKSPACE_DIR/USER.md" << EOF
# USER.md - About Rex

- **Name**: Rex
- **GitHub**: RenLimin
- **Timezone**: Asia/Shanghai (GMT+8)
- **语言**: 中文

## 对 $AGENT_NAME 的期望
- 工作准确及时
- 异常情况及时上报
EOF

# AGENTS.md
cat > "$WORKSPACE_DIR/AGENTS.md" << EOF
# AGENTS.md - $AGENT_NAME 工作区

## 团队架构

| 智能体 | 职责 | Emoji |
|--------|------|-------|
| Jerry | 主代理 & 团队协调员 | 🦞 |
| Ella | 合同管理 | 🦊 |
| Oliver | 项目管理 | 🐘 |
| Aaron | 经营计划 | 🦉 |
| Iris | 辅助工作 | 🐦‍⬛ |
| $AGENT_NAME | $AGENT_ROLE | $AGENT_EMOJI |

## 技能清单
| 技能 | 版本 | 状态 |
|------|------|------|
| 待添加 | — | ⏳ |

## 工作区路径
- 技能: \$WORKSPACE_DIR/skills/
- 脚本: \$WORKSPACE_DIR/scripts/
- 记忆: \$MEMORY_DIR/

## 团队规则
遵守 \`~/.openclaw/workspace/team-rules/\` 下所有规则。
EOF

# TOOLS.md
cat > "$WORKSPACE_DIR/TOOLS.md" << EOF
# TOOLS.md - $AGENT_NAME 工具配置

## 外部系统
| 系统 | 状态 | 配置项 |
|------|------|--------|
| 待配置 | ⏳ | — |

## 笔记
- 待添加
EOF

# MEMORY.md
cat > "$WORKSPACE_DIR/MEMORY.md" << EOF
# MEMORY.md - $AGENT_NAME 长期记忆

## 训练状态
- $(date +%Y-%m-%d): 基础架构搭建完成
- 待完成: Phase 2 技能训练
EOF

# training-memory.md
cat > "$MEMORY_DIR/training-memory.md" << EOF
# Training Memory - $AGENT_NAME

## 训练日志
- $(date +%Y-%m-%d): Agent 创建完成
EOF

# 3. 注册到 OpenClaw
echo "🔗 注册到 OpenClaw..."
openclaw agents add "$AGENT_NAME" \
    --agent-dir "$AGENT_DIR" \
    --workspace "$WORKSPACE_DIR" \
    --model "$MODEL" \
    --non-interactive 2>/dev/null || echo "⚠️ 注册失败，可稍后手动注册"

echo ""
echo "✅ Agent $AGENT_NAME 创建完成!"
echo "   目录: $AGENT_DIR"
echo "   工作区: $WORKSPACE_DIR"
echo ""
echo "下一步:"
echo "  1. 编辑 SOUL.md 定义角色职责"
echo "  2. 添加专属技能到 $SKILLS_DIR/"
echo "  3. 配置外部系统接入"
echo "  4. 开始 Phase 2 训练"
```

### 3.4 验证脚本

```bash
#!/bin/bash
# scripts/agent-validator.sh
# Agent 创建验证 v2.0

AGENT_NAME="${1:?Usage: agent-validator.sh <name>}"
AGENT_DIR="$HOME/.openclaw/agents/$AGENT_NAME"
WORKSPACE_DIR="$AGENT_DIR/workspace"

echo "🔍 验证 Agent: $AGENT_NAME"
echo ""

PASS=0
FAIL=0

check() {
    local desc="$1"
    local path="$2"
    if [ -f "$path" ]; then
        echo "  ✅ $desc"
        ((PASS++))
    else
        echo "  ❌ $desc (缺失: $path)"
        ((FAIL++))
    fi
}

check_dir() {
    local desc="$1"
    local path="$2"
    if [ -d "$path" ]; then
        echo "  ✅ $desc"
        ((PASS++))
    else
        echo "  ❌ $desc (缺失: $path)"
        ((FAIL++))
    fi
}

echo "=== 目录结构 ==="
check_dir "主目录" "$AGENT_DIR"
check_dir "agent/" "$AGENT_DIR/agent"
check_dir "workspace/" "$WORKSPACE_DIR"
check_dir "memory/" "$AGENT_DIR/memory"
check_dir "skills/" "$WORKSPACE_DIR/skills"
check_dir "scripts/" "$WORKSPACE_DIR/scripts"

echo ""
echo "=== 核心文件 ==="
check "config.json" "$AGENT_DIR/agent/config.json"
check "SOUL.md" "$WORKSPACE_DIR/SOUL.md"
check "USER.md" "$WORKSPACE_DIR/USER.md"
check "AGENTS.md" "$WORKSPACE_DIR/AGENTS.md"
check "TOOLS.md" "$WORKSPACE_DIR/TOOLS.md"
check "MEMORY.md" "$WORKSPACE_DIR/MEMORY.md"
check "training-memory.md" "$AGENT_DIR/memory/training-memory.md"

echo ""
echo "=== 注册状态 ==="
if openclaw agents list 2>/dev/null | grep -q "$AGENT_NAME"; then
    echo "  ✅ 已注册"
    ((PASS++))
else
    echo "  ❌ 未注册"
    ((FAIL++))
fi

echo ""
echo "=== 验证结果 ==="
echo "通过: $PASS | 失败: $FAIL"

if [ $FAIL -eq 0 ]; then
    echo "✅ Agent 验证通过!"
    exit 0
else
    echo "❌ Agent 验证失败，请检查缺失项"
    exit 1
fi
```

---

## 四、Phase 2: 训练阶段

> **核心原则**：与技能训练框架一致，采用 Phase A (方案生成) → Rex 审阅 → Phase B (自主执行) 模型

### 4.1 训练流程

```
新 Agent
   │
   ▼
┌─────────────────────────┐
│ Phase A: 方案生成        │
│ - 分析训练目标           │
│ - 检查环境依赖           │
│ - 生成训练计划           │
│ - 提交 Rex 审阅          │
└─────────────────────────┘
   │
   ▼
Rex 审阅通过？
   ╱          ╲
  是            否 → 修改方案
  │
  ▼
┌─────────────────────────┐
│ Phase B: 自主执行        │
│ - 环境熟悉 (30min)       │
│ - 技能测试 (1h)          │
│ - 领域训练 (2h)          │
│ - 实战演练 (1h)          │
│ - 复盘优化 (30min)       │
└─────────────────────────┘
   │
   ▼
训练完成 → 验证 → 部署
```

### 4.2 训练内容清单

| 阶段 | 内容 | 时长 | 验收标准 |
|------|------|------|---------|
| **环境熟悉** | 认识技能目录、检查依赖 | 30min | 能列出所有已安装技能 |
| **技能测试** | 逐个测试 L0-L3 技能 | 1h | 每个技能执行 1 次成功 |
| **领域训练** | 执行领域专属任务 | 2h | 完成训练手册全部场景 |
| **实战演练** | 端到端任务流程 | 1h | 独立完成完整工作流 |
| **复盘优化** | self-improving 复盘 | 30min | 写入经验教训到 memory |

### 4.3 验证标准

| 验证项 | 方法 | 通过标准 |
|--------|------|---------|
| 目录完整性 | `agent-validator.sh` | 所有文件存在 |
| 注册状态 | `openclaw agents list` | Agent 在列表中 |
| 技能安装 | `openclaw skills check` | 无缺失依赖 |
| 功能测试 | 执行测试脚本 | 通过率 100% |
| 路由配置 | `openclaw agents bindings` | 路由正确 |

---

## 五、Phase 3: 验证阶段

### 5.1 功能验证

```bash
# 1. 验证 Agent 注册
openclaw agents list | grep {name}

# 2. 验证工作区
ls ~/.openclaw/agents/{name}/workspace/

# 3. 验证技能
openclaw skills check

# 4. 验证路由
openclaw agents bindings
```

### 5.2 安全验证

| 检查项 | 方法 | 通过标准 |
|--------|------|---------|
| 凭证隔离 | 检查 Keychain 条目 | 凭证仅对对应 Agent 可见 |
| 权限最小化 | 检查技能权限 | 无多余权限 |
| 日志审计 | 检查 memory 日志 | 所有操作有记录 |
| 网络代理 | 检查代理配置 | 符合 network-rules.md |

### 5.3 性能验证

| 检查项 | 方法 | 通过标准 |
|--------|------|---------|
| 响应时间 | 发送测试消息 | < 30s 响应 |
| 内存使用 | `ps aux | grep {name}` | 无异常增长 |
| 磁盘使用 | `du -sh ~/.openclaw/agents/{name}/` | < 100MB |

---

## 六、Phase 4: 部署阶段

### 6.1 路由配置

```bash
# 绑定 Channel 到 Agent
openclaw agents bind --agent {name} --bind {channel}:{accountId}

# 示例：绑定企业微信到 Jerry
openclaw agents bind --agent jerry --bind wecom:default

# 查看所有绑定
openclaw agents bindings
```

### 6.2 外部系统接入

| 系统 | Agent | 配置项 | 状态 |
|------|-------|--------|------|
| 泛微 OA | Ella | external.oa | ⏳ |
| 万事 ONES | Oliver | external.ones | ⏳ |
| 网易邮箱 | Iris | external.email | ⏳ |
| Office 365 | Iris | external.office365 | ⏳ |

### 6.3 备份配置

```bash
# 确保 Agent 工作区在 Git 仓库中
cd ~/.openclaw/workspace
git add agents/registry.json
git commit -m "feat: add {name} agent"
git push
```

---

## 七、Phase 5: 运维阶段

### 7.1 健康监控

```bash
# 检查 Agent 状态
openclaw agents list

# 检查路由状态
openclaw agents bindings

# 检查 Channel 状态
openclaw channels status --probe
```

### 7.2 日志管理

| 日志类型 | 位置 | 保留策略 |
|---------|------|---------|
| 每日日志 | `memory/YYYY-MM-DD.md` | 保留 90 天 |
| 长期记忆 | `MEMORY.md` | 永久保留 |
| 训练记忆 | `memory/training-memory.md` | 永久保留 |
| 系统日志 | Gateway 日志 | 保留 30 天 |

### 7.3 版本管理

```bash
# Agent 配置变更提交
cd ~/.openclaw/workspace
git add agents/{name}/
git commit -m "chore({name}): update agent config"
git push
```

---

## 八、Agent 注册表

### 8.1 注册表结构

`~/.openclaw/workspace/agents/registry.json`

```json
{
  "version": "2.0",
  "updatedAt": "2026-04-12T14:37:00+08:00",
  "agents": {
    "{name}": {
      "name": "{AgentName}",
      "emoji": "{Emoji}",
      "role": "{角色描述}",
      "status": "active|inactive|training",
      "registered": true,
      "agentDir": "~/.openclaw/agents/{name}",
      "workspace": "~/.openclaw/agents/{name}/workspace",
      "model": "bailian/qwen3.6-plus",
      "channels": ["wecom", "openclawwechat"],
      "capabilities": ["能力 1", "能力 2"],
      "skills": ["技能 1", "技能 2"]
    }
  }
}
```

### 8.2 当前注册表

| Agent | 状态 | 注册 | 渠道 | 技能数 |
|-------|------|------|------|--------|
| Jerry 🦞 | active | ✅ | wecom, openclawwechat | 17 |
| Ella 🦊 | active | ✅ | — | 2 |
| Oliver 🐘 | active | ✅ | — | 1 |
| Aaron 🦉 | active | ✅ | — | 1 |
| Iris 🐦‍⬛ | active | ✅ | — | 1 |

---

## 九、GitHub 提交规范

### 9.1 Commit 格式

```
<type>(agent): <agent-name> - <description>

Types:
  feat     - 新功能/新 Agent
  fix      - 修复问题
  docs     - 文档更新
  chore    - 配置变更
  training - 训练相关

Examples:
  feat(agent): create ella - contract management agent
  fix(agent): repair oliver workspace config
  docs(agent): update jerry SOUL.md
  chore(agent): register iris to OpenClaw
  training(ella): phase 2 milestone 1 complete
```

### 9.2 提交粒度

| 变更类型 | 提交频率 | 包含内容 |
|---------|---------|---------|
| Agent 创建 | 1 commit/Agent | 所有文件 + 注册 |
| 技能安装 | 1 commit/技能 | SKILL.md + _meta.json + scripts |
| 训练里程碑 | 1 commit/阶段 | memory 更新 + 测试记录 |
| 配置变更 | 1 commit/变更 | 相关配置文件 |

---

## 十、最佳实践

### 10.1 命名规范

| 项目 | 规范 | 示例 |
|------|------|------|
| Agent 名称 | 简短、易记、有意义 | Ella, Oliver |
| Emoji | 唯一标识 | 🦊, 🐘 |
| 目录名 | 小写、无空格 | `ella`, `oliver` |
| 技能名 | kebab-case | `oa-approval`, `contract-management` |

### 10.2 职责划分

| 原则 | 说明 | 反例 |
|------|------|------|
| **高内聚** | 每个 Agent 专注一个领域 | Ella 既做合同又做项目 |
| **低耦合** | Agent 间通过 Jerry 协调 | Ella 直接调用 Oliver |
| **可替代** | 职责可独立替换 | 硬编码依赖 |
| **可扩展** | 预留技能扩展接口 | 封闭的固定实现 |

### 10.3 安全原则

| 原则 | 实施方法 |
|------|---------|
| **最小权限** | 每个 Agent 只有所需的最小权限 |
| **凭证隔离** | 每个 Agent 的凭证独立存储 |
| **操作审计** | 所有外部操作记录日志 |
| **定期审查** | 每月审查权限和凭证 |

### 10.4 维护规范

| 任务 | 频率 | 负责人 |
|------|------|--------|
| 日志更新 | 每日 | 对应 Agent |
| 记忆整理 | 每周 | 对应 Agent |
| 技能更新 | 按需 | Jerry |
| 健康检查 | 每日 | Jerry (Heartbeat) |
| 备份推送 | 每次变更后 | 对应 Agent |

---

## 八、Phase 6: 自进化阶段（v3.0 新增核心能力）

> **执行角色**：Jerry 🦞
> **核心目标**：智能体团队不是静态的，而是持续学习、持续优化的生命体

### 8.1 四阶段成长模型

| 阶段 | 时间 | 核心目标 | 进入下一阶段条件 |
|------|------|---------|----------------|
| 🌱 种子期 | 0-7天 | 验证核心假设 | MVP团队跑通核心流程，验证B级以上 |
| 🌿 生长期 | 7-30天 | 完善团队能力 | 覆盖所有核心能力，连续7天稳定运行，验证A级以上 |
| 🌳 成熟期 | 30-90天 | 优化性能，激活自进化 | 性能优化30%+，自监控部署，自进化激活，验证S级 |
| 🏛️ 卓越期 | 90天+ | 行业标杆，持续进化 | 持续输出最佳实践，形成完整知识体系 |

### 8.2 自进化反馈闭环机制

```
运行中的智能体团队
    │
    ▼ 产生日志/指标/错误/反馈
🔍 数据采集与分析层
    │
    ├── 性能数据采集（响应时间、成本、准确率）
    ├── 错误模式识别（Pattern识别与分类）
    ├── 用户反馈分析（满意度、改进建议）
    └── 成本趋势监控（Token消耗、API调用）
    │
    ▼
🧠 问题诊断与根因分析层
    │
    ├── 问题分类与分级（P0/P1/P2）
    ├── 根因定位（5 Whys 方法）
    ├── 影响范围评估
    └── 优先级排序
    │
    ▼
💡 优化方案生成层
    │
    ├── 知识库匹配最佳实践
    ├── 生成候选优化方案
    ├── 方案成本收益评估
    └── 风险评估
    │
    ▼
✅ 方案验证与实施层
    │
    ├── 方案模拟验证（沙箱环境）
    ├── 用户审批确认（涉及架构变更时）
    ├── 灰度发布实施（10%流量）
    ├── 效果验证与全量发布
    └── 回滚机制（效果不达标时）
    │
    ▼
📚 知识沉淀层
    │
    ├── 更新最佳实践库
    ├── 更新错误案例库
    ├── 更新优化模式库
    ├── 生成版本发布说明
    └── 生成月度进化报告
    │
    ▼
🔄 回到运行中的智能体团队 - 开始新一轮循环
```

### 8.3 自进化触发条件矩阵

| 触发类型 | 触发条件 | 响应级别 | 响应时间 |
|---------|---------|---------|---------|
| **错误触发** | 发生P0级错误 | 🔴 紧急 | 立即启动分析，2小时内出方案 |
| | 连续3次P1级错误 | 🟠 高 | 24小时内出优化方案 |
| **性能触发** | 响应时间超过基线50% | 🟡 中 | 启动性能分析 |
| | 成本超过基线30% | 🟡 中 | 启动成本优化 |
| | 准确率下降超过10% | 🟡 中 | 启动质量分析 |
| **定期触发** | 每周一 | 🟢 例行 | 例行健康检查与优化建议 |
| | 每月1号 | 🟢 例行 | 深度评估与月度优化计划 |
| **用户触发** | 用户反馈满意度 < 3.5分 | 🟡 中 | 启动用户体验优化 |
| | 用户提出功能需求 | 🟢 低 | 进入需求评估流程 |

### 8.4 自进化工具链（开发中）

| 工具名称 | 版本 | 计划完成时间 | 状态 |
|---------|------|------------|------|
| 🔄 evolution_engine.py | v0.1 | 2026-05-15 | 🚧 开发中 |
| 📚 knowledge_manager.py | v0.1 | 2026-05-22 | 📋 规划中 |
| 📊 performance_monitor.py | v0.1 | 2026-05-29 | 📋 规划中 |
| 🧠 pattern_recognizer.py | v0.1 | 2026-06-05 | 📋 规划中 |

### 8.5 进化指标体系

| 指标类别 | 具体指标 | 目标 | 测量频率 |
|---------|---------|------|---------|
| **业务进化** | 用户满意度提升 | ≥ 0.5分/月 | 每月 |
| | 任务完成率提升 | ≥ 2%/月 | 每月 |
| | ROI提升 | ≥ 5%/季度 | 每季度 |
| **效能进化** | 平均响应时间缩短 | ≥ 10%/月 | 每月 |
| | 准确率提升 | ≥ 1%/月 | 每月 |
| | 大模型调用占比下降 | ≥ 3%/月 | 每月 |
| **技术进化** | 系统可用性提升 | ≥ 99.5% | 实时 |
| | P0错误数量 | 0 | 实时 |
| | 自动修复率 | ≥ 80% | 每月 |
| **知识进化** | 知识库新增条目 | ≥ 5条/月 | 每月 |
| | 最佳实践新增 | ≥ 2条/月 | 每月 |
| | 错误案例新增 | ≥ 1条/月 | 每月 |

---

## 九、风险 & 回退

| 风险 | 影响 | 可能性 | 应对 |
|------|------|--------|------|
| 创建失败 | Agent 不可用 | 低 | 使用 agent-creator.sh 重试 |
| 注册冲突 | 配置覆盖 | 低 | 备份 openclaw.json |
| 技能不兼容 | 功能异常 | 中 | skill-vetter 预扫描 |
| 路由错误 | 消息丢失 | 中 | 测试路由后上线 |
| 凭证泄露 | 安全风险 | 低 | 定期轮换凭证 |
| 磁盘满 | Agent 崩溃 | 低 | 定期清理日志 |

---

## 十二、与技能训练框架的关系

```
Agent 创建框架 (本文档)          技能训练框架
┌─────────────────────┐     ┌─────────────────────┐
│ Phase 0: 规划       │     │                     │
│ Phase 1: 创建       │────▶│ Phase 0: 基础设施   │
│ Phase 2: 训练       │────▶│ Phase 1: 环境准备   │
│ Phase 3: 验证       │     │ Phase 2: 并行训练   │
│ Phase 4: 部署       │     │ Phase 3: 系统集成   │
│ Phase 5: 运维       │     │                     │
└─────────────────────┘     └─────────────────────┘
      ↑                           ↑
      │                           │
   Agent 生命周期              技能生命周期
```

- **Agent 创建框架** 定义如何创建和管理 Agent
- **技能训练框架** 定义如何训练和优化技能
- 两者在 Phase 2 (训练阶段) 交汇

---

## 十二、版本升级历史

| 版本 | 发布日期 | 核心变更 | 成熟度 |
|------|---------|---------|--------|
| v3.0 | 2026-05-08 | 新增 L0 层业务目标深度分析阶段，新增 Phase 6 自进化阶段，Jerry 升级为「智能体团队创建者」 | 98% |
| v2.0 | 2026-04-12 | 完整的Agent生命周期6阶段管理 | 85% |
| v1.0 | 2026-04-08 | 初始版本，Agent创建基础流程 | 70% |

---

_创建时间: 2026-04-12 14:32 | 版本: v3.0 | 最后更新: 2026-05-08 | 作者: Jerry 🦞（智能体团队创建者）_
