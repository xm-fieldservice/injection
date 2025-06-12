#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
热重载管理器 - 提供代码热插拔功能
支持在运行时动态重新加载修改的模块，无需重启程序

作者: Assistant
创建时间: 2025-06-08
项目: injection
"""

import sys
import os
import time
import importlib
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtCore import QObject, pyqtSignal
import traceback
from pathlib import Path

class HotReloadManager(QObject):
    """热重载管理器"""
    
    # 信号定义
    module_reloaded = pyqtSignal(str, bool, str)  # 模块名, 是否成功, 消息
    reload_status_changed = pyqtSignal(str)  # 状态变化
    
    def __init__(self, watch_directories=None, parent=None):
        super().__init__(parent)
        
        # 监控目录列表
        self.watch_directories = watch_directories or [os.getcwd()]
        
        # 可重载的模块列表
        self.reloadable_modules = {
            'layout_manager',
            'mindmap_integration', 
            'template_manager',
            'template_dialog',
            'cursor_capture',
            'cursor_processor',
            'ai_service'
        }
        
        # 模块依赖关系（子模块 -> 父模块列表）
        self.module_dependencies = {
            'mindmap_integration': ['layout_manager'],
            'template_dialog': ['template_manager'],
            'cursor_processor': ['cursor_capture']
        }
        
        # 文件监控器
        self.observer = None
        self.file_handler = None
        
        # 重载状态
        self.is_watching = False
        self.reload_lock = threading.Lock()
        
        # 模块引用缓存
        self.module_refs = {}
        
        print("🔥 热重载管理器已初始化")
    
    def start_watching(self):
        """开始监控文件变化"""
        if self.is_watching:
            return
        
        try:
            self.file_handler = PythonFileHandler(self)
            self.observer = Observer()
            
            for directory in self.watch_directories:
                if os.path.exists(directory):
                    self.observer.schedule(self.file_handler, directory, recursive=False)
                    print(f"📁 监控目录: {directory}")
            
            self.observer.start()
            self.is_watching = True
            
            self.reload_status_changed.emit("🔥 热重载已启动 - 监控文件变化中...")
            print("🔥 热重载监控已启动")
            
        except Exception as e:
            print(f"❌ 启动热重载失败: {e}")
            self.reload_status_changed.emit(f"❌ 热重载启动失败: {e}")
    
    def stop_watching(self):
        """停止监控文件变化"""
        if not self.is_watching:
            return
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None
            
            self.is_watching = False
            self.reload_status_changed.emit("⏹️ 热重载已停止")
            print("⏹️ 热重载监控已停止")
            
        except Exception as e:
            print(f"❌ 停止热重载失败: {e}")
    
    def reload_module(self, module_name):
        """重新加载指定模块"""
        with self.reload_lock:
            try:
                if module_name not in self.reloadable_modules:
                    msg = f"模块 {module_name} 不在可重载列表中"
                    print(f"⚠️ {msg}")
                    self.module_reloaded.emit(module_name, False, msg)
                    return False
                
                # 检查模块是否已加载
                if module_name not in sys.modules:
                    msg = f"模块 {module_name} 尚未加载"
                    print(f"⚠️ {msg}")
                    self.module_reloaded.emit(module_name, False, msg)
                    return False
                
                print(f"🔄 开始重载模块: {module_name}")
                
                # 重新加载模块
                module = sys.modules[module_name]
                importlib.reload(module)
                
                # 更新模块引用缓存
                self.module_refs[module_name] = module
                
                # 重载依赖模块
                self._reload_dependent_modules(module_name)
                
                msg = f"模块 {module_name} 重载成功"
                print(f"✅ {msg}")
                self.module_reloaded.emit(module_name, True, msg)
                
                return True
                
            except Exception as e:
                error_msg = f"重载模块 {module_name} 失败: {str(e)}"
                print(f"❌ {error_msg}")
                print(traceback.format_exc())
                self.module_reloaded.emit(module_name, False, error_msg)
                return False
    
    def _reload_dependent_modules(self, module_name):
        """重载依赖模块"""
        for dependent_module, dependencies in self.module_dependencies.items():
            if module_name in dependencies and dependent_module in sys.modules:
                print(f"🔄 重载依赖模块: {dependent_module}")
                try:
                    importlib.reload(sys.modules[dependent_module])
                    self.module_refs[dependent_module] = sys.modules[dependent_module]
                    print(f"✅ 依赖模块 {dependent_module} 重载成功")
                except Exception as e:
                    print(f"❌ 重载依赖模块 {dependent_module} 失败: {e}")
    
    def force_reload_all(self):
        """强制重载所有可重载模块"""
        print("🔄 开始强制重载所有模块...")
        success_count = 0
        
        for module_name in self.reloadable_modules:
            if module_name in sys.modules:
                if self.reload_module(module_name):
                    success_count += 1
        
        msg = f"强制重载完成: {success_count}/{len(self.reloadable_modules)} 个模块成功"
        print(f"📊 {msg}")
        self.reload_status_changed.emit(msg)
    
    def get_module_status(self):
        """获取模块状态信息"""
        status = {}
        for module_name in self.reloadable_modules:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                status[module_name] = {
                    'loaded': True,
                    'file': getattr(module, '__file__', 'Unknown'),
                    'modified': self._get_file_modified_time(getattr(module, '__file__', None))
                }
            else:
                status[module_name] = {
                    'loaded': False,
                    'file': None,
                    'modified': None
                }
        return status
    
    def _get_file_modified_time(self, file_path):
        """获取文件修改时间"""
        if file_path and os.path.exists(file_path):
            return time.ctime(os.path.getmtime(file_path))
        return None
    
    def add_reloadable_module(self, module_name):
        """添加可重载模块"""
        self.reloadable_modules.add(module_name)
        print(f"➕ 添加可重载模块: {module_name}")
    
    def remove_reloadable_module(self, module_name):
        """移除可重载模块"""
        self.reloadable_modules.discard(module_name)
        print(f"➖ 移除可重载模块: {module_name}")
    
    def __del__(self):
        """析构函数"""
        self.stop_watching()


class PythonFileHandler(FileSystemEventHandler):
    """Python文件变化处理器"""
    
    def __init__(self, reload_manager):
        super().__init__()
        self.reload_manager = reload_manager
        self.last_reload_times = {}
        self.reload_delay = 1.0  # 防抖延迟（秒）
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        if not file_path.endswith('.py'):
            return
        
        # 获取模块名
        module_name = Path(file_path).stem
        
        if module_name not in self.reload_manager.reloadable_modules:
            return
        
        # 防抖处理
        current_time = time.time()
        last_time = self.last_reload_times.get(module_name, 0)
        
        if current_time - last_time < self.reload_delay:
            return
        
        self.last_reload_times[module_name] = current_time
        
        print(f"📝 检测到文件变化: {file_path}")
        
        # 延迟重载，确保文件写入完成
        def delayed_reload():
            time.sleep(0.5)  # 等待文件写入完成
            self.reload_manager.reload_module(module_name)
        
        threading.Thread(target=delayed_reload, daemon=True).start()


# 全局热重载管理器实例
_hot_reload_manager = None

def get_hot_reload_manager():
    """获取全局热重载管理器实例"""
    global _hot_reload_manager
    if _hot_reload_manager is None:
        _hot_reload_manager = HotReloadManager()
    return _hot_reload_manager

def start_hot_reload():
    """启动热重载功能"""
    manager = get_hot_reload_manager()
    manager.start_watching()
    return manager

def stop_hot_reload():
    """停止热重载功能"""
    manager = get_hot_reload_manager()
    manager.stop_watching()

def reload_module(module_name):
    """重载指定模块"""
    manager = get_hot_reload_manager()
    return manager.reload_module(module_name)

if __name__ == "__main__":
    # 测试代码
    print("🔥 热重载管理器测试")
    
    manager = HotReloadManager()
    manager.start_watching()
    
    try:
        # 保持运行
        input("按回车键停止监控...")
    finally:
        manager.stop_watching()
        print("测试完成") 