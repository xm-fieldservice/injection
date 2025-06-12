import sys
import os
import time
import win32gui
import win32con
import win32api
import win32clipboard
import pyperclip
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QComboBox, QMenu, QShortcut, QMessageBox, 
                             QFileDialog, QDialog, QLineEdit, QCheckBox, QInputDialog, QFrame, QListWidget,
                             QListWidgetItem, QScrollArea, QTextBrowser, QSplitter, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QEvent, QBuffer, QByteArray, QUrl
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QImage, QClipboard
import datetime
import json
from template_dialog import TemplateDialog
from template_manager import TemplateManager
from ai_service import AIService
from api_key_dialog import APIKeyDialog
import win32process

# 导入新的布局管理器和脑图集成模块
from layout_manager import LayoutManager
from mindmap_integration import MindmapWidget

# 导入热重载管理器
from hot_reload_manager import HotReloadManager, start_hot_reload, stop_hot_reload

# 导入全屏管理器
from fullscreen_manager import integrate_fullscreen_manager

# 导入新的窗口管理器（模块化解耦方案）
from window_manager import integrate_window_manager

# 导入新的项目集成服务
try:
    from src.services.project_integration_service import ProjectIntegrationService
    PROJECT_INTEGRATION_AVAILABLE = True
except ImportError:
    PROJECT_INTEGRATION_AVAILABLE = False
    print("项目集成服务不可用，将使用基础功能")

# 定义应用程序路径常量
APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(APP_DIR, 'logs')

# 生成持久化实例ID用于独立配置
import time

