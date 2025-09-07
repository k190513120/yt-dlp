# Koyeb IPv4强制部署指南

本指南将帮助你将Koyeb部署修改为强制使用IPv4，解决YouTube链接访问的IPv6问题。

## 📋 问题背景

之前的部署中，云端API仍在返回IPv6地址的YouTube链接，导致某些地区无法正常访问。通过强制使用IPv4可以解决这个问题。

## 🔧 已完成的配置修改

### 1. koyeb.yaml 配置更新

**修改内容：**
- 端口从5000改为8000（匹配Dockerfile）
- 添加IPv4强制环境变量

```yaml
name: yt-dlp-api
services:
  - name: api
    type: web
    build:
      type: docker
      dockerfile: ./Dockerfile
    ports:
      - port: 8000  # 已修改
        protocol: http
    env:
      - PORT=8000   # 已修改
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
      - FORCE_IPV4=true        # 新增
      - YT_DLP_FORCE_IPV4=1    # 新增
    health_check:
      http:
        path: /health
        port: 8000  # 已修改
```

### 2. Dockerfile 配置更新

**添加的环境变量：**
```dockerfile
ENV FORCE_IPV4=true
ENV YT_DLP_FORCE_IPV4=1
```

### 3. yt_dlp_api.py 代码确认

确认代码中包含IPv4强制配置：
```python
ydl_opts = {
    'force_ipv4': True,  # 强制使用IPv4
    # ... 其他配置
}
```

## 🚀 重新部署步骤

### 方法一：使用自动化脚本（推荐）

1. **运行部署脚本：**
   ```bash
   python3 koyeb_ipv4_deploy.py
   ```

   脚本将自动执行：
   - 检查Git状态
   - 提交并推送更改
   - 等待Koyeb重新部署
   - 验证IPv4配置是否生效

### 方法二：手动部署

1. **提交并推送代码：**
   ```bash
   git add .
   git commit -m "Update Koyeb config for IPv4 support"
   git push origin main
   ```

2. **在Koyeb控制台手动触发重新部署：**
   - 访问 [Koyeb控制台](https://app.koyeb.com/)
   - 找到你的yt-dlp-api应用
   - 点击"Redeploy"按钮

3. **等待部署完成：**
   - 监控部署日志
   - 确认服务状态为"Running"

## ✅ 验证IPv4配置

### 1. 健康检查
```bash
curl https://your-app.koyeb.app/health
```

### 2. 测试API功能
```bash
curl -X POST https://your-app.koyeb.app/api/playable-links \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### 3. 检查返回的链接
**期望结果：**
- `original_url` 应包含IPv4地址（如：`142.250.xxx.xxx`）
- 不应包含IPv6地址标识（如：`::`、`2001:`、`2605:`）

## 🔍 故障排除

### 问题1：部署后仍返回IPv6地址

**可能原因：**
- Koyeb环境变量未正确设置
- 代码缓存问题
- 构建过程中出现错误

**解决方案：**
1. 检查Koyeb控制台中的环境变量设置
2. 查看构建日志是否有错误
3. 尝试完全删除并重新创建服务

### 问题2：部署失败

**检查项目：**
1. **构建日志：** 查看Koyeb控制台中的构建日志
2. **端口配置：** 确认所有端口都设置为8000
3. **依赖文件：** 确认requirements.txt存在且正确

### 问题3：健康检查失败

**检查项目：**
1. **健康检查路径：** 确认`/health`端点正常工作
2. **端口映射：** 确认容器端口8000正确暴露
3. **启动时间：** 增加`initial_delay_seconds`值

## 📊 环境变量说明

| 变量名 | 值 | 说明 |
|--------|----|---------|
| `PORT` | `8000` | 应用监听端口 |
| `FLASK_ENV` | `production` | Flask运行环境 |
| `PYTHONUNBUFFERED` | `1` | Python输出不缓冲 |
| `FORCE_IPV4` | `true` | 强制IPv4标志 |
| `YT_DLP_FORCE_IPV4` | `1` | yt-dlp IPv4强制标志 |

## 🎯 验证成功标准

部署成功的标准：
1. ✅ 健康检查返回200状态码
2. ✅ API基本功能正常
3. ✅ `/api/playable-links`返回IPv4地址
4. ✅ 返回的代理链接可正常访问
5. ✅ 不再出现IPv6地址

## 📞 技术支持

如果遇到问题，请检查：
1. **Koyeb控制台：** 查看服务状态和日志
2. **GitHub仓库：** 确认最新代码已推送
3. **本地测试：** 确认本地API工作正常

## 📝 更新日志

- **2024-01-XX：** 修复端口配置不匹配问题
- **2024-01-XX：** 添加IPv4强制环境变量
- **2024-01-XX：** 创建自动化部署脚本
- **2024-01-XX：** 完善验证和故障排除流程

---

**注意：** 请将脚本中的`KOYEB_API_URL`替换为你的实际Koyeb应用地址。