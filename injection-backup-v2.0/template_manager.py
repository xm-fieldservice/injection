import json
import os
from typing import Dict, List

class TemplateManager:
    def __init__(self):
        self.templates_file = 'templates.json'
        self.templates = self.load_templates()
        
    def load_templates(self) -> Dict:
        """加载模板配置"""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.get_default_templates()
        return self.get_default_templates()
    
    def save_templates(self):
        """保存模板配置"""
        with open(self.templates_file, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)
    
    def get_default_templates(self) -> Dict:
        """获取默认模板"""
        return {
            "代码修改场景": {
                "versions": [
                    {
                        "name": "默认模板",
                        "prefix": "[请严格按照原有代码路径修改，禁止创建新方法或新变量。]",
                        "suffix": "[请确认修改是否在原有代码基础上进行。]"
                    }
                ]
            },
            "截图相关场景": {
                "versions": [
                    {
                        "name": "默认模板",
                        "prefix": "[请仔细查看截图，确保理解准确。]",
                        "suffix": "[请确认截图内容理解是否正确。]"
                    }
                ]
            },
            "上下文记忆场景": {
                "versions": [
                    {
                        "name": "默认模板",
                        "prefix": "[请记住以下上下文信息。]",
                        "suffix": "[请在后续对话中始终保持对这些上下文的记忆。]"
                    }
                ]
            }
        }
    
    def get_scenes(self) -> List[str]:
        """获取所有场景名称"""
        return list(self.templates.keys())
    
    def get_scene_versions(self, scene: str) -> List[str]:
        """获取指定场景的所有版本名称"""
        if scene in self.templates:
            return [v["name"] for v in self.templates[scene]["versions"]]
        return []
    
    def get_template(self, scene: str, version: str = "默认模板") -> Dict:
        """获取指定场景和版本的模板"""
        if scene in self.templates:
            for v in self.templates[scene]["versions"]:
                if v["name"] == version:
                    return v
        return None
    
    def add_scene(self, scene: str) -> bool:
        """添加新场景"""
        if scene not in self.templates:
            self.templates[scene] = {
                "versions": [
                    {
                        "name": "默认模板",
                        "prefix": "",
                        "suffix": ""
                    }
                ]
            }
            self.save_templates()
            return True
        return False
    
    def add_version(self, scene: str, version: str, prefix: str, suffix: str) -> bool:
        """添加新版本"""
        if scene in self.templates:
            # 检查版本名是否已存在
            if version not in [v["name"] for v in self.templates[scene]["versions"]]:
                self.templates[scene]["versions"].append({
                    "name": version,
                    "prefix": prefix,
                    "suffix": suffix
                })
                self.save_templates()
                return True
        return False
    
    def update_version(self, scene: str, version: str, prefix: str, suffix: str) -> bool:
        """更新版本"""
        if scene in self.templates:
            for v in self.templates[scene]["versions"]:
                if v["name"] == version:
                    v["prefix"] = prefix
                    v["suffix"] = suffix
                    self.save_templates()
                    return True
        return False
    
    def delete_scene(self, scene: str) -> bool:
        """删除场景"""
        if scene in self.templates:
            del self.templates[scene]
            self.save_templates()
            return True
        return False
    
    def delete_version(self, scene: str, version: str) -> bool:
        """删除版本"""
        if scene in self.templates:
            versions = self.templates[scene]["versions"]
            for i, v in enumerate(versions):
                if v["name"] == version:
                    # 不允许删除最后一个版本
                    if len(versions) > 1:
                        versions.pop(i)
                        self.save_templates()
                        return True
        return False 
    
    def rename_scene(self, old_name: str, new_name: str) -> bool:
        """重命名场景"""
        if old_name in self.templates and new_name not in self.templates:
            # 复制旧场景的数据到新名称
            self.templates[new_name] = self.templates[old_name]
            # 删除旧场景
            del self.templates[old_name]
            self.save_templates()
            return True
        return False