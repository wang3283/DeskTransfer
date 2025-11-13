@echo off
chcp 65001 >nul
title DeskTransfer 一键打包工具
color 0B

echo ========================================
echo    DeskTransfer 一键打包工具
echo ========================================
echo.
echo 本工具将自动完成以下操作:
echo   1. 检查Python环境
echo   2. 安装必要依赖
echo   3. 清理旧的构建文件
echo   4. 使用PyInstaller打包程序
echo   5. 创建便携版ZIP包
echo   6. 生成安装程序脚本
echo.
echo 打包完成后，可执行文件将位于:
echo   dist\DeskTransfer\
echo.
echo ========================================
echo.

:: 暂停等待用户确认
set /p confirm=按任意键开始打包，或按Ctrl+C取消...

echo.
echo 开始打包，请稍候...
echo.

:: 运行Python打包脚本
python build_windows.py

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   打包失败！请检查上面的错误信息
    echo ========================================
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo         打包成功完成！
echo ========================================
echo.

:: 询问是否打开输出目录
set /p open_folder=是否打开输出目录? (Y/N): 
if /i "%open_folder%"=="Y" (
    explorer "dist\DeskTransfer"
)

echo.
echo 感谢使用DeskTransfer打包工具！
echo.
pause
