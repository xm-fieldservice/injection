"""
全屏管理器 - 提供真正的全屏显示功能
解决Qt标准最大化受系统限制的问题

功能特点：
1. 真正的全屏显示（覆盖任务栏）
2. 无边框窗口模式
3. 全屏状态记忆和恢复
4. 支持多显示器环境
5. 键盘快捷键支持（Esc退出全屏）
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


class FullScreenManager(QObject):
    """全屏管理器"""
    
    # 信号定义
    fullscreen_entered = pyqtSignal()      # 进入全屏信号
    fullscreen_exited = pyqtSignal()       # 退出全屏信号
    fullscreen_toggled = pyqtSignal(bool)  # 全屏状态切换信号
    
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.is_fullscreen = False
        
        # 保存窗口状态
        self.normal_geometry = None
        self.normal_window_state = None
        self.normal_window_flags = None
        
        # 初始化
        self._init_fullscreen_config()
        self._setup_keyboard_shortcuts()
        
        print("🖥️ 全屏管理器已初始化")
    
    def _init_fullscreen_config(self):
        """初始化全屏配置"""
        # 获取主屏幕信息
        self.primary_screen = QApplication.primaryScreen()
        
        # 获取所有屏幕信息
        self.all_screens = QApplication.screens()
        
        # 获取当前窗口所在屏幕
        self.current_screen = self._get_window_screen()
        
        print(f"🖥️ 检测到 {len(self.all_screens)} 个显示器")
        for i, screen in enumerate(self.all_screens):
            geometry = screen.geometry()
            print(f"   显示器 {i+1}: {geometry.width()}×{geometry.height()} at ({geometry.x()}, {geometry.y()})")
    
    def _get_window_screen(self):
        """获取窗口当前所在的屏幕"""
        window_center = self.window.geometry().center()
        
        for screen in self.all_screens:
            if screen.geometry().contains(window_center):
                return screen
        
        # 如果没找到，返回主屏幕
        return self.primary_screen
    
    def _setup_keyboard_shortcuts(self):
        """设置键盘快捷键"""
        # ESC键退出全屏
        self.escape_shortcut = QShortcut(QKeySequence('Escape'), self.window)
        self.escape_shortcut.activated.connect(self._on_escape_pressed)
        
        # F11键切换全屏
        self.f11_shortcut = QShortcut(QKeySequence('F11'), self.window)
        self.f11_shortcut.activated.connect(self.toggle_fullscreen)
        
        print("⌨️ 全屏快捷键已设置：F11切换全屏，Esc退出全屏")
    
    def _on_escape_pressed(self):
        """ESC键被按下"""
        if self.is_fullscreen:
            self.exit_fullscreen()
    
    def enter_fullscreen(self, target_screen=None):
        """进入全屏模式"""
        if self.is_fullscreen:
            return
        
        print("🔄 正在进入真正的全屏模式...")
        
        # 保存当前窗口状态
        self._save_window_state()
        
        # 确定目标屏幕
        if target_screen is None:
            target_screen = self._get_window_screen()
        
        # 获取目标屏幕的完整几何信息
        screen_geometry = target_screen.geometry()
        
        # 设置窗口为无边框
        self.window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # 设置全屏几何信息
        self.window.setGeometry(screen_geometry)
        
        # 显示窗口
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        
        # 更新状态
        self.is_fullscreen = True
        self.current_screen = target_screen
        
        # 发送信号
        self.fullscreen_entered.emit()
        self.fullscreen_toggled.emit(True)
        
        print(f"✅ 已进入真正全屏模式！屏幕尺寸：{screen_geometry.width()}×{screen_geometry.height()}")
        
        # 更新最大化按钮状态
        self._update_maximize_button(True)
    
    def exit_fullscreen(self):
        """退出全屏模式"""
        if not self.is_fullscreen:
            return
        
        print("🔄 正在退出全屏模式...")
        
        # 恢复窗口标志
        if self.normal_window_flags is not None:
            self.window.setWindowFlags(self.normal_window_flags)
        else:
            # 默认窗口标志，包含最大化按钮
            self.window.setWindowFlags(
                Qt.WindowStaysOnTopHint | 
                Qt.Window | 
                Qt.WindowMaximizeButtonHint | 
                Qt.WindowMinimizeButtonHint | 
                Qt.WindowCloseButtonHint
            )
        
        # 恢复窗口几何信息
        if self.normal_geometry is not None:
            self.window.setGeometry(self.normal_geometry)
        
        # 恢复窗口状态
        if self.normal_window_state is not None:
            self.window.setWindowState(self.normal_window_state)
        
        # 显示窗口
        self.window.show()
        
        # 更新状态
        self.is_fullscreen = False
        
        # 发送信号
        self.fullscreen_exited.emit()
        self.fullscreen_toggled.emit(False)
        
        print("✅ 已退出全屏模式，窗口已恢复正常状态")
        
        # 更新最大化按钮状态
        self._update_maximize_button(False)
    
    def toggle_fullscreen(self):
        """切换全屏状态"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def _save_window_state(self):
        """保存当前窗口状态"""
        self.normal_geometry = self.window.geometry()
        self.normal_window_state = self.window.windowState()
        self.normal_window_flags = self.window.windowFlags()
        
        print(f"💾 已保存窗口状态：{self.normal_geometry.width()}×{self.normal_geometry.height()}")
    
    def _update_maximize_button(self, is_fullscreen):
        """更新最大化按钮状态"""
        if hasattr(self.window, 'maximize_btn'):
            if is_fullscreen:
                self.window.maximize_btn.setText("🗗")
                if hasattr(self.window, 'resize_status_label'):
                    self.window.resize_status_label.setText("真正全屏模式 | 按Esc或F11退出全屏")
            else:
                self.window.maximize_btn.setText("🗖")
                if hasattr(self.window, 'resize_status_label'):
                    self.window.resize_status_label.setText("可拖拽边框调整窗口大小 | 双击标题栏最大化")
    
    def force_true_fullscreen(self):
        """强制进入真正的全屏模式（覆盖任务栏）"""
        print("🚀 强制进入覆盖任务栏的真正全屏模式...")
        
        # 保存当前状态
        self._save_window_state()
        
        # 获取主屏幕的完整几何信息（包括任务栏区域）
        primary_screen = QApplication.primaryScreen()
        full_geometry = primary_screen.geometry()  # 完整屏幕区域
        
        # 设置最强的全屏标志组合
        fullscreen_flags = (
            Qt.FramelessWindowHint |     # 无边框
            Qt.WindowStaysOnTopHint |    # 保持最前
            Qt.MaximizeUsingFullscreenGeometryHint  # 使用全屏几何
        )
        
        self.window.setWindowFlags(fullscreen_flags)
        
        # 直接设置到完整屏幕几何
        self.window.setGeometry(full_geometry)
        
        # 确保窗口可见
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        
        # 更新状态
        self.is_fullscreen = True
        
        print(f"✅ 强制全屏完成！尺寸：{full_geometry.width()}×{full_geometry.height()}")
        print(f"   位置：({full_geometry.x()}, {full_geometry.y()})")
        
        # 发送信号
        self.fullscreen_entered.emit()
        self.fullscreen_toggled.emit(True)
        self._update_maximize_button(True)
    
    def get_screen_info(self):
        """获取屏幕信息"""
        info = {
            'primary_screen': {
                'geometry': self.primary_screen.geometry(),
                'available_geometry': self.primary_screen.availableGeometry(),
                'name': self.primary_screen.name()
            },
            'all_screens': [],
            'current_screen': None
        }
        
        for i, screen in enumerate(self.all_screens):
            screen_info = {
                'index': i,
                'geometry': screen.geometry(),
                'available_geometry': screen.availableGeometry(),
                'name': screen.name(),
                'is_primary': screen == self.primary_screen
            }
            info['all_screens'].append(screen_info)
        
        # 当前屏幕信息
        current = self._get_window_screen()
        info['current_screen'] = {
            'geometry': current.geometry(),
            'available_geometry': current.availableGeometry(),
            'name': current.name()
        }
        
        return info
    
    def switch_to_screen(self, screen_index):
        """切换到指定屏幕的全屏模式"""
        if 0 <= screen_index < len(self.all_screens):
            target_screen = self.all_screens[screen_index]
            
            if self.is_fullscreen:
                # 如果已经全屏，直接切换屏幕
                screen_geometry = target_screen.geometry()
                self.window.setGeometry(screen_geometry)
                self.current_screen = target_screen
                print(f"✅ 已切换到屏幕 {screen_index + 1}")
            else:
                # 进入指定屏幕的全屏模式
                self.enter_fullscreen(target_screen)
    
    def get_status(self):
        """获取全屏管理器状态"""
        return {
            'is_fullscreen': self.is_fullscreen,
            'current_screen': self.current_screen.name() if self.current_screen else None,
            'normal_geometry': self.normal_geometry,
            'total_screens': len(self.all_screens)
        }


def integrate_fullscreen_manager(main_window):
    """为主窗口集成全屏管理器"""
    # 创建全屏管理器
    main_window.fullscreen_manager = FullScreenManager(main_window)
    
    # 替换原有的最大化方法
    def new_toggle_maximize():
        """新的全屏切换方法"""
        main_window.fullscreen_manager.toggle_fullscreen()
    
    # 保存原始方法
    main_window._original_toggle_maximize = main_window.toggle_maximize
    main_window.toggle_maximize = new_toggle_maximize
    
    # 连接信号
    main_window.fullscreen_manager.fullscreen_entered.connect(
        lambda: print("📢 信号：已进入全屏模式")
    )
    main_window.fullscreen_manager.fullscreen_exited.connect(
        lambda: print("📢 信号：已退出全屏模式")
    )
    
    print("✅ 全屏管理器已集成到主窗口")
    return main_window.fullscreen_manager 