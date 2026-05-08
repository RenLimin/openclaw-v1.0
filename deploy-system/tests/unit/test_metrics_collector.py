# ==============================================
# 指标收集器单元测试
# ==============================================

import json
import pytest
from pathlib import Path


class TestMetricsCollector:
    """指标收集器测试套件"""

    def test_initialization(self):
        """测试初始化"""
        from deploy_system.scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        assert collector is not None

    def test_collect_system_metrics_returns_data(self):
        """测试收集系统指标"""
        from deploy_system.scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        metrics = collector.collect_system_metrics()

        assert "cpu" in metrics
        assert "memory" in metrics
        assert "disk" in metrics
        assert "load_average" in metrics

        # 验证 CPU 指标结构
        assert "usage_percent" in metrics["cpu"]
        assert "cores" in metrics["cpu"]

        # 验证内存指标结构
        assert "total_gb" in metrics["memory"]
        assert "used_percent" in metrics["memory"]

    def test_collect_process_metrics(self):
        """测试收集进程指标"""
        from deploy_system.scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        metrics = collector.collect_process_metrics()

        assert "total_processes" in metrics
        assert "python_processes" in metrics
        assert isinstance(metrics["python_processes"], list)

    def test_collect_llm_metrics(self):
        """测试收集 LLM 指标（占位符）"""
        from deploy_system.scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        metrics = collector.collect_llm_metrics()

        assert "total_requests" in metrics
        assert "successful_requests" in metrics
        assert "failed_requests" in metrics
        assert "estimated_cost_usd" in metrics

    def test_collect_agent_metrics(self):
        """测试收集 Agent 团队指标（占位符）"""
        from deploy_system.scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        metrics = collector.collect_agent_metrics()

        assert "active_agents" in metrics
        assert "total_tasks" in metrics
        assert "pending_tasks" in metrics
        assert "completed_tasks" in metrics

    def test_collect_all_metrics(self):
        """测试收集所有指标"""
        from deploy_system.scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        all_metrics = collector.collect_all()

        assert "system" in all_metrics
        assert "processes" in all_metrics
        assert "llm" in all_metrics
        assert "agents" in all_metrics
        assert "timestamp" in all_metrics

    def test_export_prometheus_format(self):
        """测试导出 Prometheus 格式"""
        from deploy_system.scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        collector.collect_all()

        prometheus_output = collector.export_prometheus_format()

        assert "openclaw_cpu_usage_percent" in prometheus_output
        assert "openclaw_memory_usage_percent" in prometheus_output

    def test_save_to_file_json(self, temp_dir):
        """测试保存指标到 JSON 文件"""
        from deploy_system.scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        collector.collect_all()

        output_file = temp_dir / "metrics.json"
        collector.save_to_file(str(output_file), format="json")

        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
            assert "system" in data

    def test_save_to_file_prometheus(self, temp_dir):
        """测试保存指标到 Prometheus 格式文件"""
        from deploy_system.scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        collector.collect_all()

        output_file = temp_dir / "metrics.prom"
        collector.save_to_file(str(output_file), format="prometheus")

        assert output_file.exists()
        content = output_file.read_text()
        assert "openclaw_" in content

    def test_print_summary(self, capsys):
        """测试打印摘要"""
        from deploy_system.scripts.metrics_collector import MetricsCollector
        collector = MetricsCollector()
        collector.collect_all()

        collector.print_summary()
        captured = capsys.readouterr()

        assert "系统资源" in captured.out or "System" in captured.out


# ==============================================
# 版本：v1.0 | 最后更新：2026-05-08
# ==============================================
