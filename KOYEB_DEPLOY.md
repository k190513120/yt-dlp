# Koyeb SSH 部署指南

本指南将帮助你通过SSH方式将yt-dlp HTTP API部署到Koyeb平台。

## 📋 准备工作

### 1. 系统要求
- Git
- Docker (用于本地测试)
- SSH客户端
- GitHub账号
- Koyeb账号

### 2. 项目文件检查
确保以下文件存在：
- `yt_dlp_api.py` - 主应用文件
- `requirements.txt` - Python依赖
- `Dockerfile` - 容器配置
- `.dockerignore` - Docker忽略文件

## 🚀 部署步骤

### 步骤1: 准备代码仓库

```bash
# 1. 初始化Git仓库（如果还没有）
git init

# 2. 添加所有文件
git add .

# 3. 提交代码
git commit -m "Ready for Koyeb deployment"

# 4. 添加远程仓库（替换为你的GitHub仓库地址）
git remote add origin https://github.com/yourusername/yt-dlp-api.git

# 5. 推送到GitHub
git branch -M main
git push -u origin main
```

### 步骤2: 本地测试

```bash
# 1. 构建Docker镜像
docker build -t yt-dlp-api .

# 2. 运行容器测试
docker run -d --name yt-dlp-test -p 8000:8000 yt-dlp-api

# 3. 测试健康检查
curl http://localhost:8000/health

# 4. 测试API功能
curl "http://localhost:8000/api/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 5. 清理测试容器
docker stop yt-dlp-test
docker rm yt-dlp-test
```

### 步骤3: Koyeb控制台部署

#### 3.1 登录Koyeb
1. 访问 [Koyeb控制台](https://app.koyeb.com/)
2. 注册或登录账号
3. 完成账号验证

#### 3.2 创建应用
1. 点击 "Create App" 按钮
2. 选择 "GitHub" 作为源
3. 授权Koyeb访问你的GitHub账号
4. 选择包含yt-dlp-api的仓库

#### 3.3 配置部署设置

**基本配置:**
- **App name**: `yt-dlp-api`
- **Branch**: `main`
- **Build method**: `Docker`
- **Dockerfile path**: `./Dockerfile`

**服务配置:**
- **Service name**: `api`
- **Port**: `8000`
- **Health check path**: `/health`
- **Instance type**: `nano` (512MB RAM) 或 `micro` (1GB RAM)
- **Regions**: 选择离用户最近的区域
  - `fra` - 法兰克福
  - `was` - 华盛顿
  - `sin` - 新加坡

**环境变量:**
```
PORT=8000
FLASK_ENV=production
PYTHONUNBUFFERED=1
```

**扩缩容设置:**
- **Min instances**: 1
- **Max instances**: 3

#### 3.4 部署应用
1. 检查所有配置
2. 点击 "Deploy" 按钮
3. 等待构建和部署完成（通常需要3-5分钟）

### 步骤4: 验证部署

部署完成后，你将获得一个类似这样的URL：
`https://yt-dlp-api-<random-id>.koyeb.app`

```bash
# 测试健康检查
curl https://your-app-url.koyeb.app/health

# 测试API功能
curl "https://your-app-url.koyeb.app/api/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 测试音频下载
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' \
  https://your-app-url.koyeb.app/api/audio
```

## 🔧 SSH连接和管理

### 通过Koyeb CLI管理

```bash
# 1. 安装Koyeb CLI
curl -fsSL https://github.com/koyeb/koyeb-cli/raw/main/install.sh | sh

# 2. 登录
koyeb auth login

# 3. 查看应用状态
koyeb apps list
koyeb services list yt-dlp-api

# 4. 查看日志
koyeb services logs yt-dlp-api/api --follow

# 5. 重新部署
koyeb services redeploy yt-dlp-api/api
```

### 通过SSH连接实例（如果需要）

注意：Koyeb是无服务器平台，通常不提供直接SSH访问。但你可以通过以下方式进行调试：

```bash
# 查看实时日志
koyeb services logs yt-dlp-api/api --follow

# 查看服务详情
koyeb services describe yt-dlp-api/api

# 查看部署历史
koyeb deployments list yt-dlp-api/api
```

## 📊 监控和维护

### 1. 监控面板
- 访问Koyeb控制台查看实时指标
- 监控CPU、内存使用情况
- 查看请求数量和响应时间

### 2. 日志管理
```bash
# 查看最近的日志
koyeb services logs yt-dlp-api/api --tail 100

# 实时监控日志
koyeb services logs yt-dlp-api/api --follow

# 过滤错误日志
koyeb services logs yt-dlp-api/api --follow | grep ERROR
```

### 3. 更新部署
```bash
# 1. 更新代码
git add .
git commit -m "Update API"
git push origin main

# 2. Koyeb会自动检测到更改并重新部署
# 或者手动触发重新部署
koyeb services redeploy yt-dlp-api/api
```

## 🛠️ 故障排除

### 常见问题

1. **构建失败**
   ```bash
   # 检查构建日志
   koyeb deployments logs <deployment-id>
   ```

2. **健康检查失败**
   - 确保 `/health` 端点正常工作
   - 检查端口配置是否正确
   - 验证环境变量设置

3. **内存不足**
   - 升级到更大的实例类型
   - 优化代码减少内存使用

4. **下载失败**
   - 检查ffmpeg是否正确安装
   - 验证yt-dlp版本兼容性

### 调试命令

```bash
# 查看服务状态
koyeb services describe yt-dlp-api/api

# 查看最新部署
koyeb deployments list yt-dlp-api/api --limit 5

# 查看环境变量
koyeb services env list yt-dlp-api/api

# 更新环境变量
koyeb services env set yt-dlp-api/api PORT=8000
```

## 💰 费用优化

### Koyeb定价
- **免费层**: 每月$5.50免费额度
- **Nano实例**: $2.50/月 (512MB RAM)
- **Micro实例**: $5.50/月 (1GB RAM)

### 优化建议
1. 使用最小的实例类型满足需求
2. 设置合理的扩缩容策略
3. 监控使用情况避免超出免费额度

## 🔗 有用链接

- [Koyeb官方文档](https://www.koyeb.com/docs/)
- [Koyeb CLI文档](https://www.koyeb.com/docs/cli/)
- [Docker最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [yt-dlp文档](https://github.com/yt-dlp/yt-dlp)

## 🎉 完成！

恭喜！你已经成功将yt-dlp HTTP API部署到Koyeb平台。现在你可以通过公网URL访问你的API服务了。