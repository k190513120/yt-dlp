#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证yt-dlp API修复方案的有效性
测试YouTube链接访问问题的修复情况
"""

import requests
import json
import sys
from urllib.parse import urlparse

def test_api_endpoint(base_url, endpoint, test_url):
    """测试API端点"""
    print(f"\n🧪 测试端点: {endpoint}")
    
    try:
        # 发送POST请求到API
        response = requests.post(
            f"{base_url}{endpoint}",
            json={"url": test_url},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ API请求失败: {response.status_code}")
            return False
            
        data = response.json()
        print(f"✅ API响应成功")
        print(f"📹 视频标题: {data.get('title', 'N/A')}")
        print(f"⏱️ 视频时长: {data.get('duration', 'N/A')}秒")
        
        # 测试音频流链接
        audio_stream = data.get('audio_stream')
        if audio_stream and audio_stream.get('url'):
            audio_url = audio_stream['url']
            print(f"🎵 测试音频流链接...")
            if test_direct_access(audio_url):
                print(f"✅ 音频流链接可访问")
            else:
                print(f"❌ 音频流链接无法访问")
                return False
        else:
            print(f"⚠️ 未找到音频流")
            
        # 测试视频流链接
        video_stream = data.get('video_stream')
        if video_stream and video_stream.get('url'):
            video_url = video_stream['url']
            print(f"🎬 测试视频流链接...")
            if test_direct_access(video_url):
                print(f"✅ 视频流链接可访问")
            else:
                print(f"❌ 视频流链接无法访问")
                return False
        else:
            print(f"⚠️ 未找到视频流")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_direct_access(url):
    """测试直接访问链接"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试yt-dlp API修复方案")
    print("=" * 50)
    
    # 配置
    base_url = "http://localhost:5000"
    test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # 测试API是否运行
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print(f"❌ API服务器未运行或不健康")
            sys.exit(1)
        print(f"✅ API服务器运行正常")
    except:
        print(f"❌ 无法连接到API服务器 ({base_url})")
        print(f"请确保API服务器正在运行")
        sys.exit(1)
    
    # 测试各个端点
    endpoints_to_test = [
        "/api/stream-links",
        "/api/playable-links"
    ]
    
    all_passed = True
    
    for endpoint in endpoints_to_test:
        if not test_api_endpoint(base_url, endpoint, test_video_url):
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！修复方案有效！")
        print("✅ YouTube链接访问问题已解决")
        print("✅ API返回的链接可以直接访问")
    else:
        print("❌ 部分测试失败，需要进一步调试")
        sys.exit(1)

if __name__ == "__main__":
    main()