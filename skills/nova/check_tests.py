"""
测试覆盖检查工具 - 检查单元测试覆盖率、测试用例数量、断言质量、边界测试
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Set


class TestCoverageChecker:
    def __init__(self, path: str):
        self.path = Path(path)
        self.issues: List[Dict] = []
        self.score = 100
        self.findings = {
            "test_files": [],
            "total_test_files": 0,
            "total_test_functions": 0,
            "total_assertions": 0,
            "avg_assertions_per_test": 0,
            "tested_functions": set(),
            "all_functions": set(),
            "has_edge_case_tests": False,
            "has_setup_teardown": False
        }

    def run(self) -> Dict[str, Any]:
        """运行测试检查"""
        self._find_test_files()
        self._analyze_test_files()
        self._find_all_functions()
        self._calculate_coverage()
        self._check_assertion_quality()
        self._check_edge_cases()
        self._calculate_score()
        
        # 转换 set 为 list 以便 JSON 序列化
        self.findings["tested_functions"] = list(self.findings["tested_functions"])
        self.findings["all_functions"] = list(self.findings["all_functions"])
        
        return {
            "score": self.score,
            "findings": self.findings,
            "issues": self.issues,
            "suggestions": self._get_suggestions()
        }

    def _find_test_files(self):
        """查找测试文件"""
        test_patterns = [
            "test_*.py",
            "*_test.py",
            "tests/**/*.py",
            "test/**/*.py"
        ]
        
        test_files = []
        for pattern in test_patterns:
            test_files.extend(list(self.path.glob(pattern)))
        
        # 去重
        test_files = list(set(test_files))
        test_files = [f for f in test_files if '__pycache__' not in str(f)]
        
        self.findings["test_files"] = [str(f.relative_to(self.path)) for f in test_files]
        self.findings["total_test_files"] = len(test_files)
        
        if not test_files:
            self.issues.append({
                "type": "no_test_files",
                "severity": "high",
                "message": "未找到测试文件"
            })
        
        return test_files

    def _analyze_test_files(self):
        """分析测试文件内容"""
        test_files = self._find_test_files()
        total_assertions = 0
        test_func_count = 0
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                has_setup = False
                has_teardown = False
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_name = node.name.lower()
                        # 检查是否是测试函数
                        if func_name.startswith('test_'):
                            test_func_count += 1
                            
                            # 统计断言数量
                            assert_count = self._count_assertions(node)
                            total_assertions += assert_count
                            
                            # 记录测试的函数名（从测试函数名推断）
                            tested_func = func_name.replace('test_', '', 1)
                            if tested_func:
                                self.findings["tested_functions"].add(tested_func)
                        
                        # 检查 setup/teardown
                        if func_name in ['setUp', 'setup_method', 'setup']:
                            has_setup = True
                        if func_name in ['tearDown', 'teardown_method', 'teardown']:
                            has_teardown = True
                
                if has_setup and has_teardown:
                    self.findings["has_setup_teardown"] = True
            
            except Exception:
                continue
        
        self.findings["total_test_functions"] = test_func_count
        self.findings["total_assertions"] = total_assertions
        if test_func_count > 0:
            self.findings["avg_assertions_per_test"] = round(total_assertions / test_func_count, 2)

    def _count_assertions(self, node: ast.AST) -> int:
        """计算函数中的断言数量"""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                count += 1
            elif isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr.startswith('assert'):
                        count += 1
        return count

    def _find_all_functions(self):
        """查找所有待测试的函数"""
        for py_file in self.path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
            if 'test' in py_file.name.lower():
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not node.name.startswith('_'):
                            self.findings["all_functions"].add(node.name)
                    elif isinstance(node, ast.ClassDef):
                        for item in node.body:
                            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                if not item.name.startswith('_'):
                                    self.findings["all_functions"].add(item.name)
            except Exception:
                continue

    def _calculate_coverage(self):
        """计算测试覆盖率（基于函数名匹配）"""
        all_funcs = self.findings["all_functions"]
        tested_funcs = self.findings["tested_functions"]
        
        if not all_funcs:
            self.findings["function_coverage"] = 0
            return
        
        # 模糊匹配
        matched = 0
        for func in all_funcs:
            func_lower = func.lower()
            for tested in tested_funcs:
                tested_lower = tested.lower()
                if (func_lower in tested_lower or 
                    tested_lower in func_lower or
                    func_lower.replace('_', '') == tested_lower.replace('_', '')):
                    matched += 1
                    break
        
        coverage = matched / len(all_funcs)
        self.findings["function_coverage"] = round(coverage, 3)
        self.findings["matched_functions"] = matched
        self.findings["total_functions_to_test"] = len(all_funcs)
        
        if coverage < 0.3:
            self.issues.append({
                "type": "low_test_coverage",
                "severity": "high",
                "message": f"测试覆盖率过低: {coverage:.1%}",
                "coverage": coverage
            })

    def _check_assertion_quality(self):
        """检查断言质量"""
        avg_assert = self.findings.get("avg_assertions_per_test", 0)
        if avg_assert < 1:
            self.issues.append({
                "type": "poor_assertions",
                "severity": "medium",
                "message": f"平均每个测试函数的断言数过少: {avg_assert}",
                "avg_assertions": avg_assert
            })

    def _check_edge_cases(self):
        """检查边界测试"""
        edge_case_keywords = [
            'empty', 'null', 'none', 'zero', 'negative', 'max', 'min',
            '边界', '异常', '错误', 'invalid', 'error', 'exception',
            'edge', 'boundary', 'limit', 'corner'
        ]
        
        found_edge_cases = False
        test_files = self._find_test_files()
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                for keyword in edge_case_keywords:
                    if keyword in content:
                        found_edge_cases = True
                        break
                if found_edge_cases:
                    break
            except Exception:
                continue
        
        self.findings["has_edge_case_tests"] = found_edge_cases
        
        if not found_edge_cases and test_files:
            self.issues.append({
                "type": "no_edge_cases",
                "severity": "low",
                "message": "未发现边界条件测试"
            })

    def _calculate_score(self):
        """计算评分"""
        penalty = 0
        
        # 没有测试文件
        if self.findings["total_test_files"] == 0:
            penalty += 40
        else:
            # 测试覆盖率
            coverage = self.findings.get("function_coverage", 0)
            if coverage < 0.2:
                penalty += 25
            elif coverage < 0.4:
                penalty += 15
            elif coverage < 0.6:
                penalty += 10
            
            # 断言质量
            avg_assert = self.findings.get("avg_assertions_per_test", 0)
            if avg_assert < 0.5:
                penalty += 15
            elif avg_assert < 1:
                penalty += 10
            
            # 边界测试
            if not self.findings["has_edge_case_tests"]:
                penalty += 10
        
        self.score = max(0, 100 - penalty)

    def _get_suggestions(self) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if self.findings["total_test_files"] == 0:
            suggestions.append("创建测试文件，建议使用 test_ 前缀命名")
        else:
            coverage = self.findings.get("function_coverage", 0)
            if coverage < 0.5:
                suggestions.append(f"增加测试用例以提高覆盖率（当前: {coverage:.1%}）")
            
            avg_assert = self.findings.get("avg_assertions_per_test", 0)
            if avg_assert < 1:
                suggestions.append("在测试中添加更多断言，验证更多输出条件")
            
            if not self.findings["has_edge_case_tests"]:
                suggestions.append("添加边界条件测试（空值、异常输入、极值等）")
        
        return suggestions
