#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🩺 系统自诊断与优化建议工具 v1.0

功能：
1. 系统环境完整性检查
2. 性能瓶颈诊断
3. 配置合理性分析
4. 安全审计
5. 生成优化建议报告

创建时间：2026-05-08
"""

import os
import sys
import json
import shutil
import socket
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple


class SystemDiagnostic:
    """系统诊断器"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.getcwd()

        self.base_dir = Path(base_dir).resolve()
        self.results = {}
        self.issues = []
        self.recommendations = []

        print("🩺 OpenClaw 系统自诊断工具 v1.0")
        print(f"   诊断目录: {self.base_dir}")

    def check_python_environment(self) -> Dict:
        """检查 Python 环境"""
        print("\n🔍 检查 Python 环境...", end=" ")

        result = {
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "python_path": sys.executable,
            "meets_requirements": sys.version_info >= (3, 8),
            "checks": {}
        }

        # 检查版本要求
        if result["meets_requirements"]:
            result["checks"]["version"] = {"status": "pass", "message": f"Python {result['version']} 满足要求"}
        else:
            result["checks"]["version"] = {"status": "fail", "message": f"Python 版本过低: {result['version']}，需要 >= 3.8"}
            self.issues.append(("high", "Python 版本不满足最低要求"))

        # 检查必要依赖
        required_packages = {
            "yaml": "pyyaml",
            "cryptography": "cryptography",
            "requests": "requests"
        }

        for package, pip_name in required_packages.items():
            try:
                __import__(package)
                result["checks"][package] = {"status": "pass", "message": f"{pip_name} 已安装"}
            except ImportError:
                result["checks"][package] = {"status": "warning", "message": f"{pip_name} 未安装"}
                self.issues.append(("medium", f"依赖包未安装: {pip_name}"))

        # 统计结果
        total_checks = len(result["checks"])
        passed = sum(1 for c in result["checks"].values() if c["status"] == "pass")

        if passed == total_checks:
            print("✅ 通过")
        else:
            print("⚠️ 存在问题")

        return result

    def check_directory_structure(self) -> Dict:
        """检查目录结构完整性"""
        print("🔍 检查目录结构...", end=" ")

        required_dirs = [
            "core-config",
            "deploy-system",
            "deploy-team",
            "skills",
            "knowledge-base"
        ]

        optional_dirs = [
            "tenants",
            "memory",
            "agents",
            "scripts"
        ]

        result = {
            "required_dirs": {},
            "optional_dirs": {},
            "structure_score": 0
        }

        for d in required_dirs:
            exists = (self.base_dir / d).exists()
            result["required_dirs"][d] = {
                "exists": exists,
                "status": "pass" if exists else "fail"
            }
            if not exists:
                self.issues.append(("high", f"必需目录缺失: {d}"))

        for d in optional_dirs:
            exists = (self.base_dir / d).exists()
            result["optional_dirs"][d] = {
                "exists": exists,
                "status": "pass" if exists else "warning"
            }
            if not exists:
                self.issues.append(("low", f"可选目录缺失: {d}"))

        # 计算结构完整性分数
        total_required = len(required_dirs)
        passed_required = sum(1 for d in result["required_dirs"].values() if d["exists"])
        structure_score = int((passed_required / total_required) * 100)
        result["structure_score"] = structure_score

        if structure_score == 100:
            print("✅ 完整")
        elif structure_score >= 80:
            print("⚠️ 基本完整")
        else:
            print("❌ 严重缺失")

        return result

    def check_config_files(self) -> Dict:
        """检查配置文件"""
        print("🔍 检查配置文件...", end=" ")

        result = {
            "core_configs": {},
            "deploy_configs": {},
            "permissions": {}
        }

        # 核心配置文件
        config_dir = self.base_dir / "core-config"
        if config_dir.exists():
            for f in ["AGENT.md", "IDENTITY.md", "MEMORY.md", "SOUL.md"]:
                config_path = config_dir / f
                exists = config_path.exists()
                result["core_configs"][f] = {
                    "exists": exists,
                    "size_bytes": config_path.stat().st_size if exists else 0
                }
                if not exists:
                    self.issues.append(("medium", f"核心配置缺失: {f}"))

        # 部署配置文件
        deploy_config_dir = self.base_dir / "deploy-system" / "config"
        if deploy_config_dir.exists():
            for f in ["config.dev.yaml", "config.staging.yaml", "config.prod.yaml"]:
                config_path = deploy_config_dir / f
                result["deploy_configs"][f] = config_path.exists()

        print("✅ 完成")
        return result

    def check_system_resources(self) -> Dict:
        """检查系统资源状况"""
        print("🔍 检查系统资源...", end=" ")

        result = {
            "disk": {},
            "memory": {},
            "network": {}
        }

        # 磁盘空间
        disk_usage = shutil.disk_usage(self.base_dir)
        total_gb = disk_usage.total / (1024 ** 3)
        used_gb = disk_usage.used / (1024 ** 3)
        free_gb = disk_usage.free / (1024 ** 3)
        usage_percent = (used_gb / total_gb) * 100

        result["disk"] = {
            "total_gb": round(total_gb, 1),
            "used_gb": round(used_gb, 1),
            "free_gb": round(free_gb, 1),
            "usage_percent": round(usage_percent, 1)
        }

        if usage_percent > 90:
            self.issues.append(("high", "磁盘空间严重不足"))
            self.recommendations.append("考虑清理磁盘或扩容存储")
        elif usage_percent > 80:
            self.issues.append(("medium", "磁盘空间使用率较高"))
            self.recommendations.append("建议关注磁盘空间使用情况")

        # 内存 - 使用 psutil 如果可用
        try:
            import psutil
            mem = psutil.virtual_memory()
            result["memory"] = {
                "total_gb": round(mem.total / (1024 ** 3), 1),
                "available_gb": round(mem.available / (1024 ** 3), 1),
                "percent_used": round(mem.percent, 1)
            }
            if mem.percent > 90:
                self.issues.append(("high", "系统内存严重不足"))
            elif mem.percent > 80:
                self.issues.append(("medium", "系统内存使用率较高"))
        except ImportError:
            result["memory"] = {"status": "unavailable"}

        # 网络连通性
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            result["network"]["internet"] = True
        except:
            result["network"]["internet"] = False
            self.issues.append(("medium", "网络连接可能存在问题"))

        print("✅ 完成")
        return result

    def check_security(self) -> Dict:
        """安全审计检查"""
        print("🔍 执行安全审计...", end=" ")

        result = {
            "gitignore": False,
            "env_files_permissions": {},
            "sensitive_files": []
        }

        # 检查 .gitignore
        gitignore_path = self.base_dir / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                content = f.read()
            result["gitignore"] = True
            # 检查是否包含敏感文件排除规则
            sensitive_patterns = [".env", "*.key", "secrets", "*.pem"]
            for pattern in sensitive_patterns:
                if pattern not in content:
                    result["sensitive_files"].append(f".gitignore 缺少 {pattern} 排除规则")
                    self.issues.append(("medium", f".gitignore 缺少敏感文件保护规则: {pattern}"))

        # 检查潜在的明文密钥
        potential_secret_files = []
        for ext in ["*.env", "*.key", "*.pem"]:
            potential_secret_files.extend(list(self.base_dir.rglob(ext)))

        result["potential_secret_files_count"] = len(potential_secret_files)
        if potential_secret_files:
            self.issues.append(("medium", f"发现 {len(potential_secret_files)} 个潜在敏感文件"))

        print("✅ 完成")
        return result

    def check_performance_settings(self) -> Dict:
        """检查性能配置"""
        print("🔍 检查性能配置...", end=" ")

        result = {
            "llm_settings": {},
            "cache_settings": {},
            "concurrency_settings": {}
        }

        # 检查是否有性能优化配置
        config_file = self.base_dir / "deploy-system" / "config" / "config.prod.yaml"
        if config_file.exists():
            result["has_prod_config"] = True
        else:
            result["has_prod_config"] = False
            self.issues.append(("low", "缺少生产环境专用配置文件"))

        print("✅ 完成")
        return result

    def run_full_diagnosis(self) -> Dict:
        """执行完整诊断"""
        print("\n" + "=" * 60)
        print("🚀 开始系统全面诊断")
        print("=" * 60)

        self.results["python"] = self.check_python_environment()
        self.results["directory"] = self.check_directory_structure()
        self.results["config"] = self.check_config_files()
        self.results["resources"] = self.check_system_resources()
        self.results["security"] = self.check_security()
        self.results["performance"] = self.check_performance_settings()

        return self.results

    def generate_report(self) -> str:
        """生成诊断报告"""
        high_count = sum(1 for s, _ in self.issues if s == "high")
        medium_count = sum(1 for s, _ in self.issues if s == "medium")
        low_count = sum(1 for s, _ in self.issues if s == "low")

        overall_health = 100 - (high_count * 20 + medium_count * 10 + low_count * 5)
        overall_health = max(0, overall_health)

        report_lines = [
            "\n" + "=" * 80,
            "📊 系统诊断报告",
            "=" * 80,
            "",
            f"🕐 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"📍 诊断目录: {self.base_dir}",
            "",
            "📈 健康状况评分",
            "-" * 40,
            f"   综合健康分数: {'🟢' if overall_health >= 80 else '🟡' if overall_health >= 60 else '🔴'} {overall_health}/100",
            "",
            "⚠️ 发现的问题",
            "-" * 40,
            f"   🔴 严重问题: {high_count} 个",
            f"   🟡 中等问题: {medium_count} 个",
            f"   🟢 轻微问题: {low_count} 个",
            "",
            "详细问题列表:",
        ]

        for severity, issue in self.issues:
            icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
            report_lines.append(f"   {icon} [{severity.upper()}] {issue}")

        if self.recommendations:
            report_lines.extend([
                "",
                "💡 优化建议",
                "-" * 40,
            ])
            for i, rec in enumerate(self.recommendations, 1):
                report_lines.append(f"   {i}. {rec}")

        report_lines.extend([
            "",
            "=" * 80,
            "💡 建议: 根据问题严重程度，优先处理高危问题",
            "=" * 80,
        ])

        return "\n".join(report_lines)

    def save_report(self, output_file: str = None):
        """保存诊断报告到文件"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.base_dir / "diagnostics" / f"report_{timestamp}.json"
            output_file.parent.mkdir(exist_ok=True)

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "base_dir": str(self.base_dir),
            "results": self.results,
            "issues": self.issues,
            "recommendations": self.recommendations
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 详细报告已保存到: {output_file}")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw 系统诊断工具")
    parser.add_argument("--dir", help="指定诊断目录")
    parser.add_argument("--save", action="store_true", help="保存报告到文件")
    parser.add_argument("--quick", action="store_true", help="快速检查模式")

    args = parser.parse_args()

    diagnostic = SystemDiagnostic(base_dir=args.dir)

    if args.quick:
        # 快速检查
        diagnostic.check_python_environment()
        diagnostic.check_directory_structure()
        diagnostic.check_system_resources()
    else:
        # 完整诊断
        diagnostic.run_full_diagnosis()

    report = diagnostic.generate_report()
    print(report)

    if args.save:
        diagnostic.save_report()


if __name__ == "__main__":
    main()
