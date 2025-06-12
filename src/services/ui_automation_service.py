"""
UI Automation服务模块 - 用于自动化UI交互和获取文本内容
"""

import uiautomation as auto
import time
import win32gui
import win32api
import win32con

# 获取正确的控件类型常量
# uiautomation使用数字来表示控件类型
TEXT_CONTROL_TYPES = [
    50032,  # EditControl
    50030,  # DocumentControl
    50020,  # TextControl
    50008,  # ListControl
    50007,  # ListItemControl
    50025   # CustomControl
]

class UIAutomationService:
    """UI自动化服务，提供UI元素识别和文本获取功能"""
    
    def __init__(self):
        """初始化UI自动化服务"""
        self.output_window_info = {}
        self.output_element_info = {}
        self.output_element_path = []
    
    def calibrate_output_area(self):
        """校准输出区域，识别用户点击的UI元素"""
        try:
            # 等待用户点击
            time.sleep(1)
            
            # 获取鼠标位置
            x, y = win32api.GetCursorPos()
            
            # 获取鼠标位置下的窗口
            hwnd = win32gui.WindowFromPoint((x, y))
            
            # 获取窗口下的UI元素
            element = auto.ControlFromHandle(hwnd)
            
            if element:
                # 保存元素的识别信息
                self.output_element_info = {
                    'control_type': element.ControlType,
                    'class_name': element.ClassName,
                    'name': element.Name,
                    'automation_id': element.AutomationId
                }
                
                # 尝试获取元素路径
                path = []
                parent = element
                while parent and parent.ControlType != 50032:  # WindowControl
                    siblings = parent.GetParentControl().GetChildren()
                    index = -1
                    for i, sibling in enumerate(siblings):
                        if sibling == parent:
                            index = i
                            break
                    path.insert(0, (parent.ControlType, index))
                    parent = parent.GetParentControl()
                    
                self.output_element_path = path
                
                # 保存窗口信息
                window = element.GetTopLevelControl()
                self.output_window_info = {
                    'title': window.Name,
                    'class_name': window.ClassName,
                    'handle': window.Handle
                }
                
                return True, {
                    'window_title': window.Name,
                    'element_name': element.Name or element.ControlTypeName,
                    'element_type': element.ControlTypeName
                }
            else:
                return False, "未能识别UI元素，请重试"
        except Exception as e:
            return False, f"校准过程出错: {str(e)}"
    
    def get_output_text(self):
        """获取已校准的输出区域文本"""
        try:
            # 首先尝试通过窗口信息找到窗口
            window = None
            if self.output_window_info.get('handle'):
                try:
                    window = auto.ControlFromHandle(self.output_window_info['handle'])
                except:
                    pass
            
            if not window or not window.Exists():
                # 如果句柄无效，尝试通过标题和类名查找
                window = auto.WindowControl(
                    Name=self.output_window_info.get('title'),
                    ClassName=self.output_window_info.get('class_name')
                )
            
            if not window.Exists():
                return False, "找不到目标窗口"
            
            # 尝试多种方法定位元素
            element = None
            
            # 方法1: 通过路径定位
            if self.output_element_path and not element:
                try:
                    current = window
                    for control_type, index in self.output_element_path:
                        children = current.GetChildren()
                        if 0 <= index < len(children):
                            current = children[index]
                        else:
                            break
                    if current and current != window:
                        element = current
                except:
                    pass
            
            # 方法2: 通过控件类型和属性定位
            if not element:
                element_info = self.output_element_info
                element = window.Control(
                    ControlType=element_info.get('control_type'),
                    ClassName=element_info.get('class_name'),
                    AutomationId=element_info.get('automation_id'),
                    Name=element_info.get('name')
                )
            
            # 方法3: 搜索所有文本控件
            if not element or not element.Exists():
                # 查找所有可能的文本控件
                text_elements = window.FindAllControls(
                    lambda c: c.ControlType in TEXT_CONTROL_TYPES
                )
                
                # 选择最大的那个（假设输出区域通常较大）
                if text_elements:
                    element = max(text_elements, key=lambda e: e.BoundingRectangle.width() * e.BoundingRectangle.height())
            
            if element and element.Exists():
                # 尝试获取文本
                text = ""
                
                # 尝试获取文本
                if element.ControlType == 50032:  # EditControl
                    if element.GetValuePattern():
                        text = element.GetValuePattern().Value
                elif element.ControlType == 50030:  # DocumentControl
                    if element.GetTextPattern():
                        text = element.GetTextPattern().DocumentRange.GetText(-1)
                elif element.ControlType == 50008:  # ListControl
                    items = element.GetChildren()
                    text = "\n".join([item.Name for item in items if item.Name])
                
                # 如果上述方法都失败，尝试通用方法
                if not text:
                    text = element.Name
                
                if not text:
                    # 最后尝试通过模拟复制粘贴获取
                    try:
                        # 激活窗口
                        window.SetFocus()
                        time.sleep(0.3)
                        
                        # 点击元素
                        element.Click()
                        time.sleep(0.2)
                        
                        # 全选
                        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                        win32api.keybd_event(ord('A'), 0, 0, 0)
                        time.sleep(0.2)
                        win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
                        
                        # 复制
                        win32api.keybd_event(ord('C'), 0, 0, 0)
                        time.sleep(0.2)
                        win32api.keybd_event(ord('C'), 0, win32con.KEYEVENTF_KEYUP, 0)
                        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                        
                        # 获取剪贴板内容
                        import pyperclip
                        text = pyperclip.paste()
                    except:
                        pass
                
                if text:
                    return True, text
                else:
                    return False, "无法获取文本内容"
            
            return False, "未找到输出区域元素"
            
        except Exception as e:
            return False, f"获取输出区域文本失败: {str(e)}"
    
    def find_element_with_adaptive_strategy(self, window):
        """使用自适应策略查找元素"""
        # 策略1: 精确匹配
        element = self.find_element_exact(window)
        if element and element.Exists():
            return element
        
        # 策略2: 部分属性匹配
        element = self.find_element_partial(window)
        if element and element.Exists():
            return element
        
        # 策略3: 基于位置的匹配
        element = self.find_element_by_position(window)
        if element and element.Exists():
            return element
        
        # 策略4: 特定应用规则
        app_name = window.Name.lower()
        if "chrome" in app_name or "edge" in app_name:
            # 浏览器特定规则
            return self.find_browser_content_element(window)
        elif "notepad" in app_name:
            # 记事本特定规则
            return window.EditControl()
        
        # 策略5: 启发式搜索
        return self.find_element_heuristic(window)
    
    def find_element_exact(self, window):
        """精确匹配元素"""
        if not self.output_element_info:
            return None
            
        return window.Control(
            ControlType=self.output_element_info.get('control_type'),
            ClassName=self.output_element_info.get('class_name'),
            AutomationId=self.output_element_info.get('automation_id'),
            Name=self.output_element_info.get('name')
        )
    
    def find_element_partial(self, window):
        """部分属性匹配元素"""
        if not self.output_element_info:
            return None
            
        # 只使用控件类型和类名
        return window.Control(
            ControlType=self.output_element_info.get('control_type'),
            ClassName=self.output_element_info.get('class_name')
        )
    
    def find_element_by_position(self, window):
        """通过位置查找元素"""
        if not self.output_element_path:
            return None
            
        try:
            current = window
            for control_type, index in self.output_element_path:
                children = current.GetChildren()
                if 0 <= index < len(children):
                    current = children[index]
                else:
                    return None
            return current if current != window else None
        except:
            return None
    
    def find_browser_content_element(self, window):
        """查找浏览器内容元素"""
        # 尝试查找Chrome/Edge的内容区域
        try:
            # 查找所有可能的文本控件
            text_elements = window.FindAllControls(
                lambda c: c.ControlType in TEXT_CONTROL_TYPES
            )
            
            # 选择最大的那个（假设输出区域通常较大）
            if text_elements:
                return max(text_elements, key=lambda e: e.BoundingRectangle.width() * e.BoundingRectangle.height())
        except:
            pass
        return None
    
    def find_element_heuristic(self, window):
        """启发式搜索元素"""
        # 查找所有可能的文本控件
        text_elements = window.FindAllControls(
            lambda c: c.ControlType in TEXT_CONTROL_TYPES
        )
        
        # 选择最大的那个（假设输出区域通常较大）
        if text_elements:
            return max(text_elements, key=lambda e: e.BoundingRectangle.width() * e.BoundingRectangle.height())
        return None
    
    def load_config(self, config):
        """从配置加载输出区域信息"""
        self.output_window_info = config.get('output_window_info', {})
        self.output_element_info = config.get('output_element_info', {})
        self.output_element_path = config.get('output_element_path', [])
    
    def save_config(self):
        """保存输出区域信息到配置"""
        return {
            'output_window_info': self.output_window_info,
            'output_element_info': self.output_element_info,
            'output_element_path': self.output_element_path
        }
