"""
文档检查工具 - 检查 README.md、API 文档、代码注释、示例代码完整性
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any


class DocumentationChecker:
    def __init__(self, path: str):
        self.path = Path(path)
        self.issues: List[Dict] = []
        self.score = 100
        self.findings = {
            "readme_exists": False,
            "readme_sections": [],
            "has_docstrings": 0,
            "total_functions": 0,
            "has_example_code": False,
            "comment_ratio": 0.0,
            "total_lines": 0,
            "comment_lines": 0
        }

    def run(self) -> Dict[str, Any]:
        """运行文档检查"""
        self._check_readme()
        self._check_docstrings()
        self._check_comments()
        self._check_example_code()
        self._check_skill_md()
        self._calculate_score()
        
        return {
            "score": self.score,
            "findings": self.findings,
            "issues": self.issues,
            "suggestions": self._get_suggestions()
        }

    def _check_readme(self):
        """检查 README.md"""
        readme_file = self.path / "README.md"
        if not readme_file.exists():
            self.issues.append({
                "type": "missing_readme",
                "severity": "high",
                "message": "缺少 README.md 文件"
            })
            return
        
        self.findings["readme_exists"] = True
        
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键章节
        sections = {
            "功能说明": ["功能", "功能说明", "简介", "概述", "introduction", "features"],
            "安装说明": ["安装", "install", "setup", "依赖"],
            "使用方法": ["使用", "用法", "使用方法", "usage", "example"],
            "API 说明": ["API", "接口", "函数说明", "参数"],
        }
        
        found_sections = []
        for section_name, keywords in sections.items():
            for keyword in keywords:
                if re.search(r'^#.*' + re.escape(keyword), content, re.IGNORECASE | re.MULTILINE):
                    found_sections.append(section_name)
                    break
        
        self.findings["readme_sections"] = found_sections
        
        missing = len(sections) - len(found_sections)
        if missing > 0:
            self.issues.append({
                "type": "incomplete_readme",
                "severity": "medium",
                "message": f"README 缺少 {missing} 个关键章节"
            })

    def _check_skill_md(self):
        """检查 SKILL.md"""
        skill_md = self.path / "SKILL.md"
        if skill_md.exists():
            self.findings["has_skill_md"] = True
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content.strip()) < 50:
                    self.issues.append({
                        "type": "empty_skill_md",
                        "severity": "low",
                        "message": "SKILL.md 内容过短"
                    })
        else:
            self.findings["has_skill_md"] = False
            self.issues.append({
                "type": "missing_skill_md",
                "severity": "medium",
                "message": "缺少 SKILL.md 技能描述文件"
            })

    def _check_docstrings(self):
        """检查函数和类的文档字符串"""
        for py_file in self.path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        if not node.name.startswith('_') or node.name == '__init__':
                            self.findings["total_functions"] += 1
                            docstring = ast.get_docstring(node)
                            if docstring and len(docstring.strip()) > 10:
                                self.findings["has_docstrings"] += 1
            except Exception:
                continue

    def _check_comments(self):
        """检查代码注释比例"""
        total_lines = 0
        comment_lines = 0
        
        for py_file in self.path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
            with open(py_file, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        total_lines += 1
                        if stripped.startswith('#'):
                            comment_lines += 1
        
        self.findings["total_lines"] = total_lines
        self.findings["comment_lines"] = comment_lines
        if total_lines > 0:
            ratio = comment_lines / total_lines
            self.findings["comment_ratio"] = round(ratio, 3)
            
            if ratio < 0.05:
                self.issues.append({
                    "type": "low_comment_ratio",
                    "severity": "low",
                    "message": f"注释比例过低: {ratio:.1%}"
                })

    def _check_example_code(self):
        """检查示例代码"""
        example_files = list(self.path.glob("example*.py")) + list(self.path.glob("*_example*.py"))
        if example_files:
            self.findings["has_example_code"] = True
            self.findings["example_files"] = [f.name for f in example_files]
        else:
            # 检查 README 中是否有代码块
            readme_file = self.path / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if re.search(r'```python', content):
                    self.findings["has_example_code"] = True
                    self.findings["example_in_readme"] = True

    def _calculate_score(self):
        """计算评分"""
        penalty = 0
        
        # README 相关
        if not self.findings["readme_exists"]:
            penalty += 25
        else:
            missing_sections = 4 - len(self.findings.get("readme_sections", []))
            penalty += missing_sections * 5
        
        # 文档字符串
        if self.findings["total_functions"] > 0:
            docstring_ratio = self.findings["has_docstrings"] / self.findings["total_functions"]
            if docstring_ratio < 0.3:
                penalty += 15
            elif docstring_ratio < 0.6:
                penalty += 10
        
        # 注释比例
        comment_ratio = self.findings.get("comment_ratio", 0)
        if comment_ratio < 0.05:
            penalty += 10
        elif comment_ratio < 0.1:
            penalty += 5
        
        # 示例代码
        if not self.findings["has_example_code"]:
            penalty += 10
        
        # SKILL.md
        if not self.findings.get("has_skill_md", False):
            penalty += 15
        
        self.score = max(0, 100 - penalty)

    def _get_suggestions(self) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if not self.findings["readme_exists"]:
            suggestions.append("创建 README.md 文件，包含功能说明、安装方法和使用示例")
        else:
            expected = ["功能说明", "安装说明", "使用方法", "API 说明"]
            missing = [s for s in expected if s not in self.findings.get("readme_sections", [])]
            if missing:
                suggestions.append(f"在 README 中补充以下章节: {', '.join(missing)}")
        
        if self.findings["total_functions"] > 0:
            ratio = self.findings["has_docstrings"] / self.findings["total_functions"]
            if ratio < 0.5:
                suggestions.append(f"为函数和类添加 docstring（当前覆盖率: {ratio:.1%}）")
        
        if not self.findings["has_example_code"]:
            suggestions.append("提供示例代码，可以是 example.py 文件或 README 中的代码片段")
        
        if not self.findings.get("has_skill_md", False):
            suggestions.append("创建 SKILL.md 技能描述文件")
        
        return suggestions
