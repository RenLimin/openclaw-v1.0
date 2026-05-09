#!/usr/bin/env python3
"""
Excel Engine 使用示例
======================
展示Excel引擎各个模块的基本使用方法
"""

import sys
from pathlib import Path

# 添加 scripts 目录到路径
scripts_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from excel_io import ExcelIO
from formula_protector import FormulaProtector
from format_checker import FormatChecker
from pivot_controller import PivotController
from style_applicator import StyleApplicator


def example_1_read_write():
    """示例1: 读写Excel/CSV文件"""
    print("\n" + "="*60)
    print("示例1: 读写Excel/CSV文件")
    print("="*60)
    
    io = ExcelIO()
    
    # 读取CSV文件（自动检测编码）
    # df = io.read_file("data.csv")
    # print(f"读取CSV: {len(df)} 行")
    
    # 读取Excel文件
    # df = io.read_file("data.xlsx", sheet_name="Sheet1")
    # print(f"读取Excel: {len(df)} 行")
    
    # 读取所有Sheet
    # sheets = io.read_all_sheets("data.xlsx")
    # print(f"读取所有Sheet: {list(sheets.keys())}")
    
    # 写入Excel
    # io.write_excel("output.xlsx", {"Sheet1": df})
    
    print("✓ 读写功能就绪")
    print("  API: io.read_file(path), io.write_excel(path, data_dict)")


def example_2_formula_protection():
    """示例2: 公式保护"""
    print("\n" + "="*60)
    print("示例2: 公式保护")
    print("="*60)
    
    # 使用 with 语句自动管理资源
    # with FormulaProtector("template.xlsx") as protector:
    #     # 检测公式列
    #     formula_cols = protector.detect_formula_columns("Sheet1")
    #     print(f"检测到公式列: {formula_cols}")
    #     
    #     # 写入数据（自动跳过公式列）
    #     protector.write_data("Sheet1", df, start_row=2)
    #     
    #     # 校验公式完整性
    #     report = protector.verify_formula_integrity()
    #     print(f"公式校验: {report['success']}")
    #     
    #     # 保存
    #     protector.save("output.xlsx")
    
    print("✓ 公式保护功能就绪")
    print("  API: protector.write_data(), protector.verify_formula_integrity()")


def example_3_format_check():
    """示例3: 格式校验"""
    print("\n" + "="*60)
    print("示例3: 格式校验")
    print("="*60)
    
    # with FormatChecker("template.xlsx", "output.xlsx") as checker:
    #     # 校验所有Sheet
    #     report = checker.check_all_sheets(max_rows=500)
    #     print(f"校验结果: {'通过' if report['success'] else '未通过'}")
    #     print(f"检查单元格: {report['total_cells_checked']}")
    #     print(f"差异数量: {len(report['differences'])}")
    #     
    #     # 打印差异详情
    #     checker.print_differences(report, limit=10)
    #     
    #     # 保存报告
    #     checker.save_report("format_report.json", report)
    
    print("✓ 格式校验功能就绪")
    print("  API: checker.check_all_sheets(), checker.print_differences()")


def example_4_pivot_control():
    """示例4: 透视表操作"""
    print("\n" + "="*60)
    print("示例4: 透视表操作")
    print("="*60)
    
    # with PivotController("report.xlsx") as pivot:
    #     # 列出所有透视表
    #     all_pivots = pivot.list_all_pivots()
    #     
    #     # 更新透视表数据源
    #     pivot.update_pivot_data_source(
    #         sheet_name="汇总",
    #         pivot_name="PivotTable1",
    #         new_data_range="数据源!A1:D1000"
    #     )
    #     
    #     # 标记需要刷新
    #     pivot.refresh_all_pivots()
    #     
    #     pivot.save("report_updated.xlsx")
    
    print("✓ 透视表操作功能就绪")
    print("  API: pivot.list_all_pivots(), pivot.update_pivot_data_source()")


def example_5_style_application():
    """示例5: 样式批量应用"""
    print("\n" + "="*60)
    print("示例5: 样式批量应用")
    print("="*60)
    
    # 创建样式应用器
    applier = StyleApplicator()
    
    # 创建常用样式
    header_fill = applier.create_fill('FFD9D9D9')  # 灰色背景
    header_font = applier.create_font(bold=True, size=11)
    header_align = applier.create_alignment()
    
    header_style = {
        'fill': header_fill,
        'font': header_font,
        'alignment': header_align
    }
    
    print("✓ 样式工具就绪")
    print("  预定义样式: create_fill(), create_font(), create_border(), create_alignment()")
    print("  批量应用: apply_row_style(), apply_column_style(), apply_range_style()")
    print("  快捷功能: apply_header_style(), apply_table_borders(), auto_fit_columns()")


def example_6_full_workflow():
    """示例6: 完整工作流"""
    print("\n" + "="*60)
    print("示例6: 完整数据填充工作流")
    print("="*60)
    
    print("完整流程:")
    print("1. 读取数据 -> ExcelIO.read_file()")
    print("2. 加载模板 -> FormulaProtector()")
    print("3. 写入数据（跳过公式列）-> protector.write_data()")
    print("4. 保存文件 -> protector.save()")
    print("5. 格式校验 -> FormatChecker.check_all_sheets()")
    print("6. 刷新透视表 -> PivotController.refresh_all_pivots()")
    print("✓ 完整工作流就绪")


def main():
    """运行所有示例"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           Excel Engine - 通用Excel智能处理引擎               ║
║                     快速使用指南 v1.0.0                       ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    example_1_read_write()
    example_2_formula_protection()
    example_3_format_check()
    example_4_pivot_control()
    example_5_style_application()
    example_6_full_workflow()
    
    print("\n" + "="*60)
    print("所有功能演示完成！")
    print("详细文档请查看: SKILL.md")
    print("依赖说明请查看: DEPENDENCIES.md")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
