---
name: Excel Engine
slug: excel-engine
version: 1.0.0
description: "通用Excel智能处理引擎 - 高性能读写、公式保护、格式比对、透视表操作、样式批量应用。作为底层能力为所有Excel相关技能提供支持。"
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## 概述

Excel Engine 是一个通用的Excel处理底层引擎，从经营报告生成和交付中心月报技能中抽取固化而来。提供标准化的Excel/CSV处理接口，支持10万+行级数据高效处理。

## 技能定位

**通用能力层** → 所有需要Excel/CSV处理的智能体都可调用

## 核心功能

### 1. 高性能IO模块 (`excel_io.py`)
- 支持 10万+ 行级数据高效读写（openpyxl / pandas 双后端）
- CSV/Excel 自动格式检测
- 多 Sheet 批量读写
- 数据类型自动识别与转换

### 2. 公式保护模块 (`formula_protector.py`)
- 智能检测公式列
- 写入时自动跳过公式列
- 支持公式自动计算刷新
- 公式完整性校验（写入前后一致性检查）

### 3. 格式比对模块 (`format_checker.py`)
- 逐单元格格式比对（底色、边框、字体、字号、对齐、数字格式）
- 批量格式比对报告（Pass/Fail）
- 支持规则可配置

### 4. 透视表操作模块 (`pivot_controller.py`)
- 检测现有透视表位置与数据源
- 透视表数据源更新
- 透视表自动刷新

### 5. 样式批量应用模块 (`style_applicator.py`)
- 从模板复制样式到目标文件
- 支持按行/列批量设置样式

## 快速开始

### 安装依赖

```bash
pip install pandas openpyxl numpy pyyaml
```

### 基础使用示例

```python
from scripts.excel_io import ExcelIO
from scripts.formula_protector import FormulaProtector
from scripts.format_checker import FormatChecker

# 1. 读取Excel/CSV文件
io = ExcelIO()
data = io.read_file("data.csv")  # 自动检测格式

# 2. 写入数据到模板（带公式保护）
protector = FormulaProtector("template.xlsx")
protector.write_data("Sheet1", data, start_row=2)
protector.save("output.xlsx")

# 3. 格式校验
checker = FormatChecker("template.xlsx", "output.xlsx")
report = checker.check_all_sheets()
print(f"校验结果: {'通过' if report['success'] else '失败'}")
```

## 接口文档

### ExcelIO 类

```python
class ExcelIO:
    """高性能Excel/CSV读写类"""
    
    def read_file(self, file_path: str, sheet_name: str = None, **kwargs) -> pd.DataFrame:
        """
        读取文件，自动检测格式
        
        Args:
            file_path: 文件路径
            sheet_name: Sheet名称（仅Excel有效）
            **kwargs: 传递给pandas的额外参数
            
        Returns:
            pd.DataFrame
        """
    
    def read_all_sheets(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """读取Excel的所有Sheet"""
    
    def write_excel(self, file_path: str, data: Dict[str, pd.DataFrame], 
                    template_path: str = None, **kwargs):
        """
        写入Excel文件
        
        Args:
            file_path: 输出文件路径
            data: {sheet_name: dataframe} 字典
            template_path: 可选模板路径
        """
    
    def detect_format(self, file_path: str) -> str:
        """检测文件格式: 'excel' 或 'csv'"""
    
    @staticmethod
    def optimize_for_large_data(df: pd.DataFrame) -> pd.DataFrame:
        """优化大内存占用的DataFrame"""
```

### FormulaProtector 类

```python
class FormulaProtector:
    """公式保护与自动计算类"""
    
    def __init__(self, workbook_path: str, data_only: bool = False):
        """加载工作簿"""
    
    def detect_formula_columns(self, sheet_name: str, analyze_rows: int = 50) -> List[int]:
        """
        检测公式列
        
        Args:
            sheet_name: Sheet名称
            analyze_rows: 分析的行数
            
        Returns:
            公式列的列号列表（从1开始）
        """
    
    def write_data(self, sheet_name: str, data: pd.DataFrame, 
                   start_row: int = 2, skip_formula_columns: bool = True):
        """
        写入数据，自动跳过公式列
        
        Args:
            sheet_name: Sheet名称
            data: 要写入的数据
            start_row: 起始行号（从1开始）
            skip_formula_columns: 是否跳过公式列
        """
    
    def refresh_formulas(self, sheet_name: str = None):
        """刷新公式（标记需要Excel重新计算）"""
    
    def verify_formula_integrity(self, sheet_name: str, original_formulas: Dict) -> Dict:
        """校验公式完整性"""
    
    def save(self, output_path: str):
        """保存工作簿"""
```

