#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 引擎 v2.0 - 深度优化版
解决三大核心问题：表格错行、乱码、段落排版
"""

import os
import re
import tempfile
from pathlib import Path
from typing import List, Tuple


def is_chinese_char(c: str) -> bool:
    """判断是否为中文字符（用于乱码过滤）"""
    return '\u4e00' <= c <= '\u9fff'


def is_valid_text_char(c: str) -> bool:
    """判断是否为有效文本字符（过滤乱码）"""
    if c.isspace():
        return True
    if c.isalnum():
        return True
    if c in '，。、；：“”‘’（）【】《》！？,.?!()[]""\'':
        return True
    if is_chinese_char(c):
        return True
    return False


def clean_ocr_noise(text: str) -> str:
    """深度清理OCR噪音和乱码"""
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 统计有效字符比例
        if len(line) > 0:
            valid_chars = sum(1 for c in line if is_valid_text_char(c))
            valid_ratio = valid_chars / len(line)
            
            # 有效字符低于50%，判定为乱码行，丢弃
            if valid_ratio < 0.5:
                continue
            
            # 清理单字符垃圾行
            if len(line) == 1 and line not in '0123456789一二三四五六七八九十':
                continue
            
            # 清理纯符号行
            if all(not c.isalnum() and not is_chinese_char(c) for c in line):
                continue
            
            # OCR常见错误修正
            line = line.replace(' ', '')  # 先去除所有空格
            line = line.replace('，，', '，')
            line = line.replace('。。', '。')
            line = line.replace('，。', '。')
            
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def merge_paragraphs_smart(lines: List[str]) -> List[str]:
    """智能段落合并：解决段落排版差问题
    依据：标点结尾判断、行首缩进、关键词判断
    """
    if not lines:
        return []
    
    paragraphs = []
    current_para = lines[0]
    
    # 段落结束标点
    end_punctuations = {'。', '！', '？', '；', '：', '”', '）', '】', '》'}
    # 段落开头关键词
    start_keywords = {'第', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
                      '甲', '乙', '丙', '丁', '（', '(', '【', '《', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        
        # 判断上一行是否为段落结尾
        prev_ended = False
        if current_para and current_para[-1] in end_punctuations:
            prev_ended = True
        
        # 判断当前行是否为新段落开始
        is_new_para = False
        if len(line) >= 1 and line[0] in start_keywords:
            is_new_para = True
        
        # 上一行结束 AND 当前行是新段落开始 → 分段
        if prev_ended and is_new_para:
            paragraphs.append(current_para)
            current_para = line
        else:
            # 否则合并
            current_para += line
    
    # 加入最后一段
    if current_para:
        paragraphs.append(current_para)
    
    return paragraphs


def extract_pdf_text_optimized(pdf_path: Path, dpi: int = 400) -> str:
    """
    优化版PDF OCR提取
    解决：表格错行、乱码、段落排版
    """
    print(f"\n{'='*60}")
    print(f"  📂 优化版 PDF OCR 解析: {pdf_path.name}")
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
    
    # ========== 第二步：扫描版 PDF OCR（深度优化版） ==========
    print(f"  📷 检测到扫描版 PDF，启动优化版 OCR ...")
    
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError as e:
        print(f"  ❌ 缺少依赖: {e}")
        return ""
    
    # PDF 转高分辨率图片（提升表格识别精度）
    print(f"  🖨️  PDF 转高分辨率图片 (DPI={dpi}) ...")
    try:
        pages = convert_from_path(str(pdf_path), dpi=dpi)
        print(f"  ✅ 共 {len(pages)} 页")
    except Exception as e:
        print(f"  ❌ PDF 转图片失败: {e}")
        return ""
    
    # ========== OCR 参数优化（表格识别核心改进） ==========
    # PSM=11: 稀疏文本模式（适合表格）
    # PSM=6: 统一块（适合正文）
    # 双模式识别，取最优
    print(f"  🤖  Tesseract OCR 识别中（双模式：正文+表格优化）...")
    
    all_lines = []
    
    for i, page_img in enumerate(pages, 1):
        print(f"  🔍  识别第 {i}/{len(pages)} 页 ...", end='\r')
        
        # ========== 模式1：正文模式（PSM=6） ==========
        config_normal = r'--oem 3 --psm 6 -l chi_sim+eng --dpi ' + str(dpi)
        text_normal = pytesseract.image_to_string(page_img, config=config_normal)
        
        # ========== 模式2：稀疏文本模式（PSM=11，适合表格） ==========
        config_sparse = r'--oem 3 --psm 11 -l chi_sim+eng --dpi ' + str(dpi)
        text_sparse = pytesseract.image_to_string(page_img, config=config_sparse)
        
        # ========== 合并两种模式结果，取最优 ==========
        # 策略：字数多的模式优先（通常识别更完整）
        lines_normal = [l.strip() for l in text_normal.split('\n') if l.strip()]
        lines_sparse = [l.strip() for l in text_sparse.split('\n') if l.strip()]
        
        if len(lines_normal) >= len(lines_sparse):
            page_lines = lines_normal
        else:
            page_lines = lines_sparse
        
        all_lines.extend(page_lines)
    
    print(f"\n  ✅ OCR 原始识别: {len(all_lines)} 行")
    
    # ========== 第三步：深度清理乱码 ==========
    print(f"  🧹  清理 OCR 噪音与乱码 ...")
    raw_text = '\n'.join(all_lines)
    cleaned_text = clean_ocr_noise(raw_text)
    print(f"  ✅ 清理完成: {len(cleaned_text.splitlines())} 行有效")
    
    # ========== 第四步：智能段落合并（解决排版问题） ==========
    print(f"  📝  智能段落合并中 ...")
    lines = cleaned_text.split('\n')
    merged_paras = merge_paragraphs_smart(lines)
    print(f"  ✅ 合并完成: {len(merged_paras)} 个段落")
    
    final_text = '\n'.join(merged_paras)
    print(f"\n  📊 最终结果: {len(merged_paras)} 段落, {len(final_text)} 字符")
    
    return final_text


if __name__ == "__main__":
    pdf_file = Path("/Users/bangcle/Downloads/contract/XSZS2603090130北京聚信得仁.pdf")
    text = extract_pdf_text_optimized(pdf_file)
    print(f"\n\n{'='*60}")
    print(f"  前 1000 字符预览：")
    print(f"{'='*60}")
    print(text[:1000])
