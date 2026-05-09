# ==========================================
# OCR 微服务 Dockerfile (Tesseract 5 + OCRmyPDF)
# ==========================================
FROM jbarlow83/ocrmypdf:latest

# 安装中文语言包
RUN apt-get update && \
    apt-get install -y tesseract-ocr-chi-sim tesseract-ocr-eng && \
    rm -rf /var/lib/apt/lists/*

# 安装 Python API
RUN pip install fastapi uvicorn python-multipart pypdf

# 创建工作目录
WORKDIR /app

# 启动脚本
COPY ocr-server.py /app/

EXPOSE 8000

CMD ["uvicorn", "ocr-server:app", "--host", "0.0.0.0", "--port", "8000"]
