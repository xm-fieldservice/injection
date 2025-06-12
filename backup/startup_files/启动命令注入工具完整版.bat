@echo off
echo ================================================
echo           提示词注入工具启动程序
echo ================================================
echo.
echo 正在启动提示词注入工具...
echo 工具目录: D:\AI既往文档\injection
echo.

REM 设置代码页为UTF-8，支持中文显示
chcp 65001 >nul

REM 切换到工具目录
cd /d "D:\AI既往文档\injection"

REM 检查当前目录是否正确
if not exist "main.py" (
    echo [错误] 未找到main.py文件，请检查工具目录路径
    echo 当前目录: %CD%
    echo 预期目录: D:\AI既往文档\injection
    pause
    exit /b 1
)

REM 检查Python是否可用
echo [检查] 验证Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python环境，请确保已安装Python 3.8+
    echo 请检查Python是否已安装并添加到系统PATH环境变量中
    pause
    exit /b 1
)

REM 显示Python版本信息
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [信息] 使用 %%i

REM 检查依赖项是否安装
echo [检查] 验证PyQt5依赖...
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] PyQt5未安装，正在尝试安装依赖项...
    echo [安装] pip install -r requirements.txt
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖项安装失败，请手动执行：pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo [成功] 依赖项安装完成
)

REM 检查配置文件
if not exist "config.json" (
    echo [信息] 首次运行，将创建默认配置文件
)

REM 检查日志目录
if not exist "logs" (
    echo [信息] 创建日志目录...
    mkdir logs
)

echo.
echo [启动] 正在启动提示词注入工具...
echo [提示] 工具启动后将在系统托盘中显示
echo [提示] 使用 Shift+F2 调出主界面
echo [提示] 按 Ctrl+C 可停止程序
echo.

REM 启动主程序
python main.py

REM 检查程序退出状态
if %errorlevel% equ 0 (
    echo.
    echo [完成] 程序正常退出
) else (
    echo.
    echo [错误] 程序异常退出，错误代码: %errorlevel%
)

echo.
pause 