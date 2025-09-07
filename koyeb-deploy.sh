#!/bin/bash

# Koyeb 部署脚本
# 使用SSH方式部署yt-dlp HTTP API到Koyeb平台

set -e

echo "🚀 开始部署yt-dlp HTTP API到Koyeb平台"

# 检查必要的工具
command -v git >/dev/null 2>&1 || { echo "❌ 需要安装git"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ 需要安装docker"; exit 1; }

# 项目配置
APP_NAME="yt-dlp-api"
GIT_REPO="https://github.com/yourusername/yt-dlp-api.git"  # 替换为你的仓库地址
REGION="fra"  # 可选: fra, was, sin
INSTANCE_TYPE="nano"  # 可选: nano, micro, small

echo "📦 项目名称: $APP_NAME"
echo "🌍 部署区域: $REGION"
echo "💻 实例类型: $INSTANCE_TYPE"

# 检查是否已初始化git仓库
if [ ! -d ".git" ]; then
    echo "📝 初始化Git仓库..."
    git init
    git add .
    git commit -m "Initial commit for Koyeb deployment"
fi

# 构建Docker镜像（本地测试）
echo "🐳 构建Docker镜像进行本地测试..."
docker build -t $APP_NAME:latest .

echo "🧪 启动本地测试容器..."
docker run -d --name ${APP_NAME}-test -p 8000:8000 $APP_NAME:latest

# 等待容器启动
sleep 5

# 测试健康检查
echo "🏥 测试健康检查端点..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 健康检查通过"
else
    echo "❌ 健康检查失败"
    docker logs ${APP_NAME}-test
    docker stop ${APP_NAME}-test
    docker rm ${APP_NAME}-test
    exit 1
fi

# 清理测试容器
docker stop ${APP_NAME}-test
docker rm ${APP_NAME}-test

echo "✅ 本地测试通过！"
echo ""
echo "📋 接下来的步骤:"
echo "1. 将代码推送到GitHub仓库"
echo "2. 在Koyeb控制台创建应用"
echo "3. 连接GitHub仓库并配置部署"
echo ""
echo "🔗 Koyeb控制台: https://app.koyeb.com/"
echo "📚 部署文档: https://www.koyeb.com/docs/"
echo ""
echo "🎯 推荐的环境变量配置:"
echo "   PORT=8000"
echo "   FLASK_ENV=production"
echo "   PYTHONUNBUFFERED=1"
echo ""
echo "🚀 部署完成后，你的API将在以下地址可用:"
echo "   https://$APP_NAME-<random>.koyeb.app/"