def get_persistent_instance_id():
    """获取或创建持久化实例ID"""
    instance_file = os.path.join(APP_DIR, 'persistent_instance.json')
    
    try:
        if os.path.exists(instance_file):
            with open(instance_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('instance_id')
    except:
        pass
    
    # 如果没有找到持久化ID，创建新的
    new_instance_id = str(int(time.time() * 1000))[-8:]
    
    try:
        with open(instance_file, 'w', encoding='utf-8') as f:
            json.dump({
                'instance_id': new_instance_id,
                'created_time': datetime.datetime.now().isoformat()
            }, f)
    except:
        pass
    
    return new_instance_id

INSTANCE_ID = get_persistent_instance_id()
CONFIG_PATH = os.path.join(APP_DIR, f'config_instance_{INSTANCE_ID}.json')

# 确保日志目录存在
os.makedirs(LOGS_DIR, exist_ok=True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('提示词注入工具')
        
        # 实例唯一标识
        self.instance_id = INSTANCE_ID
        
        # 初始化变量
        self.target_window = None
        self.target_position = None
        self.target_window_title = None  # 添加目标窗口标题变量
        self.dragPosition = None  # 初始化拖拽位置变量
        
        # [修复] 2025-01-08: 添加dragPosition初始化以防止mouseMoveEvent闪退 (文件:main.py:82)
        
        # 项目绑定相关变量
        self.project_folder = None  # 绑定的项目文件夹路径
        self.project_name = None    # 项目名称
        self.log_file = None        # 项目对应的日志文件路径
        
        # MD阅读器面板相关变量
        self.md_reader_panel = None
        self.md_reader_visible = False
        
        # 新架构：布局管理器
        self.layout_manager = None
        
        # 热重载管理器
        self.hot_reload_manager = None
        
        # 文件保护功能相关变量
        self.backup_dir = None
        self.last_log_size = 0
        self.template_manager = TemplateManager()
        self.ai_service = AIService()
        
        # 默认模板设置
        self.default_scene = None
        self.default_version = None
        
        # 故障诊断数据收集
        self.debug_log = {
            'startup_time': datetime.datetime.now().isoformat(),
            'events': [],
            'errors': [],
            'operations': [],
            'injection_attempts': [],
            'system_info': self.collect_system_info(),
            # 针对注入失败问题的特定数据收集
            'injection_failure_diagnosis': {
                'failed_attempts': [],
                'successful_attempts': [],
                'fallback_to_note_records': [],
                'target_window_checks': [],
                'calibration_status_checks': []
            }
        }
        
        # 加载配置（需要在UI初始化前加载）
        self.load_config()
        
        # 清理过期项目锁
        self.cleanup_expired_project_locks()
        
        # 如果没有项目绑定，尝试自动检测当前项目
        if not self.project_folder or not self.project_name:
            self.auto_detect_current_project()
        
        self.initUI()
        self.setupShortcut()
        self.setupCommandArea()
        
        # 初始化热重载功能
        self.init_hot_reload()
        
        # 项目集成服务已禁用 - 清理项目显示标签区域
        self.project_integration = None
    

        # if PROJECT_INTEGRATION_AVAILABLE:
        #     try:
        #         self.project_integration = ProjectIntegrationService(self)
        #         print("项目集成服务已启用")
        #     except Exception as e:
        #         print(f"初始化项目集成服务失败: {e}")
        #         self.project_integration = None
        
    def load_config(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.target_window = config.get('target_window')
                self.target_position = config.get('target_position')
                self.target_window_title = config.get('target_window_title')  # 加载窗口标题
                
                # 加载项目绑定信息
                self.project_folder = config.get('project_folder')
                self.project_name = config.get('project_name')
                
                # 加载默认模板设置
                self.default_scene = config.get('default_scene')
                self.default_version = config.get('default_version')
                
                # 根据项目文件夹设置日志文件路径
                if self.project_folder and self.project_name:
                    self.log_file = os.path.join(self.project_folder, f"{self.project_name}-log.md")
                    self.backup_dir = os.path.join(self.project_folder, "backups")
                    # 初始化文件保护
                    self.init_log_protection()
                    # 启动日志文件监控
                    self.start_log_file_monitoring()
                else:
                    self.log_file = None
                    self.backup_dir = None
                    
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
            self.target_window = None
            self.target_position = None
            self.target_window_title = None  # 重置窗口标题
            self.project_folder = None
            self.project_name = None
            self.log_file = None
            self.backup_dir = None
        
    def save_config(self):
        config = {
            'target_window': self.target_window,
            'target_position': self.target_position,
            'target_window_title': self.target_window_title,  # 保存窗口标题
            'project_folder': self.project_folder,
            'project_name': self.project_name,
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
        self.setWindowTitle(f'提示词注入工具 - 实例 {INSTANCE_ID}')
        # 优化窗口设置：保留置顶但允许调整大小，启用最大化按钮
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.Window | 
            Qt.WindowMaximizeButtonHint | 
            Qt.WindowMinimizeButtonHint | 
            Qt.WindowCloseButtonHint
        )
        
        # 设置窗口可调整大小的范围 - 屏幕自适应
        self.setMinimumSize(600, 400)    # 最小尺寸：600x400
        
        # 设置窗口背景和样式 - 优化边框显示
        self.setStyleSheet("""
            QMainWindow { 
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
            }
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
            /* 分割器样式优化 */
            QSplitter::handle {
                background-color: #e0e0e0;
                margin: 1px;
            }
            QSplitter::handle:horizontal {
                width: 6px;
                border-left: 1px solid #ccc;
                border-right: 1px solid #ccc;
            }
            QSplitter::handle:vertical {
                height: 6px;
                border-top: 1px solid #ccc;
                border-bottom: 1px solid #ccc;
            }
            QSplitter::handle:hover {
                background-color: #4CAF50;
            }
        """)
        
        # 设置初始窗口大小和位置（自适应屏幕）
        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()  # 可用桌面区域（用于窗口定位）
        full_screen_size = screen.geometry()      # 完整屏幕尺寸（用于最大化）
        
        # 设置窗口最大尺寸为完整屏幕尺寸，允许真正的全屏最大化
        self.setMaximumSize(full_screen_size.width(), full_screen_size.height())
        
        # 窗口大小为屏幕的80%，更好展示四区域布局
        initial_width = int(screen_size.width() * 0.8)
        initial_height = int(screen_size.height() * 0.8)
        
        # 窗口居中显示
        x = (screen_size.width() - initial_width) // 2
        y = (screen_size.height() - initial_height) // 2
        
        self.setGeometry(x, y, initial_width, initial_height)
        
        # 使窗口可以调整大小
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 添加自定义标题栏功能
        self.setup_custom_title_bar()
        
    def setupCommandArea(self):
        # 新架构：使用LayoutManager管理布局
        self.layout_manager = LayoutManager(self)
        self.setCentralWidget(self.layout_manager)
        
        # 向后兼容：保留原有接口引用
        self.main_splitter = self.layout_manager.main_splitter
        self.main_layout = self.main_splitter  # 兼容现有代码
        
        # 连接布局管理器信号
        self.layout_manager.layout_changed.connect(self.handle_layout_events)
        self.layout_manager.region_resized.connect(self.handle_resize_events)
        
        # 保存原始的resizeEvent以支持自动调节
        self._original_resize_event = self.resizeEvent
        self.resizeEvent = self.custom_resize_event
        
        # 获取各区域的容器，用于填充原有组件
        left_panel_container = self.layout_manager.get_region_widget('left_panel')
        command_area_container = self.layout_manager.get_region_widget('command_area')
        
        # 迁移原有组件到新布局
        self.migrate_left_panel_components(left_panel_container)
        self.migrate_command_area_components(command_area_container)
        
        # 集成新的窗口管理器（模块化解耦方案 - 统一管理窗口状态）
        self.window_manager = integrate_window_manager(self)
        
        # 集成全屏管理器（第二条轨道全屏机制）
        self.fullscreen_manager = integrate_fullscreen_manager(self)
    def migrate_left_panel_components(self, left_panel_container):
        """迁移左侧面板组件到新布局"""
        # 获取左侧面板的布局
        left_layout = left_panel_container.layout()
        
        # 移除占位符（最后一个widget）
        if left_layout.count() > 1:
            item = left_layout.takeAt(left_layout.count() - 1)
            if item.widget():
                item.widget().deleteLater()
        
        # ===== 原有左侧面板内容迁移 =====
        
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
        
        # 将场景布局添加到左侧面板
        left_layout.addLayout(scene_layout)
        
        # 添加标签按钮区域
        tags_container = QWidget()
        tags_layout = QVBoxLayout(tags_container)
        tags_layout.setContentsMargins(5, 10, 5, 5)
        
        # 标签区域标题
        tags_title = QLabel("快捷标签")
        tags_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333;
                padding: 2px;
            }
        """)
        tags_layout.addWidget(tags_title)
        
        # 创建标签按钮
        self.tag_buttons = []
        tag_names = ["任务", "里程碑", "问题", "AI犯坏"]
        tag_colors = ["#4CAF50", "#2196F3", "#FF9800", "#F44336"]  # 绿色、蓝色、橙色、红色
        
        # 创建两行标签布局
        tag_row1_layout = QHBoxLayout()
        tag_row2_layout = QHBoxLayout()
        
        for i, (tag_name, color) in enumerate(zip(tag_names, tag_colors)):
            tag_button = QPushButton(tag_name)
            tag_button.setFixedSize(85, 30)  # 调整按钮大小适应新布局
            tag_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                    margin: 1px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {self.darken_color(color, 0.8)};
                }}
            """)
            
            # 连接点击事件
            tag_button.clicked.connect(lambda checked, name=tag_name: self.on_tag_clicked(name))
            
            # 第一行放前两个按钮，第二行放后两个
            if i < 2:
                tag_row1_layout.addWidget(tag_button)
            else:
                tag_row2_layout.addWidget(tag_button)
            
            self.tag_buttons.append(tag_button)
        
        # 添加弹性空间到每行
        tag_row1_layout.addStretch()
        tag_row2_layout.addStretch()
        
        tags_layout.addLayout(tag_row1_layout)
        tags_layout.addLayout(tag_row2_layout)
        
        # 将标签容器添加到左侧面板
        left_layout.addWidget(tags_container)
        
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
    
    def migrate_command_area_components(self, command_area_container):
        """迁移命令区域组件到新布局"""
        # 获取命令注入选项卡的布局（不是整个命令区域的布局）
        if hasattr(self.layout_manager, 'command_injection_tab'):
            command_layout = self.layout_manager.command_injection_tab.layout()
            
            # 移除占位符（最后一个widget）
            if command_layout.count() > 0:
                item = command_layout.takeAt(command_layout.count() - 1)
                if item.widget():
                    item.widget().deleteLater()
        else:
            # 回退到原来的方式（兼容性）
            command_layout = command_area_container.layout()
            if command_layout.count() > 1:
                item = command_layout.takeAt(command_layout.count() - 1)
                if item.widget():
                    item.widget().deleteLater()
        
        # ===== 原有右侧面板内容迁移 =====
        
        # 注意：MD阅读器按钮现在由LayoutManager管理，这里不需要重复创建
        # 原有的md_reader_button功能已经集成到layout_manager的md_toggle_btn中
        
        # 标题栏已由状态栏的窗口控制按钮管理，这里不再重复创建
        
        # 创建项目文件夹选择区域
        project_layout = QHBoxLayout()
        self.project_label = QLabel("未绑定项目")
        self.project_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 12px;
                padding: 5px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
        """)
        # 这里暂时不设置，让setupCommandArea完成后再更新
        pass
        
        project_layout.addWidget(self.project_label)
        
        self.project_button = QPushButton("选择项目文件夹")
        self.project_button.clicked.connect(self.select_project_folder)
        project_layout.addWidget(self.project_button)
        
        command_layout.addLayout(project_layout)
        
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
        command_layout.addLayout(info_layout)
        
        # 创建状态标签
        self.status_label = QLabel("未校准目标窗口")
        command_layout.addWidget(self.status_label)
        
        # 创建命令输入框
        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText("请输入命令...\n使用 Alt + Enter 注入命令")
        self.command_input.setMinimumHeight(300)
        # 允许接收富文本内容，支持图片显示
        self.command_input.setAcceptRichText(True)
        
        # 设置命令输入框的事件过滤器
        self.command_input.installEventFilter(self)
        command_layout.addWidget(self.command_input)
        
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
        
        command_layout.addLayout(button_layout)
        
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
        
        # 添加注入失败诊断日志导出按钮
        self.export_debug_log_button = QPushButton("导出注入失败诊断")
        self.export_debug_log_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E55A2D;
            }
        """)
        self.export_debug_log_button.clicked.connect(self.export_injection_failure_log)
        bottom_layout.addWidget(self.export_debug_log_button)
        
        command_layout.addLayout(bottom_layout)
        
        # 完成组件迁移后的初始化
        self.finalize_migration()
    
    def finalize_migration(self):
        """完成迁移后的初始化工作"""
        # 更新状态标签
        self.update_status_label()
        
        # 更新项目显示
        self.update_project_display()
        
        # 加载场景列表
        self.load_scenes()
    
    def handle_layout_events(self, event_type, data):
        """处理布局管理器事件"""
        if event_type == "md_reader_opened":
            # MD阅读器打开时的处理
            pass
        elif event_type == "md_reader_closed":
            # MD阅读器关闭时的处理
            pass
        elif event_type == "tab_changed":
            # 选项卡切换时的处理
            tab_name = data.get("tab_name", "")
            if tab_name == "mindmap":
                # 切换到脑图时的处理
                pass
        elif event_type == "list_selection_sync":
            # 列表选择同步时的处理
            selected_data = data.get("selected_data", {})
            # 这里可以添加与列表同步的逻辑
            pass
    
    def handle_resize_events(self, direction, pos, index):
        """处理区域大小调整事件"""
        # 可以在这里添加大小调整的响应逻辑
        pass
    
    def custom_resize_event(self, event):
        """自定义窗口调整大小事件处理"""
        # 调用原始的resize事件处理
        self._original_resize_event(event)
        
        # 通知布局管理器进行自动调节
        if hasattr(self, 'layout_manager'):
            self.layout_manager.auto_adjust_on_resize(event.size())
    
    def setup_custom_title_bar(self):
        """设置自定义标题栏功能"""
        # 启用窗口拖拽
        self.setWindowFlag(Qt.WindowType.Window, True)
        
        # 创建状态栏显示调整信息
        self.status_bar = self.statusBar()
        self.resize_status_label = QLabel("就绪")
        self.resize_status_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 11px;
                padding: 2px 5px;
            }
        """)
        self.status_bar.addWidget(self.resize_status_label)
        
        # 窗口控制按钮已移除 - 使用系统默认标题栏控制
        pass
        
    def toggle_maximize(self):
        """切换最大化/还原状态"""
        if self.isMaximized():
            print("🗖【全屏按钮】已被点击！正在还原窗口...")
            self.showNormal()
            self.resize_status_label.setText("就绪")
            print("✅ 窗口已还原到正常大小！")
        else:
            print("🗖【全屏按钮】已被点击！正在全屏显示...")
            self.showMaximized()
            self.resize_status_label.setText("全屏模式")
            print("✅ 窗口已全屏显示！")
    
    # 向后兼容：保留原有的MD阅读器接口
    def toggle_md_reader_panel(self):
        """向后兼容的MD阅读器切换方法"""
        if self.layout_manager:
            return self.layout_manager.toggle_md_reader()
        return False
        


    def setupShortcut(self):
        # 创建快捷键
        self.shortcut = QShortcut(QKeySequence("Shift+F2"), self)
        self.shortcut.activated.connect(self.showWindow)
        
        # 添加主题切换快捷键
        if hasattr(self, 'project_integration') and self.project_integration:
            theme_shortcut = QShortcut(QKeySequence('Ctrl+Shift+T'), self)
            theme_shortcut.activated.connect(self.switch_theme)
        
        # HTML强制刷新快捷键 (F5)
        html_refresh_shortcut = QShortcut(QKeySequence('F5'), self)
        html_refresh_shortcut.activated.connect(self.force_refresh_html_pages)
        
    def showWindow(self):
        self.show()
        self.activateWindow()
        self.command_input.setFocus()
        
    def update_status_label(self):
        if self.target_window and self.target_position:
            app_name = self.target_window_title or win32gui.GetWindowText(self.target_window)
            self.status_label.setText(f"已校准: {app_name} (实例 {self.instance_id})")
            self.window_info_label.setText(f"目标窗口：{app_name}")
            self.input_info_label.setText(f"输入框位置：X={self.target_position[0]}, Y={self.target_position[1]}")
        else:
            self.status_label.setText(f"未校准目标窗口 (实例 {self.instance_id})")
            self.window_info_label.setText("目标窗口：未选择")
            self.input_info_label.setText("输入框位置：未校准")
        
        # 同步更新左侧面板状态
        if hasattr(self, 'layout_manager') and self.layout_manager:
            self.layout_manager.update_left_panel_status()
    
    def update_project_display(self):
        """更新项目显示"""
        if hasattr(self, 'project_label'):
            if self.project_name and self.project_folder:
                self.project_label.setText(f"项目: {self.project_name} 📁")
            else:
                self.project_label.setText("未绑定项目")
        
        # 同步更新左侧面板状态
        if hasattr(self, 'layout_manager') and self.layout_manager:
            self.layout_manager.update_left_panel_status()
        
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
            
    def find_current_cursor_window(self):
        """动态查找当前的Cursor窗口句柄"""
        try:
            def enum_windows_callback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title and "Cursor" in window_title:
                        results.append((hwnd, window_title))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            # 优先选择最活跃的Cursor窗口（通常是最后一个）
            if windows:
                # 按窗口句柄排序，选择最新的
                windows.sort(key=lambda x: x[0], reverse=True)
                latest_hwnd, latest_title = windows[0]
                print(f"🔍 找到Cursor窗口: {latest_title} (句柄: {latest_hwnd})")
                return latest_hwnd
            
            return None
            
        except Exception as e:
            print(f"查找Cursor窗口失败: {e}")
            return None

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
        """统一的命令注入实现 - 删除冗余逻辑，专注核心功能"""
        
        # === 基础校验 ===
        if not self.target_window or not self.target_position:
            QMessageBox.warning(self, "错误", "请先校准目标窗口")
            return
            
        command = self.command_input.toPlainText().strip()
        
        # 智能空命令检查 - 允许纯模板注入
        has_template = False
        if self.default_scene and self.default_version:
            template = self.template_manager.get_template(self.default_scene, self.default_version)
            if template and (template.get('prefix', '').strip() or template.get('suffix', '').strip()):
                has_template = True
        
        # 如果没有命令且没有有效模板，则阻止注入
        if not command and not has_template:
            QMessageBox.warning(self, "错误", "请输入命令或设置包含内容的模板")
            return
            
        # 允许空命令但有模板的情况
        if not command and has_template:
            print("📝 空命令但检测到有效模板，允许纯模板注入")
            self.show_mini_notification("已检测到模板内容，执行纯模板注入")
            
        # 确保项目日志文件设置正确
        if not self.project_folder or not self.project_name or not self.log_file:
            self.auto_detect_current_project()
            
        # === 准备注入内容 ===
        project_name = self.get_cursor_project_name()
        original_command = command
        
        # 处理空命令的情况
        if command:
            command_with_project = f"【项目：{project_name}】\n{command}"
        else:
            # 空命令时只添加项目标识
            command_with_project = f"【项目：{project_name}】"
        
        # 应用模板或AI修饰
        if self.realtime_check.isChecked():
            if not self.ai_service.api_key:
                print("⚠️ 实时生成已启用但未设置API密钥，回退到默认模板模式")
                # 回退到默认模板而不是直接返回
                if self.default_scene and self.default_version:
                    template = self.template_manager.get_template(self.default_scene, self.default_version)
                    if template:
                        final_command = f"{template['prefix']}\n\n{command_with_project}\n\n{template['suffix']}"
                    else:
                        final_command = command_with_project
                else:
                    final_command = command_with_project
                # 提示用户API密钥缺失但不阻止注入
                self.show_mini_notification("API密钥未设置，已使用默认模板")
            else:
                decorators = self.ai_service.generate_decorators(command_with_project, self.default_scene)
                if decorators:
                    final_command = f"{decorators['prefix']}\n\n{command_with_project}\n\n{decorators['suffix']}"
                else:
                    final_command = command_with_project
        else:
            # 使用默认模板
            if self.default_scene and self.default_version:
                template = self.template_manager.get_template(self.default_scene, self.default_version)
                if template:
                    final_command = f"{template['prefix']}\n\n{command_with_project}\n\n{template['suffix']}"
                else:
                    final_command = command_with_project
            else:
                final_command = command_with_project
        
        try:
            # === 1. 窗口激活（带动态句柄检测和重试机制） ===
            success = False
            target_window = self.target_window  # 使用当前配置的句柄
            
            for attempt in range(3):  # 增加到3次尝试
                try:
                    # 第一次尝试失败后，尝试重新查找Cursor窗口
                    if attempt == 1:
                        print(f"⚠️ 第一次激活失败，尝试重新查找Cursor窗口...")
                        new_cursor_window = self.find_current_cursor_window()
                        if new_cursor_window and new_cursor_window != self.target_window:
                            print(f"🔄 发现新的Cursor窗口句柄: {new_cursor_window} (原句柄: {self.target_window})")
                            target_window = new_cursor_window
                            # 更新配置中的窗口句柄
                            self.target_window = new_cursor_window
                            self.save_config()
                    
                    # 第二次失败后强制恢复窗口状态
                    if attempt == 2:
                        win32gui.ShowWindow(target_window, win32con.SW_RESTORE)
                        time.sleep(0.3)
                    
                    win32gui.SetForegroundWindow(target_window)
                    time.sleep(0.2)
                    
                    # 验证激活成功
                    current_foreground = win32gui.GetForegroundWindow()
                    if current_foreground == target_window:
                        print(f"✅ 窗口激活成功 (尝试 #{attempt + 1}, 句柄: {target_window})")
                        success = True
                        break
                    else:
                        print(f"❌ 窗口激活失败 (尝试 #{attempt + 1}): 目标={target_window}, 当前前台={current_foreground}")
                        
                except Exception as e:
                    print(f"❌ 窗口激活异常 (尝试 #{attempt + 1}): {str(e)}")
                    if attempt == 2:  # 最后一次尝试失败
                        raise Exception(f"窗口激活失败: {str(e)}")
                    
            if not success:
                raise Exception(f"无法激活目标窗口 (最终句柄: {target_window})")
            
            # === 2. 鼠标定位和点击 ===
            point = win32gui.ClientToScreen(target_window, self.target_position)
            win32api.SetCursorPos(point)
            time.sleep(0.1)
            
            # 执行点击
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.1)
            
            # === 3. 剪贴板操作（带验证） ===
            pyperclip.copy(final_command)
            time.sleep(0.1)
            
            # 验证剪贴板内容
            clipboard_content = pyperclip.paste()
            if clipboard_content != final_command:
                raise Exception("剪贴板复制失败")
            
            # === 4. 粘贴操作 ===
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            
            # === 5. 发送回车 ===
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.2)
            
            # === 6. 记录日志 ===
            try:
                self.auto_recover_log_file()
                
                log_dir = os.path.dirname(self.log_file)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                    
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                app_name = self.target_window_title if self.target_window_title else "未知应用"
                
                # 修改日志：2025-12-21 by Assistant - 最终修复日志记录混乱问题
                # 变更：注入工具只记录简单操作事实，避免与AI工作总结混淆
                # 目的：区分技术操作记录和AI分析内容，解决"中间结果"问题
                output_content = f"✅ 命令注入完成 - {app_name} - {timestamp}"

                log_content = f"\n# {timestamp} ({app_name} - 项目：{project_name})\n\n## 📥 输入\n\n{original_command}\n\n## 📤 输出\n\n{output_content}\n"
                
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_content)
                
                # 【修复】增量备份机制 - 每次注入后自动创建备份
                try:
                    backup1 = self.create_log_backup("backup-1")
                    backup2 = self.create_log_backup("backup-2")
                    if backup1 and backup2:
                        print("✅ 自动双重增量备份创建完成")
                    elif backup1 or backup2:
                        print("⚠️ 部分增量备份创建成功")
                    else:
                        print("⚠️ 增量备份创建失败")
                except Exception as backup_error:
                    print(f"⚠️ 备份创建异常：{backup_error}")
                
                # 移除独立时间戳备份，减少冗余文件
                
            except Exception as e:
                QMessageBox.warning(self, "警告", f"记录日志失败：{str(e)}")
            
            # === 7. 完成操作 ===
            self.clear_command()
            
            # 根据注入类型显示不同的成功消息
            if original_command:
                self.show_mini_notification("命令已注入")
                print(f"✅ 命令注入成功: {original_command[:50]}{'...' if len(original_command) > 50 else ''}")
            else:
                self.show_mini_notification("纯模板已注入")
                print(f"✅ 纯模板注入成功: [{self.default_scene} - {self.default_version}]")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"注入命令失败: {str(e)}")
            print(f"注入失败详情: {str(e)}")  # 调试信息
    
    def clear_command(self):
        self.command_input.clear()
        
    def auto_detect_current_project(self):
        """自动检测当前项目"""
        try:
            # 清理过期项目锁
            self.cleanup_expired_project_locks()
            
            # 获取当前工作目录
            current_dir = os.getcwd()
            project_name = os.path.basename(current_dir)
            
            # 检查是否是有效的项目目录（可以根据需要添加更多检查条件）
            if project_name and len(project_name) > 0 and project_name != '.':
                
                # 检查项目实例冲突
                conflict_result = self.check_project_instance_conflict(project_name)
                if conflict_result['conflict']:
                    print(f"⚠️ 项目绑定冲突：{conflict_result['message']}")
                    print(f"当前实例 {self.instance_id} 无法绑定项目 '{project_name}'")
                    
                    # 记录冲突事件
                    if hasattr(self, 'log_injection_failure_check'):
                        self.log_injection_failure_check("PROJECT_BINDING_CONFLICT", "auto_detect", {
                            'project_name': project_name,
                            'conflict_instance': conflict_result['instance_id'],
                            'current_instance': self.instance_id,
                            'message': conflict_result['message']
                        })
                    
                    return False
                
                # 设置项目信息
                self.project_folder = current_dir
                self.project_name = project_name
                self.log_file = os.path.join(current_dir, f"{project_name}-log.md")
                self.backup_dir = os.path.join(current_dir, "backups")
                
                # 创建项目锁
                if not self.create_project_lock(project_name):
                    print(f"❌ 无法为项目 '{project_name}' 创建锁文件")
                    return False
                
                # 确保备份目录存在
                os.makedirs(self.backup_dir, exist_ok=True)
                
                # 初始化文件保护
                self.init_log_protection()
                # 启动日志文件监控
                self.start_log_file_monitoring()
                
                # 保存配置
                self.save_config()
                
                # 记录自动绑定事件
                if hasattr(self, 'log_injection_failure_check'):
                    self.log_injection_failure_check("PROJECT_BINDING", "auto_detect", {
                        'project_name': project_name,
                        'project_folder': current_dir,
                        'log_file': self.log_file,
                        'instance_id': self.instance_id
                    })
                
                print(f"自动检测并绑定项目: {project_name}")
                return True
                
        except Exception as e:
            print(f"自动检测项目失败: {e}")
            return False

    def select_project_folder(self):
        """选择项目文件夹"""
        # 清理过期项目锁
        self.cleanup_expired_project_locks()
        
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "选择项目文件夹",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if folder_path:
            # 获取项目名称（文件夹名）
            project_name = os.path.basename(folder_path)
            
            if not project_name:
                QMessageBox.warning(self, "错误", "无法获取项目名称")
                return
            
            # 检查项目实例冲突
            conflict_result = self.check_project_instance_conflict(project_name)
            if conflict_result['conflict']:
                QMessageBox.warning(
                    self, 
                    "项目绑定冲突", 
                    f"项目 '{project_name}' 已被实例 {conflict_result['instance_id']} 绑定！\n\n"
                    f"锁定时间：{conflict_result['lock_time']}\n\n"
                    f"请选择其他项目或等待该实例释放项目锁。"
                )
                
                # 记录冲突事件
                if hasattr(self, 'log_injection_failure_check'):
                    self.log_injection_failure_check("PROJECT_BINDING_CONFLICT", "user_action", {
                        'project_name': project_name,
                        'conflict_instance': conflict_result['instance_id'],
                        'current_instance': self.instance_id,
                        'message': conflict_result['message']
                    })
                
                return
            
            # 如果当前已绑定其他项目，先释放
            if self.project_name and self.project_name != project_name:
                self.release_project_lock(self.project_name)
                
            # 设置项目信息
            self.project_folder = folder_path
            self.project_name = project_name
            self.log_file = os.path.join(folder_path, f"{project_name}-log.md")
            self.backup_dir = os.path.join(folder_path, "backups")
            
            # 创建项目锁
            if not self.create_project_lock(project_name):
                QMessageBox.critical(self, "错误", f"无法为项目 '{project_name}' 创建锁文件")
                return
            
            # 确保项目文件夹和备份目录存在
            os.makedirs(folder_path, exist_ok=True)
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # 初始化文件保护
            self.init_log_protection()
            # 启动日志文件监控
            self.start_log_file_monitoring()
            
            # 更新UI显示
            self.update_project_display()
            
            # 保存配置
            self.save_config()
            
            # 显示成功消息
            self.show_mini_notification(f"已绑定项目：{project_name}")
            
            # 记录项目绑定事件
            if hasattr(self, 'log_injection_failure_check'):
                self.log_injection_failure_check("PROJECT_BINDING", "user_action", {
                    'project_name': project_name,
                    'project_folder': folder_path,
                    'log_file': self.log_file,
                    'instance_id': self.instance_id
                })
        
    def switch_theme(self):
        """切换主题"""
        if hasattr(self, 'project_integration') and self.project_integration:
            success = self.project_integration.switch_theme()
            if success:
                current_theme = self.project_integration.get_current_theme()
                self.show_mini_notification(f"已切换到{current_theme}主题")
                
    def refresh_project_info(self):
        """刷新项目信息"""
        if hasattr(self, 'project_integration') and self.project_integration:
            self.project_integration.refresh_project_detection()
            current_project = self.project_integration.get_current_project()
            if current_project:
                self.show_mini_notification(f"项目已更新: {current_project}")
            else:
                self.show_mini_notification("未检测到项目")

    def init_hot_reload(self):
        """初始化热重载功能"""
        try:
            self.hot_reload_manager = HotReloadManager()
            
            # 连接热重载信号
            self.hot_reload_manager.module_reloaded.connect(self.on_module_reloaded)
            self.hot_reload_manager.reload_status_changed.connect(self.on_reload_status_changed)
            
            # 启动热重载监控
            self.hot_reload_manager.start_watching()
            
            print("🔥 热重载功能已启动")
            
            # 在布局管理器中添加热重载控制面板
            if self.layout_manager:
                self.add_hot_reload_controls()
                
        except ImportError as e:
            print(f"⚠️ 热重载功能不可用，缺少依赖: {e}")
            self.hot_reload_manager = None
        except Exception as e:
            print(f"❌ 初始化热重载功能失败: {e}")
            self.hot_reload_manager = None
    
    def add_hot_reload_controls(self):
        """在布局管理器中添加热重载控制面板"""
        try:
            if not self.hot_reload_manager:
                return
            
            # 在命令区添加热重载控制按钮
            hot_reload_btn = QPushButton("🔥")
            hot_reload_btn.setFixedSize(32, 32)
            hot_reload_btn.setToolTip("切换热重载功能 (当前文件变化时自动重载模块)")
            hot_reload_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF5722;
                    color: white;
                    border: none;
                    border-radius: 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E64A19;
                    border: 2px solid #FF7043;
                }
                QPushButton:pressed {
                    background-color: #D84315;
                    border: 2px solid #BF360C;
                }
            """)
            hot_reload_btn.clicked.connect(self.toggle_hot_reload)
            
            # 添加到布局管理器的标题栏
            if hasattr(self.layout_manager, 'save_layout_btn'):
                # 获取标题栏布局
                parent = self.layout_manager.save_layout_btn.parent()
                if parent:
                    layout = parent.layout()
                    if layout:
                        # 在保存按钮前插入热重载按钮
                        button_index = layout.indexOf(self.layout_manager.save_layout_btn)
                        layout.insertWidget(button_index, hot_reload_btn)
                        
        except Exception as e:
            print(f"❌ 添加热重载控制面板失败: {e}")
    
    def toggle_hot_reload(self):
        """切换热重载功能"""
        if not self.hot_reload_manager:
            self.show_mini_notification("❌ 热重载功能不可用")
            return
        
        if self.hot_reload_manager.is_watching:
            self.hot_reload_manager.stop_watching()
            self.show_mini_notification("⏹️ 热重载已停止")
        else:
            self.hot_reload_manager.start_watching()
            self.show_mini_notification("🔥 热重载已启动")
    
    def force_reload_all_modules(self):
        """强制重载所有模块"""
        if self.hot_reload_manager:
            self.hot_reload_manager.force_reload_all()
            self.show_mini_notification("🔄 强制重载所有模块")
    
    def on_module_reloaded(self, module_name, success, message):
        """模块重载回调"""
        if success:
            self.show_mini_notification(f"✅ {module_name} 重载成功")
            
            # 特殊处理：如果布局管理器被重载，需要重新初始化
            if module_name == 'layout_manager' and self.layout_manager:
                self.reinit_layout_manager()
            
            # 🔄 检测HTML文件变化并强制刷新页面
            if self.should_refresh_html_on_reload(module_name):
                QTimer.singleShot(500, self.force_refresh_html_pages)  # 延迟500ms执行以确保模块加载完成
                
        else:
            self.show_mini_notification(f"❌ {module_name} 重载失败")
            print(f"模块重载失败: {message}")
    
    def on_reload_status_changed(self, status):
        """重载状态变化回调"""
        print(f"🔥 热重载状态: {status}")
    
    def reinit_layout_manager(self):
        """重新初始化布局管理器"""
        try:
            print("🔄 重新初始化布局管理器...")
            
            # 保存当前状态
            if self.layout_manager:
                self.layout_manager.save_layout_state()
            
            # 重新创建布局管理器实例
            old_layout = self.layout_manager
            self.layout_manager = LayoutManager(parent_window=self)
            
            # 重新连接信号
            self.layout_manager.layout_changed.connect(self.handle_layout_events)
            self.layout_manager.region_resized.connect(self.handle_resize_events)
            
            # 更新中央组件
            self.setCentralWidget(self.layout_manager)
            
            # 🔧 重要修复：重新迁移组件，确保第三个选项卡被创建
            left_panel_container = self.layout_manager.get_region_widget('left_panel')
            command_area_container = self.layout_manager.get_region_widget('command_area')
            
            # 重新迁移组件到新的布局管理器
            self.migrate_left_panel_components(left_panel_container)
            self.migrate_command_area_components(command_area_container)
            
            # 重新添加热重载控制
            self.add_hot_reload_controls()
            
            # 🔄 强制刷新HTML页面以清除缓存
            self.force_refresh_html_pages()
            
            print("✅ 布局管理器重新初始化完成（包含第三个选项卡）")
            self.show_mini_notification("✅ 布局管理器已更新")
            
        except Exception as e:
            print(f"❌ 重新初始化布局管理器失败: {e}")
            self.show_mini_notification("❌ 布局管理器更新失败")

    def closeEvent(self, event):
        # 停止热重载监控
        if hasattr(self, 'hot_reload_manager') and self.hot_reload_manager:
            self.hot_reload_manager.stop_watching()
            print("🔥 热重载功能已停止")
        
        # 保存布局状态
        if hasattr(self, 'layout_manager'):
            self.layout_manager.save_layout_state()
        
        # 停止日志文件监控
        if hasattr(self, 'log_monitor_timer'):
            self.log_monitor_timer.stop()
        
        # 释放项目锁
        if self.project_name:
            self.release_project_lock(self.project_name)
        
        # 清理项目集成服务
        if hasattr(self, 'project_integration') and self.project_integration:
            self.project_integration.cleanup()
            
        # 真正关闭程序，不再隐藏到托盘
        event.accept()
        QApplication.quit()

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
    
    def mouseDoubleClickEvent(self, event):
        """双击事件处理 - 支持标题栏双击最大化"""
        # 如果双击位置在窗口顶部（标题栏区域）
        if event.y() < 30:  # 标题栏高度范围
            self.toggle_maximize()
        else:
            super().mouseDoubleClickEvent(event)

    def eventFilter(self, obj, event):
        """事件过滤器，处理 Alt+Enter 注入命令和 Ctrl+V 粘贴图片"""
        if obj is self.command_input and event.type() == QEvent.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            
            # 检测 Alt+Enter，执行命令注入
            if key == Qt.Key_Return and modifiers == Qt.AltModifier:
                # 记录用户操作意图：想要注入命令
                operation_id = datetime.datetime.now().isoformat()
                command_before = self.command_input.toPlainText().strip()
                
                self.log_injection_failure_check("USER_INTENT_INJECT", operation_id, {
                    'operation': 'Alt+Enter pressed',
                    'command_length_before': len(command_before),
                    'command_preview': command_before[:50] + '...' if len(command_before) > 50 else command_before
                })
                
                # 执行注入
                self.inject_command()
                
                # 立即检查注入结果
                QTimer.singleShot(500, lambda: self.check_injection_result(operation_id, command_before))
                return True
            
            # 检测 Shift+Enter，记笔记功能
            if key == Qt.Key_Return and modifiers == Qt.ShiftModifier:
                # 记录用户操作意图：选择记笔记
                operation_id = datetime.datetime.now().isoformat()
                command_before = self.command_input.toPlainText().strip()
                
                self.log_injection_failure_check("USER_INTENT_NOTE", operation_id, {
                    'operation': 'Shift+Enter pressed',
                    'command_length_before': len(command_before),
                    'is_after_failed_injection': hasattr(self, '_last_failed_injection_time') and 
                        (datetime.datetime.now() - self._last_failed_injection_time).seconds < 30
                })
                
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
            
    def check_injection_result(self, operation_id, command_before):
        """检查注入操作的实际结果"""
        command_after = self.command_input.toPlainText().strip()
        injection_successful = (len(command_after) == 0)  # 输入框被清空说明注入成功
        
        if injection_successful:
            self.log_injection_failure_check("INJECTION_RESULT_SUCCESS", operation_id, {
                'result': 'SUCCESS',
                'command_cleared': True,
                'command_before_length': len(command_before),
                'command_after_length': len(command_after)
            })
        else:
            # 注入失败，记录失败时间
            self._last_failed_injection_time = datetime.datetime.now()
            
            self.log_injection_failure_check("INJECTION_RESULT_FAILED", operation_id, {
                'result': 'FAILED',
                'command_cleared': False,
                'command_before_length': len(command_before),
                'command_after_length': len(command_after),
                'command_still_present': command_after[:50] + '...' if len(command_after) > 50 else command_after,
                'possible_cause': 'injection process did not complete successfully'
            })

    def take_note(self):
        """记录笔记到日志文件"""
        print("DEBUG: take_note 方法被调用")  # 调试信息
        
        # 确保项目日志文件设置正确
        if not self.project_folder or not self.project_name or not self.log_file:
            self.auto_detect_current_project()
            
        # 获取富文本内容
        note_html = self.command_input.toHtml()
        plain_text = self.command_input.toPlainText().strip()
        
        if not plain_text and "<img" not in note_html:
            QMessageBox.warning(self, "错误", "请输入笔记内容或插入图片")
            return
            
        try:
            # 检查并自动恢复日志文件（如果需要）
            self.auto_recover_log_file()
            
            # 监控日志写入尝试
            write_attempt_id = self.monitor_log_write_attempt("take_note", plain_text)
            
            # 确保日志文件目录存在
            log_dir = os.path.dirname(self.log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 获取时间戳和应用名称
            timestamp_text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            app_name = self.target_window_title if self.target_window_title else "未知应用"
            project_name = self.get_cursor_project_name()
            
            # 修改日志：2025-12-21 by Assistant - 为笔记创建专属格式标识
            # 笔记专属格式: "# 时间戳 (📝 笔记 - 项目：项目名称)"
            title_text = f"\n# {timestamp_text} (📝 笔记 - 项目：{project_name})\n\n"
            
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
                                
                            # 再写入图片引用（笔记不需要输出块）
                            f.write(f"{image_md}\n")
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
                
            # 验证写入是否成功并进行双重备份
            if write_attempt_id:
                if self.verify_log_write_success(write_attempt_id, expected_append=True):
                    # 创建双重备份（两个独立的备份文件）
                    backup1 = self.create_log_backup("backup-1")
                    backup2 = self.create_log_backup("backup-2")
                    if backup1 and backup2:
                        print("✅ 笔记日志双重备份创建完成")
                    else:
                        print("⚠️ 备份创建部分失败")
            
            # 清除输入框
            self.clear_command()
            
            # 显示成功消息
            self.status_label.setText("笔记已保存")
            # 显示小提示，1秒后自动消失
            self.show_mini_notification("笔记已保存")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存笔记失败：{str(e)}")
            # 记录日志写入失败
            self.log_injection_failure_check("LOG_WRITE_FAILED", "take_note", {
                'error': str(e),
                'content_preview': plain_text[:50] if plain_text else ""
            })
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
                
                # 确保项目日志文件设置正确
                if not self.project_folder or not self.project_name or not self.log_file:
                    self.auto_detect_current_project()
                    
                try:
                    # 确保日志文件目录存在
                    log_dir = os.path.dirname(self.log_file)
                    if not os.path.exists(log_dir):
                        os.makedirs(log_dir, exist_ok=True)
                        
                    # 执行完整的日志保护流程
                    self.auto_recover_log_file()
                    write_attempt_id = self.monitor_log_write_attempt("capture_cascade_text", text[:100] + "..." if len(text) > 100 else text)
                    
                    with open(self.log_file, 'a', encoding='utf-8') as f:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        project_name = self.get_cursor_project_name()
                        # 统一使用交互块格式
                        f.write(f"\n# {timestamp} (从Cascade获取 - 项目：{project_name})\n\n## 📥 输入\n\n从Cascade窗口捕获文本\n\n## 📤 输出\n\n{text}\n")
                    
                    # 验证写入成功并进行双重备份
                    if self.verify_log_write_success(write_attempt_id):
                        # 创建双重备份（两个独立的备份文件）
                        backup1 = self.create_log_backup("backup-1")
                        backup2 = self.create_log_backup("backup-2")
                        if backup1 and backup2:
                            print("✅ Cascade日志双重备份创建完成")
                        else:
                            print("⚠️ 备份创建部分失败")
                        
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

    def collect_system_info(self):
        """收集系统信息"""
        import platform
        try:
            import psutil
            return {
                'os': f"{platform.system()} {platform.version()}",
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').free if platform.system() != 'Windows' else psutil.disk_usage('C:').free,
                'timestamp': datetime.datetime.now().isoformat()
            }
        except ImportError:
            return {
                'os': f"{platform.system()} {platform.version()}",
                'python_version': platform.python_version(),
                'timestamp': datetime.datetime.now().isoformat(),
                'error': 'psutil not available'
            }

    def log_injection_failure_check(self, check_type, attempt_id, details):
        """记录注入失败诊断的检查点"""
        record = {
            'timestamp': datetime.datetime.now().isoformat(),
            'attempt_id': attempt_id,
            'check_type': check_type,
            'details': details
        }
        
        # 根据检查类型分类记录
        if check_type in ['INJECTION_RESULT_SUCCESS']:
            self.debug_log['injection_failure_diagnosis']['successful_attempts'].append(record)
        elif check_type in ['INJECTION_RESULT_FAILED', 'INJECTION_FAILED', 'CALIBRATION_FAILED', 'LOG_FILE_MISSING', 'EMPTY_COMMAND', 'API_KEY_MISSING']:
            self.debug_log['injection_failure_diagnosis']['failed_attempts'].append(record)
        elif check_type in ['USER_INTENT_NOTE']:
            self.debug_log['injection_failure_diagnosis']['fallback_to_note_records'].append(record)
        elif check_type in ['TARGET_WINDOW_CHECK', 'WINDOW_ACTIVATION', 'WINDOW_ACTIVATION_ERROR']:
            self.debug_log['injection_failure_diagnosis']['target_window_checks'].append(record)
        elif check_type in ['USER_INTENT_INJECT', 'INJECTION_ATTEMPT_START']:
            self.debug_log['injection_failure_diagnosis']['calibration_status_checks'].append(record)
        
        print(f"INJECTION_DEBUG [{check_type}]: {details}")

    def log_debug_event(self, event_type, description, details=None):
        """记录调试事件"""
        event = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': event_type,
            'description': description,
            'details': details or {}
        }
        self.debug_log['events'].append(event)
        print(f"DEBUG [{event_type}]: {description}")

    def log_error(self, error_type, error_message, traceback_info=None):
        """记录错误信息"""
        error = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': error_type,
            'message': error_message,
            'traceback': traceback_info
        }
        self.debug_log['errors'].append(error)
        print(f"ERROR [{error_type}]: {error_message}")

    def log_injection_attempt(self, command, scene, version, success, error=None):
        """记录命令注入尝试"""
        attempt = {
            'timestamp': datetime.datetime.now().isoformat(),
            'command': command[:100] + '...' if len(command) > 100 else command,  # 限制长度
            'scene': scene,
            'version': version,
            'success': success,
            'error': error,
            'target_window': self.target_window_title,
            'target_position': self.target_position
        }
        self.debug_log['injection_attempts'].append(attempt)

    def collect_current_state(self):
        """收集当前状态信息"""
        current_item = self.scene_list.currentItem()
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'target_window_configured': bool(self.target_window),
            'target_window_title': self.target_window_title,
            'target_position': self.target_position,
            'log_file': self.log_file,
            'default_scene': self.default_scene,
            'default_version': self.default_version,
            'current_selected_scene': current_item.text() if current_item else None,
            'current_selected_version': self.version_combo.currentText(),
            'realtime_enabled': self.realtime_check.isChecked(),
            'command_input_length': len(self.command_input.toPlainText()),
            'scenes_count': self.scene_list.count(),
            'template_manager_status': len(self.template_manager.templates) if hasattr(self.template_manager, 'templates') else 0
        }

    def export_injection_failure_log(self):
        """导出命令注入失败专项诊断日志"""
        try:
            # 收集最新状态
            current_state = self.collect_current_state()
            
            # 专门针对注入失败的数据结构
            diagnosis_data = {
                'report_time': current_state['timestamp'],
                'system_info': self.debug_log['system_info'],
                'current_state': current_state,
                'injection_failure_diagnosis': self.debug_log['injection_failure_diagnosis']
            }
            
            # 生成文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"注入失败诊断_{timestamp}"
            
            # 选择保存位置
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出命令注入失败诊断报告",
                default_filename + ".json",
                "JSON Files (*.json);;Markdown Files (*.md);;All Files (*)"
            )
            
            if file_path:
                # 根据选择的扩展名决定格式
                if file_path.endswith('.md'):
                    # 导出Markdown格式
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("# 命令注入失败专项诊断报告\n\n")
                        f.write(f"**报告生成时间**: {current_state['timestamp']}\n\n")
                        f.write("---\n\n")
                        
                        # 问题概述
                        failed_count = len(diagnosis_data['injection_failure_diagnosis']['failed_attempts'])
                        success_count = len(diagnosis_data['injection_failure_diagnosis']['successful_attempts'])
                        fallback_count = len(diagnosis_data['injection_failure_diagnosis']['fallback_to_note_records'])
                        
                        f.write("## 📊 问题概述\n\n")
                        f.write(f"- **注入失败次数**: {failed_count}\n")
                        f.write(f"- **注入成功次数**: {success_count}\n")
                        f.write(f"- **回退到笔记次数**: {fallback_count}\n")
                        f.write(f"- **总尝试次数**: {failed_count + success_count}\n\n")
                        
                        if failed_count > 0 and success_count > 0:
                            success_rate = (success_count / (failed_count + success_count)) * 100
                            f.write(f"- **成功率**: {success_rate:.1f}%\n\n")
                        
                        # 系统环境
                        f.write("## 🖥️ 系统环境\n\n")
                        system_info = diagnosis_data['system_info']
                        for key, value in system_info.items():
                            f.write(f"- **{key}**: {value}\n")
                        f.write("\n")
                        
                        # 当前配置状态
                        f.write("## ⚙️ 当前配置状态\n\n")
                        key_states = [
                            ('target_window_configured', '目标窗口已配置'),
                            ('target_window_title', '目标窗口标题'),
                            ('log_file', '日志文件路径'),
                            ('default_scene', '默认场景'),
                            ('default_version', '默认版本'),
                            ('realtime_enabled', '实时生成启用')
                        ]
                        
                        for key, label in key_states:
                            value = current_state.get(key, 'N/A')
                            status = "✅" if value else "❌"
                            f.write(f"- {status} **{label}**: {value}\n")
                        f.write("\n")
                        
                        # 失败尝试详情
                        if failed_count > 0:
                            f.write("## ❌ 注入失败详情\n\n")
                            for i, attempt in enumerate(diagnosis_data['injection_failure_diagnosis']['failed_attempts'], 1):
                                f.write(f"### 失败记录 #{i}\n")
                                f.write(f"- **时间**: {attempt['timestamp']}\n")
                                f.write(f"- **尝试ID**: {attempt['attempt_id']}\n")
                                f.write(f"- **失败类型**: {attempt['check_type']}\n")
                                f.write(f"- **详细信息**:\n")
                                for key, value in attempt['details'].items():
                                    f.write(f"  - {key}: {value}\n")
                                f.write("\n")
                        
                        # 诊断建议
                        f.write("## 💡 诊断建议\n\n")
                        if failed_count > 0:
                            # 分析失败原因并给出建议
                            failure_types = {}
                            for attempt in diagnosis_data['injection_failure_diagnosis']['failed_attempts']:
                                failure_type = attempt['check_type']
                                failure_types[failure_type] = failure_types.get(failure_type, 0) + 1
                            
                            for failure_type, count in failure_types.items():
                                if failure_type == 'CALIBRATION_FAILED':
                                    f.write(f"- **校准问题** (出现{count}次): 请重新校准目标窗口位置\n")
                                elif failure_type == 'WINDOW_ACTIVATION_ERROR':
                                    f.write(f"- **窗口激活失败** (出现{count}次): 目标窗口可能已关闭或不可访问\n")
                                elif failure_type == 'LOG_FILE_MISSING':
                                    f.write(f"- **日志文件问题** (出现{count}次): 请检查日志文件路径设置\n")
                                elif failure_type == 'API_KEY_MISSING':
                                    f.write(f"- **API密钥问题** (出现{count}次): 请设置AI服务API密钥\n")
                                else:
                                    f.write(f"- **{failure_type}** (出现{count}次): 请查看详细错误信息\n")
                        else:
                            f.write("- 暂无注入失败记录，系统运行正常\n")
                        
                        f.write(f"\n---\n\n**报告结束** - 生成于 {current_state['timestamp']}")
                
                else:
                    # 默认导出JSON格式
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(diagnosis_data, f, ensure_ascii=False, indent=2)
                
                # 显示成功消息
                QMessageBox.information(
                    self, 
                    "导出成功", 
                    f"命令注入失败诊断报告已导出到:\n{file_path}"
                )
                
                # 记录导出事件
                self.log_debug_event("EXPORT", "注入失败诊断日志导出成功", {"file_path": file_path})
                
        except Exception as e:
            error_msg = f"导出诊断报告失败: {str(e)}"
            QMessageBox.critical(self, "导出失败", error_msg)
            self.log_error("EXPORT_ERROR", error_msg)

    # === 日志文件保护功能 ===
    def init_log_protection(self):
        """初始化日志文件保护功能 - 使用增量备份机制"""
        try:
            # 确保备份目录存在
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # 确保日志文件目录存在
            log_dir = os.path.dirname(self.log_file)
            os.makedirs(log_dir, exist_ok=True)
            
            # 初始化文件状态
            if os.path.exists(self.log_file):
                self.last_log_size = os.path.getsize(self.log_file)
                # 创建启动时的增量备份
                self.create_log_backup("startup")
                print(f"🔐 增量备份保护已启用，文件大小：{self.last_log_size} 字节")
                print("📝 增量备份机制：只备份新增内容，防止AI篡改历史日志")
            else:
                print("📝 日志文件不存在，将在首次使用时创建增量备份")
                
            # 记录保护启用事件
            self.log_injection_failure_check("LOG_PROTECTION_INIT", "startup", {
                'log_file': self.log_file,
                'backup_dir': self.backup_dir,
                'initial_size': self.last_log_size,
                'backup_type': 'incremental'
            })
            
        except Exception as e:
            print(f"❌ 初始化增量备份保护失败：{e}")
            self.log_error("LOG_PROTECTION_INIT_ERROR", str(e))
    
    def start_log_file_monitoring(self):
        """启动日志文件监控，自动检测文件变化并创建双备份"""
        if not self.log_file:
            return
            
        # 启动定时器，每2秒检查一次文件变化
        self.log_monitor_timer = QTimer()
        self.log_monitor_timer.timeout.connect(self.check_log_file_changes)
        self.log_monitor_timer.start(2000)  # 2秒间隔
        print("🔍 日志文件监控已启动")
    
    def check_log_file_changes(self):
        """检查日志文件是否有变化，如有变化则创建双备份"""
        try:
            if not os.path.exists(self.log_file):
                return
                
            current_size = os.path.getsize(self.log_file)
            
            # 如果文件大小发生变化，说明有新内容写入
            if current_size > self.last_log_size:
                print(f"📝 检测到日志文件变化：{self.last_log_size} → {current_size} 字节")
                
                # 更新记录的文件大小
                self.last_log_size = current_size
                
                # 创建双重备份
                backup1 = self.create_log_backup("backup-1")
                backup2 = self.create_log_backup("backup-2")
                
                if backup1 and backup2:
                    print("✅ 自动双重备份创建完成")
                else:
                    print("⚠️ 自动备份创建部分失败")
                    
        except Exception as e:
            # 静默处理监控错误，避免干扰正常功能
            pass
    
    def create_log_backup(self, backup_type="auto"):
        """创建增量日志文件备份"""
        try:
            if not os.path.exists(self.log_file):
                return None
                
            # 使用项目名称作为备份文件前缀
            project_prefix = self.project_name if self.project_name else "unknown"
            
            # 生成备份文件名
            if backup_type.startswith("backup-"):
                backup_filename = f"{project_prefix}-log-incremental-{backup_type.split('-')[1]}.md"
            elif backup_type == "startup":
                backup_filename = f"{project_prefix}-log-incremental-startup.md"
            else:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{project_prefix}-log-incremental-{backup_type}-{timestamp}.md"
                
            # 三级备份策略：当前目录、项目backups、AI项目目录
            if backup_type == "backup-2":
                # backup-2 移动到 d:\ai-projects 目录
                ai_projects_dir = r"d:\ai-projects"
                os.makedirs(ai_projects_dir, exist_ok=True)
                backup_path = os.path.join(ai_projects_dir, backup_filename)
            else:
                backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # 增量备份逻辑
            increment_content = self.create_incremental_backup_content(backup_type)
            
            if increment_content:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(increment_content)
                location = "AI项目目录" if backup_type == "backup-2" else "项目目录"
                print(f"✅ 增量日志备份创建 ({location})：{backup_filename} ({len(increment_content)} 字符)")
                
                # 记录备份创建事件
                self.log_injection_failure_check("LOG_INCREMENTAL_BACKUP_CREATED", backup_type, {
                    'backup_file': backup_filename,
                    'increment_size': len(increment_content),
                    'backup_type': 'incremental',
                    'backup_location': location
                })
                
                return backup_path
            else:
                print(f"⚠️ 没有新内容需要备份：{backup_type}")
                return None
            
        except Exception as e:
            print(f"❌ 创建增量日志备份失败：{e}")
            self.log_error("LOG_BACKUP_ERROR", str(e))
            return None

    def create_incremental_backup_content(self, backup_type):
        """创建增量备份内容"""
        try:
            # 读取当前日志文件
            with open(self.log_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # 获取上次备份位置标记
            last_backup_position = self.get_last_backup_position(backup_type)
            
            # 如果是首次备份，备份全部内容
            if last_backup_position == 0:
                increment_content = self.create_backup_header(backup_type, "FULL_BACKUP") + current_content
                self.update_backup_position(backup_type, len(current_content))
                return increment_content
            
            # 提取增量内容
            if len(current_content) > last_backup_position:
                new_content = current_content[last_backup_position:]
                increment_content = self.create_backup_header(backup_type, "INCREMENTAL_BACKUP", last_backup_position) + new_content
                self.update_backup_position(backup_type, len(current_content))
                return increment_content
            
            # 检测到文件被截断或清空
            if len(current_content) < last_backup_position:
                increment_content = self.create_backup_header(backup_type, "TRUNCATION_DETECTED") + current_content
                self.update_backup_position(backup_type, len(current_content))
                return increment_content
            
            return None  # 没有新内容
            
        except Exception as e:
            print(f"❌ 创建增量备份内容失败：{e}")
            return None

    def create_backup_header(self, backup_type, backup_mode, start_position=0):
        """创建备份文件头部信息"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"""# 增量日志备份
## 备份信息
- 备份时间: {timestamp}
- 备份类型: {backup_type}
- 备份模式: {backup_mode}
- 起始位置: {start_position}
- 项目名称: {self.project_name if self.project_name else "unknown"}

---

"""
        return header

    def get_last_backup_position(self, backup_type):
        """获取上次备份的位置"""
        try:
            backup_meta_file = os.path.join(self.backup_dir, f"backup_meta_{backup_type}.txt")
            if os.path.exists(backup_meta_file):
                with open(backup_meta_file, 'r', encoding='utf-8') as f:
                    return int(f.read().strip())
            return 0
        except:
            return 0

    def update_backup_position(self, backup_type, position):
        """更新备份位置记录"""
        try:
            backup_meta_file = os.path.join(self.backup_dir, f"backup_meta_{backup_type}.txt")
            with open(backup_meta_file, 'w', encoding='utf-8') as f:
                f.write(str(position))
        except Exception as e:
            print(f"❌ 更新备份位置失败：{e}")

    def check_log_file_integrity(self):
        """检查日志文件完整性"""
        try:
            if not os.path.exists(self.log_file):
                self.log_injection_failure_check("LOG_FILE_MISSING", "integrity_check", {
                    'expected_path': self.log_file,
                    'last_known_size': self.last_log_size
                })
                return "missing"
            
            current_size = os.path.getsize(self.log_file)
            
            # 检查文件是否被清零
            if current_size == 0 and self.last_log_size > 0:
                self.log_injection_failure_check("LOG_FILE_CLEARED", "integrity_check", {
                    'previous_size': self.last_log_size,
                    'current_size': current_size,
                    'auto_recovery_attempted': True
                })
                return "cleared"
            
            # 检查文件大小是否异常减少（可能被部分清空）
            if current_size < self.last_log_size * 0.1 and self.last_log_size > 1000:
                self.log_injection_failure_check("LOG_FILE_TRUNCATED", "integrity_check", {
                    'previous_size': self.last_log_size,
                    'current_size': current_size,
                    'reduction_ratio': current_size / self.last_log_size
                })
                return "truncated"
            
            # 更新记录的文件大小
            self.last_log_size = current_size
            return "ok"
            
        except Exception as e:
            self.log_error("LOG_INTEGRITY_CHECK_ERROR", str(e))
            return "error"
    
    def auto_recover_log_file(self):
        """自动恢复被损坏的日志文件"""
        integrity_status = self.check_log_file_integrity()
        
        if integrity_status in ["cleared", "missing", "truncated"]:
            print(f"🚨 检测到日志文件问题：{integrity_status}")
            
            # 记录恢复尝试
            recovery_id = datetime.datetime.now().isoformat()
            self.log_injection_failure_check("LOG_RECOVERY_ATTEMPT", recovery_id, {
                'problem_type': integrity_status,
                'recovery_method': 'auto_restore_from_backup'
            })
            
            # 尝试从最新备份恢复
            latest_backup = self.get_latest_log_backup()
            if latest_backup:
                try:
                    # 如果当前文件存在且有内容，先备份
                    if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > 0:
                        self.create_log_backup("before-recovery")
                    
                    # 恢复文件
                    shutil.copy2(latest_backup, self.log_file)
                    self.last_log_size = os.path.getsize(self.log_file)
                    
                    print(f"✅ 日志文件已自动恢复，使用备份：{os.path.basename(latest_backup)}")
                    
                    # 记录恢复成功
                    self.log_injection_failure_check("LOG_RECOVERY_SUCCESS", recovery_id, {
                        'backup_used': os.path.basename(latest_backup),
                        'restored_size': self.last_log_size
                    })
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ 自动恢复失败：{e}")
                    self.log_injection_failure_check("LOG_RECOVERY_FAILED", recovery_id, {
                        'error': str(e)
                    })
                    return False
            else:
                print("❌ 没有可用的备份文件")
                self.log_injection_failure_check("LOG_RECOVERY_FAILED", recovery_id, {
                    'error': 'no_backup_available'
                })
                return False
        
        return True
    
    def get_latest_log_backup(self):
        """获取最新的日志备份文件（优先增量备份）"""
        try:
            backup_files = []
            project_prefix = self.project_name if self.project_name else "unknown"
            
            for file in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, file)
                mtime = os.path.getmtime(file_path)
                
                # 优先获取增量备份文件
                if file.startswith(f"{project_prefix}-log-incremental-") and file.endswith(".md"):
                    backup_files.append((file_path, mtime, "incremental"))
                # 兼容旧的整体备份文件
                elif (file.startswith(f"{project_prefix}-log-bak-") or file.startswith("my-log-backup-")) and file.endswith(".md"):
                    backup_files.append((file_path, mtime, "full"))
            
            if backup_files:
                # 按修改时间排序，优先返回增量备份
                backup_files.sort(key=lambda x: (x[2] == "incremental", x[1]), reverse=True)
                return backup_files[0][0]
            else:
                return None
                
        except Exception as e:
            print(f"❌ 获取备份文件失败：{e}")
            return None

    def restore_from_incremental_backup(self):
        """从增量备份恢复完整日志"""
        try:
            project_prefix = self.project_name if self.project_name else "unknown"
            incremental_files = []
            
            # 收集所有增量备份文件
            for file in os.listdir(self.backup_dir):
                if file.startswith(f"{project_prefix}-log-incremental-") and file.endswith(".md"):
                    file_path = os.path.join(self.backup_dir, file)
                    mtime = os.path.getmtime(file_path)
                    incremental_files.append((file_path, mtime))
            
            if not incremental_files:
                return None
            
            # 按时间排序
            incremental_files.sort(key=lambda x: x[1])
            
            # 合并所有增量备份内容
            restored_content = ""
            for backup_file, _ in incremental_files:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 跳过备份头部信息，只取实际日志内容
                    if "---\n\n" in content:
                        actual_content = content.split("---\n\n", 1)[1]
                        restored_content += actual_content
            
            # 创建恢复文件
            recovery_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            recovery_file = os.path.join(self.backup_dir, f"{project_prefix}-log-recovered-{recovery_timestamp}.md")
            
            with open(recovery_file, 'w', encoding='utf-8') as f:
                f.write(restored_content)
            
            print(f"✅ 从增量备份恢复完整日志：{recovery_file}")
            return recovery_file
            
        except Exception as e:
            print(f"❌ 从增量备份恢复失败：{e}")
            return None

    def manual_incremental_backup(self):
        """手动创建增量备份"""
        backup_path = self.create_log_backup("manual")
        if backup_path:
            print(f"🔐 手动增量备份完成：{os.path.basename(backup_path)}")
            return backup_path
        else:
            print("⚠️ 没有新内容需要备份")
            return None

    def list_incremental_backups(self):
        """列出所有增量备份文件"""
        try:
            project_prefix = self.project_name if self.project_name else "unknown"
            incremental_files = []
            
            for file in os.listdir(self.backup_dir):
                if file.startswith(f"{project_prefix}-log-incremental-") and file.endswith(".md"):
                    file_path = os.path.join(self.backup_dir, file)
                    mtime = os.path.getmtime(file_path)
                    file_size = os.path.getsize(file_path)
                    incremental_files.append((file, mtime, file_size))
            
            incremental_files.sort(key=lambda x: x[1], reverse=True)
            
            print("📋 增量备份文件列表：")
            for filename, mtime, size in incremental_files:
                time_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                size_kb = size // 1024
                print(f"  - {filename} ({size_kb}KB, {time_str})")
            
            return incremental_files
            
        except Exception as e:
            print(f"❌ 列出备份文件失败：{e}")
            return []
    
    def monitor_log_write_attempt(self, operation_type, content_preview=""):
        """监控日志写入尝试的检测点"""
        try:
            # 在写入前检查文件完整性
            pre_write_status = self.check_log_file_integrity()
            
            # 记录写入前的文件大小
            pre_write_size = os.path.getsize(self.log_file) if os.path.exists(self.log_file) else 0
            self._last_write_attempt_size = pre_write_size
            
            # 记录写入尝试
            write_attempt_id = datetime.datetime.now().isoformat()
            self.log_injection_failure_check("LOG_WRITE_ATTEMPT", write_attempt_id, {
                'operation_type': operation_type,
                'pre_write_status': pre_write_status,
                'content_preview': content_preview[:100] if content_preview else "",
                'log_file': self.log_file,
                'current_size': pre_write_size
            })
            
            return write_attempt_id
            
        except Exception as e:
            self.log_error("LOG_WRITE_MONITOR_ERROR", str(e))
            return None
    
    def verify_log_write_success(self, write_attempt_id, expected_append=True):
        """验证日志写入是否成功且未破坏文件"""
        try:
            # 检查写入后的文件完整性
            post_write_status = self.check_log_file_integrity()
            
            current_size = os.path.getsize(self.log_file) if os.path.exists(self.log_file) else 0
            
            # 获取写入前的文件大小（从写入尝试记录中获取）
            pre_write_size = 0
            try:
                # 从日志记录中查找写入前的大小
                if hasattr(self, '_last_write_attempt_size'):
                    pre_write_size = self._last_write_attempt_size
                else:
                    pre_write_size = self.last_log_size
            except:
                pre_write_size = self.last_log_size
            
            # 计算实际的文件大小变化
            actual_size_change = current_size - pre_write_size
            
            # 判断写入是否正常（允许文件大小增加或保持不变）
            write_success = True
            if expected_append and current_size < pre_write_size:
                write_success = False
                
            # 记录写入结果
            self.log_injection_failure_check("LOG_WRITE_RESULT", write_attempt_id, {
                'post_write_status': post_write_status,
                'current_size': current_size,
                'pre_write_size': pre_write_size,
                'write_success': write_success,
                'size_change': actual_size_change,
                'last_log_size_at_verify': self.last_log_size
            })
            
            # 如果写入正常，更新文件大小记录（备份由调用方负责）
            if write_success:
                self.last_log_size = current_size
            
            return write_success
            
        except Exception as e:
            self.log_error("LOG_WRITE_VERIFY_ERROR", str(e))
            return False

    def check_project_instance_conflict(self, project_name):
        """检查是否有其他实例已绑定相同项目"""
        try:
            # 项目锁文件路径
            lock_file = os.path.join(APP_DIR, f'.project_lock_{project_name}')
            
            if os.path.exists(lock_file):
                # 读取锁文件信息
                with open(lock_file, 'r', encoding='utf-8') as f:
                    lock_info = json.load(f)
                
                lock_instance_id = lock_info.get('instance_id')
                lock_pid = lock_info.get('pid')
                lock_time = lock_info.get('lock_time')
                
                # 检查锁定的实例是否还在运行
                if lock_instance_id != self.instance_id:
                    if self.is_instance_running(lock_pid, lock_instance_id):
                        # 其他实例仍在运行且已绑定此项目
                        return {
                            'conflict': True,
                            'instance_id': lock_instance_id,
                            'lock_time': lock_time,
                            'message': f"项目 '{project_name}' 已被实例 {lock_instance_id} 绑定"
                        }
                    else:
                        # 锁定的实例已退出，清理过期锁文件
                        os.remove(lock_file)
                        print(f"✅ 清理过期项目锁：{project_name}")
            
            return {'conflict': False}
            
        except Exception as e:
            print(f"检查项目实例冲突失败: {e}")
            return {'conflict': False}
    
    def is_instance_running(self, pid, instance_id):
        """检查指定的实例是否还在运行"""
        try:
            import psutil
            
            # 检查进程是否存在
            if pid and psutil.pid_exists(pid):
                process = psutil.Process(pid)
                
                # 检查是否是Python进程
                if 'python' in process.name().lower():
                    # 检查命令行参数是否包含main.py
                    cmdline = ' '.join(process.cmdline())
                    if 'main.py' in cmdline:
                        return True
            
            return False
            
        except ImportError:
            # 如果没有psutil，使用简单的文件检查
            config_file = os.path.join(APP_DIR, f'config_instance_{instance_id}.json')
            return os.path.exists(config_file)
        except Exception as e:
            print(f"检查实例运行状态失败: {e}")
            return False
    
    def create_project_lock(self, project_name):
        """为项目创建锁文件"""
        try:
            import os
            
            lock_file = os.path.join(APP_DIR, f'.project_lock_{project_name}')
            lock_info = {
                'instance_id': self.instance_id,
                'pid': os.getpid(),
                'project_name': project_name,
                'lock_time': datetime.datetime.now().isoformat(),
                'project_folder': self.project_folder
            }
            
            with open(lock_file, 'w', encoding='utf-8') as f:
                json.dump(lock_info, f, indent=2, ensure_ascii=False)
            
            print(f"🔒 为项目 '{project_name}' 创建锁文件 (实例: {self.instance_id})")
            return True
            
        except Exception as e:
            print(f"创建项目锁失败: {e}")
            return False
    
    def release_project_lock(self, project_name=None):
        """释放项目锁文件"""
        try:
            target_project = project_name or self.project_name
            if not target_project:
                return
                
            lock_file = os.path.join(APP_DIR, f'.project_lock_{target_project}')
            
            if os.path.exists(lock_file):
                # 验证锁文件确实属于当前实例
                with open(lock_file, 'r', encoding='utf-8') as f:
                    lock_info = json.load(f)
                
                if lock_info.get('instance_id') == self.instance_id:
                    os.remove(lock_file)
                    print(f"🔓 释放项目锁：{target_project} (实例: {self.instance_id})")
                
        except Exception as e:
            print(f"释放项目锁失败: {e}")
    
    def cleanup_expired_project_locks(self):
        """清理过期的项目锁文件"""
        try:
            lock_files = [f for f in os.listdir(APP_DIR) if f.startswith('.project_lock_')]
            
            for lock_file in lock_files:
                lock_path = os.path.join(APP_DIR, lock_file)
                try:
                    with open(lock_path, 'r', encoding='utf-8') as f:
                        lock_info = json.load(f)
                    
                    lock_pid = lock_info.get('pid')
                    lock_instance_id = lock_info.get('instance_id')
                    
                    # 检查锁定的实例是否还在运行
                    if not self.is_instance_running(lock_pid, lock_instance_id):
                        os.remove(lock_path)
                        project_name = lock_info.get('project_name', 'unknown')
                        print(f"🧹 清理过期项目锁：{project_name}")
                        
                except Exception as e:
                    print(f"清理锁文件 {lock_file} 失败: {e}")
                    
        except Exception as e:
            print(f"清理过期项目锁失败: {e}")
    
    def darken_color(self, hex_color, factor=0.9):
        """将十六进制颜色变暗"""
        try:
            # 移除 # 号
            hex_color = hex_color.lstrip('#')
            
            # 转换为RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)  
            b = int(hex_color[4:6], 16)
            
            # 应用变暗因子
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            
            # 转换回十六进制
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
    
    def on_tag_clicked(self, tag_name):
        """处理标签点击事件 - 插入最简洁的标签格式"""
        try:
            # 获取当前文本框的光标位置
            cursor = self.command_input.textCursor()
            
            # 生成最简洁的标签格式
            markdown_tag = f"[{tag_name}] "
            
            # 在光标位置插入标签
            cursor.insertText(markdown_tag)
            
            # 显示成功消息
            self.show_mini_notification(f"已插入标签: [{tag_name}]")
            
        except Exception as e:
            print(f"标签点击处理失败: {e}")
            QMessageBox.warning(self, "错误", f"插入标签失败：{str(e)}")
    
    def create_md_reader_panel(self):
        """创建MD阅读器面板"""
        # 创建MD阅读器面板
        self.md_reader_panel = QWidget()
        self.md_reader_panel.setMinimumWidth(250)  # 设置最小宽度，支持可调节
        self.md_reader_panel.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-left: 2px solid #e0e0e0;
            }
        """)
        
        # 创建面板布局
        panel_layout = QVBoxLayout(self.md_reader_panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标题栏
        title_layout = QHBoxLayout()
        
        # 标题
        title_label = QLabel("📖 日志阅读器")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 5px;
            }
        """)
        title_layout.addWidget(title_label)
        
        # 添加弹性空间
        title_layout.addStretch()
        
        # 刷新按钮
        refresh_button = QPushButton("🔄")
        refresh_button.setFixedSize(30, 30)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        refresh_button.clicked.connect(self.refresh_log_content)
        refresh_button.setToolTip("刷新日志内容")
        title_layout.addWidget(refresh_button)
        
        # 关闭按钮
        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 15px;
                color: #666;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: white;
            }
        """)
        close_button.clicked.connect(self.toggle_md_reader_panel)
        title_layout.addWidget(close_button)
        
        panel_layout.addLayout(title_layout)
        
        # 创建文件信息区域
        file_info_layout = QHBoxLayout()
        
        self.log_file_label = QLabel("当前日志：未绑定项目")
        self.log_file_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                padding: 3px;
                background-color: #f8f9fa;
                border-radius: 3px;
            }
        """)
        file_info_layout.addWidget(self.log_file_label)
        
        panel_layout.addLayout(file_info_layout)
        
        # 创建MD内容显示区域
        self.md_content_browser = QTextBrowser()
        self.md_content_browser.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #ffffff;
                font-family: 'Microsoft YaHei', sans-serif;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        
        # 设置支持Markdown渲染
        self.md_content_browser.setOpenExternalLinks(True)
        
        panel_layout.addWidget(self.md_content_browser)
        
        # 创建底部状态栏
        status_layout = QHBoxLayout()
        
        self.log_status_label = QLabel("准备就绪")
        self.log_status_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #888;
                padding: 2px;
            }
        """)
        status_layout.addWidget(self.log_status_label)
        
        status_layout.addStretch()
        
        # 添加AI问答预留区域提示
        ai_hint_label = QLabel("💡 AI问答功能即将上线")
        ai_hint_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #999;
                font-style: italic;
            }
        """)
        status_layout.addWidget(ai_hint_label)
        
        panel_layout.addLayout(status_layout)
        
        return self.md_reader_panel
    
    def toggle_md_reader_panel(self):
        """切换MD阅读器面板显示状态"""
        try:
            if not self.md_reader_visible:
                # 显示面板
                if not self.md_reader_panel:
                    self.create_md_reader_panel()
                
                # 添加到分割器
                self.main_splitter.addWidget(self.md_reader_panel)
                # 设置三面板的宽度比例（左侧220px，中间600px，右侧400px）
                self.main_splitter.setSizes([220, 600, 400])
                self.md_reader_visible = True
                
                # 更新按钮样式（激活状态）
                self.md_reader_button.setStyleSheet("""
                    QPushButton {
                        background-color: #7B1FA2;
                        color: white;
                        border: none;
                        border-radius: 15px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #6A1B9A;
                    }
                    QPushButton:pressed {
                        background-color: #4A148C;
                    }
                """)
                
                # 加载日志内容
                self.load_log_content()
                
                self.show_mini_notification("日志阅读器已打开")
                
            else:
                # 隐藏面板
                if self.md_reader_panel:
                    # 从分割器中移除
                    self.md_reader_panel.setParent(None)
                    # 恢复两面板布局
                    self.main_splitter.setSizes([220, 600])
                
                self.md_reader_visible = False
                
                # 恢复按钮样式（正常状态）
                self.md_reader_button.setStyleSheet("""
                    QPushButton {
                        background-color: #9C27B0;
                        color: white;
                        border: none;
                        border-radius: 15px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #7B1FA2;
                    }
                    QPushButton:pressed {
                        background-color: #6A1B9A;
                    }
                """)
                
                self.show_mini_notification("日志阅读器已关闭")
                
        except Exception as e:
            print(f"切换MD阅读器面板失败: {e}")
            QMessageBox.warning(self, "错误", f"切换MD阅读器面板失败：{str(e)}")
    
    def load_log_content(self):
        """加载日志文件内容"""
        try:
            if not self.log_file or not os.path.exists(self.log_file):
                # 没有绑定项目或日志文件不存在
                self.md_content_browser.setHtml("""
                <div style="text-align: center; color: #666; margin-top: 50px;">
                    <h3>📂 未找到日志文件</h3>
                    <p>请先绑定项目文件夹，系统将自动加载对应的日志文件。</p>
                    <p style="font-size: 12px; color: #999;">
                        预期日志文件：{项目名称}-log.md
                    </p>
                </div>
                """)
                self.log_file_label.setText("当前日志：未绑定项目")
                self.log_status_label.setText("无日志文件")
                return
            
            # 更新文件信息
            file_name = os.path.basename(self.log_file)
            file_size = os.path.getsize(self.log_file)
            size_mb = file_size / (1024 * 1024)
            
            self.log_file_label.setText(f"当前日志：{file_name} ({size_mb:.1f}MB)")
            
            # 读取文件内容
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 如果文件为空
            if not content.strip():
                self.md_content_browser.setHtml("""
                <div style="text-align: center; color: #666; margin-top: 50px;">
                    <h3>📝 日志文件为空</h3>
                    <p>开始使用工具后，工作记录将自动保存到此文件。</p>
                </div>
                """)
                self.log_status_label.setText("日志文件为空")
                return
            
            # 简单的Markdown转HTML处理
            html_content = self.convert_markdown_to_html(content)
            
            # 设置内容
            self.md_content_browser.setHtml(html_content)
            
            # 滚动到底部显示最新内容
            self.md_content_browser.verticalScrollBar().setValue(
                self.md_content_browser.verticalScrollBar().maximum()
            )
            
            # 更新状态
            lines = len(content.split('\n'))
            self.log_status_label.setText(f"已加载 {lines} 行内容")
            
        except Exception as e:
            print(f"加载日志内容失败: {e}")
            self.md_content_browser.setHtml(f"""
            <div style="text-align: center; color: #ff4444; margin-top: 50px;">
                <h3>⚠️ 加载失败</h3>
                <p>无法读取日志文件：{str(e)}</p>
            </div>
            """)
            self.log_status_label.setText(f"加载失败：{str(e)}")
    
    def convert_markdown_to_html(self, markdown_content):
        """简单的Markdown到HTML转换"""
        try:
            html_lines = []
            lines = markdown_content.split('\n')
            
            for line in lines:
                line = line.rstrip()
                
                # 处理标题
                if line.startswith('# '):
                    html_lines.append(f'<h1 style="color: #333; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px;">{line[2:]}</h1>')
                elif line.startswith('## '):
                    html_lines.append(f'<h2 style="color: #444; margin-top: 20px;">{line[3:]}</h2>')
                elif line.startswith('### '):
                    html_lines.append(f'<h3 style="color: #555;">{line[4:]}</h3>')
                elif line.startswith('#### '):
                    html_lines.append(f'<h4 style="color: #666;">{line[5:]}</h4>')
                
                # 处理列表
                elif line.startswith('- '):
                    html_lines.append(f'<li style="margin: 5px 0;">{line[2:]}</li>')
                elif line.startswith('* '):
                    html_lines.append(f'<li style="margin: 5px 0;">{line[2:]}</li>')
                
                # 处理代码块
                elif line.startswith('```'):
                    if '```' in line[3:]:  # 单行代码块
                        code = line[3:].replace('```', '')
                        html_lines.append(f'<code style="background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px;">{code}</code>')
                    else:
                        html_lines.append('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 3px solid #007acc;">')
                
                # 处理引用
                elif line.startswith('> '):
                    html_lines.append(f'<blockquote style="border-left: 3px solid #ccc; margin: 10px 0; padding-left: 10px; color: #666;">{line[2:]}</blockquote>')
                
                # 处理分隔线
                elif line.strip() == '---':
                    html_lines.append('<hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">')
                
                # 处理空行
                elif not line.strip():
                    html_lines.append('<br>')
                
                # 普通文本
                else:
                    # 处理粗体和斜体
                    processed_line = line
                    
                    # 粗体 **text**
                    import re
                    processed_line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', processed_line)
                    
                    # 斜体 *text*
                    processed_line = re.sub(r'\*(.*?)\*', r'<em>\1</em>', processed_line)
                    
                    # 内联代码 `code`
                    processed_line = re.sub(r'`(.*?)`', r'<code style="background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px;">\1</code>', processed_line)
                    
                    html_lines.append(f'<p style="margin: 8px 0; line-height: 1.6;">{processed_line}</p>')
            
            # 组装完整HTML
            html_content = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 20px;
                    }}
                    h1, h2, h3, h4 {{
                        margin-bottom: 10px;
                    }}
                    li {{
                        margin-left: 20px;
                    }}
                    pre {{
                        white-space: pre-wrap;
                        word-wrap: break-word;
                    }}
                </style>
            </head>
            <body>
                {''.join(html_lines)}
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            print(f"Markdown转HTML失败: {e}")
            return f"<p>内容加载失败：{str(e)}</p>"
    
    def refresh_log_content(self):
        """刷新日志内容并滚动到最后一个交互块"""
        try:
            self.load_log_content()
            
            # 滚动到最后一个交互块
            self.scroll_to_latest_interaction()
            
            self.show_mini_notification("日志内容已刷新，已定位到最新交互")
        except Exception as e:
            print(f"刷新日志内容失败: {e}")
            QMessageBox.warning(self, "错误", f"刷新日志内容失败：{str(e)}")
    
    def scroll_to_latest_interaction(self):
        """滚动到最后一个交互块的位置"""
        try:
            if not hasattr(self, 'md_content_browser') or not self.md_content_browser:
                return
                
            # 获取当前HTML内容
            html_content = self.md_content_browser.toHtml()
            
            # 查找最后一个"📥 输入"或"📤 输出"标记的位置
            last_input_pos = html_content.rfind("📥 输入")
            last_output_pos = html_content.rfind("📤 输出")
            
            # 确定最后一个交互块的位置
            last_interaction_pos = max(last_input_pos, last_output_pos)
            
            if last_interaction_pos > 0:
                # 滚动到页面底部，确保显示最新内容
                scrollbar = self.md_content_browser.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
                
                # 使用JavaScript精确定位到最后交互块
                self.md_content_browser.page().runJavaScript(f"""
                    var elements = document.querySelectorAll('*');
                    var lastInteraction = null;
                    for(var i = elements.length - 1; i >= 0; i--) {{
                        var text = elements[i].textContent || elements[i].innerText || '';
                        if(text.includes('📥 输入') || text.includes('📤 输出')) {{
                            lastInteraction = elements[i];
                            break;
                        }}
                    }}
                    if(lastInteraction) {{
                        lastInteraction.scrollIntoView({{behavior: 'smooth', block: 'start'}});
                    }}
                """)
            else:
                # 如果没找到交互块标记，直接滚动到底部
                scrollbar = self.md_content_browser.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
                
        except Exception as e:
            print(f"滚动到最新交互位置失败: {e}")
            # 降级处理：直接滚动到底部
            try:
                scrollbar = self.md_content_browser.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
            except:
                pass
    
    def generate_work_summary(self, user_input, ai_output):
        """生成工作总结并保存到项目日志文件"""
        try:
            # 获取当前时间
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 自动识别项目名称
            project_name = self.project_name if self.project_name else "injection"
            
            # 生成总结内容
            summary_content = f"""
