@echo off
echo ================================================
echo         智能Python启动工具
echo ================================================
echo.

REM 设置UTF-8编码
chcp 65001 >nul

REM 切换到脚本所在目录
cd /d "%~dp0"

echo [检查] 正在检测Python环境...

REM 方法1：检查PATH中的python命令
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [成功] 在PATH中找到Python
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [版本] %%i
    for /f "tokens=*" %%i in ('where python 2^>^&1') do echo [路径] %%i
    set PYTHON_CMD=python
    goto :found_python
)

REM 方法2：检查常见安装路径
echo [检查] PATH中未找到Python，正在检查常见安装路径...

set PYTHON_PATHS=^
"C:\Python39\python.exe" ^
"C:\Python310\python.exe" ^
"C:\Python311\python.exe" ^
"C:\Python312\python.exe" ^
"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe" ^
"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe" ^
"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe" ^
"C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" ^
"C:\Program Files\Python39\python.exe" ^
"C:\Program Files\Python310\python.exe" ^
"C:\Program Files\Python311\python.exe" ^
"C:\Program Files\Python312\python.exe"

for %%P in (%PYTHON_PATHS%) do (
    if exist %%P (
        echo [找到] Python安装路径: %%P
        for /f "tokens=*" %%v in ('%%P --version 2^>^&1') do echo [版本] %%v
        set PYTHON_CMD=%%P
        goto :found_python
    )
)

REM 方法3：使用注册表查找（Python 3.3+）
echo [检查] 正在查询注册表中的Python信息...
for /f "tokens=2*" %%A in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore" /s /v InstallPath 2^>nul ^| findstr "InstallPath"') do (
    set "PYTHON_DIR=%%B"
    if exist "%%B\python.exe" (
        echo [找到] 注册表中的Python: %%B\python.exe
        for /f "tokens=*" %%v in ('"%%B\python.exe" --version 2^>^&1') do echo [版本] %%v
        set PYTHON_CMD="%%B\python.exe"
        goto :found_python
    )
)

REM 未找到Python
echo [错误] 未找到Python安装，请执行以下操作之一：
echo   1. 安装Python 3.8+ 并确保添加到PATH环境变量
echo   2. 从 https://python.org 下载并安装Python
echo   3. 重新安装Python时勾选"Add Python to PATH"选项
echo.
pause
exit /b 1

:found_python
echo.
echo [验证] 检查项目依赖...

REM 检查main.py是否存在
if not exist "main.py" (
    echo [错误] 未找到main.py文件
    echo [当前目录] %CD%
    pause
    exit /b 1
)

REM 检查依赖项
echo [检查] 验证PyQt5依赖...
%PYTHON_CMD% -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 缺少依赖项，正在安装...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖项安装失败
        echo [解决] 请手动执行: %PYTHON_CMD% -m pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo [完成] 环境检查通过
echo.

REM 创建启动命令文件
echo [生成] 创建个性化启动命令...

echo @echo off > 我的启动命令.bat
echo REM 自动生成的启动命令 >> 我的启动命令.bat
echo REM 生成时间: %date% %time% >> 我的启动命令.bat
echo REM Python路径: %PYTHON_CMD% >> 我的启动命令.bat
echo. >> 我的启动命令.bat
echo cd /d "%~dp0" >> 我的启动命令.bat
echo %PYTHON_CMD% main.py >> 我的启动命令.bat
echo pause >> 我的启动命令.bat

echo [成功] 已生成启动命令文件: 我的启动命令.bat
echo [使用] Python命令: %PYTHON_CMD%
echo.

REM 询问是否立即启动
echo 是否立即启动程序？(Y/N)
set /p choice=请选择: 
if /i "%choice%"=="Y" (
    echo.
    echo [启动] 正在启动提示词注入工具...
    %PYTHON_CMD% main.py
) else (
    echo [完成] 可以使用生成的"我的启动命令.bat"文件启动程序
)

echo.
pause 