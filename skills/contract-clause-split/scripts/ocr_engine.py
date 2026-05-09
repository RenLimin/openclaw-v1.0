#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 引擎模块(基于 Tesseract 5.x,业界标准方案)
支持扫描版 PDF 合同识别,中文+英文混合识别
"""

import os
import re
import tempfile
from pathlib import Path
from typing import List


def is_text_pdf(pdf_path: Path) -> bool:
    """
    快速检测PDF是否为文本版(可直接提取文字)
    返回 True=文本版,False=扫描版需要OCR
    """
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        total_chars = 0
        for page in doc:
            text = page.get_text()
            total_chars += len(text.strip())

        # 平均每页超过100字符,判定为文本版
        avg_chars = total_chars / max(len(doc), 1)
        return avg_chars > 100
    except Exception:
        return False


def extract_text_from_text_pdf(pdf_path: Path) -> str:
    """从文本版PDF提取文字"""
    import fitz
    doc = fitz.open(str(pdf_path))
    paragraphs = []

    for page in doc:
        text = page.get_text()
        if text:
            for para in text.split('\n'):
                para = para.strip()
                if para and len(para) > 2:
                    paragraphs.append(para)

    full_text = '\n'.join(paragraphs)
    print(f"  ✅ PyMuPDF 提取成功,共 {len(paragraphs)} 段,{len(full_text)} 字符")
    return full_text


def ocr_pdf_with_tesseract(pdf_path: Path, dpi: int = 300) -> str:
    """
    使用 Tesseract OCR 识别扫描版 PDF
    支持中文+英文混合识别,自动降噪
    """
    print(f"  📷 检测到扫描版 PDF,启动 Tesseract OCR ...")

    # 导入依赖
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError as e:
        print(f"  ❌ 缺少依赖: {e}")
        print(f"     请执行: pip install pdf2image pytesseract")
        return ""

    # PDF 转图片
    print(f"  🖨️  PDF 转图片中 (DPI={dpi}) ...")
    try:
        pages = convert_from_path(str(pdf_path), dpi=dpi)
        print(f"  ✅ 共 {len(pages)} 页")
    except Exception as e:
        print(f"  ❌ PDF 转图片失败: {e}")
        return ""

    # OCR 逐页识别
    print(f"  🤖  OCR 识别中 (chi_sim + eng) ...")
    all_lines = []
    custom_config = r'--oem 3 --psm 6 -l chi_sim+eng'  # 简体中文+英文

    for i, page_img in enumerate(pages, 1):
        print(f"  🔍  识别第 {i}/{len(pages)} 页 ...", end='\r')
        text = pytesseract.image_to_string(page_img, config=custom_config)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 2:
                all_lines.append(line)

    full_text = '\n'.join(all_lines)
    print(f"\n  ✅ OCR 完成,共 {len(all_lines)} 行,{len(full_text)} 字符")

    # 后处理:OCR 噪音清理
    full_text = clean_ocr_text(full_text)
    print(f"  ✅ 噪音清理完成,最终 {len(full_text)} 字符")

    return full_text


def clean_ocr_text(text: str) -> str:
    """清理OCR识别结果中的常见噪音"""
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # 去除纯数字(页码)
        if re.match(r'^\d+$', line) and len(line) <= 3:
            continue

        # 去除过短的垃圾行
        if len(line) < 3:
            continue

        # 去除特殊字符过多的行
        normal_chars = sum(1 for c in line if c.isalnum() or c in '，。、；：（）【】《》,.?!')
        if normal_chars < len(line) * 0.3:
            continue

        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def extract_pdf_text(pdf_path: Path) -> str:
    """
    智能PDF文本提取入口
    自动检测:文本版 → 直接提取;扫描版 → OCR识别
    """
    print(f"\n{'='*60}")
    print(f"  📂 解析 PDF: {pdf_path.name}")
    print(f"{'='*60}")

    # 第一步:检测是否为文本版
    if is_text_pdf(pdf_path):
        print(f"  ✅ 检测为【文本版 PDF】,直接提取")
        return extract_text_from_text_pdf(pdf_path)
    else:
        print(f"  ⚠️ 检测为【扫描版 PDF】,启动 OCR")
        return ocr_pdf_with_tesseract(pdf_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pdf_file = Path(sys.argv[1])
        text = extract_pdf_text(pdf_file)
        print(f"\n前 800 字符预览:\n{text[:800]}")
    else:
        print("用法: python ocr_engine.py <pdf_file>")
