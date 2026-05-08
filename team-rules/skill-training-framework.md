# 技能训练框架 v2.0

> 设计原则：高内聚、低耦合、全自动化、可独立提交 GitHub、可共享安装

---

## 一、技能目录结构

### 1.1 全局共享技能（所有 Agent 可用）

```
~/.openclaw/workspace/skills/          # 全局技能目录
├── <skill-name>/
│   ├── SKILL.md                       # 技能说明 + 触发条件
│   ├── _meta.json                     # ClawHub 元数据（自动管理）
│   ├── scripts/                       # 自动化脚本
│   │   └── *.sh / *.py
│   └── references/                    # 参考资料
│       └── *.md
└── ...
```

### 1.2 Agent 专属技能（按职责隔离）

```
~/.openclaw/agents/{ella,oliver,aaron,iris}/workspace/skills/
├── <domain-skill>/
│   ├── SKILL.md
│   ├── _meta.json
│   └── ...
└── ...
```

### 1.3 技能元数据规范

每个技能根目录必须包含 `_meta.json`：

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "source": "clawhub|bundled|custom",
  "sourceRef": "clawhub-slug | git-url",
  "installedAt": "2026-04-12T06:00:00+08:00",
  "autoUpdate": true,
  "dependencies": ["bin1", "bin2"],
  "category": "core|search|coding|domain"
}
```

### 1.4 DEPENDENCIES.md 规范

每个技能目录或 `team-rules/templates/` 提供模板：

```markdown
# <Skill Name> Dependencies

## 二进制依赖
- `cli-tool`: 安装方式 / 版本要求

## 配置依赖
- API Key 名称及存储位置
- 环境变量

## 运行时依赖
- Node.js / Python 版本要求
```

---

## 二、技能分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    L0: 核心引擎层 (Core)                      │
│  self-improving | proactive | memory | context | prompt      │
├─────────────────────────────────────────────────────────────┤
│                  L1: 安全 & 工具层 (Safety & Tools)            │
│  skill-vetter | skill-creator | shell | code-interpreter      │
├─────────────────────────────────────────────────────────────┤
│                  L2: 信息获取层 (Information)                  │
│  tavily | websearch | summarize | ontology | doc-learning    │
├─────────────────────────────────────────────────────────────┤
│               L3: 质量保障层 (Quality Assurance)               │
│  systematic-debugging | feedback-mastery | test-driven       │
├─────────────────────────────────────────────────────────────┤
│               L4: 领域技能层 (Domain - Per Agent)             │
│  Ella: OA审批 | 合同解析 | 法务检索                           │
│  Oliver: ONES操作 | 项目跟踪 | 里程碑管理                      │
│  Aaron: 经营分析 | 预算编制 | 报表生成                         │
│  Iris: 邮件管理 | 日程安排 | 信息整理                          │
└─────────────────────────────────────────────────────────────┘
```

**依赖关系**：上层依赖下层。L4 领域技能 → L0~L3 基础能力 → Agent 运行时。

---

## 三、技能安装方案

### 3.1 安装方式优先级

| 优先级 | 方式 | 命令 | 说明 |
|--------|------|------|------|
| 1 | `openclaw skills install` | `openclaw skills install <slug>` | 官方推荐，自动写入 `_meta.json` |
| 2 | `clawhub install` | `clawhub install <slug> --dir <path>` | 指定安装路径 |
| 3 | 手动 Clone | `git clone` + 编写 SKILL.md | 自定义技能 |

### 3.2 安装位置决策树

```
技能是否 Agent 专属？
├─ 否 → 安装到 ~/.openclaw/workspace/skills/ (全局共享)
└─ 是 → 安装到 ~/.openclaw/agents/{name}/workspace/skills/
```

### 3.3 ClawHub 技能推荐选择

基于搜索结果，各技能推荐版本：

