import os
import json

class TemplateManager:
    def __init__(self, templates_file=None):
        self.templates_file = templates_file or os.path.join(os.path.dirname(__file__), '../../config/templates.json')
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """加载模板数据"""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载模板失败: {str(e)}")
        return {}
    
    def _save_templates(self):
        """保存模板数据"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.templates_file), exist_ok=True)
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存模板失败: {str(e)}")
            return False
    
    def get_scenes(self):
        """获取所有场景"""
        return list(self.templates.keys())
    
    def get_scene_versions(self, scene):
        """获取指定场景的所有版本"""
        if scene in self.templates:
            return list(self.templates[scene].keys())
        return []
    
    def get_template(self, scene, version):
        """获取指定场景和版本的模板"""
        if scene in self.templates and version in self.templates[scene]:
            return self.templates[scene][version]
        return None
    
    def save_template(self, scene, version, prefix, suffix):
        """保存模板"""
        if scene not in self.templates:
            self.templates[scene] = {}
        
        self.templates[scene][version] = {
            'prefix': prefix,
            'suffix': suffix
        }
        
        return self._save_templates()
    
    def import_templates(self, file_path):
        """从文件导入模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            self.templates.update(templates)
            return self._save_templates()
        except Exception as e:
            raise Exception(f"导入模板失败: {str(e)}")
    
    def export_templates(self, file_path):
        """导出模板到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            raise Exception(f"导出模板失败: {str(e)}")
    
    def delete_template(self, scene, version):
        """删除指定模板"""
        if scene in self.templates and version in self.templates[scene]:
            del self.templates[scene][version]
            if not self.templates[scene]:  # 如果场景没有版本了，删除场景
                del self.templates[scene]
            return self._save_templates()
        return False 