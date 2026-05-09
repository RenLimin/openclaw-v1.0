"""
数据库模块 - 任务执行日志和监控指标存储
使用统一数据库 delivery_management.db
"""

import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

DB_PATH = Path(__file__).parent.parent.parent / "delivery_management.db"


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 任务执行日志表（类似 llm_call_logs 结构）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            task_name TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at REAL NOT NULL,
            finished_at REAL,
            duration REAL,
            result TEXT,
            error_message TEXT,
            created_at REAL DEFAULT (strftime('%s', 'now'))
        )
    """)

    # 定时任务表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_tasks (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            cron_expression TEXT NOT NULL,
            command TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            timeout INTEGER DEFAULT 300,
            max_retries INTEGER DEFAULT 3,
            created_at REAL DEFAULT (strftime('%s', 'now')),
            updated_at REAL DEFAULT (strftime('%s', 'now'))
        )
    """)

    # 系统监控指标表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpu_percent REAL,
            memory_percent REAL,
            memory_used_gb REAL,
            disk_percent REAL,
            disk_used_gb REAL,
            network_in_mb REAL,
            network_out_mb REAL,
            recorded_at REAL NOT NULL
        )
    """)

    # 业务指标表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            recorded_at REAL NOT NULL
        )
    """)

    # 告警日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            rule_name TEXT NOT NULL,
            message TEXT NOT NULL,
            value REAL,
            threshold REAL,
            notified INTEGER DEFAULT 0,
            created_at REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# 任务日志相关函数
def log_task_start(task_id: str, task_name: str) -> int:
    """记录任务开始"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO task_execution_logs (task_id, task_name, status, started_at) VALUES (?, ?, ?, ?)",
        (task_id, task_name, "RUNNING", time.time())
    )
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def log_task_finish(log_id: int, status: str, result: str = None, error_message: str = None):
    """记录任务完成"""
    conn = get_db_connection()
    cursor = conn.cursor()
    finished_at = time.time()

    # 获取开始时间计算时长
    cursor.execute("SELECT started_at FROM task_execution_logs WHERE id = ?", (log_id,))
    row = cursor.fetchone()
    duration = finished_at - row["started_at"] if row else None

    cursor.execute("""
        UPDATE task_execution_logs
        SET status = ?, finished_at = ?, duration = ?, result = ?, error_message = ?
        WHERE id = ?
    """, (status, finished_at, duration, result, error_message, log_id))
    conn.commit()
    conn.close()


def get_task_logs(task_id: str = None, limit: int = 100) -> List[Dict]:
    """获取任务日志"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if task_id:
        cursor.execute(
            "SELECT * FROM task_execution_logs WHERE task_id = ? ORDER BY started_at DESC LIMIT ?",
            (task_id, limit)
        )
    else:
        cursor.execute(
            "SELECT * FROM task_execution_logs ORDER BY started_at DESC LIMIT ?",
            (limit,)
        )

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# 定时任务 CRUD
def save_task(task: Dict[str, Any]):
    """保存或更新定时任务"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO scheduled_tasks
        (id, name, cron_expression, command, enabled, timeout, max_retries, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task["id"], task["name"], task["cron_expression"],
        task["command"], task.get("enabled", 1),
        task.get("timeout", 300), task.get("max_retries", 3),
        time.time()
    ))
    conn.commit()
    conn.close()


def delete_task(task_id: str):
    """删除定时任务"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scheduled_tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def get_all_tasks() -> List[Dict]:
    """获取所有定时任务"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scheduled_tasks ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# 系统指标存储
def save_system_metrics(metrics: Dict[str, float]):
    """保存系统监控指标"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO system_metrics
        (cpu_percent, memory_percent, memory_used_gb, disk_percent,
         disk_used_gb, network_in_mb, network_out_mb, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        metrics.get("cpu_percent"),
        metrics.get("memory_percent"),
        metrics.get("memory_used_gb"),
        metrics.get("disk_percent"),
        metrics.get("disk_used_gb"),
        metrics.get("network_in_mb"),
        metrics.get("network_out_mb"),
        time.time()
    ))
    conn.commit()
    conn.close()


# 业务指标存储
def save_business_metric(metric_name: str, metric_value: float):
    """保存业务指标"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO business_metrics (metric_name, metric_value, recorded_at)
        VALUES (?, ?, ?)
    """, (metric_name, metric_value, time.time()))
    conn.commit()
    conn.close()


# 告警日志
def save_alert(level: str, rule_name: str, message: str, value: float = None, threshold: float = None):
    """保存告警日志"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alert_logs (level, rule_name, message, value, threshold, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (level, rule_name, message, value, threshold, time.time()))
    conn.commit()
    conn.close()


def get_recent_alerts(hours: int = 24) -> List[Dict]:
    """获取最近的告警"""
    since = time.time() - (hours * 3600)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM alert_logs WHERE created_at >= ? ORDER BY created_at DESC
    """, (since,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# 初始化数据库
init_db()
