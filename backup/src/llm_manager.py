from typing import List, Dict, Optional
import json
import os

class LLMManager:
    def __init__(self):
        self.models = []
        self.tags = {
            "type": ["免费", "收费"],
            "media": ["视频", "语音", "图片"],
            "custom": []
        }
        self.config_file = "models/llm_config.json"
        self.load_config()
        
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.models = config.get('models', [])
                    self.tags = config.get('tags', self.tags)
            except Exception as e:
                print(f"加载配置失败: {e}")
                
    def save_config(self):
        """保存配置文件"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'models': self.models,
                    'tags': self.tags
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
            
    def add_model(self, model_info: Dict):
        """添加大模型"""
        if not any(m['name'] == model_info['name'] for m in self.models):
            self.models.append(model_info)
            self.save_config()
            return True
        return False
        
    def update_model(self, model_name: str, model_info: Dict):
        """更新大模型信息"""
        for i, model in enumerate(self.models):
            if model['name'] == model_name:
                self.models[i] = model_info
                self.save_config()
                return True
        return False
        
    def delete_model(self, model_name: str):
        """删除大模型"""
        self.models = [m for m in self.models if m['name'] != model_name]
        self.save_config()
        
    def get_model(self, model_name: str) -> Optional[Dict]:
        """获取大模型信息"""
        for model in self.models:
            if model['name'] == model_name:
                return model
        return None
        
    def get_all_models(self) -> List[Dict]:
        """获取所有大模型"""
        return self.models
        
    def add_tag(self, tag_type: str, tag: str):
        """添加标签"""
        if tag_type in self.tags and tag not in self.tags[tag_type]:
            self.tags[tag_type].append(tag)
            self.save_config()
            return True
        return False
        
    def remove_tag(self, tag_type: str, tag: str):
        """删除标签"""
        if tag_type in self.tags and tag in self.tags[tag_type]:
            self.tags[tag_type].remove(tag)
            self.save_config()
            return True
        return False
        
    def get_tags(self, tag_type: str = None) -> Dict:
        """获取标签"""
        if tag_type:
            return self.tags.get(tag_type, [])
        return self.tags 