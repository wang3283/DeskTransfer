#!/usr/bin/env python3
"""
DeskTransfer 跨平台打包脚本
自动化构建独立的桌面可执行文件
支持Windows、macOS、Linux
"""
import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

class DeskTransferBuilder:
    def __init__(self):
        self.root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        self.dist_dir = self.root_dir / 'dist'
        self.build_dir = self.root_dir / 'build'
        self.output_dir = self.dist_dir / 'DeskTransfer'
        self.version = "1.0.0"

        # 检测平台
        import platform
        self.platform = platform.system().lower()
        self.arch = platform.machine().lower()

        # 设置平台特定的文件名后缀
        if self.platform == 'windows':
            self.exe_suffix = '.exe'
            self.script_suffix = '.bat'
        else:
            self.exe_suffix = ''
            self.script_suffix = '.sh'
        
    def log(self, message, level="INFO"):
        """打印日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_python(self):
        """检查Python环境"""
        self.log("检查Python环境...")
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
            self.log("需要Python 3.6或更高版本！", "ERROR")
            return False
        self.log(f"Python版本: {sys.version.split()[0]}")
        return True
        
    def install_dependencies(self):
        """安装打包依赖"""
        self.log("安装打包依赖...")
        try:
            # 升级pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 安装PyInstaller
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 安装项目依赖
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.log("依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"依赖安装失败: {e}", "ERROR")
            return False
            
    def clean_build(self):
        """清理之前的构建文件"""
        self.log("清理旧的构建文件...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.log("清理完成")
        
    def build_executables(self):
        """构建可执行文件"""
        self.log("开始构建可执行文件...")

        # 构建发送端
        if not self._build_single_executable('sender.py', 'DeskTransfer-Sender'):
            return False

        # 构建接收端
        if not self._build_single_executable('receiver.py', 'DeskTransfer-Receiver'):
            return False

        self.log("可执行文件构建成功")
        return True

    def _build_single_executable(self, script_file, exe_name):
        """构建单个可执行文件"""
        try:
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--clean',
                '--noconfirm',
                '--onedir',  # 生成目录而不是单文件
                '--name', exe_name,
                '--hidden-import', 'tkinterdnd2',
                '--hidden-import', 'tkinterdnd2.tkdnd',
                '--hidden-import', 'PIL',
                '--hidden-import', 'PIL._tkinter_finder',
                '--hidden-import', 'PIL.Image',
                '--hidden-import', 'PIL.ImageTk',
                '--hidden-import', 'psutil',
                '--hidden-import', 'socket',
                '--hidden-import', 'struct',
                '--hidden-import', 'threading',
                '--hidden-import', 'json',
                '--hidden-import', 'os',
                '--hidden-import', 'sys',
                '--hidden-import', 'time',
                '--hidden-import', 'datetime',
                '--hidden-import', 'hashlib',
                '--hidden-import', 'platform',
                '--hidden-import', 'subprocess',
                '--add-data', f'{self.root_dir}/data:data',
                '--exclude-module', 'matplotlib',
                '--exclude-module', 'numpy',
                '--exclude-module', 'scipy',
                '--exclude-module', 'pandas',
                '--exclude-module', 'pytest',
                '--exclude-module', 'setuptools',
                '--exclude-module', 'unittest',
                '--exclude-module', 'doctest',
                '--exclude-module', 'pydoc',
                '--noupx',  # 禁用UPX压缩以提高兼容性
                '--noconsole',  # GUI应用，不显示控制台窗口
                script_file
            ]

            # 添加平台特定的选项
            if self.platform == 'windows':
                if (self.root_dir / 'assets' / 'icon.ico').exists():
                    cmd.extend(['--icon', str(self.root_dir / 'assets' / 'icon.ico')])

            subprocess.check_call(cmd, cwd=str(self.root_dir))
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"构建 {exe_name} 失败: {e}", "ERROR")
            return False
            
    def create_distribution_package(self):
        """创建发布包"""
        self.log("创建发布包...")
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查新格式的输出（COLLECT模式）
        sender_dir = self.dist_dir / 'DeskTransfer-Sender'
        receiver_dir = self.dist_dir / 'DeskTransfer-Receiver'
        
        # 复制发送端文件
        if sender_dir.exists():
            self.log("复制发送端文件...")
            for item in sender_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, self.output_dir)
                    if item.suffix == '.exe':
                        self.log(f"复制: {item.name}")
                elif item.is_dir():
                    shutil.copytree(item, self.output_dir / item.name, dirs_exist_ok=True)
        else:
            # 兼容旧格式（单文件exe）
            sender_exe = self.dist_dir / 'DeskTransfer-Sender.exe'
            if sender_exe.exists():
                shutil.copy(sender_exe, self.output_dir)
                self.log(f"复制: {sender_exe.name}")
            else:
                self.log("警告: 未找到发送端可执行文件", "WARNING")
        
        # 复制接收端文件
        if receiver_dir.exists():
            self.log("复制接收端文件...")
            for item in receiver_dir.iterdir():
                if item.is_file():
                    dest_file = self.output_dir / item.name
                    if not dest_file.exists():  # 避免覆盖已有文件
                        shutil.copy2(item, self.output_dir)
                    if item.suffix == '.exe':
                        self.log(f"复制: {item.name}")
                elif item.is_dir():
                    shutil.copytree(item, self.output_dir / item.name, dirs_exist_ok=True)
        else:
            # 兼容旧格式（单文件exe）
            receiver_exe = self.dist_dir / 'DeskTransfer-Receiver.exe'
            if receiver_exe.exists():
                shutil.copy(receiver_exe, self.output_dir)
                self.log(f"复制: {receiver_exe.name}")
            else:
                self.log("警告: 未找到接收端可执行文件", "WARNING")
        
        # 创建data目录
        data_dir = self.output_dir / 'data'
        data_dir.mkdir(exist_ok=True)
        (data_dir / 'received').mkdir(exist_ok=True)
        (data_dir / 'temp').mkdir(exist_ok=True)
        
        # 创建启动脚本
        self.create_start_script()
        
        # 创建README文件
        self.create_readme()
        
        # 复制文档
        self.copy_documentation()
        
        self.log("发布包创建完成")
        
    def create_start_script(self):
        """创建启动脚本"""
        if self.platform == 'windows':
            start_content = self._create_windows_start_script()
        else:
            start_content = self._create_unix_start_script()

        start_script_path = self.output_dir / f'start{self.script_suffix}'
        with open(start_script_path, 'w', encoding='utf-8') as f:
            f.write(start_content)
        self.log(f"创建启动脚本: start{self.script_suffix}")

    def _create_windows_start_script(self):
        """创建Windows批处理启动脚本"""
        return """@echo off
