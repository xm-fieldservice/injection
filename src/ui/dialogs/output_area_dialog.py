"""
输出区域校准对话框 - 用于校准和管理输出区域
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QMessageBox, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer
import time

class OutputAreaDialog(QDialog):
    """输出区域校准对话框"""
    
    def __init__(self, parent=None, ui_automation_service=None):
        """初始化对话框"""
        super().__init__(parent)
        self.parent = parent
        self.ui_automation_service = ui_automation_service
        self.calibration_timer = None
        self.initUI()
    
    def initUI(self):
        """初始化UI"""
        self.setWindowTitle("输出区域校准")
        self.setMinimumSize(500, 400)
        
        # 创建布局
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 添加说明标签
        instruction_label = QLabel(
            '校准输出区域可以让工具自动获取目标应用的输出内容。\n'
            + '点击"开始校准"按钮，然后点击目标应用的输出区域。'
        )
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # 当前状态
        self.status_label = QLabel("未校准")
        self.status_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(self.status_label)
        
        # 校准信息
        self.info_list = QListWidget()
        layout.addWidget(self.info_list)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 开始校准按钮
        self.calibrate_button = QPushButton("开始校准")
        self.calibrate_button.clicked.connect(self.start_calibration)
        button_layout.addWidget(self.calibrate_button)
        
        # 测试按钮
        self.test_button = QPushButton("测试获取")
        self.test_button.clicked.connect(self.test_get_output)
        self.test_button.setEnabled(False)
        button_layout.addWidget(self.test_button)
        
        # 清除按钮
        self.clear_button = QPushButton("清除校准")
        self.clear_button.clicked.connect(self.clear_calibration)
        self.clear_button.setEnabled(False)
        button_layout.addWidget(self.clear_button)
        
        # 关闭按钮
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # 更新状态显示
        self.update_status_display()
    
    def update_status_display(self):
        """更新状态显示"""
        self.info_list.clear()
        
        if self.ui_automation_service.output_window_info:
            self.status_label.setText("已校准")
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
            self.test_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            
            # 添加窗口信息
            window_info = self.ui_automation_service.output_window_info
            self.info_list.addItem(f"窗口标题: {window_info.get('title', '未知')}")
            self.info_list.addItem(f"窗口类名: {window_info.get('class_name', '未知')}")
            
            # 添加元素信息
            element_info = self.ui_automation_service.output_element_info
            self.info_list.addItem(f"元素类型: {element_info.get('control_type', '未知')}")
            self.info_list.addItem(f"元素名称: {element_info.get('name', '未知')}")
            self.info_list.addItem(f"元素类名: {element_info.get('class_name', '未知')}")
            
            # 添加路径信息
            if self.ui_automation_service.output_element_path:
                path_str = " > ".join([f"[{p[0]}:{p[1]}]" for p in self.ui_automation_service.output_element_path])
                self.info_list.addItem(f"元素路径: {path_str}")
        else:
            self.status_label.setText("未校准")
            self.status_label.setStyleSheet("font-weight: bold; color: #666;")
            self.test_button.setEnabled(False)
            self.clear_button.setEnabled(False)
            self.info_list.addItem("请点击“开始校准”按钮，然后点击目标应用的输出区域")
    
    def start_calibration(self):
        """开始校准流程"""
        # 显示提示信息
        QMessageBox.information(self, '提示', '请点击目标应用的输出区域...')
        
        # 隐藏对话框
        self.hide()
        
        # 等待一段时间，让用户有机会点击
        QTimer.singleShot(500, self.perform_calibration)
    
    def perform_calibration(self):
        """执行校准"""
        # 执行校准
        success, result = self.ui_automation_service.calibrate_output_area()
        
        # 显示对话框
        self.show()
        self.activateWindow()
        
        if success:
            QMessageBox.information(self, '成功', f'已成功校准输出区域:\n窗口: {result["window_title"]}\n元素: {result["element_name"]}')
            self.update_status_display()
        else:
            QMessageBox.warning(self, '失败', f'校准失败: {result}')
    
    def test_get_output(self):
        """测试获取输出内容"""
        success, result = self.ui_automation_service.get_output_text()
        
        if success:
            # 显示前100个字符
            preview = result[:100] + ("..." if len(result) > 100 else "")
            QMessageBox.information(self, '成功', f'成功获取文本内容:\n{preview}')
        else:
            QMessageBox.warning(self, '失败', f'获取文本失败: {result}')
    
    def clear_calibration(self):
        """清除校准信息"""
        if QMessageBox.question(self, '确认', '确定要清除校准信息吗？') == QMessageBox.Yes:
            self.ui_automation_service.output_window_info = {}
            self.ui_automation_service.output_element_info = {}
            self.ui_automation_service.output_element_path = []
            self.update_status_display()
            QMessageBox.information(self, '成功', '已清除校准信息')
