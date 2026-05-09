# Luna 监控运维框架 v1.0

定时任务调度器 + 系统健康度监控与告警

## 功能特性

### 第一部分：定时任务调度器

1. **Cron 表达式解析器** - 支持标准 6 字段 Cron
   - 格式：`秒 分 时 日 月 周`
   - 支持通配符 `*`、范围 `a-b`、步长 `*/n`、逗号分隔值

2. **任务管理 API**
   - `add_task(name, cron, command, timeout, max_retries)` - 添加任务
   - `remove_task(task_id)` - 移除任务
   - `list_tasks()` - 列出所有任务
   - `get_task(task_id)` - 获取任务详情

3. **任务执行日志**
   - 存入数据库 `task_execution_logs` 表
   - 记录开始/结束时间、状态、结果、错误信息
   - 支持查询任务历史日志

4. **任务状态管理**
   - PENDING - 等待执行
   - RUNNING - 运行中
   - SUCCESS - 成功
   - FAILED - 失败
   - TIMEOUT - 超时

5. **并发控制与超时机制**
   - 最大并发任务数：5
   - 支持每个任务独立超时配置
   - 超时自动终止任务进程

### 第二部分：系统健康度监控与告警

1. **系统指标监控**
   - CPU 使用率
   - 内存使用率
   - 磁盘使用率
   - 网络流量（入/出）

2. **业务指标监控**
   - 合同数
   - 项目数
   - 报表生成数
   - LLM 调用次数

3. **告警规则引擎**
   - 支持阈值配置
   - 支持多种比较运算符：`>`, `>=`, `<`, `<=`, `==`
   - 告警级别：INFO / WARN / ERROR / FATAL

4. **告警通知渠道**
   - 控制台实时输出
   - 日志文件持久化（`alerts.log`）
   - 数据库存储告警历史

5. **告警静默与升级机制**
   - 支持按时间静默指定告警
   - 1小时内重复告警自动升级级别

## 文件结构

```
skills/luna/
├── __init__.py          # 模块初始化
├── __main__.py          # 主入口
├── database.py          # 数据库模型和操作
├── cron_parser.py       # Cron 表达式解析器
├── scheduler.py         # 调度器核心
├── monitor.py           # 监控与告警
├── requirements.txt     # 依赖列表
├── README.md            # 本文档
├── SKILL.md             # Skill 描述
├── tests/               # 测试用例
│   ├── test_cron_parser.py
│   ├── test_scheduler.py
│   └── test_monitor.py
└── alerts.log           # 告警日志（运行时生成）
```

## 安装与配置

```bash
# 安装依赖
pip install -r skills/luna/requirements.txt

# 或单独安装
pip install psutil
```

## CLI 使用说明

### 定时任务调度器

```bash
# 查看帮助
python -m skills.luna.scheduler

# 启动调度器
python -m skills.luna.scheduler start

# 添加任务 (每天凌晨2点执行备份)
python -m skills.luna.scheduler add backup "0 0 2 * * *" "tar -czf backup.tar.gz /data"

# 列出所有任务
python -m skills.luna.scheduler list

# 查看任务日志
python -m skills.luna.scheduler logs

# 测试 Cron 表达式
python -m skills.luna.scheduler test "0 0 2 * * *"

# 移除任务
python -m skills.luna.scheduler remove <任务ID>
```

### 系统健康度监控

```bash
# 查看帮助
python -m skills.luna.monitor

# 执行一次性检查
python -m skills.luna.monitor check

# 启动持续监控（每30秒检查一次）
python -m skills.luna.monitor start 30

# 查看监控状态
python -m skills.luna.monitor status

# 列出告警规则
python -m skills.luna.monitor rules

# 添加自定义告警规则
python -m skills.luna.monitor add-rule '{"name":"高CPU","level":"ERROR","metric":"cpu_percent","threshold":90,"operator":">"}'

# 静默告警60分钟
python -m skills.luna.monitor silence "高CPU" 60

# 查看最近24小时告警
python -m skills.luna.monitor alerts 24
```

## 数据库表结构

所有数据存入统一数据库 `delivery_management.db`：

- `task_execution_logs` - 任务执行日志
- `scheduled_tasks` - 定时任务配置
- `system_metrics` - 系统监控指标
- `business_metrics` - 业务指标
- `alert_logs` - 告警日志

## API 编程接口

### 调度器 API

```python
from skills.luna.scheduler import get_scheduler

scheduler = get_scheduler()

# 启动调度器
scheduler.start()

# 添加任务
task_id = scheduler.add_task(
    name="daily-backup",
    cron_expression="0 0 2 * * *",
    command="backup.sh",
    timeout=300,
    max_retries=3
)

# 列出任务
tasks = scheduler.list_tasks()

# 停止调度器
scheduler.stop()
```

### 监控 API

```python
from skills.luna.monitor import get_monitor, AlertRule

monitor = get_monitor()

# 执行一次检查
result = monitor.check_once()
print(result['system'])
print(result['business'])

# 启动持续监控
monitor.start(interval=60)

# 添加自定义告警规则
monitor.add_alert_rule(AlertRule(
    name="高内存告警",
    level="WARN",
    metric="memory_percent",
    threshold=85,
    operator=">"
))
```

## Cron 表达式示例

| 表达式 | 说明 |
|--------|------|
| `* * * * * *` | 每秒执行 |
| `0 * * * * *` | 每分钟执行 |
| `0 0 * * * *` | 每小时执行 |
| `0 0 2 * * *` | 每天凌晨2点 |
| `0 0 2 * * 1` | 每周一凌晨2点 |
| `0 0 2 1 * *` | 每月1号凌晨2点 |
| `0 */5 * * * *` | 每5分钟执行 |

## 默认告警规则

| 规则名 | 级别 | 指标 | 阈值 |
|--------|------|------|------|
| CPU使用率过高 | WARN | cpu_percent | > 80% |
| CPU使用率严重过高 | ERROR | cpu_percent | > 95% |
| 内存使用率过高 | WARN | memory_percent | > 80% |
| 内存使用率严重过高 | ERROR | memory_percent | > 95% |
| 磁盘使用率过高 | WARN | disk_percent | > 85% |
| 磁盘使用率严重过高 | ERROR | disk_percent | > 95% |
| LLM调用频繁 | INFO | llm_call_count | > 100 |

## 测试

```bash
# 运行所有测试
python -m pytest skills/luna/tests/ -v

# 或单独运行
python skills/luna/tests/test_cron_parser.py
python skills/luna/tests/test_scheduler.py
python skills/luna/tests/test_monitor.py
```

## 注意事项

1. **数据持久化** - 所有任务配置和监控数据自动存入 SQLite 数据库
2. **任务恢复** - 调度器重启后自动加载之前注册的任务
3. **并发限制** - 默认最多同时运行5个任务，可在代码中调整
4. **时区** - Cron 表达式使用系统本地时区
5. **权限** - 某些系统指标收集可能需要管理员权限