chcp 65001 >nul
title DeskTransfer - 局域网图片传输工具
color 0A

:menu
cls
echo ========================================
echo    DeskTransfer v1.0.0
echo    局域网图片传输工具
echo ========================================
echo.
echo    1. 启动接收端 (Receiver)
echo    2. 启动发送端 (Sender)
echo    3. 打开接收文件夹
echo    4. 查看使用说明
echo    5. 退出
echo.
echo ========================================

set /p choice=请选择操作 (1-5):

if "%choice%"=="1" (
    echo.
    echo 正在启动接收端...
    start "" "DeskTransfer-Receiver.exe"
    timeout /t 2 >nul
    goto menu
) else if "%choice%"=="2" (
    echo.
    echo 正在启动发送端...
    start "" "DeskTransfer-Sender.exe"
    timeout /t 2 >nul
    goto menu
) else if "%choice%"=="3" (
    echo.
    echo 正在打开接收文件夹...
    if exist "data\\received" (
        explorer "data\\received"
    ) else (
        echo 接收文件夹不存在，正在创建...
        mkdir "data\\received"
        explorer "data\\received"
    )
    timeout /t 2 >nul
    goto menu
) else if "%choice%"=="4" (
    if exist "README.txt" (
        notepad "README.txt"
    ) else if exist "使用说明.txt" (
        notepad "使用说明.txt"
    ) else (
        echo 未找到使用说明文件
        pause
    )
    goto menu
) else if "%choice%"=="5" (
    echo.
    echo 谢谢使用！
    timeout /t 1 >nul
    exit
) else (
    echo.
    echo 无效选择，请重新选择！
    timeout /t 2 >nul
    goto menu
)
"""

    def _create_unix_start_script(self):
        """创建Unix shell启动脚本"""
        return """#!/bin/bash

