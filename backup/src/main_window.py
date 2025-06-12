from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QListWidget, QPushButton, 
                            QMessageBox)
from PyQt5.QtCore import Qt
from pynput import keyboard
import pystray
from PIL import Image
import os
from src.llm_manager import LLMManager
from src.llm_detail import LLMDetail
from src.debug_window import DebugWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.llm_manager = LLMManager()
        self.current_model = None
        self.initUI()
        self.setup_hotkey()
        self.setup_tray()
        
    def initUI(self):
        """初始化UI"""
        self.setWindowTitle('Sealed LLM')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QHBoxLayout()
        central_widget.setLayout(layout)
        
        # 左侧模型列表
        left_layout = QVBoxLayout()
        model_label = QLabel('大模型列表:', self)
        self.model_list = QListWidget(self)
        self.model_list.itemClicked.connect(self.on_model_selected)
        self.update_model_list()
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton('添加', self)
        self.add_btn.clicked.connect(self.add_model)
        self.edit_btn = QPushButton('编辑', self)
        self.edit_btn.clicked.connect(self.edit_model)
        self.delete_btn = QPushButton('删除', self)
        self.delete_btn.clicked.connect(self.delete_model)
        self.debug_btn = QPushButton('调试', self)
        self.debug_btn.clicked.connect(self.open_debug)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.debug_btn)
        
        left_layout.addWidget(model_label)
        left_layout.addWidget(self.model_list)
        left_layout.addLayout(btn_layout)
        
        # 右侧详情区域
        right_layout = QVBoxLayout()
        detail_label = QLabel('模型详情:', self)
        self.detail_widget = QWidget(self)
        right_layout.addWidget(detail_label)
        right_layout.addWidget(self.detail_widget)
        
        # 添加布局
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)
        
        # 设置窗口标志
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
    def update_model_list(self):
        """更新模型列表"""
        self.model_list.clear()
        for model in self.llm_manager.get_all_models():
            self.model_list.addItem(model['name'])
            
    def on_model_selected(self, item):
        """选择模型"""
        model_name = item.text()
        self.current_model = model_name
        self.update_detail_view()
        
    def update_detail_view(self):
        """更新详情视图"""
        if not self.current_model:
            return
            
        model = self.llm_manager.get_model(self.current_model)
        if model:
            # TODO: 实现详情视图更新
            pass
            
    def add_model(self):
        """添加模型"""
        # TODO: 实现添加模型对话框
        pass
        
    def edit_model(self):
        """编辑模型"""
        if not self.current_model:
            QMessageBox.warning(self, "错误", "请先选择一个模型")
            return
            
        # TODO: 实现编辑模型对话框
        pass
        
    def delete_model(self):
        """删除模型"""
        if not self.current_model:
            QMessageBox.warning(self, "错误", "请先选择一个模型")
            return
            
        reply = QMessageBox.question(
            self, 
            "确认删除",
            f"确定要删除模型 {self.current_model} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.llm_manager.delete_model(self.current_model)
            self.current_model = None
            self.update_model_list()
            self.update_detail_view()
            
    def open_debug(self):
        """打开调试窗口"""
        if not self.current_model:
            QMessageBox.warning(self, "错误", "请先选择一个模型")
            return
            
        llm_detail = LLMDetail(self.current_model)
        debug_window = DebugWindow(self, llm_detail)
        debug_window.exec_()
        
    def setup_hotkey(self):
        """设置热键监听"""
        self.hotkey = keyboard.GlobalHotKeys({
            '<shift>+<f2>': self.toggle_window
        })
        self.hotkey.start()
        
    def setup_tray(self):
        """设置系统托盘"""
        # 创建托盘图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icon.png')
        icon = Image.open(icon_path)
        self.tray = pystray.Icon("sealed_llm", icon, "Sealed LLM")
        
        # 添加菜单项
        self.tray.menu = pystray.Menu(
            pystray.MenuItem("显示", self.show_window),
            pystray.MenuItem("退出", self.quit_application)
        )
        
        # 启动托盘
        self.tray.run()
        
    def toggle_window(self):
        """切换窗口显示状态"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            
    def show_window(self):
        """显示窗口"""
        self.show()
        
    def quit_application(self):
        """退出应用程序"""
        self.hotkey.stop()
        self.tray.stop()
        QApplication.quit() 