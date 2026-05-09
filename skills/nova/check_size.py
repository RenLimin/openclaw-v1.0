"""
颗粒度检查工具 - 检查单个技能文件行数、函数数量、圈复杂度、单一职责
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any


class GranularityChecker:
    def __init__(self, path: str):
        self.path = Path(path)
        self.issues: List[Dict] = []
        self.score = 100
        self.findings = {
            "files": [],
            "total_files": 0,
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "avg_complexity": 0,
            "high_complexity_functions": []
        }

    def run(self) -> Dict[str, Any]:
        """运行颗粒度检查"""
        self._scan_files()
        self._check_single_responsibility()
        self._calculate_score()
        
        return {
            "score": self.score,
            "findings": self.findings,
            "issues": self.issues,
            "suggestions": self._get_suggestions()
        }

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            # 增加复杂度的节点
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.IfExp):  # 三元表达式
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):  # 逻辑运算符
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.Match):  # Python 3.10+ match 语句
                complexity += len(child.cases)
        
        return complexity

    def _scan_files(self):
        """扫描所有 Python 文件"""
        file_stats = []
        
        for py_file in self.path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = [line.rstrip() for line in f]
                
                # 统计代码行数（排除空行和纯注释行）
                code_lines = 0
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        code_lines += 1
                
                # 解析 AST
                try:
                    tree = ast.parse('\n'.join(lines))
                except SyntaxError:
                    continue
                
                functions = []
                classes = []
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not node.name.startswith('_'):
                            func_lines = node.end_lineno - node.lineno + 1
                            complexity = self._calculate_cyclomatic_complexity(node)
                            functions.append({
                                "name": node.name,
                                "lines": func_lines,
                                "complexity": complexity
                            })
                            
                            if complexity > 15:
                                self.findings["high_complexity_functions"].append({
                                    "file": str(py_file.relative_to(self.path)),
                                    "function": node.name,
                                    "complexity": complexity
                                })
                    
                    elif isinstance(node, ast.ClassDef):
                        class_methods = []
                        for item in node.body:
                            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                class_methods.append(item.name)
                        classes.append({
                            "name": node.name,
                            "methods": class_methods,
                            "method_count": len(class_methods)
                        })
                
                file_stats.append({
                    "file": str(py_file.relative_to(self.path)),
                    "total_lines": len(lines),
                    "code_lines": code_lines,
                    "function_count": len(functions),
                    "class_count": len(classes),
                    "functions": functions,
                    "classes": classes
                })
                
                # 检查文件大小
                if code_lines > 500:
                    self.issues.append({
                        "type": "file_too_large",
                        "severity": "medium",
                        "message": f"文件过大: {py_file.name} ({code_lines} 行代码)",
                        "file": str(py_file.relative_to(self.path)),
                        "lines": code_lines
                    })
                
                # 检查函数大小
                for func in functions:
                    if func["lines"] > 80:
                        self.issues.append({
                            "type": "function_too_large",
                            "severity": "medium",
                            "message": f"函数过大: {func['name']} ({func['lines']} 行)",
                            "file": str(py_file.relative_to(self.path)),
                            "function": func["name"],
                            "lines": func["lines"]
                        })
                
                # 检查圈复杂度
                for func in functions:
                    if func["complexity"] > 15:
                        self.issues.append({
                            "type": "high_cyclomatic_complexity",
                            "severity": "medium",
                            "message": f"圈复杂度过高: {func['name']} (复杂度={func['complexity']})",
                            "file": str(py_file.relative_to(self.path)),
                            "function": func["name"],
                            "complexity": func["complexity"]
                        })
            
            except Exception as e:
                continue
        
        self.findings["files"] = file_stats
        self.findings["total_files"] = len(file_stats)
        self.findings["total_lines"] = sum(f["total_lines"] for f in file_stats)
        self.findings["total_code_lines"] = sum(f["code_lines"] for f in file_stats)
        self.findings["total_functions"] = sum(f["function_count"] for f in file_stats)
        self.findings["total_classes"] = sum(f["class_count"] for f in file_stats)
        
        # 平均圈复杂度
        all_complexities = []
        for f in file_stats:
            for func in f["functions"]:
                all_complexities.append(func["complexity"])
        if all_complexities:
            self.findings["avg_complexity"] = round(sum(all_complexities) / len(all_complexities), 2)

    def _check_single_responsibility(self):
        """检查单一职责原则"""
        for file_info in self.findings["files"]:
            # 检查类的方法数量
            for cls in file_info["classes"]:
                if cls["method_count"] > 15:
                    self.issues.append({
                        "type": "class_too_large",
                        "severity": "medium",
                        "message": f"类可能承担过多职责: {cls['name']} ({cls['method_count']} 个方法)",
                        "file": file_info["file"],
                        "class": cls["name"],
                        "methods": cls["method_count"]
                    })
            
            # 检查文件中的类数量
            if file_info["class_count"] > 3:
                self.issues.append({
                    "type": "too_many_classes",
                    "severity": "low",
                    "message": f"文件中类过多: {file_info['file']} ({file_info['class_count']} 个类)",
                    "file": file_info["file"]
                })

    def _calculate_score(self):
        """计算评分"""
        penalty = 0
        
        # 文件过大
        large_files = sum(1 for i in self.issues if i["type"] == "file_too_large")
        penalty += large_files * 10
        
        # 函数过大
        large_funcs = sum(1 for i in self.issues if i["type"] == "function_too_large")
        penalty += large_funcs * 5
        
        # 高复杂度
        high_complex = sum(1 for i in self.issues if i["type"] == "high_cyclomatic_complexity")
        penalty += high_complex * 8
        
        # 大类
        large_classes = sum(1 for i in self.issues if i["type"] == "class_too_large")
        penalty += large_classes * 5
        
        # 平均复杂度
        avg_complex = self.findings.get("avg_complexity", 0)
        if avg_complex > 10:
            penalty += 10
        
        self.score = max(0, 100 - penalty)

    def _get_suggestions(self) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 文件过大建议
        large_files = [i["file"] for i in self.issues if i["type"] == "file_too_large"]
        if large_files:
            suggestions.append(f"考虑拆分以下大文件: {', '.join(large_files)}")
        
        # 函数过大建议
        large_funcs = [f"{i['function']}({i['file']})" for i in self.issues if i["type"] == "function_too_large"]
        if large_funcs:
            suggestions.append(f"考虑拆分以下大函数: {', '.join(large_funcs[:3])}" + (" 等" if len(large_funcs) > 3 else ""))
        
        # 高复杂度建议
        high_complex = [f"{i['function']}(复杂度={i['complexity']})" for i in self.issues if i["type"] == "high_cyclomatic_complexity"]
        if high_complex:
            suggestions.append(f"重构以下高复杂度函数以降低圈复杂度: {', '.join(high_complex[:3])}")
        
        # 平均复杂度
        avg_complex = self.findings.get("avg_complexity", 0)
        if avg_complex > 10:
            suggestions.append(f"整体平均圈复杂度较高 ({avg_complex})，建议整体重构降低复杂度")
        
        return suggestions