| 需求 | 推荐 Slug | 评分 | 理由 |
|------|-----------|------|------|
| 自我进化 | `self-improving` | 3.46 | 综合版，含主动触发 |
| 主动 Agent | `proactive-agent-lite` | 3.79 | 轻量、高评分 |
| 记忆管理 | `openclaw-memory` | 3.56 | OpenClaw 原生适配 |
| 上下文增强 | `context-scope-tags` | 3.48 | 标签化上下文管理 |
| 提示词优化 | `prompt-enhancer` | 2.59 | 可用选项 |
| 技能创建 | `skill-creator` | — | 已内置 ✅ |
| 技能审核 | `openclaw-skill-vetter` | 3.66 | OpenClaw 官方出品 |
| Tavily 搜索 | `openclaw-tavily-search` | 3.78 | OpenClaw 官方适配 |
| 网页搜索 | `websearch-free-skill` | 3.45 | 免费可用 |
| 总结提炼 | `summarize` | — | 需验证安装名 |
| 知识图谱 | `ontology` | 3.46 | 基础本体论 |
| Shell | `claw-shell` | 3.57 | ClawHub 高评分 |
| 代码解释器 | 手动编写 | — | 无合适现成技能 |
| 调试 | `runesleo-systematic-debugging` | 3.69 | 高评分 |
| 反馈大师 | `feedback-loop` | 3.31 | 可用 |
| 测试驱动 | `imbeasting-test-driven-development` | 3.49 | 可用 |

---

## 四、自主训练执行协议（核心）

> **核心原则：训练的核心目的是全自动化实现。**
> Agent 不是执行指令的工具，而是能自主规划、自主执行、自主解决问题的智能体。

### 4.1 两阶段执行模型

```
输入数据 + 训练目标
       │
       ▼
┌──────────────────────────────────┐
│  Phase A: 自动生成处理方案        │
│  (Agent 自主规划)                │
│  1. 理解训练目标                  │
│  2. 分析输入数据                  │
│  3. 生成执行方案                  │
│  4. 标注风险/不确定性             │
│  5. 提交 Rex 审阅                 │
└──────────────────────────────────┘
       │
       ▼
    Rex 审阅通过？
   ╱            ╲
  是              否 → 退回修改，重新生成方案
  │
  ▼
┌──────────────────────────────────┐
│  Phase B: 自主执行                │
│  (Agent 全自动化)                │
│  1. 按方案执行训练任务            │
│  2. 遇技术瓶颈 → 自行研究解决     │
│  3. 查找可用技能 → 安装/创建      │
│  4. 记录测试方案 & 执行效果       │
│  5. 完成后自动复盘                │
└──────────────────────────────────┘
```

### 4.2 Phase A: 方案生成规范

Agent 收到训练任务后，必须先生成处理方案，格式如下：

```markdown
# 训练方案: [任务名称]

## 训练目标
- 目标 1
- 目标 2

## 输入数据
- 数据来源:
- 数据格式:
- 数据质量评估:

## 执行步骤
| 步骤 | 操作 | 使用技能 | 预期输出 |
|------|------|---------|---------|
| 1 | ... | ... | ... |

## 风险评估
| 风险 | 可能性 | 应对方案 |
|------|--------|---------|
| ... | 高/中/低 | ... |

## 不确定项
- [ ] 需要 Rex 确认: ...

## 验收标准
- [ ] 标准 1
- [ ] 标准 2
```

### 4.3 Phase B: 自主执行规范

方案通过后，Agent 进入自主执行模式，**无需 Rex 逐条确认**：

#### 4.3.1 正常执行
- 严格按方案步骤执行
- 每步完成后记录执行结果
- 输出写入 `memory/YYYY-MM-DD.md`

#### 4.3.2 遇到技术瓶颈

```
遇到瓶颈
   │
   ▼
1. 尝试已知解决方案（最多 3 次）
   │
   ├── 成功 → 继续执行
   │
   ▼ 失败
2. 自行研究
   ├── 使用 tavily / websearch 搜索
   ├── 使用 `gh search code/repos/issues` 搜索 GitHub 代码/仓库/问题
   ├── 使用 summarize 提炼关键信息
   ├── 查找 ClawHub 是否有可用技能
   │
   ▼
3. 评估研究结果
   ├── 找到方案 → 应用并记录
   ├── 需要新技能 → 使用 skill-creator 创建
   ├── 仍无法解决 → 记录问题详情，上报 Jerry
   │
   ▼
4. 记录测试结果
   ├── 测试了什么
   ├── 成功/失败原因
   ├── 最终采用的方案
   └── 经验教训写入 self-improving
```

#### 4.3.3 技能查找与安装

自主执行过程中，如需要新技能：

```bash
# 1. 搜索 GitHub（代码示例、开源实现、最佳实践）
gh search code "<关键词>" --language python
gh search repos "<关键词>" --stars=">100"
gh search issues "<关键词>"

# 2. 搜索 ClawHub（OpenClaw 专用技能）
clawhub search "<关键词>"

# 3. 安全扫描（必须执行）
openclaw skills info <slug>
# 人工检查技能内容，确认无风险

# 4. 安装
openclaw skills install <slug>

# 5. 记录
# 写入 DEPENDENCIES.md + memory/YYYY-MM-DD.md
```

