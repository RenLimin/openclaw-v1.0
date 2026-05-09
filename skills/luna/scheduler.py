"""
定时任务调度器模块
支持任务注册/取消、状态管理、并发控制、超时机制
"""

import time
import uuid
import threading
import subprocess
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from .cron_parser import CronParser
from .database import (
    save_task, delete_task, get_all_tasks,
    log_task_start, log_task_finish, get_task_logs
)

TASK_STATUSES = ['PENDING', 'RUNNING', 'SUCCESS', 'FAILED', 'TIMEOUT']


class Task:
    """任务类"""

    def __init__(self, task_id: str, name: str, cron_expression: str,
                 command: str, timeout: int = 300, max_retries: int = 3):
        self.id = task_id
        self.name = name
        self.cron_expression = cron_expression
        self.cron_parser = CronParser(cron_expression)
        self.command = command
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_count = 0
        self.enabled = True
        self.status = 'PENDING'
        self.last_run = None
        self.next_run = self.cron_parser.next_run_time()
        self.current_process = None

    def should_run(self) -> bool:
        """检查是否应该运行"""
        if not self.enabled:
            return False
        return self.cron_parser.should_run()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'cron_expression': self.cron_expression,
            'command': self.command,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_count': self.retry_count,
            'enabled': self.enabled,
            'status': self.status,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None
        }


class Scheduler:
    """调度器类"""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.max_concurrent = 5
        self.active_tasks = 0
        self._load_saved_tasks()

    def _load_saved_tasks(self):
        """从数据库加载已保存的任务"""
        saved_tasks = get_all_tasks()
        for task_data in saved_tasks:
            if task_data['enabled']:
                task = Task(
                    task_id=task_data['id'],
                    name=task_data['name'],
                    cron_expression=task_data['cron_expression'],
                    command=task_data['command'],
                    timeout=task_data['timeout'],
                    max_retries=task_data['max_retries']
                )
                self.tasks[task.id] = task

    def add_task(self, name: str, cron_expression: str, command: str,
                 timeout: int = 300, max_retries: int = 3) -> str:
        """添加任务"""
        task_id = str(uuid.uuid4())[:8]

        # 验证 cron 表达式
        try:
            CronParser(cron_expression)
        except ValueError as e:
            raise ValueError(f"无效的 cron 表达式: {e}")

        task = Task(task_id, name, cron_expression, command, timeout, max_retries)

        with self.lock:
            self.tasks[task_id] = task
            save_task(task.to_dict())

        return task_id

    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                delete_task(task_id)
                return True
            return False

    def list_tasks(self) -> List[Dict[str, Any]]:
        """列出所有任务"""
        with self.lock:
            return [task.to_dict() for task in self.tasks.values()]

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取单个任务信息"""
        with self.lock:
            task = self.tasks.get(task_id)
            return task.to_dict() if task else None

    def _execute_task(self, task: Task):
        """执行任务（在单独线程中运行）"""
        with self.lock:
            self.active_tasks += 1

        task.status = 'RUNNING'
        task.last_run = datetime.now()
        log_id = log_task_start(task.id, task.name)

        result = None
        error_message = None
        final_status = 'SUCCESS'

        try:
            process = subprocess.Popen(
                task.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            task.current_process = process

            try:
                stdout, stderr = process.communicate(timeout=task.timeout)
                if process.returncode != 0:
                    final_status = 'FAILED'
                    error_message = stderr or f"Exit code: {process.returncode}"
                result = stdout
            except subprocess.TimeoutExpired:
                process.kill()
                final_status = 'TIMEOUT'
                error_message = f"任务超时（{task.timeout}秒）"

        except Exception as e:
            final_status = 'FAILED'
            error_message = str(e)

        finally:
            task.status = final_status
            task.next_run = task.cron_parser.next_run_time()
            task.current_process = None
            log_task_finish(log_id, final_status, result, error_message)

            with self.lock:
                self.active_tasks -= 1

    def _run_loop(self):
        """主调度循环"""
        while self.running:
            current_time = datetime.now()

            with self.lock:
                for task in self.tasks.values():
                    if task.should_run() and task.status != 'RUNNING':
                        if self.active_tasks < self.max_concurrent:
                            # 启动任务线程
                            task_thread = threading.Thread(
                                target=self._execute_task,
                                args=(task,),
                                daemon=True
                            )
                            task_thread.start()

            # 每秒检查一次
            time.sleep(1)

    def start(self):
        """启动调度器"""
        if self.running:
            return False

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        return True

    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        return {
            'running': self.running,
            'task_count': len(self.tasks),
            'active_tasks': self.active_tasks,
            'max_concurrent': self.max_concurrent
        }


# 全局调度器实例
_scheduler_instance: Optional[Scheduler] = None


def get_scheduler() -> Scheduler:
    """获取全局调度器实例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = Scheduler()
    return _scheduler_instance


