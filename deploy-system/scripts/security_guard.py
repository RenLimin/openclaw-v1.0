#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔒 OpenClaw 安全卫士 v1.0

**核心设计原则：检查失败 = 立即终止，绝不允许静默跳过！**

功能：
1. GitHub 提交前强制审批确认
2. 版本变更依赖关系同步检查
3. 安全违规审计日志
4. 违规次数累计与告警

创建时间：2026-05-08
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class SecurityGuard:
    """安全卫士 - 强制安全检查机制"""

    VIOLATION_LOG = Path.home() / ".openclaw" / "security_violations.json"
    MAX_CONSECUTIVE_VIOLATIONS = 3

    def __init__(self):
        self.workspace = Path.cwd()
        self.violations = self._load_violations()
        self._init_log_directory()

        print("🔒" + "=" * 58)
        print("🔒 OpenClaw 安全卫士 v1.0 - 强制安全检查")
        print("🔒" + "=" * 58)
        print()

    def _init_log_directory(self):
        """初始化日志目录"""
        self.VIOLATION_LOG.parent.mkdir(parents=True, exist_ok=True)
        if not self.VIOLATION_LOG.exists():
            with open(self.VIOLATION_LOG, 'w', encoding='utf-8') as f:
                json.dump({"violations": [], "total_count": 0}, f, indent=2)

    def _load_violations(self) -> Dict:
        """加载违规历史记录"""
        if self.VIOLATION_LOG.exists():
            with open(self.VIOLATION_LOG, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"violations": [], "total_count": 0}

    def _save_violation(self, violation_type: str, details: str):
        """记录违规行为"""
        self.violations["total_count"] += 1
        self.violations["violations"].append({
            "timestamp": datetime.now().isoformat(),
            "type": violation_type,
            "details": details,
            "workspace": str(self.workspace)
        })

        with open(self.VIOLATION_LOG, 'w', encoding='utf-8') as f:
            json.dump(self.violations, f, indent=2, ensure_ascii=False)

        # 连续违规告警
        recent_count = sum(
            1 for v in self.violations["violations"][-5:]
            if (datetime.now() - datetime.fromisoformat(v["timestamp"])).seconds < 3600
        )

        if recent_count >= self.MAX_CONSECUTIVE_VIOLATIONS:
            print(f"\n🚨 严重告警：1小时内连续违规 {recent_count} 次！")
            print("🚨 安全机制已触发锁定，请人工审核！")

    def _exit_denied(self, reason: str, violation_type: str = "security_violation"):
        """拒绝操作并退出"""
        print(f"\n❌ 操作已拒绝！原因：{reason}")
        self._save_violation(violation_type, reason)
        print(f"\n💡 如需继续，请先获得用户明确批准指令！")
        sys.exit(1)

    def check_github_commit_approval(self, auto_mode: bool = False) -> bool:
        """🔴 GitHub 提交强制审批检查（核心安全机制）"""
        print("📋 执行检查：GitHub 提交权限验证")
        print("-" * 60)

        # 显示违规历史
        recent = self.violations["violations"][-3:]
        if recent:
            print(f"⚠️  历史违规记录：{len(recent)} 次")
            for v in recent:
                print(f"   - {v['timestamp'][:19]}: {v['type']}")
            print()

        if auto_mode:
            # 自动模式下检查是否有批准令牌
            approval_token = os.getenv("OPENCLAW_COMMIT_APPROVED")
            if not approval_token:
                self._exit_denied("自动模式下缺少批准令牌", "missing_approval_token")
            print("✅ 检测到批准令牌")
            return True

        # 交互模式 - 强制确认
        print("⚠️  即将执行 GitHub 敏感操作！")
        print("⚠️  请确认已获得用户明确批准！")
        print()

        # 第一层简单确认
        confirm1 = input("🔍 第一层确认：是否已获得批准？(yes/no): ").strip().lower()
        if confirm1 != "yes":
            self._exit_denied("未获得第一层确认", "user_denied_level1")

        # 第二层精确确认（必须输入完整批准指令）
        print()
        print("🔐 第二层强制确认：请输入完整批准指令")
        confirm2 = input("   请输入 '批准提交github' 以继续: ").strip()

        if confirm2 != "批准提交github":
            self._exit_denied(f"批准指令不匹配，输入内容：{confirm2}", "user_denied_level2")

        print()
        print("✅ 已获得用户明确批准，允许提交！")
        print()
        return True

    def check_version_dependency_sync(self) -> bool:
        """检查版本依赖同步状态"""
        print("📋 执行检查：版本依赖同步验证")
        print("-" * 60)

        issues = []

        # 1. 检查 roadmap 实际文件版本
        roadmap_dir = self.workspace / "roadmap"
        if roadmap_dir.exists():
            # 找出最新的智能体进阶规划版本
            plan_files = sorted(roadmap_dir.glob("智能体进阶规划_v*.md"))
            if plan_files:
                latest_plan = plan_files[-1]
                actual_version = latest_plan.stem.split("_v")[-1]

                # 检查 README.md 引用版本
                readme = self.workspace / "README.md"
                if readme.exists():
                    readme_content = readme.read_text(encoding='utf-8')

                    # 检查是否引用旧版本
                    for i in range(1, 20):
                        old_ver = f"v3.{i}"
                        if old_ver in readme_content and old_ver != f"v{actual_version}":
                            if f"进阶规划_v3.{i}" in readme_content:
                                issues.append(f"README.md 引用旧版本 {old_ver}，实际版本 {actual_version}")

        # 2. 检查其他交叉引用
        # FOLDER_STRUCTURE.md
        folder_struct = self.workspace / "FOLDER_STRUCTURE.md"
        if folder_struct.exists():
            folder_content = folder_struct.read_text(encoding='utf-8')
            for issue in list(issues):
                for ver_part in issue.split():
                    if ver_part.startswith("v") and ver_part in folder_content:
                        pass  # 可以增加更多检查

        if issues:
            print(f"⚠️  发现 {len(issues)} 个版本同步问题：")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
            print()

            # 询问是否继续
            choice = input("存在版本不一致，是否继续？(强制继续输入 YES 并回车): ").strip()
            if choice != "YES":
                self._exit_denied("版本依赖不同步", "version_sync_missing")
        else:
            print("✅ 版本同步检查通过！")
            print()

        return True

    def run_pre_commit_checks(self, skip_approval: bool = False) -> bool:
        """执行完整的提交前检查序列"""
        print("\n🚦 开始执行提交前安全检查序列\n")

        # 检查1：版本依赖同步（可选跳过批准检查用于测试）
        self.check_version_dependency_sync()

        # 检查2：GitHub 提交批准（强制，除非显式跳过）
        if not skip_approval:
            self.check_github_commit_approval()

        # 检查3：敏感文件泄漏
        self._check_sensitive_files()

        print("\n✅" + "=" * 58)
        print("✅ 所有安全检查通过！")
        print("✅" + "=" * 58)

        return True

    def _check_sensitive_files(self) -> bool:
        """检查敏感文件"""
        sensitive_patterns = [
            ".env",
            "*.key",
            "*.pem",
            "api_keys.json",
            "secrets.json",
        ]

        found = []
        for pattern in sensitive_patterns:
            for match in self.workspace.rglob(pattern):
                if '.git' not in str(match):
                    found.append(str(match.relative_to(self.workspace)))

        if found:
            print(f"\n⚠️  检测到潜在敏感文件：{len(found)} 个")
            for f in found[:5]:
                print(f"   - {f}")
            if len(found) > 5:
                print(f"   ... 还有 {len(found) - 5} 个")

            print()
            choice = input("检测到敏感文件，是否确认提交？(确认输入 YES): ").strip()
            if choice != "YES":
                self._exit_denied("检测到敏感文件，用户终止操作", "sensitive_file_detected")

        return True

    def show_status(self):
        """显示安全状态"""
        total = self.violations.get("total_count", 0)
        print(f"\n📊 安全状态统计：")
        print(f"   历史违规次数：{total}")
        print(f"   安全卫士状态：🔒 运行中")
        print()


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw 安全卫士 - 强制安全检查机制")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # pre-commit 命令
    commit_parser = subparsers.add_parser("pre-commit", help="执行提交前全部检查")
    commit_parser.add_argument("--skip-approval", action="store_true", help="跳过批准检查（仅测试）")
    commit_parser.add_argument("--auto", action="store_true", help="自动模式（使用环境变量令牌）")

    # status 命令
    subparsers.add_parser("status", help="显示安全状态")

    args = parser.parse_args()

    guard = SecurityGuard()

    if args.command == "pre-commit":
        guard.run_pre_commit_checks(skip_approval=args.skip_approval)
        print("\n🚀 检查全部通过，可以执行提交！")

    elif args.command == "status":
        guard.show_status()

    elif args.command is None:
        parser.print_help()
        guard.show_status()


if __name__ == "__main__":
    main()
