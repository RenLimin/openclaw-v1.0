"""
系统健康度监控与告警模块
支持系统指标监控、业务指标监控、告警规则引擎
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

# 配置日志
LOG_FILE = Path(__file__).parent / "alerts.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

ALERT_LEVELS = ['INFO', 'WARN', 'ERROR', 'FATAL']

# 业务指标名称
BUSINESS_METRICS = {
    'contract_count': '合同数',
    'project_count': '项目数',
    'report_count': '报表生成数',
    'llm_call_count': 'LLM调用次数'
}


class AlertRule:
    """告警规则"""

    def __init__(self, name: str, level: str, metric: str,
                 threshold: float, operator: str = '>=',
                 description: str = None):
        self.name = name
        self.level = level
        self.metric = metric
        self.threshold = threshold
        self.operator = operator
        self.description = description or name

    def evaluate(self, value: float) -> bool:
        """评估规则是否触发"""
        if self.operator == '>=':
            return value >= self.threshold
        elif self.operator == '>':
            return value > self.threshold
        elif self.operator == '<=':
            return value <= self.threshold
        elif self.operator == '<':
            return value < self.threshold
        elif self.operator == '==':
            return value == self.threshold
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'level': self.level,
            'metric': self.metric,
            'threshold': self.threshold,
            'operator': self.operator,
            'description': self.description
        }


class AlertManager:
    """告警管理器"""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.silenced_alerts: Dict[str, datetime] = {}
        self.alert_history: Dict[str, datetime] = {}
        self.escalation_threshold = 3  # 告警N次后升级
        self.load_default_rules()

    def load_default_rules(self):
        """加载默认告警规则"""
        default_rules = [
            AlertRule('CPU使用率过高', 'WARN', 'cpu_percent', 80, '>'),
            AlertRule('CPU使用率严重过高', 'ERROR', 'cpu_percent', 95, '>'),
            AlertRule('内存使用率过高', 'WARN', 'memory_percent', 80, '>'),
            AlertRule('内存使用率严重过高', 'ERROR', 'memory_percent', 95, '>'),
            AlertRule('磁盘使用率过高', 'WARN', 'disk_percent', 85, '>'),
            AlertRule('磁盘使用率严重过高', 'ERROR', 'disk_percent', 95, '>'),
            AlertRule('LLM调用频繁', 'INFO', 'llm_call_count', 100, '>'),
        ]
        for rule in default_rules:
            self.rules[rule.name] = rule

    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules[rule.name] = rule

    def remove_rule(self, rule_name: str) -> bool:
        """移除告警规则"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            return True
        return False

    def silence_alert(self, alert_name: str, minutes: int = 60):
        """静默告警"""
        self.silenced_alerts[alert_name] = datetime.now() + timedelta(minutes=minutes)

    def is_silenced(self, alert_name: str) -> bool:
        """检查告警是否被静默"""
        if alert_name in self.silenced_alerts:
            if datetime.now() < self.silenced_alerts[alert_name]:
                return True
            del self.silenced_alerts[alert_name]
        return False

    def should_escalate(self, alert_name: str) -> bool:
        """检查是否需要升级告警"""
        if alert_name in self.alert_history:
            time_since_first = (datetime.now() - self.alert_history[alert_name]).total_seconds()
            if time_since_first < 3600:  # 1小时内
                # 简单计数逻辑，可以扩展
                pass
        return False

    def trigger_alert(self, rule: AlertRule, value: float):
        """触发告警"""
        if self.is_silenced(rule.name):
            return

        # 记录告警时间
        if rule.name not in self.alert_history:
            self.alert_history[rule.name] = datetime.now()

        # 升级检查
        level = rule.level
        if self.should_escalate(rule.name):
            if level == 'WARN':
                level = 'ERROR'
            elif level == 'ERROR':
                level = 'FATAL'

        message = f"[{level}] {rule.description}: 当前值 {value}, 阈值 {rule.operator}{rule.threshold}"

        # 控制台输出
        print(message)

        # 日志文件
        if level == 'FATAL':
            logging.fatal(message)
        elif level == 'ERROR':
            logging.error(message)
        elif level == 'WARN':
            logging.warning(message)
        else:
            logging.info(message)

        # 保存到数据库
        from .database import save_alert
        save_alert(level, rule.name, message, value, rule.threshold)

    def evaluate_metrics(self, metrics: Dict[str, float]):
        """评估所有指标并触发告警"""
        for rule in self.rules.values():
            if rule.metric in metrics:
                value = metrics[rule.metric]
                if rule.evaluate(value):
                    self.trigger_alert(rule, value)

    def get_rules(self) -> List[Dict[str, Any]]:
        """获取所有规则"""
        return [rule.to_dict() for rule in self.rules.values()]


