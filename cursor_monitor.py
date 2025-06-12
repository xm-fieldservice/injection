import time
import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from cursor_capture import CursorAIOutputExtractor

class CursorMonitor(QThread):
    """Cursor监控线程，用于定期检查和捕获Cursor中的AI输出"""
    
    # 定义信号
    status_update = pyqtSignal(str)  # 状态更新信号
    text_captured = pyqtSignal(str)  # 捕获到文本的信号
    
    def __init__(self, interval=3.0, parent=None):
        """
        初始化监控线程
        
        参数:
        - interval: 监控间隔，单位秒
        - parent: 父对象
        """
        super().__init__(parent)
        self.interval = interval
        self.running = False
        self.extractor = CursorAIOutputExtractor()
        
        # 连接提取器的信号
        self.extractor.status_update.connect(self.relay_status)
        self.extractor.text_extracted.connect(self.handle_text_extracted)
        
        # 已提取文本的哈希，用于检测变化
        self.last_text_hash = None
        self.last_capture_time = None
    
    def relay_status(self, status):
        """转发状态信息"""
        self.status_update.emit(status)
    
    def handle_text_extracted(self, text):
        """处理提取到的文本"""
        # 计算文本哈希
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # 检查是否是新内容
        if text_hash != self.last_text_hash:
            self.last_text_hash = text_hash
            self.last_capture_time = datetime.datetime.now()
            
            # 发送捕获到的文本
            self.text_captured.emit(text)
            self.status_update.emit(f"捕获到新内容 ({len(text)} 字符)")
    
    def start_monitoring(self):
        """开始监控"""
        self.running = True
        self.start()
        self.status_update.emit("Cursor监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        self.status_update.emit("Cursor监控已停止")
        
    def run(self):
        """线程运行函数"""
        self.status_update.emit("Cursor监控线程开始运行")
        
        while self.running:
            try:
                # 提取Cursor输出
                self.extractor.run()
                
                # 等待指定的时间间隔
                for _ in range(int(self.interval * 2)):
                    if not self.running:
                        break
                    time.sleep(0.5)
                    
            except Exception as e:
                self.status_update.emit(f"监控出错: {str(e)}")
                time.sleep(2)  # 出错后等待2秒再继续
        
        self.status_update.emit("Cursor监控线程已结束") 