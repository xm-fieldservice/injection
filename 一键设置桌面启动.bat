@echo off
title 一键设置桌面启动
echo ================================================
echo        一键设置桌面启动程序
echo ================================================
echo.

REM 设置UTF-8编码
chcp 65001 >nul

REM 切换到脚本所在目录
cd /d "%~dp0"

echo [步骤1] 检查项目文件...
if not exist "main.py" (
    echo [错误] 未找到main.py文件，请在项目根目录运行此脚本
    pause
    exit /b 1
)

if not exist "桌面启动.bat" (
    echo [错误] 未找到桌面启动.bat文件
    pause
    exit /b 1
)

echo [完成] 项目文件检查通过
echo.

echo [步骤2] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python环境
    echo.
    echo 请先安装Python：
    echo 1. 访问 https://python.org 下载Python 3.8+
    echo 2. 安装时勾选"Add Python to PATH"
    echo 3. 安装完成后重新运行此脚本
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [完成] 找到 %%i
echo.

echo [步骤3] 检查依赖项...
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo [安装] 正在安装必要依赖项...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [警告] 依赖安装可能失败，程序仍会尝试创建快捷方式
    ) else (
        echo [完成] 依赖项安装成功
    )
) else (
    echo [完成] 依赖项检查通过
)
echo.

echo [步骤4] 创建桌面快捷方式...

REM 检查VBS脚本是否存在
if not exist "创建桌面快捷方式.vbs" (
    echo [错误] 未找到VBS脚本文件
    echo 将使用手动方式创建快捷方式
    goto :manual_shortcut
)

REM 运行VBS脚本创建快捷方式
cscript //nologo "创建桌面快捷方式.vbs"
if %errorlevel% equ 0 (
    echo [完成] 桌面快捷方式创建成功！
    goto :finish
) else (
    echo [警告] 自动创建失败，使用手动方式
    goto :manual_shortcut
)

:manual_shortcut
echo.
echo [手动创建] 请按以下步骤手动创建桌面快捷方式：
echo.
echo 1. 右键点击桌面 → 新建 → 快捷方式
echo 2. 在位置框中输入：
echo    "%CD%\桌面启动.bat"
echo 3. 点击"下一步"
echo 4. 输入名称：提示词注入工具
echo 5. 点击"完成"
echo.
echo 或者直接复制以下路径到快捷方式：
echo %CD%\桌面启动.bat
echo.

:finish
echo ================================================
echo               设置完成
echo ================================================
echo.
echo [使用说明]
echo • 双击桌面的"提示词注入工具"图标启动程序
echo • 程序启动后会在系统托盘显示
echo • 使用快捷键 Shift+F2 调出主界面
echo • 如有问题，请检查Python环境和依赖项
echo.
echo [项目位置] %CD%
echo [启动文件] 桌面启动.bat
echo.

pause 