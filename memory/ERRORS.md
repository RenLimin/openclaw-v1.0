# ERRORS.md - 错误与异常记录

> **自动维护**：每次命令执行失败、系统异常、训练中断时写入
> **晋升触发**：同类错误重复出现 3 次以上 → 晋升为永久修复规则

---

## 📝 错误记录

---

### [Pattern-Key: doc-version-mismatch]
- **Date**: 2026-05-08
- **Command**: 提交文档变更到 GitHub
- **Error**: 更新智能体进阶规划和 Jerry 进阶计划文档时，修改了内容但未同步更新版本号，也没有同步重命名文件
- **Root-Cause**: 
  1. 没有明确的文档版本管理检查清单
  2. 变更前没有触发检查机制
  3. 版本变更没有标准化 SOP
- **Recurrence-Count**: 1
- **Solution**: 
  - ✅ 已创建 `team-rules/error-trigger-checklist.md` 敏感操作前置检查清单
  - ✅ 文档变更前必须核对清单第一类检查点
  - ✅ 严格遵循 SemVer 语义化版本规范
- **Status**: ✅ 已补充完整根因分析 + 预防机制，错误闭环

---

### [Pattern-Key: github-push-without-approval]
- **Date**: 2026-05-08
- **Command**: `git push origin main`
- **Error**: 直接提交到 GitHub，未事先获得用户明确批准
- **Root-Cause**:
  1. 缺少提交前的强制检查步骤
  2. 用户确认的流程边界不清晰
  3. 错误的提交内容没有先展示变更内容再确认
- **Recurrence-Count**: 1
- **Solution**:
  - ✅ 所有提交前必须先展示变更预览
  - ✅ 必须获得明确的「提交」指令后才能执行 push
  - ✅ 已补充到 error-trigger-checklist.md 第二类检查点
- **Status**: ✅ 已补充完整根因分析 + 预防机制，错误闭环

---

### [Pattern-Key: session-reset-memory-loss]
- **Date**: 2026-05-06
- **Command**: OpenClaw 系统会话 .reset 机制
- **Error**: 会话重置导致训练状态完全丢失，5月5日业务目标训练痕迹全无
- **Root-Cause**: 
  1. 系统 .reset 只归档 `.jsonl`，不触发记忆持久化
  2. 会话内容与 `memory/` 目录完全脱节
  3. 缺少会话结束前的强制保存钩子
- **Recurrence-Count**: 3（4月27日、4月29日、5月5日）
- **Solution**: 
  - ✅ 建立 AGENT.md 强制记忆规则
  - ✅ 会话开始/结束必须读写 `memory/YYYY-MM-DD.md`
  - ✅ 实现记忆系统 v2.0 架构
- **Related-Tasks**: [4月27日场景训练, 4月29日验收, 5月5日业务目标训练]
- **晋升状态**: ✅ 已触发晋升 → 写入 AGENT.md

---

### [Pattern-Key: directory-path-mismatch]
- **Date**: 2026-05-05
- **Command**: `ls /Users/bangcle/.openclaw/workspace/business-driven-skill/`
- **Error**: No such file or directory
- **Root-Cause**: Rex 提及的目录实际在 `/Users/bangcle/.openclaw/business-driven-skill/`，不在 workspace 下
- **Recurrence-Count**: 1
- **Solution**: 已找到正确路径，训练继续
- **晋升状态**: ⏳ 观察中

---

## 📊 统计

| 指标 | 数值 |
|------|------|
| 总错误条目 | 2 |
| 待晋升条目 | 2 |
| 已晋升条目 | 0 |
| 已修复条目 | 2 |
