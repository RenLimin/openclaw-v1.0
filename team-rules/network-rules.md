# 🌐 智能体团队 — 网络与代理规则 v2.0

**生效日期**: 2026-04-11
**适用范围**: Gateway 配置、所有 agent 的网络访问

---

## 1. 网络架构

```
┌─────────────────────────────────────────────────────┐
│                  Gateway (主代理)                     │
│  地址: 127.0.0.1:18789 (loopback)                   │
│  模式: local                                        │
│  认证: token                                        │
└─────────────────────────────────────────────────────┘
         │                    │                    │
    webchat            Cron 任务            Agent 会话
   (Control UI)       (isolated)          (subagent)
```

## 2. 代理规则

### 2.1 主代理策略
- **默认直连**：所有网络请求默认直连，不走代理
- **代理仅作为备份**：端口 7897 作为备用代理方案

### 2.2 代理配置

| 层级 | 代理地址 | 状态 | 用途 |
|------|----------|------|------|
| Git | `http://127.0.0.1:7897` | ✅ 已启用 | GitHub 克隆/推送备份 |
| 系统 (Wi-Fi) | `127.0.0.1:7897` | ⚠️ 已配置但未启用 | 系统级备用 |
| 环境变量 | 未设置 | — | — |
| OpenClaw | 未配置 | — | — |

### 2.3 代理启用条件

仅在以下场景启用代理：

1. **GitHub 访问失败**：直连无法 clone/push 时
2. **外部 API 不可达**：模型提供商或外部服务被墙时
3. **Rex 明确要求**：手动指定使用代理

### 2.4 代理切换命令

```bash
# 启用代理（Git）
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897

# 关闭代理（Git）
git config --global --unset http.proxy
git config --global --unset https.proxy

# 启用系统代理
networksetup -setwebproxy Wi-Fi 127.0.0.1 7897
networksetup -setsecurewebproxy Wi-Fi 127.0.0.1 7897
networksetup -setwebproxystate Wi-Fi on
networksetup -setsecurewebproxystate Wi-Fi on

# 关闭系统代理
networksetup -setwebproxystate Wi-Fi off
networksetup -setsecurewebproxystate Wi-Fi off
```

### 2.5 Agent 代理规则

- Agent 默认不配置代理
- 如需代理访问外部服务，由 Jerry 动态配置环境变量
- 代理使用记录到日志

## 3. Gateway 访问

### 3.1 本地访问
- **地址**: `ws://127.0.0.1:18789`
- **Control UI**: `http://127.0.0.1:18789/`
- **绑定**: loopback（仅本地）

### 3.2 远程访问（未来规划）
- **方案 A**: SSH 隧道（推荐，最安全）
- **方案 B**: Tailscale（需开启 Tailscale）
- **当前状态**: 未配置远程访问

## 4. 安全规则

- Gateway 仅绑定 loopback，不暴露到局域网
- 远程访问优先使用 SSH 隧道，不修改 bind 地址
- `gateway.controlUi.allowInsecureAuth` 仅用于本地调试，生产环境应关闭
- 不配置 `gateway.trustedProxies`（无反向代理需求）

---

*网络与代理规则 v2.0 — 2026-04-11 — 默认直连，7897 为备份*
