#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表格识别与重建模块
功能：表格边框检测、单元格重建、表格结构还原、多格式输出
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml


class TableExtractor:
    """表格提取器"""

    def __init__(self, config_path: str = None):
        """
        初始化表格提取器

        Args:
            config_path: table-detection.yaml 配置文件路径
        """
        if config_path is None:
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / 'config' / 'table-detection.yaml'

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载配置"""
        if not self.config_path.exists():
            return {}

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    # =========================================================================
    # 简易表格检测（基于 OCR 文本）
    # =========================================================================

    def detect_table_lines(self, text: str) -> List[int]:
        """
        检测文本中的表格行

        Args:
            text: OCR 识别文本

        Returns:
            可能是表格的行号列表
        """
        lines = text.split('\n')
        table_line_indices = []

        for i, line in enumerate(lines):
            # 检测表格边框特征
            border_chars = ['─', '│', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼']
            border_count = sum(line.count(c) for c in border_chars)

            if border_count >= 3:
                table_line_indices.append(i)
                continue

            # 检测管道符表格 (| 列 | 列 |)
            pipe_count = line.count('|')
            if pipe_count >= 3 and line.strip().startswith('|') and line.strip().endswith('|'):
                table_line_indices.append(i)
                continue

            # 检测多个竖线分隔的内容
            if '  ' in line and line.count('  ') >= 2:
                # 可能是空格分隔的表格列
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 3 and all(len(p) > 0 for p in parts):
                    table_line_indices.append(i)

        return sorted(set(table_line_indices))

    def detect_table_regions(self, text: str) -> List[Tuple[int, int]]:
        """
        检测表格区域（连续的表格行）

        Args:
            text: OCR 识别文本

        Returns:
            表格区域列表 [(start_line, end_line), ...]
        """
        table_lines = self.detect_table_lines(text)
        if not table_lines:
            return []

        regions = []
        start = table_lines[0]
        prev = table_lines[0]

        for line_num in table_lines[1:]:
            if line_num - prev > 3:  # 允许最多 3 行的间隔
                regions.append((start, prev))
                start = line_num
            prev = line_num

        regions.append((start, prev))
        return regions

    # =========================================================================
    # 管道符表格解析（Markdown 风格）
    # =========================================================================

    def parse_pipe_table(self, text: str) -> Optional[Dict]:
        """
        解析管道符格式的表格

        Args:
            text: 包含管道符表格的文本

        Returns:
            表格结构字典，或 None（不是管道符表格）
        """
        lines = [l.rstrip() for l in text.split('\n')]
        pipe_lines = [i for i, l in enumerate(lines) if l.count('|') >= 2]

        if len(pipe_lines) < 2:
            return None

        # 检查是否是 Markdown 表格（有分隔线）
        has_separator = False
        separator_idx = -1
        for i in pipe_lines[1:]:
            line = lines[i]
            # 检测分隔线: |---|---| 或 |:---|---:|
            if re.match(r'^\s*\|?[\s:\-|]+\|?\s*$', line) and '---' in line:
                has_separator = True
                separator_idx = i
                break

        if not has_separator:
            return None

        # 提取表格行
        table_lines = []
        for i in range(pipe_lines[0], pipe_lines[-1] + 1):
            if lines[i].strip():
                table_lines.append(lines[i])

        if len(table_lines) < 2:
            return None

        # 解析每一行
        rows = []
        for line in table_lines:
            # 移除首尾的 | 并分割
            line = line.strip()
            if line.startswith('|'):
                line = line[1:]
            if line.endswith('|'):
                line = line[:-1]

            cells = [c.strip() for c in line.split('|')]
            rows.append(cells)

        # 确定列数
        col_count = max(len(row) for row in rows)

        # 补全行
        for row in rows:
            while len(row) < col_count:
                row.append('')

        # 识别表头
        is_separator_row = [False] * len(rows)
        for i, row in enumerate(rows):
            if all(re.match(r'^[\-:]+$', cell) for cell in row if cell):
                is_separator_row[i] = True

        header_rows = rows[:separator_idx - pipe_lines[0]] if separator_idx > 0 else []
        separator_row = rows[separator_idx - pipe_lines[0]] if separator_idx > 0 else None
        data_rows = rows[separator_idx - pipe_lines[0] + 1:] if separator_idx > 0 else rows

        # 解析对齐方式
        alignments = ['left'] * col_count
        if separator_row:
            for i, cell in enumerate(separator_row):
                if i >= col_count:
                    break
                if cell.startswith(':') and cell.endswith(':'):
                    alignments[i] = 'center'
                elif cell.endswith(':'):
                    alignments[i] = 'right'

        result = {
            'type': 'pipe_table',
            'col_count': col_count,
            'row_count': len(rows),
            'header_rows': header_rows,
            'data_rows': data_rows,
            'alignments': alignments,
            'all_rows': rows
        }

        return result

    # =========================================================================
    # 边框表格解析
    # =========================================================================

    def parse_border_table(self, text: str) -> Optional[Dict]:
        """
        解析带边框的表格

        Args:
            text: 包含表格边框的 OCR 文本

        Returns:
            表格结构字典，或 None
        """
        lines = text.split('\n')

        # 检测表格边框
        horizontal_chars = {'─', '═', '-'}
        vertical_chars = {'│', '║', '|'}
        corner_chars = {'┌', '┐', '└', '┘', '╔', '╗', '╚', '╝'}
        junction_chars = {'├', '┤', '┬', '┴', '┼'}

        has_border = False
        for line in lines:
            corner_count = sum(line.count(c) for c in corner_chars)
            horizontal_count = sum(line.count(c) for c in horizontal_chars)
            if corner_count >= 2 or horizontal_count >= 10:
                has_border = True
                break

        if not has_border:
            return None

        # 简化处理：将边框表格转换为文本内容提取
        # 实际完整实现需要图像处理，这里提供基础的文本提取

        # 移除纯边框行
        content_lines = []
        for line in lines:
            # 检查是否是纯边框行
            non_border_chars = [c for c in line if c not in horizontal_chars and c not in vertical_chars and c not in corner_chars and c not in junction_chars]
            if len([c for c in non_border_chars if not c.isspace()]) > 3:
                # 保留内容行，移除边框字符
                cleaned = line
                for c in horizontal_chars | vertical_chars | corner_chars | junction_chars:
                    cleaned = cleaned.replace(c, ' ')
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                if cleaned:
                    content_lines.append(cleaned)

        if not content_lines:
            return None

        result = {
            'type': 'border_table',
            'content_lines': content_lines,
            'note': '边框表格已提取文本内容，完整结构解析需要图像处理支持'
        }

        return result

    # =========================================================================
    # 空格分隔表格解析
    # =========================================================================

    def parse_space_table(self, text: str) -> Optional[Dict]:
        """
        解析空格分隔的表格（无框线）

        Args:
            text: OCR 识别的空格分隔表格文本

        Returns:
            表格结构字典，或 None
        """
        lines = [l.rstrip() for l in text.split('\n') if l.strip()]

        if len(lines) < 2:
            return None

        # 检测列分割位置（基于每行的空格位置一致性）
        split_positions = set()

        for line in lines:
            # 找到所有多个空格的位置
            for match in re.finditer(r'\s{2,}', line):
                split_positions.add(match.start())
                split_positions.add(match.end())

        if not split_positions:
            return None

        # 选择最一致的分割位置
        positions = sorted(split_positions)

        # 尝试分割
        rows = []
        for line in lines:
            parts = re.split(r'\s{2,}', line.strip())
            parts = [p.strip() for p in parts if p.strip()]
            if parts:
                rows.append(parts)

        if len(rows) < 2:
            return None

        # 检查列数一致性
        col_counts = [len(r) for r in rows]
        if max(col_counts) - min(col_counts) > 1:
            return None  # 列数差异太大，可能不是表格

        col_count = max(col_counts)

        # 补全行
        for row in rows:
            while len(row) < col_count:
                row.append('')

        result = {
            'type': 'space_table',
            'col_count': col_count,
            'row_count': len(rows),
            'rows': rows
        }

        return result

    # =========================================================================
    # 自动表格检测和解析
    # =========================================================================

    def extract_tables(self, text: str) -> List[Dict]:
        """
        从文本中提取所有表格

        Args:
            text: OCR 识别文本

        Returns:
            找到的所有表格列表
        """
        tables = []

        # 1. 尝试解析管道符表格
        pipe_table = self.parse_pipe_table(text)
        if pipe_table:
            tables.append(pipe_table)

        # 2. 尝试解析带边框表格
        border_table = self.parse_border_table(text)
        if border_table:
            tables.append(border_table)

        # 3. 尝试解析空格分隔表格
        space_table = self.parse_space_table(text)
        if space_table:
            tables.append(space_table)

        return tables

    # =========================================================================
    # 表格输出格式转换
    # =========================================================================

    def table_to_markdown(self, table: Dict) -> str:
        """
        将表格转换为 Markdown 格式

        Args:
            table: 表格结构字典

        Returns:
            Markdown 表格字符串
        """
        if not table:
            return ''

        table_type = table.get('type', '')

        if table_type == 'pipe_table':
            lines = []

            # 表头
            if table.get('header_rows'):
                for header_row in table['header_rows']:
                    lines.append('| ' + ' | '.join(header_row) + ' |')

            # 分隔线
            alignments = table.get('alignments', ['left'] * table['col_count'])
            sep_cells = []
            for align in alignments:
                if align == 'left':
                    sep_cells.append('---')
                elif align == 'center':
                    sep_cells.append(':---:')
                elif align == 'right':
                    sep_cells.append('---:')
            lines.append('| ' + ' | '.join(sep_cells) + ' |')

            # 数据行
            for data_row in table.get('data_rows', []):
                lines.append('| ' + ' | '.join(data_row) + ' |')

            return '\n'.join(lines)

        elif table_type == 'border_table':
            # 边框表格输出为内容行
            return '\n'.join(table.get('content_lines', []))

        elif table_type == 'space_table':
            rows = table.get('rows', [])
            if not rows:
                return ''

            # 计算每列最大宽度
            col_widths = [0] * table['col_count']
            for row in rows:
                for i, cell in enumerate(row):
                    if i < len(col_widths):
                        col_widths[i] = max(col_widths[i], len(cell))

            # 生成 Markdown
            lines = []
            for i, row in enumerate(rows):
                padded_cells = []
                for j, cell in enumerate(row):
                    if j < len(col_widths):
                        padded_cells.append(cell.ljust(col_widths[j]))
                lines.append('| ' + ' | '.join(padded_cells) + ' |')

                # 首行后加分隔线
                if i == 0:
                    sep_cells = ['-' * w for w in col_widths]
                    lines.append('| ' + ' | '.join(sep_cells) + ' |')

            return '\n'.join(lines)

        return ''

    def table_to_csv(self, table: Dict) -> str:
        """
        将表格转换为 CSV 格式

        Args:
            table: 表格结构字典

        Returns:
            CSV 字符串
        """
        if not table:
            return ''

        table_type = table.get('type', '')
        rows = []

        if table_type == 'pipe_table':
            rows.extend(table.get('header_rows', []))
            rows.extend(table.get('data_rows', []))
        elif table_type == 'space_table':
            rows = table.get('rows', [])
        elif table_type == 'border_table':
            # 边框表格每行作为单独的行
            for line in table.get('content_lines', []):
                rows.append([line])

        # 转换为 CSV
        csv_lines = []
        for row in rows:
            # 转义逗号和引号
            escaped_cells = []
            for cell in row:
                if ',' in cell or '"' in cell or '\n' in cell:
                    cell = '"' + cell.replace('"', '""') + '"'
                escaped_cells.append(cell)
            csv_lines.append(','.join(escaped_cells))

        return '\n'.join(csv_lines)

    def table_to_html(self, table: Dict) -> str:
        """
        将表格转换为 HTML 格式

        Args:
            table: 表格结构字典

        Returns:
            HTML 表格字符串
        """
        if not table:
            return ''

        table_type = table.get('type', '')
        html_lines = ['<table>']

        if table_type == 'pipe_table':
            # 表头
            if table.get('header_rows'):
                html_lines.append('  <thead>')
                for header_row in table['header_rows']:
                    html_lines.append('    <tr>')
                    for cell in header_row:
                        html_lines.append(f'      <th>{cell}</th>')
                    html_lines.append('    </tr>')
                html_lines.append('  </thead>')

            # 数据行
            html_lines.append('  <tbody>')
            for data_row in table.get('data_rows', []):
                html_lines.append('    <tr>')
                for cell in data_row:
                    html_lines.append(f'      <td>{cell}</td>')
                html_lines.append('    </tr>')
            html_lines.append('  </tbody>')

        elif table_type == 'space_table':
            rows = table.get('rows', [])
            if rows:
                html_lines.append('  <thead>')
                html_lines.append('    <tr>')
                for cell in rows[0]:
                    html_lines.append(f'      <th>{cell}</th>')
                html_lines.append('    </tr>')
                html_lines.append('  </thead>')

                html_lines.append('  <tbody>')
                for row in rows[1:]:
                    html_lines.append('    <tr>')
                    for cell in row:
                        html_lines.append(f'      <td>{cell}</td>')
                    html_lines.append('    </tr>')
                html_lines.append('  </tbody>')

        elif table_type == 'border_table':
            html_lines.append('  <tbody>')
            for line in table.get('content_lines', []):
                html_lines.append('    <tr>')
                html_lines.append(f'      <td>{line}</td>')
                html_lines.append('    </tr>')
            html_lines.append('  </tbody>')

        html_lines.append('</table>')
        return '\n'.join(html_lines)

    def table_to_json(self, table: Dict) -> Dict:
        """
        将表格转换为 JSON 格式（返回字典）

        Args:
            table: 表格结构字典

        Returns:
            标准化的 JSON 结构
        """
        if not table:
            return {}

        result = {
            'type': table.get('type', 'unknown'),
            'metadata': {
                'col_count': table.get('col_count', 0),
                'row_count': table.get('row_count', 0)
            }
        }

        table_type = table.get('type', '')

        if table_type == 'pipe_table':
            result['header'] = table.get('header_rows', [])
            result['data'] = table.get('data_rows', [])
            result['alignments'] = table.get('alignments', [])
        elif table_type == 'space_table':
            rows = table.get('rows', [])
            if rows:
                result['header'] = [rows[0]]
                result['data'] = rows[1:]
        elif table_type == 'border_table':
            result['content'] = table.get('content_lines', [])

        return result


# =============================================================================
# 命令行接口
# =============================================================================

def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description='表格识别与重建工具')
    parser.add_argument('--input', '-i', help='输入文本文件')
    parser.add_argument('--output', '-o', help='输出文件')
    parser.add_argument('--format', '-f', choices=['markdown', 'csv', 'html', 'json'],
                        default='markdown', help='输出格式')
    parser.add_argument('--test', action='store_true', help='运行测试')

    args = parser.parse_args()

    extractor = TableExtractor()

    if args.test:
        print("🧪 运行表格提取测试...\n")

        # 测试 1: Markdown 管道符表格
        print("📄 测试 1: Markdown 管道符表格")
        pipe_text = """
