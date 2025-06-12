import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                            QSpinBox, QTabWidget, QSplitter, QGroupBox,
                            QCheckBox, QComboBox, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QIcon

from cursor_monitor import CursorMonitor
from cursor_processor import CursorOutputProcessor

class CursorMonitorGUI(QMainWindow):
    """Cursor AI输出监控工具的图形界面"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化设置
        self.settings = QSettings("CursorMonitorTool", "CursorMonitor")
        
        # 初始化监控和处理器
        self.monitor = CursorMonitor()
        self.processor = CursorOutputProcessor()
        
        # 连接信号
        self.connect_signals()
        
        # 设置UI
        self.init_ui()
        self.load_settings()
        
        # 设置窗口属性
        self.setWindowTitle("Cursor AI输出监控工具")
        self.setMinimumSize(800, 600)
        
    def init_ui(self):
        """初始化用户界面"""
        # 主窗口布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # 创建一个分割器，上方是控制面板，下方是标签页
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # 上方控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        
        # 功能组
        function_group = QGroupBox("监控控制")
        function_layout = QHBoxLayout(function_group)
        
        # 监控间隔设置
        interval_layout = QVBoxLayout()
        interval_label = QLabel("监控间隔(秒):")
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 60)
        self.interval_spinbox.setValue(3)
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spinbox)
        function_layout.addLayout(interval_layout)
        
        # 控制按钮
        self.start_button = QPushButton("开始监控")
        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button = QPushButton("停止监控")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        function_layout.addWidget(self.start_button)
        function_layout.addWidget(self.stop_button)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        function_layout.addWidget(self.status_label)
        
        # 添加功能组到控制面板
        control_layout.addWidget(function_group)
        
        # 工具组
        tools_group = QGroupBox("工具选项")
        tools_layout = QHBoxLayout(tools_group)
        
        # 自动复制选项
        self.auto_copy_checkbox = QCheckBox("自动复制到剪贴板")
        tools_layout.addWidget(self.auto_copy_checkbox)
        
        # 保存到文件按钮
        self.save_button = QPushButton("保存到文件")
        self.save_button.clicked.connect(self.save_to_file)
        tools_layout.addWidget(self.save_button)
        
        # 清空按钮
        self.clear_button = QPushButton("清空输出")
        self.clear_button.clicked.connect(self.clear_output)
        tools_layout.addWidget(self.clear_button)
        
        # 添加工具组到控制面板
        control_layout.addWidget(tools_group)
        
        # 将控制面板添加到分割器
        splitter.addWidget(control_panel)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 文本输出标签页
        self.text_tab = QWidget()
        text_layout = QVBoxLayout(self.text_tab)
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        text_layout.addWidget(self.text_output)
        self.tab_widget.addTab(self.text_tab, "文本输出")
        
        # 代码输出标签页
        self.code_tab = QWidget()
        code_layout = QVBoxLayout(self.code_tab)
        self.code_output = QTextEdit()
        self.code_output.setReadOnly(True)
        # 设置等宽字体用于代码显示
        code_font = QFont("Consolas", 10)
        self.code_output.setFont(code_font)
        code_layout.addWidget(self.code_output)
        self.tab_widget.addTab(self.code_tab, "代码输出")
        
        # 日志标签页
        self.log_tab = QWidget()
        log_layout = QVBoxLayout(self.log_tab)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        self.tab_widget.addTab(self.log_tab, "日志")
        
        # 将标签页添加到分割器
        splitter.addWidget(self.tab_widget)
        
        # 设置分割器的初始大小比例
        splitter.setSizes([150, 450])
        
        # 设置中央部件
        self.setCentralWidget(central_widget)
    
    def connect_signals(self):
        """连接信号与槽"""
        # 监控器信号
        self.monitor.status_update.connect(self.update_status)
        self.monitor.text_captured.connect(self.processor.process_output)
        
        # 处理器信号
        self.processor.status_update.connect(self.update_log)
        self.processor.text_processed.connect(self.handle_processed_text)
    
    def start_monitoring(self):
        """开始监控"""
        interval = self.interval_spinbox.value()
        self.monitor.set_interval(interval)
        self.monitor.start_monitoring()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.update_status("监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitor.stop_monitoring()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.update_status("监控已停止")
    
    def update_status(self, message):
        """更新状态标签"""
        self.status_label.setText(message)
        self.update_log(message)
    
    def update_log(self, message):
        """更新日志输出"""
        timestamp = self.get_timestamp()
        self.log_output.append(f"[{timestamp}] {message}")
    
    def get_timestamp(self):
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    def handle_processed_text(self, text, text_type):
        """处理处理后的文本"""
        # 根据类型分别处理
        if text_type.startswith("code_"):
            self.code_output.append(text)
            self.tab_widget.setCurrentWidget(self.code_tab)
            
            # 自动复制代码到剪贴板
            if self.auto_copy_checkbox.isChecked():
                self.processor.copy_to_clipboard(text)
        elif text_type == "code":
            self.code_output.append(text)
            self.tab_widget.setCurrentWidget(self.code_tab)
        elif text_type == "text":
            self.text_output.append(text)
            self.tab_widget.setCurrentWidget(self.text_tab)
    
    def save_to_file(self):
        """保存当前标签页内容到文件"""
        current_tab = self.tab_widget.currentWidget()
        
        if current_tab == self.text_tab:
            content = self.text_output.toPlainText()
            file_type = "文本文件 (*.txt)"
            default_name = "cursor_text_output.txt"
        elif current_tab == self.code_tab:
            content = self.code_output.toPlainText()
            file_type = "所有文件 (*.*)"
            default_name = "cursor_code_output.txt"
        elif current_tab == self.log_tab:
            content = self.log_output.toPlainText()
            file_type = "日志文件 (*.log)"
            default_name = "cursor_monitor.log"
        else:
            return
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", default_name, file_type
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.update_status(f"已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"文件保存失败: {str(e)}")
    
    def clear_output(self):
        """清空当前标签页的输出"""
        current_tab = self.tab_widget.currentWidget()
        
        if current_tab == self.text_tab:
            self.text_output.clear()
        elif current_tab == self.code_tab:
            self.code_output.clear()
        elif current_tab == self.log_tab:
            self.log_output.clear()
    
    def load_settings(self):
        """加载应用设置"""
        # 加载窗口位置和大小
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        
        # 加载监控间隔
        if self.settings.contains("interval"):
            self.interval_spinbox.setValue(int(self.settings.value("interval")))
        
        # 加载自动复制设置
        if self.settings.contains("auto_copy"):
            self.auto_copy_checkbox.setChecked(
                self.settings.value("auto_copy") == "true"
            )
    
    def save_settings(self):
        """保存应用设置"""
        # 保存窗口位置和大小
        self.settings.setValue("geometry", self.saveGeometry())
        
        # 保存监控间隔
        self.settings.setValue("interval", self.interval_spinbox.value())
        
        # 保存自动复制设置
        self.settings.setValue(
            "auto_copy", str(self.auto_copy_checkbox.isChecked()).lower()
        )
    
    def closeEvent(self, event):
        """关闭窗口事件处理"""
        # 停止监控
        self.stop_monitoring()
        
        # 保存设置
        self.save_settings()
        
        # 接受关闭事件
        event.accept()

# 主入口点
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = CursorMonitorGUI()
    window.show()
    
    sys.exit(app.exec_()) 