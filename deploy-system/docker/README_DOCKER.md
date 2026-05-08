# 🐳 Docker 容器化部署指南 v1.0

> **适用环境：** Linux / macOS / Windows (WSL2)
> **部署时间：** 5 分钟内完成

---

## 🚀 一键启动（推荐）

### 第1步：准备环境

```bash
# 克隆代码
git clone https://github.com/RenLimin/openclaw-v1.0.git
cd openclaw-v1.0/deploy-system/docker

# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（填入你的 API Key 等配置）
vim .env
```

### 第2步：启动服务

```bash
# 基础版（仅 OpenClaw 主服务）
docker-compose up -d

# 完整版（含 Prometheus + Grafana 监控）
docker-compose --profile monitoring up -d
```

### 第3步：验证服务

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f openclaw

# 健康检查
curl http://localhost:8080/health
```

✅ **服务启动成功！**

---

## 📦 启动方式说明

| 启动方式 | 命令 | 包含服务 | 适用场景 |
|---------|------|---------|---------|
| 基础版 | `docker-compose up -d` | OpenClaw 主服务 | 日常使用 |
| 完整版 | `docker-compose --profile monitoring up -d` | 主服务 + Prometheus + Grafana | 生产环境 |
| 开发版 | `docker-compose -f docker-compose.dev.yml up` | 开发模式（热重载） | 开发调试 |
| 生产版 | `docker-compose -f docker-compose.prod.yml up -d` | 资源限制 + 完整监控 | 生产部署 |

---

## 🔧 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 停止并删除容器 + 数据卷（⚠️ 慎用！）
docker-compose down -v
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f openclaw
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

### 进入容器

```bash
# 进入 OpenClaw 主容器
docker-compose exec openclaw bash

# 执行 Python 脚本
docker-compose exec openclaw python scripts/health_check.py
```

---

## 📊 监控系统使用

### 访问监控面板

启动完整版后，访问：
- **Grafana 看板：** http://localhost:3000 (默认账号: admin / admin)
- **Prometheus：** http://localhost:9090

### 默认监控指标

- 系统资源：CPU、内存、磁盘使用率
- API 调用：成功率、响应时间、调用次数
- 成本统计：每日/每月 Token 消耗
- Agent 状态：活跃 Agent 数、任务完成率

---

## 🔄 版本升级

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d
```

---

## 💾 数据持久化

### 数据卷位置

| 数据类型 | 容器内路径 | 说明 |
|---------|-----------|------|
| 核心配置 | /app/core-config | 只读挂载 |
| 记忆数据 | /app/memory | 可读写 |
| 知识库 | /app/knowledge-base | 只读挂载 |
| 业务数据 | /app/data | 可读写 |
| Prometheus 数据 | /prometheus | 监控数据 |
| Grafana 数据 | /var/lib/grafana | 看板配置 |

### 数据备份

```bash
# 备份记忆数据
docker cp openclaw-main:/app/memory ./backup/memory-$(date +%Y%m%d)

# 备份完整数据卷
docker run --rm -v openclaw-prometheus-data:/data -v $(pwd)/backup:/backup alpine tar czf /backup/prometheus-$(date +%Y%m%d).tar.gz -C /data .
```

---

## 🔐 安全建议

1. **修改默认密码：** 生产环境务必修改 Grafana 默认密码
2. **限制访问：** 管理端口只绑定到 127.0.0.1，不对外暴露
3. **使用 HTTPS：** 生产环境建议配置反向代理 + SSL
4. **定期备份：** 配置自动备份任务，每日备份关键数据
5. **密钥管理：** 敏感信息使用环境变量或加密存储，不提交到 Git

---

## 🐛 故障排查

### 问题：容器启动失败

```bash
# 查看详细日志
docker-compose logs openclaw

# 检查环境变量是否正确配置
cat .env

# 检查端口是否被占用
netstat -tlnp | grep 8080
```

### 问题：健康检查失败

```bash
# 手动执行健康检查脚本
docker-compose exec openclaw python scripts/health_check.py

# 检查网络连接
docker-compose exec openclaw ping api.openai.com
```

---

## 📈 性能优化建议

### 资源限制配置

在 `docker-compose.prod.yml` 中调整：
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'       # 根据服务器 CPU 调整
      memory: 8G        # 根据服务器内存调整
    reservations:
      cpus: '1.0'
      memory: 2G
```

---

**版本：v1.0 | 最后更新：2026-05-08**
