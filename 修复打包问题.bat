@echo off
chcp 65001 >nul
title DeskTransfer 打包问题修复工具
color 0E

echo ========================================
echo    DeskTransfer 打包问题修复工具
echo ========================================
echo.
echo 本工具将尝试解决常见的打包问题
echo.

:: 显示Python版本
echo [检查1] Python环境
python --version
if %errorlevel% neq 0 (
    echo ❌ 错误: 未检测到Python
    echo 请先安装Python 3.8-3.12版本（推荐3.11）
    pause
    exit /b 1
)
echo ✓ Python已安装
echo.

:: 检查PyInstaller版本
echo [检查2] PyInstaller版本
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller未安装，正在安装...
    python -m pip install pyinstaller
) else (
    echo PyInstaller已安装，正在升级到最新版本...
    python -m pip install --upgrade pyinstaller
)
echo.

:: 显示PyInstaller版本
python -m pip show pyinstaller | findstr "Version"
echo.

:: 检查项目依赖
echo [检查3] 项目依赖
echo 正在安装/更新项目依赖...
python -m pip install --upgrade -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✓ 依赖安装成功
echo.

:: 清理旧文件
echo [步骤1] 清理旧的构建文件
if exist "build" (
    echo 删除 build 目录...
    rmdir /s /q build
)
if exist "dist" (
    echo 删除 dist 目录...
    rmdir /s /q dist
)
if exist "__pycache__" (
    rmdir /s /q __pycache__
)
if exist "ui\__pycache__" (
    rmdir /s /q ui\__pycache__
)
if exist "common\__pycache__" (
    rmdir /s /q common\__pycache__
)
echo ✓ 清理完成
echo.

:: 选择打包方式
echo [步骤2] 选择打包方式
echo.
echo 1. 使用标准配置（推荐）
echo 2. 使用简化配置（如果标准配置失败）
echo 3. 取消
echo.
set /p choice=请选择 (1-3): 

if "%choice%"=="1" (
    echo.
    echo 使用标准配置: DeskTransfer.spec
    echo 正在打包...
    python -m PyInstaller --clean --noconfirm DeskTransfer.spec
    goto check_result
) else if "%choice%"=="2" (
    echo.
    echo 使用简化配置: DeskTransfer-Simple.spec
    echo 正在打包...
    python -m PyInstaller --clean --noconfirm DeskTransfer-Simple.spec
    goto check_result
) else if "%choice%"=="3" (
    echo 取消操作
    pause
    exit /b 0
) else (
    echo 无效选择
    pause
    exit /b 1
)

:check_result
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   打包失败！
    echo ========================================
    echo.
    echo 可能的解决方法:
    echo 1. 检查错误信息中提到的缺失模块
    echo 2. 尝试使用简化配置（选择2）
    echo 3. 降级Python版本到3.11（当前可能版本太新）
    echo 4. 查看 打包问题排查.txt 获取更多帮助
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo        打包成功！
echo ========================================
echo.

:: 检查输出文件
echo 正在验证输出文件...
python 验证打包.py

echo.
echo ========================================
echo.
echo 打包完成！可执行文件位于:
if exist "dist\DeskTransfer" (
    echo   dist\DeskTransfer\
) else if exist "dist\DeskTransfer-Sender" (
    echo   dist\ 目录（需要整理到DeskTransfer目录）
    echo.
    echo 正在整理文件...
    python build_windows.py
)
echo.
echo ========================================
echo.

:: 询问是否打开目录
set /p open_folder=是否打开输出目录? (Y/N): 
if /i "%open_folder%"=="Y" (
    if exist "dist\DeskTransfer" (
        explorer "dist\DeskTransfer"
    ) else (
        explorer "dist"
    )
)

echo.
pause
