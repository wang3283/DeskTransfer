#!/usr/bin/env python3
"""
打包验证脚本
用于检查打包结果是否完整
"""
import os
import sys
from pathlib import Path

def check_file(file_path, description):
    """检查文件是否存在"""
    if file_path.exists():
        size = file_path.stat().st_size
        size_mb = size / (1024 * 1024)
        print(f"  ✓ {description:<35} ({size_mb:.2f} MB)")
        return True
    else:
        print(f"  ✗ {description:<35} (缺失)")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("DeskTransfer 打包验证工具")
    print("=" * 60)
    print()
    
    root_dir = Path(__file__).parent
    dist_dir = root_dir / 'dist' / 'DeskTransfer'
    
    if not dist_dir.exists():
        print("❌ 错误: dist/DeskTransfer 目录不存在")
        print("   请先运行打包脚本!")
        print()
        print("   运行: 一键打包.bat")
        print("   或: python build_windows.py")
        return 1
    
    print(f"检查目录: {dist_dir}")
    print()
    
    # 必需文件列表
    required_files = [
        ('DeskTransfer-Sender.exe', '发送端可执行文件'),
        ('DeskTransfer-Receiver.exe', '接收端可执行文件'),
        ('start.bat', '启动脚本'),
        ('README.txt', '使用说明'),
    ]
    
    # 可选文件列表
    optional_files = [
        ('使用指南.md', '详细使用指南'),
        ('USAGE.md', '使用文档'),
        ('installer.iss', '安装程序脚本'),
    ]
    
    # 必需目录列表
    required_dirs = [
        ('data', '数据目录'),
        ('data/received', '接收文件目录'),
        ('data/temp', '临时文件目录'),
    ]
    
    print("检查必需文件:")
    print("-" * 60)
    missing_required = 0
    for filename, description in required_files:
        if not check_file(dist_dir / filename, description):
            missing_required += 1
    
    print()
    print("检查可选文件:")
    print("-" * 60)
    for filename, description in optional_files:
        check_file(dist_dir / filename, description)
    
    print()
    print("检查目录结构:")
    print("-" * 60)
    missing_dirs = 0
    for dirname, description in required_dirs:
        dir_path = dist_dir / dirname
        if dir_path.exists():
            print(f"  ✓ {description:<35}")
        else:
            print(f"  ✗ {description:<35} (缺失)")
            missing_dirs += 1
    
    print()
    print("检查便携版ZIP包:")
    print("-" * 60)
    zip_files = list((root_dir / 'dist').glob('DeskTransfer_*_Portable.zip'))
    if zip_files:
        for zip_file in zip_files:
            size_mb = zip_file.stat().st_size / (1024 * 1024)
            print(f"  ✓ {zip_file.name} ({size_mb:.2f} MB)")
    else:
        print(f"  ✗ 未找到便携版ZIP包")
    
    print()
    print("=" * 60)
    
    if missing_required == 0 and missing_dirs == 0:
        print("✅ 打包验证通过！所有必需文件都存在。")
        print()
        print("下一步:")
        print("  1. 测试运行 DeskTransfer-Sender.exe")
        print("  2. 测试运行 DeskTransfer-Receiver.exe")
        print("  3. 测试传输功能")
        print("  4. 分发给用户使用")
    else:
        print("❌ 打包验证失败！")
        if missing_required > 0:
            print(f"   缺少 {missing_required} 个必需文件")
        if missing_dirs > 0:
            print(f"   缺少 {missing_dirs} 个必需目录")
        print()
        print("请重新运行打包脚本")
    
    print("=" * 60)
    print()
    
    return 0 if (missing_required == 0 and missing_dirs == 0) else 1

if __name__ == "__main__":
    sys.exit(main())
