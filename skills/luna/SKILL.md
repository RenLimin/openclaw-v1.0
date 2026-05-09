---
name: Luna 监控运维框架
description: 定时任务调度器 + 系统健康度监控与告警框架
version: 1.0.0
author: Luna 🌙
category: DevOps
tags:
  - scheduler
  - monitoring
  - alerting
  - cron
  - devops
---

# Luna 监控运维框架 Skill

## 概述

Luna 是一个轻量级的运维监控框架，提供定时任务调度和系统健康度监控能力。

## 核心能力

### 1. 定时任务调度器

- **Cron 表达式解析** - 支持标准 6 字段 Cron 表达式（秒 分 时 日 月 周）
- **任务生命周期管理** - 注册、取消、查询任务状态
- **执行日志记录** - 完整记录任务执行历史
- **并发控制** - 限制同时运行的任务数量
- **超时机制** - 任务超时自动终止
- **自动恢复** - 重启后自动加载已注册的任务

### 2. 系统健康度监控

- **系统指标** - CPU、内存、磁盘、网络
- **业务指标** - 可扩展的业务指标收集
- **告警引擎** - 基于阈值的告警规则
- **多渠道通知** - 控制台、日志文件、数据库
- **静默与升级** - 支持告警静默和自动升级

## 使用场景

1. **周期性任务调度** - 数据备份、报表生成、数据同步
2. **系统监控告警** - 服务器资源监控和异常告警
3. **业务指标统计** - 业务关键指标收集和监控
4. **自动化运维** - 配合其他工具实现自动化运维

## CLI 快速参考

### 调度器命令

```bash
# 启动/停止/状态
python -m skills.luna.scheduler start
python -m skills.luna.scheduler stop
python -m skills.luna.scheduler status

# 任务管理
python -m skills.luna.scheduler add <名称> <cron> <命令>
python -m skills.luna.scheduler remove <任务ID>
python -m skills.luna.scheduler list

# 日志
python -m skills.luna.scheduler logs [任务ID]
python -m skills.luna.scheduler test <cron>
```

### 监控命令

```bash
# 检查/启动/停止
python -m skills.luna.monitor check
python -m skills.luna.monitor start [间隔秒数]
python -m skills.luna.monitor stop
python -m skills.luna.monitor status

# 告警管理
python -m skills.luna.monitor rules
python -m skills.luna.monitor add-rule <JSON>
python -m skills.luna.monitor silence <告警名> <分钟>
python -m skills.luna.monitor alerts [小时数]
```

## 依赖要求

- Python 3.7+
- psutil >= 5.9.0 (用于系统指标收集)

## 数据库集成

自动使用项目根目录下的 `delivery_management.db` SQLite 数据库，创建以下表：

- `task_execution_logs` - 任务执行日志
- `scheduled_tasks` - 定时任务配置
- `system_metrics` - 系统监控指标
- `business_metrics` - 业务指标
- `alert_logs` - 告警历史

## 配置说明

### Cron 表达式格式

```
* * * * * *
│ │ │ │ │ │
│ │ │ │ │ └─ 星期 (0-6, 0=周日)
│ │ │ │ └─── 月份 (1-12)
│ │ │ └───── 日期 (1-31)
│ │ └─────── 小时 (0-23)
│ └───────── 分钟 (0-59)
└─────────── 秒 (0-59)
```

### 告警级别

- **INFO** - 信息提示，无需处理
- **WARN** - 警告，需要关注
- **ERROR** - 错误，需要处理
- **FATAL** - 严重，立即处理

## 扩展开发

### 添加自定义业务指标

在 `monitor.py` 的 `collect_business_metrics()` 方法中添加指标收集逻辑。

### 添加告警通知渠道

在 `AlertManager.trigger_alert()` 方法中扩展通知方式（邮件、短信、Webhook等）。

### 自定义调度器参数

修改 `Scheduler` 类中的 `max_concurrent` 属性调整并发限制。

## 注意事项

1. Cron 表达式使用系统本地时区
2. 长时间运行建议配合 systemd 或 supervisor 管理
3. 生产环境建议配置日志轮转
4. 数据库文件定期备份
5. psutil 在某些系统可能需要编译安装
