@echo off
chcp 65001 >nul

echo DeskTransfer - 局域网图片传输软件
echo ==================================
echo 1. 启动接收端
echo 2. 启动发送端
echo 3. 退出
echo ==================================

set /p choice=请选择 (1-3): 

if "%choice%"=="1" (
    echo 正在启动接收端...
    python receiver.py
) else if "%choice%"=="2" (
    echo 正在启动发送端...
    python sender.py
) else if "%choice%"=="3" (
    echo 退出程序
    exit /b 0
) else (
    echo 无效选择，请重新运行脚本
    pause
    exit /b 1
)