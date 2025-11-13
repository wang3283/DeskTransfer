#!/usr/bin/env python3
"""
GitHub Actions 诊断脚本
检查DeskTransfer项目的GitHub Actions配置
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n🔍 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 成功")
            return result.stdout.strip()
        else:
            print("❌ 失败")
            print(f"错误: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def check_git_status():
    """检查git状态"""
    print("=" * 60)
    print("📋 Git状态检查")
    print("=" * 60)

    # 检查远程仓库
    remote = run_command("git remote -v", "检查Git远程仓库配置")
    if remote and "github.com" in remote:
        print("✅ GitHub远程仓库已配置")
    else:
        print("❌ GitHub远程仓库未配置")
        return False

    # 检查分支状态
    status = run_command("git status", "检查Git分支状态")
    if status and "up to date" in status:
        print("✅ 本地分支与远程同步")
    else:
        print("⚠️  本地分支可能不同步")

    return True

def check_workflow_files():
    """检查工作流文件"""
    print("\n" + "=" * 60)
    print("🔧 工作流文件检查")
    print("=" * 60)

    workflow_path = Path(".github/workflows/build-windows.yml")

    if workflow_path.exists():
        print("✅ 工作流文件存在")
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查关键内容
        checks = [
            ("name: Build Windows Executables", "工作流名称"),
            ("runs-on: windows-latest", "运行环境"),
            ("workflow_dispatch:", "手动触发"),
            ("python build.py", "构建命令")
        ]

        for check, description in checks:
            if check in content:
                print(f"✅ {description}正确")
            else:
                print(f"❌ {description}缺失")

        return True
    else:
        print("❌ 工作流文件不存在")
        return False

def check_github_repo():
    """检查GitHub仓库状态"""
    print("\n" + "=" * 60)
    print("🌐 GitHub仓库检查")
    print("=" * 60)

    # 获取远程URL
    remote_url = run_command("git config --get remote.origin.url", "获取远程仓库URL")
    if remote_url:
        print(f"仓库地址: {remote_url}")

        if "wang3283" in remote_url and "DeskTransfer" in remote_url:
            print("✅ 仓库地址正确")
        else:
            print("⚠️  仓库地址可能有误")
    else:
        print("❌ 无法获取远程仓库地址")

def generate_troubleshooting_guide():
    """生成故障排除指南"""
    print("\n" + "=" * 60)
    print("🔧 故障排除指南")
    print("=" * 60)

    guide = """
如果仍然找不到"Build Windows Executables"，请按以下步骤操作：

1️⃣ 刷新GitHub页面
   - 按 Ctrl+F5 (Windows/Linux) 或 Cmd+Shift+R (Mac) 强制刷新
   - 或者清除浏览器缓存后重新访问

2️⃣ 检查Actions功能是否启用
   - 在仓库页面点击 "Actions" 标签
   - 如果看到提示框，点击 "I understand..." 启用Actions

3️⃣ 确认工作流文件存在
   - 访问: https://github.com/wang3283/DeskTransfer
   - 点击文件列表，查看是否有 .github/workflows/build-windows.yml

4️⃣ 手动触发工作流
   - 进入Actions页面
   - 点击左侧 "Build Windows Executables"
   - 如果看不到，点击右上角 "Run workflow" 下拉菜单

5️⃣ 检查仓库设置
   - 点击仓库右上角的 "Settings"
   - 确保仓库是 "Public" (公开)
   - 在 "Actions" -> "General" 中确认Actions已启用

6️⃣ 重新推送代码
   如果上述都不行，重新推送一次：
   git add .
   git commit -m "Update workflow"
   git push origin main

7️⃣ 联系GitHub支持
   如果还是不行，可以联系GitHub支持或创建新的仓库重新上传

🎯 常见问题：
• Actions功能对免费账户有每月2000分钟限制
• 私有仓库需要Pro计划才能使用Actions
• 某些地区可能需要VPN访问GitHub

"""

    print(guide)

def main():
    """主函数"""
    print("🚀 DeskTransfer GitHub Actions 诊断工具")
    print("检查你的项目配置是否正确")

    # 检查Git状态
    if not check_git_status():
        print("\n❌ Git配置有问题，请先解决Git问题")
        return

    # 检查工作流文件
    if not check_workflow_files():
        print("\n❌ 工作流文件有问题")
        return

    # 检查GitHub仓库
    check_github_repo()

    # 生成故障排除指南
    generate_troubleshooting_guide()

    print("\n" + "=" * 60)
    print("📝 总结")
    print("=" * 60)
    print("1. 代码已上传到GitHub")
    print("2. 工作流文件已配置")
    print("3. 如果找不到Actions，请按上面的故障排除指南操作")
    print("4. 或者直接访问: https://github.com/wang3283/DeskTransfer/actions")
    print("\n🎉 祝你成功获得Windows exe文件！")

if __name__ == "__main__":
    main()
