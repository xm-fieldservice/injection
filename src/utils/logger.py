import os
import datetime

class Logger:
    def __init__(self, log_file):
        self.log_file = log_file
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
    
    def log_command(self, command):
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n# {timestamp}\n\n{command}\n")
            return True
        except Exception as e:
            print(f"记录命令失败: {str(e)}")
            return False
    
    def log_note(self, note):
        return self.log_command(note)  # 使用相同的格式记录笔记 