import sys
import os
import time
import win32gui
import win32con
import win32api
import win32clipboard
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QComboBox, QSystemTrayIcon, QMenu, QShortcut, QMessageBox, 
                             QFileDialog, QDialog, QLineEdit, QCheckBox, QInputDialog, QFrame, QListWidget,
                             QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer, QEvent, QBuffer, QByteArray, QUrl
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QImage, QClipboard
import datetime
import json
from template_dialog import TemplateDialog
from template_manager import TemplateManager
from ai_service import AIService
from api_key_dialog import APIKeyDialog
import win32process

# 定义应用程序路径常量
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(APP_DIR, 'config.json')
LOGS_DIR = os.path.join(APP_DIR, 'logs')

# 确保日志目录存在
os.makedirs(LOGS_DIR, exist_ok=True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('提示词注入工具')
        
        # 初始化变量
        self.target_window = None
        self.target_position = None
        self.target_window_title = None  # 添加目标窗口标题变量
        self.log_file = os.path.join(LOGS_DIR, 'commands.md')  # 设置默认日志文件
        self.template_manager = TemplateManager()
        self.ai_service = AIService()
        
        # 默认模板设置
        self.default_scene = None
        self.default_version = None
        
        # 加载配置（需要在UI初始化前加载）
        self.load_config()
        
        self.initUI()
        self.setupTrayIcon()
        self.setupShortcut()
        self.setupCommandArea()
        
    def load_config(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.target_window = config.get('target_window')
                self.target_position = config.get('target_position')
                self.target_window_title = config.get('target_window_title')  # 加载窗口标题
                self.log_file = config.get('log_file')
                
                # 加载默认模板设置
                self.default_scene = config.get('default_scene')
                self.default_version = config.get('default_version')
                
                # 如果日志文件不存在或目录不存在，使用默认路径
                if not self.log_file or not os.path.exists(os.path.dirname(self.log_file)):
                    default_log_file = os.path.join(LOGS_DIR, 'commands.md')
                    self.log_file = default_log_file
                    
                # 确保日志文件目录存在
                log_dir = os.path.dirname(self.log_file)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                    
                # 更新保存配置，确保持久化
                self.save_config()
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
            self.target_window = None
            self.target_position = None
            self.target_window_title = None  # 重置窗口标题
            # 使用默认日志文件
            self.log_file = os.path.join(LOGS_DIR, 'commands.md')
            
            # 确保日志文件目录存在
            log_dir = os.path.dirname(self.log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 保存默认配置
            self.save_config()
        
    def save_config(self):
        config = {
            'target_window': self.target_window,
            'target_position': self.target_position,
            'target_window_title': self.target_window_title,  # 保存窗口标题
            'log_file': self.log_file,
            'default_scene': self.default_scene,
            'default_version': self.default_version
        }
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(CONFIG_PATH)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
        
    def initUI(self):
        self.setWindowTitle('提示词注入工具')
        # 设置窗口无边框和置顶
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        # 设置窗口背景为白色
        self.setStyleSheet("""
            QMainWindow { background-color: white; }
            QTextEdit { 
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 14px;
                color: #666;
            }
        """)
        # 设置窗口大小 - 增加宽度以显示侧栏
        self.setGeometry(100, 100, 800, 500)
        
    def setupCommandArea(self):
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局（水平布局，分为左右两部分）
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 创建左侧面板（垂直布局）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(200)  # 设置左侧面板宽度
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-right: 1px solid #ddd;
            }
        """)
        
        # 创建右侧面板（垂直布局）
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 添加左右面板到主布局
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # ===== 左侧面板内容 =====
        
        # 创建场景列表区域标题
        scene_title = QLabel("场景列表")
        scene_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 5px;
                border-bottom: 1px solid #ddd;
            }
        """)
        left_layout.addWidget(scene_title)
        
        # 创建场景列表区域（使用列表视图）
        scene_layout = QVBoxLayout()
        
        # 场景列表
        self.scene_list = QListWidget()
        self.scene_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e0f0e0;
                color: #333;
                font-weight: bold;
            }
            QListWidget::item:hover {
                background-color: #f0f0f0;
            }
        """)
        self.scene_list.setMinimumHeight(150)  # 设置最小高度
        self.scene_list.currentItemChanged.connect(self.on_scene_item_changed)
        scene_layout.addWidget(self.scene_list)
        
        scene_layout.addWidget(self.scene_list)
        
        # 版本选择下拉框（虚化处理，保持架构不变）
        version_layout = QHBoxLayout()
        version_label = QLabel("版本:")
        version_label.setStyleSheet("""
            QLabel {
                color: #bbb;
                font-size: 11px;
            }
        """)
        version_layout.addWidget(version_label)
        
        self.version_combo = QComboBox()
        self.version_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 3px;
                background-color: #f8f8f8;
                color: #999;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        self.version_combo.currentTextChanged.connect(self.on_version_changed)
        self.version_combo.setEnabled(False)  # 禁用交互，只作为显示
        version_layout.addWidget(self.version_combo)
        
        scene_layout.addLayout(version_layout)
        
        # 添加设为默认按钮
        self.default_button = QPushButton("设为默认")
        self.default_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.default_button.clicked.connect(self.set_default_template)
        scene_layout.addWidget(self.default_button)
        
        left_layout.addLayout(scene_layout)
        
        # 添加一个分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        left_layout.addWidget(separator)
        
        # 创建应用校准区域标题
        calibration_title = QLabel("应用校准")
        calibration_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 5px;
                border-bottom: 1px solid #ddd;
            }
        """)
        left_layout.addWidget(calibration_title)
        
        # 创建应用校准区域
        calibration_layout = QVBoxLayout()
        
        # 校准按钮
        self.calibrate_button = QPushButton("校准目标窗口")
        self.calibrate_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #ccc;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.calibrate_button.clicked.connect(self.start_calibration)
        calibration_layout.addWidget(self.calibrate_button)
        
        left_layout.addLayout(calibration_layout)
        
        # 添加弹性空间
        left_layout.addStretch()
        
        # ===== 右侧面板内容 =====
        
        # 创建标题栏
        title_layout = QHBoxLayout()
        title_layout.addStretch()
        
        # 添加最小化按钮
        minimize_button = QPushButton("－")
        minimize_button.setFixedSize(20, 20)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                border-radius: 10px;
                color: #666;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        minimize_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(minimize_button)
        
        # 添加退出按钮
        exit_button = QPushButton("×")
        exit_button.setFixedSize(20, 20)
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                border-radius: 10px;
                color: #666;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        exit_button.clicked.connect(QApplication.quit)
        title_layout.addWidget(exit_button)
        
        right_layout.addLayout(title_layout)
        
        # 创建日志文件选择区域
        log_layout = QHBoxLayout()
        self.log_file_label = QLabel("未选择日志文件")
        self.log_file_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 12px;
                padding: 5px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
        """)
        if self.log_file:
            self.log_file_label.setText(f"当前日志文件: {os.path.basename(self.log_file)}")
            
        log_layout.addWidget(self.log_file_label)
        
        self.log_file_button = QPushButton("选择日志文件")
        self.log_file_button.clicked.connect(self.select_log_file)
        log_layout.addWidget(self.log_file_button)
        
        right_layout.addLayout(log_layout)
        
        # 创建目标窗口信息区域
        info_layout = QVBoxLayout()
        self.window_info_label = QLabel("目标窗口：未选择")
        self.window_info_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 12px;
                padding: 5px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
        """)
        info_layout.addWidget(self.window_info_label)
        
        self.input_info_label = QLabel("输入框位置：未校准")
        self.input_info_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 12px;
                padding: 5px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
        """)
        info_layout.addWidget(self.input_info_label)
        right_layout.addLayout(info_layout)
        
        # 创建状态标签
        self.status_label = QLabel("未校准目标窗口")
        right_layout.addWidget(self.status_label)
        
        # 创建命令输入框
        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("请输入命令...\n使用 Alt + Enter 注入命令")
        self.command_input.setMinimumHeight(300)
        # 允许接收富文本内容，支持图片显示
        self.command_input.setAcceptRichText(True)
        
        # 设置命令输入框的事件过滤器
        self.command_input.installEventFilter(self)
        right_layout.addWidget(self.command_input)
        
        # 创建按钮区域
        button_layout = QVBoxLayout()
        
        # 创建注入按钮
        self.inject_button = QPushButton("注入命令 (Alt+Enter)")
        self.inject_button.clicked.connect(self.inject_command)
        button_layout.addWidget(self.inject_button)
        
        # 创建清除按钮
        self.clear_button = QPushButton("清除")
        self.clear_button.clicked.connect(self.clear_command)
        button_layout.addWidget(self.clear_button)
        
        # 创建从Cascade获取文本的按钮
        self.cascade_button = QPushButton("从Cascade获取")
        self.cascade_button.clicked.connect(self.capture_cascade_text)
        button_layout.addWidget(self.cascade_button)
        
        right_layout.addLayout(button_layout)
        
        # 创建底部功能按钮区域
        bottom_layout = QHBoxLayout()
        
        # 添加模板管理按钮
        self.template_button = QPushButton("模板管理")
        self.template_button.clicked.connect(self.show_template_dialog)
        bottom_layout.addWidget(self.template_button)
        
        # 添加AI设置按钮
        self.ai_settings_button = QPushButton("AI设置")
        self.ai_settings_button.clicked.connect(self.show_api_settings)
        bottom_layout.addWidget(self.ai_settings_button)
        
        # 添加实时生成修饰词复选框
        self.realtime_check = QCheckBox("实时生成修饰词")
        self.realtime_check.setChecked(False)
        bottom_layout.addWidget(self.realtime_check)
        
        right_layout.addLayout(bottom_layout)
        
        # 更新状态标签
        self.update_status_label()
        
        # 加载场景列表
        self.load_scenes()
        
    def setupTrayIcon(self):
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon('icon.png'))
        
        trayMenu = QMenu()
        showAction = trayMenu.addAction('显示')
        showAction.triggered.connect(self.showWindow)
        quitAction = trayMenu.addAction('退出')
        quitAction.triggered.connect(QApplication.quit)
        
        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.show()

    def setupShortcut(self):
        # 创建快捷键
        self.shortcut = QShortcut(QKeySequence("Shift+F2"), self)
        self.shortcut.activated.connect(self.showWindow)
        
    def showWindow(self):
        self.show()
        self.activateWindow()
        self.command_input.setFocus()
        
    def update_status_label(self):
        if self.target_window and self.target_position:
            app_name = self.target_window_title or win32gui.GetWindowText(self.target_window)
            self.status_label.setText(f"已校准: {app_name}")
            self.window_info_label.setText(f"目标窗口：{app_name}")
            self.input_info_label.setText(f"输入框位置：X={self.target_position[0]}, Y={self.target_position[1]}")
        else:
            self.status_label.setText("未校准目标窗口")
            self.window_info_label.setText("目标窗口：未选择")
            self.input_info_label.setText("输入框位置：未校准")
        
    def start_calibration(self):
        """开始校准流程"""
        try:
            # 显示提示信息
            QMessageBox.information(self, "提示", "请点击目标窗口的命令输入框...")
            
            # 设置鼠标钩子
            self.mouse_hook = True
            self.calibrate_button.setEnabled(False)
            self.calibrate_button.setText("正在校准...")
            
            # 隐藏窗口
            self.hide()
            
            # 启动定时器检查鼠标点击
            self.calibration_timer = QTimer()
            self.calibration_timer.timeout.connect(self.check_mouse_click)
            self.calibration_timer.start(100)  # 每100ms检查一次
            
        except Exception as e:
            print(f"校准过程出错: {str(e)}")
            self.reset_calibration()
            QMessageBox.critical(self, "错误", f"校准过程出错: {str(e)}")

    def check_mouse_click(self):
        """检查鼠标点击"""
        try:
            if not self.mouse_hook:
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
                        # 尝试获取更精确的应用名称
                        app_name = self.get_application_name(hwnd, title)
                        
                        # 转换为窗口坐标
                        client_point = win32gui.ScreenToClient(hwnd, point)
                        self.target_position = client_point
                        self.target_window = hwnd
                        self.target_window_title = app_name  # 保存识别后的应用名称
                        
                        # 保存配置
                        self.save_config()
                        
                        # 更新UI
                        self.calibrate_button.setStyleSheet("""
                            QPushButton {
                                background-color: #4CAF50;
                                color: white;
                                border: none;
                                padding: 8px 16px;
                                border-radius: 4px;
                            }
                        """)
                        self.calibrate_button.setText("已校准")
                        self.calibrate_button.setEnabled(True)
                        
                        # 更新窗口信息
                        self.window_info_label.setText(f"目标窗口：{app_name}")
                        self.input_info_label.setText(f"输入框位置：X={self.target_position[0]}, Y={self.target_position[1]}")
                        self.update_status_label()
                        
                        # 停止校准
                        self.reset_calibration()
                        
                        # 显示主窗口
                        self.show()
                        self.activateWindow()
                        return
                        
        except Exception as e:
            print(f"检查鼠标点击出错: {str(e)}")
            self.reset_calibration()
            self.show()
            QMessageBox.critical(self, "错误", f"校准过程出错: {str(e)}")
            
    def get_application_name(self, hwnd, window_title):
        """获取更精确的应用程序名称"""
        try:
            # 尝试获取进程ID
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            
            # 尝试获取进程名称
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, process_id)
                exe_path = win32process.GetModuleFileNameEx(handle, 0)
                app_name = os.path.basename(exe_path)
                win32api.CloseHandle(handle)
                
                # 去掉扩展名
                app_name = os.path.splitext(app_name)[0]
                
                # 应用名称美化映射表
                app_name_mapping = {
                    'msedgewebview2': 'Edge WebView',
                    'msedge': 'Microsoft Edge',
                    'chrome': 'Google Chrome',
                    'firefox': 'Firefox',
                    'ApplicationFrameHost': 'Windows App',
                    'explorer': 'Windows Explorer',
                    'code': 'VS Code',
                    'devenv': 'Visual Studio',
                    'winword': 'Microsoft Word',
                    'excel': 'Microsoft Excel',
                    'powerpnt': 'Microsoft PowerPoint',
                    'outlook': 'Microsoft Outlook',
                    'notepad': 'Notepad',
                    'notepad++': 'Notepad++',
                    'WindowsTerminal': 'Windows Terminal',
                    'cmd': 'Command Prompt',
                    'powershell': 'PowerShell',
                    'pythonw': 'Python',
                    'windsurf': 'Windsurf',
                }
                
                # 检查是否有映射的更友好名称
                lower_app_name = app_name.lower()
                if lower_app_name in app_name_mapping:
                    app_name = app_name_mapping[lower_app_name]
                
                # 针对特定应用进行特殊处理
                if lower_app_name in ['chrome', 'msedge', 'firefox', 'msedgewebview2'] and 'cursor' in window_title.lower():
                    return "Cursor Editor"
                
                # 如果窗口标题包含特定关键词
                if 'cursor' in window_title.lower():
                    return "Cursor Editor"
                
                # 对话框或元素检测，经常在标题中包含 - 字符
                if ' - ' in window_title:
                    # 尝试从窗口标题中提取应用名称
                    parts = window_title.split(' - ')
                    # 检查是否是应用名称在最后面（如VS Code、Chrome等）
                    if any(browser.lower() in parts[-1].lower() for browser in ['chrome', 'edge', 'firefox', 'opera']):
                        app_title = parts[0]  # 网页标题通常在前面
                    else:
                        app_title = parts[-1]  # 应用名称通常在最后
                    
                    # 如果提取的部分看起来像应用名称，则使用它
                    if len(app_title) < 30 and not app_title.startswith('http'):
                        return app_title
                
                # 特殊处理WebView应用
                if lower_app_name == 'msedgewebview2':
                    # 如果标题有意义，用它来标识应用
                    if window_title and window_title != "msedgewebview2" and len(window_title) < 30:
                        return f"{app_name} - {window_title}"
                
                # 对Chrome Legacy Window特殊处理
                if window_title == "Chrome Legacy Window" and lower_app_name in ['chrome', 'msedge']:
                    # 尝试从父窗口或子窗口获取更有意义的标题
                    parent = win32gui.GetParent(hwnd)
                    if parent:
                        parent_title = win32gui.GetWindowText(parent)
                        if parent_title and parent_title != window_title:
                            if 'cursor' in parent_title.lower():
                                return "Cursor Editor"
                            return parent_title
                    
                    # 遍历子窗口
                    def enum_child_windows(child_hwnd, child_windows):
                        child_title = win32gui.GetWindowText(child_hwnd)
                        if child_title and child_title != window_title:
                            child_windows.append(child_title)
                        return True
                    
                    child_windows = []
                    win32gui.EnumChildWindows(hwnd, enum_child_windows, child_windows)
                    
                    for child_title in child_windows:
                        if 'cursor' in child_title.lower():
                            return "Cursor Editor"
                
                # 如果无法确定更精确的名称，则使用进程名称
                if app_name and app_name.lower() not in ['explorer', 'applicationframehost']:
                    return app_name
            except Exception as e:
                print(f"获取进程名称出错: {str(e)}")
            
            # 如果上述方法失败，则直接使用窗口标题
            return window_title
        except Exception as e:
            print(f"获取应用名称出错: {str(e)}")
            return window_title
            
    def reset_calibration(self):
        """重置校准状态"""
        self.mouse_hook = False
        if self.calibration_timer:
            self.calibration_timer.stop()
        self.calibrate_button.setEnabled(True)
        if not self.target_window:
            self.calibrate_button.setText("校准目标窗口")

    def on_version_changed(self, version):
        """版本选择改变事件"""
        # 更新UI状态，显示当前选择的模板
        current_item = self.scene_list.currentItem()
        if current_item and version:
            scene_text = current_item.text()
            scene = scene_text.replace("★ ", "") if scene_text.startswith("★ ") else scene_text
            template = self.template_manager.get_template(scene, version)
            if template:
                # 可以在这里更新UI显示模板内容
                # 例如显示前缀和后缀在某个预览区域
                pass
            
            # 更新"设为默认"按钮状态
            self.update_default_button_state()
    
    def update_default_button_state(self):
        """统一更新默认按钮状态"""
        current_item = self.scene_list.currentItem()
        if current_item:
            scene_text = current_item.text()
            scene = scene_text.replace("★ ", "") if scene_text.startswith("★ ") else scene_text
            version = self.version_combo.currentText()
            
            # 检查当前选择是否为默认模板
            is_default = (self.default_scene == scene and self.default_version == version)
            
            if is_default:
                self.default_button.setText("已设为默认 ✓")
                self.default_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 4px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
            else:
                self.default_button.setText("设为默认")
                self.default_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 4px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
            
            # 确保按钮始终可见并启用
            self.default_button.setVisible(True)
            self.default_button.setEnabled(True)
        
    def show_template_dialog(self):
        """显示模板管理对话框"""
        dialog = TemplateDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 保存当前选择的场景和版本
            current_scene = ""
            current_version = ""
            current_item = self.scene_list.currentItem()
            if current_item:
                current_scene = current_item.text()
                current_version = self.version_combo.currentText()
            
            # 强制重新加载模板缓存，确保模板修改立即生效
            self.template_manager.templates = self.template_manager.load_templates()
            
            # 重新加载场景列表
            self.load_scenes()
            
            # 尝试恢复之前的选择
            if current_scene in self.template_manager.get_scenes():
                # 找到并选中之前的场景
                for i in range(self.scene_list.count()):
                    if self.scene_list.item(i).text() == current_scene:
                        self.scene_list.setCurrentRow(i)
                        break
                
                self.load_versions(current_scene)
                
                versions = self.template_manager.get_scene_versions(current_scene)
                if current_version in versions:
                    self.version_combo.setCurrentText(current_version)
            
    def show_api_settings(self):
        """显示API设置对话框"""
        dialog = APIKeyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.ai_service.set_api_key(dialog.get_api_key())
            
    def load_api_key(self):
        """加载API密钥"""
        dialog = APIKeyDialog(self)
        api_key = dialog.get_api_key()
        if api_key:
            self.ai_service.set_api_key(api_key)
            
    def get_cursor_project_name(self):
        """识别当前Cursor所在的项目名称"""
        try:
            # 尝试查找Cursor窗口
            cursor_window = None
            cursor_title = ""
            
            def enum_windows_callback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title and ("Cursor" in window_title or "cursor" in window_title):
                        results.append((hwnd, window_title))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            # 优先选择最相关的Cursor窗口
            for hwnd, title in windows:
                if "Cursor" in title:
                    cursor_window = hwnd
                    cursor_title = title
                    break
            
            if cursor_window and cursor_title:
                # 从窗口标题中提取项目名称
                # Cursor窗口标题通常格式为: "filename - project_name - Cursor"
                parts = cursor_title.split(" - ")
                if len(parts) >= 2:
                    # 倒数第二个部分通常是项目名称
                    project_name = parts[-2].strip()
                    if project_name != "Cursor":
                        return project_name
                
                # 如果从标题提取失败，尝试从路径提取
                # 获取窗口的进程信息
                try:
                    thread_id, process_id = win32process.GetWindowThreadProcessId(cursor_window)
                    process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, process_id)
                    if process_handle:
                        # 这里可以进一步获取进程的工作目录
                        # 由于复杂性，我们使用标题中的信息
                        pass
                except:
                    pass
                    
                # 最后的备选方案：使用整个标题
                return cursor_title.replace(" - Cursor", "").strip()
            
            return "Cursor项目"
            
        except Exception as e:
            print(f"获取Cursor项目名称失败: {str(e)}")
            return "未知项目"
            
    def inject_command(self):
        print("DEBUG: inject_command 方法被调用")  # 调试信息
        if not self.target_window or not self.target_position:
            QMessageBox.warning(self, "错误", "请先校准目标窗口")
            return
            
        if not self.log_file:
            QMessageBox.warning(self, "错误", "请先选择日志文件")
            return
            
        command = self.command_input.toPlainText().strip()
        if not command:
            QMessageBox.warning(self, "错误", "请输入命令")
            return
            
        # 获取当前场景
        current_item = self.scene_list.currentItem()
        scene = current_item.text() if current_item else None
        
        # 获取Cursor项目名称
        project_name = self.get_cursor_project_name()
        
        # 保存原始命令内容用于日志记录
        original_command = command
        
        try:
            # 在命令前添加项目标识
            command_with_project = f"【项目：{project_name}】\n{command}"
            
            # 如果启用了实时生成
            if self.realtime_check.isChecked():
                if not self.ai_service.api_key:
                    if QMessageBox.question(self, "提示", "未设置API密钥，是否现在设置？") == QMessageBox.Yes:
                        self.show_api_settings()
                    return
                    
                # 使用AI生成修饰词，基于默认场景
                decorators = self.ai_service.generate_decorators(command_with_project, self.default_scene)
                if decorators:
                    command = f"{decorators['prefix']}\n\n{command_with_project}\n\n{decorators['suffix']}"
                else:
                    command = command_with_project
            else:
                # 始终使用默认模板（而不是当前选择的模板）
                if self.default_scene and self.default_version:
                    template = self.template_manager.get_template(self.default_scene, self.default_version)
                    if template:
                        command = f"{template['prefix']}\n\n{command_with_project}\n\n{template['suffix']}"
                    else:
                        command = command_with_project
                else:
                    command = command_with_project
            
            # 同时复制生成的内容到系统剪贴板
            pyperclip.copy(command)
            
            # 激活目标窗口
            win32gui.SetForegroundWindow(self.target_window)
            time.sleep(0.1)  # 等待窗口激活
            
            # 移动鼠标到目标位置
            point = win32gui.ClientToScreen(self.target_window, self.target_position)
            win32api.SetCursorPos(point)
            time.sleep(0.1)
            
            # 点击目标位置
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.1)
            
            # 将命令复制到剪贴板并使用win32clipboard进行注入
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(command)
            win32clipboard.CloseClipboard()
            
            # 模拟Ctrl+V粘贴
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 模拟回车键
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 记录命令到日志文件
            try:
                # 确保日志文件目录存在
                log_dir = os.path.dirname(self.log_file)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                    
                # 获取时间戳和应用名称
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                app_name = self.target_window_title if self.target_window_title else "未知应用"
                
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    # 时间作为标题，添加应用名称和项目名称
                    f.write(f"\n# {timestamp} ({app_name} - 项目：{project_name})\n\n{original_command}\n")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"记录日志失败：{str(e)}")
                return
                
            # 清除输入框
            self.clear_command()
            
            # 显示小提示，1秒后自动消失
            self.show_mini_notification("命令已注入并复制到剪贴板")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"注入命令失败: {str(e)}")
        
    def clear_command(self):
        self.command_input.clear()
        
    def select_log_file(self):
        # 使用当前日志文件目录作为起始目录
        start_dir = os.path.dirname(self.log_file) if self.log_file else LOGS_DIR
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择日志文件",
            start_dir,
            "Markdown Files (*.md);;All Files (*)"
        )
        if file_path:
            self.log_file = file_path
            self.log_file_label.setText(f"当前日志文件: {os.path.basename(file_path)}")
            
            # 确保日志文件目录存在
            log_dir = os.path.dirname(self.log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            # 立即保存配置以确保持久化
            self.save_config()
            self.show_mini_notification("日志文件已保存")
        
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.trayIcon.showMessage('提示', '程序已最小化到托盘')

    def mousePressEvent(self, event):
        """只处理窗口拖动"""
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event):
        """处理鼠标释放"""
        self.dragPosition = None
        event.accept()

    def mouseMoveEvent(self, event):
        """处理窗口拖动"""
        if event.buttons() == Qt.LeftButton and self.dragPosition is not None:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def eventFilter(self, obj, event):
        """事件过滤器，处理 Alt+Enter 注入命令和 Ctrl+V 粘贴图片"""
        if obj is self.command_input and event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            
            # 检测 Alt+Enter，执行命令注入
            if key == Qt.Key_Return and modifiers == Qt.AltModifier:
                self.inject_command()
                return True
            
            # 检测 Shift+Enter，记笔记功能
            if key == Qt.Key_Return and modifiers == Qt.ShiftModifier:
                self.take_note()
                return True
            
            # 检测 Ctrl+V，处理图片粘贴
            if key == Qt.Key_V and modifiers == Qt.ControlModifier:
                return self.paste_from_clipboard()
            
            # 普通回车键允许换行（返回False让QTextEdit处理）
            if key == Qt.Key_Return and modifiers == Qt.NoModifier:
                return False
            
        return super().eventFilter(obj, event)
        
    def paste_from_clipboard(self):
        """从剪贴板粘贴内容，支持图片和文本"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        # 如果剪贴板包含图片
        if mime_data.hasImage():
            image = clipboard.image()
            if not image.isNull():
                # 将图片插入到文本编辑器
                self.insert_image_to_editor(image)
                self.show_mini_notification("已粘贴图片")
                return True
                
        # 没有图片则让QTextEdit自行处理粘贴
        return False
    
    def insert_image_to_editor(self, image):
        """将图片插入到文本编辑器"""
        try:
            # 调整图片大小，如果太大
            if image.width() > 600:
                image = image.scaledToWidth(600, Qt.SmoothTransformation)
                
            # 创建一个QTextCursor来操作文本编辑器内容
            cursor = self.command_input.textCursor()
            
            # 将QImage转换为QPixmap，然后插入到文档中
            pixmap = QPixmap.fromImage(image)
            self.command_input.document().addResource(
                1,  # QTextDocument.ImageResource
                QUrl("clipboard_image"),
                pixmap
            )
            
            # 使用HTML插入图片
            cursor.insertHtml(f'<img src="clipboard_image" /><br>')
            
            # 显示成功消息
            self.status_label.setText("已粘贴图片")
            
        except Exception as e:
            print(f"插入图片错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"插入图片失败: {str(e)}")
            
    def take_note(self):
        """记录笔记到日志文件"""
        print("DEBUG: take_note 方法被调用")  # 调试信息
        if not self.log_file:
            # 如果没有设置日志文件，使用默认日志文件
            self.log_file = os.path.join(LOGS_DIR, 'commands.md')
            self.log_file_label.setText(f"当前日志文件: {os.path.basename(self.log_file)}")
            self.save_config()
            
        # 获取富文本内容
        note_html = self.command_input.toHtml()
        plain_text = self.command_input.toPlainText().strip()
        
        if not plain_text and "<img" not in note_html:
            QMessageBox.warning(self, "错误", "请输入笔记内容或插入图片")
            return
            
        try:
            # 确保日志文件目录存在
            log_dir = os.path.dirname(self.log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 获取时间戳和应用名称
            timestamp_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            app_name = self.target_window_title if self.target_window_title else "未知应用"
            
            # 标题格式: "# 时间戳 (应用名称)"
            title_text = f"\n# {timestamp_text} ({app_name})\n\n"
            
            # 如果内容中包含图片，保存图片文件并生成Markdown链接
            if "<img" in note_html:
                # 创建图片保存目录
                image_dir = os.path.join(log_dir, "images")
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir, exist_ok=True)
                
                # 获取文档中的图片
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                
                # 从HTML中提取图片
                # 创建一个临时文件来保存剪贴板中的图片
                temp_image_path = os.path.join(image_dir, f"{timestamp}.png")
                
                # 获取当前剪贴板中的图片（如果有）
                clipboard = QApplication.clipboard()
                if clipboard.mimeData().hasImage():
                    image = clipboard.image()
                    if not image.isNull():
                        # 保存图片
                        image.save(temp_image_path)
                        
                        # 创建图片的Markdown链接
                        rel_path = os.path.relpath(temp_image_path, os.path.dirname(self.log_file))
                        rel_path = rel_path.replace("\\", "/")  # 确保使用正斜杠
                        image_md = f"\n![图片]({rel_path})\n"
                        
                        # 写入日志文件
                        with open(self.log_file, 'a', encoding='utf-8') as f:
                            f.write(title_text)
                            
                            # 如果有文本，先写入文本
                            if plain_text.strip():
                                f.write(f"{plain_text}\n\n")
                                
                            # 再写入图片引用
                            f.write(image_md)
                    else:
                        # 没有图片，只写入文本
                        with open(self.log_file, 'a', encoding='utf-8') as f:
                            f.write(title_text)
                            f.write(f"{plain_text}\n")
                else:
                    # 没有图片，只写入文本
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        f.write(title_text)
                        f.write(f"{plain_text}\n")
            else:
                # 纯文本笔记
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(title_text)
                    f.write(f"{plain_text}\n")
                
            # 清除输入框
            self.clear_command()
            
            # 显示成功消息
            self.status_label.setText("笔记已保存")
            # 显示小提示，1秒后自动消失
            self.show_mini_notification("笔记已保存")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存笔记失败：{str(e)}")
            print(f"保存笔记错误: {str(e)}")

    def capture_cascade_text(self):
        """从Cascade窗口捕获文本并显示在输入框中，同时保存到日志"""
        try:
            # 保存当前窗口句柄
            current_window = win32gui.GetForegroundWindow()
            
            # 尝试查找可能的Cascade窗口标题
            possible_titles = ["Cascade", "Codeium", "AI Assistant", "ChatGPT", "Claude", "Chrome Legacy Window"]
            cascade_window = None
            
            # 尝试所有可能的标题
            for title in possible_titles:
                hwnd = win32gui.FindWindow(None, title)
                if hwnd:
                    cascade_window = hwnd
                    self.status_label.setText(f"找到窗口: {title}")
                    break
            
            if not cascade_window:
                # 如果找不到预设标题，尝试枚举所有窗口
                def enum_windows_callback(hwnd, results):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if window_title and len(window_title) > 0:
                            results.append((hwnd, window_title))
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                # 显示窗口选择对话框
                if windows:
                    window_titles = [w[1] for w in windows if w[1]]
                    if window_titles:
                        # 创建简单的窗口选择对话框
                        dialog = QDialog(self)
                        dialog.setWindowTitle("选择窗口")
                        layout = QVBoxLayout(dialog)
                        layout.addWidget(QLabel("请选择要获取文本的窗口:"))
                        
                        list_widget = QComboBox()
                        for title in window_titles:
                            list_widget.addItem(title)
                        layout.addWidget(list_widget)
                        
                        button_box = QHBoxLayout()
                        ok_button = QPushButton("确定")
                        ok_button.clicked.connect(dialog.accept)
                        cancel_button = QPushButton("取消")
                        cancel_button.clicked.connect(dialog.reject)
                        button_box.addWidget(ok_button)
                        button_box.addWidget(cancel_button)
                        layout.addLayout(button_box)
                        
                        if dialog.exec_() == QDialog.Accepted:
                            selected_title = list_widget.currentText()
                            for hwnd, title in windows:
                                if title == selected_title:
                                    cascade_window = hwnd
                                    break
                
                if not cascade_window:
                    self.show_mini_notification("未找到可用窗口")
                    return
            
            # 激活Cascade窗口
            win32gui.SetForegroundWindow(cascade_window)
            time.sleep(0.5)  # 等待窗口激活
            
            # 执行全选和复制操作
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('A'), 0, 0, 0)
            time.sleep(0.2)
            win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.2)
            
            win32api.keybd_event(ord('C'), 0, 0, 0)
            time.sleep(0.2)
            win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.5)  # 等待复制操作完成
            
            # 获取剪贴板内容
            text = pyperclip.paste()
            
            # 切回原窗口
            win32gui.SetForegroundWindow(current_window)
            time.sleep(0.3)
            
            # 将获取的文本显示在输入框中
            if text:
                self.command_input.setText(text)
                
                # 记录到日志文件
                if not self.log_file:
                    self.log_file = os.path.join(LOGS_DIR, 'commands.md')
                    
                try:
                    # 确保日志文件目录存在
                    log_dir = os.path.dirname(self.log_file)
                    if not os.path.exists(log_dir):
                        os.makedirs(log_dir, exist_ok=True)
                        
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        project_name = self.get_cursor_project_name()
                        f.write(f"\n# {timestamp} (从Cascade获取 - 项目：{project_name})\n\n{text}\n")
                        
                    # 显示成功消息
                    self.status_label.setText("已从Cascade获取文本并保存到日志")
                    self.show_mini_notification("已获取Cascade文本")
                    
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"保存日志失败：{str(e)}")
            else:
                self.show_mini_notification("未获取到文本")
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取Cascade文本失败：{str(e)}")
    
    def show_mini_notification(self, message):
        """显示小型提示，自动消失"""
        # 创建一个小的无边框窗口
        notification = QDialog(self)
        notification.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        notification.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置布局
        layout = QVBoxLayout(notification)
        
        # 创建信息图标（直接使用文字，避免加载图片资源）
        icon_label = QLabel("i")
        icon_label.setStyleSheet("QLabel { color: white; font-size: 24px; font-weight: bold; background-color: #2196F3; border-radius: 16px; padding: 8px; }")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(32, 32)  # 固定大小
        
        # 创建消息标签
        msg_label = QLabel(message)
        msg_label.setStyleSheet("QLabel { color: #333333; font-size: 14px; }")
        msg_label.setAlignment(Qt.AlignCenter)
        
        # 添加到布局
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.addWidget(icon_label, 0, Qt.AlignCenter)
        content_layout.addWidget(msg_label)
        content_widget.setStyleSheet("QWidget { background-color: white; border-radius: 8px; }")
        
        layout.addWidget(content_widget)
        
        # 设置大小和位置
        notification.setFixedSize(200, 120)
        notification.move(
            self.x() + (self.width() - notification.width()) // 2,
            self.y() + (self.height() - notification.height()) // 2
        )
        
        # 显示并设置定时器关闭
        notification.show()
        QTimer.singleShot(1000, notification.close)  # 1秒后自动关闭

    def load_scenes(self):
        # 加载场景列表
        scenes = self.template_manager.get_scenes()
        self.scene_list.clear()
        

        
        default_scene_found = False
        
        # 添加场景到列表
        for scene in scenes:
            item = QListWidgetItem(scene)
            self.scene_list.addItem(item)
            
            # 如果是默认场景，标记为选中状态
            if self.default_scene and scene == self.default_scene:
                self.scene_list.setCurrentItem(item)
                self.load_versions(scene)
                default_scene_found = True
                
                # 如果有默认版本，则选中
                if self.default_version:
                    versions = self.template_manager.get_scene_versions(scene)
                    if self.default_version in versions:
                        self.version_combo.setCurrentText(self.default_version)
                        # 添加视觉标识，表示这是默认模板
                        item.setText(f"★ {scene}")
                        item.setToolTip(f"默认场景: {scene}\n默认版本: {self.default_version}")
        
        # 确保按钮始终可见并启用
        self.default_button.setVisible(True)
        self.default_button.setEnabled(True)
        
        # 延迟更新按钮状态，确保UI完全加载后再更新
        QTimer.singleShot(100, self.update_default_button_state)
        
        # 如果没有默认场景但有场景，选中第一个
        if not self.default_scene and self.scene_list.count() > 0:
            self.scene_list.setCurrentRow(0)
            first_scene = self.scene_list.item(0).text()
            self.load_versions(first_scene)
            
    def load_versions(self, scene):
        # 加载版本列表
        if scene:
            versions = self.template_manager.get_scene_versions(scene)
            self.version_combo.clear()
            self.version_combo.addItems(versions)
            
    def on_scene_item_changed(self, current, previous):
        # 场景选择改变事件
        if current:
            scene_text = current.text()
            scene = scene_text.replace("★ ", "") if scene_text.startswith("★ ") else scene_text
            self.load_versions(scene)
            
            # 延迟更新按钮状态，等待版本加载完成
            QTimer.singleShot(50, self.update_default_button_state)
            


    def set_default_template(self):
        """设置当前选择的模板为默认模板"""
        current_item = self.scene_list.currentItem()
        if current_item:
            # 获取纯净的场景名称（去掉★符号）
            scene_text = current_item.text()
            scene = scene_text.replace("★ ", "") if scene_text.startswith("★ ") else scene_text
            version = self.version_combo.currentText()

            if scene and version:
                # 先清除之前的默认标记
                for i in range(self.scene_list.count()):
                    item = self.scene_list.item(i)
                    if item.text().startswith("★ "):
                        item.setText(item.text().replace("★ ", ""))
                        item.setToolTip("")
                
                self.default_scene = scene
                self.default_version = version
                self.save_config()
                
                # 更新UI显示
                current_item.setText(f"★ {scene}")
                current_item.setToolTip(f"默认场景: {scene}\n默认版本: {version}")
                
                # 强制重新加载模板缓存，确保立即生效
                self.template_manager.templates = self.template_manager.load_templates()
                
                # 更新按钮状态
                self.update_default_button_state()
                
                self.show_mini_notification(f"已设置 [{scene} - {version}] 为默认模板")
            else:
                QMessageBox.warning(self, "错误", "请先选择模板版本")
        else:
            QMessageBox.warning(self, "错误", "请先选择场景")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 