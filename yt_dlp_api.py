#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yt-dlp HTTP API 服务器
提供REST API接口来调用yt-dlp功能
"""

from flask import Flask, request, jsonify
import yt_dlp
import os
import threading
import uuid
from datetime import datetime

app = Flask(__name__)

# 存储下载任务状态
download_tasks = {}

# 下载目录
DOWNLOAD_DIR = "./downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def progress_hook(d):
    """下载进度回调函数"""
    task_id = d.get('task_id')
    if task_id and task_id in download_tasks:
        if d['status'] == 'downloading':
            download_tasks[task_id]['status'] = 'downloading'
            download_tasks[task_id]['progress'] = {
                'downloaded_bytes': d.get('downloaded_bytes', 0),
                'total_bytes': d.get('total_bytes', 0),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0)
            }
        elif d['status'] == 'finished':
            download_tasks[task_id]['status'] = 'completed'
            download_tasks[task_id]['filename'] = d.get('filename')

def download_video(url, task_id, options=None):
    """后台下载视频"""
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
        }
        
        # 合并用户自定义选项
        if options:
            ydl_opts.update(options)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 添加task_id到进度回调
            for hook in ydl_opts['progress_hooks']:
                hook.__defaults__ = (task_id,) if hook.__defaults__ is None else hook.__defaults__ + (task_id,)
            
            download_tasks[task_id]['status'] = 'downloading'
            ydl.download([url])
            
    except Exception as e:
        download_tasks[task_id]['status'] = 'error'
        download_tasks[task_id]['error'] = str(e)

@app.route('/api/info', methods=['GET'])
def get_video_info():
    """获取视频信息（不下载）"""
    url = request.args.get('url')
    if not url:
        return jsonify({'error': '缺少URL参数'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 返回关键信息
            result = {
                'title': info.get('title'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'upload_date': info.get('upload_date'),
                'view_count': info.get('view_count'),
                'description': info.get('description', '')[:200] + '...' if info.get('description') else None,
                'formats': [{
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'quality': f.get('quality'),
                    'filesize': f.get('filesize'),
                    'url': f.get('url')
                } for f in info.get('formats', [])[:5]]  # 只返回前5个格式
            }
            
            return jsonify(result)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def start_download():
    """开始下载视频"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': '缺少URL参数'}), 400
    
    url = data['url']
    options = data.get('options', {})
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 初始化任务状态
    download_tasks[task_id] = {
        'status': 'pending',
        'url': url,
        'created_at': datetime.now().isoformat(),
        'progress': {},
        'filename': None,
        'error': None
    }
    
    # 启动后台下载线程
    thread = threading.Thread(target=download_video, args=(url, task_id, options))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'task_id': task_id,
        'status': 'pending',
        'message': '下载任务已创建'
    })

@app.route('/api/status/<task_id>', methods=['GET'])
def get_download_status(task_id):
    """获取下载状态"""
    if task_id not in download_tasks:
        return jsonify({'error': '任务不存在'}), 404
    
    return jsonify(download_tasks[task_id])

@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """列出所有任务"""
    return jsonify({
        'tasks': download_tasks,
        'total': len(download_tasks)
    })

@app.route('/api/formats', methods=['GET'])
def get_available_formats():
    """获取可用的下载格式"""
    url = request.args.get('url')
    if not url:
        return jsonify({'error': '缺少URL参数'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'listformats': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # 格式化输出
            result = []
            for f in formats:
                result.append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'resolution': f.get('resolution'),
                    'fps': f.get('fps'),
                    'filesize': f.get('filesize'),
                    'tbr': f.get('tbr'),  # 总比特率
                    'vcodec': f.get('vcodec'),
                    'acodec': f.get('acodec'),
                    'format_note': f.get('format_note')
                })
            
            return jsonify({
                'title': info.get('title'),
                'formats': result
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/audio', methods=['POST'])
def download_audio_only():
    """仅下载音频"""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': '缺少URL参数'}), 400
    
    url = data['url']
    
    # 音频专用选项
    audio_options = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 初始化任务状态
    download_tasks[task_id] = {
        'status': 'pending',
        'url': url,
        'type': 'audio_only',
        'created_at': datetime.now().isoformat(),
        'progress': {},
        'filename': None,
        'error': None
    }
    
    # 启动后台下载线程
    thread = threading.Thread(target=download_video, args=(url, task_id, audio_options))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'task_id': task_id,
        'status': 'pending',
        'message': '音频下载任务已创建'
    })

