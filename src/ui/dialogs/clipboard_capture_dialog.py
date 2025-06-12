import os
import time
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QListWidget, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QTimer

import win32gui
import win32con
import win32api
import pyperclip

class ClipboardCaptureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("输出区域捕获")
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 初始化变量
        self.target_window = None
        self.target_window_title = ""
        self.capture_hotkey = "Ctrl+C"  # 默认使用Ctrl+C
        self.mouse_hook = False
        self.calibration_timer = None
        
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 添加说明标签
        instruction_label = QLabel(
            '本功能通过模拟热键操作来捕获其他应用的输出内容。\n'
            '使用步骤：\n'
            '1. 点击"选择窗口"按钮\n'
            '2. 在弹出的窗口列表中选择目标应用\n'
            '3. 点击"捕获内容"按钮，工具会自动激活目标窗口并执行复制操作'
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # 添加窗口选择区域
        window_layout = QHBoxLayout()
        window_layout.addWidget(QLabel("目标窗口:"))
        
        self.window_label = QLabel("未选择")
        self.window_label.setStyleSheet("font-weight: bold; color: #666;")
        window_layout.addWidget(self.window_label, 1)
        
        self.select_window_btn = QPushButton("选择窗口")
        self.select_window_btn.clicked.connect(self.select_window)
        window_layout.addWidget(self.select_window_btn)
        
        layout.addLayout(window_layout)
        
        # 添加热键选择
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(QLabel("捕获热键:"))
        
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems(["Ctrl+A 然后 Ctrl+C", "Ctrl+C", "Ctrl+Insert"])
        self.hotkey_combo.currentTextChanged.connect(self.on_hotkey_changed)
        hotkey_layout.addWidget(self.hotkey_combo)
        
        layout.addLayout(hotkey_layout)
        
        # 添加状态信息列表
        self.info_list = QListWidget()
        self.info_list.addItem("请先选择目标窗口")
        layout.addWidget(self.info_list)
        
        # 添加按钮区域
        button_layout = QHBoxLayout()
        
        self.capture_button = QPushButton("捕获内容")
        self.capture_button.clicked.connect(self.capture_content)
        self.capture_button.setEnabled(False)
        button_layout.addWidget(self.capture_button)
        
        self.test_button = QPushButton("测试")
        self.test_button.clicked.connect(self.test_capture)
        self.test_button.setEnabled(False)
        button_layout.addWidget(self.test_button)
        
        self.clear_button = QPushButton("清除设置")
        self.clear_button.clicked.connect(self.clear_settings)
        self.clear_button.setEnabled(False)
        button_layout.addWidget(self.clear_button)
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def select_window(self):
        """选择目标窗口"""
        # 显示选择方式对话框
        method_dialog = QDialog(self)
        method_dialog.setWindowTitle("选择方式")
        method_dialog.setWindowFlags(method_dialog.windowFlags() | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(method_dialog)
        layout.addWidget(QLabel("请选择窗口选择方式:"))
        
        # 添加两个选择按钮
        calibrate_button = QPushButton("校准方式 (点击目标窗口)")
        calibrate_button.clicked.connect(lambda: self.start_calibration(method_dialog))
        layout.addWidget(calibrate_button)
        
        list_button = QPushButton("列表方式 (从窗口列表中选择)")
        list_button.clicked.connect(lambda: self.show_window_list(method_dialog))
        layout.addWidget(list_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(method_dialog.reject)
        layout.addWidget(cancel_button)
        
        method_dialog.exec_()
    
    def start_calibration(self, parent_dialog=None):
        """开始校准流程"""
        try:
            # 如果有父对话框，关闭它
            if parent_dialog:
                parent_dialog.accept()
                
            # 显示提示信息
            QMessageBox.information(self, "提示", "请点击要捕获内容的目标窗口...")
            
            # 隐藏对话框
            self.hide()
            
            # 设置鼠标钩子
            self.mouse_hook = True
            
            # 启动定时器检查鼠标点击
            self.calibration_timer = QTimer(self)
            self.calibration_timer.timeout.connect(self.check_mouse_click)
            self.calibration_timer.start(100)  # 每100ms检查一次
            
        except Exception as e:
            print(f"校准过程出错: {str(e)}")
            self.reset_calibration()
            QMessageBox.critical(self, "错误", f"校准过程出错: {str(e)}")
    
    def check_mouse_click(self):
        """检查鼠标点击"""
        try:
            if not hasattr(self, 'mouse_hook') or not self.mouse_hook:
                self.calibration_timer.stop()
                return
                
            if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                # 获取鼠标位置
                point = win32api.GetCursorPos()
                
                # 获取点击的窗口句柄
                hwnd = win32gui.WindowFromPoint(point)
                if hwnd:
                    # 获取窗口标题
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        self.target_window = hwnd
                        self.target_window_title = title
                        
                        # 更新UI
                        self.window_label.setText(title)
                        self.info_list.clear()
                        self.info_list.addItem(f"已选择窗口: {title}")
                        self.info_list.addItem(f"窗口句柄: {hwnd}")
                        self.info_list.addItem(f"捕获热键: {self.capture_hotkey}")
                        
                        # 启用按钮
                        self.capture_button.setEnabled(True)
                        self.test_button.setEnabled(True)
                        self.clear_button.setEnabled(True)
                        
                        # 停止校准
                        self.reset_calibration()
                        
                        # 显示对话框
                        self.show()
                        self.activateWindow()
                        return
                        
        except Exception as e:
            print(f"检查鼠标点击出错: {str(e)}")
            self.reset_calibration()
            self.show()
            QMessageBox.critical(self, "错误", f"校准过程出错: {str(e)}")
    
    def reset_calibration(self):
        """重置校准状态"""
        self.mouse_hook = False
        if hasattr(self, 'calibration_timer') and self.calibration_timer.isActive():
            self.calibration_timer.stop()
    
    def show_window_list(self, parent_dialog=None):
        """显示窗口列表选择对话框"""
        # 如果有父对话框，关闭它
        if parent_dialog:
            parent_dialog.accept()
            
        # 枚举所有可见窗口
        windows = []
        
        def enum_windows_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if window_title and len(window_title) > 0:
                    results.append((hwnd, window_title))
            return True
        
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        # 创建窗口选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("选择窗口")
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("请选择要捕获内容的窗口:"))
        
        window_list = QListWidget()
        for hwnd, title in windows:
            window_list.addItem(f"{title} (句柄: {hwnd})")
            
        layout.addWidget(window_list)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(dialog.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        if dialog.exec_() == QDialog.Accepted and window_list.currentItem():
            selected_text = window_list.currentItem().text()
            handle_start = selected_text.rfind("句柄: ") + 5
            handle_end = selected_text.rfind(")")
            
            try:
                hwnd = int(selected_text[handle_start:handle_end])
                title = win32gui.GetWindowText(hwnd)
                
                self.target_window = hwnd
                self.target_window_title = title
                
                self.window_label.setText(title)
                self.info_list.clear()
                self.info_list.addItem(f"已选择窗口: {title}")
                self.info_list.addItem(f"窗口句柄: {hwnd}")
                self.info_list.addItem(f"捕获热键: {self.capture_hotkey}")
                
                # 启用按钮
                self.capture_button.setEnabled(True)
                self.test_button.setEnabled(True)
                self.clear_button.setEnabled(True)
                
            except Exception as e:
                QMessageBox.warning(self, "错误", f"选择窗口失败: {str(e)}")
    
    def on_hotkey_changed(self, hotkey):
        """热键选择改变事件"""
        self.capture_hotkey = hotkey
        if self.target_window:
            # 更新信息
            self.info_list.clear()
            self.info_list.addItem(f"已选择窗口: {self.target_window_title}")
            self.info_list.addItem(f"窗口句柄: {self.target_window}")
            self.info_list.addItem(f"捕获热键: {self.capture_hotkey}")
    
    def capture_content(self):
        """捕获目标窗口内容"""
        if not self.target_window:
            QMessageBox.warning(self, "错误", "请先选择目标窗口")
            return
        
        try:
            # 保存当前活动窗口
            current_window = win32gui.GetForegroundWindow()
            
            # 激活目标窗口
            win32gui.SetForegroundWindow(self.target_window)
            time.sleep(0.5)  # 等待窗口激活
            
            # 根据选择的热键执行不同的复制操作
            if self.capture_hotkey == "Ctrl+A 然后 Ctrl+C":
                # 全选
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(ord('A'), 0, 0, 0)
                time.sleep(0.2)
                win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.2)
                
                # 复制
                win32api.keybd_event(ord('C'), 0, 0, 0)
                time.sleep(0.2)
                win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                
            elif self.capture_hotkey == "Ctrl+C":
                # 直接复制
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(ord('C'), 0, 0, 0)
                time.sleep(0.2)
                win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                
            elif self.capture_hotkey == "Ctrl+Insert":
                # 使用Ctrl+Insert复制
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(win32con.VK_INSERT, 0, 0, 0)
                time.sleep(0.2)
                win32api.keybd_event(win32con.VK_INSERT, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 等待复制操作完成
            time.sleep(0.5)
            
            # 切回原窗口
            win32gui.SetForegroundWindow(current_window)
            time.sleep(0.3)
            
            # 获取剪贴板内容
            text = pyperclip.paste()
            
            # 将内容传递给父窗口
            if self.parent and hasattr(self.parent, 'command_input'):
                self.parent.command_input.setText(text)
                
                # 如果父窗口有日志记录功能，也记录到日志
                if hasattr(self.parent, 'log_file') and self.parent.log_file:
                    try:
                        with open(self.parent.log_file, 'a', encoding='utf-8') as f:
                            import datetime
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            f.write(f"\n# {timestamp} (从{self.target_window_title}获取)\n\n{text}\n")
                    except Exception as e:
                        QMessageBox.warning(self, "错误", f"记录日志失败: {str(e)}")
            
            return True, text
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"捕获内容失败: {str(e)}")
            return False, str(e)
    
    def test_capture(self):
        """测试捕获功能"""
        success, result = self.capture_content()
        
        if success:
            # 显示前100个字符
            preview = result[:100] + ("..." if len(result) > 100 else "")
            QMessageBox.information(self, "成功", f"成功获取内容:\n{preview}")
        else:
            QMessageBox.warning(self, "失败", f"获取内容失败: {result}")
    
    def clear_settings(self):
        """清除设置"""
        if QMessageBox.question(self, "确认", "确定要清除设置吗？") == QMessageBox.Yes:
            self.target_window = None
            self.target_window_title = ""
            
            self.window_label.setText("未选择")
            self.info_list.clear()
            self.info_list.addItem("请先选择目标窗口")
            
            # 禁用按钮
            self.capture_button.setEnabled(False)
            self.test_button.setEnabled(False)
            self.clear_button.setEnabled(False)
            
            QMessageBox.information(self, "成功", "已清除设置")
    
    def get_settings(self):
        """获取当前设置"""
        if self.target_window:
            return {
                "window_handle": self.target_window,
                "window_title": self.target_window_title,
                "capture_hotkey": self.capture_hotkey
            }
        return None
