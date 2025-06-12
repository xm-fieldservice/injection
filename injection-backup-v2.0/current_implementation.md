# 当前命令注入实现

## 1. 核心类结构

```python
class CommandInjector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True
        self.click_x = None
        self.click_y = None
        
        # 场景命令模板
        self.scene_templates = {
            "代码修改场景": {
                "prefix": "[请严格按照原有代码路径修改，禁止创建新方法或新变量。]",
                "suffix": "[请确认修改是否在原有代码基础上进行。]"
            },
            "截图相关场景": {
                "prefix": "[请仔细查看截图，确保理解准确。]",
                "suffix": "[请确认截图内容理解是否正确。]"
            },
            "上下文记忆场景": {
                "prefix": "[请记住以下上下文信息。]",
                "suffix": "[请在后续对话中始终保持对这些上下文的记忆。]"
            }
        }
```

## 2. 主要方法

### 2.1 校准相关
```python
def is_calibrated(self) -> bool:
    """检查是否已经校准"""
    return self.click_x is not None and self.click_y is not None

def set_click_position(self, x: int, y: int):
    """设置点击位置"""
    self.click_x = x
    self.click_y = y
```

### 2.2 命令修饰
```python
def _decorate_command(self, command: str, scene: str) -> str:
    """根据场景修饰命令"""
    template = self.scene_templates.get(scene)
    if template:
        decorated_command = f"{template['prefix']}\n\n{command}\n\n{template['suffix']}"
        return decorated_command
    return command
```

### 2.3 命令注入
```python
def inject_to_cursor(self, command: str, scene: str) -> bool:
    """将命令注入到 Cursor 编辑器"""
    try:
        if not self.is_calibrated():
            self.logger.error("未设置点击位置，请先校准")
            return False
            
        # 保存当前鼠标位置
        original_x, original_y = pyautogui.position()
        
        # 激活 Cursor 窗口
        if not self._activate_cursor_window():
            return False
        
        # 点击命令输入区域
        if not self._click_at_position(self.click_x, self.click_y):
            return False
        
        # 清除现有内容
        self._clear_input_area()
        
        # 修饰并输入命令
        decorated_command = self._decorate_command(command, scene)
        
        # 使用剪贴板输入
        original_clipboard = pyperclip.paste()
        try:
            pyperclip.copy(decorated_command)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')
        finally:
            pyperclip.copy(original_clipboard)
        
        # 恢复鼠标位置
        pyautogui.moveTo(original_x, original_y)
        return True
    except Exception as e:
        self.logger.error(f"命令注入失败: {e}")
        return False
```

### 2.4 窗口激活
```python
def _activate_cursor_window(self) -> bool:
    """激活 Cursor 窗口"""
    try:
        # 查找 Cursor 窗口
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if 'Cursor' in title:
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if not windows:
            return False
        
        # 激活窗口
        hwnd = windows[0]
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception as e:
        self.logger.error(f"激活 Cursor 窗口失败: {e}")
        return False
```

## 3. 存在的问题

1. **窗口激活不稳定**：
   - 窗口查找可能不准确
   - 激活后没有验证是否真正激活
   - 没有处理窗口最小化的情况

2. **点击位置不准确**：
   - 点击后没有验证是否成功
   - 没有处理点击位置偏移的情况

3. **剪贴板操作不可靠**：
   - 没有验证剪贴板内容是否正确
   - 没有处理剪贴板操作失败的情况

4. **命令发送不稳定**：
   - 没有验证命令是否成功发送
   - 没有处理发送失败的情况

5. **错误处理不完善**：
   - 异常捕获后缺乏恢复机制
   - 日志记录不够详细

## 4. 改进建议

1. **窗口激活改进**：
   - 添加窗口激活状态检测
   - 实现窗口焦点验证
   - 添加窗口最小化处理

2. **点击位置改进**：
   - 添加点击位置验证
   - 实现点击位置校准
   - 添加点击重试机制

3. **剪贴板操作改进**：
   - 添加剪贴板内容验证
   - 实现剪贴板操作重试
   - 添加剪贴板状态检测

4. **命令发送改进**：
   - 添加命令发送验证
   - 实现发送重试机制
   - 添加发送状态检测

5. **错误处理改进**：
   - 完善异常处理机制
   - 添加详细日志记录
   - 实现自动恢复机制 