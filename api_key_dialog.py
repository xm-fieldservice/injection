from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox)
from PyQt5.QtCore import Qt

class APIKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        """初始化UI"""
        self.setWindowTitle('选择大模型')
        self.setFixedSize(400, 100)
        
        layout = QVBoxLayout()
        
        # 模型选择
        model_layout = QHBoxLayout()
        model_label = QLabel('选择模型:', self)
        self.model_combo = QComboBox(self)
        self.model_combo.setFixedWidth(250)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        
        # 添加布局
        layout.addLayout(model_layout)
        self.setLayout(layout)
        
        # 添加模型列表
        self.model_combo.addItems([
            "DeepSeek",
            "ChatGLM",
            "Claude"
        ])
        
    def get_api_key(self):
        """保持与原有代码的兼容性"""
        return "" 