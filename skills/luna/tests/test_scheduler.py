"""
调度器模块测试用例
"""

import unittest
import time
import tempfile
import os

from skills.luna.scheduler import Scheduler, Task, get_scheduler
from skills.luna.database import get_task_logs, init_db


class TestTask(unittest.TestCase):

    def test_task_creation(self):
        """测试任务创建"""
        task = Task(
            task_id="test-001",
            name="Test Task",
            cron_expression="* * * * * *",
            command="echo hello",
            timeout=300,
            max_retries=3
        )

        self.assertEqual(task.id, "test-001")
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.cron_expression, "* * * * * *")
        self.assertEqual(task.command, "echo hello")
        self.assertEqual(task.timeout, 300)
        self.assertEqual(task.max_retries, 3)
        self.assertTrue(task.enabled)
        self.assertEqual(task.status, 'PENDING')

    def test_task_should_run(self):
        """测试任务运行条件"""
        task = Task(
            task_id="test-001",
            name="Test Task",
            cron_expression="* * * * * *",
            command="echo hello"
        )

        self.assertTrue(task.should_run())

        # 禁用任务
        task.enabled = False
        self.assertFalse(task.should_run())

    def test_task_to_dict(self):
        """测试任务序列化"""
        task = Task(
            task_id="test-001",
            name="Test Task",
            cron_expression="* * * * * *",
            command="echo hello"
        )

        task_dict = task.to_dict()

        self.assertEqual(task_dict['id'], "test-001")
        self.assertEqual(task_dict['name'], "Test Task")
        self.assertEqual(task_dict['status'], 'PENDING')


class TestScheduler(unittest.TestCase):

    def setUp(self):
        """每个测试前创建新的调度器实例"""
        # 删除现有数据库确保测试隔离
        db_path = '/Users/bangcle/.openclaw/workspace/delivery_management.db'
        if os.path.exists(db_path):
            os.unlink(db_path)

        # 初始化数据库
        init_db()

        # 重置全局调度器实例
        import skills.luna.scheduler as scheduler_module
        scheduler_module._scheduler_instance = None

        self.scheduler = Scheduler()

    def tearDown(self):
        """每个测试后清理"""
        if self.scheduler.running:
            self.scheduler.stop()
        # 清理数据库
        db_path = '/Users/bangcle/.openclaw/workspace/delivery_management.db'
        if os.path.exists(db_path):
            os.unlink(db_path)

    def test_scheduler_creation(self):
        """测试调度器创建"""
        self.assertFalse(self.scheduler.running)
        self.assertEqual(self.scheduler.active_tasks, 0)

    def test_add_task(self):
        """测试添加任务"""
        task_id = self.scheduler.add_task(
            name="Test Task",
            cron_expression="* * * * * *",
            command="echo hello"
        )

        self.assertIsNotNone(task_id)
        self.assertEqual(len(self.scheduler.tasks), 1)

        task = self.scheduler.tasks[task_id]
        self.assertEqual(task.name, "Test Task")

    def test_add_task_invalid_cron(self):
        """测试添加无效 Cron 表达式"""
        with self.assertRaises(ValueError):
            self.scheduler.add_task(
                name="Test Task",
                cron_expression="invalid cron",
                command="echo hello"
            )

    def test_remove_task(self):
        """测试移除任务"""
        task_id = self.scheduler.add_task(
            name="Test Task",
            cron_expression="* * * * * *",
            command="echo hello"
        )

        result = self.scheduler.remove_task(task_id)
        self.assertTrue(result)
        self.assertEqual(len(self.scheduler.tasks), 0)

        # 移除不存在的任务
        result = self.scheduler.remove_task("non-existent")
        self.assertFalse(result)

    def test_list_tasks(self):
        """测试列出任务"""
        for i in range(3):
            self.scheduler.add_task(
                name=f"Task {i}",
                cron_expression="* * * * * *",
                command=f"echo {i}"
            )

        tasks = self.scheduler.list_tasks()
        self.assertEqual(len(tasks), 3)

    def test_get_task(self):
        """测试获取单个任务"""
        task_id = self.scheduler.add_task(
            name="Test Task",
            cron_expression="* * * * * *",
            command="echo hello"
        )

        task = self.scheduler.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task['name'], "Test Task")

        # 获取不存在的任务
        task = self.scheduler.get_task("non-existent")
        self.assertIsNone(task)

    def test_start_stop(self):
        """测试启动和停止调度器"""
        self.assertFalse(self.scheduler.running)

        result = self.scheduler.start()
        self.assertTrue(result)
        self.assertTrue(self.scheduler.running)

        # 重复启动
        result = self.scheduler.start()
        self.assertFalse(result)

        result = self.scheduler.stop()
        self.assertTrue(result)
        self.assertFalse(self.scheduler.running)

    def test_get_status(self):
        """测试获取状态"""
        status = self.scheduler.get_status()

        self.assertIn('running', status)
        self.assertIn('task_count', status)
        self.assertIn('active_tasks', status)
        self.assertIn('max_concurrent', status)

        self.assertFalse(status['running'])
        self.assertEqual(status['task_count'], 0)

    def test_task_execution_log(self):
        """测试任务执行日志记录"""
        from skills.luna.database import log_task_start, log_task_finish

        task_id = self.scheduler.add_task(
            name="Log Test",
            cron_expression="* * * * * *",
            command="echo test"
        )

        log_id = log_task_start(task_id, "Log Test")
        self.assertIsNotNone(log_id)

        log_task_finish(log_id, "SUCCESS", "output", None)

        logs = get_task_logs(task_id)
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['status'], "SUCCESS")


class TestGetScheduler(unittest.TestCase):

    def setUp(self):
        # 清理数据库并初始化
        db_path = '/Users/bangcle/.openclaw/workspace/delivery_management.db'
        if os.path.exists(db_path):
            os.unlink(db_path)
        init_db()
        # 重置全局实例
        import skills.luna.scheduler as scheduler_module
        scheduler_module._scheduler_instance = None

    def tearDown(self):
        db_path = '/Users/bangcle/.openclaw/workspace/delivery_management.db'
        if os.path.exists(db_path):
            os.unlink(db_path)

    def test_get_singleton(self):
        """测试单例模式"""
        s1 = get_scheduler()
        s2 = get_scheduler()

        self.assertIs(s1, s2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
