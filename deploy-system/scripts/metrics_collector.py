#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 指标收集器 v1.0

功能：
1. 收集系统资源指标（CPU、内存、磁盘）
2. 收集 LLM API 调用指标
3. 收集 Agent 团队运行指标
4. 输出 Prometheus 兼容格式

创建时间：2026-05-08
"""

import os
import sys
import time
import json
import psutil
from datetime import datetime
from typing import Dict, List, Any


class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self.metrics = {}
        print("📊 OpenClaw 指标收集器 v1.0")

    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统资源指标"""
        print("\n🔍 收集系统资源指标...")

        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()

        metrics = {
            "cpu": {
                "usage_percent": cpu_percent,
                "cores": psutil.cpu_count(),
                "cores_physical": psutil.cpu_count(logical=False)
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent,
                "used_gb": round(memory.used / (1024**3), 2)
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_percent": round(disk.percent, 1)
            },
            "network": {
                "bytes_sent_mb": round(network.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(network.bytes_recv / (1024**2), 2),
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else []
        }

        print(f"   CPU: {cpu_percent}% | 内存: {memory.percent}% | 磁盘: {disk.percent}%")
        self.metrics["system"] = metrics
        return metrics

    def collect_process_metrics(self) -> Dict[str, Any]:
        """收集进程指标"""
        print("\n🔍 收集进程指标...")

        current_process = psutil.Process()
        python_processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_percent', 'cpu_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "memory_percent": round(proc.info['memory_percent'], 2),
                        "cpu_percent": proc.info['cpu_percent'],
                        "cmdline": ' '.join(proc.info['cmdline'][:3]) if proc.info['cmdline'] else ''
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        metrics = {
            "total_processes": len(psutil.pids()),
            "python_processes": python_processes,
            "current_process": {
                "pid": current_process.pid,
                "memory_percent": round(current_process.memory_percent(), 2),
                "cpu_percent": current_process.cpu_percent()
            }
        }

        print(f"   总进程数: {metrics['total_processes']} | Python 进程数: {len(python_processes)}")
        self.metrics["processes"] = metrics
        return metrics

    def collect_llm_metrics(self) -> Dict[str, Any]:
        """收集 LLM API 调用指标（占位，待完善）"""
        print("\n🔍 收集 LLM API 指标...")

        metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_latency_seconds": 0,
            "total_tokens_used": 0,
            "estimated_cost_usd": 0
        }

        print(f"   请求总数: {metrics['total_requests']} | 失败: {metrics['failed_requests']}")
        self.metrics["llm"] = metrics
        return metrics

    def collect_agent_metrics(self) -> Dict[str, Any]:
        """收集 Agent 团队指标（占位，待完善）"""
        print("\n🔍 收集 Agent 团队指标...")

        metrics = {
            "active_agents": 0,
            "total_tasks": 0,
            "pending_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_task_duration_seconds": 0
        }

        print(f"   活跃 Agent: {metrics['active_agents']} | 待处理任务: {metrics['pending_tasks']}")
        self.metrics["agents"] = metrics
        return metrics

    def collect_all(self) -> Dict[str, Any]:
        """收集所有指标"""
        print("\n" + "=" * 60)
        print("📊 开始收集所有指标")
        print("=" * 60)

        self.collect_system_metrics()
        self.collect_process_metrics()
        self.collect_llm_metrics()
        self.collect_agent_metrics()

        self.metrics["timestamp"] = datetime.now().isoformat()

        print("\n" + "=" * 60)
        print("✅ 指标收集完成")
        print("=" * 60)

        return self.metrics

    def export_prometheus_format(self) -> str:
        """导出为 Prometheus 格式"""
        lines = []
        m = self.metrics

        # System metrics
        if "system" in m:
            s = m["system"]
            lines.append(f'# HELP openclaw_cpu_usage_percent CPU usage percentage')
            lines.append(f'# TYPE openclaw_cpu_usage_percent gauge')
            lines.append(f'openclaw_cpu_usage_percent {s["cpu"]["usage_percent"]}')

            lines.append(f'# HELP openclaw_memory_usage_percent Memory usage percentage')
            lines.append(f'# TYPE openclaw_memory_usage_percent gauge')
            lines.append(f'openclaw_memory_usage_percent {s["memory"]["used_percent"]}')

            lines.append(f'# HELP openclaw_disk_usage_percent Disk usage percentage')
            lines.append(f'# TYPE openclaw_disk_usage_percent gauge')
            lines.append(f'openclaw_disk_usage_percent {s["disk"]["used_percent"]}')

        # LLM metrics
        if "llm" in m:
            l = m["llm"]
            lines.append(f'# HELP openclaw_llm_total_requests Total LLM API requests')
            lines.append(f'# TYPE openclaw_llm_total_requests counter')
            lines.append(f'openclaw_llm_total_requests {l["total_requests"]}')

            lines.append(f'# HELP openclaw_llm_failed_requests Failed LLM API requests')
            lines.append(f'# TYPE openclaw_llm_failed_requests counter')
            lines.append(f'openclaw_llm_failed_requests {l["failed_requests"]}')

        # Agent metrics
        if "agents" in m:
            a = m["agents"]
            lines.append(f'# HELP openclaw_active_agents Number of active agents')
            lines.append(f'# TYPE openclaw_active_agents gauge')
            lines.append(f'openclaw_active_agents {a["active_agents"]}')

            lines.append(f'# HELP openclaw_pending_tasks Number of pending tasks')
            lines.append(f'# TYPE openclaw_pending_tasks gauge')
            lines.append(f'openclaw_pending_tasks {a["pending_tasks"]}')

        return "\n".join(lines)

    def save_to_file(self, filepath: str, format: str = "json"):
        """保存指标到文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        if format == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        elif format == "prometheus":
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.export_prometheus_format())

        print(f"\n💾 指标已保存到: {filepath}")

    def print_summary(self):
        """打印指标摘要"""
        print("\n" + "=" * 60)
        print("📊 指标摘要")
        print("=" * 60)

        if "system" in self.metrics:
            s = self.metrics["system"]
            print(f"\n💻 系统资源:")
            print(f"   CPU: {s['cpu']['usage_percent']}% ({s['cpu']['cores']} 核)")
            print(f"   内存: {s['memory']['used_percent']}% ({s['memory']['used_gb']}/{s['memory']['total_gb']} GB)")
            print(f"   磁盘: {s['disk']['used_percent']}% ({s['disk']['used_gb']}/{s['disk']['total_gb']} GB)")

        if "llm" in self.metrics:
            l = self.metrics["llm"]
            print(f"\n🤖 LLM API:")
            print(f"   请求总数: {l['total_requests']} (失败 {l['failed_requests']})")
            print(f"   Token 消耗: {l['total_tokens_used']} (预估 ${l['estimated_cost_usd']:.4f})")

        if "agents" in self.metrics:
            a = self.metrics["agents"]
            print(f"\n👥 Agent 团队:")
            print(f"   活跃 Agent: {a['active_agents']}")
            print(f"   待处理任务: {a['pending_tasks']}")
            print(f"   任务成功率: {((a['completed_tasks']/a['total_tasks']*100 if a['total_tasks'] else 0)}%")

        print("\n" + "=" * 60)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw 指标收集器")
    parser.add_argument(
        "--mode",
        choices=["once", "daemon"],
        default="once",
        help="运行模式：once 一次收集，daemon 守护进程持续收集"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="守护模式下的收集间隔，单位秒，默认 60 秒"
    )
    parser.add_argument(
        "--output",
        help="输出文件路径"
    )
    parser.add_argument(
        "--format",
        choices=["json", "prometheus"],
        default="json",
        help="输出格式"
    )

    args = parser.parse_args()

    collector = MetricsCollector()

    if args.mode == "once":
        collector.collect_all()
        collector.print_summary()

        if args.output:
            collector.save_to_file(args.output, args.format)
        else:
            # 默认输出到 stdout
            if args.format == "json":
                print(json.dumps(collector.metrics, indent=2, ensure_ascii=False))
            else:
                print(collector.export_prometheus_format())

    elif args.mode == "daemon":
        print(f"\n🔄 守护模式启动，每 {args.interval} 秒收集一次指标...")
        print("   按 Ctrl+C 停止\n")

        try:
            while True:
                collector.collect_all()
                collector.print_summary()
                if args.output:
                    collector.save_to_file(args.output, args.format)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n\n👋 已停止指标收集")


if __name__ == "__main__":
    main()