class SystemMonitor:
    """系统监控器"""

    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.alert_manager = AlertManager()
        self.interval = 60  # 默认60秒检查一次
        self.previous_network = None

    def collect_system_metrics(self) -> Dict[str, float]:
        """收集系统指标"""
        metrics = {}

        try:
            import psutil

            # CPU
            metrics['cpu_percent'] = psutil.cpu_percent(interval=1)

            # 内存
            mem = psutil.virtual_memory()
            metrics['memory_percent'] = mem.percent
            metrics['memory_used_gb'] = mem.used / (1024 ** 3)

            # 磁盘
            disk = psutil.disk_usage('/')
            metrics['disk_percent'] = disk.percent
            metrics['disk_used_gb'] = disk.used / (1024 ** 3)

            # 网络
            net = psutil.net_io_counters()
            if self.previous_network:
                metrics['network_in_mb'] = (net.bytes_recv - self.previous_network['bytes_recv']) / (1024 ** 2)
                metrics['network_out_mb'] = (net.bytes_sent - self.previous_network['bytes_sent']) / (1024 ** 2)
            else:
                metrics['network_in_mb'] = 0
                metrics['network_out_mb'] = 0

            self.previous_network = {
                'bytes_recv': net.bytes_recv,
                'bytes_sent': net.bytes_sent
            }

        except ImportError:
            print("警告: psutil 未安装，无法收集系统指标")
            metrics = {
                'cpu_percent': 0,
                'memory_percent': 0,
                'memory_used_gb': 0,
                'disk_percent': 0,
                'disk_used_gb': 0,
                'network_in_mb': 0,
                'network_out_mb': 0
            }

        return metrics

    def collect_business_metrics(self) -> Dict[str, float]:
        """收集业务指标（模拟）"""
        # 在实际使用中，这里应该从数据库或其他数据源获取
        # 这里返回模拟数据
        return {
            'contract_count': 150,
            'project_count': 25,
            'report_count': 45,
            'llm_call_count': 78
        }

    def check_once(self) -> Dict[str, Any]:
        """执行一次检查"""
        system_metrics = self.collect_system_metrics()
        business_metrics = self.collect_business_metrics()

        # 保存到数据库
        from .database import save_system_metrics, save_business_metric
        save_system_metrics(system_metrics)

        for name, value in business_metrics.items():
            save_business_metric(name, value)

        # 评估告警
        all_metrics = {**system_metrics, **business_metrics}
        self.alert_manager.evaluate_metrics(all_metrics)

        return {
            'system': system_metrics,
            'business': business_metrics,
            'timestamp': time.time()
        }

    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            self.check_once()
            time.sleep(self.interval)

    def start(self, interval: int = 60):
        """启动持续监控"""
        if self.running:
            return False

        self.interval = interval
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        """停止监控"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        return True

    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_manager.add_rule(rule)

    def silence_alert(self, alert_name: str, minutes: int):
        """静默告警"""
        self.alert_manager.silence_alert(alert_name, minutes)

    def get_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        return {
            'running': self.running,
            'interval': self.interval,
            'alert_rules_count': len(self.alert_manager.rules)
        }


# 全局监控实例
_monitor_instance: Optional[SystemMonitor] = None


def get_monitor() -> SystemMonitor:
    """获取全局监控实例"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SystemMonitor()
    return _monitor_instance


def main():
    """CLI 入口"""
    import sys

    if len(sys.argv) < 2:
        print("""
Luna 系统健康度监控 v1.0

用法: python -m skills.luna.monitor <命令> [参数]

命令:
  check              - 执行一次性检查
  start [间隔秒数]     - 启动持续监控
  stop               - 停止监控
  status             - 查看监控状态
  rules              - 列出所有告警规则
  add-rule <JSON>    - 添加告警规则
  silence <告警名> <分钟>
                     - 静默指定告警
  alerts [小时数]     - 查看最近告警日志

示例:
  python -m skills.luna.monitor check
  python -m skills.luna.monitor start 30
  python -m skills.luna.monitor rules
        """)
        return

    monitor = get_monitor()
    command = sys.argv[1]

    if command == 'check':
        print("执行系统检查...")
        result = monitor.check_once()
        print("\n系统指标:")
        for k, v in result['system'].items():
            print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")
        print("\n业务指标:")
        for k, v in result['business'].items():
            print(f"  {k}: {v}")

    elif command == 'start':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"启动持续监控，间隔 {interval} 秒...")
        monitor.start(interval)
        print("监控已启动，按 Ctrl+C 停止")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止...")
            monitor.stop()
            print("监控已停止")

    elif command == 'stop':
        monitor.stop()
        print("监控已停止")

    elif command == 'status':
        status = monitor.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif command == 'rules':
        rules = monitor.alert_manager.get_rules()
        if not rules:
            print("没有配置告警规则")
            return
        for rule in rules:
            print(f"\n[{rule['level']}] {rule['name']}")
            print(f"  指标: {rule['metric']}")
            print(f"  条件: {rule['operator']}{rule['threshold']}")
            print(f"  描述: {rule['description']}")

    elif command == 'add-rule':
        if len(sys.argv) < 3:
            print("用法: python -m skills.luna.monitor add-rule '{\"name\":\"规则名\",\"level\":\"WARN\",\"metric\":\"cpu_percent\",\"threshold\":80,\"operator\":\">\"}")
            return
        try:
            rule_data = json.loads(sys.argv[2])
            rule = AlertRule(
                name=rule_data['name'],
                level=rule_data['level'],
                metric=rule_data['metric'],
                threshold=rule_data['threshold'],
                operator=rule_data.get('operator', '>'),
                description=rule_data.get('description')
            )
            monitor.add_alert_rule(rule)
            print(f"规则 '{rule.name}' 已添加")
        except Exception as e:
            print(f"添加规则失败: {e}")

    elif command == 'silence':
        if len(sys.argv) < 4:
            print("用法: python -m skills.luna.monitor silence <告警名> <分钟>")
            return
        alert_name = sys.argv[2]
        minutes = int(sys.argv[3])
        monitor.silence_alert(alert_name, minutes)
        print(f"告警 '{alert_name}' 已静默 {minutes} 分钟")

    elif command == 'alerts':
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        from .database import get_recent_alerts
        alerts = get_recent_alerts(hours)
        if not alerts:
            print(f"最近 {hours} 小时没有告警")
            return
        for alert in alerts:
            created = datetime.fromtimestamp(alert['created_at'])
            print(f"[{alert['level']}] {alert['rule_name']} - {created}")
            print(f"  {alert['message']}")

    else:
        print(f"未知命令: {command}")


if __name__ == '__main__':
    main()
