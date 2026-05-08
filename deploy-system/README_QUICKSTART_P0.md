# 🚀 P0 智能体系统快速部署指南

> **使用者：** 用户（系统管理员）
> **定位：** 30分钟内从零搭建一套完整的 OpenClaw 智能体系统
> **版本：** v1.0.0

---

## 🎯 一句话说明

拿到一台新服务器，只需 3 步，就能跑起来一套完整的 OpenClaw 智能体系统！

---

## 📋 前置要求

| 项目 | 最低要求 |
|------|---------|
| 操作系统 | Linux / macOS |
| Python | 3.8+ |
| Git | 已安装 |
| 内存 | 4GB+ |
| 磁盘 | 20GB+ 可用空间 |

---

## 🚀 三步快速部署

### 第1步：克隆部署包

```bash
git clone https://github.com/RenLimin/openclaw-v1.0.git
cd openclaw-v1.0/deploy-system
```

### 第2步：执行一键安装

```bash
# 方式一：全自动安装
./install.sh

# 方式二：手动分步安装（推荐）
# 1. 安装依赖
pip install -r requirements.txt

# 2. 复制配置模板
cp config-templates/*.md ../core-config/

# 3. 个性化配置
# 编辑 ../core-config/IDENTITY.md - 配置 Agent 身份
# 编辑 ../core-config/AGENT.md - 配置 Agent 行为规则
```

### 第3步：启动系统

```bash
./start.sh
```

访问 http://localhost:8080 即可使用！

---

## 📦 部署包内容说明

```
deploy-system/
├── README_QUICKSTART_P0.md          # 本文档
├── install.sh                        # 一键安装脚本
├── start.sh                          # 系统启动脚本
├── stop.sh                           # 系统停止脚本
├── requirements.txt                  # Python 依赖
│
├── config-templates/                 # 配置模板
│   ├── AGENT.md.template            # Agent 行为规则模板
│   ├── IDENTITY.md.template         # Agent 身份定义模板
│   ├── MEMORY.md.template           # 长期记忆模板
│   ├── SOUL.md.template             # 灵魂/价值观模板
│   └── USER.md.template             # 用户偏好模板
│
├── bootstrap/                        # 启动引导脚本
│   ├── init_system.py                # 系统初始化
│   └── check_env.py                  # 环境检查
│
└── VERSION                           # 部署包版本号
```

---

## 🔧 配置说明

### 必须修改的配置

1. **`core-config/IDENTITY.md`**
   - 修改 Agent 名称、角色、描述
   - 设定你的 Agent 的人格特质

2. **`core-config/SOUL.md`**
   - 设定使命、愿景、价值观
   - 这是 Agent 的灵魂核心

3. **`core-config/AGENT.md`**
   - 设定行为规则、工作流程
   - 根据实际业务需求调整

---

## 📊 部署验证

部署完成后，执行：

```bash
./healthcheck.sh
```

看到以下输出即为成功：
```
✅ Python 环境：正常
✅ 配置文件：完整
✅ 依赖包：已安装
✅ 网络连接：正常
🚀 OpenClaw 系统部署完成！版本：v1.0.0
```

---

## 🔄 版本升级

```bash
# 拉取最新部署包
git pull origin main

# 执行升级脚本
./upgrade.sh
```

---

## ❓ 常见问题

### Q: 部署失败怎么办？
A: 先执行 `./bootstrap/check_env.py` 检查环境，根据提示修复问题后重试。

### Q: 如何备份配置？
A: 整个 `core-config/` 目录打包备份即可。

### Q: 如何升级到 P1/P2/P3？
A: 系统部署完成（P0）后，由 Jerry 智能体自动处理 P1-P3 团队创建工作。

---

## 📞 获取帮助

- 查看 `../roadmap/智能体进阶规划_v3.10.0.md` 获取完整方法论
- 提交 Issue 到 GitHub

---

**版本：v1.0.0 | 最后更新：2026-05-08**
