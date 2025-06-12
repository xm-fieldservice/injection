#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目检测器 - 智能识别Cursor项目名称
"""

import os
import re
import win32gui
import win32process
import psutil
from typing import Optional, Dict, List
import json

class ProjectDetector:
    """项目检测器，用于检测Cursor所在的项目名称"""
    
    def __init__(self):
        self.cursor_process_names = ['cursor.exe', 'cursor', 'code.exe', 'code']
        self.project_cache = {}
        
    def get_cursor_project_name(self) -> Optional[str]:
        """获取Cursor当前项目名称"""
        try:
            # 方法1: 通过窗口标题检测
            project_name = self._detect_from_window_title()
            if project_name:
                return project_name
                
            # 方法2: 通过进程工作目录检测  
            project_name = self._detect_from_process_cwd()
            if project_name:
                return project_name
                
            # 方法3: 通过最近使用项目检测
            project_name = self._detect_from_recent_projects()
            if project_name:
                return project_name
                
        except Exception as e:
            print(f"项目检测失败: {e}")
            
        return None
        
    def _detect_from_window_title(self) -> Optional[str]:
        """通过Cursor窗口标题检测项目名称"""
        cursor_windows = []
        
        def enum_windows_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if any(keyword in window_title.lower() for keyword in ['cursor', 'visual studio code']):
                    results.append({
                        'hwnd': hwnd,
                        'title': window_title,
                        'class': win32gui.GetClassName(hwnd)
                    })
            return True
            
        win32gui.EnumWindows(enum_windows_callback, cursor_windows)
        
        for window in cursor_windows:
            title = window['title']
            
            # 解析窗口标题格式: "filename - projectname - Cursor"
            # 或者 "projectname - Cursor"
            if ' - ' in title:
                parts = title.split(' - ')
                
                # 移除最后的 "Cursor" 或 "Visual Studio Code"
                if parts[-1].lower() in ['cursor', 'visual studio code']:
                    parts = parts[:-1]
                    
                # 如果有多个部分，通常最后一个是项目名
                if len(parts) >= 2:
                    project_name = parts[-1].strip()
                    # 过滤掉明显不是项目名的部分
                    if not self._is_valid_project_name(project_name):
                        continue
                    return project_name
                elif len(parts) == 1:
                    project_name = parts[0].strip()
                    if self._is_valid_project_name(project_name):
                        return project_name
                        
        return None
        
    def _detect_from_process_cwd(self) -> Optional[str]:
        """通过进程工作目录检测项目名称"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cwd']):
                try:
                    if proc.info['name'] and any(name in proc.info['name'].lower() 
                                               for name in self.cursor_process_names):
                        cwd = proc.info['cwd']
                        if cwd and os.path.exists(cwd):
                            project_name = os.path.basename(cwd)
                            if self._is_valid_project_name(project_name):
                                return project_name
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"通过进程检测项目失败: {e}")
            
        return None
        
    def _detect_from_recent_projects(self) -> Optional[str]:
        """通过最近使用项目检测"""
        try:
            # Cursor配置文件路径
            cursor_config_paths = [
                os.path.expanduser('~/.cursor-server'),
                os.path.expanduser('~/AppData/Roaming/Cursor'),
                os.path.expanduser('~/Library/Application Support/Cursor'),
            ]
            
            for config_path in cursor_config_paths:
                if os.path.exists(config_path):
                    storage_path = os.path.join(config_path, 'User', 'globalStorage', 'storage.json')
                    if os.path.exists(storage_path):
                        project_name = self._parse_storage_file(storage_path)
                        if project_name:
                            return project_name
                            
        except Exception as e:
            print(f"通过配置文件检测项目失败: {e}")
            
        return None
        
    def _parse_storage_file(self, storage_path: str) -> Optional[str]:
        """解析Cursor存储文件"""
        try:
            with open(storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 查找最近打开的项目
            recent_folders = data.get('openedPathsList', {}).get('entries', [])
            if recent_folders:
                latest_folder = recent_folders[0].get('folderUri', '')
                if latest_folder:
                    # 解析 file:// URI
                    if latest_folder.startswith('file://'):
                        folder_path = latest_folder[7:]  # 移除 file://
                        project_name = os.path.basename(folder_path)
                        if self._is_valid_project_name(project_name):
                            return project_name
                            
        except Exception as e:
            print(f"解析存储文件失败: {e}")
            
        return None
        
    def _is_valid_project_name(self, name: str) -> bool:
        """验证项目名称是否有效"""
        if not name or len(name.strip()) == 0:
            return False
            
        name = name.strip()
        
        # 过滤掉明显不是项目名的内容
        invalid_names = [
            'untitled', 'new folder', 'desktop', 'documents', 
            'downloads', 'temp', 'tmp', 'system32', 'program files',
            'users', 'windows', 'cursor', 'vscode', 'code'
        ]
        
        if name.lower() in invalid_names:
            return False
            
        # 过滤掉文件扩展名
        if '.' in name and len(name.split('.')[-1]) <= 4:
            return False
            
        # 过滤掉系统路径
        if name.startswith('C:') or name.startswith('/'):
            return False
            
        return True
        
    def get_project_info(self) -> Dict[str, str]:
        """获取完整的项目信息"""
        project_name = self.get_cursor_project_name()
        
        return {
            'project_name': project_name or 'Unknown Project',
            'display_name': project_name or '未知项目',
            'detection_time': str(int(__import__('time').time())),
            'detection_method': self._get_last_detection_method()
        }
        
    def _get_last_detection_method(self) -> str:
        """获取最后使用的检测方法"""
        # 这里可以记录实际使用的检测方法
        return 'window_title'
        
    def is_cursor_running(self) -> bool:
        """检查Cursor是否正在运行"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and any(name in proc.info['name'].lower() 
                                           for name in self.cursor_process_names):
                    return True
        except Exception:
            pass
        return False
        
    def get_all_cursor_projects(self) -> List[str]:
        """获取所有Cursor项目列表"""
        projects = set()
        
        try:
            # 从窗口标题获取
            cursor_windows = []
            
            def enum_windows_callback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if any(keyword in window_title.lower() for keyword in ['cursor', 'visual studio code']):
                        results.append(window_title)
                return True
                
            win32gui.EnumWindows(enum_windows_callback, cursor_windows)
            
            for title in cursor_windows:
                if ' - ' in title:
                    parts = title.split(' - ')
                    if parts[-1].lower() in ['cursor', 'visual studio code']:
                        parts = parts[:-1]
                    if len(parts) >= 1:
                        project_name = parts[-1].strip()
                        if self._is_valid_project_name(project_name):
                            projects.add(project_name)
                            
        except Exception as e:
            print(f"获取所有Cursor项目失败: {e}")
            
        return list(projects) 