# DeskTransfer 启动脚本
# 支持macOS和Linux

show_menu() {
    clear
    echo "========================================"
    echo "    DeskTransfer v1.0.0"
    echo "    局域网图片传输工具"
    echo "========================================"
    echo ""
    echo "    1. 启动接收端 (Receiver)"
    echo "    2. 启动发送端 (Sender)"
    echo "    3. 打开接收文件夹"
    echo "    4. 查看使用说明"
    echo "    5. 退出"
    echo ""
    echo "========================================"
}

# 创建接收文件夹（如果不存在）
ensure_received_dir() {
    if [ ! -d "data/received" ]; then
        mkdir -p "data/received"
        echo "接收文件夹已创建"
    fi
}

# 主菜单循环
while true; do
    show_menu
    read -p "请选择操作 (1-5): " choice

    case $choice in
        1)
            echo ""
            echo "正在启动接收端..."
            if [ -f "./DeskTransfer-Receiver" ]; then
                ./DeskTransfer-Receiver &
            else
                echo "错误：找不到接收端可执行文件"
                read -p "按回车键继续..."
            fi
            ;;
        2)
            echo ""
            echo "正在启动发送端..."
            if [ -f "./DeskTransfer-Sender" ]; then
                ./DeskTransfer-Sender &
            else
                echo "错误：找不到发送端可执行文件"
                read -p "按回车键继续..."
            fi
            ;;
        3)
            echo ""
            echo "正在打开接收文件夹..."
            ensure_received_dir
            if command -v open >/dev/null 2>&1; then
                # macOS
                open "data/received"
            elif command -v xdg-open >/dev/null 2>&1; then
                # Linux
                xdg-open "data/received"
            else
                echo "无法自动打开文件夹，请手动打开 data/received 目录"
                read -p "按回车键继续..."
            fi
            ;;
        4)
            if [ -f "README.txt" ]; then
                if command -v open >/dev/null 2>&1; then
                    open "README.txt"
                elif command -v xdg-open >/dev/null 2>&1; then
                    xdg-open "README.txt"
                else
                    cat "README.txt" | less
                fi
            elif [ -f "使用说明.txt" ]; then
                if command -v open >/dev/null 2>&1; then
                    open "使用说明.txt"
                elif command -v xdg-open >/dev/null 2>&1; then
                    xdg-open "使用说明.txt"
                else
                    cat "使用说明.txt" | less
                fi
            else
                echo "未找到使用说明文件"
                read -p "按回车键继续..."
            fi
            ;;
        5)
            echo ""
            echo "谢谢使用！"
            exit 0
            ;;
        *)
            echo ""
            echo "无效选择，请重新选择！"
            read -p "按回车键继续..."
            ;;
    esac
done
"""
        
    def create_readme(self):
        """创建README文件"""
        readme_content = """# DeskTransfer - 局域网图片传输工具

## 版本信息
版本: v1.0.0
发布日期: """ + datetime.now().strftime("%Y-%m-%d") + """

## 快速开始

### 方式一：使用启动脚本（推荐）
1. 双击运行 `start.bat`
2. 根据菜单选择：
   - 选择 1 启动接收端
   - 选择 2 启动发送端
   - 选择 3 打开接收文件夹
   - 选择 4 查看使用说明

### 方式二：直接运行
1. 双击 `DeskTransfer-Receiver.exe` 启动接收端
2. 双击 `DeskTransfer-Sender.exe` 启动发送端

## 使用步骤

### 1. 启动接收端
- 在接收端电脑上运行接收端程序
- 点击"启动服务器"按钮
- 记录显示的IP地址和端口号（默认：12345）

