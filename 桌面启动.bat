@echo off
title 提示词注入工具
echo ================================================
echo           提示词注入工具
echo ================================================
echo.

REM 设置UTF-8编码支持中文
chcp 65001 >nul

REM 切换到脚本所在目录
cd /d "%~dp0"

echo [启动] 工具目录: %CD%
echo.

REM 检查主程序文件
if not exist "main.py" (
    echo [错误] 未找到main.py文件
    echo 请确保将此启动文件放在项目根目录
    echo.
    pause
    exit /b 1
)

REM 快速检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python环境
    echo 请安装Python 3.8+并添加到PATH环境变量
    echo 下载地址: https://python.org
    echo.
    pause
    exit /b 1
)

REM 显示Python版本
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [Python] %%i

REM 检查关键依赖
echo [检查] 验证依赖项...
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo [安装] 正在安装依赖项...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)

echo [完成] 环境检查通过
echo.
echo [启动] 正在启动提示词注入工具...
echo [提示] 程序将在系统托盘显示
echo [快捷键] Shift+F2 调出主界面
echo.

REM 启动程序
python main.py

REM 程序退出处理
if %errorlevel% equ 0 (
    echo [完成] 程序正常退出
) else (
    echo [错误] 程序异常退出，错误代码: %errorlevel%
    echo 请检查错误信息或联系开发者
)

echo.
pause 