def main():
    """CLI 入口"""
    import sys

    if len(sys.argv) < 2:
        print("""
Luna 定时任务调度器 v1.0

用法: python -m skills.luna.scheduler <命令> [参数]

命令:
  start              - 启动调度器
  stop               - 停止调度器
  status             - 查看调度器状态
  add <名称> <cron> <命令>
                     - 添加任务 (cron 6字段: 秒 分 时 日 月 周)
  remove <任务ID>    - 移除任务
  list               - 列出所有任务
  logs [任务ID]      - 查看任务执行日志
  test <cron>        - 测试 cron 表达式

示例:
  python -m skills.luna.scheduler start
  python -m skills.luna.scheduler add backup "0 0 2 * * *" "tar -czf backup.tar.gz /data"
  python -m skills.luna.scheduler list
        """)
        return

    scheduler = get_scheduler()
    command = sys.argv[1]

    if command == 'start':
        print("启动调度器...")
        scheduler.start()
        print("调度器已启动，按 Ctrl+C 停止")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止...")
            scheduler.stop()
            print("调度器已停止")

    elif command == 'stop':
        scheduler.stop()
        print("调度器已停止")

    elif command == 'status':
        status = scheduler.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif command == 'add':
        if len(sys.argv) < 5:
            print("用法: python -m skills.luna.scheduler add <名称> <cron> <命令>")
            return
        name = sys.argv[2]
        cron = sys.argv[3]
        cmd = sys.argv[4]
        task_id = scheduler.add_task(name, cron, cmd)
        print(f"任务已添加，ID: {task_id}")

    elif command == 'remove':
        if len(sys.argv) < 3:
            print("用法: python -m skills.luna.scheduler remove <任务ID>")
            return
        task_id = sys.argv[2]
        if scheduler.remove_task(task_id):
            print(f"任务 {task_id} 已移除")
        else:
            print(f"未找到任务 {task_id}")

    elif command == 'list':
        tasks = scheduler.list_tasks()
        if not tasks:
            print("没有已注册的任务")
            return
        for task in tasks:
            print(f"\n[{task['id']}] {task['name']}")
            print(f"  Cron: {task['cron_expression']}")
            print(f"  命令: {task['command']}")
            print(f"  状态: {task['status']}")
            print(f"  下次运行: {task['next_run']}")

    elif command == 'logs':
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        logs = get_task_logs(task_id, limit=20)
        for log in logs:
            start_time = datetime.fromtimestamp(log['started_at'])
            print(f"[{log['status']}] {log['task_name']} - {start_time}")
            if log['error_message']:
                print(f"  错误: {log['error_message']}")

    elif command == 'test':
        if len(sys.argv) < 3:
            print("用法: python -m skills.luna.scheduler test <cron>")
            return
        cron = sys.argv[2]
        try:
            from .cron_parser import format_next_runs
            runs = format_next_runs(cron, 5)
            print(f"Cron 表达式 '{cron}' 的接下来 5 次运行:")
            for i, run in enumerate(runs, 1):
                print(f"  {i}. {run}")
        except Exception as e:
            print(f"错误: {e}")

    else:
        print(f"未知命令: {command}")


if __name__ == '__main__':
    main()
