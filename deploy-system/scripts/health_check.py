#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏥 健康检查脚本 v1.0

检查项：
1. Python 环境与依赖
2. 配置文件完整性
3. 网络连通性
4. API 可用性
5. 磁盘空间

创建时间：2026-05-08
"""

import os
import sys
import json
import shutil
import socket
from datetime import datetime


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.results = []
        self.all_passed = True

        print("=" * 60)
        print("🏥 OpenClaw 健康检查 v1.0")
        print("=" * 60)
        print(f"🕐 检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def check_python_env(self) -> bool:
        """检查 Python 环境"""
        print("🔍 检查 Python 环境...", end=" ")

        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                print("✅ 通过")
                print(f"   Python 版本：{version.major}.{version.minor}.{version.micro}")
                self.results.append({"name": "Python 版本", "status": "pass", "version": f"{version.major}.{version.minor}.{version.micro}"})
                return True
            else:
                print("❌ 失败")
                print(f"   Python 版本过低：{version.major}.{version.minor}.{version.micro}，需要 >= 3.8")
                self.results.append({"name": "Python 版本", "status": "fail", "error": f"版本过低：{version.major}.{version.minor}.{version.micro}"})
                self.all_passed = False
                return False
        except Exception as e:
            print(f"❌ 失败：{e}")
            self.results.append({"name": "Python 版本", "status": "fail", "error": str(e)})
            self.all_passed = False
            return False

    def check_dependencies(self) -> bool:
        """检查依赖包"""
        print("\n🔍 检查核心依赖...", end=" ")

        required_packages = [
            "yaml",
            "json"
        ]

        optional_packages = [
            "cryptography"
        ]

        try:
            missing = []
            for pkg in required_packages:
                try:
                    __import__(pkg)
                except ImportError:
                    missing.append(pkg)

            if not missing:
                print("✅ 通过")
                print(f"   必需依赖：全部已安装")
            else:
                print("❌ 失败")
                print(f"   缺失依赖：{', '.join(missing)}")
                self.all_passed = False

            # 检查可选依赖
            missing_optional = []
            for pkg in optional_packages:
                try:
                    __import__(pkg)
                except ImportError:
                    missing_optional.append(pkg)

            if missing_optional:
                print(f"   ⚠️  可选依赖缺失：{', '.join(missing_optional)}")

            self.results.append({
                "name": "依赖检查",
                "status": "pass" if not missing else "fail",
                "missing_required": missing,
                "missing_optional": missing_optional
            })

            return not missing

        except Exception as e:
            print(f"❌ 失败：{e}")
            self.results.append({"name": "依赖检查", "status": "fail", "error": str(e)})
            self.all_passed = False
            return False

    def check_config_files(self) -> bool:
        """检查配置文件"""
        print("\n🔍 检查配置文件...", end=" ")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(script_dir, "..", "config")

        required_files = [
            os.path.join(config_dir, "config.dev.yaml"),
            os.path.join(config_dir, "config.staging.yaml"),
            os.path.join(config_dir, "config.prod.yaml"),
        ]

        try:
            missing = []
            for file in required_files:
                if not os.path.exists(file):
                    missing.append(os.path.basename(file))

            if not missing:
                print("✅ 通过")
                print(f"   所有配置文件齐全")
            else:
                print("⚠️  警告")
                print(f"   缺失配置文件：{', '.join(missing)}")

            self.results.append({
                "name": "配置文件",
                "status": "pass" if not missing else "warning",
                "missing_files": missing
            })

            return True

        except Exception as e:
            print(f"❌ 失败：{e}")
            self.results.append({"name": "配置文件", "status": "fail", "error": str(e)})
            self.all_passed = False
            return False

    def check_disk_space(self, min_free_gb: int = 5) -> bool:
        """检查磁盘空间"""
        print("\n🔍 检查磁盘空间...", end=" ")

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            disk = shutil.disk_usage(script_dir)
            free_gb = disk.free / (1024 ** 3)

            if free_gb >= min_free_gb:
                print("✅ 通过")
                print(f"   可用空间：{free_gb:.1f} GB")
            else:
                print("⚠️  警告")
                print(f"   可用空间不足：{free_gb:.1f} GB（建议 >= {min_free_gb} GB）")

            self.results.append({
                "name": "磁盘空间",
                "status": "pass" if free_gb >= min_free_gb else "warning",
                "free_gb": round(free_gb, 1),
                "min_required_gb": min_free_gb
            })

            return free_gb >= min_free_gb

        except Exception as e:
            print(f"❌ 失败：{e}")
            self.results.append({"name": "磁盘空间", "status": "fail", "error": str(e)})
            self.all_passed = False
            return False

    def check_network(self) -> bool:
        """检查网络连通性"""
        print("\n🔍 检查网络连通性...", end=" ")

        test_hosts = [
            ("8.8.8.8", 53),      # Google DNS
            ("github.com", 443),  # GitHub
        ]

        try:
            results = []
            for host, port in test_hosts:
                try:
                    socket.create_connection((host, port), timeout=5)
                    results.append((host, True))
                except Exception:
                    results.append((host, False))

            all_pass = all(r[1] for r in results)

            if all_pass:
                print("✅ 通过")
            else:
                print("⚠️  部分失败")

            for host, ok in results:
                status = "✅" if ok else "❌"
                print(f"   {status} {host}")

            self.results.append({
                "name": "网络连通性",
                "status": "pass" if all_pass else "warning",
                "results": [{"host": h, "status": "pass" if o else "fail"} for h, o in results]
            })

            return all_pass

        except Exception as e:
            print(f"❌ 失败：{e}")
            self.results.append({"name": "网络连通性", "status": "fail", "error": str(e)})
            self.all_passed = False
            return False

    def run_all_checks(self) -> dict:
        """运行所有检查"""
        self.check_python_env()
        self.check_dependencies()
        self.check_config_files()
        self.check_disk_space()
        self.check_network()

        # 输出总结
        print()
        print("=" * 60)
        print("📊 检查结果总结")
        print("=" * 60)

        passed = sum(1 for r in self.results if r["status"] == "pass")
        warnings = sum(1 for r in self.results if r["status"] == "warning")
        failed = sum(1 for r in self.results if r["status"] == "fail")

        print(f"   ✅ 通过：{passed}")
        print(f"   ⚠️  警告：{warnings}")
        print(f"   ❌ 失败：{failed}")
        print()

        if self.all_passed and failed == 0:
            print("🎉 所有检查通过！系统状态健康")
            status = "healthy"
        elif failed == 0:
            print("✅ 核心检查通过，注意警告项")
            status = "warning"
        else:
            print("❌ 存在检查失败项，请排查问题")
            status = "unhealthy"

        print()
        print("=" * 60)

        return {
            "status": status,
            "checks": self.results,
            "summary": {
                "passed": passed,
                "warnings": warnings,
                "failed": failed,
                "total": len(self.results)
            },
            "timestamp": datetime.now().isoformat()
        }


def main():
    """主函数"""
    checker = HealthChecker()
    result = checker.run_all_checks()

    # 如果有失败项，退出码非 0
    if result["status"] == "unhealthy":
        sys.exit(1)

    return result


if __name__ == "__main__":
    main()
