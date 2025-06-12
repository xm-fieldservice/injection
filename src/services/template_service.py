import os
import json

class TemplateService:
    def __init__(self, templates_path):
        self.templates_path = templates_path
        self.templates = {}
        
        # 确保配置文件存在
        if not os.path.exists(templates_path):
            self._create_default_templates()
        else:
            self.load_templates()
    
    def _create_default_templates(self):
        """创建默认模板配置"""
        self.templates = {
            "default": {
                "name": "默认模板",
                "content": "请按照以下格式回答问题：\n1. 分析问题\n2. 提供解决方案\n3. 总结"
            }
        }
        self.save_templates()
    
    def load_templates(self):
        """加载模板配置"""
        try:
            with open(self.templates_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
        except Exception as e:
            print(f"加载模板失败: {str(e)}")
            self._create_default_templates()
    
    def save_templates(self):
        """保存模板配置"""
        try:
            with open(self.templates_path, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存模板失败: {str(e)}")
    
    def get_template(self, template_id):
        """获取指定模板"""
        return self.templates.get(template_id)
    
    def add_template(self, template_id, name, content):
        """添加新模板"""
        self.templates[template_id] = {
            "name": name,
            "content": content
        }
        self.save_templates()
    
    def update_template(self, template_id, name=None, content=None):
        """更新模板"""
        if template_id in self.templates:
            if name is not None:
                self.templates[template_id]["name"] = name
            if content is not None:
                self.templates[template_id]["content"] = content
            self.save_templates()
    
    def delete_template(self, template_id):
        """删除模板"""
        if template_id in self.templates:
            del self.templates[template_id]
            self.save_templates()
    
    def list_templates(self):
        """获取所有模板"""
        return self.templates 