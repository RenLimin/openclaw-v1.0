#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 微服务 API
提供 PDF OCR HTTP 接口
"""

import os
import tempfile
import subprocess
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI(title="OCR Service", version="1.0")


@app.post("/ocr/pdf", response_class=PlainTextResponse)
async def ocr_pdf(file: UploadFile = File(...), lang: str = "chi_sim+eng"):
    """上传 PDF，返回识别后的纯文本"""
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_pdf = Path(tmpdir) / "input.pdf"
        output_pdf = Path(tmpdir) / "output.pdf"
        
        # 保存上传文件
        with open(input_pdf, "wb") as f:
            f.write(await file.read())
        
        # 运行 OCRmyPDF
        result = subprocess.run([
            'ocrmypdf',
            '-l', lang,
            '--skip-text',
            '--clean',
            '--quiet',
            str(input_pdf),
            str(output_pdf)
        ], capture_output=True, timeout=300)
        
        if result.returncode not in [0, 2]:
            raise HTTPException(status_code=500, detail=f"OCR 失败: {result.stderr.decode()}")
        
        # 从 OCR 后的 PDF 提取文本
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(output_pdf))
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n\n"
            return full_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文本提取失败: {e}")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "ocr-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
