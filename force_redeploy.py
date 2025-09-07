#!/usr/bin/env python3
"""
强制重新部署脚本
用于触发Koyeb重新部署，确保IPv4配置生效
"""

import subprocess
import sys
from datetime import datetime

def run_command(cmd, description):
    """执行命令并处理结果"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description}成功")
        if result.stdout.strip():
            print(f"输出: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        if e.stderr:
            print(f"错误: {e.stderr.strip()}")
        return False

def check_git_status():
    """检查Git状态"""
    print("\n📋 检查Git状态...")
    try:
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  发现未提交的更改:")
            print(result.stdout)
            return False
        else:
            print("✅ 工作目录干净")
            return True
    except Exception as e:
        print(f"❌ 检查Git状态失败: {e}")
        return False

def force_redeploy():
    """执行强制重新部署"""
    print("🚀 开始强制重新部署流程...")
    
    # 检查Git状态
    if not check_git_status():
        print("\n⚠️  请先提交或暂存未完成的更改")
        return False
    
    # 创建时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    commit_message = f"Force redeploy to ensure IPv4 configuration takes effect - {timestamp}"
    
    # 执行强制重新部署步骤
    steps = [
        ("git add .", "添加所有文件到暂存区"),
        (f'git commit --allow-empty -m "{commit_message}"', "创建空提交"),
        ("git push origin main", "推送到远程仓库")
    ]
    
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            print(f"\n❌ 部署流程在'{desc}'步骤失败")
            return False
    
    print("\n🎉 强制重新部署完成!")
    print("\n📝 后续步骤:")
    print("1. 等待Koyeb重新部署完成（通常需要2-5分钟）")
    print("2. 访问 https://app.koyeb.com 查看部署状态")
    print("3. 部署完成后重新测试API确认IPv4配置是否生效")
    print("4. 运行: python3 test_api_fix.py 验证修复效果")
    
    return True

def verify_deployment():
    """验证部署配置"""
    print("\n🔍 验证当前配置...")
    
    # 检查本地IPv4配置
    try:
        with open('yt_dlp_api.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if "'force_ipv4': True" in content:
                print("✅ 本地代码包含IPv4强制配置")
            else:
                print("❌ 本地代码缺少IPv4强制配置")
                return False
    except FileNotFoundError:
        print("❌ 找不到yt_dlp_api.py文件")
        return False
    
    # 检查Git远程仓库
    try:
        result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
        if "github.com" in result.stdout:
            print("✅ GitHub远程仓库已配置")
        else:
            print("❌ 未找到GitHub远程仓库")
            return False
    except Exception as e:
        print(f"❌ 检查远程仓库失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 Koyeb强制重新部署工具")
    print("=" * 60)
    
    # 验证配置
    if not verify_deployment():
        print("\n❌ 配置验证失败，请检查配置后重试")
        sys.exit(1)
    
    # 询问用户确认
    print("\n⚠️  此操作将创建空提交并推送到GitHub，触发Koyeb重新部署")
    confirm = input("是否继续？(y/N): ").lower().strip()
    
    if confirm != 'y':
        print("❌ 操作已取消")
        sys.exit(0)
    
    # 执行强制重新部署
    if force_redeploy():
        print("\n🎯 建议测试命令:")
        print("curl -X POST \"https://yt-dlp-api-miaomiaocompany-3d8d2eee.koyeb.app/api/playable-links\" -H \"Content-Type: application/json\" -d '{\"url\": \"https://www.youtube.com/watch?v=rQe1-bmQ6PI\"}'")
        sys.exit(0)
    else:
        print("\n❌ 强制重新部署失败")
        sys.exit(1)

if __name__ == "__main__":
    main()