#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版主窗口 - 集成项目名称显示和主题管理
"""

import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QSystemTrayIcon, QMenu, QAction, QPushButton)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

# 添加父目录到路径以导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.theme_manager import ThemeManager
from core.project_detector import ProjectDetector

class EnhancedMainWindow(QWidget):
    """增强版主窗口，支持项目名称显示和主题管理"""
    
    # 信号定义
    project_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化组件
        self.theme_manager = ThemeManager()
        self.project_detector = ProjectDetector()
        
        # 状态变量
        self.current_project = None
        self.is_minimized = False
        
        # 定时器
        self.project_update_timer = QTimer()
        self.project_update_timer.timeout.connect(self.update_project_info)
        self.project_update_timer.start(3000)  # 每3秒更新一次
        
        # 初始化UI
        self.init_ui()
        self.setup_system_tray()
        
        # 初始更新
        self.update_project_info()
        
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        
        # 应用主题样式
        self.apply_theme()
        
        # 创建主布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 创建标题栏
        self.create_title_bar(main_layout)
        
        # 创建项目信息区域
        self.create_project_info_area(main_layout)
        
        # 创建控制按钮区域
        self.create_control_buttons(main_layout)
        
    def create_title_bar(self, parent_layout):
        """创建标题栏"""
        title_frame = QFrame()
        title_frame.setObjectName("title_bar")
        title_layout = QHBoxLayout(title_frame)
        
        # 窗口标题
        self.title_label = QLabel("提示词注入工具")
        self.title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # 最小化按钮
        min_btn = QPushButton("−")
        min_btn.setObjectName("min_button")
        min_btn.setFixedSize(30, 25)
        min_btn.clicked.connect(self.minimize_window)
        title_layout.addWidget(min_btn)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setObjectName("close_button")
        close_btn.setFixedSize(30, 25)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        parent_layout.addWidget(title_frame)
        
    def create_project_info_area(self, parent_layout):
        """创建项目信息显示区域"""
        info_frame = QFrame()
        info_frame.setObjectName("project_info")
        info_layout = QVBoxLayout(info_frame)
        
        # 项目名称标签
        self.project_label = QLabel("检测项目中...")
        self.project_label.setObjectName("project_title")
        self.project_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.project_label)
        
        # 实例信息标签
        self.instance_label = QLabel("")
        self.instance_label.setObjectName("instance_info") 
        self.instance_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.instance_label)
        
        parent_layout.addWidget(info_frame)
        
    def create_control_buttons(self, parent_layout):
        """创建控制按钮区域"""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        
        # 刷新项目按钮
        refresh_btn = QPushButton("刷新项目")
        refresh_btn.clicked.connect(self.refresh_project)
        button_layout.addWidget(refresh_btn)
        
        # 切换主题按钮
        theme_btn = QPushButton("切换主题")
        theme_btn.clicked.connect(self.cycle_theme)
        button_layout.addWidget(theme_btn)
        
        parent_layout.addWidget(button_frame)
        
    def apply_theme(self):
        """应用主题样式"""
        stylesheet = self.theme_manager.get_stylesheet()
        
        # 添加自定义样式
        custom_styles = """
        QFrame#title_bar {
            background-color: """ + self.theme_manager.get_current_theme()['primary'] + """;
            color: white;
            padding: 5px;
        }
        
        QFrame#project_info {
            background-color: """ + self.theme_manager.get_current_theme()['secondary'] + """;
            border: 1px solid """ + self.theme_manager.get_current_theme()['border'] + """;
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
        }
        
        QPushButton#min_button, QPushButton#close_button {
            background-color: transparent;
            color: white;
            border: 1px solid white;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
        }
        
        QPushButton#min_button:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        QPushButton#close_button:hover {
            background-color: rgba(255, 0, 0, 0.6);
        }
        
        QLabel#instance_info {
            font-size: 12px;
            color: """ + self.theme_manager.get_current_theme()['text'] + """;
            margin-top: 5px;
        }
        """
        
        self.setStyleSheet(stylesheet + custom_styles)
        
    def setup_system_tray(self):
        """设置系统托盘"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置托盘图标
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'icon.png')
            if os.path.exists(icon_path):
                self.tray_icon.setIcon(QIcon(icon_path))
            else:
                # 使用默认图标
                self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        except:
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        refresh_action = QAction("刷新项目", self)
        refresh_action.triggered.connect(self.refresh_project)
        tray_menu.addAction(refresh_action)
        
        theme_action = QAction("切换主题", self)
        theme_action.triggered.connect(self.cycle_theme)
        tray_menu.addAction(theme_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
        
    def update_project_info(self):
        """更新项目信息"""
        try:
            project_info = self.project_detector.get_project_info()
            project_name = project_info['project_name']
            
            # 检查项目是否改变
            if project_name != self.current_project:
                self.current_project = project_name
                self.project_changed.emit(project_name)
                
            # 更新显示
            self.project_label.setText(f"📁 项目: {project_info['display_name']}")
            
            # 更新实例信息
            instance_info = self.theme_manager.get_instance_info()
            instance_text = f"{instance_info['icon_color']} {instance_info['theme_display_name']} | 实例: {instance_info['instance_id']}"
            self.instance_label.setText(instance_text)
            
            # 更新窗口标题
            self.update_window_title(project_name)
            
            # 更新系统托盘提示
            self.update_tray_tooltip(project_name, instance_info)
            
        except Exception as e:
            print(f"更新项目信息失败: {e}")
            self.project_label.setText("❌ 项目检测失败")
            
    def update_window_title(self, project_name):
        """更新窗口标题"""
        instance_info = self.theme_manager.get_instance_info()
        title = f"提示词注入工具 - {project_name} [{instance_info['theme_display_name']}]"
        self.title_label.setText(title)
        self.setWindowTitle(title)
        
    def update_tray_tooltip(self, project_name, instance_info):
        """更新系统托盘提示"""
        if hasattr(self, 'tray_icon'):
            tooltip = f"提示词注入工具\n项目: {project_name}\n主题: {instance_info['theme_display_name']}\n实例: {instance_info['instance_id']}"
            self.tray_icon.setToolTip(tooltip)
            
    def refresh_project(self):
        """手动刷新项目信息"""
        self.project_detector.project_cache.clear()
        self.update_project_info()
        
    def cycle_theme(self):
        """循环切换主题"""
        themes = list(self.theme_manager.get_available_themes().keys())
        current_index = themes.index(self.theme_manager.current_theme)
        next_index = (current_index + 1) % len(themes)
        next_theme = themes[next_index]
        
        if self.theme_manager.set_theme(next_theme):
            self.apply_theme()
            self.update_project_info()  # 更新显示
            self.theme_changed.emit(next_theme)
            
    def minimize_window(self):
        """最小化窗口"""
        self.hide()
        self.is_minimized = True
        
        if hasattr(self, 'tray_icon'):
            self.tray_icon.showMessage(
                "提示词注入工具",
                "已最小化到系统托盘",
                QSystemTrayIcon.Information,
                2000
            )
            
    def show_window(self):
        """显示窗口"""
        self.show()
        self.raise_()
        self.activateWindow()
        self.is_minimized = False
        
    def tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.is_minimized:
                self.show_window()
            else:
                self.minimize_window()
                
    def closeEvent(self, event):
        """窗口关闭事件"""
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        event.accept()
        
    def get_current_project(self):
        """获取当前项目名称"""
        return self.current_project
        
    def get_current_theme(self):
        """获取当前主题"""
        return self.theme_manager.current_theme
        
    def get_instance_info(self):
        """获取实例信息"""
        return self.theme_manager.get_instance_info() 