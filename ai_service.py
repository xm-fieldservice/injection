import requests
import json
import os
from typing import Dict, Optional

class AIService:
    def __init__(self):
        self.api_keys = {}
        self.current_model = None
        self.models = {
            "DeepSeek": {
                "name": "DeepSeek",
                "api_url": "https://api.deepseek.com/v1/chat/completions",
                "model_name": "deepseek-chat",
                "requires_key": True
            },
            "ChatGLM": {
                "name": "ChatGLM",
                "api_url": "http://localhost:8000/v1/chat/completions",
                "model_name": "chatglm3",
                "requires_key": False
            },
            "Claude": {
                "name": "Claude",
                "api_url": "https://api.anthropic.com/v1/messages",
                "model_name": "claude-3-opus-20240229",
                "requires_key": True
            }
        }
        self.history = []
        
    def set_api_key(self, model: str, api_key: str):
        """设置指定模型的API密钥"""
        self.api_keys[model] = api_key
        
    def set_current_model(self, model: str):
        """设置当前使用的模型"""
        if model in self.models:
            self.current_model = model
            return True
        return False
        
    def get_available_models(self):
        """获取可用的模型列表"""
        return list(self.models.keys())
        
    def get_model_info(self, model: str):
        """获取模型信息"""
        return self.models.get(model)
        
    def needs_api_key(self, model: str):
        """检查模型是否需要API密钥"""
        model_info = self.models.get(model)
        return model_info and model_info["requires_key"]
        
    def has_api_key(self, model: str):
        """检查是否已设置API密钥"""
        return model in self.api_keys and bool(self.api_keys[model])
        
    def clear_history(self):
        """清除对话历史"""
        self.history = []
        
    def generate_decorators(self, command: str, scene: str) -> Optional[Dict[str, str]]:
        """生成命令修饰词"""
        try:
            # 构建提示词
            prompt = self._build_prompt(command, scene)
            
            # 调用API
            response = self._call_api(prompt)
            
            # 解析响应
            if response:
                return self._parse_response(response)
                
        except Exception as e:
            print(f"生成修饰词出错: {str(e)}")
        return None
        
    def _build_prompt(self, command: str, scene: str) -> str:
        """构建提示词"""
        prompts = {
            "代码修改场景": {
                "system": "你是一个代码审查助手，负责为代码修改命令添加合适的修饰词。",
                "user": f"请为以下代码修改命令生成前缀和后缀修饰词。命令内容：\n{command}\n\n" +
                       "要求：\n1. 前缀应该包含代码修改的规范和限制\n2. 后缀应该包含验证和确认要求"
            },
            "截图相关场景": {
                "system": "你是一个图像分析助手，负责为截图相关命令添加合适的修饰词。",
                "user": f"请为以下截图分析命令生成前缀和后缀修饰词。命令内容：\n{command}\n\n" +
                       "要求：\n1. 前缀应该强调图像细节的关注点\n2. 后缀应该要求确认理解的准确性"
            },
            "上下文记忆场景": {
                "system": "你是一个上下文管理助手，负责为上下文相关命令添加合适的修饰词。",
                "user": f"请为以下上下文命令生成前缀和后缀修饰词。命令内容：\n{command}\n\n" +
                       "要求：\n1. 前缀应该强调上下文的重要性\n2. 后缀应该确保上下文的连续性"
            }
        }
        
        default_prompt = {
            "system": "你是一个AI助手，负责为命令添加合适的修饰词。",
            "user": f"请为以下命令生成前缀和后缀修饰词。命令内容：\n{command}"
        }
        
        scene_prompt = prompts.get(scene, default_prompt)
        
        messages = [
            {"role": "system", "content": scene_prompt["system"]},
            {"role": "user", "content": scene_prompt["user"]}
        ]
        
        # 添加历史记录
        messages.extend(self.history)
        
        return messages
        
    def _call_api(self, messages: list) -> Optional[Dict]:
        """调用API"""
        if not self.current_model:
            raise ValueError("未选择模型")
            
        model_info = self.models[self.current_model]
        if model_info["requires_key"] and not self.has_api_key(self.current_model):
            raise ValueError(f"{self.current_model} API密钥未设置")
            
        headers = {
            "Content-Type": "application/json"
        }
        
        # 根据不同模型设置不同的认证头
        if self.current_model == "DeepSeek":
            headers["Authorization"] = f"Bearer {self.api_keys[self.current_model]}"
        elif self.current_model == "Claude":
            headers["x-api-key"] = self.api_keys[self.current_model]
            headers["anthropic-version"] = "2023-06-01"
        
        data = {
            "model": model_info["model_name"],
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(model_info["api_url"], headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API调用失败: {response.status_code} - {response.text}")
            return None
            
    def _parse_response(self, response: Dict) -> Dict[str, str]:
        """解析API响应"""
        try:
            content = response["choices"][0]["message"]["content"]
            
            # 尝试解析JSON格式
            try:
                result = json.loads(content)
                if "prefix" in result and "suffix" in result:
                    return result
            except:
                pass
                
            # 尝试解析文本格式
            lines = content.split("\n")
            prefix = ""
            suffix = ""
            
            for line in lines:
                if line.startswith("前缀:") or line.startswith("prefix:"):
                    prefix = line.split(":", 1)[1].strip()
                elif line.startswith("后缀:") or line.startswith("suffix:"):
                    suffix = line.split(":", 1)[1].strip()
                    
            return {
                "prefix": prefix or "[请注意以下内容]",
                "suffix": suffix or "[请确认以上内容]"
            }
            
        except Exception as e:
            print(f"解析响应出错: {str(e)}")
            return {
                "prefix": "[请注意以下内容]",
                "suffix": "[请确认以上内容]"
            }
            
    def add_to_history(self, role: str, content: str):
        """添加对话历史"""
        self.history.append({"role": role, "content": content})
        # 保持历史记录在合理范围内
        if len(self.history) > 10:
            self.history = self.history[-10:] 