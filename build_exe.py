#!/usr/bin/env python3
"""
DeskTransfer 打包脚本
使用PyInstaller将应用程序打包成可执行文件
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装成功")
    except subprocess.CalledProcessError as e:
        print(f"安装PyInstaller失败: {e}")
        return False
    return True

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['sender.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('ui', 'ui'),
        ('common', 'common'),
    ],
    hiddenimports=[
        'tkinterdnd2',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DeskTransfer-Sender',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

# Receiver
b = Analysis(
    ['receiver.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),
        ('ui', 'ui'),
        ('common', 'common'),
    ],
    hiddenimports=[
        'tkinterdnd2',
        'PIL',
        'PIL._tkinter_finder',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz2 = PYZ(b.pure, b.zipped_data, cipher=block_cipher)

exe2 = EXE(
    pyz2,
    b.scripts,
    b.binaries,
    b.zipfiles,
    b.datas,
    [],
    name='DeskTransfer-Receiver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
"""
    
    with open('DeskTransfer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("已创建DeskTransfer.spec文件")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 检查spec文件是否存在
    if not os.path.exists('DeskTransfer.spec'):
        create_spec_file()
    
    try:
        # 运行PyInstaller
        subprocess.check_call([sys.executable, '-m', 'PyInstaller', '--clean', 'DeskTransfer.spec'])
        print("可执行文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建可执行文件失败: {e}")
        return False

def create_distribution():
    """创建发布包"""
    print("创建发布包...")
    
    # 创建发布目录
    dist_dir = Path('dist/DeskTransfer')
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制可执行文件
    if os.path.exists('dist/DeskTransfer-Sender.exe'):
        shutil.copy('dist/DeskTransfer-Sender.exe', dist_dir)
    if os.path.exists('dist/DeskTransfer-Receiver.exe'):
        shutil.copy('dist/DeskTransfer-Receiver.exe', dist_dir)
    
    # 复制必要的数据目录
    if os.path.exists('data'):
        shutil.copytree('data', dist_dir / 'data', dirs_exist_ok=True)
    
    # 创建启动脚本
    start_bat_content = """@echo off
chcp 65001 >nul
echo DeskTransfer - 局域网图片传输工具
echo.
echo 1. 启动接收端
echo 2. 启动发送端
echo 3. 退出
echo.
set /p choice=请选择操作 (1-3): 

if "%choice%"=="1" (
    echo 正在启动接收端...
    start "" "DeskTransfer-Receiver.exe"
) else if "%choice%"=="2" (
    echo 正在启动发送端...
    start "" "DeskTransfer-Sender.exe"
) else if "%choice%"=="3" (
    echo 退出程序
    exit
) else (
    echo 无效选择，请重新运行
    pause
)
"""
    
    with open(dist_dir / 'start.bat', 'w', encoding='utf-8') as f:
        f.write(start_bat_content)
    
    # 创建说明文件
    readme_content = """# DeskTransfer - 局域网图片传输工具

## 使用说明

1. 启动应用程序：
   - 双击运行 start.bat
   - 或者直接运行 DeskTransfer-Receiver.exe（接收端）或 DeskTransfer-Sender.exe（发送端）

2. 使用步骤：
   - 首先在接收端电脑上运行接收端程序，点击"启动服务器"
   - 然后在发送端电脑上运行发送端程序，输入接收端IP地址
   - 在发送端选择要发送的图片文件，点击"发送文件"

3. 接收的文件将保存在 data/received 目录下

## 注意事项

- 确保两台电脑在同一局域网内
- 确保防火墙允许程序通信（默认端口12345）
- 支持的图片格式：JPG、PNG、GIF、BMP、TIFF、WebP

## 技术支持

如有问题，请联系开发者。
"""
    
    with open(dist_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("发布包创建完成")
    print(f"发布包位置: {dist_dir.absolute()}")

def main():
    """主函数"""
    print("DeskTransfer 打包工具")
    print("====================")
    
    # 检查当前目录
    if not os.path.exists('sender.py') or not os.path.exists('receiver.py'):
        print("错误: 请在项目根目录运行此脚本")
        return 1
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return 1
    
    # 构建可执行文件
    if not build_executable():
        return 1
    
    # 创建发布包
    create_distribution()
    
    print("\n打包完成！")
    print("可执行文件位于 dist/DeskTransfer 目录")
    return 0

if __name__ == "__main__":
    sys.exit(main())