#### 4.3.4 测试记录规范

每次方案执行完成后，必须生成测试记录：

```markdown
# 测试记录: [任务名称]

## 执行时间
- 开始: HH:MM
- 结束: HH:MM
- 耗时: XX min

## 执行结果
| 步骤 | 预期 | 实际 | 状态 |
|------|------|------|------|
| 1 | ... | ... | ✅/❌ |

## 遇到的问题
- 问题 1: 描述 + 解决方案

## 效果评估
- 目标达成率: XX%
- 自动化程度: 全自动 / 半自动 / 手动
- 可改进点:

## 经验教训
- 学到的新知识:
- 下次可以做得更好:
```

### 4.4 自动化铁律

1. **方案先行**: 永远不要盲目执行，先规划再动手
2. **自主解决**: 方案通过后，能自己搞定的不问 Rex
3. **研究优先**: 遇到瓶颈先自己查，查不到再上报
4. **记录一切**: 不记录 = 没发生
5. **复盘迭代**: 每次训练后必须 self-improving 复盘

### 4.5 Rex 审阅职责

Rex 在 Phase A 的职责：
- ✅ 审查方案合理性
- ✅ 指出已知风险和替代方案
- ✅ 确认不确定项
- ✅ 批准后进入 Phase B（不再逐条确认）

Rex **不**在 Phase B 的职责：
- ❌ 逐条确认执行步骤
- ❌ 解决技术细节问题
- ❌ 手动协助执行

---

## 五、全自动化实现方案

### 4.1 自动化目标

每个技能必须实现 **"安装即可用，触发即执行"**，无需人工干预。

### 4.2 自动化机制

```
触发方式:
├── 用户消息匹配 SKILL.md description → 自动激活
├── Cron 定时任务 → 定期执行
├── Heartbeat 巡检 → 周期性检查
├── 事件驱动 (文件变更/API返回) → 被动响应
└── 子代理编排 → Jerry 分配任务
```

### 4.3 每个技能的自动化清单

| 技能 | 自动化目标 | 触发方式 | 验证方式 |
|------|-----------|---------|---------|
| self-improving | 每次任务后自动复盘、更新策略 | 任务完成事件 | 检查训练日志更新 |
| proactive-agent | 定时巡检、主动发现问题 | Cron/Heartbeat | 检查主动消息记录 |
| memory | 自动索引新文件、清理过期 | 文件变更事件 | `openclaw memory status` |
| context | 维护任务链上下文 | 对话开始/切换 | 检查上下文恢复准确率 |
| prompt-enhance | 自动优化低效 Prompt | 任务失败/重试 | 比较优化前后效果 |
| skill-creator | 按需创建新技能 | 用户请求/任务需要 | 新技能目录 + SKILL.md |
| skill-vetter | 安装前安全扫描 | `clawhub install` 前置 | 扫描报告 |
| tavily | 实时搜索获取信息 | 用户搜索请求 | 搜索结果质量 |
| websearch | 补充多源信息 | 用户搜索请求 | 搜索结果质量 |
| summarize | 长文本自动压缩 | 文件/网页输入 | 摘要完整性 |
| ontology | 构建知识关联 | 新知识输入 | 图谱节点/关系数 |
| shell | 命令自动化执行 | 任务需求 | 命令执行结果 |
| code-interpreter | Python 代码执行 | 数据分析需求 | 代码输出正确性 |
| debugging | 自动排错定位 | 任务失败 | 问题定位准确率 |
| feedback | 收集反馈、评分迭代 | 任务完成 | 反馈记录 |
| test-driven | 技能/任务自动化测试 | 技能安装/更新 | 测试通过率 |

### 4.4 自动化脚本模板

每个技能的 `scripts/` 目录应包含：

```bash
#!/bin/bash
# scripts/auto-<skill-name>.sh
# 自动化执行入口

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="${SKILL_DIR}/logs/$(date +%Y%m%d).log"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_FILE"; }

main() {
    log "Starting <skill-name> automation"
    # 1. 检查依赖
    # 2. 执行核心逻辑
    # 3. 输出结果
    # 4. 记录状态
    log "Completed <skill-name> automation"
}

main "$@"
```

---

## 六、训练阶段规划

### Phase 0: 基础设施（Jerry 执行）

