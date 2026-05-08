# 路由规则 v2.0

> **核心**: Jerry 为唯一入口（智能体团队创建者），按职责智能分派给对应 Agent
> **版本升级**: v1.0 → v2.0 (2026-05-08) | Jerry 角色升级：智能体团队创建者

---

## 一、消息路由矩阵

| 关键词/意图 | 目标 Agent | 说明 |
|------------|-----------|------|
| **合同、审批、OA、签章、履约** | Ella 🦊 | 泛微OA流程、合同义务跟踪 |
| **项目、进度、ONES、里程碑、风险** | Oliver 🐘 | ONES系统操作、项目统计 |
| **经营、数据、报告、统计、KPI** | Aaron 🦉 | 经营分析、仪表盘、周期性报告 |
| **邮件、巡检、系统状态、技术研究** | Iris 🐦‍⬛ | 智能巡检、邮件管理、自进化 |
| **智能体团队、创建、设计、优化、Agent团队** | Jerry 🦞 | 智能体团队创建、架构设计、优化、训练 |
| **业务目标分析、需求拆解、ROI分析** | Jerry 🦞 | L0层核心能力：深度业务目标分析 |
| **其他、不确定、跨域协调** | Jerry 🦞 | 默认兜底 + 团队协调 |

## 二、通道绑定

当前配置（所有消息统一进入 Jerry）：

| 通道 | 绑定 Agent | 原因 |
|------|-----------|------|
| 企业微信 (wecom) | Jerry (main) | 唯一入口，由 Jerry 分派 |
| 微信小程序 (openclawwechat) | Jerry (main) | 同上 |

> 注意：OpenClaw 不支持按消息内容自动路由到不同 Agent。所有 inbound 先到 Jerry，由 Jerry 识别意图后通过 `sessions_send` 或 `sessions_spawn` 分派。

## 三、Jerry 分派流程

```
Rex 发消息
   │
   ▼
1. Jerry 识别意图
   │
   ├── 通用/协调 → Jerry 直接处理
   │
   ├── 合同/OA → sessions_send → Ella
   │
   ├── 项目/ONES → sessions_send → Oliver
   │
   ├── 经营/数据 → sessions_send → Aaron
   │
   └── 邮件/巡检 → sessions_send → Iris
```

## 四、跨 Agent 协作

### 4.1 协作原则

- **所有跨 Agent 通信经 Jerry 协调**，不直接互相调用
- 协作场景：Ella 需要项目数据 → 请求 Jerry → Jerry 向 Oliver 获取 → 汇总给 Ella
- 结果由 Jerry 汇总后回复 Rex

### 4.2 错误上报

```
Agent 失败 (3次重试)
   │
   ▼
上报 Jerry
   │
   ▼
Jerry 重试 (3次)
   │
   ▼
仍失败 → 上报 Rex
```

## 五、优先级定义

| 级别 | 条件 | 响应时间 | 分派策略 |
|------|------|---------|---------|
| **P0** | 系统崩溃/数据丢失 | 立即 | Jerry 直 + 全员通知 |
| **P1** | 功能异常/认证失败 | 2h 内 | Jerry 直派对应 Agent |
| **P2** | 性能下降/日志未更新 | 24h 内 | 加入待办队列 |

## 六、Agent 技能清单

### Jerry 🦞 (智能体团队创建者 / Agent Team Founder)
**版本：v2.0 | 成熟度：98%**

**核心定位：** 智能体团队创建者，L0-L3四层能力架构

**L0 - 业务目标分析层核心技能：**
- 业务目标深度分析与拆解
- 利益相关者映射与需求对齐
- 风险识别与应对方案
- ROI预估与投资回报分析
- 核心能力需求矩阵

**L1 - 团队规划层核心技能：**
- 智能体团队架构设计（三层架构）
- 专业化角色定义（CrewAI风格）
- 协作流程设计与通信协议
- 权限边界设计与安全闸门

**L2 - 工具执行层核心技能：**
- 🎯 goal_analyzer.py - 业务目标深度分析器
- 🤖 generate_agent.py - 智能体团队生成器
- ✅ validate_agent.py - 质量验证器（S/A/B/C/D五级评级）

**L3 - 自进化层核心技能（设计完成，开发中）：**
- 四阶段成长模型指导（种子期→生长期→成熟期→卓越期）
- 自进化反馈闭环机制
- 性能监控与持续优化建议

**通用技能：**
- 团队协调 (sessions_send/spawn)
- websearch, summarize-pro, code-interpreter
- 记忆管理: openclaw-memory

**0级强制规则：**
> 创建任何智能体团队之前，必须先完成业务目标深度分析并获得用户确认！

### Ella 🦊 (合同管理)
- 专属: oa-approval, contract-management
- 共享: websearch, summarize-pro

### Oliver 🐘 (项目管理)
- 专属: ones-integration
- 共享: websearch, summarize-pro

### Aaron 🦉 (经营计划)
- 专属: business-analysis
- 共享: websearch, summarize-pro, code-interpreter

### Iris 🐦‍⬛ (智能巡检)
- 专属: email-management
- 共享: websearch, summarize-pro
- Agent Loop: 自动巡检（30min 周期）

---

_创建时间: 2026-04-12 | 版本: v1.0_
