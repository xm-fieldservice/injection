import sys
import os
from PyQt5.QtWidgets import QApplication
from src.main_window import MainWindow

if __name__ == '__main__':
    # 添加项目根目录到Python路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 