# {current_time} (Cursor - 项目：{project_name})

## 📥 输入

{user_input}

## 📤 输出

### 🛠️ MD阅读器功能开发完成

#### 📋 工作内容概述
在injection项目中成功实现了MD阅读器功能，在标签区域底部添加了"日志阅读器"按键，点击后在工具右侧展开400px宽度的窗口面板，实现了日志文件的实时阅读和展示功能。

#### 🎯 技术实现要点

**1. UI布局扩展**：
- 在标签面板底部添加紫色"日志阅读器"按钮
- 实现动态面板切换，点击展开/收起右侧窗口
- 采用固定400px宽度，保持工具整体布局平衡

**2. MD阅读器核心功能**：
- 自动识别并加载项目对应的{project_name}-log.md文件
- 实现简化版Markdown到HTML转换器，支持：
  - 标题（H1-H4）样式渲染
  - 列表项格式化
  - 代码块和内联代码高亮
  - 引用块和分隔线
  - 粗体、斜体文本格式
- 内容自动滚动到底部，显示最新记录

**3. 交互体验优化**：
- 文件信息显示（文件名、大小）
- 实时刷新按钮，支持内容更新
- 优雅的关闭按钮和状态提示
- 空文件和错误状态的友好提示
- AI问答功能预留接口提示

