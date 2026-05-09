
# 🧠 记忆管理技能 - 永久知识固化系统

**版本**: v1.0  
**作者**: Jerry 🦞  
**创建日期**: 2026-04-29  
**触发问题**: OA登录核心jumpSystem API在v2重构时丢失，导致反复登录失败

---

## ❓ 为什么需要这个技能？

### 历史教训
| 时间 | 问题 | 损失 |
|------|------|------|
| 2026-04-13 | 首次成功实现OA jumpSystem API登录 | ✅ 功能正常 |
| 2026-04-23 | v2版本重构，错误删除核心API调用 | 🔴 功能完全失效 |
| 2026-04-28 | 29个问题修复，仍未发现根因 | ⚠️ 问题仍隐蔽存在 |
| 2026-04-29 | Rex发现问题，要求建立经验库 | ✅ 问题解决 |

### 核心痛点
- **成功经验不沉淀** - 核心流程只存在于代码，重构时就丢
- **失败教训不记录** - 同样的错误反复发生
- **Rex要求被遗忘** - 反复违反已知要求，信任度下降
- **跨会话知识断层** - 新会话从零开始，效率低下

---

## 📋 技能功能清单

| 命令 | 功能 | 触发时机 | 强制执行 |
|------|------|---------|---------|
| `skill memory-manager memory-check` | 会话启动自检 | 每个会话开始时 | ✅ 必须执行 |
| `skill memory-manager record-requirement "<原文>"` | 记录Rex新要求 | Rex提出要求后10分钟内 | ✅ 必须执行 |
| `skill memory-manager end-session` | 会话结束6项梳理 | 会话结束前 | ✅ 必须执行 |
| `skill memory-manager new-lesson "<名称>"` | 生成经验库 | P0级问题解决后24小时内 | ✅ 必须执行 |
| `skill memory-manager search "<关键词>"` | 语义搜索记忆 | 随时需要时 | ⚪ 可选 |

---

## 🚀 使用方法

### 1. 会话启动 - 必须执行记忆自检

每个新会话开始时，第一句话执行：
```bash
skill memory-manager memory-check
```

检查内容：
- ✅ MEMORY.md 是否包含核心规则
- ✅ 昨天的会话记忆是否已读
- ✅ 是否有需要建立但未建立的经验库

未通过自检禁止开始工作！

### 2. Rex提出新要求 - 10分钟内必须记录

```bash
skill memory-manager record-requirement "耗时较长的任务单独进程执行"
```

⚠️ **重要提醒：必须一字不差地记录原文，绝对不能 paraphrase！**

### 3. P0级问题解决后 - 24小时内生成经验库

```bash
skill memory-manager new-lesson "OA登录核心流程"
```

经验库必须包含：
- ✅ 核心成功流程（不可修改的步骤）
- ✅ 失败教训与根本原因分析
- ✅ 防复发检查清单（修改代码前必须逐项核对）
- ✅ 相关文件与提交记录
- ✅ Rex的特殊要求与提示

### 4. 会话结束前 - 必须完成6项梳理

```bash
skill memory-manager end-session
```

按引导完成以下6项：
1. 🎯 本次会话的核心成果
2. ✅ 本次学到的成功经验
3. ❌ 本次犯的错误与教训
4. 📢 Rex提出的新要求
5. 🔄 需要沉淀到长期记忆/经验库的内容
6. 📋 下次会话的注意事项（给下次的自己写3条提醒）

---

## 🚨 违反规则的后果

| 违反项 | 后果 |
|--------|------|
| 会话启动不执行自检 | 知识断层，新会话从零开始踩坑 |
| Rex要求10分钟内未记录 | 反复违反已知要求，失去信任 |
| P0级问题24小时内不建经验库 | 同样的错误反复发生 |
| 会话结束不梳理记忆 | 成功经验流失，失败教训白交学费 |

---

## 📁 记忆文件结构

```
workspace/
├── MEMORY.md                           # 永久长期记忆
│   ├── Rex的5条+硬性要求                # 绝对不能违反
│   ├── 经验库索引                      # 所有经验库的目录
│   └── 系统架构与核心信息               # 基础常识
│
├── training-reports/
│   └── 经验库-*.md                    # 领域经验库（每个P0问题一个）
│       ├── 经验库-OA登录核心流程.md
│       ├── 经验库-场景1月报生成.md
│       ├── 经验库-子代理使用规范.md
│       └── ...
│
└── memory/
    ├── YYYY-MM-DD.md                  # 每日会话记忆（6项梳理）
    └── 会话记忆模板.md                 # 标准化模板
```

---

## 💡 记忆检索心法

1. **每个问题先搜经验库** - 有没有人踩过这个坑？
2. **每次改代码先查经验库** - 这个功能的核心流程是什么？
3. **每次Rex提要求先记录** - 10分钟内同步到 MEMORY.md
4. **每个会话结束先梳理** - 6项梳理一个都不能少
5. **每个P0问题解决先建库** - 24小时内完成经验沉淀

---

## 🔗 相关文件

- 技能定义: `skills/memory-manager/skill.yml`
- 会话启动自检: `skills/memory-manager/scripts/session_start_check.py`
- Rex要求记录: `skills/memory-manager/scripts/record_requirement.py`
- 会话结束梳理: `skills/memory-manager/scripts/session_end_reminder.py`
- 经验库生成: `skills/memory-manager/scripts/generate_lesson_db.py`
- 记忆搜索: `skills/memory-manager/scripts/search_memory.py`
- 模板文件: `skills/memory-manager/templates/*.md`

---

⚠️ **此技能是所有技能的基础，必须严格执行！违反就是严重失职！** ⚠️
