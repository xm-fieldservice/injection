@echo off
chcp 65001 >nul
echo 工作记录脚本启动...
python auto_work_logger.py %*
pause 