| 序号 | 项目 | 金额 | 备注 |
|------|------|------|------|
| 1 | 服务费 | 1000 | 基础服务 |
| 2 | 咨询费 | 2000 | 专家咨询 |
| 3 | 材料费 | 500 | 耗材 |
        """
        tables = extractor.extract_tables(pipe_text)
        if tables:
            print(f"✅ 找到 {len(tables)} 个表格")
            md = extractor.table_to_markdown(tables[0])
            print(f"Markdown 输出:\n{md}\n")
        else:
            print("❌ 未找到表格\n")

        # 测试 2: 空格分隔表格
        print("📄 测试 2: 空格分隔表格")
        space_text = """
序号   项目     金额    备注
1    服务费   1000   基础服务
2    咨询费   2000   专家咨询
3    材料费   500    耗材
        """
        tables = extractor.extract_tables(space_text)
        if tables:
            print(f"✅ 找到 {len(tables)} 个表格")
            md = extractor.table_to_markdown(tables[-1])  # 可能识别为 space_table
            print(f"Markdown 输出:\n{md}\n")
        else:
            print("❌ 未找到表格\n")

        print("✅ 测试完成!")
        return

    if args.input:
        text = Path(args.input).read_text(encoding='utf-8')
        tables = extractor.extract_tables(text)

        print(f"📄 找到 {len(tables)} 个表格\n")

        output_content = ""
        for i, table in enumerate(tables, 1):
            print(f"📊 表格 {i}: 类型={table['type']}, 列数={table.get('col_count', 'N/A')}")

            if args.format == 'markdown':
                result = extractor.table_to_markdown(table)
            elif args.format == 'csv':
                result = extractor.table_to_csv(table)
            elif args.format == 'html':
                result = extractor.table_to_html(table)
            elif args.format == 'json':
                result = json.dumps(extractor.table_to_json(table),
                                     ensure_ascii=False, indent=2)
            else:
                result = str(table)

            output_content += f"\n{'='*60}\n"
            output_content += f"表格 {i}\n"
            output_content += f"{'='*60}\n"
            output_content += result + "\n"

            if not args.output:
                print(f"\n{'-'*60}")
                print(result)
                print(f"{'-'*60}\n")

        if args.output:
            Path(args.output).write_text(output_content, encoding='utf-8')
            print(f"✅ 已保存到: {args.output}")


if __name__ == '__main__':
    main()
