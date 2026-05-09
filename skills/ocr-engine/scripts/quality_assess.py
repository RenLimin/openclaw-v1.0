#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 质量评估模块
功能：中文识别率估算、噪音等级评估、表格完整性检测、综合质量评分
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import yaml


class QualityAssessor:
    """OCR 质量评估器"""

    def __init__(self, config_path: str = None):
        """
        初始化质量评估器

        Args:
            config_path: engine-config.yaml 配置文件路径
        """
        if config_path is None:
            script_dir = Path(__file__).parent
            config_path = script_dir.parent / 'config' / 'engine-config.yaml'

        self.config_path = Path(config_path)
        self.config = self._load_config()

        # 常见中文字符集（用于检测）
        self.chinese_chars = set()
        self._init_charset()

    def _load_config(self) -> Dict:
        """加载配置"""
        if not self.config_path.exists():
            return {}

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _init_charset(self):
        """初始化常见中文字符集"""
        # 常用汉字 Unicode 范围
        common_chars = list(range(0x4e00, 0x9fff + 1))

        # 常见标点
        common_punct = [
            0x3002, 0xff0c, 0x3001, 0xff1b, 0xff1a,  # 。，、；：
            0xff01, 0xff1f, 0x300c, 0x300d, 0x300e,  # ！？「」『』
            0x300f, 0x2018, 0x2019, 0x201c, 0x201d,  #
            0xff08, 0xff09, 0x3014, 0x3015, 0x3010,  # （）〔〕【】
            0x3011, 0x2014, 0x2026, 0x2013, 0xff0e,  # ——……－．
            0xff05, 0x00b0, 0x2032, 0x2033, 0xffe5,  # ％°℃′″￥
        ]

        # 数字和字母
        numbers = list(range(0x30, 0x39 + 1))  # 0-9
        letters_lower = list(range(0x61, 0x7a + 1))  # a-z
        letters_upper = list(range(0x41, 0x5a + 1))  # A-Z

        all_codes = (common_chars + common_punct + numbers +
                     letters_lower + letters_upper)

        self.chinese_chars = set(chr(c) for c in all_codes)

    # =========================================================================
    # 单项评估功能
    # =========================================================================

    def estimate_chinese_recognition_rate(self, text: str) -> Tuple[float, Dict]:
        """
        估算中文识别率

        原理：统计文本中合法字符比例，异常字符（乱码、罕见符号）比例越高，识别率越低

        Args:
            text: OCR 识别文本

        Returns:
            (识别率估算值 0-1, 详细信息)
        """
        if not text:
            return 0.0, {'error': '空文本'}

        total_chars = len(text)
        valid_chars = 0
        garbage_chars = 0
        chinese_chars = 0
        unknown_chars = 0

        # OCR 常见垃圾字符
        garbage_patterns = [
            r'[─│┌┐└┘├┤┬┴┼╔╗╚╝═║]',  # 表格边框
            r'[■□▪▫●○◆◇★☆]',  # 符号
            r'[@®©™]',  # 特殊符号
        ]

        for char in text:
            # 跳过空白字符
            if char.isspace():
                continue

            # 检查是否是垃圾字符
            is_garbage = False
            for pattern in garbage_patterns:
                if re.match(pattern, char):
                    garbage_chars += 1
                    is_garbage = True
                    break

            if is_garbage:
                continue

            # 检查是否是合法字符
            if char in self.chinese_chars or char.isprintable():
                valid_chars += 1
                if '\u4e00' <= char <= '\u9fff':
                    chinese_chars += 1
            else:
                unknown_chars += 1

        # 计算识别率
        non_space_chars = sum(1 for c in text if not c.isspace())
        if non_space_chars == 0:
            return 0.0, {'error': '无有效字符'}

        valid_ratio = valid_chars / non_space_chars
        garbage_ratio = garbage_chars / non_space_chars

        # 识别率估算
        recognition_rate = valid_ratio * (1 - garbage_ratio * 0.5)
        recognition_rate = max(0.0, min(1.0, recognition_rate))

        details = {
            'total_chars': total_chars,
            'non_space_chars': non_space_chars,
            'valid_chars': valid_chars,
            'chinese_chars': chinese_chars,
            'garbage_chars': garbage_chars,
            'unknown_chars': unknown_chars,
            'valid_ratio': valid_ratio,
            'garbage_ratio': garbage_ratio
        }

        return recognition_rate, details

    def assess_noise_level(self, text: str) -> Tuple[int, Dict]:
        """
        评估噪音等级

        Args:
            text: OCR 识别文本

        Returns:
            (噪音等级 1-5, 详细信息)
        """
        if not text:
            return 5, {'error': '空文本'}

        score = 0
        issues = []

        # 1. 检测公章干扰
        seal_keywords = ['公章', '盖章', '签章', '签名', '签字', 'Android', 'AaB', 'BaA']
        seal_count = sum(text.count(k) for k in seal_keywords)
        if seal_count > 0:
            issues.append(f'公章干扰 ({seal_count} 处)')
            score += min(seal_count, 3)

        # 2. 检测表格边框垃圾
        border_chars = ['─', '│', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼',
                        '╔', '╗', '╚', '╝', '═', '║']
        border_count = sum(text.count(c) for c in border_chars)
        if border_count > 20:
            issues.append(f'表格边框残留较多 ({border_count} 个字符)')
            score += min(border_count // 20, 2)

        # 3. 检测 OCR 垃圾串
        garbage_strings = ['fcoFBSH', 'FBSH', 'Siannltc', 'ARMAS', 'BiaA']
        garbage_count = sum(text.count(g) for g in garbage_strings)
        if garbage_count > 0:
            issues.append(f'OCR 垃圾串 ({garbage_count} 处)')
            score += min(garbage_count, 2)

        # 4. 检测过短行比例
        lines = text.split('\n')
        short_lines = sum(1 for l in lines if len(l.strip()) < 3)
        short_ratio = short_lines / max(len(lines), 1)
        if short_ratio > 0.4:
            issues.append(f'过短行比例高 ({short_ratio:.1%})')
            score += 1

        # 5. 检测空行比例
        empty_lines = sum(1 for l in lines if not l.strip())
        empty_ratio = empty_lines / max(len(lines), 1)
        if empty_ratio > 0.5:
            issues.append(f'空行比例高 ({empty_ratio:.1%})')
            score += 1

        # 转换为 1-5 等级
        noise_level = min(max(score // 2 + 1, 1), 5)

        details = {
            'noise_level': noise_level,
            'score': score,
            'issues': issues,
            'seal_count': seal_count,
            'border_count': border_count,
            'garbage_count': garbage_count,
            'short_line_ratio': short_ratio,
            'empty_line_ratio': empty_ratio
        }

        return noise_level, details

    def assess_line_coherence(self, text: str) -> Tuple[float, Dict]:
        """
        评估行连贯性

        原理：连续行之间的语义连贯性、长度一致性

        Args:
            text: OCR 识别文本

        Returns:
            (连贯性评分 0-1, 详细信息)
        """
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        if len(lines) < 3:
            return 1.0, {'note': '行数过少，无法评估'}

        # 长度一致性
        lengths = [len(l) for l in lines]
        avg_length = sum(lengths) / len(lengths)
        length_variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        length_std = length_variance ** 0.5
        length_consistency = max(0, 1 - length_std / max(avg_length, 1))

        # 行开头模式一致性（序号、标点等）
        start_patterns = []
        for line in lines:
            if re.match(r'^[\d第一二三四五六七八九十]+[、.．]', line):
                start_patterns.append('number')
            elif line[0] in '（([{【':
                start_patterns.append('bracket')
            else:
                start_patterns.append('normal')

        pattern_consistency = 0.0
        if start_patterns:
            most_common = max(set(start_patterns), key=start_patterns.count)
            pattern_count = start_patterns.count(most_common)
            pattern_consistency = pattern_count / len(start_patterns)

        # 综合连贯性
        coherence = length_consistency * 0.6 + pattern_consistency * 0.4

        details = {
            'line_count': len(lines),
            'avg_length': avg_length,
            'length_std': length_std,
            'length_consistency': length_consistency,
            'pattern_consistency': pattern_consistency,
            'overall_coherence': coherence
        }

        return coherence, details

    def assess_table_integrity(self, text: str) -> Tuple[float, Dict]:
        """
        评估表格完整性

        Args:
            text: OCR 识别文本

        Returns:
            (完整性评分 0-1, 详细信息)
        """
        # 检测表格特征
        has_border = any(c in text for c in ['─', '│', '┌', '┐', '└', '┘'])
        has_pipe_table = '|' in text and text.count('|') > 4

        if not has_border and not has_pipe_table:
            return 1.0, {'note': '未检测到表格'}

        # 简单评分机制
        issues = []
        score = 100

        # 检测边框残缺
        border_chars = ['─', '│', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼']
        border_counts = {c: text.count(c) for c in border_chars}

        horizontal = border_counts['─']
        vertical = border_counts['│']

        if horizontal == 0 and vertical > 0:
            issues.append('缺少水平边框')
            score -= 30
        elif vertical == 0 and horizontal > 0:
            issues.append('缺少垂直边框')
            score -= 30

        # 检测边角
        corners = sum(border_counts[c] for c in ['┌', '┐', '└', '┘'])
        if corners < 4 and corners > 0:
            issues.append(f'边角不完整 (检测到 {corners}/4)')
            score -= 20

        integrity = max(0, score / 100)

        details = {
            'has_table': True,
            'border_type': 'line_border' if has_border else 'pipe_table',
            'horizontal_lines': horizontal,
            'vertical_lines': vertical,
            'corners': corners,
            'issues': issues
        }

        return integrity, details

    def assess_garbage_ratio(self, text: str) -> Tuple[float, Dict]:
        """
        评估垃圾字符比例

        Args:
            text: OCR 识别文本

        Returns:
            (垃圾比例 0-1, 详细信息)
        """
        if not text:
            return 1.0, {'error': '空文本'}

        # 垃圾字符模式
        garbage_patterns = [
            r'[─│┌┐└┘├┤┬┴┼╔╗╚╝═║]',  # 表格边框
            r'[■□▪▫●○◆◇★☆]',  # 形状符号
            r'[@®©™]',  # 特殊符号
        ]

        garbage_chars = 0
        for char in text:
            if char.isspace():
                continue
            for pattern in garbage_patterns:
                if re.match(pattern, char):
                    garbage_chars += 1
                    break

        non_space_chars = sum(1 for c in text if not c.isspace())
        garbage_ratio = garbage_chars / max(non_space_chars, 1)

        details = {
            'total_non_space': non_space_chars,
            'garbage_chars': garbage_chars,
            'garbage_ratio': garbage_ratio
        }

        return garbage_ratio, details

    # =========================================================================
    # 综合评估
    # =========================================================================

    def assess_full(self, text: str, detailed: bool = False) -> Dict:
        """
        完整质量评估

        Args:
            text: OCR 识别文本
            detailed: 是否返回详细信息

        Returns:
            完整评估结果字典
        """
        if not text or not text.strip():
            return {
                'overall_score': 0,
                'quality_level': 'unusable',
                'issues': ['空文本'],
                'summary': '无法评估：空文本'
            }

        # 各项评估
        chinese_rate, chinese_details = self.estimate_chinese_recognition_rate(text)
        noise_level, noise_details = self.assess_noise_level(text)
        coherence, coherence_details = self.assess_line_coherence(text)
        table_integrity, table_details = self.assess_table_integrity(text)
        garbage_ratio, garbage_details = self.assess_garbage_ratio(text)

        # 收集所有问题
        all_issues = []
        all_issues.extend(noise_details.get('issues', []))
        all_issues.extend(table_details.get('issues', []))

        # 计算综合评分 (0-100)
        weights = self.config.get('quality_assessment', {}).get('assessment_items', {
            'chinese_recognition_rate': True,
            'noise_level': True,
            'table_integrity': True,
            'line_coherence': True,
            'garbage_ratio': True
        })

        # 标准化各项为 0-100 分
        scores = {}
        if weights.get('chinese_recognition_rate', True):
            scores['chinese_recognition'] = chinese_rate * 100

        if weights.get('noise_level', True):
            # 噪音等级反向：等级 1 = 100 分，等级 5 = 0 分
            scores['noise_cleanliness'] = (5 - noise_level) / 4 * 100

        if weights.get('table_integrity', True):
            scores['table_integrity'] = table_integrity * 100

        if weights.get('line_coherence', True):
            scores['line_coherence'] = coherence * 100

        if weights.get('garbage_ratio', True):
            scores['cleanliness'] = (1 - garbage_ratio) * 100

        # 综合评分
        if scores:
            overall_score = sum(scores.values()) / len(scores)
        else:
            overall_score = 50  # 默认中等

        overall_score = round(overall_score, 1)

        # 质量等级
        thresholds = self.config.get('quality_assessment', {}).get('thresholds', {
            'excellent': 90,
            'good': 75,
            'fair': 60,
            'poor': 40
        })

        if overall_score >= thresholds.get('excellent', 90):
            quality_level = 'excellent'
        elif overall_score >= thresholds.get('good', 75):
            quality_level = 'good'
        elif overall_score >= thresholds.get('fair', 60):
            quality_level = 'fair'
        elif overall_score >= thresholds.get('poor', 40):
            quality_level = 'poor'
        else:
            quality_level = 'unusable'

        # 质量等级中文描述
        level_names = {
            'excellent': '优秀',
            'good': '良好',
            'fair': '一般',
            'poor': '较差',
            'unusable': '不可用'
        }

        result = {
            'overall_score': overall_score,
            'quality_level': quality_level,
            'quality_level_name': level_names.get(quality_level, '未知'),
            'chinese_recognition_rate': round(chinese_rate, 3),
            'noise_level': noise_level,
            'line_coherence': round(coherence, 3),
            'table_integrity': round(table_integrity, 3),
            'garbage_ratio': round(garbage_ratio, 3),
            'issues': all_issues,
            'summary': f"综合评分 {overall_score}/100，质量{level_names.get(quality_level, '未知')}"
        }

        if detailed:
            result['details'] = {
                'chinese_recognition': chinese_details,
                'noise': noise_details,
                'coherence': coherence_details,
                'table': table_details,
                'garbage': garbage_details,
                'component_scores': scores
            }

        return result

    def print_assessment(self, result: Dict):
        """打印评估结果"""
        print(f"\n{'=' * 50}")
        print(f"📊 OCR 质量评估结果")
        print(f"{'=' * 50}")
        print(f"  综合评分: {result['overall_score']}/100")
        print(f"  质量等级: {result['quality_level_name']} ({result['quality_level']})")
        print()
        print(f"  中文识别率: {result['chinese_recognition_rate']:.1%}")
        print(f"  噪音等级: {result['noise_level']}/5")
        print(f"  行连贯性: {result['line_coherence']:.1%}")
        print(f"  表格完整性: {result['table_integrity']:.1%}")
        print(f"  垃圾字符比例: {result['garbage_ratio']:.1%}")
        print()

        if result['issues']:
            print(f"  ⚠️ 发现的问题:")
            for issue in result['issues']:
                print(f"    - {issue}")
        else:
            print(f"  ✅ 未发现明显问题")

        print(f"{'=' * 50}")


# =============================================================================
# 命令行接口
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='OCR 质量评估工具')
    parser.add_argument('--input', '-i', help='输入文本文件')
    parser.add_argument('--text', '-t', help='直接输入文本')
    parser.add_argument('--detailed', '-d', action='store_true', help='显示详细信息')
    parser.add_argument('--test', action='store_true', help='运行测试')

    args = parser.parse_args()

    assessor = QualityAssessor()

    if args.test:
        print("🧪 运行质量评估测试...\n")

        # 测试文本 1: 高质量
        good_text = """
        第一条 为了规范公司管理，提高工作效率，特制定本规定。
        第二条 所有员工必须遵守公司规章制度。
        第三条 工作时间为上午 9:00 至下午 6:00。
        第四条 请假需提前申请，经主管批准后方可休假。
        第五条 本规定自发布之日起生效。
        """

        print("📄 测试 1: 高质量文本")
        result = assessor.assess_full(good_text)
        assessor.print_assessment(result)

        # 测试文本 2: 有噪音
        noisy_text = """
        ┌───────────────┐
        │Android应用第 一 条│
        └───────────────┘
        甲力：XX 公同
        乙力：YY 公司
        1
        人民市 10，000 元
        fcoFBSH
        """

        print("\n📄 测试 2: 含噪音文本")
        result = assessor.assess_full(noisy_text)
        assessor.print_assessment(result)

        print("\n✅ 测试完成!")
        return

    text = ""
    if args.input:
        text = Path(args.input).read_text(encoding='utf-8')
    elif args.text:
        text = args.text
    else:
        print("❌ 请指定 --input 或 --text 参数")
        return

    result = assessor.assess_full(text, detailed=args.detailed)
    assessor.print_assessment(result)

    if args.detailed and 'details' in result:
        print(f"\n📋 详细信息:")
        import json
        print(json.dumps(result['details'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
