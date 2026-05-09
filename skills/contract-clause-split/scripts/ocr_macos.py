#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 macOS 内置 Vision 框架进行 PDF OCR 识别
无需 PyTorch、无需下载大模型，速度快、准确率高
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


def ocr_image_with_vision(image_path: Path) -> str:
    """
    使用 macOS 内置的 VNRecognizeTextRequest 进行 OCR
    通过 AppleScript / Shortcuts / Python 桥接调用
    """
    # 使用 Swift 命令行工具调用 Vision
    swift_code = f'''
import Vision
import Foundation

let imagePath = "{image_path}"
let image = CIImage(contentsOf: URL(fileURLWithPath: imagePath))!

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(ciImage: image, options: [:])
try handler.perform([request])

var results: [String] = []
for observation in request.results ?? [] {{
    if let text = try? observation.topCandidate(1).string {{
        results.append(text)
    }}
}}

print(results.joined(separator: "\\n"))
'''
    
    # 写入临时 Swift 文件并执行
    with tempfile.NamedTemporaryFile(suffix='.swift', mode='w') as f:
        f.write(swift_code)
        f.flush()
        
        try:
            result = subprocess.run(
                ['swift', f.name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except Exception as e:
            return ""


def pdf_to_images_pdf2image(pdf_path: Path, output_dir: Path) -> list:
    """使用 pdf2image 将 PDF 转为图片"""
    try:
        from pdf2image import convert_from_path
        pages = convert_from_path(str(pdf_path), dpi=200)
        image_paths = []
        
        for i, page in enumerate(pages, 1):
            img_path = output_dir / f"page_{i}.png"
            page.save(img_path)
            image_paths.append(img_path)
        
        return image_paths
    except Exception as e:
        print(f"  ⚠️  pdf2image 失败: {e}")
        return []


def extract_text_with_ocr(pdf_path: Path) -> str:
    """智能 PDF 文本提取"""
    print(f"\n{Colors.CYAN}📂 解析文档: {pdf_path.name}{Colors.ENDC}")
    
    # 第一步：尝试 PyMuPDF 提取（文本版 PDF）
    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        all_text = ""
        has_text = False
        
        for page in doc:
            text = page.get_text()
            all_text += text
            if len(text.strip()) > 50:
                has_text = True
        
        if has_text:
            print(f"  ✅ PyMuPDF 提取成功，共 {len(all_text)} 字符")
            return all_text
    except Exception:
        pass
    
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
            print(f"  ✅ pdfplumber 提取成功，共 {len(all_text)} 字符")
            return all_text
    except Exception:
        pass
    
    # 第三步：这是扫描件，需要 OCR
    print(f"  📷 检测到扫描件 PDF，启动 OCR...")
    
    # 检查是否有 OCRmyPDF（最省心方案）
    try:
        result = subprocess.run(
            ['ocrmypdf', '--version'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  🤖  使用 OCRmyPDF 进行识别...")
            return ocr_with_ocrmypdf(pdf_path)
    except Exception:
        pass
    
    print(f"  ⚠️  未找到 OCRmyPDF，建议安装: brew install ocrmypdf tesseract tesseract-lang")
    print(f"  💡  临时方案：先使用 Word 版开发，生产环境部署 OCRmyPDF")
    
    # 兜底返回空，让主程序给用户明确提示
    return ""


def ocr_with_ocrmypdf(pdf_path: Path) -> str:
    """使用 OCRmyPDF + Tesseract 进行 OCR"""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_pdf = Path(tmpdir) / "ocr_output.pdf"
        output_txt = Path(tmpdir) / "ocr_output.txt"
        
        # 第一步：生成可搜索 PDF
        result = subprocess.run([
            'ocrmypdf',
            '-l', 'chi_sim+eng',  # 中文简体 + 英文
            '--skip-text',
            '--clean',
            str(pdf_path),
            str(output_pdf)
        ], capture_output=True, timeout=300)
        
        if result.returncode != 0:
            print(f"  ⚠️  OCRmyPDF 可能需要更长时间，或尝试降低 DPI")
            return ""
        
        # 第二步：从 OCR 后的 PDF 提取文本
        try:
            import fitz
            doc = fitz.open(str(output_pdf))
            all_text = ""
            for page in doc:
                all_text += page.get_text() + "\n\n"
            
            print(f"  ✅ OCR 完成，共 {len(all_text)} 字符")
            return all_text
        except Exception as e:
            print(f"  ❌ OCR 后文本提取失败: {e}")
            return ""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_file = Path(sys.argv[1])
        text = extract_text_with_ocr(pdf_file)
        if text:
            print(f"\n前 800 字符预览:\n{text[:800]}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  需要安装 OCRmyPDF 进行扫描件识别{Colors.ENDC}")
            print(f"   执行: brew install ocrmypdf tesseract tesseract-lang")
    else:
        print("用法: python ocr_macos.py <pdf_file>")
