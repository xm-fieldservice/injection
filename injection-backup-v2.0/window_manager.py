"""
窗口管理器模块 - injection项目模块化解耦方案

统一管理窗口状态、标志和全屏功能，解决多处设置冲突的问题。
这是模块化解耦方案的核心组件之一。

功能：
1. 统一窗口标志管理
2. 窗口状态监控和恢复
3. 全屏模式集成
4. 最大化按钮修复
5. 多显示器支持
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import time


class WindowState:
    """窗口状态数据类"""
    def __init__(self):
        self.geometry = None
        self.flags = None
        self.state = None
        self.is_fullscreen = False
        self.timestamp = time.time()


class WindowManager(QObject):
    """窗口管理器 - 统一管理所有窗口相关功能"""
    
    # 信号定义
    window_state_changed = pyqtSignal(str, dict)  # 窗口状态变化信号
    maximize_button_fixed = pyqtSignal(bool)      # 最大化按钮修复信号
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.window_state = WindowState()
        self.last_flags_check = 0
        
        # 正确的窗口标志配置
        self.correct_flags = (
            Qt.WindowStaysOnTopHint | 
            Qt.Window | 
            Qt.WindowMaximizeButtonHint | 
            Qt.WindowMinimizeButtonHint | 
            Qt.WindowCloseButtonHint
        )
        
        # 初始化
        self._init_window_manager()
        
        print("🔧 窗口管理器已初始化")
    
    def _init_window_manager(self):
        """初始化窗口管理器"""
        # 创建定时器监控窗口状态
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_window_state)
        self.monitor_timer.start(1000)  # 每秒检查一次
        
        # 延迟应用初始设置
        QTimer.singleShot(100, self._apply_initial_setup)
        QTimer.singleShot(500, self._force_maximize_button_fix)
        QTimer.singleShot(1000, self._verify_and_enforce)
    
    def _apply_initial_setup(self):
        """应用初始窗口设置"""
        print("🔧 [窗口管理器] 应用初始窗口设置...")
        
        # 强制设置正确的窗口标志
        self._set_window_flags(self.correct_flags)
        
        # 保存当前状态
        self._save_current_state()
    
    def _force_maximize_button_fix(self):
        """强制修复最大化按钮"""
        print("🔧 [窗口管理器] 强制修复最大化按钮...")
        
        # 方法1：重新创建窗口标志
        self.main_window.setWindowFlags(self.correct_flags)
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        
        # 方法2：强制更新窗口系统
        self.main_window.update()
        QApplication.processEvents()
        
        # 验证结果
        current_flags = self.main_window.windowFlags()
        has_maximize = bool(current_flags & Qt.WindowMaximizeButtonHint)
        
        print(f"🔍 [窗口管理器] 最大化按钮标志检查：{'✅ 存在' if has_maximize else '❌ 缺失'}")
        
        # 发送修复信号
        self.maximize_button_fixed.emit(has_maximize)
        
        if not has_maximize:
            print("⚠️ [窗口管理器] 最大化按钮仍然缺失，尝试替代方案...")
            self._try_alternative_fix()
    
    def _try_alternative_fix(self):
        """尝试替代修复方案"""
        print("🔧 [窗口管理器] 尝试替代修复方案...")
        
        # 方案1：完全重建窗口
        try:
            # 保存当前几何信息
            geometry = self.main_window.geometry()
            
            # 隐藏窗口
            self.main_window.hide()
            
            # 清除所有标志后重新设置
            self.main_window.setWindowFlags(Qt.Widget)  # 清除所有标志
            QApplication.processEvents()
            
            # 重新设置正确标志
            self.main_window.setWindowFlags(self.correct_flags)
            
            # 恢复几何信息并显示
            self.main_window.setGeometry(geometry)
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            print("✅ [窗口管理器] 替代修复方案执行完成")
            
        except Exception as e:
            print(f"❌ [窗口管理器] 替代修复失败：{e}")
    
    def _verify_and_enforce(self):
        """验证并强制执行正确设置"""
        print("🔍 [窗口管理器] 最终验证窗口状态...")
        
        current_flags = self.main_window.windowFlags()
        
        # 详细标志分析
        flag_analysis = {
            'Window': bool(current_flags & Qt.Window),
            'StaysOnTop': bool(current_flags & Qt.WindowStaysOnTopHint),
            'MaximizeButton': bool(current_flags & Qt.WindowMaximizeButtonHint),
            'MinimizeButton': bool(current_flags & Qt.WindowMinimizeButtonHint),
            'CloseButton': bool(current_flags & Qt.WindowCloseButtonHint),
            'Frameless': bool(current_flags & Qt.FramelessWindowHint)
        }
        
        print("📋 [窗口管理器] 当前窗口标志分析：")
        for flag_name, exists in flag_analysis.items():
            status = "✅" if exists else "❌"
            print(f"   {status} {flag_name}: {exists}")
        
        # 检查是否需要强制修复
        if not flag_analysis['MaximizeButton']:
            print("⚠️ [窗口管理器] 最大化按钮标志仍然缺失，执行最终强制修复...")
            self._final_force_fix()
        else:
            print("✅ [窗口管理器] 窗口标志验证通过")
    
    def _final_force_fix(self):
        """最终强制修复方案"""
        print("🚀 [窗口管理器] 执行最终强制修复...")
        
        # 获取当前窗口的所有属性
        geometry = self.main_window.geometry()
        is_visible = self.main_window.isVisible()
        is_active = self.main_window.isActiveWindow()
        
        # 创建新的窗口实例（如果可能）
        try:
            # 方案：使用 setParent 重新初始化窗口系统
            self.main_window.setParent(None)
            self.main_window.setWindowFlags(self.correct_flags)
            
            # 恢复状态
            self.main_window.setGeometry(geometry)
            if is_visible:
                self.main_window.show()
            if is_active:
                self.main_window.raise_()
                self.main_window.activateWindow()
            
            print("✅ [窗口管理器] 最终强制修复完成")
            
        except Exception as e:
            print(f"❌ [窗口管理器] 最终修复失败：{e}")
            print("💡 [窗口管理器] 建议：重启应用程序以应用修复")
    
    def _set_window_flags(self, flags):
        """安全设置窗口标志"""
        try:
            old_flags = self.main_window.windowFlags()
            self.main_window.setWindowFlags(flags)
            
            # 记录更改
            print(f"🔧 [窗口管理器] 窗口标志已更新：{old_flags} -> {flags}")
            
        except Exception as e:
            print(f"❌ [窗口管理器] 设置窗口标志失败：{e}")
    
    def _save_current_state(self):
        """保存当前窗口状态"""
        self.window_state.geometry = self.main_window.geometry()
        self.window_state.flags = self.main_window.windowFlags()
        self.window_state.state = self.main_window.windowState()
        self.window_state.timestamp = time.time()
    
    def _monitor_window_state(self):
        """监控窗口状态变化"""
        current_time = time.time()
        
        # 每5秒检查一次标志状态
        if current_time - self.last_flags_check > 5:
            self.last_flags_check = current_time
            
            current_flags = self.main_window.windowFlags()
            has_maximize = bool(current_flags & Qt.WindowMaximizeButtonHint)
            
            if not has_maximize:
                print("⚠️ [窗口管理器] 检测到最大化按钮标志丢失，重新应用...")
                self._set_window_flags(self.correct_flags)
    
    def force_maximize_button_available(self):
        """强制使最大化按钮可用"""
        print("🔧 [窗口管理器] 用户请求强制修复最大化按钮...")
        self._force_maximize_button_fix()
    
    def get_window_info(self):
        """获取窗口信息"""
        current_flags = self.main_window.windowFlags()
        
        return {
            'geometry': self.main_window.geometry(),
            'flags': current_flags,
            'state': self.main_window.windowState(),
            'has_maximize_button': bool(current_flags & Qt.WindowMaximizeButtonHint),
            'is_visible': self.main_window.isVisible(),
            'is_active': self.main_window.isActiveWindow()
        }
    
    def reset_to_correct_state(self):
        """重置到正确的窗口状态"""
        print("🔄 [窗口管理器] 重置窗口到正确状态...")
        
        # 保存当前几何信息
        geometry = self.main_window.geometry()
        
        # 应用正确设置
        self._set_window_flags(self.correct_flags)
        self.main_window.setGeometry(geometry)
        self.main_window.show()
        
        # 验证
        QTimer.singleShot(100, self._verify_and_enforce)


def integrate_window_manager(main_window):
    """为主窗口集成窗口管理器"""
    # 创建窗口管理器
    window_manager = WindowManager(main_window)
    
    # 添加到主窗口
    main_window.window_manager = window_manager
    
    # 连接信号
    window_manager.maximize_button_fixed.connect(
        lambda success: print(f"📢 [窗口管理器] 最大化按钮修复信号：{'成功' if success else '失败'}")
    )
    
    print("✅ [窗口管理器] 已集成到主窗口")
    return window_manager


# 调试和测试功能
def debug_window_flags(window):
    """调试窗口标志"""
    flags = window.windowFlags()
    
    print("🔍 [调试] 窗口标志详细信息：")
    print(f"   原始标志值：{flags}")
    
    flag_checks = [
        ('Qt.Window', Qt.Window),
        ('Qt.Dialog', Qt.Dialog),
        ('Qt.Sheet', Qt.Sheet),
        ('Qt.Drawer', Qt.Drawer),
        ('Qt.Popup', Qt.Popup),
        ('Qt.Tool', Qt.Tool),
        ('Qt.ToolTip', Qt.ToolTip),
        ('Qt.SplashScreen', Qt.SplashScreen),
        ('Qt.Desktop', Qt.Desktop),
        ('Qt.SubWindow', Qt.SubWindow),
        ('Qt.WindowStaysOnTopHint', Qt.WindowStaysOnTopHint),
        ('Qt.WindowStaysOnBottomHint', Qt.WindowStaysOnBottomHint),
        ('Qt.WindowMaximizeButtonHint', Qt.WindowMaximizeButtonHint),
        ('Qt.WindowMinimizeButtonHint', Qt.WindowMinimizeButtonHint),
        ('Qt.WindowCloseButtonHint', Qt.WindowCloseButtonHint),
        ('Qt.FramelessWindowHint', Qt.FramelessWindowHint),
    ]
    
    for name, flag in flag_checks:
        has_flag = bool(flags & flag)
        if has_flag:
            print(f"   ✅ {name}")
    
    return flags 