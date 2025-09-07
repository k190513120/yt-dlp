# yt-dlp HTTP API

基于yt-dlp的HTTP API服务，支持YouTube视频信息获取、流媒体链接提取和直接播放功能。

## 功能特性

- 🎥 获取YouTube视频信息
- 🔗 提取流媒体链接
- 🎬 直接流式播放
- 🍪 支持cookies认证绕过机器人验证
- 📱 支持多种视频格式和质量
- 🚀 高性能异步处理

## API端点

### 1. 获取视频信息
```bash
GET /api/info?url=https://www.youtube.com/watch?v=VIDEO_ID
```

### 2. 获取流媒体链接
```bash
GET /api/stream-links?url=https://www.youtube.com/watch?v=VIDEO_ID
```

### 3. 获取可播放链接（代理）
```bash
GET /api/playable-links?url=https://www.youtube.com/watch?v=VIDEO_ID
```

### 4. 直接流式播放
```bash
GET /api/stream?url=https://www.youtube.com/watch?v=VIDEO_ID&format=best
```

## 部署方式

### Railway 部署（推荐）

1. Fork 此仓库到你的GitHub账户
2. 访问 [Railway](https://railway.app)
3. 点击 "Deploy from GitHub repo"
4. 选择你fork的仓库
5. Railway会自动检测Dockerfile并部署

### Render 部署

1. Fork 此仓库
2. 访问 [Render](https://render.com)
3. 创建新的Web Service
4. 连接你的GitHub仓库
5. 使用以下设置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 yt_dlp_api.py`

### Heroku 部署

1. 安装Heroku CLI
2. 登录Heroku: `heroku login`
3. 创建应用: `heroku create your-app-name`
4. 推送代码: `git push heroku main`

### Docker 部署

```bash
# 构建镜像
docker build -t yt-dlp-api .

# 运行容器
docker run -p 8000:8000 yt-dlp-api
```

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
python3 yt_dlp_api.py
```

## 环境变量

- `PORT`: 服务端口（默认：8000）
- `HOST`: 服务主机（默认：0.0.0.0）

## Cookies 配置

为了绕过YouTube的机器人验证，需要配置cookies.txt文件：

1. 使用浏览器扩展导出YouTube cookies
2. 将cookies保存为Netscape格式的cookies.txt文件
3. 确保cookies.txt在项目根目录

## 使用示例

```bash
# 获取视频信息
curl "https://your-api-domain.com/api/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 获取播放链接
curl "https://your-api-domain.com/api/playable-links?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 直接播放（在浏览器中打开）
https://your-api-domain.com/api/stream?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## 技术栈

- Python 3.9+
- FastAPI
- yt-dlp
- uvicorn
- aiofiles

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 注意事项

- 请遵守YouTube的服务条款
- 仅用于个人学习和研究目的
- 不要用于商业用途或大规模爬取