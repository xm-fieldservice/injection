#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目集成服务 - 将现有功能与项目名称显示功能集成
"""

import sys
import os
from typing import Optional, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QLabel

# 添加父目录到路径以导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.theme_manager import ThemeManager
from core.project_detector import ProjectDetector

class ProjectIntegrationService(QObject):
    """项目集成服务，负责将项目名称显示功能集成到现有主窗口中"""
    
    # 信号定义
    project_detected = pyqtSignal(str)
    theme_updated = pyqtSignal(str)
    
    def __init__(self, main_window):
        super().__init__()
        
        self.main_window = main_window
        # 使用实例ID创建独立的主题管理器
        instance_id = getattr(main_window, 'instance_id', 'default')
        self.theme_manager = ThemeManager(config_dir=f'config_instance_{instance_id}')
        # 手动设置主题管理器的实例ID以确保一致性，必须在初始化后立即设置
        self.theme_manager.instance_id = instance_id
        # 重新加载配置以使用正确的实例ID
        self.theme_manager._load_config()
        self.project_detector = ProjectDetector()
        
        # 当前状态
        self.current_project = None
        self.project_display_label = None
        
        # 定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_project_display)
        self.update_timer.start(3000)  # 每3秒更新一次
        
        # 初始化
        self.setup_integration()
        
    def setup_integration(self):
        """设置集成"""
        try:
            # 应用主题到现有窗口
            self.apply_theme_to_main_window()
            
            # 添加项目显示控件
            self.add_project_display_widget()
            
            # 更新窗口标题
            self.update_window_title()
            
            # 初始项目检测
            self.update_project_display()
            
        except Exception as e:
            print(f"设置集成失败: {e}")
            
    def apply_theme_to_main_window(self):
        """将主题应用到现有主窗口"""
        try:
            # 获取当前主题样式
            theme_stylesheet = self.theme_manager.get_stylesheet()
            
            # 获取现有样式
            current_stylesheet = self.main_window.styleSheet()
            
            # 合并样式（新主题样式优先）
            combined_stylesheet = theme_stylesheet + "\n" + current_stylesheet
            
            # 应用合并后的样式
            self.main_window.setStyleSheet(combined_stylesheet)
            
        except Exception as e:
            print(f"应用主题失败: {e}")
            
    def add_project_display_widget(self):
        """添加项目显示控件到现有界面"""
        try:
            # 查找现有的状态标签或合适的位置
            central_widget = self.main_window.centralWidget()
            if central_widget:
                layout = central_widget.layout()
                if layout:
                    # 创建项目信息标签
                    self.project_display_label = QLabel("检测项目中...")
                    self.project_display_label.setObjectName("project_title")
                    self.project_display_label.setStyleSheet("""
                        QLabel#project_title {
                            font-size: 14px;
                            font-weight: bold;
                            padding: 5px;
                            margin: 2px;
                            background-color: """ + self.theme_manager.get_current_theme()['secondary'] + """;
                            color: """ + self.theme_manager.get_current_theme()['primary'] + """;
                            border: 1px solid """ + self.theme_manager.get_current_theme()['border'] + """;
                            border-radius: 4px;
                        }
                    """)
                    
                    # 将标签插入到布局的顶部
                    layout.insertWidget(0, self.project_display_label)
                    
        except Exception as e:
            print(f"添加项目显示控件失败: {e}")
            
    def update_project_display(self):
        """更新项目显示"""
        try:
            # 获取项目信息
            project_info = self.project_detector.get_project_info()
            project_name = project_info['project_name']
            
            # 检查项目是否改变
            if project_name != self.current_project:
                self.current_project = project_name
                self.project_detected.emit(project_name)
                
            # 更新显示标签
            if self.project_display_label:
                instance_info = self.theme_manager.get_instance_info()
                display_text = f"📁 {project_info['display_name']} {instance_info['icon_color']}"
                self.project_display_label.setText(display_text)
                
            # 更新窗口标题
            self.update_window_title(project_name)
            
        except Exception as e:
            print(f"更新项目显示失败: {e}")
            if self.project_display_label:
                self.project_display_label.setText("❌ 项目检测失败")
                
    def update_window_title(self, project_name: Optional[str] = None):
        """更新窗口标题"""
        try:
            if project_name is None:
                project_name = self.current_project or "未知项目"
                
            instance_info = self.theme_manager.get_instance_info()
            
            # 构建新标题
            base_title = "提示词注入工具"
            new_title = f"{base_title} - {project_name} [{instance_info['theme_display_name']}]"
            
            # 设置窗口标题
            self.main_window.setWindowTitle(new_title)
            
        except Exception as e:
            print(f"更新窗口标题失败: {e}")
            
    def switch_theme(self, theme_name: Optional[str] = None):
        """切换主题"""
        try:
            if theme_name:
                success = self.theme_manager.set_theme(theme_name)
            else:
                # 循环切换主题
                themes = list(self.theme_manager.get_available_themes().keys())
                current_index = themes.index(self.theme_manager.current_theme)
                next_index = (current_index + 1) % len(themes)
                theme_name = themes[next_index]
                success = self.theme_manager.set_theme(theme_name)
                
            if success:
                # 重新应用主题
                self.apply_theme_to_main_window()
                
                # 更新项目显示标签样式
                if self.project_display_label:
                    self.project_display_label.setStyleSheet("""
                        QLabel#project_title {
                            font-size: 14px;
                            font-weight: bold;
                            padding: 5px;
                            margin: 2px;
                            background-color: """ + self.theme_manager.get_current_theme()['secondary'] + """;
                            color: """ + self.theme_manager.get_current_theme()['primary'] + """;
                            border: 1px solid """ + self.theme_manager.get_current_theme()['border'] + """;
                            border-radius: 4px;
                        }
                    """)
                
                # 更新显示
                self.update_project_display()
                
                # 发送信号
                self.theme_updated.emit(theme_name)
                
                return True
                
        except Exception as e:
            print(f"切换主题失败: {e}")
            
        return False
        
    def get_current_project(self) -> Optional[str]:
        """获取当前项目名称"""
        return self.current_project
        
    def get_current_theme(self) -> str:
        """获取当前主题名称"""
        return self.theme_manager.current_theme
        
    def get_instance_info(self) -> Dict[str, str]:
        """获取实例信息"""
        return self.theme_manager.get_instance_info()
        
    def refresh_project_detection(self):
        """刷新项目检测"""
        try:
            self.project_detector.project_cache.clear()
            self.update_project_display()
        except Exception as e:
            print(f"刷新项目检测失败: {e}")
            
    def is_cursor_running(self) -> bool:
        """检查Cursor是否运行"""
        return self.project_detector.is_cursor_running()
        
    def get_available_themes(self) -> Dict[str, Dict]:
        """获取可用主题列表"""
        return self.theme_manager.get_available_themes()
        
    def cleanup(self):
        """清理资源"""
        try:
            if self.update_timer.isActive():
                self.update_timer.stop()
        except Exception as e:
            print(f"清理资源失败: {e}")
            
    def add_theme_menu_to_main_window(self):
        """为主窗口添加主题菜单"""
        try:
            # 这个方法可以用来为现有主窗口添加主题切换菜单
            # 具体实现取决于主窗口的菜单结构
            pass
        except Exception as e:
            print(f"添加主题菜单失败: {e}")
            
    def export_current_config(self) -> Dict[str, Any]:
        """导出当前配置"""
        try:
            return {
                'current_project': self.current_project,
                'current_theme': self.get_current_theme(),
                'instance_info': self.get_instance_info(),
                'cursor_running': self.is_cursor_running()
            }
        except Exception as e:
            print(f"导出配置失败: {e}")
            return {} 