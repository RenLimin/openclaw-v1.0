"""
依赖检查工具 - 检查 requirements.txt、setup.py、import 依赖
识别未声明/未使用/版本冲突
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


class DependencyChecker:
    def __init__(self, path: str):
        self.path = Path(path)
        self.declared_deps: Dict[str, str] = {}  # package -> version
        self.imported_modules: Set[str] = set()
        self.used_packages: Set[str] = set()
        self.issues: List[Dict] = []
        self.score = 100

    def run(self) -> Dict[str, Any]:
        """运行依赖检查"""
        self._parse_requirements()
        self._parse_setup_py()
        self._scan_imports()
        self._map_imports_to_packages()
        self._check_issues()
        self._calculate_score()
        
        return {
            "score": self.score,
            "declared_dependencies": self.declared_deps,
            "imported_modules": list(self.imported_modules),
            "used_packages": list(self.used_packages),
            "issues": self.issues,
            "suggestions": self._get_suggestions()
        }

    def _parse_requirements(self):
        """解析 requirements.txt"""
        req_file = self.path / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 解析包名和版本
                        match = re.match(r'^([a-zA-Z0-9_-]+)([<>=!].*)?$', line)
                        if match:
                            pkg, version = match.groups()
                            self.declared_deps[pkg.lower()] = version or "*"

    def _parse_setup_py(self):
        """解析 setup.py 中的 install_requires"""
        setup_file = self.path / "setup.py"
        if setup_file.exists():
            try:
                with open(setup_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 简单的正则匹配 install_requires
                match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if match:
                    reqs_str = match.group(1)
                    for line in reqs_str.split(','):
                        line = line.strip().strip('"\'')
                        if line:
                            match_pkg = re.match(r'^([a-zA-Z0-9_-]+)([<>=!].*)?$', line)
                            if match_pkg:
                                pkg, version = match_pkg.groups()
                                self.declared_deps[pkg.lower()] = version or "*"
            except Exception:
                pass

    def _scan_imports(self):
        """扫描所有 Python 文件中的 import 语句"""
        for py_file in self.path.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_name = alias.name.split('.')[0]
                            self.imported_modules.add(module_name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_name = node.module.split('.')[0]
                            self.imported_modules.add(module_name)
            except Exception:
                continue

    def _map_imports_to_packages(self):
        """将导入的模块映射到 PyPI 包名"""
        # 常见的包名与模块名映射
        common_mapping = {
            'bs4': 'beautifulsoup4',
            'PIL': 'pillow',
            'yaml': 'pyyaml',
            'dotenv': 'python-dotenv',
            'dateutil': 'python-dateutil',
            'pytz': 'pytz',
            'requests': 'requests',
            'numpy': 'numpy',
            'pandas': 'pandas',
            'openpyxl': 'openpyxl',
            'docx': 'python-docx',
            'pdfplumber': 'pdfplumber',
            'playwright': 'playwright',
            'sqlalchemy': 'sqlalchemy',
            'jsonschema': 'jsonschema',
        }
        
        std_libs = self._get_std_libs()
        
        # 获取当前目录下的所有 Python 文件和目录名作为内部模块
        internal_modules = set()
        for py_file in self.path.rglob("*.py"):
            internal_modules.add(py_file.stem)
        # 添加目录名（包名）
        for dir_path in self.path.rglob("*"):
            if dir_path.is_dir() and not dir_path.name.startswith('.'):
                internal_modules.add(dir_path.name)
        # 添加根目录名
        internal_modules.add(self.path.name)
        
        for module in self.imported_modules:
            if module in std_libs:
                continue
            if module in internal_modules:
                continue  # 跳过内部模块
            pkg_name = common_mapping.get(module, module.lower())
            self.used_packages.add(pkg_name)

    def _get_std_libs(self) -> Set[str]:
        """获取标准库列表"""
        return {
            'os', 'sys', 're', 'json', 'ast', 'math', 'datetime', 'time',
            'collections', 'itertools', 'functools', 'pathlib', 'typing',
            'enum', 'dataclasses', 'logging', 'argparse', 'subprocess',
            'threading', 'multiprocessing', 'queue', 'socket', 'http',
            'urllib', 'hashlib', 'base64', 'csv', 'configparser', 'shutil',
            'tempfile', 'random', 'statistics', 'string', 'copy', 'pickle',
            'inspect', 'warnings', 'abc', 'types', 'weakref', 'gc',
            'uuid', 'traceback', 'glob', 'io', 'platform', 'zlib'
        }

    def _check_issues(self):
        """检查问题"""
        # 未声明的依赖
        for pkg in self.used_packages:
            if pkg not in self.declared_deps and pkg:
                self.issues.append({
                    "type": "undeclared_dependency",
                    "severity": "high",
                    "message": f"依赖未声明: {pkg}",
                    "package": pkg
                })

        # 未使用的依赖
        for pkg in self.declared_deps:
            if pkg not in self.used_packages:
                self.issues.append({
                    "type": "unused_dependency",
                    "severity": "low",
                    "message": f"依赖已声明但未使用: {pkg}",
                    "package": pkg
                })

    def _calculate_score(self):
        """计算评分"""
        high_count = sum(1 for i in self.issues if i['severity'] == 'high')
        low_count = sum(1 for i in self.issues if i['severity'] == 'low')
        
        penalty = high_count * 15 + low_count * 5
        self.score = max(0, 100 - penalty)

    def _get_suggestions(self) -> List[str]:
        """生成改进建议"""
        suggestions = []
        undeclared = [i['package'] for i in self.issues if i['type'] == 'undeclared_dependency']
        unused = [i['package'] for i in self.issues if i['type'] == 'unused_dependency']
        
        if undeclared:
            suggestions.append(f"请在 requirements.txt 中声明以下依赖: {', '.join(undeclared)}")
        if unused:
            suggestions.append(f"考虑移除以下未使用的依赖: {', '.join(unused)}")
        if not self.declared_deps:
            suggestions.append("建议创建 requirements.txt 声明项目依赖")
        
        return suggestions
