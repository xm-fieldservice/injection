# 提示词注入工具 - 项目架构统一计划

*文档创建日期：2025-04-15*

## 目录

1. [当前项目状况分析](#当前项目状况分析)
2. [架构统一目标](#架构统一目标)
3. [建议的项目架构](#建议的项目架构)
4. [重构步骤](#重构步骤)
5. [核心模块设计](#核心模块设计)
6. [迁移策略](#迁移策略)
7. [预期收益](#预期收益)

## 当前项目状况分析

### 已发现问题

1. **代码组织混乱**：
   - 主要功能集中在单一的 `main.py` 文件中
   - 辅助模块分散在多个文件中
   - 备份目录中存在另一套架构

2. **文件重名问题**：
   - `icon.png` 在根目录和 `resources` 目录下都存在
   - `start.bat` 和 `启动提示词注入工具.bat` 功能重复

3. **配置和日志管理不统一**：
   - 配置文件位于根目录
   - 日志文件分散在根目录和 `logs` 目录

4. **代码重复**：
   - 根目录下的 `main.py` 和 `src` 目录下的代码结构重复
   - 多个启动脚本包含重复功能

5. **废弃代码和未使用的代码**：
   - `icon.py` 文件未被主程序使用
   - 备份目录中存在大量未使用的代码

### 当前项目结构

当前项目结构混乱，包含多个重复文件和未使用的代码。主要功能集中在单一的 `main.py` 文件中，导致代码难以维护和扩展。

## 架构统一目标

1. **提高代码可维护性**：将代码拆分为逻辑清晰的模块
2. **消除代码重复**：统一功能实现，避免多个实现方式
3. **统一资源管理**：所有资源文件放在统一的目录中
4. **统一配置管理**：集中管理所有配置文件
5. **统一日志管理**：使用统一的日志记录机制
6. **清理未使用的代码**：移除所有废弃和未使用的代码

## 建议的项目架构

```
injection/
├── src/                    # 源代码目录
│   ├── __init__.py         # 包初始化文件
│   ├── main.py             # 入口点，只包含应用启动逻辑
│   ├── ui/                 # UI相关模块
│   │   ├── __init__.py
│   │   ├── main_window.py  # 主窗口类
│   │   ├── dialogs/        # 对话框组件
│   │   │   ├── __init__.py
│   │   │   ├── api_key_dialog.py
│   │   │   └── template_dialog.py
│   │   └── widgets/        # 自定义控件
│   │       └── __init__.py
│   ├── services/           # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── ai_service.py   # AI服务
│   │   ├── injection_service.py  # 注入服务
│   │   └── template_service.py   # 模板服务
│   └── utils/              # 工具类
│       ├── __init__.py
│       ├── config_manager.py  # 配置管理
│       └── logger.py       # 日志管理
├── resources/              # 资源文件
│   └── icon.png            # 应用图标
├── logs/                   # 日志目录
├── config/                 # 配置目录
│   ├── config.json         # 主配置文件
│   └── templates.json      # 模板配置
├── requirements.txt        # 依赖管理
├── README.md               # 项目说明
└── start.bat               # 启动脚本
```

## 重构步骤

### 1. 创建目录结构

- 创建 `src` 目录及其子目录
- 创建 `config` 目录统一存放配置文件
- 确保 `resources` 和 `logs` 目录存在

### 2. 拆分 main.py 文件

- 将 `MainWindow` 类移至 `src/ui/main_window.py`
- 将注入功能移至 `src/services/injection_service.py`
- 将配置管理功能移至 `src/utils/config_manager.py`
- 将日志功能移至 `src/utils/logger.py`

### 3. 统一资源文件

- 将所有资源文件移至 `resources` 目录
- 删除重复的资源文件

### 4. 统一配置管理

- 将所有配置文件移至 `config` 目录
- 创建统一的配置管理类

### 5. 统一日志管理

- 创建统一的日志管理类
- 确保所有日志都保存到 `logs` 目录

### 6. 创建新的入口点

- 创建简洁的 `src/main.py` 作为应用入口点
- 更新启动脚本指向新的入口点

## 核心模块设计

### 配置管理类

```python
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
```

### 日志管理类

```python
# src/utils/logger.py
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
```

### 注入服务类

```python
# src/services/injection_service.py
import win32gui
import win32con
import win32api
import win32clipboard
import time

class InjectionService:
    def __init__(self, logger):
        self.logger = logger
    
    def inject_command(self, command, target_window, target_position):
        try:
            # 激活目标窗口
            hwnd = win32gui.FindWindow(None, target_window)
            if hwnd == 0:
                return False, "找不到目标窗口"
            
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            
            # 移动鼠标到目标位置
            x, y = target_position
            win32api.SetCursorPos((x, y))
            time.sleep(0.1)
            
            # 点击目标位置
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.1)
            
            # 将命令复制到剪贴板
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(command)
            win32clipboard.CloseClipboard()
            
            # 模拟Ctrl+V粘贴
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
            win32api.keybd_event(ord('V'), 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 模拟回车键
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            # 记录命令到日志
            self.logger.log_command(command)
            
            return True, "命令已注入"
        except Exception as e:
            return False, f"注入命令失败: {str(e)}"
```

### 主窗口类（部分示例）

```python
# src/ui/main_window.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
# 其他导入...

class MainWindow(QMainWindow):
    def __init__(self, config_manager, injection_service, template_service, ai_service):
        super().__init__()
        self.config_manager = config_manager
        self.injection_service = injection_service
        self.template_service = template_service
        self.ai_service = ai_service
        
        # 从配置管理器获取配置
        self.target_window = self.config_manager.get('target_window')
        self.target_position = self.config_manager.get('target_position')
        
        self.initUI()
        self.setupTrayIcon()
        self.setupShortcut()
    
    # 其他方法...
```

### 应用入口点

```python
# src/main.py
import sys
import os
from PyQt5.QtWidgets import QApplication

# 添加项目根目录到Python路径
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_dir)

from src.ui.main_window import MainWindow
from src.utils.config_manager import ConfigManager
from src.utils.logger import Logger
from src.services.injection_service import InjectionService
from src.services.template_service import TemplateService
from src.services.ai_service import AIService

def main():
    app = QApplication(sys.argv)
    
    # 初始化配置管理器
    config_manager = ConfigManager(app_dir)
    
    # 初始化日志管理器
    logger = Logger(config_manager.get('log_file'))
    
    # 初始化服务
    injection_service = InjectionService(logger)
    template_service = TemplateService(os.path.join(app_dir, 'config', 'templates.json'))
    ai_service = AIService()
    
    # 创建主窗口
    window = MainWindow(config_manager, injection_service, template_service, ai_service)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
```

## 迁移策略

为了确保平稳过渡，建议采用以下迁移策略：

1. **备份当前代码**：
   - 将当前工作代码完整备份

2. **增量实现**：
   - 首先创建目录结构
   - 逐步移动和重构代码，每次只处理一个模块
   - 每完成一个模块就进行测试

3. **保持兼容性**：
   - 在迁移期间保留原有的入口点
   - 使用导入重定向确保旧代码仍能工作

4. **完整测试**：
   - 完成所有模块迁移后进行全面测试
   - 确保所有功能正常工作

5. **切换入口点**：
   - 确认新架构稳定后，更新启动脚本
   - 移除旧的入口点

## 预期收益

1. **提高代码可维护性**：
   - 模块化设计使代码更易于理解和维护
   - 每个模块有明确的职责，降低耦合度

2. **提高代码可扩展性**：
   - 新功能可以作为独立模块添加
   - 现有功能可以更容易地修改或替换

3. **提高代码质量**：
   - 消除代码重复
   - 统一错误处理和日志记录

4. **提高开发效率**：
   - 清晰的项目结构使开发者更容易理解和修改代码
   - 模块化设计支持多人同时开发不同模块

5. **提高用户体验**：
   - 更稳定的应用程序
   - 更一致的配置和日志管理