### FormatChecker 类

```python
class FormatChecker:
    """格式校验类"""
    
    def __init__(self, template_path: str, generated_path: str, rules_path: str = None):
        """
        初始化格式校验器
        
        Args:
            template_path: 模板文件路径
            generated_path: 生成文件路径
            rules_path: 规则配置文件路径
        """
    
    def check_all_sheets(self, max_rows: int = 1000, 
                         check_types: List[str] = None) -> Dict[str, Any]:
        """
        校验所有Sheet格式
        
        Args:
            max_rows: 每个Sheet最大检查行数
            check_types: 检查类型列表，可选: fill, font, border, alignment, number_format
            
        Returns:
            校验报告字典
        """
    
    def check_sheet(self, sheet_name: str, max_rows: int = 1000) -> Dict[str, Any]:
        """校验单个Sheet"""
    
    def save_report(self, output_path: str):
        """保存校验报告到JSON文件"""
```

### PivotController 类

```python
class PivotController:
    """透视表操作类"""
    
    def __init__(self, workbook_path: str):
        """加载工作簿"""
    
    def detect_pivot_tables(self, sheet_name: str = None) -> Dict[str, List]:
        """检测透视表位置"""
    
    def update_pivot_data_source(self, pivot_name: str, new_data_range: str):
        """更新透视表数据源"""
    
    def refresh_all_pivots(self):
        """刷新所有透视表"""
    
    def save(self, output_path: str):
        """保存工作簿"""
```

### StyleApplicator 类

```python
class StyleApplicator:
    """样式批量应用类"""
    
    def __init__(self, template_path: str):
        """加载模板"""
    
    def copy_style_from_template(self, template_sheet: str, target_wb, target_sheet: str,
                                 row_range: Tuple[int, int] = None, 
                                 col_range: Tuple[int, int] = None):
        """
        从模板复制样式到目标文件
        
        Args:
            template_sheet: 模板Sheet名
            target_wb: 目标工作簿
            target_sheet: 目标Sheet名
            row_range: 行范围 (start, end)
            col_range: 列范围 (start, end)
        """
    
    def apply_row_style(self, ws, row_num: int, style_template):
        """应用行样式"""
    
    def apply_column_style(self, ws, col_num: int, style_template):
        """应用列样式"""
```

## 配置文件

### config/formula-rules.yaml
公式处理规则配置，详见文件内部注释

### config/format-rules.yaml
格式比对规则配置，详见文件内部注释

### config/data-import.yaml
数据导入规则配置，详见文件内部注释

## 性能优化建议

### 大文件处理技巧

1. **使用 pandas 读取大数据**
   ```python
   # 分块读取
   chunks = pd.read_csv("large_file.csv", chunksize=10000)
   for chunk in chunks:
       process(chunk)
   ```

2. **指定 dtype 减少内存占用**
   ```python
   df = pd.read_csv("data.csv", dtype={
       'id': str,
       'amount': 'float32'
   }, low_memory=False)
   ```

3. **openpyxl 优化模式**
   ```python
   wb = openpyxl.load_workbook(
       "large.xlsx",
       read_only=True,  # 只读模式
       data_only=True   # 只读取值
   )
   ```

4. **避免遍历整个工作表**
   - 只读取需要的范围
   - 使用 ws.iter_rows() 代替 ws[row][col]

## 常见问题

### Q: 写入数据后公式不更新？
A: openpyxl 不会自动计算公式，需要在Excel中打开时触发计算。可以使用 `refresh_formulas()` 标记需要重新计算。

### Q: 大文件写入太慢？
A: 推荐使用 pandas 的 ExcelWriter，配合 openpyxl 引擎，避免逐单元格操作。

### Q: 格式校验报告差异很多？
A: 
1. 检查是否只需要检查表头区域
2. 使用 `max_rows` 参数限制检查行数
3. 通过 format-rules.yaml 配置忽略特定类型的格式检查

### Q: 透视表更新后数据不刷新？
A: 需要在Excel中手动刷新，或使用VBA宏自动刷新。openpyxl 支持更新数据源但不执行计算。

### Q: 中文乱码？
A: CSV文件读取时指定编码: `pd.read_csv(path, encoding='utf-8-sig')` 或 `encoding='gbk'`

## 代码风格

- 遵循 PEP 8 规范
- 使用类型注解 (type hints)
- 详细的 docstring 文档
- 模块化设计，单一职责原则

## 版本历史

- v1.0.0 (2026-04-24) - 初始版本，从经营报告生成和交付中心月报技能抽取固化
