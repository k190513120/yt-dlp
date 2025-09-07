#!/usr/bin/env python3
"""
部署验证脚本 - 检查云端API是否使用了最新的IPv4修复代码
"""

import requests
import json
import subprocess
import sys
from datetime import datetime

# 配置
CLOUD_API_URL = "https://yt-dlp-api-miaomiaocompany-3d8d2eee.koyeb.app"
LOCAL_API_URL = "http://localhost:5000"
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def check_git_status():
    """检查Git状态和最新提交"""
    print("=== Git状态检查 ===")
    try:
        # 获取最新提交信息
        result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"最新提交: {result.stdout.strip()}")
        
        # 检查是否有未推送的提交
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            if result.stdout.strip():
                print("⚠️  有未提交的更改:")
                print(result.stdout)
            else:
                print("✅ 工作目录干净")
        
        # 检查远程状态
        result = subprocess.run(['git', 'status', '-uno'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Git状态: {result.stdout}")
            
    except Exception as e:
        print(f"❌ Git检查失败: {e}")

def test_api_endpoint(api_url, endpoint, params=None):
    """测试API端点"""
    try:
        url = f"{api_url}{endpoint}"
        if params:
            response = requests.get(url, params=params, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ {url} 返回状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 请求 {url} 失败: {e}")
        return None

def analyze_video_response(response, api_name):
    """分析视频响应中的IP地址类型"""
    if not response:
        return None
    
    print(f"\n=== {api_name} API 响应分析 ===")
    
    # 检查视频流URL中的IP地址
    video_stream = response.get('video_stream')
    if video_stream and 'url' in video_stream:
        url = video_stream['url']
        print(f"视频流URL: {url[:100]}...")
        
        # 检查IPv4/IPv6
        if '2605:6440' in url or '::' in url:
            print("🔴 检测到IPv6地址 - 修复未生效")
            return 'ipv6'
        elif any(ipv4_pattern in url for ipv4_pattern in ['34.', '35.', '172.', '192.']):
            print("🟢 检测到IPv4地址 - 修复已生效")
            return 'ipv4'
        else:
            print("⚪ 无法确定IP类型")
            return 'unknown'
    
    return None

def compare_apis():
    """对比本地和云端API响应"""
    print("\n=== API对比测试 ===")
    
    # 测试云端API
    print("测试云端API...")
    cloud_response = test_api_endpoint(CLOUD_API_URL, "/api/stream-links", 
                                     {"url": TEST_VIDEO_URL})
    cloud_ip_type = analyze_video_response(cloud_response, "云端")
    
    # 测试本地API
    print("\n测试本地API...")
    local_response = test_api_endpoint(LOCAL_API_URL, "/api/stream-links", 
                                     {"url": TEST_VIDEO_URL})
    local_ip_type = analyze_video_response(local_response, "本地")
    
    # 对比结果
    print("\n=== 对比结果 ===")
    if cloud_ip_type == 'ipv6' and local_ip_type == 'ipv4':
        print("🔴 问题确认: 云端API未使用IPv4修复，本地API已修复")
        return False
    elif cloud_ip_type == 'ipv4' and local_ip_type == 'ipv4':
        print("🟢 修复成功: 云端和本地API都使用IPv4")
        return True
    else:
        print(f"⚪ 状态不明确: 云端={cloud_ip_type}, 本地={local_ip_type}")
        return None

def check_deployment_status():
    """检查部署状态"""
    print("\n=== 部署状态检查 ===")
    
    # 检查API基本信息
    info = test_api_endpoint(CLOUD_API_URL, "/")
    if info:
        print(f"API版本: {info.get('version', 'unknown')}")
        print(f"API名称: {info.get('name', 'unknown')}")
    
    # 检查健康状态
    health = test_api_endpoint(CLOUD_API_URL, "/health")
    if health:
        print(f"健康状态: {health.get('status', 'unknown')}")
        print(f"时间戳: {health.get('timestamp', 'unknown')}")

def provide_solutions():
    """提供解决方案"""
    print("\n=== 解决方案 ===")
    print("1. 强制重新部署到Koyeb:")
    print("   - 在Koyeb控制台中手动触发重新部署")
    print("   - 或者推送一个新的提交来触发自动部署")
    
    print("\n2. 检查Koyeb配置:")
    print("   - 确认Koyeb连接到正确的GitHub分支(main)")
    print("   - 检查构建日志是否有错误")
    
    print("\n3. 验证环境变量:")
    print("   - 检查Koyeb是否设置了正确的环境变量")
    
    print("\n4. 创建新的部署提交:")
    print("   git commit --allow-empty -m 'Force redeploy with IPv4 fix'")
    print("   git push origin main")

def main():
    """主函数"""
    print(f"部署验证脚本 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 检查Git状态
    check_git_status()
    
    # 2. 检查部署状态
    check_deployment_status()
    
    # 3. 对比API响应
    is_fixed = compare_apis()
    
    # 4. 提供解决方案
    if is_fixed is False:
        provide_solutions()
        
        # 创建强制重新部署的提交
        print("\n=== 自动创建重新部署提交 ===")
        try:
            result = subprocess.run([
                'git', 'commit', '--allow-empty', 
                '-m', 'Force redeploy: Ensure IPv4 configuration is applied in cloud environment'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 创建空提交成功")
                print("现在推送到远程仓库...")
                
                push_result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                           capture_output=True, text=True)
                if push_result.returncode == 0:
                    print("✅ 推送成功，Koyeb应该会自动重新部署")
                    print("请等待几分钟后重新运行此脚本验证")
                else:
                    print(f"❌ 推送失败: {push_result.stderr}")
            else:
                print(f"❌ 创建提交失败: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 自动部署失败: {e}")
    
    elif is_fixed is True:
        print("\n🎉 云端API已成功应用IPv4修复！")
    
    else:
        print("\n⚠️  无法确定修复状态，请手动检查")

if __name__ == "__main__":
    main()