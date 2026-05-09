#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF OCR 文字识别模块
处理扫描版 PDF
"""

import os
import sys
from pathlib import Path

# 颜色输出
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'

def ocr_pdf_with_easyocr(pdf_path: Path, temp_dir: Path = None) -> str:
    """使用 EasyOCR 识别扫描版 PDF"""
    print(f"{Colors.CYAN}📷 检测到扫描版 PDF，启动 OCR 识别...{Colors.ENDC}")
    
    try:
        from pdf2image import convert_from_path
        import easyocr
    except ImportError as e:
        print(f"{Colors.RED}❌ 缺少依赖: {e}{Colors.ENDC}")
        print(f"   请安装: pip install pdf2image easyocr")
        return ""
    
    # 临时目录
    if temp_dir is None:
        temp_dir = Path.home() / ".cache" / "pdf_ocr"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. PDF 转图片
    print(f"  🖨️  PDF 转图片中...")
    try:
        pages = convert_from_path(str(pdf_path), dpi=300)
        print(f"  ✅ 共 {len(pages)} 页")
    except Exception as e:
        print(f"{Colors.RED}❌ PDF 转图片失败: {e}{Colors.ENDC}")
        print(f"   可能需要安装 poppler: brew install poppler")
        return ""
    
    # 2. 初始化 OCR
    print(f"  🤖  初始化 OCR 引擎 (EasyOCR)...")
    reader = easyocr.Reader(['ch_sim', 'en'], verbose=False)
    
    # 3. 逐页识别
    all_text = ""
    for i, page_img in enumerate(pages, 1):
        print(f"  🔍  正在识别第 {i}/{len(pages)} 页...", end="\r")
        
        # 保存临时图片
        img_path = temp_dir / f"page_{i}.png"
        page_img.save(img_path)
        
        # OCR 识别
        result = reader.readtext(str(img_path), detail=0)
        page_text = "\n".join(result)
        all_text += page_text + "\n\n"
        
        # 清理
        img_path.unlink()
    
    print(f"\n  ✅ OCR 完成，共 {len(all_text)} 字符")
    return all_text


def extract_text_with_ocr(pdf_path: Path) -> str:
    """智能提取 PDF 文本：先尝试普通提取，失败则用 OCR"""
    print(f"\n{Colors.CYAN}📂 解析文档: {pdf_path.name}{Colors.ENDC}")
    
    # 第一步：尝试普通文本提取
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf_path))
        all_text = ""
        has_text = False
        
        for page in doc:
            text = page.get_text()
            all_text += text
            if len(text.strip()) > 100:
                has_text = True
        
        if has_text:
            print(f"  ✅ PyMuPDF 提取成功，共 {len(all_text)} 字符")
            return all_text
    except Exception as e:
        print(f"  ⚠️  PyMuPDF 提取失败: {e}")
    
    # 第二步：尝试 pdfplumber
    try:
        import pdfplumber
        paragraphs = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                text = page.get_text()
                if text:
                    for para in text.split('\n'):
                        para = para.strip()
                        if para and len(para) > 3:
                            paragraphs.append(para)
        
        all_text = '\n'.join(paragraphs)
        if len(all_text) > 500:
            print(f"  ✅ pdfplumber 提取成功，共 {len(all_text)} 字符，{len(paragraphs)} 段")
            return all_text
    except Exception as e:
        print(f"  ⚠️  pdfplumber 提取失败: {e}")
    
    # 第三步：OCR 识别（扫描件）
    return ocr_pdf_with_easyocr(pdf_path)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_file = Path(sys.argv[1])
        text = extract_text_with_ocr(pdf_file)
        print(f"\n前 500 字符预览:\n{text[:500]}")
    else:
        print("用法: python ocr_extract.py <pdf_file>")
