"""
监控与告警模块测试用例
"""

import unittest
import time
import tempfile
import os

from skills.luna.monitor import AlertRule, AlertManager, SystemMonitor, get_monitor
from skills.luna.monitor import ALERT_LEVELS


class TestAlertRule(unittest.TestCase):

    def test_alert_rule_creation(self):
        """测试告警规则创建"""
        rule = AlertRule(
            name="高CPU",
            level="WARN",
            metric="cpu_percent",
            threshold=80,
            operator=">",
            description="CPU 使用率过高"
        )

        self.assertEqual(rule.name, "高CPU")
        self.assertEqual(rule.level, "WARN")
        self.assertEqual(rule.metric, "cpu_percent")
        self.assertEqual(rule.threshold, 80)
        self.assertEqual(rule.operator, ">")
        self.assertEqual(rule.description, "CPU 使用率过高")

    def test_evaluate_operators(self):
        """测试各种比较运算符"""
        # >
        rule = AlertRule("test", "WARN", "cpu", 80, ">")
        self.assertTrue(rule.evaluate(90))
        self.assertFalse(rule.evaluate(80))
        self.assertFalse(rule.evaluate(70))

        # >=
        rule = AlertRule("test", "WARN", "cpu", 80, ">=")
        self.assertTrue(rule.evaluate(90))
        self.assertTrue(rule.evaluate(80))
        self.assertFalse(rule.evaluate(70))

        # <
        rule = AlertRule("test", "WARN", "cpu", 80, "<")
        self.assertFalse(rule.evaluate(90))
        self.assertFalse(rule.evaluate(80))
        self.assertTrue(rule.evaluate(70))

        # <=
        rule = AlertRule("test", "WARN", "cpu", 80, "<=")
        self.assertFalse(rule.evaluate(90))
        self.assertTrue(rule.evaluate(80))
        self.assertTrue(rule.evaluate(70))

        # ==
        rule = AlertRule("test", "WARN", "cpu", 80, "==")
        self.assertFalse(rule.evaluate(90))
        self.assertTrue(rule.evaluate(80))
        self.assertFalse(rule.evaluate(70))

    def test_rule_to_dict(self):
        """测试规则序列化"""
        rule = AlertRule(
            name="高CPU",
            level="WARN",
            metric="cpu_percent",
            threshold=80,
            operator=">"
        )

        rule_dict = rule.to_dict()
        self.assertEqual(rule_dict['name'], "高CPU")
        self.assertEqual(rule_dict['level'], "WARN")
        self.assertEqual(rule_dict['threshold'], 80)


class TestAlertManager(unittest.TestCase):

    def setUp(self):
        self.alert_manager = AlertManager()

    def test_default_rules_loaded(self):
        """测试默认规则已加载"""
        rules = self.alert_manager.get_rules()
        self.assertGreater(len(rules), 0)

    def test_add_rule(self):
        """测试添加规则"""
        initial_count = len(self.alert_manager.rules)

        new_rule = AlertRule(
            name="自定义规则",
            level="ERROR",
            metric="memory",
            threshold=90,
            operator=">"
        )
        self.alert_manager.add_rule(new_rule)

        self.assertEqual(len(self.alert_manager.rules), initial_count + 1)
        self.assertIn("自定义规则", self.alert_manager.rules)

    def test_remove_rule(self):
        """测试移除规则"""
        # 先添加一个规则
        new_rule = AlertRule(
            name="要删除的规则",
            level="ERROR",
            metric="memory",
            threshold=90
        )
        self.alert_manager.add_rule(new_rule)

        result = self.alert_manager.remove_rule("要删除的规则")
        self.assertTrue(result)
        self.assertNotIn("要删除的规则", self.alert_manager.rules)

        # 删除不存在的规则
        result = self.alert_manager.remove_rule("不存在的规则")
        self.assertFalse(result)

    def test_silence_alert(self):
        """测试告警静默"""
        self.assertFalse(self.alert_manager.is_silenced("高CPU"))

        self.alert_manager.silence_alert("高CPU", minutes=1)
        self.assertTrue(self.alert_manager.is_silenced("高CPU"))

    def test_evaluate_metrics(self):
        """测试评估指标"""
        metrics = {
            'cpu_percent': 99,  # 应该触发 ERROR 告警
            'memory_percent': 85,  # 应该触发 WARN 告警
        }

        # 这个应该不会抛出异常
        self.alert_manager.evaluate_metrics(metrics)


class TestSystemMonitor(unittest.TestCase):

    def setUp(self):
        self.monitor = SystemMonitor()

    def test_monitor_creation(self):
        """测试监控器创建"""
        self.assertFalse(self.monitor.running)
        self.assertIsNotNone(self.monitor.alert_manager)

    def test_collect_system_metrics(self):
        """测试收集系统指标"""
        metrics = self.monitor.collect_system_metrics()

        # 检查是否收集了所有系统指标
        self.assertIn('cpu_percent', metrics)
        self.assertIn('memory_percent', metrics)
        self.assertIn('memory_used_gb', metrics)
        self.assertIn('disk_percent', metrics)
        self.assertIn('disk_used_gb', metrics)
        self.assertIn('network_in_mb', metrics)
        self.assertIn('network_out_mb', metrics)

    def test_collect_business_metrics(self):
        """测试收集业务指标"""
        metrics = self.monitor.collect_business_metrics()

        self.assertIn('contract_count', metrics)
        self.assertIn('project_count', metrics)
        self.assertIn('report_count', metrics)
        self.assertIn('llm_call_count', metrics)

    def test_check_once(self):
        """测试一次性检查"""
        result = self.monitor.check_once()

        self.assertIn('system', result)
        self.assertIn('business', result)
        self.assertIn('timestamp', result)

    def test_start_stop(self):
        """测试启动和停止监控"""
        self.assertFalse(self.monitor.running)

        result = self.monitor.start(interval=1)
        self.assertTrue(result)
        self.assertTrue(self.monitor.running)

        # 运行一小段时间
        time.sleep(0.5)

        result = self.monitor.stop()
        self.assertTrue(result)
        self.assertFalse(self.monitor.running)

    def test_get_status(self):
        """测试获取状态"""
        status = self.monitor.get_status()

        self.assertIn('running', status)
        self.assertIn('interval', status)
        self.assertIn('alert_rules_count', status)

        self.assertFalse(status['running'])

    def test_add_alert_rule(self):
        """测试添加告警规则"""
        rule = AlertRule(
            name="测试规则",
            level="INFO",
            metric="test",
            threshold=50
        )
        self.monitor.add_alert_rule(rule)

        rules = self.monitor.alert_manager.get_rules()
        rule_names = [r['name'] for r in rules]
        self.assertIn("测试规则", rule_names)


class TestGetMonitor(unittest.TestCase):

    def test_get_singleton(self):
        """测试单例模式"""
        m1 = get_monitor()
        m2 = get_monitor()

        self.assertIs(m1, m2)


class TestAlertLevels(unittest.TestCase):

    def test_alert_levels(self):
        """测试告警级别"""
        expected = ['INFO', 'WARN', 'ERROR', 'FATAL']
        self.assertEqual(ALERT_LEVELS, expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
