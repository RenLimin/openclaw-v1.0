#!/usr/bin/env python3
"""
Excel Engine - 通用Excel智能处理引擎
========================================

这是一个独立固化的通用Excel处理底层能力，提供：
- 高性能Excel/CSV读写
- 公式保护与自动计算
- 格式校验与比对
- 透视表操作
- 样式批量应用

版本: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Jerry 🦞"

# 导出核心类
from .excel_io import ExcelIO
from .formula_protector import FormulaProtector
from .format_checker import FormatChecker
from .pivot_controller import PivotController
from .style_applicator import StyleApplicator

__all__ = [
    'ExcelIO',
    'FormulaProtector',
    'FormatChecker',
    'PivotController',
    'StyleApplicator',
]
