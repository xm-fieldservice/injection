@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================
echo 验证主题修复 - 多实例独立测试
echo ==========================================
echo.

echo 📋 当前实例配置情况:
echo.

echo 🔍 检查实例配置文件...
for %%f in (config_instance_*.json) do (
    echo 找到实例配置: %%f
)

echo.
echo 🎨 检查主题配置目录...
for /d %%d in (config_instance_*) do (
    echo 找到主题目录: %%d
    if exist "%%d\theme_config.json" (
        echo   ✅ 主题配置存在
    ) else (
        echo   ❌ 主题配置缺失
    )
)

echo.
echo ==========================================
echo 🚀 启动测试说明:
echo 1. 现在启动两个工具实例
echo 2. 第一个实例应该显示蓝色🔵主题
echo 3. 第二个实例应该显示红色🔴主题
echo 4. 两个实例的校准位置应该独立
echo ==========================================
echo.

pause 