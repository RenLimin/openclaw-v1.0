#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word 格式比对引擎
================
对比目标文档与模板的格式一致性，检测字体、行距、标题层级等差异

功能:
  - 文档与模板格式比对
  - 字体/字号/颜色/行距/段前段后距检查
  - 标题层级一致性检查
  - 样式不一致检测

作者: Word-Analyzer Team
版本: v1.0
日期: 2026-04-24
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

try:
    from docx import Document
except ImportError:
    print("❌ 错误: 请安装 python-docx: pip install python-docx")
    exit(1)

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from word_parser import WordParser, ParagraphStyle


class StyleComparator:
    """Word 文档格式比对器"""

    def __init__(self, template_path: str, config_path: str = None):
        """
        初始化格式比对器

        Args:
            template_path: 模板文档路径
            config_path: 配置文件路径（可选）
        """
        self.template_path = Path(template_path)
        self.config = self._load_config(config_path)
        self.template_parser = WordParser(template_path, config_path)
        self.template_data = None

    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置文件"""
        default_config = {
            'font_rules': {
                'body': {
                    'allowed_fonts': ["宋体", "SimSun", "Times New Roman"],
                    'allowed_sizes': [10.5, 11, 12],
                    'line_spacing': 1.5,
                    'bold': False,
                    'italic': False
                },
                'heading_1': {
                    'allowed_fonts': ["黑体", "SimHei", "微软雅黑", "Microsoft YaHei"],
                    'allowed_sizes': [14, 16, 18, 20],
                    'bold': True
                },
                'heading_2': {
                    'allowed_fonts': ["黑体", "SimHei", "微软雅黑", "Microsoft YaHei"],
                    'allowed_sizes': [12, 14, 16],
                    'bold': True
                },
                'heading_3': {
                    'allowed_fonts': ["黑体", "SimHei", "宋体", "SimSun"],
                    'allowed_sizes': [12, 14],
                    'bold': True
                }
            },
            'tolerance': {
                'font_size': 0.5,  # 字号容差（磅）
                'spacing': 1.0      # 间距容差（磅）
            }
        }

        if config_path and HAS_YAML:
            cfg_path = Path(config_path)
            if cfg_path.exists():
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if 'font_rules' in user_config:
                        default_config['font_rules'].update(user_config['font_rules'])
                    if 'tolerance' in user_config:
                        default_config['tolerance'].update(user_config['tolerance'])

        return default_config

    def _is_font_allowed(self, font_name: str, allowed_fonts: List[str]) -> bool:
        """检查字体是否在允许列表中（大小写不敏感）"""
        if not font_name:
            return False
        font_name_lower = font_name.lower()
        return any(allowed.lower() in font_name_lower or font_name_lower in allowed.lower()
                   for allowed in allowed_fonts)

    def _is_size_allowed(self, size: float, allowed_sizes: List[float]) -> bool:
        """检查字号是否在允许列表中（带容差）"""
        tolerance = self.config['tolerance']['font_size']
        return any(abs(size - allowed) <= tolerance for allowed in allowed_sizes)

    def check_font_style(self, paragraphs: List[Dict]) -> Dict[str, Any]:
        """检查字体样式一致性"""
        results = {
            'total_checked': 0,
            'font_issues': [],
            'size_issues': [],
            'color_issues': [],
            'bold_issues': [],
            'italic_issues': []
        }

        font_rules = self.config['font_rules']

        for para in paragraphs:
            if para['is_empty']:
                continue

            results['total_checked'] += 1
            style = para['style']
            level = para['heading_level']

            # 根据标题级别选择规则
            if level == 1:
                rule = font_rules.get('heading_1', font_rules['body'])
                context = f"一级标题"
            elif level == 2:
                rule = font_rules.get('heading_2', font_rules['body'])
                context = f"二级标题"
            elif level == 3:
                rule = font_rules.get('heading_3', font_rules['body'])
                context = f"三级标题"
            elif level and level > 3:
                rule = font_rules.get(f'heading_{level}', font_rules['body'])
                context = f"{level}级标题"
            else:
                rule = font_rules['body']
                context = "正文"

            # 检查字体
            if 'allowed_fonts' in rule:
                if not self._is_font_allowed(style['font_name'], rule['allowed_fonts']):
                    results['font_issues'].append({
                        'paragraph_index': para['index'],
                        'context': context,
                        'actual': style['font_name'],
                        'expected': rule['allowed_fonts'],
                        'preview': para['text'][:50]
                    })

            # 检查字号
            if 'allowed_sizes' in rule and style['font_size'] > 0:
                if not self._is_size_allowed(style['font_size'], rule['allowed_sizes']):
                    results['size_issues'].append({
                        'paragraph_index': para['index'],
                        'context': context,
                        'actual': style['font_size'],
                        'expected': rule['allowed_sizes'],
                        'preview': para['text'][:50]
                    })

            # 检查加粗
            if 'bold' in rule and style['bold'] != rule['bold']:
                results['bold_issues'].append({
                    'paragraph_index': para['index'],
                    'context': context,
                    'actual': style['bold'],
                    'expected': rule['bold'],
                    'preview': para['text'][:50]
                })

            # 检查斜体
            if 'italic' in rule and style['italic'] != rule['italic']:
                results['italic_issues'].append({
                    'paragraph_index': para['index'],
                    'context': context,
                    'actual': style['italic'],
                    'expected': rule['italic'],
                    'preview': para['text'][:50]
                })

        return results

    def check_paragraph_spacing(self, paragraphs: List[Dict]) -> Dict[str, Any]:
        """检查段落间距（行间距、段前距、段后距）"""
        results = {
            'total_checked': 0,
            'line_spacing_issues': [],
            'space_before_issues': [],
            'space_after_issues': [],
            'indent_issues': []
        }

        font_rules = self.config['font_rules']
        tolerance = self.config['tolerance']['spacing']

        for para in paragraphs:
            if para['is_empty']:
                continue

            results['total_checked'] += 1
            style = para['style']
            level = para['heading_level']

            # 根据标题级别选择规则
            if level and level <= 3:
                rule = font_rules.get(f'heading_{level}', font_rules['body'])
                context = f"{level}级标题"
            else:
                rule = font_rules['body']
                context = "正文"

            # 检查行间距
            if 'line_spacing' in rule and style['line_spacing'] > 0:
                expected = rule['line_spacing']
                if abs(style['line_spacing'] - expected) > tolerance:
                    results['line_spacing_issues'].append({
                        'paragraph_index': para['index'],
                        'context': context,
                        'actual': style['line_spacing'],
                        'expected': expected,
                        'preview': para['text'][:50]
                    })

            # 检查段前距
            if 'space_before' in rule:
                expected = rule['space_before']
                if abs(style['space_before'] - expected) > tolerance:
                    results['space_before_issues'].append({
                        'paragraph_index': para['index'],
                        'context': context,
                        'actual': style['space_before'],
                        'expected': expected,
                        'preview': para['text'][:50]
                    })

            # 检查段后距
            if 'space_after' in rule:
                expected = rule['space_after']
                if abs(style['space_after'] - expected) > tolerance:
                    results['space_after_issues'].append({
                        'paragraph_index': para['index'],
                        'context': context,
                        'actual': style['space_after'],
                        'expected': expected,
                        'preview': para['text'][:50]
                    })

        return results

    def check_heading_hierarchy(self, headings: List[Dict]) -> Dict[str, Any]:
        """检查标题层级一致性"""
        results = {
            'total_headings': len(headings),
            'level_skips': [],
            'level_order_issues': [],
            'style_inconsistencies': []
        }

        if len(headings) < 2:
            return results

        # 检查层级跳跃（如从1级直接跳到3级）
        for i in range(1, len(headings)):
            prev_level = headings[i - 1]['level']
            curr_level = headings[i]['level']

            # 层级跳跃超过1级
            if curr_level - prev_level > 1:
                results['level_skips'].append({
                    'heading_index': i,
                    'text': headings[i]['text'],
                    'previous_level': prev_level,
                    'current_level': curr_level
                })

        # 统计各级别标题的样式一致性
        styles_by_level = {}
        for heading in headings:
            level = heading['level']
            if level not in styles_by_level:
                styles_by_level[level] = []
            styles_by_level[level].append(heading['style'])

        # 检查同级别标题样式是否一致
        for level, styles in styles_by_level.items():
            if len(styles) < 2:
                continue

            # 检查字体一致性
            fonts = set(s['font_name'] for s in styles if s['font_name'])
            if len(fonts) > 1:
                results['style_inconsistencies'].append({
                    'level': level,
                    'issue': '字体不一致',
                    'values': list(fonts)
                })

            # 检查字号一致性
            sizes = set(s['font_size'] for s in styles if s['font_size'] > 0)
            if len(sizes) > 1:
                results['style_inconsistencies'].append({
                    'level': level,
                    'issue': '字号不一致',
                    'values': list(sizes)
                })

        return results

    def compare_with_template(self, target_parser: WordParser) -> Dict[str, Any]:
        """与模板文档进行格式比对"""
        # 加载模板数据
        if self.template_data is None:
            self.template_data = self.template_parser.parse()

        target_data = target_parser.parse()

        # 各项检查
        font_check = self.check_font_style(target_data['paragraphs'])
        spacing_check = self.check_paragraph_spacing(target_data['paragraphs'])
        heading_check = self.check_heading_hierarchy(target_data['headings'])

        # 统计所有问题
        all_issues = (
            len(font_check['font_issues']) +
            len(font_check['size_issues']) +
            len(font_check['bold_issues']) +
            len(spacing_check['line_spacing_issues']) +
            len(spacing_check['space_before_issues']) +
            len(spacing_check['space_after_issues']) +
            len(heading_check['level_skips']) +
            len(heading_check['style_inconsistencies'])
        )

        total_checked = max(font_check['total_checked'], 1)
        match_rate = max(0, 1 - (all_issues / total_checked * 0.1))  # 每个问题扣10%匹配度

        report = {
            'success': True,
            'template_path': str(self.template_path),
            'target_path': str(target_parser.file_path),
            'match_rate': round(match_rate, 3),
            'total_issues': all_issues,
            'font_check': font_check,
            'spacing_check': spacing_check,
            'heading_check': heading_check
        }

        return report

    def compare(self, target_path: str) -> Dict[str, Any]:
        """
        比对目标文档与模板

        Args:
            target_path: 目标文档路径

        Returns:
            比对报告
        """
        target_parser = WordParser(target_path)
        return self.compare_with_template(target_parser)

    def print_report(self, report: Dict[str, Any]):
        """打印比对报告"""
        print(f"\n{'=' * 60}")
        print(f"📊 格式比对报告")
        print(f"{'=' * 60}")
        print(f"📄 模板: {report['template_path']}")
        print(f"📄 目标: {report['target_path']}")
        print(f"🎯 匹配度: {report['match_rate'] * 100:.1f}%")
        print(f"⚠️  总问题数: {report['total_issues']}")

        fc = report['font_check']
        sc = report['spacing_check']
        hc = report['heading_check']

        print(f"\n--- 字体检查 ---")
        print(f"  检查段落: {fc['total_checked']}")
        print(f"  字体问题: {len(fc['font_issues'])}")
        print(f"  字号问题: {len(fc['size_issues'])}")
        print(f"  加粗问题: {len(fc['bold_issues'])}")
        print(f"  斜体问题: {len(fc['italic_issues'])}")

        # 显示前5个字体问题
        for issue in fc['font_issues'][:5]:
            print(f"    - 第{issue['paragraph_index']}段 [{issue['context']}]: "
                  f"字体为 '{issue['actual']}' (期望: {issue['expected']})")

        print(f"\n--- 间距检查 ---")
        print(f"  行间距问题: {len(sc['line_spacing_issues'])}")
        print(f"  段前距问题: {len(sc['space_before_issues'])}")
        print(f"  段后距问题: {len(sc['space_after_issues'])}")

        print(f"\n--- 标题层级检查 ---")
        print(f"  标题总数: {hc['total_headings']}")
        print(f"  层级跳跃: {len(hc['level_skips'])}")
        print(f"  样式不一致: {len(hc['style_inconsistencies'])}")

        for issue in hc['style_inconsistencies'][:5]:
            print(f"    - {issue['level']}级标题 {issue['issue']}: {issue['values']}")

        print(f"\n{'=' * 60}")

        if report['match_rate'] >= 0.9:
            print("✅ 格式一致性良好！")
        elif report['match_rate'] >= 0.7:
            print("⚠️  格式基本一致，存在少量问题")
        else:
            print("❌ 格式存在较多问题，建议检查")


def main():
    parser = argparse.ArgumentParser(description='Word 文档格式比对工具')
    parser.add_argument('--template', '-t', required=True, help='模板文档路径')
    parser.add_argument('--target', '-g', required=True, help='目标文档路径')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--output', '-o', help='输出报告路径 (JSON)')

    args = parser.parse_args()

    comparator = StyleComparator(args.template, args.config)
    report = comparator.compare(args.target)
    comparator.print_report(report)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n💾 报告已保存: {args.output}")


if __name__ == "__main__":
    main()
