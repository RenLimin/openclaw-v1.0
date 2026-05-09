# Word 文档智能分析工具包

from .word_parser import WordParser, ParagraphStyle
from .table_extractor import TableExtractor
from .style_comparator import StyleComparator
from .toc_generator import TOCGenerator

__all__ = [
    'WordParser',
    'ParagraphStyle',
    'TableExtractor',
    'StyleComparator',
    'TOCGenerator',
]

__version__ = '1.0.0'
