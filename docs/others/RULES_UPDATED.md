# 🔴 工作目录限制规则更新公告

**更新时间**: 2026-04-25
**更新人**: Rex
**执行范围**: 全部 5 个智能体 + 全部技能 + 全部操作

---

## 🚨 核心规则

**所有 OpenClaw 操作仅限在 `~/.openclaw` 目录（即 `/Users/bangcle/.openclaw`）内进行，除非 Rex 单独发送明确指令授权。**

---

## 📋 已更新文件清单

| 文件 | 版本更新 | 说明 |
|------|---------|------|
| `team-rules/general-rules.md` | v2.0 → v2.1 | 新增 0 级强制规则 + 权限矩阵 + 合规检查流程 |
| `team-rules/security-rules.md` | v2.0 → v2.1 | 新增 0 级最高优先级规则 + 详细权限矩阵 + 违规后果 |
| `team-rules/skill-rules.md` | v2.0 → v2.1 | 新增 0 级强制规则 + 技能输出目录要求 + 违规处理 |
| `team-rules/environment-config.md` | v2.0 → v2.1 | 新增 0 级强制规则 + 标准目录结构 + 路径标准化示例 |

---

## 🔍 检查清单（所有 Agent 必须遵守）

### 执行任何操作前必须检查：

1. ✅ 操作路径是否在 `~/.openclaw/` 或 `/Users/bangcle/.openclaw/` 内？
2. ✅ 如果不在允许范围内，是否获得了 Rex 的明确授权？
3. ✅ 如果获得授权，是否在日志中明确记录了授权来源？

### 文件输出必须遵守：

- ✅ 日志文件 → `~/.openclaw/logs/`
- ✅ 临时文件 → `~/.openclaw/tmp/`
- ✅ 数据文件 → `~/.openclaw/workspace/data/`
- ✅ 报告输出 → `~/.openclaw/workspace/training-reports/`
- ✅ 技能配置 → `~/.openclaw/workspace/skills/{skill-name}/config/`

---

## ⚠️ 违规后果

1. 任何违反此规则的操作，Jerry 有权立即终止执行
2. 违规输出到非法目录的文件必须立即迁移或删除
3. 多次违规将触发 Agent 重新训练流程
4. 违规操作造成的数据损失由违规 Agent 负责回滚恢复

---

## 📝 备注

- 此规则从 **2026-04-25 15:54** 起立即生效
- 所有正在执行中的任务必须立即检查路径合规性
- 所有历史输出文件如有不在 `~/.openclaw/` 内的，由 Jerry 统一整理迁移

---

*公告发布时间: 2026-04-25 15:54*
