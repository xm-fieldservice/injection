#!/usr/bin/env python3
"""
最大化按钮修复脚本

专门用于修复injection项目中系统最大化按钮虚化的问题。
通过延迟设置窗口标志来确保按钮正常显示。
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, Qt

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def fix_maximize_button_for_window(window):
    """为指定窗口修复最大化按钮"""
    
    def apply_correct_flags():
        """应用正确的窗口标志"""
        print("🔧 正在修复最大化按钮...")
        
        # 设置完整的窗口标志
        correct_flags = (
            Qt.WindowStaysOnTopHint | 
            Qt.Window | 
            Qt.WindowMaximizeButtonHint | 
            Qt.WindowMinimizeButtonHint | 
            Qt.WindowCloseButtonHint
        )
        
        window.setWindowFlags(correct_flags)
        window.show()
        
        # 验证设置
        current_flags = window.windowFlags()
        if current_flags & Qt.WindowMaximizeButtonHint:
            print("✅ 最大化按钮修复成功！")
        else:
            print("❌ 最大化按钮修复失败，需要进一步调试")
            
        # 打印当前标志状态
        flag_names = []
        if current_flags & Qt.Window:
            flag_names.append("Window")
        if current_flags & Qt.WindowStaysOnTopHint:
            flag_names.append("StaysOnTop")
        if current_flags & Qt.WindowMaximizeButtonHint:
            flag_names.append("MaximizeButton")
        if current_flags & Qt.WindowMinimizeButtonHint:
            flag_names.append("MinimizeButton")
        if current_flags & Qt.WindowCloseButtonHint:
            flag_names.append("CloseButton")
        
        print(f"📋 当前窗口标志：{' | '.join(flag_names)}")
    
    # 延迟100毫秒后应用标志，确保所有初始化完成
    QTimer.singleShot(100, apply_correct_flags)
    
    # 再次延迟500毫秒后检查，作为备用
    QTimer.singleShot(500, apply_correct_flags)


def apply_fix_to_main_window():
    """为主程序应用修复"""
    try:
        # 导入主窗口类
        from main import MainWindow
        
        # 保存原始的 __init__ 方法
        original_init = MainWindow.__init__
        
        def patched_init(self, *args, **kwargs):
            """修补后的初始化方法"""
            # 调用原始初始化
            original_init(self, *args, **kwargs)
            
            # 应用最大化按钮修复
            fix_maximize_button_for_window(self)
            
            print("🔧 已为主窗口应用最大化按钮修复")
        
        # 应用补丁
        MainWindow.__init__ = patched_init
        
        print("✅ 最大化按钮修复补丁已应用")
        return True
        
    except Exception as e:
        print(f"❌ 应用修复补丁失败：{e}")
        return False


def test_window_flags_directly():
    """直接测试窗口标志设置"""
    print("🧪 开始直接测试窗口标志...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    from PyQt5.QtWidgets import QMainWindow, QLabel
    
    # 创建测试窗口
    test_window = QMainWindow()
    test_window.setWindowTitle("最大化按钮测试窗口")
    test_window.setGeometry(400, 400, 500, 300)
    
    # 添加标签
    label = QLabel("请检查右上角的最大化按钮是否可用（不虚化）")
    label.setStyleSheet("padding: 20px; font-size: 14px;")
    test_window.setCentralWidget(label)
    
    # 设置正确的窗口标志
    correct_flags = (
        Qt.WindowStaysOnTopHint | 
        Qt.Window | 
        Qt.WindowMaximizeButtonHint | 
        Qt.WindowMinimizeButtonHint | 
        Qt.WindowCloseButtonHint
    )
    
    test_window.setWindowFlags(correct_flags)
    test_window.show()
    
    # 检查标志
    current_flags = test_window.windowFlags()
    print(f"测试窗口标志设置：{current_flags}")
    
    if current_flags & Qt.WindowMaximizeButtonHint:
        print("✅ 测试窗口的最大化按钮标志已正确设置")
    else:
        print("❌ 测试窗口的最大化按钮标志设置失败")
    
    return test_window


if __name__ == "__main__":
    print("🚀 启动最大化按钮修复工具...")
    
    # 测试1：直接测试窗口标志
    print("\n=== 测试1：直接窗口标志测试 ===")
    test_window_flags_directly()
    
    # 测试2：应用主程序修复
    print("\n=== 测试2：主程序修复应用 ===")
    success = apply_fix_to_main_window()
    
    if success:
        print("✅ 修复脚本准备完毕，现在可以启动主程序")
        print("💡 建议：运行 'python main.py' 来测试修复效果")
    else:
        print("❌ 修复脚本应用失败")
    
    print("\n🎯 修复要点：")
    print("   1. 确保设置 Qt.WindowMaximizeButtonHint 标志")
    print("   2. 在所有初始化完成后重新设置窗口标志")
    print("   3. 避免其他代码覆盖窗口标志设置")
    print("   4. 使用延迟设置来确保标志生效") 