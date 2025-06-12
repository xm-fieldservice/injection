from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QTextEdit, QLabel, QSystemTrayIcon,
                            QMenu, QMessageBox, QShortcut)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon, QKeySequence

class MainWindow(QMainWindow):
    def __init__(self, config_manager, template_service, ai_service):
        super().__init__()
        self.config_manager = config_manager
        self.template_service = template_service
        self.ai_service = ai_service
        
        # 从配置管理器获取配置
        self.target_window = self.config_manager.get('target_window')
        self.target_position = self.config_manager.get('target_position')
        
        self.initUI()
        self.setupTrayIcon()
        self.setupShortcut()
    
    def initUI(self):
        """初始化用户界面"""
        self.setWindowTitle('提示词注入工具')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedSize(400, 300)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout(central_widget)
        
        # 创建标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题标签
        title_label = QLabel('提示词注入工具')
        title_bar_layout.addWidget(title_label)
        
        # 最小化按钮
        minimize_button = QPushButton('—')
        minimize_button.setFixedSize(30, 30)
        minimize_button.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(minimize_button)
        
        # 关闭按钮
        close_button = QPushButton('×')
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.close)
        title_bar_layout.addWidget(close_button)
        
        layout.addWidget(title_bar)
        
        # 创建命令输入区域
        self.command_input = QTextEdit()
        self.command_input.setPlaceholderText('请输入要注入的命令...')
        layout.addWidget(self.command_input)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        
        # 注入按钮
        inject_button = QPushButton('注入命令')
        inject_button.clicked.connect(self.inject_command)
        button_layout.addWidget(inject_button)
        
        # 清除按钮
        clear_button = QPushButton('清除')
        clear_button.clicked.connect(self.clear_input)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
    
    def setupTrayIcon(self):
        """设置系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('resources/icon.png'))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        show_action = tray_menu.addAction('显示')
        show_action.triggered.connect(self.show)
        quit_action = tray_menu.addAction('退出')
        quit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def setupShortcut(self):
        """设置快捷键"""
        self.shortcut = QShortcut(QKeySequence(Qt.SHIFT + Qt.Key_F2), self)
        self.shortcut.activated.connect(self.toggle_window)
    
    def toggle_window(self):
        """切换窗口显示状态"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
    
    def inject_command(self):
        """注入命令"""
        command = self.command_input.toPlainText()
        if not command:
            QMessageBox.warning(self, '警告', '请输入要注入的命令')
            return
        
        if not self.target_window or not self.target_position:
            QMessageBox.warning(self, '警告', '请先设置目标窗口和位置')
            return
        
        success, message = self.injection_service.inject_command(
            command,
            self.target_window,
            self.target_position
        )
        
        if success:
            QMessageBox.information(self, '成功', message)
            self.clear_input()
        else:
            QMessageBox.critical(self, '错误', message)
    
    def clear_input(self):
        """清除输入"""
        self.command_input.clear()
    
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def closeEvent(self, event):
        """处理关闭事件"""
        event.ignore()
        self.hide() 