**4. 代码架构设计**：
- 模块化方法设计：`create_md_reader_panel()`, `toggle_md_reader_panel()`, `load_log_content()`
- 状态管理：`md_reader_visible`, `md_reader_panel`变量
- 样式统一：与工具整体UI风格保持一致

#### 🔧 解决的问题

**问题1：项目日志阅读效率低**
- **解决方案**：集成MD阅读器，无需外部工具即可查看日志
- **效果**：提高工作效率，实现"边工作边查看"的流畅体验

**问题2：日志内容格式化显示**
- **解决方案**：自研Markdown解析器，适配项目日志格式
- **效果**：良好的阅读体验，支持代码高亮和结构化显示

**问题3：界面空间利用**
- **解决方案**：侧边展开设计，不影响主要工作区域
- **效果**：充分利用屏幕空间，保持工具紧凑性

#### ✅ 完成状态

**✅ UI组件开发完成**：
- 标签按钮已添加并集成到现有界面
- 面板展开/收起逻辑已实现
- 按钮状态切换和视觉反馈已完善

**✅ 核心功能实现完成**：
- 日志文件自动识别和加载机制已建立
- Markdown渲染引擎已开发并测试
- 内容刷新和错误处理机制已完善

**✅ 扩展功能预留完成**：
- AI问答功能接口已预留
- 界面布局为后续功能扩展做好准备
- 代码结构支持功能模块化添加

