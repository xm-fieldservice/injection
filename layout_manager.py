"""
Layout Manager for Injection Tool
布局管理器 - 负责管理injection工具的四区域布局

区域划分：
1. 左侧面板：场景列表和标签区域
2. 命令注入区：中间的命令输入和处理区域  
3. MD阅读区：右侧的日志阅读器面板
4. 列表区域：底部的父子表格区域

作者: AI Assistant
创建时间: 2025-06-08
"""

# 热重载触发 - 2025-06-10 01:35
# [新增] 2025-06-11 00:12:18: 恢复PyQt文件保存对话框功能 (layout_manager.py:45-78)
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
                            QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                            QTabWidget, QPushButton, QGroupBox, QScrollArea, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QObject, pyqtSlot
from PyQt5.QtGui import QFont
import json



class LayoutManager(QWidget):
    """布局管理器 - 两区域布局管理"""
    
    # 信号定义
    layout_changed = pyqtSignal(str, dict)  # 布局变化信号
    region_resized = pyqtSignal(str, int, int)  # 区域大小变化信号
    save_node_requested = pyqtSignal(dict)  # 保存节点请求信号
    
    def __init__(self, parent=None, parent_window=None):
        super().__init__(parent)
        # 兼容热重载时的parent_window参数
        self.parent_window = parent_window if parent_window is not None else parent
        
        # 区域引用
        self.left_panel = None
        self.command_area = None  
        
        # 分割器引用
        self.main_splitter = None
        
        # 持久化相关
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'layout_config.json')
        self.layout_state = None
        
        # 自动保存计时器（防抖）
        from PyQt5.QtCore import QTimer
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_layout_state)
        self.save_delay = 1000  # 1秒延迟保存
        
        # 配置参数 - 屏幕自适应配置，将在init_layout中初始化
        self.config = {
            # 默认值，将在init_layout中基于屏幕尺寸更新
            'left_panel_width': 212,
            'min_widths': {
                'left_panel': 120,
                'command_area': 300
            },
            'min_heights': {
                'command_area': 250
            },
            # 比例配置（用于自动调节）- 屏幕自适应比例
            'ratios': {
                'left_panel_ratio': 0.15
            }
        }
        
        self.init_layout()
    
    def _init_screen_adaptive_config(self):
        """初始化屏幕自适应配置"""
        try:
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                # 使用完整屏幕尺寸而不是可用桌面区域，支持真正的全屏布局
                screen_size = screen.geometry()
                screen_width = screen_size.width()
                screen_height = screen_size.height()
                
                # 更新配置为屏幕自适应值
                self.config.update({
                    'left_panel_width': max(212, int(screen_width * 0.12)),    # 12%屏幕宽度或212px最小值
                    'min_widths': {
                        'left_panel': max(120, int(screen_width * 0.08)),      # 8%屏幕宽度或120px最小值
                        'command_area': max(300, int(screen_width * 0.20))     # 20%屏幕宽度或300px最小值
                    },
                    'min_heights': {
                        'command_area': max(250, int(screen_height * 0.20))   # 20%屏幕高度或250px最小值
                    }
                })
                
                print(f"🖥️ 屏幕自适应配置已初始化：{screen_width}x{screen_height}")
        except Exception as e:
            print(f"⚠️ 屏幕自适应配置初始化失败，使用默认值: {e}")

    def init_layout(self):
        """初始化两区域布局"""
        # 首先初始化屏幕自适应配置
        self._init_screen_adaptive_config()
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # 创建水平分割器（左右分割）
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # 创建两个主要区域
        self.left_panel = self.create_left_panel()
        self.command_area = self.create_command_area()
        
        # 添加到水平分割器
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.command_area)
        
        # 添加到主布局（不再使用垂直分割器）
        main_layout.addWidget(self.main_splitter)
        
        # 设置分割器样式
        self.setup_splitter_styles()
        
        # 设置初始大小
        self.setup_initial_sizes()
        
        # 连接信号
        self.connect_signals()
        
        # 加载保存的布局状态
        layout_loaded = self.load_layout_state()
            
        # 如果没有加载到配置，强制应用默认布局
        if not layout_loaded:
            self.apply_default_layout()
    
    def create_left_panel(self):
        """创建左侧面板（场景列表和标签区域）"""
        panel = QWidget()
        panel.setMinimumWidth(self.config['min_widths']['left_panel'])
        panel.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-right: 2px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # 区域标题
        title = QLabel("命令注入区")
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 8px;
                background-color: #e8f4f8;
                border-radius: 4px;
                border: 1px solid #c0d6dc;
            }
        """)
        layout.addWidget(title)
        
        # 添加项目状态信息区域
        status_group = QGroupBox("📊 项目状态信息")
        status_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #17a2b8;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #17a2b8;
                font-size: 12px;
            }
        """)
        
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(6)
        
        # 项目信息行
        project_row = QHBoxLayout()
        project_label_title = QLabel("项目:")
        project_label_title.setStyleSheet("font-weight: bold; color: #555; min-width: 45px; font-size: 11px;")
        project_row.addWidget(project_label_title)
        
        self.left_project_status_label = QLabel("injection 📁")
        self.left_project_status_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 15px;
                padding: 3px 5px;
                background-color: #f5f5f5;
                border-radius: 3px;
            }
        """)
        project_row.addWidget(self.left_project_status_label, 1)
        status_layout.addLayout(project_row)
        
        # 目标窗口信息行
        window_row = QHBoxLayout()
        window_label_title = QLabel("目标:")
        window_label_title.setStyleSheet("font-weight: bold; color: #555; min-width: 45px; font-size: 11px;")
        window_row.addWidget(window_label_title)
        
        self.left_window_status_label = QLabel("Cursor (87347960)")
        self.left_window_status_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 15px;
                padding: 3px 5px;
                background-color: #f5f5f5;
                border-radius: 3px;
            }
        """)
        window_row.addWidget(self.left_window_status_label, 1)
        status_layout.addLayout(window_row)
        
        # 输入位置信息行
        input_row = QHBoxLayout()
        input_label_title = QLabel("坐标:")
        input_label_title.setStyleSheet("font-weight: bold; color: #555; min-width: 45px; font-size: 11px;")
        input_row.addWidget(input_label_title)
        
        self.left_input_status_label = QLabel("X=1654, Y=1039")
        self.left_input_status_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 15px;
                padding: 3px 5px;
                background-color: #f5f5f5;
                border-radius: 3px;
            }
        """)
        input_row.addWidget(self.left_input_status_label, 1)
        status_layout.addLayout(input_row)
        
        # 状态信息行
        status_row = QHBoxLayout()
        status_label_title = QLabel("状态:")
        status_label_title.setStyleSheet("font-weight: bold; color: #555; min-width: 45px; font-size: 11px;")
        status_row.addWidget(status_label_title)
        
        self.left_calibration_status_label = QLabel("未校准目标窗口")
        self.left_calibration_status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 15px;
                padding: 3px 5px;
                background-color: #f5f5f5;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        status_row.addWidget(self.left_calibration_status_label, 1)
        status_layout.addLayout(status_row)
        
        # 项目选择按钮
        project_button_copy = QPushButton("选择项目文件夹")
        project_button_copy.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 6px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        # 连接到主窗口的选择项目文件夹功能
        main_window = self.parent()
        if main_window and hasattr(main_window, 'select_project_folder'):
            project_button_copy.clicked.connect(main_window.select_project_folder)
        status_layout.addWidget(project_button_copy)
        
        layout.addWidget(status_group)
        
        # 预留场景列表区域
        scene_placeholder = QLabel("场景列表区域\n(由主窗口管理)")
        scene_placeholder.setAlignment(Qt.AlignCenter)
        scene_placeholder.setStyleSheet("""
            QLabel {
                color: #666;
                background-color: #fff;
                border: 1px dashed #ccc;
                border-radius: 4px;
                padding: 15px;
                margin: 8px 0;
                font-size: 11px;
            }
        """)
        layout.addWidget(scene_placeholder)
        
        return panel
    
    def update_left_panel_status(self):
        """更新左侧面板的项目状态信息"""
        main_window = self.parent()
        if not main_window:
            return
            
        # 更新项目信息
        if hasattr(main_window, 'project_name') and hasattr(main_window, 'project_folder'):
            if main_window.project_name and main_window.project_folder:
                self.left_project_status_label.setText(f"{main_window.project_name} 📁")
            else:
                self.left_project_status_label.setText("未绑定项目")
        
        # 更新目标窗口信息
        if hasattr(main_window, 'target_window') and hasattr(main_window, 'target_window_title'):
            if main_window.target_window and main_window.target_window_title:
                self.left_window_status_label.setText(f"{main_window.target_window_title}")
            else:
                self.left_window_status_label.setText("目标窗口：未选择")
        
        # 更新输入位置信息
        if hasattr(main_window, 'target_position'):
            if main_window.target_position:
                self.left_input_status_label.setText(f"X={main_window.target_position[0]}, Y={main_window.target_position[1]}")
            else:
                self.left_input_status_label.setText("输入框位置：未校准")
        
        # 更新校准状态
        if hasattr(main_window, 'target_window') and hasattr(main_window, 'target_position'):
            if main_window.target_window and main_window.target_position:
                self.left_calibration_status_label.setText(f"已校准")
                self.left_calibration_status_label.setStyleSheet("""
                    QLabel {
                        color: #28a745;
                        font-size: 15px;
                        padding: 3px 5px;
                        background-color: #d4edda;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                """)
            else:
                self.left_calibration_status_label.setText("未校准目标窗口")
                self.left_calibration_status_label.setStyleSheet("""
                    QLabel {
                        color: #666;
                        font-size: 15px;
                        padding: 3px 5px;
                        background-color: #f5f5f5;
                        border-radius: 3px;
                        font-weight: bold;
                    }
                """)
    
    def create_command_area(self):
        """创建命令注入区域（中间主要区域）- 选项卡样式"""
        area = QWidget()
        area.setMinimumWidth(self.config['min_widths']['command_area'])
        area.setMinimumHeight(self.config['min_heights']['command_area'])
        
        layout = QVBoxLayout(area)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # 区域标题栏
        title_layout = QHBoxLayout()
        
        title_label = QLabel("🏗️ 工作区域")
        title_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #333;
                padding: 8px;
            }
        """)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # 创建选项卡容器
        self.command_tabs = QTabWidget()
        self.command_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #ffffff;
                border-top: 2px solid #f44336;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                color: #666;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                font-weight: bold;
                min-width: 60px;
                max-width: 130px;
            }
            QTabBar::tab:selected {
                background-color: #f44336;
                color: white;
                border-bottom: 1px solid #f44336;
            }
            QTabBar::tab:hover {
                background-color: #ffcdd2;
            }
            QTabBar::tab:selected:hover {
                background-color: #d32f2f;
            }
        """)
        
        # 创建命令注入选项卡
        self.command_injection_tab = QWidget()
        command_injection_layout = QVBoxLayout(self.command_injection_tab)
        command_injection_layout.setContentsMargins(8, 8, 8, 8)
        
        # 命令注入区域占位符（由主窗口填充）
        self.command_placeholder = QLabel("命令注入区域\n(由主窗口管理)")
        self.command_placeholder.setAlignment(Qt.AlignCenter)
        self.command_placeholder.setStyleSheet("""
            QLabel {
                color: #666;
                background-color: #fff;
                border: 1px dashed #ccc;
                border-radius: 4px;
                padding: 40px;
                margin: 8px 0;
            }
        """)
        command_injection_layout.addWidget(self.command_placeholder)
        
        # 创建工具启动页选项卡
        self.tool_launcher_tab = QWidget()
        tool_launcher_layout = QVBoxLayout(self.tool_launcher_tab)
        tool_launcher_layout.setContentsMargins(8, 8, 8, 8)
        
        # 页面标题
        title_label = QLabel("🛠️ 工具启动中心")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #2E7D32;
                padding: 12px;
                background-color: #E8F5E8;
                border-radius: 8px;
                margin-bottom: 16px;
            }
        """)
        tool_launcher_layout.addWidget(title_label)
        
        # 成功启动提示
        success_label = QLabel("✅ 登录页面和问答系统启动成功！")
        success_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        success_label.setAlignment(Qt.AlignCenter)
        success_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                padding: 8px;
                background-color: #F1F8E9;
                border-radius: 6px;
                border: 2px solid #81C784;
                margin-bottom: 16px;
            }
        """)
        tool_launcher_layout.addWidget(success_label)
        
        # 可访问地址区域
        access_label = QLabel("可访问地址:")
        access_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        access_label.setStyleSheet("color: #333; margin-bottom: 8px;")
        tool_launcher_layout.addWidget(access_label)
        
        # 工具链接区域
        tools_widget = QWidget()
        tools_layout = QVBoxLayout(tools_widget)
        tools_layout.setSpacing(8)
        
        # 定义工具项样式
        tool_item_style = """
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                margin: 4px 0;
            }
            QWidget:hover {
                background-color: #f5f5f5;
                border: 1px solid #2196F3;
            }
        """
        
        # 登录页面
        login_widget = QWidget()
        login_widget.setStyleSheet(tool_item_style + """
            QWidget {
                cursor: pointer;
            }
        """)
        login_layout = QHBoxLayout(login_widget)
        login_icon = QLabel("🔒")
        login_icon.setFont(QFont("Arial", 16))
        login_title = QLabel("登录页面")
        login_title.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        login_url = QLabel("http://localhost:3001/auth-block/auth.html")
        login_url.setStyleSheet("color: #1976D2; background-color: #E3F2FD; padding: 4px 8px; border-radius: 3px;")
        login_layout.addWidget(login_icon)
        login_layout.addWidget(login_title)
        login_layout.addWidget(login_url)
        login_layout.addStretch()
        
        # 添加点击事件
        def open_login_page(event):
            import webbrowser
            webbrowser.open("http://localhost:3001/auth-block/auth.html")
        login_widget.mousePressEvent = open_login_page
        
        tools_layout.addWidget(login_widget)
        
        # 问答系统
        qa_widget = QWidget()
        qa_widget.setStyleSheet(tool_item_style + """
            QWidget {
                cursor: pointer;
            }
        """)
        qa_layout = QHBoxLayout(qa_widget)
        qa_icon = QLabel("💬")
        qa_icon.setFont(QFont("Arial", 16))
        qa_title = QLabel("问答系统")
        qa_title.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        qa_url = QLabel("http://localhost:3001/qa-note-block/qa-note.html")
        qa_url.setStyleSheet("color: #1976D2; background-color: #E3F2FD; padding: 4px 8px; border-radius: 3px;")
        qa_layout.addWidget(qa_icon)
        qa_layout.addWidget(qa_title)
        qa_layout.addWidget(qa_url)
        qa_layout.addStretch()
        
        # 添加点击事件
        def open_qa_page(event):
            import webbrowser
            webbrowser.open("http://localhost:3001/qa-note-block/qa-note.html")
        qa_widget.mousePressEvent = open_qa_page
        
        tools_layout.addWidget(qa_widget)
        
        # 主界面
        main_widget = QWidget()
        main_widget.setStyleSheet(tool_item_style + """
            QWidget {
                cursor: pointer;
            }
        """)
        main_layout = QHBoxLayout(main_widget)
        main_icon = QLabel("🏠")
        main_icon.setFont(QFont("Arial", 16))
        main_title = QLabel("主界面")
        main_title.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        main_url = QLabel("http://localhost:3001")
        main_url.setStyleSheet("color: #1976D2; background-color: #E3F2FD; padding: 4px 8px; border-radius: 3px;")
        main_layout.addWidget(main_icon)
        main_layout.addWidget(main_title)
        main_layout.addWidget(main_url)
        main_layout.addStretch()
        
        # 添加点击事件
        def open_main_page(event):
            import webbrowser
            webbrowser.open("http://localhost:3001")
        main_widget.mousePressEvent = open_main_page
        
        tools_layout.addWidget(main_widget)
        
        # 系统状态检查
        health_widget = QWidget()
        health_widget.setStyleSheet(tool_item_style + """
            QWidget {
                cursor: pointer;
            }
        """)
        health_layout = QHBoxLayout(health_widget)
        health_icon = QLabel("📊")
        health_icon.setFont(QFont("Arial", 16))
        health_title = QLabel("系统状态检查")
        health_title.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        health_url = QLabel("http://localhost:3001/health")
        health_url.setStyleSheet("color: #1976D2; background-color: #E3F2FD; padding: 4px 8px; border-radius: 3px;")
        health_layout.addWidget(health_icon)
        health_layout.addWidget(health_title)
        health_layout.addWidget(health_url)
        health_layout.addStretch()
        
        # 添加点击事件
        def open_health_page(event):
            import webbrowser
            webbrowser.open("http://localhost:3001/health")
        health_widget.mousePressEvent = open_health_page
        
        tools_layout.addWidget(health_widget)
        
        tool_launcher_layout.addWidget(tools_widget)
        
        # 测试账户信息
        test_info_label = QLabel("🔧 测试账户信息:")
        test_info_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        test_info_label.setStyleSheet("color: #333; margin: 16px 0 8px 0;")
        tool_launcher_layout.addWidget(test_info_label)
        
        # 账户信息区域
        accounts_widget = QWidget()
        accounts_layout = QVBoxLayout(accounts_widget)
        accounts_layout.setSpacing(4)
        
        # 管理员账户
        admin_label = QLabel("• 管理员: admin / admin123")
        admin_label.setStyleSheet("color: #555; padding: 4px; background-color: #FFF3E0; border-radius: 3px;")
        accounts_layout.addWidget(admin_label)
        
        # 普通用户
        user_label = QLabel("• 普通用户: user / user123")
        user_label.setStyleSheet("color: #555; padding: 4px; background-color: #F3E5F5; border-radius: 3px;")
        accounts_layout.addWidget(user_label)
        
        # 演示用户
        demo_label = QLabel("• 演示用户: demo / demo123")
        demo_label.setStyleSheet("color: #555; padding: 4px; background-color: #E8F5E8; border-radius: 3px;")
        accounts_layout.addWidget(demo_label)
        
        tool_launcher_layout.addWidget(accounts_widget)
        
        # 添加弹性空间
        tool_launcher_layout.addStretch()
        
        # 创建思维导图选项卡 - 临时占位符，等待新HTML页面替换
        self.jsmind_tab = QWidget()
        jsmind_layout = QVBoxLayout(self.jsmind_tab)
        jsmind_layout.setContentsMargins(8, 8, 8, 8)
        
        # 临时占位符内容，避免JavaScriptBridge错误
        placeholder_label = QLabel()
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("""
            QLabel {
                color: #666;
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 40px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        placeholder_label.setText("""
🧠 思维导图选项卡

📋 当前状态：等待新HTML页面集成

🔄 即将替换：
• 移除当前WebChannel通信
• 集成新的左右结构HTML页面
• 统一HTML技术栈

⏳ 暂时使用占位符显示，避免启动错误
        """)
        
        jsmind_layout.addWidget(placeholder_label)
        print("📋 思维导图选项卡已临时解约，使用占位符显示")
        

        
        # 添加选项卡
        self.command_tabs.addTab(self.command_injection_tab, "⚡ 命令注入")
        self.command_tabs.addTab(self.tool_launcher_tab, "🛠️ 工具启动")
        self.command_tabs.addTab(self.jsmind_tab, "🧠 思维导图")
        
        # 设置默认选中第一个选项卡
        self.command_tabs.setCurrentIndex(0)
        
        # 连接选项卡切换信号
        self.command_tabs.currentChanged.connect(self.on_command_tab_changed)
        
        layout.addWidget(self.command_tabs)
        
        return area
    

    


    
    def refresh_node_form_data(self):
        """刷新节点表单数据"""
        try:
            # 更新状态
            self.status_label.setText("🔄 正在刷新数据...")
            
            # 如果当前有选中的节点，重新加载其数据
            if hasattr(self, 'current_node_id') and self.current_node_id:
                self.load_node_to_form(self.current_node_id)
                self.status_label.setText("✅ 数据刷新完成")
            else:
                self.status_label.setText("📋 就绪状态：等待选择节点进行编辑")
                
        except Exception as e:
            self.status_label.setText(f"❌ 刷新失败：{str(e)}")
    
    def on_tag_button_clicked(self):
        """处理标签按钮点击"""
        self.status_label.setText("🏷️ 标签已更新")
    
    def sync_tags_from_mindmap(self):
        """🔄 从标签管理脑图同步标签到当前节点"""
        try:
            # 🎯 获取脑图WebView - 修复访问路径
            web_view = None
            if hasattr(self, 'parent_window') and self.parent_window:
                # 方法1: 通过reader_tabs获取
                if hasattr(self.parent_window, 'layout_manager') and hasattr(self.parent_window.layout_manager, 'reader_tabs'):
                    reader_tabs = self.parent_window.layout_manager.reader_tabs
                    if reader_tabs.count() > 0:
                        # 思维导图选项卡通常是第一个
                        mindmap_widget = reader_tabs.widget(0)
                        if hasattr(mindmap_widget, 'web_view'):
                            web_view = mindmap_widget.web_view
                        elif hasattr(mindmap_widget, 'findChild'):
                            from PyQt5.QtWebEngineWidgets import QWebEngineView
                            web_view = mindmap_widget.findChild(QWebEngineView)
                
                # 方法2: 直接从layout_manager获取
                if not web_view and hasattr(self.parent_window, 'layout_manager'):
                    layout_mgr = self.parent_window.layout_manager
                    if hasattr(layout_mgr, 'mindmap_tab') and hasattr(layout_mgr.mindmap_tab, 'web_view'):
                        web_view = layout_mgr.mindmap_tab.web_view
            
            if web_view:
                # 调用JavaScript的标签同步函数
                js_code = """
                try {
                    if (typeof window.syncTagsFromMindmap === 'function') {
                        var selectedNode = getCurrentJsMind().get_selected_node();
                        if (selectedNode) {
                            var result = window.syncTagsFromMindmap(selectedNode.id);
                            console.log('🔄 PyQt调用标签同步结果:', result);
                            result;
                        } else {
                            console.log('❌ 没有选中的节点');
                            false;
                        }
                    } else {
                        console.log('❌ syncTagsFromMindmap函数不存在');
                        false;
                    }
                } catch (error) {
                    console.error('❌ 标签同步调用失败:', error);
                    false;
                }
                """
                
                web_view.page().runJavaScript(js_code, self.on_tag_sync_result)
                self.status_label.setText("🔄 正在同步标签...")
            else:
                self.status_label.setText("❌ 无法访问脑图视图")
                
        except Exception as e:
            self.status_label.setText(f"❌ 标签同步失败：{str(e)}")
            print(f"❌ 标签同步失败: {e}")
    
    def on_tag_sync_result(self, result):
        """处理标签同步结果"""
        try:
            if result:
                self.status_label.setText("✅ 标签同步成功！")
                # 刷新标签显示
                self.refresh_tags_display()
            else:
                self.status_label.setText("❌ 标签同步失败，请检查控制台")
        except Exception as e:
            self.status_label.setText(f"❌ 处理同步结果失败：{str(e)}")
    
    def debug_tag_sync(self):
        """🔧 调试标签同步功能"""
        try:
            if hasattr(self.parent_window, 'layout_manager') and hasattr(self.parent_window.layout_manager, 'mindmap_tab'):
                mindmap_tab = self.parent_window.layout_manager.mindmap_tab
                if hasattr(mindmap_tab, 'web_view'):
                    web_view = mindmap_tab.web_view
                    
                    # 调用JavaScript的调试函数
                    js_code = """
                    try {
                        if (typeof window.debugTagSync === 'function') {
                            window.debugTagSync();
                            true;
                        } else {
                            console.log('❌ debugTagSync函数不存在');
                            false;
                }
                    } catch (error) {
                        console.error('❌ 调试函数调用失败:', error);
                        false;
                }
                    """
                    
                    web_view.page().runJavaScript(js_code)
                    self.status_label.setText("🔧 调试功能已启动，请查看控制台")
                else:
                    self.status_label.setText("❌ 无法访问脑图视图")
            else:
                self.status_label.setText("❌ 无法访问脑图组件")
                
        except Exception as e:
            self.status_label.setText(f"❌ 调试功能失败：{str(e)}")
            print(f"❌ 调试功能失败: {e}")
    
    def add_custom_tag_to_mindmap(self):
        """➕ 添加自定义标签到标签管理脑图"""
        try:
            custom_tag = self.custom_tag_input.text().strip()
            if not custom_tag:
                self.status_label.setText("❌ 请输入标签名称")
                return
            
            if hasattr(self.parent_window, 'layout_manager') and hasattr(self.parent_window.layout_manager, 'mindmap_tab'):
                mindmap_tab = self.parent_window.layout_manager.mindmap_tab
                if hasattr(mindmap_tab, 'web_view'):
                    web_view = mindmap_tab.web_view
                    
                    # 调用JavaScript添加标签到脑图
                    js_code = f"""
                    try {{
                        // 切换到标签管理脑图
                        if (typeof switchMindmapTab === 'function') {{
                            switchMindmapTab('knowledge');
                        }}
                        
                        // 添加到自定义标签分类
                        if (window.mindmaps && window.mindmaps.knowledge) {{
                            var customCategoryNode = window.mindmaps.knowledge.get_node('custom_tags');
                            if (customCategoryNode) {{
                                var newTagId = 'custom_tag_' + Date.now();
                                window.mindmaps.knowledge.add_node(customCategoryNode, newTagId, '{custom_tag}');
                                
                                // 同步到标签数据库
                                if (typeof syncMindmapToTagDatabase === 'function') {{
                                    syncMindmapToTagDatabase();
                                }}
                                
                                console.log('✅ 已添加自定义标签到脑图: {custom_tag}');
                                true;
                            }} else {{
                                console.log('❌ 未找到自定义标签分类节点');
                                false;
                            }}
                        }} else {{
                            console.log('❌ 标签管理脑图不存在');
                            false;
                        }}
                    }} catch (error) {{
                        console.error('❌ 添加标签到脑图失败:', error);
                        false;
                    }}
                    """
                    
                    web_view.page().runJavaScript(js_code, self.on_add_tag_result)
                    self.status_label.setText(f"➕ 正在添加标签: {custom_tag}")
                else:
                    self.status_label.setText("❌ 无法访问脑图视图")
            else:
                self.status_label.setText("❌ 无法访问脑图组件")
            
        except Exception as e:
            self.status_label.setText(f"❌ 添加标签失败：{str(e)}")
            print(f"❌ 添加标签失败: {e}")
    
    def on_add_tag_result(self, result):
        """处理添加标签结果"""
        try:
            if result:
                tag_name = self.custom_tag_input.text().strip()
                self.custom_tag_input.clear()
                self.status_label.setText(f"✅ 已添加标签到脑图: {tag_name}")
            else:
                self.status_label.setText("❌ 添加标签失败，请检查控制台")
        except Exception as e:
            self.status_label.setText(f"❌ 处理添加结果失败：{str(e)}")
    
    def refresh_tags_display(self):
        """刷新标签显示"""
        try:
            if self.current_node_tags:
                tag_texts = []
                
                # 分类标签
                if self.current_node_tags.get('categories'):
                    tag_texts.append(f"📂 分类: {', '.join(self.current_node_tags['categories'])}")
                
                # 技术标签
                if self.current_node_tags.get('technical'):
                    tag_texts.append(f"⚙️ 技术: {', '.join(self.current_node_tags['technical'])}")
                
                # 状态标签
                if self.current_node_tags.get('status'):
                    tag_texts.append(f"📊 状态: {', '.join(self.current_node_tags['status'])}")
                
                # 自定义标签
                if self.current_node_tags.get('custom'):
                    tag_texts.append(f"🎨 自定义: {', '.join(self.current_node_tags['custom'])}")
                
                if tag_texts:
                    self.tags_display_label.setText(" | ".join(tag_texts))
                    self.tags_display_label.setStyleSheet("""
                        QLabel {
                            background-color: #e8f5e8;
                            border: 1px solid #4CAF50;
                            border-radius: 4px;
                            padding: 6px 10px;
                            font-size: 10px;
                            color: #2e7d32;
                            min-height: 20px;
                        }
                    """)
                else:
                    self.tags_display_label.setText("暂无标签")
                    self.tags_display_label.setStyleSheet("""
                        QLabel {
                            background-color: #f8f9fa;
                            border: 1px solid #dee2e6;
                            border-radius: 4px;
                            padding: 6px 10px;
                            font-size: 10px;
                            color: #6c757d;
                            min-height: 20px;
                        }
                    """)
            else:
                self.tags_display_label.setText("暂无标签")
        except Exception as e:
            print(f"❌ 刷新标签显示失败: {e}")
    
    def add_custom_tag(self):
        """保持兼容性的旧方法"""
        self.add_custom_tag_to_mindmap()
    
    def get_current_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_node_form_data(self):
        """保存节点表单数据"""
        try:
            # 收集表单数据
            node_data = {
                'title': self.node_title_input.text().strip(),
                'content': self.node_content_input.toPlainText().strip(),
                'tags': self.get_selected_tags(),
                'creation_time': self.creation_time_label.text(),
                'author': self.author_label.text(),
                'node_id': getattr(self, 'current_node_id', None)
            }
            
            # 验证数据
            if not node_data['title']:
                self.status_label.setText("❌ 错误：标题不能为空")
                return
            
            # 发送保存信号
            self.save_node_requested.emit(node_data)
            
            # 更新状态
            self.status_label.setText(f"💾 节点已保存：{node_data['title']}")
            
        except Exception as e:
            self.status_label.setText(f"❌ 保存失败：{str(e)}")
    
    def reset_node_form(self):
        """重置节点表单"""
        try:
            self.node_title_input.clear()
            self.node_content_input.clear()
            
            # 取消所有标签选择
            for button in self.tag_buttons:
                button.setChecked(False)
            
            # 重置时间和作者
            from datetime import datetime
            self.creation_time_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.author_label.setText("系统用户")
            
            # 清除当前节点ID
            self.current_node_id = None
            
            self.status_label.setText("🔄 表单已重置，准备创建新节点")
            
        except Exception as e:
            self.status_label.setText(f"❌ 重置失败：{str(e)}")
    
    def delete_node_data(self):
        """删除节点数据"""
        try:
            if not hasattr(self, 'current_node_id') or not self.current_node_id:
                self.status_label.setText("❌ 错误：没有选择要删除的节点")
                return
            
            # 确认删除
            title = self.node_title_input.text().strip()
            
            # 发送删除信号（可以复用save信号，通过特殊标记区分）
            delete_data = {
                'action': 'delete',
                'node_id': self.current_node_id,
                'title': title
            }
            self.save_node_requested.emit(delete_data)
            
            # 重置表单
            self.reset_node_form()
            
            self.status_label.setText(f"🗑️ 节点已删除：{title}")
            
        except Exception as e:
            self.status_label.setText(f"❌ 删除失败：{str(e)}")
    
    def get_selected_tags(self):
        """获取选中的标签"""
        selected_tags = []
        for button in self.tag_buttons:
            if button.isChecked():
                selected_tags.append(button.text())
        return selected_tags
    
    def load_node_to_form(self, node_data):
        """将节点数据加载到表单"""
        try:
            if isinstance(node_data, str):
                # 如果是节点ID，这里可以从某个数据源获取完整数据
                # 暂时使用默认数据
                self.current_node_id = node_data
                self.node_title_input.setText(f"节点 {node_data}")
                self.node_content_input.setText("节点内容...")
            elif isinstance(node_data, dict):
                # 如果是完整的节点数据字典
                self.current_node_id = node_data.get('id', node_data.get('node_id'))
                self.node_title_input.setText(node_data.get('title', ''))
                self.node_content_input.setText(node_data.get('content', ''))
                
                # 🏷️ 增强标签处理 - 支持预设标签+自定义标签
                tags = node_data.get('tags', [])
                if isinstance(tags, str):
                    tags = [tags]
                elif not isinstance(tags, list):
                    tags = []
                
                # 重置所有标签按钮
                for button in self.tag_buttons:
                    button.setChecked(False)
                
                # 预设标签列表
                preset_tags = ["重要", "待办", "已完成", "想法", "资源", "问题"]
                
                # 处理每个标签
                for tag in tags:
                    tag_found = False
                    
                    # 1. 检查预设标签按钮
                    for button in self.tag_buttons:
                        if button.text() == tag:
                            button.setChecked(True)
                            tag_found = True
                            break
                    
                    # 2. 如果是自定义标签，需要动态创建按钮
                    if not tag_found and tag not in preset_tags:
                        try:
                            # 创建新的动态标签按钮（自定义标签）
                            new_tag_btn = QPushButton(tag)
                            new_tag_btn.setCheckable(True)
                            new_tag_btn.setChecked(True)  # 自动选中
                            new_tag_btn.setStyleSheet("""
                                QPushButton {
                                    background-color: #FF9800;
                                    color: white;
                                    border: 1px solid #F57C00;
                                    border-radius: 12px;
                                    padding: 4px 8px;
                                    font-size: 10px;
                                }
                                QPushButton:checked {
                                    background-color: #F57C00;
                                    color: white;
                                    border-color: #E65100;
                                }
                                QPushButton:hover {
                                    background-color: #FB8C00;
                                }
                                QPushButton:checked:hover {
                                    background-color: #E65100;
                                }
                            """)
                            new_tag_btn.clicked.connect(self.on_tag_button_clicked)
                            
                            # 将新标签按钮添加到标签容器中
                            if hasattr(self, 'custom_tag_input') and self.custom_tag_input.parent():
                                tags_widget = self.custom_tag_input.parent()
                                tags_layout = tags_widget.layout()
                                # 在stretch之前插入新按钮
                                stretch_index = tags_layout.count() - 3  # 去掉自定义输入框、添加按钮和stretch
                                tags_layout.insertWidget(stretch_index, new_tag_btn)
                                
                            # 将新按钮添加到标签按钮列表
                            self.tag_buttons.append(new_tag_btn)
                            print(f"✅ 动态创建自定义标签按钮: {tag}")
                            
                        except Exception as e:
                            print(f"❌ 创建自定义标签按钮失败: {tag} - {e}")
                
                print(f"📋 标签加载完成: {tags} (共{len(tags)}个)")
                
                # 设置时间和作者
                creation_time = node_data.get('creation_time', node_data.get('createdTime', '未设置'))
                self.creation_time_label.setText(creation_time)
                self.author_label.setText(node_data.get('author', '系统用户'))
            
            # 更新状态，显示已加载的节点信息
            node_title = self.node_title_input.text()
            selected_tags = self.get_selected_tags()
            tag_info = f"，标签: {', '.join(selected_tags)}" if selected_tags else ""
            self.status_label.setText(f"📝 已加载节点：{node_title}{tag_info}")
            
        except Exception as e:
            self.status_label.setText(f"❌ 加载失败：{str(e)}")
            print(f"❌ 加载节点到表单失败: {e}")

    def save_node_content_to_html(self):
        """🔄 将PyQt表单数据保存到HTML节点结构中 - 双向数据同步的核心功能"""
        try:
            # 检查是否有当前编辑的节点
            if not hasattr(self, 'current_node_id') or not self.current_node_id:
                self.status_label.setText("❌ 错误：没有选择要保存的节点")
                return
            
            # 🎯 收集详情页的所有表单数据
            selected_tags = self.get_selected_tags()
            node_data = {
                'nodeId': self.current_node_id,  # HTML端期望的键名
                'title': self.node_title_input.text().strip(),
                'content': self.node_content_input.toPlainText().strip(),
                'author': self.author_label.text(),
                'createdTime': self.creation_time_label.text(),
                'modifiedTime': '',  # 将在HTML端自动生成
                'tags': selected_tags,
                'tagsCount': len(selected_tags),
                'hasCustomTags': any(tag not in ["重要", "待办", "已完成", "想法", "资源", "问题"] for tag in selected_tags),
                'formSource': 'PyQt_DetailPage',
                'saveTimestamp': self.get_current_timestamp(),
                'dataComplete': True
            }
            
            # 验证数据
            if not node_data['title']:
                self.status_label.setText("❌ 错误：标题不能为空")
                return
            
            # 🎯 通过pyqtSaveNodeContent函数将数据发送到HTML端
            import json
            node_data_json = json.dumps(node_data)
            
            update_command = f"""
            // 🔄 调用PyQt数据接收函数
            try {{
                if (typeof window.pyqtSaveNodeContent === 'function') {{
                    var success = window.pyqtSaveNodeContent({node_data_json});
                    if (success) {{
                        console.log('✅ PyQt数据保存成功');
                    }} else {{
                        console.log('ℹ️ PyQt数据无变化，跳过保存');
                    }}
                }} else {{
                    console.error('❌ pyqtSaveNodeContent函数未定义，请检查HTML页面');
                }}
            }} catch(error) {{
                console.error('❌ 调用PyQt数据保存函数失败:', error);
            }}
            """
            
            # 获取WebView并执行JavaScript - 修复访问路径
            webview_found = False
            
            try:
                # 方法1：通过LayoutManager的jsmind_view访问（推荐）
                if hasattr(self, 'jsmind_view') and self.jsmind_view:
                    if hasattr(self.jsmind_view, 'page'):
                        self.jsmind_view.page().runJavaScript(update_command)
                        webview_found = True
                        print("✅ 通过jsmind_view发送数据到HTML")
                        
                # 方法2：通过parent_window的layout_manager访问
                if not webview_found and hasattr(self.parent_window, 'layout_manager'):
                    layout_manager = self.parent_window.layout_manager
                    if hasattr(layout_manager, 'jsmind_view') and layout_manager.jsmind_view:
                        if hasattr(layout_manager.jsmind_view, 'page'):
                            layout_manager.jsmind_view.page().runJavaScript(update_command)
                            webview_found = True
                            print("✅ 通过parent_window.layout_manager.jsmind_view发送数据到HTML")
                
                if webview_found:
                    # 🎯 详细状态更新
                    content_length = len(node_data['content'])
                    tags_info = f"，{node_data['tagsCount']}个标签" if node_data['tagsCount'] > 0 else ""
                    custom_tag_info = "（含自定义）" if node_data['hasCustomTags'] else ""
                    
                    status_message = f"💾 已保存: {node_data['title']} ({content_length}字符{tags_info}{custom_tag_info})"
                    self.status_label.setText(status_message)
                    
                    print(f"✅ 完整节点数据已保存:")
                    print(f"   📝 标题: {node_data['title']}")
                    print(f"   📄 内容: {content_length}字符")
                    print(f"   👤 作者: {node_data['author']}")
                    print(f"   🏷️ 标签: {node_data['tags']} ({node_data['tagsCount']}个)")
                    print(f"   📅 时间: {node_data['createdTime']} → {node_data['saveTimestamp']}")
                    print(f"   🎯 来源: {node_data['formSource']}")
                else:
                    self.status_label.setText("❌ 错误：无法找到WebView")
                    print("❌ 错误：无法找到可用的WebView")
                    
            except Exception as webview_error:
                self.status_label.setText("❌ 错误：WebView通信失败")
                print(f"❌ WebView通信错误: {webview_error}")
                
        except Exception as e:
            self.status_label.setText(f"❌ 保存失败：{str(e)}")
            print(f"❌ 保存节点内容到HTML失败: {e}")
            import traceback
            traceback.print_exc()


    
    def setup_splitter_styles(self):
        """设置分割器样式"""
        splitter_style = """
            QSplitter::handle {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #d0d0d0;
                border: 1px solid #999999;
            }
            QSplitter::handle:horizontal {
                width: 4px;
                margin: 2px 0;
            }
        """
        
        self.main_splitter.setStyleSheet(splitter_style)
        
        # 防止面板完全折叠
        self.main_splitter.setChildrenCollapsible(False)
    
    def setup_initial_sizes(self):
        """设置初始大小 - 支持自适应"""
        # 获取父窗口大小，如果没有则使用默认值
        if self.parent_window:
            parent_size = self.parent_window.size()
            window_width = parent_size.width()
            window_height = parent_size.height()
        else:
            window_width = 1200  # 默认宽度
            window_height = 800  # 默认高度
        
        # 根据比例计算大小
        left_panel_width = max(
            int(window_width * self.config['ratios']['left_panel_ratio']),
            self.config['min_widths']['left_panel']
        )
        
        # 水平分割器初始大小（左侧面板 + 命令区域）
        command_area_width = window_width - left_panel_width
        self.main_splitter.setSizes([left_panel_width, command_area_width])
        
        # 更新配置
        self.config['left_panel_width'] = left_panel_width
    
    def connect_signals(self):
        """连接信号"""
        # 分割器大小变化信号
        self.main_splitter.splitterMoved.connect(self.on_horizontal_splitter_moved)
    

    
    def on_command_tab_changed(self, index):
        """处理命令区域选项卡切换"""
        if hasattr(self, 'command_tabs'):
            current_tab_text = self.command_tabs.tabText(index)
            self.layout_changed.emit("command_tab_changed", {
                "tab_index": index,
                "tab_name": current_tab_text
            })
            
            # 根据选项卡自动调整界面
            if index == 1:  # 脑图选项卡
                # 可以在这里添加脑图激活时的特殊处理
                pass
                
            # 自动保存布局状态
            self.auto_save_layout()
    
    def inject_mindmap_content(self):
        """工具启动页模式 - 此功能已被工具启动页替代"""
        print("工具启动页模式 - 此功能已被工具启动页替代")
    
    def refresh_mindmap(self):
        """已移除嵌套选项卡结构 - 热重载触发"""
        print("✅ 嵌套选项卡结构已移除，脑图现在直接显示在思维导图选项卡中")
    
    def export_mindmap(self):
        """工具启动页模式 - 此功能已被工具启动页替代"""
        print("工具启动页模式 - 此功能已被工具启动页替代")
    
    def import_mindmap(self):
        """工具启动页模式 - 此功能已被工具启动页替代"""
        print("工具启动页模式 - 此功能已被工具启动页替代")
    
    def add_mindmap_node(self):
        """工具启动页模式 - 此功能已被工具启动页替代"""
        print("工具启动页模式 - 此功能已被工具启动页替代")
    
    def toggle_mindmap_dragging(self):
        """工具启动页模式 - 此功能已被工具启动页替代"""
        print("工具启动页模式 - 此功能已被工具启动页替代")
    
    def show_mindmap_help(self):
        """显示工具启动页使用指南"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout
            
            # 创建帮助对话框
            help_dialog = QDialog(self)
            help_dialog.setWindowTitle("🛠️ 工具启动页使用指南")
            help_dialog.setMinimumSize(600, 500)
            
            layout = QVBoxLayout(help_dialog)
            
            # 帮助内容
            help_content = QTextBrowser()
            help_content.setHtml("""
                <div style="font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; padding: 20px;">
                    <h2 style="color: #4CAF50; text-align: center;">🛠️ 工具启动页使用指南</h2>
                    
                    <h3 style="color: #4CAF50;">📋 主要功能</h3>
                    <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <p><strong>集中管理：</strong>统一管理和启动各种工具服务</p>
                        <p><strong>快速访问：</strong>提供快速访问链接和启动命令</p>
                        <p><strong>状态监控：</strong>显示系统状态和服务信息</p>
                        <p><strong>账户管理：</strong>管理测试账户和访问权限</p>
                    </div>
                    
                    <h3 style="color: #2196F3;">🔗 可访问地址</h3>
                    <ul>
                        <li><strong>🔒 登录页面：</strong> http://localhost:3001/auth-block/auth.html</li>
                        <li><strong>💬 问答系统：</strong> http://localhost:3001/qa-note-block/qa-note.html</li>
                        <li><strong>🏠 主界面：</strong> http://localhost:3001</li>
                        <li><strong>📊 系统状态检查：</strong> http://localhost:3001/health</li>
                    </ul>
                    
                    <h3 style="color: #FF9800;">🔧 测试账户信息</h3>
                    <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <ul>
                            <li><strong>管理员：</strong> admin / admin123</li>
                            <li><strong>普通用户：</strong> user / user123</li>
                            <li><strong>演示用户：</strong> demo / demo123</li>
                        </ul>
                    </div>
                    
                    <h3 style="color: #9C27B0;">💡 使用方法</h3>
                    <ul>
                        <li><strong>直接访问：</strong>点击对应的链接可以直接访问服务</li>
                        <li><strong>复制链接：</strong>复制URL地址到浏览器中访问</li>
                        <li><strong>登录验证：</strong>使用提供的测试账户进行登录验证</li>
                        <li><strong>状态检查：</strong>通过系统状态检查确认服务运行情况</li>
                    </ul>
                    
                    <h3 style="color: #607D8B;">⚙️ 系统要求</h3>
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <ul>
                            <li>✅ 确保本地服务器在端口3001运行</li>
                            <li>✅ 浏览器支持现代web标准</li>
                            <li>✅ 网络连接正常</li>
                        </ul>
                    </div>
                    
                    <h3 style="color: #795548;">🔧 故障排除</h3>
                    <ul>
                        <li><strong>无法访问：</strong>请检查服务是否启动</li>
                        <li><strong>连接拒绝：</strong>确认防火墙设置允许3001端口访问</li>
                        <li><strong>页面无法加载：</strong>检查浏览器是否支持localhost访问</li>
                        <li><strong>登录失败：</strong>确认使用正确的测试账户信息</li>
                    </ul>
                </div>
            """)
            layout.addWidget(help_content)
            
            # 按钮区域
            button_layout = QHBoxLayout()
            
            open_browser_btn = QPushButton("🌐 打开浏览器")
            open_browser_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #45a049; }
            """)
            import webbrowser
            from PyQt5.QtWidgets import QMessageBox
            open_browser_btn.clicked.connect(lambda: webbrowser.open("http://localhost:3001") or QMessageBox.information(help_dialog, "浏览器启动", "已尝试打开浏览器访问主界面。\n如果没有自动打开，请手动复制链接到浏览器中访问。"))
            button_layout.addWidget(open_browser_btn)
            
            button_layout.addStretch()
            
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(help_dialog.accept)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            help_dialog.exec_()
            
        except Exception as e:
            print(f"显示帮助失败: {e}")
    
    def on_node_details_received(self, nodeDetailsJson):
        """处理接收到的节点详情"""
        try:
            node_details = json.loads(nodeDetailsJson)
            print(f"📋 处理节点详情: {node_details['title']}")
            
            # 格式化节点详情为显示文本
            details_text = self.format_node_details(node_details)
            
            # 更新节点详情显示区域
            if hasattr(self, 'mindmap_node_display'):
                self.mindmap_node_display.setPlainText(details_text)
                
                # 自动切换到数据分析选项卡以便编辑
                if hasattr(self, 'reader_tabs'):
                    self.reader_tabs.setCurrentIndex(2)  # 切换到数据分析选项卡
                    
                # 更新同步状态指示器
                if hasattr(self, 'mindmap_sync_indicator'):
                    self.mindmap_sync_indicator.setText(f"🔗 已同步节点: {node_details['title']}")
                    self.mindmap_sync_indicator.setStyleSheet("""
                        QLabel {
                            color: #4CAF50;
                            font-size: 10px;
                            padding: 3px 8px;
                            background-color: #e8f5e8;
                            border-radius: 3px;
                        }
                    """)
            
            # 同时填充数据分析选项卡中的节点表单
            self.populate_analysis_form(node_details)
                
        except Exception as e:
            print(f"❌ 处理节点详情失败: {e}")
    
    def populate_analysis_form(self, node_details):
        """填充数据分析选项卡中的节点表单"""
        try:
            # 🎯 提取并更新标签信息
            node_tags = node_details.get('tags', {})
            self.current_node_tags = {
                'categories': node_tags.get('categories', []),
                'technical': node_tags.get('technical', []),
                'status': node_tags.get('status', []),
                'custom': node_tags.get('custom', [])
            }
            
            # 准备表单数据
            form_data = {
                'id': node_details['id'],
                'title': node_details['title'],
                'content': node_details.get('content', ''),
                'tags': self.extract_node_tags(node_details),
                'creation_time': node_details.get('createdTime', '未设置'),
                'author': node_details.get('author', '系统用户')
            }
            
            # 🏷️ 更新标签显示
            self.refresh_tags_display()
            
            # 加载到表单
            if hasattr(self, 'load_node_to_form'):
                self.load_node_to_form(form_data)
                
            # 节点详情已自动切换到数据分析选项卡，更新状态提示
            if hasattr(self, 'status_label'):
                total_tags = sum(len(tags) for tags in self.current_node_tags.values())
                self.status_label.setText(f"📊 节点已加载: {form_data['title']} (包含 {total_tags} 个标签)")
                
        except Exception as e:
            print(f"❌ 填充分析表单失败: {e}")
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"❌ 加载节点失败：{str(e)}")
    
    def extract_node_tags(self, node_details):
        """从节点详情中提取标签列表 - 增强版"""
        tags = []
        try:
            node_tags = node_details.get('tags', {})
            
            # 🏷️ 优先提取保存的自定义标签（PyQt标签系统）
            if node_tags.get('custom') and isinstance(node_tags['custom'], list):
                tags.extend(node_tags['custom'])
                print(f"✅ 提取到自定义标签: {node_tags['custom']}")
            
            # 🏷️ 提取各类分类标签（HTML端分类系统）
            if node_tags.get('categories'):
                for tag in node_tags['categories']:
                    if tag not in tags:  # 避免重复
                        tags.append(tag)
                        
            if node_tags.get('technical'):
                for tag in node_tags['technical']:
                    if tag not in tags:  # 避免重复
                        tags.append(tag)
                        
            if node_tags.get('status'):
                for tag in node_tags['status']:
                    if tag not in tags:  # 避免重复
                        tags.append(tag)
            
            # 优先级标签（如果有的话）
            if node_tags.get('priority') and node_tags['priority'] not in tags:
                tags.append(node_tags['priority'])
                
            # 如果没有任何标签，根据节点内容推断一些基本标签
            if not tags:
                content = node_details.get('content', '').lower()
                title = node_details.get('title', '').lower()
                
                # 简单的关键词匹配
                if any(word in content or word in title for word in ['重要', '关键', 'important']):
                    tags.append('重要')
                if any(word in content or word in title for word in ['待办', 'todo', '任务']):
                    tags.append('待办')
                if any(word in content or word in title for word in ['想法', 'idea', '思考']):
                    tags.append('想法')
            
            print(f"📋 节点 {node_details['id']} 提取到标签: {tags}")
                    
        except Exception as e:
            print(f"❌ 提取标签失败: {e}")
            
        return tags
    
    def format_node_details(self, node_details):
        """格式化节点详情为显示文本"""
        details_text = f"""📋 思维导图节点详情信息

🏷️ 节点标题: {node_details['title']}

📍 节点路径: {node_details['path']}

🔗 基本信息:
• 节点ID: {node_details['id']}
• 父节点: {node_details['parentNode']}
• 子节点数量: {node_details['childrenCount']} 个
• 创建时间: {node_details['createdTime']}
• 修改时间: {node_details['modifiedTime']}
• 作者: {node_details['author']}

📝 详细内容:
{node_details['content']}

🏷️ 标签信息:"""

        tags = node_details.get('tags', {})
        if tags.get('categories'):
            details_text += f"\n• 分类标签: {', '.join(tags['categories'])}"
        if tags.get('technical'):
            details_text += f"\n• 技术标签: {', '.join(tags['technical'])}"
        if tags.get('status'):
            details_text += f"\n• 状态标签: {', '.join(tags['status'])}"
        
        if not any(tags.values()):
            details_text += "\n• 暂无标签"
            
        details_text += f"""

💡 操作提示:
• 在思维导图中点击不同节点可实时更新此处信息
• 此页面专注于信息展示，编辑请在思维导图中进行
• 详情信息会自动同步到此区域"""

        return details_text
    
    def on_horizontal_splitter_moved(self, pos, index):
        """水平分割器移动事件"""
        sizes = self.main_splitter.sizes()
        self.region_resized.emit("horizontal", pos, index)
        
        # 更新配置
        if len(sizes) >= 2:
            self.config['left_panel_width'] = sizes[0]
        if len(sizes) >= 3:
            self.config['md_reader_width'] = sizes[2]
        
        # 自动保存布局状态
        self.auto_save_layout()
    

    
    def get_region_widget(self, region_name):
        """获取指定区域的Widget"""
        regions = {
            'left_panel': self.left_panel,
            'command_area': self.command_area,
            'command_injection_tab': getattr(self, 'command_injection_tab', None),
            'mindmap_tab': getattr(self, 'mindmap_tab', None)
        }
        return regions.get(region_name)
    
    def set_region_content(self, region_name, widget):
        """设置指定区域的内容Widget"""
        region = self.get_region_widget(region_name)
        if region and hasattr(region, 'layout'):
            # 清除占位符并添加实际内容
            layout = region.layout()
            # 移除占位符（通常是最后一个widget）
            if layout.count() > 1:
                item = layout.takeAt(layout.count() - 1)
                if item.widget():
                    item.widget().deleteLater()
            
            # 添加新内容
            layout.addWidget(widget)
    
    def sync_with_list_selection(self, selected_item_data):
        """与列表选择同步"""
        # 更新同步指示器
        if hasattr(self, 'sync_indicator'):
            self.sync_indicator.setText(f"🔗 同步: {selected_item_data.get('title', '未知项目')}")
            self.sync_indicator.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 11px;
                    padding: 4px 8px;
                    background-color: #e8f5e8;
                    border-radius: 3px;
                }
            """)
        
        if hasattr(self, 'mindmap_sync_indicator'):
            self.mindmap_sync_indicator.setText(f"🧠 分析: {selected_item_data.get('title', '未知项目')}")
            self.mindmap_sync_indicator.setStyleSheet("""
                QLabel {
                    color: #2196F3;
                    font-size: 11px;
                    padding: 4px 8px;
                    background-color: #e3f2fd;
                    border-radius: 3px;
                }
            """)
        
        # 发送同步信号
        self.layout_changed.emit("list_selection_sync", {
            "selected_data": selected_item_data,
            "current_tab": self.reader_tabs.currentIndex() if hasattr(self, 'reader_tabs') else 0
        })
    
    def switch_to_tab(self, tab_name):
        """切换到指定选项卡"""
        if hasattr(self, 'reader_tabs'):
            tab_index_map = {
                "md_reader": 0,
                "mindmap": 1
            }
            if tab_name in tab_index_map:
                self.reader_tabs.setCurrentIndex(tab_index_map[tab_name])
    
    def save_layout_state(self):
        """保存布局状态到文件"""
        try:
            import json
            import datetime
            
            # 安全获取控件状态，防止控件被销毁时出错
            state = {
                'main_splitter_sizes': self.main_splitter.sizes() if hasattr(self, 'main_splitter') else [200, 600],
                'current_command_tab': self.command_tabs.currentIndex() if hasattr(self, 'command_tabs') else 0,
                'config': self.config.copy() if hasattr(self, 'config') else {},
                'window_size': {
                    'width': self.parent_window.width() if self.parent_window and hasattr(self.parent_window, 'width') else 1414,
                    'height': self.parent_window.height() if self.parent_window and hasattr(self.parent_window, 'height') else 1080
                },
                'timestamp': datetime.datetime.now().isoformat(),
                'version': '2.0'
            }
            
            # 验证状态数据的有效性
            if not all(isinstance(size, int) for size in state['main_splitter_sizes']):
                print("⚠️ 主分割器大小数据无效，跳过保存")
                return None
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            self.layout_state = state
            if hasattr(self, 'layout_changed'):
                self.layout_changed.emit("layout_saved", state)
            print(f"✅ 布局状态已保存: {len(state)} 项配置")
            return state
            
        except Exception as e:
            print(f"❌ 保存布局状态失败: {e}")
            return None
    
    def restore_layout_state(self, state):
        """恢复布局状态"""
        if 'main_splitter_sizes' in state:
            self.main_splitter.setSizes(state['main_splitter_sizes'])
        
        if 'config' in state:
            # 只恢复比例配置，保持屏幕自适应计算的尺寸配置
            old_config = state['config']
            if 'ratios' in old_config:
                self.config['ratios'].update(old_config['ratios'])
            print("🔄 已恢复布局比例配置，保持屏幕自适应尺寸")
            
        if 'current_command_tab' in state and hasattr(self, 'command_tabs'):
            self.command_tabs.setCurrentIndex(state['current_command_tab'])
        
        print(f"✅ 布局状态已恢复: {len(state)} 项配置")
    
    def load_layout_state(self):
        """从文件加载布局状态"""
        try:
            import json
            import os
            
            if not os.path.exists(self.config_file):
                print("💡 未找到布局配置文件，将创建默认配置")
                # 立即保存默认配置
                self.force_save_layout()
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # 验证配置文件完整性
            required_keys = ['main_splitter_sizes']
            if not all(key in state for key in required_keys):
                print("⚠️ 配置文件不完整，重新创建默认配置")
                self.force_save_layout()
                return False
            
            # 延迟恢复，确保UI已完全初始化
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(200, lambda: self.restore_layout_state(state))
            
            print(f"✅ 布局配置文件已加载: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 加载布局状态失败: {e}，将创建默认配置")
            # 出错时强制保存默认配置
            self.force_save_layout()
            return False
    
    def auto_save_layout(self):
        """自动保存布局状态（带防抖）"""
        # 重置计时器，实现防抖效果
        self.save_timer.stop()
        self.save_timer.start(self.save_delay)
    def force_save_layout(self):
        """立即强制保存布局状态"""
        # 停止防抖计时器，立即保存
        if hasattr(self, 'save_timer'):
            self.save_timer.stop()
        result = self.save_layout_state()
        if result:
            # 更新按钮状态提供视觉反馈（如果按钮存在）
            if hasattr(self, 'save_layout_btn') and self.save_layout_btn:
                try:
                    original_style = self.save_layout_btn.styleSheet()
                    self.save_layout_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            border: none;
                            border-radius: 16px;
                            font-size: 16px;
                            font-weight: bold;
                        }
                    """)
                    self.save_layout_btn.setText("✅")
                    
                    # 1秒后恢复原样
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(1000, lambda: [
                        self.save_layout_btn.setStyleSheet(original_style),
                        self.save_layout_btn.setText("💾")
                    ])
                    
                    # 显示提示
                    print("🎯 【手动保存】按钮已被点击！布局已立即保存到文件")
                except Exception as e:
                    print(f"⚠️ 按钮状态更新失败: {e}")
            print("✅ 手动保存完成")
        return result
    
    def save_current_size_as_default(self):
        """将当前窗口大小保存为默认大小"""
        try:
            if self.parent_window:
                current_size = self.parent_window.size()
                current_width = current_size.width()
                current_height = current_size.height()
                
                # 更新配置
                self.config['default_window_size'] = {
                    'width': current_width,
                    'height': current_height
                }
                
                # 保存配置到文件
                import json
                with open('layout_config.json', 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                
                print(f"📐 【设置大小】按钮已被点击！")
                print(f"✅ 当前窗口大小已保存为默认：{current_width}x{current_height}")
                
                # 按钮状态反馈
                if hasattr(self, 'set_size_btn') and self.set_size_btn:
                    original_style = self.set_size_btn.styleSheet()
                    self.set_size_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            border: none;
                            border-radius: 16px;
                            font-size: 16px;
                            font-weight: bold;
                        }
                    """)
                    self.set_size_btn.setText("✅")
                    
                    # 1秒后恢复原样
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(1000, lambda: [
                        self.set_size_btn.setStyleSheet(original_style),
                        self.set_size_btn.setText("📐")
                    ])
                
                return True
        except Exception as e:
            print(f"❌ 保存默认大小失败: {e}")
            return False
    
    def apply_default_layout(self):
        """应用默认布局配置"""
        # 确保MD阅读器显示
        if self.md_reader_area.parent() is None:
            self.toggle_md_reader()
        
        # 应用默认大小设置
        self.main_splitter.setSizes([212, 802, 376])
        self.vertical_splitter.setSizes([838, 209])
        
        # 重置选项卡到第一个
        if hasattr(self, 'reader_tabs'):
            self.reader_tabs.setCurrentIndex(0)
        if hasattr(self, 'command_tabs'):
            self.command_tabs.setCurrentIndex(0)
            
        # 立即保存当前布局
        self.force_save_layout()
    
    def auto_adjust_on_resize(self, new_size):
        """窗口大小变化时自动调节布局 - 屏幕自适应增强版"""
        window_width = new_size.width()
        window_height = new_size.height()
        
        # 检测是否需要重新计算屏幕自适应配置
        screen = QApplication.primaryScreen()
        # 使用完整屏幕尺寸，支持真正的全屏布局
        current_screen_size = screen.geometry()
        if (hasattr(self, '_last_screen_size') and 
            self._last_screen_size != (current_screen_size.width(), current_screen_size.height())):
            # 屏幕分辨率发生变化，重新计算最小尺寸配置
            self._update_screen_adaptive_config()
        self._last_screen_size = (current_screen_size.width(), current_screen_size.height())
        
        # 重新计算各区域大小
        left_panel_width = max(
            int(window_width * self.config['ratios']['left_panel_ratio']),
            self.config['min_widths']['left_panel']
        )
        
        list_area_height = max(
            int(window_height * self.config['ratios']['list_area_ratio']),
            self.config['min_heights']['list_area']
        )
        
        # 调整水平分割器
        if self.md_reader_area.parent() is not None:
            # 三面板模式
            md_reader_width = max(
                int(window_width * self.config['ratios']['md_reader_ratio']),
                self.config['min_widths']['md_reader']
            )
            remaining_width = window_width - left_panel_width - md_reader_width
            command_area_width = max(remaining_width, self.config['min_widths']['command_area'])
            
            self.main_splitter.setSizes([
                left_panel_width,
                command_area_width,
                md_reader_width
            ])
        else:
            # 两面板模式
            command_area_width = window_width - left_panel_width
            self.main_splitter.setSizes([left_panel_width, command_area_width])
        
        # 调整垂直分割器
        upper_area_height = window_height - list_area_height
        self.vertical_splitter.setSizes([upper_area_height, list_area_height])
        
        # 更新配置
        self.config['left_panel_width'] = left_panel_width
        self.config['list_area_height'] = list_area_height
        
        # 发送调整完成信号
        self.layout_changed.emit("auto_adjusted", {
            "window_size": {"width": window_width, "height": window_height},
            "new_sizes": {
                "left_panel": left_panel_width,
                "list_area": list_area_height
            }
        })
    
    def _update_screen_adaptive_config(self):
        """屏幕分辨率变化时更新自适应配置"""
        try:
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.primaryScreen()
            if not screen:
                return
            # 使用完整屏幕尺寸而不是可用桌面区域，支持真正的全屏布局
            screen_size = screen.geometry()
            screen_width = screen_size.width()
            screen_height = screen_size.height()
            
            # 更新配置中的自适应尺寸
            self.config.update({
                'left_panel_width': max(212, int(screen_width * 0.12)),
                'md_reader_width': max(376, int(screen_width * 0.25)),
                'list_area_height': max(209, int(screen_height * 0.15)),
                'min_widths': {
                    'left_panel': max(120, int(screen_width * 0.08)),
                    'command_area': max(300, int(screen_width * 0.20)),
                    'md_reader': max(200, int(screen_width * 0.15))
                },
                'min_heights': {
                    'command_area': max(250, int(screen_height * 0.20)),
                    'list_area': max(120, int(screen_height * 0.10))
                }
            })
            
            print(f"🖥️ 屏幕自适应配置已更新：{screen_width}x{screen_height}")
            
            # 发送配置更新信号
            self.layout_changed.emit("screen_adaptive_updated", {
                "screen_size": {"width": screen_width, "height": screen_height},
                "config": self.config
            })
        except Exception as e:
            print(f"⚠️ 屏幕自适应配置更新失败: {e}")


    


# 修改履历记录
# [修改] 2025-01-08: 增强布局持久化功能，添加保存按钮和自动保存触发 (文件:layout_manager.py:211-258,1180-1210)
# [新增] 2025-01-08: 添加命令选项卡状态保存和恢复功能 (文件:layout_manager.py:1065,1113-1116)
# [修改] 2025-01-08: 在所有选项卡切换和MD阅读器操作时触发自动保存 (文件:layout_manager.py:897,914,388,862)
# [修改] 2025-01-08: 更新默认配置为用户当前布局，增强配置文件验证和恢复 (文件:layout_manager.py:54-72,1123-1163,1218-1234)
# [新增] 2025-01-08: 添加恢复默认布局按钮和apply_default_layout方法 (文件:layout_manager.py:239-258,1218-1234)
# [修复] 2025-01-08: 修复auto_save_layout缺失计时器启动代码，增强save_layout_state异常处理 (文件:layout_manager.py:1186-1187,1082-1110)
# [新增] 2025-06-11: 添加工作区域快捷调整按钮和对应功能方法 (文件:layout_manager.py:506-554,2674-2793)