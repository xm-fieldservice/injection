# src/utils/config_manager.py
import os
import json

class ConfigManager:
    def __init__(self, app_dir):
        self.app_dir = app_dir
        self.config_dir = os.path.join(app_dir, 'config')
        self.config_path = os.path.join(self.config_dir, 'config.json')
        self.templates_path = os.path.join(self.config_dir, 'templates.json')
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 默认配置
        self.config = {
            'target_window': None,
            'target_position': None,
            'log_file': os.path.join(app_dir, 'logs', 'commands.md')
        }
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
    
    def save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config() 