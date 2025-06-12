from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
                            QSplitter, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt

class TemplateManagerDialog(QDialog):
    def __init__(self, template_manager, parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.setWindowTitle("模板管理")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.init_ui()
        self.load_templates()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建水平分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：模板树形视图
        self.template_tree = QTreeWidget()
        self.template_tree.setHeaderLabels(["场景/版本"])
        self.template_tree.itemSelectionChanged.connect(self.on_template_selected)
        splitter.addWidget(self.template_tree)
        
        # 右侧：编辑和预览区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 模板编辑器
        editor_label = QLabel("模板编辑:")
        self.template_editor = QTextEdit()
        self.template_editor.textChanged.connect(self.on_template_changed)
        right_layout.addWidget(editor_label)
        right_layout.addWidget(self.template_editor)
        
        # 实时预览
        preview_label = QLabel("实时预览:")
        self.preview_panel = QTextEdit()
        self.preview_panel.setReadOnly(True)
        right_layout.addWidget(preview_label)
        right_layout.addWidget(self.preview_panel)
        
        splitter.addWidget(right_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 导入导出按钮
        self.import_btn = QPushButton("导入模板")
        self.import_btn.clicked.connect(self.import_template)
        self.export_btn = QPushButton("导出模板")
        self.export_btn.clicked.connect(self.export_template)
        
        # 保存取消按钮
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_template)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # 添加所有组件到主布局
        layout.addWidget(splitter)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_templates(self):
        """加载模板到树形视图"""
        self.template_tree.clear()
        
        # 获取所有场景
        scenes = self.template_manager.get_scenes()
        for scene in scenes:
            # 创建场景节点
            scene_item = QTreeWidgetItem(self.template_tree)
            scene_item.setText(0, scene)
            
            # 添加版本子节点
            versions = self.template_manager.get_scene_versions(scene)
            for version in versions:
                version_item = QTreeWidgetItem(scene_item)
                version_item.setText(0, version)
                version_item.setData(0, Qt.UserRole, {"scene": scene, "version": version})
    
    def on_template_selected(self):
        """处理模板选择事件"""
        items = self.template_tree.selectedItems()
        if not items:
            return
            
        item = items[0]
        data = item.data(0, Qt.UserRole)
        if data:  # 如果是版本节点
            template = self.template_manager.get_template(data["scene"], data["version"])
            if template:
                # 显示模板内容
                template_text = f"前缀:\n{template['prefix']}\n\n后缀:\n{template['suffix']}"
                self.template_editor.setText(template_text)
    
    def on_template_changed(self):
        """处理模板内容变更事件"""
        # 更新预览
        self.preview_panel.setText(self.template_editor.toPlainText())
    
    def save_template(self):
        """保存模板"""
        items = self.template_tree.selectedItems()
        if not items:
            QMessageBox.warning(self, "警告", "请先选择一个模板版本")
            return
            
        item = items[0]
        data = item.data(0, Qt.UserRole)
        if not data:
            QMessageBox.warning(self, "警告", "请选择具体的模板版本")
            return
            
        try:
            # 解析编辑器内容
            content = self.template_editor.toPlainText()
            parts = content.split("\n\n")
            if len(parts) < 2:
                QMessageBox.warning(self, "警告", "模板格式不正确，需要包含前缀和后缀")
                return
                
            prefix = parts[0].replace("前缀:\n", "")
            suffix = parts[1].replace("后缀:\n", "")
            
            # 保存模板
            self.template_manager.save_template(data["scene"], data["version"], prefix, suffix)
            
            QMessageBox.information(self, "成功", "模板保存成功")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存模板失败: {str(e)}")
    
    def import_template(self):
        """导入模板"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入模板",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                self.template_manager.import_templates(file_path)
                self.load_templates()
                QMessageBox.information(self, "成功", "模板导入成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入模板失败: {str(e)}")
    
    def export_template(self):
        """导出模板"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出模板",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                self.template_manager.export_templates(file_path)
                QMessageBox.information(self, "成功", "模板导出成功")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出模板失败: {str(e)}") 