### 2. 启动发送端
- 在发送端电脑上运行发送端程序
- 输入接收端的IP地址
- 端口号保持默认（12345）或输入接收端显示的端口

### 3. 传输文件
- 在发送端点击"选择文件"按钮，选择要传输的图片
- 支持多选，可以批量传输
- 点击"连接"按钮连接到接收端
- 连接成功后，点击"发送文件"开始传输
- 传输过程中会显示进度条

### 4. 查看接收的文件
- 接收的文件保存在 `data/received` 目录
- 可以在接收端界面点击"打开接收文件夹"按钮
- 或使用启动脚本的菜单选项3

## 功能特点

- ✅ 支持局域网内快速传输图片
- ✅ 支持批量选择和传输
- ✅ 实时显示传输进度
- ✅ 支持常见图片格式（JPG、PNG、GIF、BMP、TIFF、WebP）
- ✅ 简洁易用的图形界面
- ✅ 无需安装Python环境

## 系统要求

- 操作系统: Windows 7 或更高版本
- 网络: 发送端和接收端需在同一局域网内
- 防火墙: 需允许TCP端口12345通信

## 注意事项

1. **网络连接**
   - 确保两台电脑在同一局域网内
   - 可以通过ping命令测试网络连通性

2. **防火墙设置**
   - Windows防火墙可能会阻止连接
   - 首次运行时，请允许程序通过防火墙
   - 默认使用TCP端口12345

3. **文件路径**
   - 不要移动或删除exe文件所在目录的其他文件
   - data目录用于存储接收的文件

4. **杀毒软件**
   - 某些杀毒软件可能会误报
   - 如遇此问题，请将程序添加到白名单

## 故障排除

### 问题：无法连接到接收端
解决方法：
1. 检查两台电脑是否在同一局域网内
2. 确认接收端服务器已启动
3. 检查IP地址和端口是否正确
4. 检查防火墙设置

### 问题：传输中断
解决方法：
1. 检查网络连接是否稳定
2. 重新启动程序并重试
3. 确保没有其他程序占用端口12345

### 问题：程序无法启动
解决方法：
1. 确认Windows版本（需Windows 7或更高）
2. 以管理员权限运行
3. 安装Visual C++ Redistributable

## 技术支持

如有问题或建议，请联系开发者。

## 版权信息

Copyright © 2024 DeskTransfer
本软件仅供学习和个人使用。
"""
        
        readme_path = self.output_dir / 'README.txt'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        self.log("创建README文件")
        
    def copy_documentation(self):
        """复制文档文件"""
        docs = ['使用指南.md', 'USAGE.md']
        for doc in docs:
            doc_path = self.root_dir / doc
            if doc_path.exists():
                shutil.copy(doc_path, self.output_dir)
                self.log(f"复制文档: {doc}")
                
    def create_portable_zip(self):
        """创建便携版ZIP包"""
        self.log("创建便携版ZIP包...")
        
        zip_name = f'DeskTransfer_v{self.version}_Portable.zip'
        zip_path = self.dist_dir / zip_name
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.output_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.output_dir.parent)
                        zipf.write(file_path, arcname)
                        
            file_size = zip_path.stat().st_size / (1024 * 1024)  # MB
            self.log(f"ZIP包创建成功: {zip_name} ({file_size:.2f} MB)")
            return True
        except Exception as e:
            self.log(f"创建ZIP包失败: {e}", "ERROR")
            return False
            
    def create_installer_script(self):
        """创建Inno Setup安装程序脚本"""
        self.log("创建安装程序脚本...")
        
        iss_content = f"""[Setup]
AppName=DeskTransfer
AppVersion={self.version}
AppPublisher=DeskTransfer
DefaultDirName={{autopf}}\\DeskTransfer
DefaultGroupName=DeskTransfer
OutputDir=..\\..
OutputBaseFilename=DeskTransfer_v{self.version}_Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={{app}}\\DeskTransfer-Sender.exe
WizardStyle=modern

