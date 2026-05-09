#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 客户端
支持两种模式：
1. 本地模式（OCRmyPDF）
2. 远程模式（OCR 微服务 HTTP 接口）
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# 颜色输出
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'


def extract_text_pdf(pdf_path: Path, ocr_service_url: str = None) -> str:
    """
    智能 PDF 文本提取
    优先级：PyMuPDF > pdfplumber > 本地 OCR > 远程 OCR 服务
    """
    print(f"\n{Colors.CYAN}📂 解析 PDF: {pdf_path.name}{Colors.ENDC}")
    
    # 第一步：PyMuPDF 提取（文本版 PDF）
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
            print(f"  ✅ PyMuPDF 提取成功，{len(paragraphs)} 段，{len(full_text)} 字符")
            return full_text
    except Exception:
        pass
    
    # 第二步：pdfplumber
    try:
        import pdfplumber
        paragraphs = []
        has_text = False
        
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    for para in text.split('\n'):
                        para = para.strip()
                        if para and len(para) > 3:
                            paragraphs.append(para)
                            if len(para) > 50:
                                has_text = True
        
        full_text = '\n'.join(paragraphs)
        if has_text:
            print(f"  ✅ pdfplumber 提取成功，{len(paragraphs)} 段，{len(full_text)} 字符")
            return full_text
    except Exception:
        pass
    
    # 第三步：检测到扫描件
    print(f"  📷 检测到扫描版 PDF，需要 OCR 识别")
    
    # 优先尝试远程 OCR 服务
    if ocr_service_url:
        print(f"  🌐 尝试远程 OCR 服务: {ocr_service_url}")
        text = ocr_remote(pdf_path, ocr_service_url)
        if text:
            return text
    
    # 本地 OCR 模式
    print(f"  🔧 使用本地 OCR 模式（OCRmyPDF）")
    return ocr_local(pdf_path)


def ocr_local(pdf_path: Path) -> str:
    """本地 OCR 识别（需要安装 OCRmyPDF）"""
    try:
        # 检查 OCRmyPDF 是否已安装
        result = subprocess.run(
            ['ocrmypdf', '--version'],
            capture_output=True, timeout=10
        )
        if result.returncode != 0:
            raise Exception("OCRmyPDF 未安装")
    except Exception:
        print(f"  {Colors.YELLOW}💡  本地 OCR 未就绪，请执行以下任一方案:{Colors.ENDC}")
        print(f"     方案 A (推荐): docker-compose up -d  # 启动 OCR 微服务")
        print(f"     方案 B: brew install ocrmypdf tesseract tesseract-lang")
        print(f"     方案 C: 先用 Word 版进行开发验证")
        return ""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_pdf = Path(tmpdir) / "ocr_output.pdf"
        
        print(f"  ⏳ OCR 识别中（约需 30-60 秒）...")
        result = subprocess.run([
            'ocrmypdf',
            '-l', 'chi_sim+eng',
            '--skip-text',
            '--clean',
            '--quiet',
            str(pdf_path),
            str(output_pdf)
        ], capture_output=True, timeout=300)
        
        if result.returncode not in [0, 2]:
            print(f"  {Colors.RED}❌ OCR 失败{Colors.ENDC}")
            return ""
        
        # 提取文本
        import fitz
        doc = fitz.open(str(output_pdf))
        paragraphs = []
        for page in doc:
            text = page.get_text()
            if text:
                for para in text.split('\n'):
                    para = para.strip()
                    if para and len(para) > 2:
                        paragraphs.append(para)
        
        full_text = '\n'.join(paragraphs)
        print(f"  ✅ OCR 完成，{len(paragraphs)} 段，{len(full_text)} 字符")
        return full_text


def ocr_remote(pdf_path: Path, service_url: str) -> str:
    """调用远程 OCR 微服务"""
    try:
        import requests
    except ImportError:
        print(f"  ⚠️  请安装 requests: pip install requests")
        return ""
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{service_url}/ocr/pdf",
                files=files,
                timeout=300
            )
        
        if response.status_code == 200:
            full_text = response.text
            print(f"  ✅ 远程 OCR 完成，{len(full_text)} 字符")
            return full_text
        else:
            print(f"  ⚠️  远程 OCR 失败: {response.status_code}")
            return ""
    except Exception as e:
        print(f"  ⚠️  远程 OCR 连接失败: {e}")
        return ""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_file = Path(sys.argv[1])
        ocr_service = sys.argv[2] if len(sys.argv) > 2 else None
        text = extract_text_pdf(pdf_file, ocr_service)
        if text:
            print(f"\n前 500 字符预览:\n{text[:500]}")
    else:
        print("用法:")
        print("  python ocr_client.py <pdf_file>           # 本地模式")
        print("  python ocr_client.py <pdf_file> http://localhost:9998  # 远程模式")
