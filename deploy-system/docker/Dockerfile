# ==============================================
# OpenClaw Dockerfile v1.0
# 智能体系统基础镜像
# ==============================================

# 使用官方 Python 3.11 基础镜像
FROM python:3.11-slim

# 设置维护者信息
LABEL maintainer="OpenClaw Team"
LABEL version="1.0.0"
LABEL description="OpenClaw 智能体系统基础镜像"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV OPENCLAW_HOME /app
ENV OPENCLAW_ENV production

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    vim \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制核心配置模板
COPY config-templates/ /app/config-templates/

# 复制脚本
COPY scripts/ /app/scripts/

# 设置脚本可执行权限
RUN chmod +x /app/scripts/*.sh /app/scripts/*.py 2>/dev/null || true

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python /app/scripts/health_check.py || exit 1

# 启动命令
CMD ["python", "/app/scripts/bootstrap.py"]

# ==============================================
# 版本：v1.0 | 最后更新：2026-05-08
# ==============================================
