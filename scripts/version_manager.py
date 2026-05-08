#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 OpenClaw 版本管理器 v1.0

**核心设计原则：单一事实来源 + 工具代替人工**

功能:
  show           - 显示当前所有模块版本
  check          - 检查版本依赖一致性 (✅ 解决本次核心问题)
  impact         - 分析版本变更影响范围
  bump           - 升级版本号（自动同步所有引用）
  matrix         - 显示兼容性矩阵

创建时间：2026-05-08
"""

import os
import sys
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


class VersionManager:
    """OpenClaw 版本管理器"""

    def __init__(self, config_path: str = "version.json"):
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"找不到版本配置文件: {config_path}")

        with open(config_file, encoding='utf-8') as f:
            self.config = json.load(f)

        self.config_path = config_file
        self.workspace = config_file.parent if config_file.parent != Path(".") else Path.cwd()

        print("📦 OpenClaw 版本管理器 v1.0")
        print("=" * 60)

    def show_all(self):
        """显示所有模块版本"""
        sys_ver = self.config['system']['version']
        sys_codename = self.config['system']['codename']
        sys_release = self.config['system']['release_date']

        print(f"\n🌐 系统版本: v{sys_ver} ({sys_codename})")
        print(f"📅 发布日期: {sys_release}")
        print()
        print(f"{'模块名称':<20} {'版本号':<12} {'角色':<20}")
        print("-" * 60)

        for name, mod in self.config['modules'].items():
            dep_info = f" (依赖: {len(mod.get('dependencies', []))})" if mod.get('dependencies') else ""
            print(f"  {name:<18} v{mod['version']:<10} {mod['role']:<15}{dep_info}")

        print()

    def check_consistency(self, verbose: bool = True) -> Dict[str, List[str]]:
        """检查所有文档版本引用一致性

        这是解决本次版本同步问题的核心函数！
        """
        issues = {
            'outdated_references': [],    # 引用了过时的版本号
            'missing_files': [],           # 引用的文件不存在
            'version_mismatch': [],        # 配置与实际文件不匹配
            'cross_reference_errors': []   # 交叉引用错误
        }

        if verbose:
            print("\n🔍 开始检查版本引用一致性...")
            print("-" * 60)

        # Step 1: 找出 roadmap 目录中的所有实际版本
        roadmap_dir = self.workspace / "roadmap"
        actual_versions = {}

        if roadmap_dir.exists():
            # 扫描智能体进阶规划的版本
            for f in roadmap_dir.glob("智能体进阶规划_v*.md"):
                ver_match = re.search(r'_v([\d.]+)\.md', f.name)
                if ver_match:
                    ver = ver_match.group(1)
                    actual_versions['roadmap-main'] = {
                        'version': ver,
                        'file': str(f),
                        'pattern': f"智能体进阶规划_v{ver}.md"
                    }

            # 扫描 Jerry 角色文档
            for f in roadmap_dir.glob("Jerry*_进阶计划_v*.md"):
                ver_match = re.search(r'_v([\d.]+)\.md', f.name)
                if ver_match:
                    ver = ver_match.group(1)
                    actual_versions['jerry-role'] = {
                        'version': ver,
                        'file': str(f),
                        'pattern': f"Jerry_智能体团队创建者_进阶计划_v{ver}.md"
                    }

        if verbose:
            print(f"\n📋 检测到实际文件版本:")
            for name, info in actual_versions.items():
                print(f"   {name}: v{info['version']}")

        # Step 2: 搜索所有 Markdown 文档中的版本引用
        if verbose:
            print(f"\n🔍 扫描所有文档中的版本引用...")

        scan_count = 0
        error_count = 0

        for md_file in self.workspace.rglob("*.md"):
            if '.git' in str(md_file) or '.openclaw' in str(md_file):
                continue

            scan_count += 1
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')

                # 检查智能体进阶规划引用
                for match in re.finditer(r'智能体进阶规划_v([\d.]+)\.md', content):
                    ref_ver = match.group(1)
                    latest = actual_versions.get('roadmap-main', {}).get('version')

                    if latest and ref_ver != latest:
                        issue = (
                            f"📄 {md_file.relative_to(self.workspace)}: "
                            f"引用智能体进阶规划 v{ref_ver}，最新是 v{latest}"
                        )
                        issues['outdated_references'].append(issue)
                        error_count += 1

                # 检查 Jerry 角色文档引用
                for match in re.finditer(r'Jerry_智能体团队创建者_进阶计划_v([\d.]+)\.md', content):
                    ref_ver = match.group(1)
                    latest = actual_versions.get('jerry-role', {}).get('version')

                    if latest and ref_ver != latest:
                        issue = (
                            f"📄 {md_file.relative_to(self.workspace)}: "
                            f"引用 Jerry 进阶计划 v{ref_ver}，最新是 v{latest}"
                        )
                        issues['outdated_references'].append(issue)
                        error_count += 1

            except Exception as e:
                issues['missing_files'].append(f"读取失败: {md_file}: {e}")

        if verbose:
            print(f"   已扫描 {scan_count} 个 Markdown 文档")

        # Step 3: 检查配置文件与实际文件一致性
        for mod_name, mod_config in self.config['modules'].items():
            mod_path = Path(mod_config['path'])
            if not mod_path.exists() and not mod_path.is_dir():
                # 目录就不检查存在性，检查文件路径
                if mod_config['path'].endswith('.md'):
                    if not (self.workspace / mod_path).exists():
                        issues['missing_files'].append(
                            f"配置文件不存在: {mod_name} -> {mod_config['path']}"
                        )

        # Step 4: 输出结果
        if verbose:
            print()
            if error_count > 0:
                print(f"⚠️  发现 {error_count} 个版本引用不一致问题:\n")
                for issue in issues['outdated_references']:
                    print(f"   ❌ {issue}")
            else:
                print("✅ 所有版本引用检查通过！")

            print()
            total_issues = sum(len(v) for v in issues.values())
            if total_issues == 0:
                print("🎉 版本一致性检查：全部通过！")
            else:
                print(f"⚠️  总计发现 {total_issues} 个问题需要修复")

        return issues

    def analyze_impact(self, module: str, new_version: str) -> Dict[str, List[str]]:
        """分析某个模块版本变更的影响范围

        返回所有需要同步修改的文件列表
        """
        print(f"\n📊 分析版本变更影响: {module} -> v{new_version}")
        print("-" * 60)

        impacts = {
            'direct_references': [],
            'dependents': [],
            'documentation_refs': []
        }

        mod_config = self.config['modules'].get(module)
        if not mod_config:
            print(f"❌ 未找到模块: {module}")
            return impacts

        old_pattern = mod_config.get('path', '')

        # Step 1: 搜索直接引用
        print(f"\n🔍 扫描文件引用...")

        for md_file in self.workspace.rglob("*.md"):
            if '.git' in str(md_file):
                continue

            content = md_file.read_text(encoding='utf-8', errors='ignore')
            if module in content or old_pattern in content:
                impacts['direct_references'].append(
                    str(md_file.relative_to(self.workspace))
                )

        # Step 2: 查找依赖此模块的其他模块
        print(f"\n🔗 检查依赖链...")
        for name, mod in self.config['modules'].items():
            for dep in mod.get('dependencies', []):
                if module in dep:
                    impacts['dependents'].append(f"{name}: {dep}")

        # Step 3: 报告结果
        print(f"\n📋 影响分析结果:")
        print(f"   - 需要更新的文档: {len(impacts['direct_references'])} 个")
        for f in impacts['direct_references'][:10]:  # 只显示前10个
            print(f"     • {f}")
        if len(impacts['direct_references']) > 10:
            print(f"       ... 还有 {len(impacts['direct_references'])-10} 个")

        print(f"   - 受影响的依赖模块: {len(impacts['dependents'])} 个")
        for dep in impacts['dependents']:
            print(f"     • {dep}")

        print()
        return impacts

    def bump_version(self, module: str, level: str = "patch", auto_fix_refs: bool = True) -> str:
        """升级版本号，并自动同步更新所有引用

        Args:
            module: 模块名称
            level: major / minor / patch
            auto_fix_refs: 是否自动修复文档中的引用

        Returns:
            新版本号
        """
        mod_config = self.config['modules'].get(module)
        if not mod_config:
            raise ValueError(f"未找到模块: {module}")

        old_ver = mod_config['version']
        version_parts = list(map(int, old_ver.split('.')))

        # 确保有 3 段版本号
        while len(version_parts) < 3:
            version_parts.append(0)

        major, minor, patch = version_parts[:3]

        if level == "major":
            major += 1
            minor = 0
            patch = 0
        elif level == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        new_ver = f"{major}.{minor}.{patch}"

        print(f"\n⬆️  版本升级: {module} v{old_ver} -> v{new_ver}")
        print(f"级别: {level}")
        print("-" * 60)

        # 1. 分析影响
        impacts = self.analyze_impact(module, new_ver)

        if not auto_fix_refs:
            print("\n💡 (手动模式) 请手动更新以上文件")
            return new_ver

        # 2. 自动更新所有引用
        updated_count = 0
        failed_count = 0

        old_pattern = mod_config.get('path', '')
        # 生成新文件名模式
        new_pattern = old_pattern.replace(f"v{old_ver}", f"v{new_ver}")

        print(f"\n🔧 自动更新文件引用...")
        print(f"   搜索模式: {old_pattern}")
        print(f"   替换为: {new_pattern}")

        for file_path in impacts['direct_references']:
            try:
                file_full = self.workspace / file_path
                content = file_full.read_text(encoding='utf-8')

                if old_pattern in content:
                    new_content = content.replace(old_pattern, new_pattern)
                    file_full.write_text(new_content, encoding='utf-8')
                    updated_count += 1
                    print(f"   ✅ {file_path}")
            except Exception as e:
                failed_count += 1
                print(f"   ❌ {file_path}: {e}")

        print(f"\n📊 自动更新结果: 成功 {updated_count} 个，失败 {failed_count} 个")

        # 3. 更新配置文件
        self.config['modules'][module]['version'] = new_ver
        self.config['modules'][module]['path'] = new_pattern
        self.config['metadata']['last_updated'] = __import__('datetime').datetime.now().date().isoformat()

        # 如果主系统版本也需要更新
        if module == 'roadmap':
            self.config['system']['version'] = new_ver

        self._save_config()
        print(f"\n✅ 版本配置已更新: {self.config_path}")

        return new_ver

    def show_compatibility_matrix(self):
        """显示兼容性矩阵"""
        print("\n📐 兼容性矩阵")
        print("=" * 60)
        print()
        print(f"{'Roadmap':<12} {'部署系统':<12} {'团队工具':<12} {'兼容性':<10}")
        print("-" * 60)

        matrix = [
            ("v3.13.x", "v1.0.x", "v1.0.x", "✅ 完全兼容"),
            ("v3.12.x", "v1.0.x", "v1.0.x", "✅ 完全兼容"),
            ("v3.11.x", "v1.0.x", "v1.0.x", "✅ 完全兼容"),
            ("v3.10.x", "v1.0.x", "v1.0.x", "✅ 完全兼容"),
            ("v3.8.x", "v0.9.x", "v0.9.x", "⚠️ 部分兼容"),
            ("v2.x", "不支持", "不支持", "❌ 不兼容"),
        ]

        for row in matrix:
            print(f"{row[0]:<12} {row[1]:<12} {row[2]:<12} {row[3]:<10}")

        print()

    def _save_config(self):
        """保存配置文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="OpenClaw 版本管理器 - 企业级版本依赖管理工具"
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # show 命令
    subparsers.add_parser("show", help="显示所有模块版本")

    # check 命令
    check_parser = subparsers.add_parser("check", help="检查版本引用一致性")
    check_parser.add_argument("--quiet", action="store_true", help="静默模式")

    # impact 命令
    impact_parser = subparsers.add_parser("impact", help="分析版本变更影响范围")
    impact_parser.add_argument("module", help="模块名称")
    impact_parser.add_argument("new_version", help="新版本号")

    # bump 命令
    bump_parser = subparsers.add_parser("bump", help="升级版本号（自动同步所有引用）")
    bump_parser.add_argument("module", help="模块名称")
    bump_parser.add_argument(
        "--level", 
        default="patch", 
        choices=["major", "minor", "patch"],
        help="升级级别 (默认: patch)"
    )
    bump_parser.add_argument("--dry-run", action="store_true", help="仅分析，不实际修改")

    # matrix 命令
    subparsers.add_parser("matrix", help="显示兼容性矩阵")

    args = parser.parse_args()

    try:
        vm = VersionManager()

        if args.command == "show" or args.command is None:
            vm.show_all()

        elif args.command == "check":
            vm.check_consistency(verbose=not args.quiet)

        elif args.command == "impact":
            vm.analyze_impact(args.module, args.new_version)

        elif args.command == "bump":
            if args.dry_run:
                print("\n⚠️  (演练模式) 仅分析影响，不实际修改文件\n")
                vm.analyze_impact(args.module, "<new_version>")
            else:
                vm.bump_version(args.module, args.level)

        elif args.command == "matrix":
            vm.show_compatibility_matrix()

    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 请确保在 OpenClaw 工作区根目录运行此命令")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()