from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QTextEdit, QPushButton,
                           QListWidget, QMessageBox, QComboBox, QInputDialog)
from PyQt5.QtCore import Qt
from template_manager import TemplateManager

class TemplateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_manager = TemplateManager()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('模板管理中心')
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 添加标题和说明
        title_label = QLabel("模板管理中心")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                padding: 10px;
                border-bottom: 2px solid #e0e0e0;
                margin-bottom: 10px;
            }
        """)
        
        desc_label = QLabel("在这里您可以创建、编辑、重命名、复制和删除场景及其模板版本")
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                padding: 5px 10px;
                margin-bottom: 10px;
            }
        """)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)
        
        # 创建布局
        layout = QHBoxLayout()
        
        # 左侧布局：场景列表
        left_layout = QVBoxLayout()
        
        # 场景列表
        self.scene_list = QListWidget()
        self.scene_list.itemClicked.connect(self.on_scene_selected)
        left_layout.addWidget(QLabel("场景列表"))
        left_layout.addWidget(self.scene_list)
        
        # 场景操作按钮
        scene_btn_layout = QVBoxLayout()
        
        # 第一行按钮
        scene_btn_row1 = QHBoxLayout()
        self.add_scene_btn = QPushButton("新建场景")
        self.add_scene_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_scene_btn.clicked.connect(self.add_scene)
        
        self.rename_scene_btn = QPushButton("重命名场景")
        self.rename_scene_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.rename_scene_btn.clicked.connect(self.rename_scene)
        
        scene_btn_row1.addWidget(self.add_scene_btn)
        scene_btn_row1.addWidget(self.rename_scene_btn)
        
        # 第二行按钮
        scene_btn_row2 = QHBoxLayout()
        self.delete_scene_btn = QPushButton("删除场景")
        self.delete_scene_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.delete_scene_btn.clicked.connect(self.delete_scene)
        
        self.copy_scene_btn = QPushButton("复制场景")
        self.copy_scene_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.copy_scene_btn.clicked.connect(self.copy_scene)
        
        scene_btn_row2.addWidget(self.delete_scene_btn)
        scene_btn_row2.addWidget(self.copy_scene_btn)
        
        scene_btn_layout.addLayout(scene_btn_row1)
        scene_btn_layout.addLayout(scene_btn_row2)
        left_layout.addLayout(scene_btn_layout)
        
        layout.addLayout(left_layout)
        
        # 右侧布局：版本管理
        right_layout = QVBoxLayout()
        
        # 版本选择
        version_layout = QHBoxLayout()
        self.version_combo = QComboBox()
        self.version_combo.currentTextChanged.connect(self.on_version_selected)
        version_layout.addWidget(QLabel("版本:"))
        version_layout.addWidget(self.version_combo)
        right_layout.addLayout(version_layout)
        
        # 版本内容编辑
        self.prefix_edit = QTextEdit()
        self.prefix_edit.setPlaceholderText("请输入前缀模板...")
        # 设置自动换行
        self.prefix_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        right_layout.addWidget(QLabel("前缀模板:"))
        right_layout.addWidget(self.prefix_edit)
        
        self.suffix_edit = QTextEdit()
        self.suffix_edit.setPlaceholderText("请输入后缀模板...")
        # 设置自动换行
        self.suffix_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        right_layout.addWidget(QLabel("后缀模板:"))
        right_layout.addWidget(self.suffix_edit)
        
        # 版本操作按钮
        version_btn_layout = QVBoxLayout()
        
        # 版本操作第一行
        version_btn_row1 = QHBoxLayout()
        self.add_version_btn = QPushButton("新建版本")
        self.add_version_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_version_btn.clicked.connect(self.add_version)
        
        self.update_version_btn = QPushButton("保存修改")
        self.update_version_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.update_version_btn.clicked.connect(self.update_version)
        
        version_btn_row1.addWidget(self.add_version_btn)
        version_btn_row1.addWidget(self.update_version_btn)
        
        # 版本操作第二行
        version_btn_row2 = QHBoxLayout()
        self.delete_version_btn = QPushButton("删除版本")
        self.delete_version_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.delete_version_btn.clicked.connect(self.delete_version)
        
        self.copy_version_btn = QPushButton("复制版本")
        self.copy_version_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.copy_version_btn.clicked.connect(self.copy_version)
        
        version_btn_row2.addWidget(self.delete_version_btn)
        version_btn_row2.addWidget(self.copy_version_btn)
        
        version_btn_layout.addLayout(version_btn_row1)
        version_btn_layout.addLayout(version_btn_row2)
        right_layout.addLayout(version_btn_layout)
        
        layout.addLayout(right_layout)
        
        main_layout.addLayout(layout)
        
        # 添加底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        close_btn.clicked.connect(self.accept)
        bottom_layout.addWidget(close_btn)
        
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)
        
        # 初始化数据
        self.load_scenes()
        
    def load_scenes(self):
        """加载场景列表"""
        self.scene_list.clear()
        for scene in self.template_manager.get_scenes():
            self.scene_list.addItem(scene)
            
    def load_versions(self, scene):
        """加载版本列表"""
        self.version_combo.clear()
        versions = self.template_manager.get_scene_versions(scene)
        self.version_combo.addItems(versions)
        
    def on_scene_selected(self, item):
        """场景选择事件"""
        scene = item.text()
        self.load_versions(scene)
        
    def on_version_selected(self, version):
        """版本选择事件"""
        if not version:
            return
            
        scene = self.scene_list.currentItem()
        if not scene:
            return
            
        template = self.template_manager.get_template(scene.text(), version)
        if template:
            self.prefix_edit.setText(template["prefix"])
            self.suffix_edit.setText(template["suffix"])
            
    def add_scene(self):
        """添加场景"""
        scene, ok = QInputDialog.getText(self, "添加场景", "请输入场景名称:")
        if ok and scene:
            if self.template_manager.add_scene(scene):
                self.load_scenes()
            else:
                QMessageBox.warning(self, "错误", "场景已存在")
                
    def delete_scene(self):
        """删除场景"""
        item = self.scene_list.currentItem()
        if not item:
            QMessageBox.warning(self, "错误", "请选择要删除的场景")
            return
            
        if QMessageBox.question(self, "确认", f"确定要删除场景 {item.text()} 吗?") == QMessageBox.Yes:
            if self.template_manager.delete_scene(item.text()):
                self.load_scenes()
                self.version_combo.clear()
                self.prefix_edit.clear()
                self.suffix_edit.clear()
            else:
                QMessageBox.warning(self, "错误", "删除失败")
                
    def rename_scene(self):
        """重命名场景"""
        item = self.scene_list.currentItem()
        if not item:
            QMessageBox.warning(self, "错误", "请选择要重命名的场景")
            return
            
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self, 
            "重命名场景", 
            "请输入新的场景名称:",
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            if self.template_manager.rename_scene(old_name, new_name):
                self.load_scenes()
                # 选中重命名后的场景
                for i in range(self.scene_list.count()):
                    if self.scene_list.item(i).text() == new_name:
                        self.scene_list.setCurrentRow(i)
                        break
                QMessageBox.information(self, "成功", f"场景已重命名为 '{new_name}'")
            else:
                QMessageBox.warning(self, "错误", "场景名称已存在或重命名失败")
                
    def copy_scene(self):
        """复制场景"""
        item = self.scene_list.currentItem()
        if not item:
            QMessageBox.warning(self, "错误", "请选择要复制的场景")
            return
            
        source_name = item.text()
        new_name, ok = QInputDialog.getText(
            self, 
            "复制场景", 
            f"请输入新场景名称（复制自：{source_name}）:",
            text=f"{source_name}_副本"
        )
        
        if ok and new_name:
            # 获取源场景的所有数据
            if source_name in self.template_manager.templates:
                source_data = self.template_manager.templates[source_name].copy()
                
                # 创建新场景
                if self.template_manager.add_scene(new_name):
                    # 复制所有版本数据
                    self.template_manager.templates[new_name] = source_data
                    self.template_manager.save_templates()
                    
                    self.load_scenes()
                    # 选中新创建的场景
                    for i in range(self.scene_list.count()):
                        if self.scene_list.item(i).text() == new_name:
                            self.scene_list.setCurrentRow(i)
                            break
                    QMessageBox.information(self, "成功", f"场景已复制为 '{new_name}'")
                else:
                    QMessageBox.warning(self, "错误", "场景名称已存在")
            else:
                QMessageBox.warning(self, "错误", "源场景不存在")
                
    def add_version(self):
        """添加版本"""
        scene = self.scene_list.currentItem()
        if not scene:
            QMessageBox.warning(self, "错误", "请先选择场景")
            return
            
        version, ok = QInputDialog.getText(self, "添加版本", "请输入版本名称:")
        if ok and version:
            prefix = self.prefix_edit.toPlainText()
            suffix = self.suffix_edit.toPlainText()
            
            if self.template_manager.add_version(scene.text(), version, prefix, suffix):
                self.load_versions(scene.text())
                self.version_combo.setCurrentText(version)
            else:
                QMessageBox.warning(self, "错误", "版本已存在")
                
    def update_version(self):
        """更新版本"""
        scene = self.scene_list.currentItem()
        version = self.version_combo.currentText()
        
        if not scene or not version:
            QMessageBox.warning(self, "错误", "请选择要更新的场景和版本")
            return
            
        prefix = self.prefix_edit.toPlainText()
        suffix = self.suffix_edit.toPlainText()
        
        if self.template_manager.update_version(scene.text(), version, prefix, suffix):
            QMessageBox.information(self, "成功", "更新成功")
        else:
            QMessageBox.warning(self, "错误", "更新失败")
            
    def delete_version(self):
        """删除版本"""
        scene = self.scene_list.currentItem()
        version = self.version_combo.currentText()
        
        if not scene or not version:
            QMessageBox.warning(self, "错误", "请选择要删除的版本")
            return
            
        if QMessageBox.question(self, "确认", f"确定要删除版本 {version} 吗?") == QMessageBox.Yes:
            if self.template_manager.delete_version(scene.text(), version):
                self.load_versions(scene.text())
                self.prefix_edit.clear()
                self.suffix_edit.clear()
            else:
                QMessageBox.warning(self, "错误", "无法删除最后一个版本") 
                
    def copy_version(self):
        """复制版本"""
        scene = self.scene_list.currentItem()
        version = self.version_combo.currentText()
        
        if not scene or not version:
            QMessageBox.warning(self, "错误", "请选择要复制的场景和版本")
            return
            
        new_version, ok = QInputDialog.getText(
            self, 
            "复制版本", 
            f"请输入新版本名称（复制自：{version}）:",
            text=f"{version}_副本"
        )
        
        if ok and new_version:
            # 获取源版本的模板内容
            template = self.template_manager.get_template(scene.text(), version)
            if template:
                prefix = template["prefix"]
                suffix = template["suffix"]
                
                if self.template_manager.add_version(scene.text(), new_version, prefix, suffix):
                    self.load_versions(scene.text())
                    self.version_combo.setCurrentText(new_version)
                    QMessageBox.information(self, "成功", f"版本已复制为 '{new_version}'")
                else:
                    QMessageBox.warning(self, "错误", "版本名称已存在")
            else:
                QMessageBox.warning(self, "错误", "源版本不存在")