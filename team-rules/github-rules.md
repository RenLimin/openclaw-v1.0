# 📦 智能体团队 — GitHub 提交规则 v2.0

**生效日期**: 2026-04-11
**仓库**: `RenLimin/openclaw-workspace`

---

## 1. 仓库结构

```
openclaw-workspace/
├── team-rules/              # 团队统一规则
│   ├── general-rules.md
│   ├── security-rules.md
│   ├── training-rules.md
│   └── github-rules.md
├── agents/                  # 各 agent 独立配置
│   ├── jerry/
│   ├── ella/
│   ├── oliver/
│   ├── aaron/
│   └── iris/
├── skills/                  # 共享技能
├── scripts/                 # 共享脚本
├── memory/                  # Jerry 的记忆
└── IDENTITY.md / USER.md / SOUL.md / MEMORY.md
```

## 2. 提交单元（可独立引用）

每个 agent 是一个**可独立引用的技能包**，包含：

```
agents/{name}/
├── agent/
│   ├── config.json          # agent 配置
│   └── models.json          # 模型配置
├── workspace/
│   ├── skills/              # 专属技能
│   └── scripts/             # 专属脚本
├── memory/
│   └── training-memory.md   # 训练记忆本
└── data/                    # 数据结构定义
```

**引用方式**: 其他系统或 agent 只需引用 `agents/{name}/` 目录即可获取该 agent 的完整能力包。

## 3. Commit Message 格式

```
[{agent-emoji}] {简短描述}

详细说明（可选）
```

**示例**:
```
[🦊] 初始化 Ella 合同管理 agent 配置
[🐘] Oliver ONES API 技能更新 v1.2.0
[🦉] Aaron 经营报告分析技能训练完成
[🐦‍⬛] Iris 邮件分类规则优化
[🦞] Jerry 任务分派流程修复
[📦] 共享技能库同步 - 20260411
```

## 4. 提交频率

### 4.1 自动提交
- 每次训练阶段完成后：**立即提交**
- 规则文件修改后：**立即提交**
- 新技能安装后：**立即提交**

### 4.2 定时提交
- 每 6 小时：自动检查并提交 workspace 变更
- 每周六 22:00：远程全量备份
- 每周日 02:00：本地全量备份

## 5. Git 规则

### 5.1 分支策略
- `main`：唯一分支，所有提交直接到 main
- 不使用 `feat/` 分支，降低管理成本
- 需要回滚时使用 `git revert`，不使用 force push

### 5.2 提交权限
- **规则提交**: 由 Jerry 发起
- **Agent 独立提交**: 满足条件时（见第 6 节），agent 可自行提交
- **每个 agent 的训练成果通过独立 commit 记录**
- commit message 格式见第 3 节

### 5.3 Agent 独立提交权限
满足以下条件时，agent **可以自行提交** GitHub：

1. **技能训练完成**：某个域技能的完整训练阶段完成
2. **阶段性训练完成**：训练记忆本中某个 Phase 标记为完成
3. **技能更新**：技能文件修改（版本号已更新）

**不满足以下条件时，不得自行提交**：
- 训练中途（Phase 未完成）
- 仅修改了非技能文件（由 Jerry 统一处理）
- 未通过健康检查验证

### 5.3 不提交的内容
- `*.sqlite`（数据库文件）
- `*.jsonl`（会话记录，进备份仓库）
- `config/openclaw.json`（含敏感信息）
- `state/`（运行时状态）
- `.openclaw/`（运行时数据）

### 5.4 必须提交的内容
- `team-rules/` 所有文件
- `agents/{name}/agent/` 配置
- `agents/{name}/workspace/skills/` 技能文件
- `agents/{name}/memory/` 训练记忆
- `scripts/` 脚本文件
- `memory/` 记忆文件

## 6. Agent 独立提交流程

### 6.1 触发条件
Agent 在以下时机触发独立提交：
- **技能训练完成**: 该技能所有练习通过，DEPENDENCIES.md 已填写完整
- **阶段性训练完成**: 训练记忆本中某个 Phase 完成
- **技能更新**: 本地修改了技能文件，且版本号已更新

### 6.2 提交流程
```
Agent 训练完成/阶段完成
    │
    ▼
1. 更新 training-memory.md（标记完成）
2. 更新技能 VERSION（如有变更）
3. 更新 _meta.json（lastUpdated, version）
4. 确保 DEPENDENCIES.md 已填写
5. git add agents/{name}/workspace/skills/{skill-name}/
6. git add agents/{name}/memory/training-memory.md
7. git commit -m "[{emoji}] {skill-name} 训练完成 v{version}"
8. git push origin main
```

### 6.3 提交范围
Agent **只能提交自己目录下的文件**：
- ✅ `agents/{name}/workspace/skills/` — 自己的技能
- ✅ `agents/{name}/memory/` — 自己的训练记忆
- ✅ `agents/{name}/agent/config.json` — 自己的配置
- ❌ `agents/{other}/` — 其他 agent 的文件
- ❌ `team-rules/` — 团队规则
- ❌ `skills/` — 共享技能
- ❌ `workspace/memory/` — Jerry 的记忆

### 6.4 提交后动作
- 提交成功后，向 Jerry 汇报：`[{emoji}] {skill-name} 已提交 GitHub v{version}`
- Jerry 更新 `agents/registry.json` 中该 agent 的 `last_active` 和 `status`

### 6.5 冲突处理
- 如果 push 被拒绝（远程有新提交）：
  1. `git pull --rebase origin main`
  2. 解决冲突（如有）
  3. 重新 push
  4. 3 次失败后上报 Jerry

---

## 7. 备份仓库

- **workspace 仓库**: `RenLimin/openclaw-workspace` — 代码和配置
- **备份仓库**: `RenLimin/openclaw-backup` — 包含 session 记录、完整配置等

---

*GitHub 提交规则 v2.0 — 2026-04-11 更新 — 每次提交都是一个检查点*
