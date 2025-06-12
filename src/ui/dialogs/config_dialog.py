from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt

class ConfigDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("配置管理")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.init_ui()
        self.load_current_config()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 配置显示区域
        config_group = QVBoxLayout()
        config_label = QLabel("当前配置:")
        self.config_view = QTextEdit()
        self.config_view.setReadOnly(True)
        config_group.addWidget(config_label)
        config_group.addWidget(self.config_view)
        
        # 目录选择区域
        dir_group = QHBoxLayout()
        self.dir_label = QLabel("配置目录:")
        self.dir_path = QLabel()
        self.dir_selector = QPushButton("选择目录")
        self.dir_selector.clicked.connect(self.select_config_dir)
        dir_group.addWidget(self.dir_label)
        dir_group.addWidget(self.dir_path)
        dir_group.addWidget(self.dir_selector)
        
        # 日志目录选择
        log_group = QHBoxLayout()
        self.log_label = QLabel("日志目录:")
        self.log_path = QLabel()
        self.log_selector = QPushButton("选择目录")
        self.log_selector.clicked.connect(self.select_log_dir)
        log_group.addWidget(self.log_label)
        log_group.addWidget(self.log_path)
        log_group.addWidget(self.log_selector)
        
        # 按钮区域
        button_group = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_config)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_group.addWidget(self.save_btn)
        button_group.addWidget(self.cancel_btn)
        
        # 添加所有组件到主布局
        layout.addLayout(config_group)
        layout.addLayout(dir_group)
        layout.addLayout(log_group)
        layout.addLayout(button_group)
        
        self.setLayout(layout)
    
    def load_current_config(self):
        """加载当前配置"""
        config = self.config_manager.get_all_config()
        # 格式化配置显示
        formatted_config = "{\n"
        for key, value in config.items():
            # 对值进行格式化处理
            if isinstance(value, str):
                formatted_value = f'"{value}"'
            elif value is None:
                formatted_value = 'None'
            else:
                formatted_value = str(value)
            # 添加缩进和换行
            formatted_config += f'    "{key}": {formatted_value},\n'
        formatted_config = formatted_config.rstrip(',\n') + "\n}"
        
        self.config_view.setText(formatted_config)
        self.dir_path.setText(self.config_manager.config_dir)
        self.log_path.setText(self.config_manager.logs_dir)
    
    def select_config_dir(self):
        """选择配置目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择配置目录")
        if dir_path:
            self.dir_path.setText(dir_path)
    
    def select_log_dir(self):
        """选择日志目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择日志目录")
        if dir_path:
            self.log_path.setText(dir_path)
    
    def save_config(self):
        """保存配置"""
        try:
            self.config_manager.set_config_dir(self.dir_path.text())
            self.config_manager.set_logs_dir(self.log_path.text())
            self.accept()
            QMessageBox.information(self, "成功", "配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {str(e)}") 