[Languages]
Name: "chinese"; MessagesFile: "compiler:Languages\\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "DeskTransfer\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\DeskTransfer - 发送端"; Filename: "{{app}}\\DeskTransfer-Sender.exe"
Name: "{{group}}\\DeskTransfer - 接收端"; Filename: "{{app}}\\DeskTransfer-Receiver.exe"
Name: "{{group}}\\启动菜单"; Filename: "{{app}}\\start.bat"
Name: "{{group}}\\接收文件夹"; Filename: "{{app}}\\data\\received"
Name: "{{desktopicon}}\\DeskTransfer"; Filename: "{{app}}\\start.bat"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\start.bat"; Description: "{{cm:LaunchProgram,DeskTransfer}}"; Flags: shellexec postinstall skipifsilent
"""
        
        iss_path = self.output_dir / 'installer.iss'
        with open(iss_path, 'w', encoding='utf-8') as f:
            f.write(iss_content)
        self.log("安装程序脚本创建成功: installer.iss")
        self.log("提示: 使用Inno Setup编译此脚本可生成安装程序")
        
    def print_summary(self):
        """打印构建摘要"""
        print("\n" + "=" * 60)
        print("构建完成摘要".center(60))
        print("=" * 60)
        
        print(f"\n发布包位置: {self.output_dir}")
        print("\n包含文件:")
        
        sender_name = f"DeskTransfer-Sender{self.exe_suffix}"
        receiver_name = f"DeskTransfer-Receiver{self.exe_suffix}"
        start_name = f"start{self.script_suffix}"

        files = [
            (sender_name, "发送端可执行文件"),
            (receiver_name, "接收端可执行文件"),
            (start_name, "启动菜单脚本"),
            ("README.txt", "使用说明"),
            ("data/", "数据目录"),
        ]
        
        for filename, description in files:
            file_path = self.output_dir / filename
            if file_path.exists():
                print(f"  ✓ {filename:<30} - {description}")
            else:
                print(f"  ✗ {filename:<30} - {description} (缺失)")
        
        # 检查ZIP包
        zip_name = f'DeskTransfer_v{self.version}_Portable.zip'
        zip_path = self.dist_dir / zip_name
        if zip_path.exists():
            file_size = zip_path.stat().st_size / (1024 * 1024)
            print(f"\n便携版ZIP: {zip_name} ({file_size:.2f} MB)")
        
        print("\n" + "=" * 60)
        print("\n下一步:")
        print("  1. 测试可执行文件是否正常运行")
        if self.platform == "windows":
            print("  2. 将整个DeskTransfer目录复制到其他Windows电脑使用")
            print(f"  3. 或使用便携版ZIP包: {zip_name}")
            print("  4. 使用Inno Setup编译installer.iss创建安装程序")
        else:
            platform_name = "macOS" if self.platform == "darwin" else self.platform.title()
            print(f"  2. 将整个DeskTransfer目录复制到其他{platform_name}电脑使用")
            print(f"  3. 或使用便携版ZIP包: {zip_name}")
            print("  4. 在其他平台上重新构建以获得对应版本")
        print("=" * 60 + "\n")
        
    def build(self):
        """执行完整的构建流程"""
        print("\n" + "=" * 60)
        platform_name = "Windows" if self.platform == "windows" else ("macOS" if self.platform == "darwin" else self.platform.title())
        print(f"DeskTransfer {platform_name}构建工具".center(60))
        print("=" * 60 + "\n")
        
        # 检查Python环境
        if not self.check_python():
            return 1
            
        # 安装依赖
        if not self.install_dependencies():
            return 1
            
        # 清理旧文件
        self.clean_build()
        
        # 构建可执行文件
        if not self.build_executables():
            return 1
            
        # 创建发布包
        self.create_distribution_package()
        
        # 创建ZIP包
        self.create_portable_zip()
        
        # 创建安装程序脚本
        self.create_installer_script()
        
        # 打印摘要
        self.print_summary()
        
        return 0

def main():
    """主函数"""
    builder = DeskTransferBuilder()
    return builder.build()

if __name__ == "__main__":
    sys.exit(main())
