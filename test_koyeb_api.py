#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Koyeb云端API综合测试脚本
测试部署在Koyeb上的yt-dlp API的各项功能
"""

import requests
import time
import json
from datetime import datetime
from urllib.parse import urlparse

# 配置
CLOUD_API_BASE = "https://yt-dlp-api-miaomiaocompany-3d8d2eee.koyeb.app"
LOCAL_API_BASE = "http://localhost:5000"
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
TEST_VIDEO_ID = "dQw4w9WgXcQ"

class APITester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "cloud_api": CLOUD_API_BASE,
            "local_api": LOCAL_API_BASE,
            "test_video": TEST_VIDEO_URL,
            "tests": []
        }
    
    def log_test(self, test_name, success, response_time=None, details=None,