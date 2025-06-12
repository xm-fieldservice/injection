from typing import Dict, Optional
import json
import os

class LLMDetail:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.config = {
            "basic": {
                "name": model_name,
                "api_key": "",
                "base_url": "",
                "tags": []
            },
            "params": {
                "prompt_template": "",
                "temperature": 0.7,
                "max_tokens": 2000,
                "enable_web_search": False,
                "enable_deep_thought": False,
                "support_attachments": False,
                "custom_params": {}
            }
        }
        self.config_file = f"models/{model_name}.json"
        self.load_config()
        
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
                
    def save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
            
    def update_basic_info(self, info: Dict):
        """更新基本信息"""
        self.config["basic"].update(info)
        self.save_config()
        
    def update_params(self, params: Dict):
        """更新参数配置"""
        self.config["params"].update(params)
        self.save_config()
        
    def get_basic_info(self) -> Dict:
        """获取基本信息"""
        return self.config["basic"]
        
    def get_params(self) -> Dict:
        """获取参数配置"""
        return self.config["params"]
        
    def set_prompt_template(self, template: str):
        """设置提示词模板"""
        self.config["params"]["prompt_template"] = template
        self.save_config()
        
    def set_model_params(self, temperature: float, max_tokens: int):
        """设置模型参数"""
        self.config["params"]["temperature"] = temperature
        self.config["params"]["max_tokens"] = max_tokens
        self.save_config()
        
    def enable_feature(self, feature: str, enable: bool):
        """启用/禁用功能"""
        if feature in self.config["params"]:
            self.config["params"][feature] = enable
            self.save_config()
            
    def add_custom_param(self, key: str, value: any):
        """添加自定义参数"""
        self.config["params"]["custom_params"][key] = value
        self.save_config()
        
    def remove_custom_param(self, key: str):
        """删除自定义参数"""
        if key in self.config["params"]["custom_params"]:
            del self.config["params"]["custom_params"][key]
            self.save_config() 