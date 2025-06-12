import os
import json
import requests
from typing import Optional, Dict, Any

class AIService:
    def __init__(self):
        self.api_key = None
        self.api_base = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7
        self.max_tokens = 2000
        
        # 加载API密钥
        self._load_api_key()
    
    def _load_api_key(self):
        """从环境变量加载API密钥"""
        self.api_key = os.getenv("OPENAI_API_KEY")
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
    
    def set_model(self, model: str):
        """设置模型"""
        self.model = model
    
    def set_temperature(self, temperature: float):
        """设置温度参数"""
        self.temperature = temperature
    
    def set_max_tokens(self, max_tokens: int):
        """设置最大token数"""
        self.max_tokens = max_tokens
    
    def generate_response(self, prompt: str, template: Optional[Dict[str, Any]] = None) -> str:
        """生成AI响应"""
        if not self.api_key:
            return "错误：未设置API密钥"
        
        try:
            # 准备请求数据
            messages = [{"role": "user", "content": prompt}]
            if template:
                messages.insert(0, {"role": "system", "content": template["content"]})
            
            # 发送请求
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }
            )
            
            # 处理响应
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"错误：API请求失败 ({response.status_code})"
        except Exception as e:
            return f"错误：{str(e)}" 