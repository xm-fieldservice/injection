#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cursor AI 输出监控工具
用于监控和捕获 Cursor 编辑器 AI 的输出内容
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from cursor_monitor_gui import CursorMonitorGUI

def main():
    """主函数入口点"""
    app = QApplication(sys.argv)
    app.setApplicationName("Cursor AI 输出监控工具")
    app.setStyle("Fusion")
    
    # 设置应用图标（如果存在）
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建并显示主窗口
    window = CursorMonitorGUI()
    window.show()
    
    # 启动主事件循环
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 