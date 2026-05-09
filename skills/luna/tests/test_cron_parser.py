"""
Cron 表达式解析器测试用例
"""

import unittest
from datetime import datetime, timedelta

from skills.luna.cron_parser import CronParser, format_next_runs


class TestCronParser(unittest.TestCase):

    def test_valid_expression(self):
        """测试有效 Cron 表达式"""
        expressions = [
            "* * * * * *",  # 每秒
            "0 * * * * *",  # 每分钟
            "0 0 * * * *",  # 每小时
            "0 0 2 * * *",  # 每天2点
            "0 0 2 1 * *",  # 每月1号2点
            "0 0 2 * * 1",  # 每周一2点
            "*/5 * * * * *",  # 每5秒
        ]
        for expr in expressions:
            parser = CronParser(expr)
            self.assertIsNotNone(parser)

    def test_invalid_expression(self):
        """测试无效 Cron 表达式"""
        invalid_expressions = [
            "* * * * *",  # 缺少字段
            "* * * * * * *",  # 字段过多
            "60 * * * * *",  # 秒超出范围
            "* 60 * * * *",  # 分超出范围
        ]
        for expr in invalid_expressions:
            with self.assertRaises(ValueError):
                CronParser(expr)

    def test_field_parsing(self):
        """测试字段解析"""
        parser = CronParser("0 30 2 * * *")

        self.assertEqual(parser.fields['second'], {0})
        self.assertEqual(parser.fields['minute'], {30})
        self.assertEqual(parser.fields['hour'], {2})

    def test_wildcard_parsing(self):
        """测试通配符解析"""
        parser = CronParser("* * * * * *")

        self.assertEqual(len(parser.fields['second']), 60)
        self.assertEqual(len(parser.fields['minute']), 60)
        self.assertEqual(len(parser.fields['hour']), 24)

    def test_step_parsing(self):
        """测试步长解析"""
        parser = CronParser("*/10 * * * * *")

        expected = {0, 10, 20, 30, 40, 50}
        self.assertEqual(parser.fields['second'], expected)

    def test_range_parsing(self):
        """测试范围解析"""
        parser = CronParser("0 0 9-17 * * *")

        expected = set(range(9, 18))
        self.assertEqual(parser.fields['hour'], expected)

    def test_multiple_values(self):
        """测试多值解析"""
        parser = CronParser("0 0 1,3,5 * * *")

        self.assertEqual(parser.fields['hour'], {1, 3, 5})

    def test_should_run(self):
        """测试 should_run 方法"""
        parser = CronParser("* * * * * *")

        # 每秒执行的表达式应该总是返回 True
        self.assertTrue(parser.should_run())

    def test_next_run_time(self):
        """测试 next_run_time 方法"""
        parser = CronParser("0 * * * * *")

        after = datetime(2024, 1, 1, 12, 30, 15)
        next_run = parser.next_run_time(after)

        self.assertEqual(next_run.second, 0)
        self.assertEqual(next_run.minute, 31)
        self.assertEqual(next_run.hour, 12)

    def test_month_names(self):
        """测试月份名称"""
        parser = CronParser("0 0 0 * JAN *")
        self.assertIn(1, parser.fields['month'])

    def test_weekday_names(self):
        """测试星期名称"""
        parser = CronParser("0 0 0 * * MON")
        self.assertIn(1, parser.fields['weekday'])

    def test_format_next_runs(self):
        """测试 format_next_runs 函数"""
        runs = format_next_runs("0 * * * * *", count=5)
        self.assertEqual(len(runs), 5)

        # 检查运行时间是否按顺序递增
        for i in range(1, len(runs)):
            self.assertTrue(runs[i] > runs[i - 1])

    def test_str_representation(self):
        """测试 __str__ 方法"""
        expr = "0 0 2 * * *"
        parser = CronParser(expr)
        self.assertEqual(str(parser), expr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
