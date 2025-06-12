#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题管理器 - 支持多实例颜色主题
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional

class ThemeManager:
    """主题管理器，负责多实例主题分配和管理"""
    
    # 预定义主题配色方案
    THEMES = {
        'blue': {
            'name': '蓝色主题',
            'primary': '#3498db',
            'secondary': '#ecf0f1', 
            'accent': '#2980b9',
            'background': '#ffffff',
            'text': '#2c3e50',
            'border': '#bdc3c7',
            'hover': '#2980b9',
            'icon_color': '🔵'
        },
        'red': {
            'name': '红色主题',
            'primary': '#e74c3c',
            'secondary': '#fdf2e9',
            'accent': '#c0392b', 
            'background': '#ffffff',
            'text': '#2c3e50',
            'border': '#e67e22',
            'hover': '#c0392b',
            'icon_color': '🔴'
        },
        'green': {
            'name': '绿色主题',
            'primary': '#2ecc71',
            'secondary': '#eafaf1',
            'accent': '#27ae60',
            'background': '#ffffff', 
            'text': '#2c3e50',
            'border': '#58d68d',
            'hover': '#27ae60',
            'icon_color': '🟢'
        },
        'orange': {
            'name': '橙色主题',
            'primary': '#f39c12',
            'secondary': '#fef9e7',
            'accent': '#e67e22',
            'background': '#ffffff',
            'text': '#2c3e50', 
            'border': '#f7dc6f',
            'hover': '#e67e22',
            'icon_color': '🟠'
        }
    }
    
    def __init__(self, config_dir: str = 'config'):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, 'theme_config.json')
        self.current_theme = 'blue'  # 默认主题
        self.instance_id = self._generate_instance_id()
        
        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        # 加载或初始化主题配置
        self._load_config()
        

        
    def _generate_instance_id(self) -> str:
        """生成唯一的实例ID"""
        # 基于进程ID和当前时间生成唯一标识
        import time
        pid = os.getpid()
        timestamp = int(time.time() * 1000)
        raw_id = f"{pid}_{timestamp}"
        return hashlib.md5(raw_id.encode()).hexdigest()[:8]
        
    def _load_config(self):
        """加载主题配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 检查是否有为当前实例分配的主题
                    if self.instance_id in config.get('instance_themes', {}):
                        self.current_theme = config['instance_themes'][self.instance_id]
                    else:
                        # 为新实例分配主题
                        self.current_theme = self._assign_new_theme(config)
            else:
                # 创建新配置
                self.current_theme = self._assign_new_theme({})
                
            self._save_config()
            
        except Exception as e:
            print(f"加载主题配置失败: {e}")
            self.current_theme = 'blue'
            
    def _assign_new_theme(self, config: Dict) -> str:
        """为新实例分配主题"""
        existing_instances = config.get('instance_themes', {})
        used_themes = set(existing_instances.values())
        
        # 按优先级分配主题
        theme_priority = ['blue', 'red', 'green', 'orange']
        
        for theme in theme_priority:
            if theme not in used_themes:
                return theme
                
        # 如果所有主题都被使用，随机分配
        import random
        return random.choice(theme_priority)
        
    def _save_config(self):
        """保存主题配置"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
            if 'instance_themes' not in config:
                config['instance_themes'] = {}
                
            config['instance_themes'][self.instance_id] = self.current_theme
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存主题配置失败: {e}")
            
    def get_current_theme(self) -> Dict[str, Any]:
        """获取当前主题配置"""
        return self.THEMES.get(self.current_theme, self.THEMES['blue'])
        
    def set_theme(self, theme_name: str) -> bool:
        """设置主题"""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self._save_config()
            return True
        return False
        
    def get_available_themes(self) -> Dict[str, Dict]:
        """获取所有可用主题"""
        return self.THEMES
        
    def get_stylesheet(self) -> str:
        """生成Qt样式表"""
        theme = self.get_current_theme()
        
        return f"""
        QMainWindow {{
            background-color: {theme['background']};
            border: 2px solid {theme['primary']};
        }}
        
        QTextEdit {{
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 5px;
            font-size: 14px;
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        
        QPushButton {{
            background-color: {theme['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
        }}
        
        QPushButton:hover {{
            background-color: {theme['hover']};
        }}
        
        QLabel {{
            font-size: 14px;
            color: {theme['text']};
        }}
        
        QLabel#project_title {{
            font-size: 16px;
            font-weight: bold;
            color: {theme['primary']};
            background-color: {theme['secondary']};
            padding: 8px;
            border-radius: 4px;
            border: 1px solid {theme['border']};
        }}
        
        QFrame#left_panel {{
            background-color: {theme['secondary']};
            border-right: 1px solid {theme['border']};
        }}
        
        QComboBox {{
            border: 1px solid {theme['border']};
            border-radius: 4px;
            padding: 5px;
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        
        QListWidget {{
            border: 1px solid {theme['border']};
            border-radius: 4px;
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        """
        
    def get_instance_info(self) -> Dict[str, str]:
        """获取实例信息"""
        theme = self.get_current_theme()
        return {
            'instance_id': self.instance_id,
            'theme_name': self.current_theme,
            'theme_display_name': theme['name'],
            'icon_color': theme['icon_color']
        }
        
    def cleanup_old_instances(self, max_age_hours: int = 24):
        """清理过期的实例配置"""
        try:
            if not os.path.exists(self.config_file):
                return
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 这里可以实现根据时间戳清理过期实例的逻辑
            # 现在简单保持现有配置
            
        except Exception as e:
            print(f"清理实例配置失败: {e}") 