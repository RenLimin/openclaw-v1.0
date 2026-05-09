"""
Nova Skill Vetting Toolchain - 统一 CLI 入口
使用方式: python -m skills.nova.vet [路径] [选项]
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from .check_deps import DependencyChecker
from .check_docs import DocumentationChecker
from .check_size import GranularityChecker
from .check_tests import TestCoverageChecker
from .version_manager import VersionManager


class SkillVettingToolchain:
    def __init__(self, path: str, output_format: str = "both"):
        self.path = Path(path)
        self.output_format = output_format
        self.results = {}
        self.version_manager = VersionManager(path)

    def run_all(self):
        """运行所有检查"""
        self.run_deps_check()
        self.run_docs_check()
        self.run_size_check()
        self.run_tests_check()
        self._calculate_overall_score()
        return self.results

    def run_deps_check(self):
        """运行依赖检查"""
        checker = DependencyChecker(str(self.path))
        self.results["dependencies"] = checker.run()
        self.version_manager.record_score("dependencies", self.results["dependencies"]["score"])
        return self.results["dependencies"]

    def run_docs_check(self):
        """运行文档检查"""
        checker = DocumentationChecker(str(self.path))
        self.results["documentation"] = checker.run()
        self.version_manager.record_score("documentation", self.results["documentation"]["score"])
        return self.results["documentation"]

    def run_size_check(self):
        """运行颗粒度检查"""
        checker = GranularityChecker(str(self.path))
        self.results["granularity"] = checker.run()
        self.version_manager.record_score("granularity", self.results["granularity"]["score"])
        return self.results["granularity"]

    def run_tests_check(self):
        """运行测试覆盖检查"""
        checker = TestCoverageChecker(str(self.path))
        self.results["testing"] = checker.run()
        self.version_manager.record_score("testing", self.results["testing"]["score"])
        return self.results["testing"]

    def _calculate_overall_score(self):
        """计算综合评分"""
        scores = []
        weights = {
            "dependencies": 0.2,
            "documentation": 0.3,
            "granularity": 0.25,
            "testing": 0.25
        }
        
        for key, weight in weights.items():
            if key in self.results:
                scores.append(self.results[key]["score"] * weight)
        
        overall = sum(scores) if scores else 0
        self.results["overall"] = {
            "score": round(overall, 1),
            "timestamp": datetime.now().isoformat(),
            "skill_name": self.path.name,
            "version": self.version_manager.meta["version"]
        }
        return self.results["overall"]

    def print_human_readable(self):
        """输出人类可读的报告"""
        print("=" * 70)
        print(f"Nova Skill Vetting Report - {self.path.name}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        if "overall" in self.results:
            overall = self.results["overall"]
            grade = self._get_grade(overall["score"])
            print(f"\n🏆 综合评分: {overall['score']:.1f} / 100 [{grade}]")
            print(f"   版本: {overall['version']}")
        
        print("\n" + "-" * 70)
        
        categories = [
            ("📦 依赖检查", "dependencies"),
            ("📚 文档检查", "documentation"),
            ("📏 颗粒度检查", "granularity"),
            ("🧪 测试检查", "testing")
        ]
        
        for title, key in categories:
            if key in self.results:
                r = self.results[key]
                grade = self._get_grade(r["score"])
                print(f"\n{title}: {r['score']} / 100 [{grade}]")
                
                if r.get("issues"):
                    print("   问题:")
                    for issue in r["issues"][:5]:  # 最多显示5个
                        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.get("severity", "low"), "⚪")
                        print(f"   {severity_icon} {issue['message']}")
                    if len(r["issues"]) > 5:
                        print(f"   ... 还有 {len(r['issues']) - 5} 个问题")
                
                if r.get("suggestions"):
                    print("   建议:")
                    for suggestion in r["suggestions"]:
                        print(f"   💡 {suggestion}")
        
        print("\n" + "=" * 70)

    def _get_grade(self, score: int) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"

    def get_json_output(self) -> str:
        """获取 JSON 格式输出"""
        return json.dumps(self.results, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Nova Skill Vetting Toolchain v1.0")
    parser.add_argument("path", nargs="?", default=".", help="技能目录路径")
    parser.add_argument("--check-deps", action="store_true", help="仅运行依赖检查")
    parser.add_argument("--check-docs", action="store_true", help="仅运行文档检查")
    parser.add_argument("--check-size", action="store_true", help="仅运行颗粒度检查")
    parser.add_argument("--check-tests", action="store_true", help="仅运行测试检查")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--report", action="store_true", help="输出人类可读报告")
    parser.add_argument("--output", "-o", help="输出文件路径")
    
    # 版本管理命令
    parser.add_argument("--bump-version", choices=["major", "minor", "patch"], help="升级版本号")
    parser.add_argument("--checkpoint", help="创建检查点并添加描述")
    parser.add_argument("--rollback", help="回滚到指定检查点ID")
    parser.add_argument("--list-checkpoints", action="store_true", help="列出所有检查点")
    parser.add_argument("--changelog", help="生成变更日志，传入变更信息JSON")
    
    args = parser.parse_args()
    
    toolchain = SkillVettingToolchain(args.path)
    
    # 版本管理命令
    if args.bump_version:
        new_version = toolchain.version_manager.bump_version(args.bump_version)
        print(f"✅ 版本已升级到: {new_version}")
        return
    
    if args.checkpoint is not None:
        checkpoint = toolchain.version_manager.create_checkpoint(args.checkpoint)
        print(f"✅ 检查点已创建: {checkpoint['id']}")
        return
    
    if args.rollback is not None:
        success = toolchain.version_manager.rollback(args.rollback)
        if success:
            print(f"✅ 已回滚到检查点")
        else:
            print(f"❌ 回滚失败")
        return
    
    if args.list_checkpoints:
        checkpoints = toolchain.version_manager.list_checkpoints()
        if checkpoints:
            print(f"共有 {len(checkpoints)} 个检查点:")
            for cp in checkpoints:
                print(f"  - {cp['id']} (v{cp['version']}) {cp.get('message', '')}")
        else:
            print("没有检查点")
        return
    
    # 运行检查
    run_all = not (args.check_deps or args.check_docs or args.check_size or args.check_tests)
    
    if run_all:
        toolchain.run_all()
    else:
        if args.check_deps:
            toolchain.run_deps_check()
        if args.check_docs:
            toolchain.run_docs_check()
        if args.check_size:
            toolchain.run_size_check()
        if args.check_tests:
            toolchain.run_tests_check()
        toolchain._calculate_overall_score()
    
    # 输出
    output_json = args.json or args.output
    output_report = args.report or not args.json
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(toolchain.get_json_output())
        print(f"✅ JSON 报告已保存到: {args.output}")
    
    if output_json and not args.output:
        print(toolchain.get_json_output())
    
    if output_report:
        toolchain.print_human_readable()


if __name__ == "__main__":
    main()
