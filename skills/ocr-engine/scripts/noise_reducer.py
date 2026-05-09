#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 噪音清理模块
功能：公章干扰清理、表格乱码清理、通用垃圾字符清理、自动纠错
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class NoiseReducer:
    """OCR 噪音清理器"""

    def __init__(self, config_path: str = None):
        """
        初始化噪音清理器

        Args:
            config_path: correction-dict.yaml 配置文件路径
        """
        if config_path is None:
            # 默认路径
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / 'config' / 'correction-dict.yaml'

        self.config_path = Path(config_path)
        self.corrections = self._load_corrections()
        self.stats = {
            'seal_removed': 0,
            'table_garbage_removed': 0,
            'corrections_applied': 0,
            'garbage_lines_removed': 0
        }

    def _load_corrections(self) -> Dict:
        """加载纠错字典配置"""
        if not self.config_path.exists():
            print(f"⚠️ 配置文件不存在: {self.config_path}，使用空配置")
            return {}

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config

    def reset_stats(self):
        """重置统计数据"""
        self.stats = {
            'seal_removed': 0,
            'table_garbage_removed': 0,
            'corrections_applied': 0,
            'garbage_lines_removed': 0
        }

    def get_stats(self) -> Dict:
        """获取统计数据"""
        return self.stats.copy()

    # =========================================================================
    # 单项清理功能
    # =========================================================================

    def remove_seal_interference(self, text: str) -> str:
        """
        清理公章干扰

        Args:
            text: 原始 OCR 文本

        Returns:
            清理后的文本
        """
        seal_patterns = self.corrections.get('seal_interference_corrections', {})
        cleaned = text

        for pattern, replacement in seal_patterns.items():
            if pattern in cleaned:
                count = cleaned.count(pattern)
                cleaned = cleaned.replace(pattern, replacement)
                self.stats['seal_removed'] += count

        return cleaned

    def remove_table_garbage(self, text: str) -> str:
        """
        清理表格边框和乱码

        Args:
            text: 原始 OCR 文本

        Returns:
            清理后的文本
        """
        table_patterns = self.corrections.get('table_garbage_strings', {})
        garbage_patterns = self.corrections.get('garbage_strings', {})

        # 合并表格垃圾和通用垃圾
        all_garbage = {**table_patterns, **garbage_patterns}

        cleaned = text
        for garbage, replacement in all_garbage.items():
            if garbage in cleaned:
                count = cleaned.count(garbage)
                cleaned = cleaned.replace(garbage, replacement)
                self.stats['table_garbage_removed'] += count

        return cleaned

    def remove_page_break_markers(self, text: str) -> str:
        """
        清理跨页标记

        Args:
            text: 原始 OCR 文本

        Returns:
            清理后的文本
        """
        markers = self.corrections.get('page_break_markers', {})
        cleaned = text

        for marker, replacement in markers.items():
            cleaned = cleaned.replace(marker, replacement)

        return cleaned

    def apply_corrections(self, text: str) -> str:
        """
        应用纠错字典

        Args:
            text: 原始 OCR 文本

        Returns:
            纠错后的文本
        """
        # 按优先级顺序应用各类修正
        correction_order = [
            'bracket_corrections',
            'amount_corrections',
            'number_corrections',
            'character_corrections'
        ]

        cleaned = text
        for category in correction_order:
            corrections = self.corrections.get(category, {})
            for wrong, correct in corrections.items():
                if wrong in cleaned:
                    count = cleaned.count(wrong)
                    cleaned = cleaned.replace(wrong, correct)
                    self.stats['corrections_applied'] += count

        return cleaned

    def remove_short_garbage_lines(self, text: str, min_length: int = 3) -> str:
        """
        移除过短的垃圾行

        Args:
            text: 原始文本
            min_length: 最小行长度

        Returns:
            清理后的文本
        """
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if len(stripped) >= min_length:
                cleaned_lines.append(line)
            elif stripped:
                self.stats['garbage_lines_removed'] += 1

        return '\n'.join(cleaned_lines)

    def remove_pure_number_lines(self, text: str) -> str:
        """
        移除纯数字行（通常是页码）

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            # 检查是否是纯数字（允许少量特殊字符）
            if re.match(r'^[\d\s\-\.·]+$', stripped) and len(stripped) <= 10:
                self.stats['garbage_lines_removed'] += 1
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def remove_repeated_noise_chars(self, text: str) -> str:
        """
        清理重复字符噪音（aaaaa、|||||、::::::等OCR识别垃圾）

        Args:
            text: 原始 OCR 文本

        Returns:
            清理后的文本
        """
        # 连续4个以上相同小写字母（非单词的垃圾串）
        cleaned = re.sub(r'\b[a-z]{4,}\b', '', text)
        # 连续4个以上相同的特殊符号
        cleaned = re.sub(r'[|]{4,}', ' ', cleaned)
        cleaned = re.sub(r'[:]{4,}', ' ', cleaned)
        cleaned = re.sub(r'[=]{4,}', ' ', cleaned)
        cleaned = re.sub(r'[-]{5,}', ' ', cleaned)
        cleaned = re.sub(r'[.]{5,}', ' ', cleaned)
        cleaned = re.sub(r'[x]{4,}', ' ', cleaned)
        
        return cleaned

    def merge_broken_lines(self, text: str) -> str:
        """
        合并OCR识别产生的断行句子
        处理：单行被拆分成多行的情况，例如：
            甲方应在验
            收合格后10日
            内支付合同总
        → 合并为完整句子

        特殊处理：条款标题（第一条/第二条）和正文的边界识别

        Args:
            text: 原始OCR文本

        Returns:
            合并断行后的文本
        """
        lines = text.split('\n')
        merged_lines = []
        current_sentence = ""
        
        # 条款标题模式
        article_title_pattern = r'^[第零一二三四五六七八九十0-9]+[条款项][ 　]*[\w\u4e00-\u9fa5]{0,15}$'
        # 行尾标点（句子结束标志）
        line_end_pattern = r'[。；：？！、""''）】》]$'
        # 行首序号（新句子标志）
        sentence_start_pattern = r'^[第零一二三四五六七八九十0-9]+[条条款项.、]|^\d+\.'
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_sentence:
                    merged_lines.append(current_sentence)
                    current_sentence = ""
                continue
            
            # 单独一行的条款标题：单独保留，不与后面合并
            if re.match(article_title_pattern, line) and len(line) < 30:
                if current_sentence:
                    merged_lines.append(current_sentence)
                merged_lines.append(line)
                current_sentence = ""
                continue
            
            # 判断是否应该合并
            should_merge = False
            if current_sentence:
                # 当前行不是句子结尾，且下一行不是新条款开头 → 合并
                if not re.search(line_end_pattern, current_sentence[-3:] if len(current_sentence) > 3 else current_sentence):
                    if not re.match(sentence_start_pattern, line):
                        should_merge = True
            
            if should_merge:
                current_sentence = current_sentence.rstrip() + line
            else:
                if current_sentence:
                    merged_lines.append(current_sentence)
                current_sentence = line
        
        if current_sentence:
            merged_lines.append(current_sentence)
        
        return '\n'.join(merged_lines)

    def normalize_whitespace(self, text: str) -> str:
        """
        规范化空白字符

        Args:
            text: 原始文本

        Returns:
            规范化后的文本
        """
        # 先合并断行句子（OCR拆行问题）
        text = self.merge_broken_lines(text)
        
        # 将多个空格替换为单个空格
        text = re.sub(r' +', ' ', text)
        # 将多个换行替换为单个换行
        text = re.sub(r'\n\s*\n', '\n', text)
        # 移除行首尾空格
        lines = [line.strip() for line in text.split('\n')]
        # 移除空行
        lines = [line for line in lines if line]

        return '\n'.join(lines)

    # =========================================================================
    # 组合清理流程
    # =========================================================================

    def basic_clean(self, text: str) -> str:
        """
        基础清理流程（快速）

        Args:
            text: 原始 OCR 文本

        Returns:
            清理后的文本
        """
        cleaned = text
        cleaned = self.remove_page_break_markers(cleaned)
        cleaned = self.remove_table_garbage(cleaned)
        cleaned = self.normalize_whitespace(cleaned)

        return cleaned

    def standard_clean(self, text: str) -> str:
        """
        标准清理流程（推荐）

        Args:
            text: 原始 OCR 文本

        Returns:
            清理后的文本
        """
        cleaned = text
        cleaned = self.remove_page_break_markers(cleaned)
        cleaned = self.remove_seal_interference(cleaned)
        cleaned = self.remove_table_garbage(cleaned)
        cleaned = self.remove_repeated_noise_chars(cleaned)  # 新增：重复字符清理
        cleaned = self.remove_short_garbage_lines(cleaned)
        cleaned = self.remove_pure_number_lines(cleaned)
        cleaned = self.apply_corrections(cleaned)
        cleaned = self.normalize_whitespace(cleaned)

        return cleaned

    def full_clean(self, text: str) -> str:
        """
        完整清理流程（最彻底）

        Args:
            text: 原始 OCR 文本

        Returns:
            清理后的文本
        """
        # 标准清理
        cleaned = self.standard_clean(text)

        # 额外：重复应用修正处理级联错误
        # （有些错误修正后会产生新的可修正错误）
        for _ in range(2):
            prev_length = len(cleaned)
            cleaned = self.apply_corrections(cleaned)
            if len(cleaned) == prev_length:
                break

        cleaned = self.normalize_whitespace(cleaned)

        return cleaned

    # =========================================================================
    # 扩展功能
    # =========================================================================

    def merge_extensions(self, extension_dict: Dict[str, str]) -> None:
        """
        合并业务扩展的纠错规则

        Args:
            extension_dict: 扩展的修正字典 {错误词: 正确词}
        """
        if 'character_corrections' not in self.corrections:
            self.corrections['character_corrections'] = {}

        self.corrections['character_corrections'].update(extension_dict)

    def merge_contract_extensions(self) -> None:
        """
        合并合同场景特定的纠错规则
        """
        contract_ext = self.corrections.get('contract_extensions', {})
        additional = contract_ext.get('additional_corrections', {})
        if additional:
            self.merge_extensions(additional)

    def detect_noise_level(self, text: str) -> Tuple[int, List[str]]:
        """
        检测文本中的噪音等级

        Args:
            text: 待检测文本

        Returns:
            (噪音等级 1-5, 发现的问题列表)
        """
        issues = []
        score = 0  # 分数越高噪音越大

        # 检测公章干扰
        seal_keywords = ['公章', '盖章', '签章', 'Android', 'AaB']
        seal_count = sum(text.count(k) for k in seal_keywords)
        if seal_count > 0:
            issues.append(f"检测到公章干扰 ({seal_count} 处)")
            score += min(seal_count, 3)

        # 检测表格边框垃圾
        border_chars = ['─', '│', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼']
        border_count = sum(text.count(c) for c in border_chars)
        if border_count > 10:
            issues.append(f"表格边框残留较多 ({border_count} 个字符)")
            score += min(border_count // 10, 2)

        # 检测垃圾字符串
        garbage_strings = ['fcoFBSH', 'FBSH', 'Siannltc', 'ARMAS', 'BiaA']
        garbage_count = sum(text.count(g) for g in garbage_strings)
        if garbage_count > 0:
            issues.append(f"检测到 OCR 垃圾串 ({garbage_count} 处)")
            score += garbage_count

        # 检测过短行数
        lines = text.split('\n')
        short_lines = sum(1 for l in lines if len(l.strip()) < 3)
        short_ratio = short_lines / max(len(lines), 1)
        if short_ratio > 0.3:
            issues.append(f"过短行比例较高 ({short_ratio:.1%})")
            score += 1

        # 转换为 1-5 等级
        noise_level = min(max(score // 2 + 1, 1), 5)

        return noise_level, issues


# =============================================================================
# 命令行接口
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='OCR 噪音清理工具')
    parser.add_argument('--input', '-i', help='输入文本文件')
    parser.add_argument('--output', '-o', help='输出文本文件')
    parser.add_argument('--mode', '-m', choices=['basic', 'standard', 'full'],
                        default='standard', help='清理模式')
    parser.add_argument('--test', action='store_true', help='运行测试')
    parser.add_argument('--detect', help='仅检测噪音等级')

    args = parser.parse_args()

    reducer = NoiseReducer()

    if args.test:
        print("🧪 运行噪音清理测试...\n")

        test_text = """
        接下页
        Android应用
        ┌───────────────┐
        │ 第 一 条  合司 │
        └───────────────┘
        甲方：XX 公同
        乙方：YY 公司
        1
        3  4
        人民市 10，000 元 整
        """

        print("原始文本:")
        print(test_text)
        print("\n" + "=" * 50)

        result = reducer.full_clean(test_text)

        print("清理后文本:")
        print(result)
        print("\n" + "=" * 50)

        stats = reducer.get_stats()
        print(f"统计数据:")
        print(f"  - 公章干扰移除: {stats['seal_removed']}")
        print(f"  - 表格垃圾移除: {stats['table_garbage_removed']}")
        print(f"  - 修正应用次数: {stats['corrections_applied']}")
        print(f"  - 垃圾行移除: {stats['garbage_lines_removed']}")

        print("\n✅ 测试完成!")
        return

    if args.detect:
        text = Path(args.detect).read_text(encoding='utf-8')
        level, issues = reducer.detect_noise_level(text)
        print(f"噪音等级: {level}/5")
        if issues:
            print("发现的问题:")
            for issue in issues:
                print(f"  - {issue}")
        return

    if args.input:
        input_path = Path(args.input)
        text = input_path.read_text(encoding='utf-8')

        print(f"📄 处理文件: {input_path}")

        if args.mode == 'basic':
            cleaned = reducer.basic_clean(text)
        elif args.mode == 'standard':
            cleaned = reducer.standard_clean(text)
        else:
            cleaned = reducer.full_clean(text)

        if args.output:
            Path(args.output).write_text(cleaned, encoding='utf-8')
            print(f"✅ 已保存到: {args.output}")
        else:
            print("\n" + "=" * 50)
            print(cleaned)
            print("=" * 50)

        stats = reducer.get_stats()
        print(f"\n📊 清理统计:")
        print(f"  公章干扰移除: {stats['seal_removed']}")
        print(f"  表格垃圾移除: {stats['table_garbage_removed']}")
        print(f"  修正应用次数: {stats['corrections_applied']}")
        print(f"  垃圾行移除: {stats['garbage_lines_removed']}")


if __name__ == '__main__':
    main()