| 步骤 | 任务 | 命令 | 状态 |
|------|------|------|------|
| 0.1 | 安装 ClawHub CLI | `npm i -g clawhub` | ✅ 已完成 |
| 0.2 | 安装 L0 核心技能 | 见下方安装清单 | ⏳ 待执行 |
| 0.3 | 安装 L1 安全工具层 | 见下方安装清单 | ⏳ 待执行 |
| 0.4 | 安装 L2 信息获取层 | 见下方安装清单 | ⏳ 待执行 |
| 0.5 | 安装 L3 质量保障层 | 见下方安装清单 | ⏳ 待执行 |
| 0.6 | 验证所有技能 `openclaw skills check` | — | ⏳ 待执行 |
| 0.7 | 提交 GitHub | `git add && commit && push` | ⏳ 待执行 |

### Phase 1: Agent 环境准备（Jerry 执行）

| 步骤 | 任务 | 状态 |
|------|------|------|
| 1.1 | 为每个 Agent 创建 skills 目录 | ⏳ |
| 1.2 | 安装 Agent 专属领域技能 | ⏳ |
| 1.3 | 配置各 Agent 的 SKILL.md 触发规则 | ⏳ |
| 1.4 | 测试 Agent 技能隔离 | ⏳ |

### Phase 2: 并行训练（Ella/Oliver/Aaron/Iris）

> **每个 Agent 独立执行：Phase A 方案生成 → Rex 审阅 → Phase B 自主执行**

| 阶段 | 内容 | 时长 | 验收 |
|------|------|------|------|
| **Phase A: 方案生成** | Agent 分析训练目标，生成处理方案，提交 Rex | 15min | 方案包含完整步骤、风险、不确定项 |
| **Rex 审阅** | Rex 审查方案合理性，指出已知问题，批准执行 | 10min | 方案通过或有修改意见 |
| **Phase B: 自主执行** | Agent 按方案自动执行，遇瓶颈自行研究解决 | 4-5h | 独立完成全部训练任务 |
| **复盘优化** | self-improving 自动复盘，生成改进计划 | 30min | 写入经验教训到 memory |

#### Phase 2 训练内容（每个 Agent 独立执行）

1. **环境熟悉**: 认识技能目录、检查依赖、生成环境清单
2. **技能测试**: 逐个测试 L0-L3 技能，记录执行效果
3. **领域训练**: 执行领域专属任务（见各 Agent SOUL.md）
4. **实战演练**: 端到端任务流程，从输入到输出
5. **瓶颈研究**: 遇到问题时自行查找解决方案
6. **复盘迭代**: self-improving 复盘，更新策略

### Phase 3: 系统集成

> **跨 Agent 协作，验证端到端自动化**

| 任务 | 验收标准 | 状态 |
|------|---------|------|
| 跨 Agent 协作流程测试 | A → B → C 链路完整，无人工干预 | ⏳ |
| 错误升级链路测试 | Agent 失败 → 自动重试 3 次 → 上报 Jerry → 再重试 | ⏳ |
| 端到端集成测试 | 从输入到输出的全流程自动化 | ⏳ |
| GitHub 自动提交验证 | 训练完成后自动 commit + push | ⏳ |

---

## 七、技能安装执行清单

### L0: 核心引擎层

```bash
# 安装到全局共享
openclaw skills install self-improving
openclaw skills install proactive-agent-lite
openclaw skills install openclaw-memory
openclaw skills install context-scope-tags
openclaw skills install prompt-enhancer
```

### L1: 安全 & 工具层

```bash
# skill-creator 已内置 ✅
openclaw skills install openclaw-skill-vetter
openclaw skills install claw-shell
# code-interpreter: 手动创建（无合适现成技能）
```

### L2: 信息获取层

```bash
openclaw skills install openclaw-tavily-search
openclaw skills install websearch-free-skill
openclaw skills install summarize
openclaw skills install ontology
# pdf/markdown/file: 手动创建文档学习技能
```

### L3: 质量保障层

```bash
openclaw skills install runesleo-systematic-debugging
openclaw skills install feedback-loop
openclaw skills install imbeasting-test-driven-development
```

### L4: 领域技能层（Phase 1 安装）

按 Agent 分配到各自 `~/.openclaw/agents/{name}/workspace/skills/`

---

## 八、GitHub 提交规范

### 7.1 目录归属

| 目录 | 提交者 | 说明 |
|------|--------|------|
| `~/.openclaw/workspace/skills/` | 任意 Agent | 全局共享，独立提交 |
| `~/.openclaw/agents/*/workspace/skills/` | 对应 Agent | Agent 专属 |
| `~/.openclaw/workspace/team-rules/` | Jerry | 团队规则 |