---

**🎯 核心价值**：实现了项目内日志的即时查看功能，显著提升工作效率和用户体验。

**💡 技术亮点**：自研轻量级Markdown解析器，完美适配项目需求，无需引入第三方依赖。

**🚀 后续计划**：AI问答功能开发，实现与日志内容的智能交互。

✅ 命令注入完成 - Cursor - {current_time}

"""
            
            # 确定日志文件路径
            if self.project_folder and self.project_name:
                log_file_path = os.path.join(self.project_folder, f"{self.project_name}-log.md")
            else:
                # 如果没有绑定项目，使用默认路径
                log_file_path = os.path.join(APP_DIR, "injection-log.md")
            
            # 追加到日志文件
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(summary_content)
            
            print(f"✅ 工作总结已保存到: {log_file_path}")
            
            # 如果MD阅读器已打开，自动刷新内容
            if self.md_reader_visible and self.md_reader_panel:
                self.load_log_content()
            
        except Exception as e:
            print(f"生成工作总结失败: {e}")

    def force_refresh_html_pages(self):
        """强制刷新所有HTML页面，清除WebEngine缓存"""
        try:
            print("🔄 开始强制刷新HTML页面...")
            
            # 刷新思维导图页面
            if hasattr(self.layout_manager, 'jsmind_view') and self.layout_manager.jsmind_view:
                if hasattr(self.layout_manager.jsmind_view, 'reload'):
                    # WebEngine 方式刷新
                    self.layout_manager.jsmind_view.reload()
                    print("✅ WebEngine思维导图页面已强制刷新")
                elif hasattr(self.layout_manager.jsmind_view, 'setHtml'):
                    # QTextBrowser方式重新加载HTML文件
                    self.reload_html_file_for_textbrowser()
                    print("✅ TextBrowser思维导图页面已重新加载")
            
            # 刷新MD阅读器页面（如果存在WebEngine组件）
            if hasattr(self.layout_manager, 'md_content_display'):
                if hasattr(self.layout_manager.md_content_display, 'reload'):
                    self.layout_manager.md_content_display.reload()
                    print("✅ MD阅读器页面已强制刷新")
            
            # 强制刷新页面时添加时间戳参数避免缓存
            if hasattr(self.layout_manager, 'jsmind_view') and hasattr(self.layout_manager.jsmind_view, 'load'):
                import time
                import os
                
                # 查找HTML文件并重新加载
                html_files = ['jsmind-local.html', 'mindmap-simple.html', 'jsmind-standalone.html']
                for html_file in html_files:
                    file_path = os.path.join(os.getcwd(), html_file)
                    if os.path.exists(file_path):
                        # 添加时间戳参数强制绕过缓存
                        timestamp = str(int(time.time()))
                        url_with_timestamp = f"file:///{file_path.replace(chr(92), '/')}?t={timestamp}"
                        
                        from PyQt5.QtCore import QUrl
                        self.layout_manager.jsmind_view.load(QUrl(url_with_timestamp))
                        print(f"✅ 强制重新加载: {html_file} (带时间戳: {timestamp})")
                        break
                        
            self.show_mini_notification("🔄 HTML页面已强制刷新")
            
        except Exception as e:
            print(f"❌ 强制刷新HTML页面失败: {e}")
            self.show_mini_notification("❌ HTML页面刷新失败")
    
    def reload_html_file_for_textbrowser(self):
        """为TextBrowser重新加载HTML文件内容"""
        try:
            import os
            
            # 按优先级查找HTML文件
            html_files = [
                ('jsmind-local.html', 'node_modules/jsmind/es6/jsmind.js'),
                ('mindmap-simple.html', None),
                ('jsmind-standalone.html', None)
            ]
            
            for html_file, dependency in html_files:
                file_path = os.path.join(os.getcwd(), html_file)
                if os.path.exists(file_path):
                    # 检查依赖（如果需要）
                    if dependency:
                        dep_path = os.path.join(os.getcwd(), dependency)
                        if not os.path.exists(dep_path):
                            continue
                    
                    # 重新读取HTML文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # 添加缓存清除meta标签
                    cache_clear_meta = """
                    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
                    <meta http-equiv="Pragma" content="no-cache">
                    <meta http-equiv="Expires" content="0">
                    """
                    
                    # 在head标签后插入缓存清除meta标签
                    if '<head>' in html_content:
                        html_content = html_content.replace('<head>', f'<head>{cache_clear_meta}')
                    
                    self.layout_manager.jsmind_view.setHtml(html_content)
                    print(f"✅ TextBrowser重新加载: {html_file} (已添加缓存清除标签)")
                    break
                    
        except Exception as e:
            print(f"❌ TextBrowser重新加载HTML文件失败: {e}")

    def clear_webengine_cache(self):
        """清除WebEngine缓存"""
        try:
            # 对于PyQt5 WebEngine，可以尝试清除缓存
            if hasattr(self.layout_manager, 'jsmind_view') and hasattr(self.layout_manager.jsmind_view, 'page'):
                page = self.layout_manager.jsmind_view.page()
                if hasattr(page, 'profile'):
                    profile = page.profile()
                    if hasattr(profile, 'clearHttpCache'):
                        profile.clearHttpCache()
                        print("✅ WebEngine HTTP缓存已清除")
                    if hasattr(profile, 'clearAllVisitedLinks'):
                        profile.clearAllVisitedLinks()
                        print("✅ WebEngine访问链接缓存已清除")
        except Exception as e:
            print(f"⚠️ 清除WebEngine缓存失败: {e}")

    def should_refresh_html_on_reload(self, module_name):
        """判断是否需要在模块重载时刷新HTML页面"""
        # 影响HTML显示的模块列表
        html_related_modules = [
            'layout_manager',      # 布局管理器影响HTML容器
            'mindmap_integration', # 脑图集成模块
            'jsmind',             # 如果有jsmind相关模块
        ]
        
        return module_name in html_related_modules

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 