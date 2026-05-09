#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EasyOCR 扫描件 PDF 识别模块
使用本地已下载模型，无需联网
"""

import os
import sys
import tempfile
from pathlib import Path

# 颜色输出
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'


def ocr_pdf(pdf_path: Path) -> str:
    """使用 EasyOCR 识别扫描版 PDF（使用本地模型）"""
    print(f"\n{Colors.CYAN}📂 解析文档: {pdf_path.name}{Colors.ENDC}")
    
    # 第一步：尝试普通文本提取
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        paragraphs = []
        has_text = False
        
        for page in doc:
            text = page.get_text()
            if text:
                for para in text.split('\n'):
                    para = para.strip()
                    if para and len(para) > 3:
                        paragraphs.append(para)
                        if len(para) > 50:
                            has_text = True
        
        full_text = '\n'.join(paragraphs)
        if has_text:
            print(f"  ✅ PyMuPDF 提取成功，共 {len(paragraphs)} 段，{len(full_text)} 字符")
            return full_text
    except Exception as e:
        print(f"  ⚠️  PyMuPDF 失败: {e}")
    
    print(f"  📷 检测到扫描版 PDF，启动 OCR...")
    
    # 第二步：PDF 转图片
    try:
        from pdf2image import convert_from_path
    except ImportError:
        print(f"  {Colors.RED}❌ 请安装: pip install pdf2image{Colors.ENDC}")
        return ""
    
    print(f"  🖨️  PDF 转图片中...")
    try:
        pages = convert_from_path(str(pdf_path), dpi=200)
        print(f"  ✅ 共 {len(pages)} 页")
    except Exception as e:
        print(f"{Colors.RED}❌ PDF 转图片失败: {e}{Colors.ENDC}")
        print(f"   可能需要安装 poppler: brew install poppler")
        return ""
    
    # 第三步：EasyOCR 识别（使用本地模型）
    print(f"  🤖  加载 EasyOCR 本地模型...")
    model_dir = Path.home() / ".EasyOCR" / "model"
    
    try:
        import easyocr
        reader = easyocr.Reader(
            ['ch_sim', 'en'],
            model_storage_directory=str(model_dir.parent),
            download_enabled=False,  # 禁止下载
            verbose=False
        )
    except Exception as e:
        print(f"  {Colors.RED}❌ EasyOCR 加载失败: {e}{Colors.ENDC}")
        return ""
    
    # 逐页识别
    all_lines = []
    for i, page_img in enumerate(pages, 1):
        print(f"  🔍  识别第 {i}/{len(pages)} 页...", end="\r")
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img_path = Path(f.name)
        
        try:
            page_img.save(img_path)
            result = reader.readtext(str(img_path), detail=0)
            all_lines.extend(result)
        finally:
            img_path.unlink()
    
    full_text = '\n'.join(all_lines)
    print(f"\n  ✅ OCR 完成，共 {len(all_lines)} 行，{len(full_text)} 字符")
    return full_text


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_file = Path(sys.argv[1])
        text = ocr_pdf(pdf_file)
        if text:
            print(f"\n前 1000 字符预览:")
            print("-"*60)
            print(text[:1000])
            print("-"*60)
    else:
        print("用法: python ocr_easyocr.py <pdf_file>")
