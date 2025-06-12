@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo 启动提示词注入工具 - 增强版
echo ==========================================
echo 新功能特性：
echo ✅ 项目名称自动识别显示
echo ✅ 多实例颜色主题区分 
echo ✅ 窗口标题显示项目信息
echo ✅ 系统托盘项目信息提示
echo ✅ 快捷键 Ctrl+Shift+T 切换主题
echo ==========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python，请确保已安装Python 3.7+
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

echo.
echo 正在检查依赖包...
python -c "import PyQt5, psutil, pyperclip, win32gui" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 警告：检测到缺少依赖包，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装完成
) else (
    echo ✅ 依赖包检查通过
)

echo.
echo 正在启动增强版注入工具...
echo.
echo 使用说明：
echo - Shift+F2: 显示/隐藏主窗口
echo - Alt+Enter: 注入命令到目标窗口  
echo - Shift+Enter: 保存笔记到日志
echo - Ctrl+Shift+T: 切换主题颜色
echo - 项目名称会自动显示在窗口标题和界面中
echo - 多个工具实例会自动分配不同颜色主题
echo - 每个实例使用独立配置，校准互不干扰
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错，请检查错误信息
    pause
) 