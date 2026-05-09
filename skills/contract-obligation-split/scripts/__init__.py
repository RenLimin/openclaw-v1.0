# 履约义务拆分技能
# ===================

__version__ = "1.0.0"
__author__ = "Ella 🦊"
__description__ = "履约义务拆分业务技能 - OCR识别 → 条款拆分 → 义务提取 → 标准比对 → Excel导出"

from .obligation_splitter import ObligationSplitter

__all__ = ["ObligationSplitter"]
