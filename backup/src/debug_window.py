from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTextEdit, QPushButton, QDoubleSpinBox, QSpinBox,
                            QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt
from .llm_detail import LLMDetail

class DebugWindow(QDialog):
    def __init__(self, parent=None, llm_detail: LLMDetail = None):
        super().__init__(parent)
        self.llm_detail = llm_detail
        self.initUI()
        
    def initUI(self):
        """初始化UI"""
        self.setWindowTitle('调试窗口')
        self.setGeometry(200, 200, 800, 600)
        
        # 创建主布局
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 参数配置区域
        params_layout = QHBoxLayout()
        
        # 温度设置
        temp_layout = QVBoxLayout()
        temp_label = QLabel('温度:', self)
        self.temp_spin = QDoubleSpinBox(self)
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(0.7)
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_spin)
        
        # 最大token设置
        token_layout = QVBoxLayout()
        token_label = QLabel('最大Token:', self)
        self.token_spin = QSpinBox(self)
        self.token_spin.setRange(1, 4096)
        self.token_spin.setValue(2000)
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_spin)
        
        # 功能开关
        self.web_search = QCheckBox('启用联网搜索', self)
        self.deep_thought = QCheckBox('启用深度思考', self)
        
        params_layout.addLayout(temp_layout)
        params_layout.addLayout(token_layout)
        params_layout.addWidget(self.web_search)
        params_layout.addWidget(self.deep_thought)
        
        layout.addLayout(params_layout)
        
        # 输入输出区域
        io_layout = QHBoxLayout()
        
        # 输入区域
        input_layout = QVBoxLayout()
        input_label = QLabel('输入:', self)
        self.input_text = QTextEdit(self)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_text)
        
        # 输出区域
        output_layout = QVBoxLayout()
        output_label = QLabel('输出:', self)
        self.output_text = QTextEdit(self)
        self.output_text.setReadOnly(True)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_text)
        
        io_layout.addLayout(input_layout)
        io_layout.addLayout(output_layout)
        
        layout.addLayout(io_layout)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.send_btn = QPushButton('发送', self)
        self.send_btn.clicked.connect(self.send_request)
        
        self.clear_btn = QPushButton('清除', self)
        self.clear_btn.clicked.connect(self.clear_all)
        
        btn_layout.addWidget(self.send_btn)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        
    def send_request(self):
        """发送请求"""
        if not self.llm_detail:
            QMessageBox.warning(self, "错误", "未选择大模型")
            return
            
        # 获取输入
        input_text = self.input_text.toPlainText().strip()
        if not input_text:
            QMessageBox.warning(self, "错误", "请输入内容")
            return
            
        # 获取参数
        temperature = self.temp_spin.value()
        max_tokens = self.token_spin.value()
        enable_web = self.web_search.isChecked()
        enable_deep = self.deep_thought.isChecked()
        
        # TODO: 实现API调用
        self.output_text.setText("正在调用API...")
        
    def clear_all(self):
        """清除所有内容"""
        self.input_text.clear()
        self.output_text.clear()
        self.temp_spin.setValue(0.7)
        self.token_spin.setValue(2000)
        self.web_search.setChecked(False)
        self.deep_thought.setChecked(False) 