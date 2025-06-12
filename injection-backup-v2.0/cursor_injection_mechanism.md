# Cursor 命令注入机制分析报告

## 1. 校准机制

校准机制主要由以下几个部分组成：

### 1.1 校准流程

1. **触发校准**：
   - 用户点击界面上的"校准位置"按钮，调用`start_calibration()`方法
   - 主窗口会被隐藏，创建一个新的顶层窗口作为校准提示窗口

2. **捕获点击位置**：
   - 校准窗口绑定鼠标点击事件到`save_cursor_position()`方法
   - 用户点击Cursor输入框位置时，系统会记录鼠标的屏幕坐标

3. **保存配置**：
   - 点击位置被保存到`config/cursor_position.json`文件中
   - 配置包含简单的x和y坐标

4. **状态指示**：
   - 校准按钮的颜色会根据校准状态变化：红色表示未校准，绿色表示已校准

### 1.2 校准数据管理

```python
def save_cursor_position(self, event):
    # 获取鼠标位置（相对于屏幕）
    x = self.calibration_window.winfo_pointerx()
    y = self.calibration_window.winfo_pointery()
    
    # 保存坐标
    with open(self.CONFIG_FILE, 'w') as f:
        json.dump({'x': x, 'y': y}, f)
    
    # 更新注入器的点击位置
    self.command_injector.set_click_position(x, y)
```

- 校准数据存储在`CommandInjector`类的`click_x`和`click_y`属性中
- 程序启动时会从配置文件加载之前保存的校准位置

## 2. 命令注入机制

命令注入机制分为以下几个关键步骤：

### 2.1 注入流程

1. **激活目标窗口**：
   - 通过`_activate_cursor_window()`方法查找并激活Cursor窗口
   - 使用`win32gui`模块枚举窗口，查找标题包含"Cursor"的窗口
   - 使用`SetForegroundWindow`将窗口置于前台

2. **定位输入区域**：
   - 使用`pyautogui`将鼠标移动到之前校准保存的坐标位置
   - 执行鼠标点击操作激活输入区域

3. **清除现有内容**：
   - 使用快捷键`Ctrl+A`选择所有文本
   - 按`Delete`键删除选中内容

4. **输入新命令**：
   - 主要使用剪贴板机制：
     - 先保存原始剪贴板内容
     - 将要注入的命令复制到剪贴板
     - 使用`Ctrl+V`粘贴命令
     - 恢复原始剪贴板内容
   - 最后按`Enter`键发送命令

5. **恢复鼠标位置**：
   - 将鼠标移回原始位置，减少对用户的干扰

### 2.2 关键代码分析

```python
def inject_to_cursor(self, command: str, scene: str) -> bool:
    # 保存当前鼠标位置
    original_x, original_y = pyautogui.position()
    
    # 激活 Cursor 窗口
    if not self._activate_cursor_window():
        return False
    
    # 点击命令输入区域
    pyautogui.moveTo(self.click_x, self.click_y, duration=0.2)
    pyautogui.click()
    
    # 清除现有内容
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('delete')
    
    # 修饰命令（如果在模板模式下）
    decorated_command = self._decorate_command(command, scene)
    
    # 使用剪贴板来输入文本
    original_clipboard = pyperclip.paste()  # 保存原始剪贴板内容
    
    try:
        # 将命令复制到剪贴板
        pyperclip.copy(decorated_command)
        
        # 粘贴命令
        pyautogui.hotkey('ctrl', 'v')
        
        # 发送命令
        pyautogui.press('enter')
        
    finally:
        # 恢复原始剪贴板内容
        pyperclip.copy(original_clipboard)
    
    # 恢复鼠标位置
    pyautogui.moveTo(original_x, original_y)
```

### 2.3 命令修饰机制

在模板模式下，命令会根据选择的场景进行修饰：

```python
def _decorate_command(self, command: str, scene: str) -> str:
    template = self.scene_templates.get(scene)
    if template:
        decorated_command = f"{template['prefix']}\n\n{command}\n\n{template['suffix']}"
        return decorated_command
    return command
```

支持的场景模板包括：
- 代码修改场景
- 截图相关场景
- 上下文记忆场景

## 3. 技术实现细节

### 3.1 使用的关键库

1. **GUI自动化**：
   - `pyautogui`：处理鼠标移动、点击和键盘输入
   - `pyperclip`：处理剪贴板操作

2. **窗口管理**：
   - `win32gui`和`win32con`：查找、激活和管理窗口

3. **用户界面**：
   - `tkinter`：创建应用程序界面和校准窗口

### 3.2 错误处理与重试机制

- 窗口激活过程中有重试机制，最多尝试3次
- 点击操作也有重试机制，确保命令输入区域被正确激活
- 详细的日志记录，便于调试和问题排查

## 4. 总结

Cursor的命令注入系统采用了一种简单但有效的方法：

1. **校准机制**是一次性的操作，记录用户指定的输入位置坐标
2. **注入机制**使用GUI自动化和剪贴板操作，模拟用户输入行为
3. 系统支持两种模式：
   - **模板模式**：根据预定义场景添加前缀和后缀
   - **自由模式**：直接注入原始命令

这种实现方式的优点是通用性强，不依赖于特定应用的API，可以适用于多种文本输入场景。缺点是依赖于屏幕坐标，如果目标窗口移动或改变大小，可能需要重新校准。
