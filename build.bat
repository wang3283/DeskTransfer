@echo off
chcp 65001 >nul
title DeskTransfer 打包工具

echo ========================================
echo    DeskTransfer 打包工具
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请先安装Python 3.6或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 显示Python版本
echo 检测到的Python版本:
python --version
echo.

:: 检查pip是否可用
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: pip不可用，请确保Python安装正确
    pause
    exit /b 1
)

:: 安装依赖
echo 正在安装必要的依赖包...
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install -r requirements.txt
echo.

:: 创建assets目录（如果不存在）
if not exist "assets" mkdir assets

:: 清理之前的构建
echo 清理之前的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del *.spec
echo.

:: 开始打包
echo 开始打包应用程序...
python build_exe.py
if %errorlevel% neq 0 (
    echo.
    echo 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo           打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\DeskTransfer\
echo.
echo 包含以下文件:
if exist "dist\DeskTransfer\DeskTransfer-Sender.exe" echo   - DeskTransfer-Sender.exe (发送端)
if exist "dist\DeskTransfer\DeskTransfer-Receiver.exe" echo   - DeskTransfer-Receiver.exe (接收端)
if exist "dist\DeskTransfer\start.bat" echo   - start.bat (启动脚本)
if exist "dist\DeskTransfer\README.txt" echo   - README.txt (使用说明)
echo.

:: 询问是否打开输出目录
set /p open_folder=是否打开输出目录? (Y/N): 
if /i "%open_folder%"=="Y" (
    explorer "dist\DeskTransfer"
)

echo.
echo 打包完成！您可以将dist\DeskTransfer目录复制到其他Windows计算机上使用。
echo.
pause