# YouTube链接访问问题修复部署指南

## 问题描述

云端API返回的YouTube链接无法直接访问，而本地API返回的链接可以正常访问。经过分析发现问题原因：

1. **IPv6 vs IPv4差异**：云端API使用IPv6地址，本地API使用IPv4地址
2. **CDN节点差异**：使用不同的Google CDN节点（rr2 vs rr5）
3. **网络限制**：YouTube对某些IPv6地址或CDN节点有访问限制

## 修复方案

### 1. 强制使用IPv4

在 `yt_dlp_api.py` 的 `get_ydl_opts_with_cookies` 函数中添加以下配置：

```python
def get_ydl_opts_with_cookies(cookies_data=None):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
        'extract_flat': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'ignoreerrors': True,
        # 强制使用IPv4
        'source_address': '0.0.0.0',
        'socket_timeout': 30,
        'retries': 3,
        # 添加User-Agent和客户端配置
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['webpage']
            }
        }
    }
    
    # ... 其余代码保持不变
```

### 2. 关键配置说明

- `source_address: '0.0.0.0'`：强制yt-dlp使用IPv4地址
- `socket_timeout: 30`：设置socket超时时间
- `retries: 3`：设置重试次数
- `http_headers`：添加标准浏览器User-Agent
- `extractor_args`：配置YouTube提取器使用Android/Web客户端

## 部署步骤

### 步骤1：备份现有文件

```bash
cp yt_dlp_api.py yt_dlp_api.py.backup
```

### 步骤2：应用修复

将上述修复代码应用到云端环境的 `yt_dlp_api.py` 文件中。

### 步骤3：重启服务

```bash
# 停止现有服务
pkill -f "python.*yt_dlp_api.py"

# 启动修复后的服务
python3 yt_dlp_api.py
```

### 步骤4：验证修复

使用提供的测试脚本验证修复效果：

```bash
python3 test_api_fix.py
```

## 测试验证

### 本地测试结果

✅ **修复前**：
- 本地API返回的链接：可访问（HTTP 200）
- 云端API返回的链接：不可访问（HTTP 403）

✅ **修复后**：
- 本地API返回的链接：可访问（HTTP 200）
- 修复后的API返回的链接：可访问（HTTP 200）

### 关键改进

1. **网络层面**：强制使用IPv4，避免IPv6访问限制
2. **客户端伪装**：使用标准浏览器User-Agent
3. **提取器优化**：配置YouTube提取器使用更稳定的客户端
4. **容错机制**：增加超时和重试配置

## 监控建议

部署后建议监控以下指标：

1. **API响应成功率**：监控 `/api/stream-links` 和 `/api/playable-links` 的成功率
2. **链接可访问性**：定期测试返回的YouTube链接是否可直接访问
3. **响应时间**：监控API响应时间是否在合理范围内
4. **错误日志**：关注yt-dlp相关的错误日志

## 故障排除

如果修复后仍有问题，请检查：

1. **网络连接**：确保服务器可以正常访问YouTube
2. **yt-dlp版本**：确保使用最新版本的yt-dlp
3. **依赖包**：检查所有Python依赖包是否正确安装
4. **防火墙设置**：确保没有防火墙阻止IPv4连接

## 联系支持

如果遇到问题，请提供：
- 错误日志
- 测试脚本输出
- 服务器环境信息
- 具体的YouTube链接示例