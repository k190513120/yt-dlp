FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY yt_dlp_api.py .

# 创建下载目录
RUN mkdir -p downloads

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV FLASK_ENV=production
ENV FORCE_IPV4=true
ENV YT_DLP_FORCE_IPV4=1

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动应用
CMD ["python", "yt_dlp_api.py"]