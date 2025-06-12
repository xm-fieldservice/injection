import sys
import os
from PyQt5.QtWidgets import QApplication

# 添加项目根目录到Python路径
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from src.ui.main_window import MainWindow
from src.utils.config_manager import ConfigManager
from src.utils.logger import Logger
# from src.services.injection_service import InjectionService  # 已删除，使用main.py中的统一实现
from src.services.template_service import TemplateService
from src.services.ai_service import AIService

def main():
    app = QApplication(sys.argv)
    
    # 初始化配置管理器
    config_manager = ConfigManager(app_dir)
    
    # 初始化日志管理器
    logger = Logger(config_manager.get('log_file'))
    
    # 初始化服务
    template_service = TemplateService(os.path.join(app_dir, 'config', 'templates.json'))
    ai_service = AIService()
    
    # 创建主窗口（不再需要injection_service，统一使用main.py中的实现）
    window = MainWindow(config_manager, template_service, ai_service)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()