### 7.2 Commit 格式

```
<type>(skill): <skill-name> - <description>

Types: feat | fix | docs | chore | training

Examples:
  feat(skill): install self-improving-agent core engine
  feat(skill): add ella OA approval domain skill
  fix(skill): repair tavily-search API config
  docs(skill): update DEPENDENCIES.md for code-interpreter
  training(ella): phase 2 milestone 1 complete
```

### 7.3 提交粒度

- **每个技能独立 commit**，不批量合并
- 包含：SKILL.md + _meta.json + scripts/ + references/ + DEPENDENCIES.md
- 训练里程碑单独 commit

---

## 九、训练验证标准

### 8.1 技能安装验证

```bash
# 检查技能状态
openclaw skills check

# 验证技能可读
openclaw skills info <skill-name>

# 验证依赖
cat skills/<skill>/DEPENDENCIES.md
```

### 8.2 功能验证

| 验证项 | 方法 | 通过标准 |
|--------|------|---------|
| 触发匹配 | 发送相关消息 | 技能自动激活 |
| 依赖满足 | 检查二进制/API | 无缺失依赖 |
| 自动化执行 | 运行 scripts/*.sh | 退出码 0 |
| 结果输出 | 检查输出/文件 | 符合预期 |

### 9.3 训练完成标准

- [ ] 所有 L0-L3 技能安装并通过 `openclaw skills check`
- [ ] 每个 Agent 的领域技能安装完毕
- [ ] **Phase A**: 每个训练任务都生成了处理方案
- [ ] **Rex 审阅**: 所有方案通过审查
- [ ] **Phase B**: 每个技能执行至少 1 次功能验证（自主执行）
- [ ] 遇到瓶颈时自行研究并记录解决方案
- [ ] 每次方案执行完成生成测试记录
- [ ] self-improving 完成首次复盘
- [ ] 所有变更提交到 GitHub
- [ ] 训练日志写入 `memory/YYYY-MM-DD.md`

---

## 十、风险 & 回退

| 风险 | 应对 |
|------|------|
| ClawHub 技能不兼容 | 使用 `skill-vetter` 预扫描，失败则手动创建 |
| 依赖安装失败 | 记录到 DEPENDENCIES.md，降级到替代方案 |
| 技能冲突 | 每个技能独立目录，不共享文件 |
| 训练卡住 | 3 次重试 → 上报 Jerry → Rex 决策 |
| GitHub 推送失败 | 本地暂存，网络恢复后补推 |

---

_创建时间: 2026-04-12 | 版本: v2.0 | 作者: Jerry 🦞_

---

## 十一、训练规则 (整合自 training-rules.md)

### 11.1 训练阶段

| 阶段 | 内容 | 时长 | 验收 |
|------|------|------|------|
| **Phase A: 方案生成** | Agent 分析训练目标，生成处理方案 | 15min | 方案包含完整步骤、风险、不确定项 |
| **Rex 审阅** | Rex 审查方案合理性，指出已知问题 | 10min | 方案通过或有修改意见 |
| **Phase B: 自主执行** | Agent 按方案自动执行，遇瓶颈自行研究 | 4-5h | 独立完成全部训练任务 |
| **复盘优化** | self-improving 自动复盘 | 30min | 写入经验教训到 memory |

### 11.2 训练内容

1. **环境熟悉**: 认识技能目录、检查依赖、生成环境清单
2. **技能测试**: 逐个测试 L0-L3 技能，记录执行效果
3. **领域训练**: 执行领域专属任务（见各 Agent SOUL.md）
4. **实战演练**: 端到端任务流程，从输入到输出
5. **瓶颈研究**: 遇到问题时自行查找解决方案
6. **复盘迭代**: self-improving 复盘，更新策略

### 11.3 训练完成标准

- [ ] 所有 L0-L3 技能安装并通过 `openclaw skills check`
- [ ] 每个 Agent 的领域技能安装完毕
- [ ] **Phase A**: 每个训练任务都生成了处理方案
- [ ] **Rex 审阅**: 所有方案通过审查
- [ ] **Phase B**: 每个技能执行至少 1 次功能验证（自主执行）
- [ ] 遇到瓶颈时自行研究并记录解决方案
- [ ] 每次方案执行完成生成测试记录
- [ ] self-improving 完成首次复盘
- [ ] 所有变更提交到 GitHub
- [ ] 训练日志写入 `memory/YYYY-MM-DD.md`