@app.route('/api/stream-links', methods=['GET'])
def get_stream_links():
    """获取视频的直接播放链接（不下载）"""
    url = request.args.get('url')
    if not url:
        return jsonify({'error': '缺少URL参数'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 获取所有格式
            formats = info.get('formats', [])
            
            # 找到最佳音频流
            best_audio = None
            for f in formats:
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':  # 纯音频
                    if not best_audio or (f.get('abr', 0) > best_audio.get('abr', 0)):
                        best_audio = f
            
            # 找到最佳视频流（带音频）
            best_video = None
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':  # 视频+音频
                    if not best_video or (f.get('height', 0) > best_video.get('height', 0)):
                        best_video = f
            
            # 如果没有找到带音频的视频，找最佳纯视频
            if not best_video:
                for f in formats:
                    if f.get('vcodec') != 'none':  # 纯视频
                        if not best_video or (f.get('height', 0) > best_video.get('height', 0)):
                            best_video = f
            
            result = {
                'title': info.get('title'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'thumbnail': info.get('thumbnail'),
                'audio_stream': {
                    'url': best_audio.get('url') if best_audio else None,
                    'format_id': best_audio.get('format_id') if best_audio else None,
                    'ext': best_audio.get('ext') if best_audio else None,
                    'abr': best_audio.get('abr') if best_audio else None,
                    'acodec': best_audio.get('acodec') if best_audio else None,
                    'filesize': best_audio.get('filesize') if best_audio else None
                } if best_audio else None,
                'video_stream': {
                    'url': best_video.get('url') if best_video else None,
                    'format_id': best_video.get('format_id') if best_video else None,
                    'ext': best_video.get('ext') if best_video else None,
                    'resolution': best_video.get('resolution') if best_video else None,
                    'height': best_video.get('height') if best_video else None,
                    'width': best_video.get('width') if best_video else None,
                    'vcodec': best_video.get('vcodec') if best_video else None,
                    'acodec': best_video.get('acodec') if best_video else None,
                    'fps': best_video.get('fps') if best_video else None,
                    'filesize': best_video.get('filesize') if best_video else None
                } if best_video else None
            }
            
            return jsonify(result)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'yt-dlp-api',
        'version': '1.0.0'
    })

@app.route('/', methods=['GET'])
def index():
    """API文档"""
    docs = {
        'name': 'yt-dlp HTTP API',
        'version': '1.0.0',
        'description': '通过HTTP接口调用yt-dlp功能',
        'endpoints': {
            'GET /health': '健康检查',
            'GET /api/info?url=<video_url>': '获取视频信息（不下载）',
            'POST /api/download': '开始下载视频 {"url": "<video_url>", "options": {}}',
            'GET /api/status/<task_id>': '获取下载状态',
            'GET /api/tasks': '列出所有任务',
            'GET /api/formats?url=<video_url>': '获取可用的下载格式',
            'POST /api/audio': '仅下载音频 {"url": "<video_url>"}',
            'GET /api/stream-links?url=<video_url>': '获取视频直接播放链接（不下载）'
        },
        'examples': {
            'get_info': 'curl "http://localhost:5000/api/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"',
            'download': 'curl -X POST -H "Content-Type: application/json" -d \'{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "options": {"format": "best[height<=720]"}}\' "http://localhost:5000/api/download"',
            'check_status': 'curl "http://localhost:5000/api/status/<task_id>"',
            'get_stream_links': 'curl "http://localhost:5000/api/stream-links?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"'
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    # 从环境变量获取端口，默认为5000
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("🚀 yt-dlp HTTP API 服务器启动中...")
    print(f"📖 API文档: http://localhost:{port}/")
    print(f"🏥 健康检查: http://localhost:{port}/health")
    print(f"🎵 示例: curl \"http://localhost:{port}/api/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ\"")
    
    app.run(host='0.0.0.0', port=port, debug=debug)