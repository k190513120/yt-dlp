# YouTube 视频转文字 API 使用指南

## 概述

新增的 `/api/transcribe` 端点使用 OpenAI Whisper 模型将 YouTube 视频的音频转换为文字。该功能支持多种语言的自动识别和转录。

## 端点信息

- **URL**: `/api/transcribe`
- **方法**: GET, POST
- **功能**: 提取 YouTube 视频音频并转换为文字

## 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `url` | string | 是 | - | YouTube 视频链接 |
| `model` | string | 否 | base | Whisper 模型大小 (tiny/base/small/medium/large) |
| `language` | string | 否 | auto | 语言代码，auto 为自动检测 |
| `cookies` | object | 否 | - | cookies 配置（用于访问受限视频） |

## 使用限制

- **最大视频时长**: 30分钟（1800秒）
- **推荐模型**: base（平衡速度和准确性）
- **支持格式**: 所有 yt-dlp 支持的 YouTube 视频格式

## 使用示例

### 1. GET 请求（基础用法）

```bash
curl "http://localhost:5000/api/transcribe?url=https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

### 2. GET 请求（指定模型和语言）

```bash
curl "http://localhost:5000/api/transcribe?url=https://www.youtube.com/watch?v=jNQXAC9IVRw&model=base&language=en"
```

### 3. POST 请求（JSON 格式）

```bash
curl -X POST "http://localhost:5000/api/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "model": "base",
    "language": "en"
  }'
```

### 4. 使用 cookies（访问受限视频）

```bash
curl -X POST "http://localhost:5000/api/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "model": "base",
    "cookies": {
      "use_browser": true,
      "browser": "chrome"
    }
  }'
```

## 响应格式

### 成功响应

```json
{
  "title": "视频标题",
  "duration": 19,
  "language": "en",
  "text": "完整的转录文本...",
  "segments": [
    {
      "start": 0.0,
      "end": 4.0,
      "text": "分段文本内容"
    }
  ],
  "model_used": "base",
  "processing_info": {
    "audio_extracted": true,
    "transcription_completed": true
  }
}
```

### 错误响应

```json
{
  "error": "错误描述信息"
}
```

## 模型选择建议

| 模型 | 速度 | 准确性 | 内存使用 | 适用场景 |
|------|------|--------|----------|----------|
| tiny | 最快 | 较低 | 最少 | 快速预览、资源受限环境 |
| base | 快 | 良好 | 适中 | **推荐**，平衡性能 |
| small | 中等 | 较好 | 较多 | 高质量转录 |
| medium | 慢 | 很好 | 多 | 专业用途 |
| large | 最慢 | 最好 | 最多 | 最高质量要求 |

## 语言代码示例

- `en` - 英语
- `zh` - 中文
- `ja` - 日语
- `ko` - 韩语
- `es` - 西班牙语
- `fr` - 法语
- `de` - 德语
- `auto` - 自动检测（默认）

## 错误处理

常见错误及解决方案：

1. **视频时长超限**: 选择较短的视频或分段处理
2. **无效URL**: 检查 YouTube 链接格式
3. **视频不可用**: 视频可能被删除或设为私有
4. **音频提取失败**: 检查网络连接和视频可访问性
5. **模型加载失败**: 确保有足够的内存和存储空间

## 性能优化建议

1. **选择合适的模型**: 根据需求平衡速度和准确性
2. **控制视频时长**: 较短视频处理更快
3. **网络环境**: 确保稳定的网络连接
4. **系统资源**: 确保有足够的内存和CPU资源

## 部署注意事项

- 确保安装了 `ffmpeg`
- 云端部署时注意内存限制
- 生产环境建议使用 WSGI 服务器
- 考虑添加请求频率限制

## 技术实现

- **音频提取**: 使用 yt-dlp 提取高质量音频
- **语音识别**: 使用 OpenAI Whisper 模型
- **格式支持**: 自动处理多种音频格式
- **临时文件**: 自动清理临时音频文件
- **错误处理**: 完整的异常捕获和用户友好的错误信息