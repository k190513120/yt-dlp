#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Koyeb IPv4强制部署脚本
用于确保IPv4配置在Koyeb云端生效
"""

import subprocess
import sys
import time
import requests
from datetime import datetime

# 配置
KOYEB_API_URL = "https://yt-dlp-api-bytedance.koyeb.app"  # 替换为你的Koyeb应用URL
TEST_YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def run_command(cmd, description):
    """执行命令并返回结果"""
    print(f"\n🔧 {description}")
    print(f"执行命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ 成功: {result.stdout.strip()}")
            return True, result.stdout
        else:
            print(f"❌ 失败: {result.stderr.strip()}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print("❌ 命令执行超时")
        return False, "超时"
    except Exception as e:
        print(f"❌ 执行错误: {str(e)}")
        return False, str(e)

def check_git_status():
    """检查Git状态"""
    print("\n=== 检查Git状态 ===")
    
    # 检查是否有未提交的更改
    success, output = run_command("git status --porcelain", "检查未提交的更改")
    if success and output.strip():
        print("📝 发现未提交的更改:")
        print(output)
        return False
    
    # 检查当前分支
    success, branch = run_command("git branch --show-current", "获取当前分支")
    if success:
        print(f"📍 当前分支: {branch.strip()}")
    
    return True

def commit_and_push_changes():
    """提交并推送更改"""
    print("\n=== 提交并推送更改 ===")
    
    # 添加所有更改
    success, _ = run_command("git add .", "添加所有更改到暂存区")
    if not success:
        return False
    
    # 提交更改
    commit_msg = f"Update Koyeb config for IPv4 support - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    success, _ = run_command(f'git commit -m "{commit_msg}"', "提交更改")
    if not success:
        print("ℹ️ 可能没有新的更改需要提交")
    
    # 推送到远程仓库
    success, _ = run_command("git push origin main", "推送到远程仓库")
    return success

def wait_for_deployment(max_wait_minutes=10):
    """等待部署完成"""
    print(f"\n⏳ 等待Koyeb部署完成 (最多{max_wait_minutes}分钟)...")
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while time.time() - start_time < max_wait_seconds:
        try:
            response = requests.get(f"{KOYEB_API_URL}/health", timeout=10)
            if response.status_code == 200:
                print("✅ 部署完成，API健康检查通过")
                return True
        except requests.RequestException:
            pass
        
        print("⏳ 等待中...", end="\r")
        time.sleep(30)
    
    print(f"\n⚠️ 等待超时({max_wait_minutes}分钟)，请手动检查部署状态")
    return False

def test_ipv4_configuration():
    """测试IPv4配置是否生效"""
    print("\n=== 测试IPv4配置 ===")
    
    try:
        # 测试API基本功能
        print("🔍 测试API基本功能...")
        response = requests.get(f"{KOYEB_API_URL}/api/info", timeout=30)
        if response.status_code != 200:
            print(f"❌ API基本功能测试失败: {response.status_code}")
            return False
        
        print("✅ API基本功能正常")
        
        # 测试playable-links端点
        print("🔍 测试playable-links端点...")
        data = {"url": TEST_YOUTUBE_URL}
        response = requests.post(f"{KOYEB_API_URL}/api/playable-links", json=data, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ playable-links测试失败: {response.status_code}")
            return False
        
        result = response.json()
        original_url = result.get('original_url', '')
        
        # 检查是否包含IPv6地址
        if '::' in original_url or '2001:' in original_url or '2605:' in original_url:
            print(f"❌ 仍在使用IPv6地址: {original_url}")
            print("💡 建议检查Koyeb环境变量配置")
            return False
        else:
            print(f"✅ IPv4配置生效: {original_url}")
            return True
            
    except requests.RequestException as e:
        print(f"❌ 网络请求失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 测试过程出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Koyeb IPv4强制部署脚本")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查Git状态
    if not check_git_status():
        print("\n❌ Git状态检查失败，请先处理未提交的更改")
        return False
    
    # 2. 提交并推送更改
    if not commit_and_push_changes():
        print("\n❌ 代码推送失败")
        return False
    
    # 3. 等待部署完成
    if not wait_for_deployment():
        print("\n⚠️ 部署等待超时，继续进行测试")
    
    # 4. 测试IPv4配置
    if test_ipv4_configuration():
        print("\n🎉 IPv4配置部署成功！")
        return True
    else:
        print("\n❌ IPv4配置未生效，需要进一步检查")
        print("\n📋 建议检查项目:")
        print("1. Koyeb控制台中的环境变量设置")
        print("2. 构建日志是否有错误")
        print("3. 服务是否正确重启")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)