import re
import datetime
from PyQt5.QtCore import QObject, pyqtSignal
import pyperclip

class CursorOutputProcessor(QObject):
    """处理从Cursor捕获的输出内容"""
    
    # 定义信号
    status_update = pyqtSignal(str)  # 状态更新信号
    text_processed = pyqtSignal(str, str)  # 处理完成的文本信号 (内容, 类型)
    
    def __init__(self, parent=None):
        """初始化处理器"""
        super().__init__(parent)
        self.last_processed = None
        
    def process_output(self, text):
        """处理捕获的输出文本"""
        if not text or text.strip() == "":
            self.status_update.emit("捕获内容为空，跳过处理")
            return
            
        self.status_update.emit(f"开始处理捕获内容 ({len(text)} 字符)")
        
        # 提取代码块
        code_blocks = self._extract_code_blocks(text)
        
        # 处理提取到的代码块
        if code_blocks:
            self.status_update.emit(f"提取到 {len(code_blocks)} 个代码块")
            for i, (lang, code) in enumerate(code_blocks):
                # 发送处理后的代码块
                block_info = f"代码块 {i+1}/{len(code_blocks)} ({lang})" if lang else f"代码块 {i+1}/{len(code_blocks)}"
                self.text_processed.emit(code, f"code_{lang}" if lang else "code")
                self.status_update.emit(f"已处理 {block_info}")
        
        # 处理纯文本（移除代码块后的文本）
        text_only = self._extract_text_only(text, code_blocks)
        if text_only and text_only.strip():
            self.status_update.emit("处理纯文本内容")
            self.text_processed.emit(text_only, "text")
        
        # 标记为已处理
        self.last_processed = datetime.datetime.now()
        self.status_update.emit("内容处理完成")
    
    def _extract_code_blocks(self, text):
        """
        从文本中提取代码块
        返回: [(language, code), ...]
        """
        # 匹配 ```language\ncode\n``` 格式的代码块
        pattern = r'```([\w\+\-\.]*)\n([\s\S]*?)\n```'
        matches = re.findall(pattern, text)
        
        # 如果没有匹配到带语言的代码块，尝试匹配不带语言标识的代码块
        if not matches:
            pattern = r'```\n([\s\S]*?)\n```'
            simple_matches = re.findall(pattern, text)
            matches = [(None, code) for code in simple_matches]
            
        # 尝试匹配没有换行的情况
        if not matches:
            pattern = r'```([\w\+\-\.]*)([\s\S]*?)```'
            special_matches = re.findall(pattern, text)
            matches = [(lang, code.strip()) for lang, code in special_matches if code.strip()]
            
        return matches
        
    def _extract_text_only(self, text, code_blocks):
        """
        从原始文本中提取纯文本部分（移除代码块）
        """
        result = text
        
        # 移除所有代码块
        for lang, code in code_blocks:
            if lang:
                result = result.replace(f"```{lang}\n{code}\n```", "")
            else:
                result = result.replace(f"```\n{code}\n```", "")
                # 尝试移除没有换行的情况
                result = result.replace(f"```{code}```", "")
        
        # 清理多余换行符并标准化空白
        result = re.sub(r'\n{3,}', '\n\n', result)
        result = result.strip()
        
        return result
        
    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        try:
            pyperclip.copy(text)
            self.status_update.emit("已复制到剪贴板")
            return True
        except Exception as e:
            self.status_update.emit(f"复制到剪贴板失败: {str(e)}")
            return False 