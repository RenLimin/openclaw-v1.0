# TOOLS.md - 本地工具配置

## 网络代理

| 项目 | 值 | 备注 |
|------|-----|------|
| 备份代理端口 | 7897 | 默认关闭，仅在直连失败时启用 |
| Git 代理 | `http://127.0.0.1:7897` | 当前已配置 |
| 系统代理 | `127.0.0.1:7897` | 已配置但未启用 |

## Gateway

| 项目 | 值 |
|------|-----|
| 地址 | `ws://127.0.0.1:18789` |
| Control UI | `http://127.0.0.1:18789/` |
| 绑定 | loopback |
| 认证 | token |

## Git 配置

| 项目 | 值 |
|------|-----|
| 仓库 | `RenLimin/openclaw-workspace` |
| 备份仓库 | `RenLimin/openclaw-backup` |
| 用户 | Jerry <jerry@openclaw> |
| 代理 | `http://127.0.0.1:7897` |

## GitHub

| 项目 | 值 |
|------|-----|
| 用户 | RenLimin |
| Token 位置 | Keychain: `gh:github.com` |
| Token 类型 | PAT (gho_) |

## Keychain 条目

| 条目名 | 用途 | 状态 |
|--------|------|------|
| `gh:github.com` | GitHub CLI 认证 | ✅ 已配置 |
| `openclaw-github` | OpenClaw 备份推送 | ✅ 已配置 |

---

_本地配置速查表，随环境变化更新_
