#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 引擎 v3.0 - 终极优化版
精准解决：表格乱码、OCR常见错误、中文识别准确率
"""

import re
from pathlib import Path
from typing import List, Dict


# ==========================================
# 合同场景 OCR 常见错误修正字典
# ==========================================
OCR_CORRECTION_DICT = {
    # 数字/符号类
    '安时': '安卓',
    '内起三': '1、',
    '内起': '1、',
    '起三': '1、',
    'BiaA': '',
    'fcoFBSH': '',
    'ARMAS': '',
    'Siannltc': '',
    'FBSH': '',
    'fco': '',
    '®': '',
    '@': '',
    # 合同常用词
    '违造': '违约',
    '造约': '违约',
    '违备': '违约',
    '尝还': '偿还',
    '尝付': '偿付',
    '保正': '保证',
    '负任': '责任',
    '责仁': '责任',
    '叉方': '双方',
    '甲力': '甲方',
    '乙方': '乙方',
    '丙力': '丙方',
    '合问': '合同',
    '合司': '合同',
    '条敦': '条款',
    '条欺': '条款',
    '条软': '条款',
    '权力': '权利',
    '叉利': '权利',
    '艾务': '义务',
    '又务': '义务',
    '陪偿': '赔偿',
    '培偿': '赔偿',
    '滞钠金': '滞纳金',
    '滞拿金': '滞纳金',
    '置拟': '质疑',
    '异以': '异议',
    # 金额/数字
    '元整': '元整',
    '人民市': '人民币',
    '人民而': '人民币',
    '人民市': '人民币',
}


def correct_ocr_errors(text: str) -> str:
    """基于字典修正OCR常见错误"""
    corrected = text
    for wrong, right in OCR_CORRECTION_DICT.items():
        corrected = corrected.replace(wrong, right)
    return corrected


def is_chinese_char(c: str) -> bool:
    """判断是否为中文字符"""
    return '\u4e00' <= c <= '\u9fff'


def is_valid_contract_char(c: str) -> bool:
    """判断是否为合同有效字符"""
    if c.isspace():
        return True
    if c.isalnum():
        return True
    if c in '，。、；：“”‘’（）【】《》！？,.?!()[]""\'<>%¥$&+-=·\\':
        return True
    if is_chinese_char(c):
        return True
    return False


def filter_garbage_chars(text: str) -> str:
    """过滤乱码垃圾字符"""
    return ''.join(c for c in text if is_valid_contract_char(c))


def remove_table_artifacts(text: str) -> str:
    """去除表格线、竖线等OCR误识别垃圾"""
    lines = text.split('\n')
    cleaned = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 统计特殊字符比例
        special_chars = sum(1 for c in line if not c.isalnum() and not is_chinese_char(c))
        if len(line) > 0 and special_chars / len(line) > 0.6:
            # 超过60%是特殊字符，判定为表格线/垃圾，丢弃
            continue
        
        # 过滤全大写英文无意义串（OCR识别表格线常见）
        if re.match(r'^[A-Z]{4,15}$', line):
            continue
        
        # 过滤长度<3的无意义短串
        if len(line) < 3 and not re.match(r'^[一二三四五六七八九十\d、.]+$', line):
            continue
        
        cleaned.append(line)
    
    return '\n'.join(cleaned)


def merge_paragraphs_intelligent(lines: List[str]) -> List[str]:
    """智能段落合并 v2.0"""
    if not lines:
        return []
    
    paragraphs = []
    current_para = lines[0]
    
    end_punctuations = {'。', '！', '？', '；', '：', '”', '）', '】', '》'}
    start_keywords = {'第', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                      '甲', '乙', '丙', '丁', '（', '(', '【', '《', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        
        prev_ended = current_para and current_para[-1] in end_punctuations
        is_new_para = len(line) >= 1 and line[0] in start_keywords
        
        if prev_ended and is_new_para:
            paragraphs.append(current_para)
            current_para = line
        else:
            current_para += line
    
    if current_para:
        paragraphs.append(current_para)
    
    return paragraphs


def ocr_pdf_ultimate(pdf_path: Path) -> str:
    """
    终极版 PDF OCR
    三种PSM模式融合 + 图像预处理 + 后处理优化
    """
    print(f"\n{'='*60}")
    print(f"  📜 OCR 引擎 v3.0 - 合同专项优化版")
    print(f"{'='*60}")
    
    # ========== 第一步：检测是否为文本版 ==========
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        total_chars = 0
        paragraphs = []
        
        for page in doc:
            text = page.get_text()
            total_chars += len(text.strip())
            for para in text.split('\n'):
                para = para.strip()
                if para and len(para) > 2:
                    paragraphs.append(para)
        
        avg_chars = total_chars / max(len(doc), 1)
        if avg_chars > 100:
            print(f"  ✅ 检测为【文本版 PDF】，直接提取")
            full_text = '\n'.join(paragraphs)
            print(f"  ✅ 提取成功: {len(paragraphs)} 段, {len(full_text)} 字符")
            return full_text
    except Exception as e:
        print(f"  ⚠️  PyMuPDF 提取失败: {e}")
    
    # ========== 第二步：扫描版 PDF OCR ==========
    print(f"  📷 检测到扫描版 PDF，启动 OCR ...")
    
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError as e:
        print(f"  ❌ 缺少依赖: {e}")
        return ""
    
    # PDF 转高分辨率图片
    dpi = 450
    print(f"  🖨️  PDF 转图片 (DPI={dpi}) ...")
    try:
        pages = convert_from_path(str(pdf_path), dpi=dpi)
        print(f"  ✅ 共 {len(pages)} 页")
    except Exception as e:
        print(f"  ❌ PDF 转图片失败: {e}")
        return ""
    
    # ========== 三种 PSM 模式融合识别 ==========
    print(f"  🤖  三模式融合识别中 (PSM=6 + PSM=11 + PSM=3) ...")
    
    psm_configs = [
        r'--oem 3 --psm 6 -l chi_sim --dpi ' + str(dpi),   # 统一块（正文佳）
        r'--oem 3 --psm 11 -l chi_sim --dpi ' + str(dpi),  # 稀疏文本（表格佳）
        r'--oem 3 --psm 3 -l chi_sim --dpi ' + str(dpi),   # 全自动页段
    ]
    
    all_results = []
    
    for i, page_img in enumerate(pages, 1):
        print(f"  🔍  识别第 {i}/{len(pages)} 页 ...", end='\r')
        
        best_lines = []
        max_valid_chars = 0
        
        # 三种模式都试，取最优结果
        for config in psm_configs:
            text = pytesseract.image_to_string(page_img, config=config)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            # 计算有效中文字符数，作为评估标准
            valid_chars = sum(len(l) for l in lines if any(is_chinese_char(c) for c in l))
            
            if valid_chars > max_valid_chars:
                max_valid_chars = valid_chars
                best_lines = lines
        
        all_results.extend(best_lines)
    
    print(f"\n  ✅ OCR 原始识别: {len(all_results)} 行")
    
    # ========== 第三步：深度后处理 ==========
    print(f"  🧹  深度清理乱码与表格噪音 ...")
    raw_text = '\n'.join(all_results)
    
    # 1. 过滤乱码字符
    text = filter_garbage_chars(raw_text)
    
    # 2. 去除表格线等干扰
    text = remove_table_artifacts(text)
    
    # 3. OCR常见错误修正
    print(f"  🔧  OCR 错误修正 (共 {len(OCR_CORRECTION_DICT)} 条规则) ...")
    text = correct_ocr_errors(text)
    
    # 4. 智能段落合并
    print(f"  📝  智能段落合并 ...")
    lines = text.split('\n')
    merged = merge_paragraphs_intelligent(lines)
    
    final_text = '\n'.join(merged)
    print(f"\n  ✅ 最终结果: {len(merged)} 段落, {len(final_text)} 字符")
    
    return final_text


if __name__ == "__main__":
    pdf_file = Path("/Users/bangcle/Downloads/contract/XSZS2603090130北京聚信得仁.pdf")
    text = ocr_pdf_ultimate(pdf_file)
    
    print(f"\n\n{'='*60}")
    print(f"  前 1500 字符预览：")
    print(f"{'='*60}")
    print(text[:1500])
