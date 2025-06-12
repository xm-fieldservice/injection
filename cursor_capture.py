import pyautogui
import pygetwindow as gw
import pytesseract
import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import time
import re
import pyperclip
from PyQt5.QtCore import QObject, pyqtSignal

class CursorAIOutputExtractor(QObject):
    """Cursor AI输出提取器，用于自动捕获Cursor编辑器中AI生成的内容"""
    
    # 定义信号，用于通知提取到的文本
    text_extracted = pyqtSignal(str)
    status_update = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.cursor_window = None
        self.output_region = None
        
        # 尝试初始化Tesseract路径
        self.tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        try:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        except Exception as e:
            print(f"Tesseract初始化失败: {str(e)}")
    
    def find_cursor_window(self):
        """找到Cursor应用窗口"""
        # 搜索可能的Cursor窗口标题
        cursor_windows = []
        
        # 查找标题中包含"Cursor"的窗口
        for win in gw.getAllWindows():
            if "Cursor" in win.title:
                cursor_windows.append(win)
        
        # 如果没有找到，尝试通过窗口类等方式查找
        if not cursor_windows:
            # 使用枚举窗口方式查找可能的窗口
            def enum_windows_callback(hwnd, result):
                title = win32gui.GetWindowText(hwnd)
                if "Cursor" in title:
                    try:
                        win = gw.Window(hwnd)
                        result.append(win)
                    except:
                        pass
                return True
            
            result = []
            win32gui.EnumWindows(enum_windows_callback, result)
            cursor_windows = result
            
        if not cursor_windows:
            self.status_update.emit("未找到Cursor窗口")
            return False
            
        # 选择最大的窗口作为Cursor主窗口
        self.cursor_window = max(cursor_windows, key=lambda w: w.width * w.height)
        self.status_update.emit(f"找到Cursor窗口: {self.cursor_window.title}")
        return True
    
    def identify_output_region(self):
        """识别AI输出区域的特征"""
        if not self.cursor_window:
            return False
            
        # 截图整个Cursor窗口
        screenshot = self.capture_window(self.cursor_window)
        
        # 识别特征：寻找可能的聊天区域特征
        # 1. 寻找代码块 (通常有深色背景和语法高亮)
        # 2. 查找固定UI元素如"Copy"按钮
        # 3. 寻找聊天气泡或文本区域分隔线
        
        # 方法1: 寻找代码块特征
        code_blocks = self.find_code_blocks(screenshot)
        
        # 方法2: 寻找聊天界面分隔线 (通常是垂直线)
        separators = self.find_separator_lines(screenshot)
        
        # 方法3: 查找固定元素如"Copy"按钮
        ui_elements = self.find_ui_elements(screenshot, ["Copy", "AI", "Chat"])
        
        # 综合以上特征确定输出区域
        self.output_region = self.determine_output_region(code_blocks, separators, ui_elements)
        
        if self.output_region:
            self.status_update.emit(f"识别到输出区域")
            return True
        return False
    
    def capture_window(self, window):
        """截取指定窗口的图像"""
        left, top, right, bottom = window.left, window.top, window.left + window.width, window.top + window.height
        
        # 创建设备上下文
        hwnd = win32gui.FindWindow(None, window.title)
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, window.width, window.height)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (window.width, window.height), dcObj, (0, 0), win32con.SRCCOPY)
        
        # 转换为PIL图像
        bmpinfo = dataBitMap.GetInfo()
        bmpstr = dataBitMap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)
        
        # 清理资源
        win32gui.DeleteObject(dataBitMap.GetHandle())
        cDC.DeleteDC()
        dcObj.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        
        return np.array(img)
    
    def find_code_blocks(self, image):
        """识别代码块区域 (通常有特定背景色和边框)"""
        # 转为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 查找矩形边框 (代码块通常有矩形边框)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        code_block_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # 过滤掉太小的区域和长宽比异常的区域
            if w > 100 and h > 50 and 1 < w/h < 8:
                code_block_regions.append((x, y, w, h))
        
        return code_block_regions
    
    def find_separator_lines(self, image):
        """查找界面分隔线"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # 使用霍夫变换查找直线
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
        
        separators = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # 主要识别垂直分隔线
                if abs(x2 - x1) < 5 and abs(y2 - y1) > 100:
                    separators.append((x1, y1, x2, y2))
        
        return separators
    
    def find_ui_elements(self, image, keywords):
        """查找包含关键词的UI元素 (如Copy按钮)"""
        # 使用OCR识别文本区域
        text_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        ui_elements = []
        for i, text in enumerate(text_data['text']):
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    x = text_data['left'][i]
                    y = text_data['top'][i]
                    w = text_data['width'][i]
                    h = text_data['height'][i]
                    ui_elements.append((keyword, x, y, w, h))
        
        return ui_elements
    
    def determine_output_region(self, code_blocks, separators, ui_elements):
        """综合分析确定输出区域"""
        # 如果找到分隔线，就假设右侧是输出区域
        if separators:
            # 找最右侧的垂直分隔线
            rightmost_separator = max(separators, key=lambda s: s[0])
            x1 = rightmost_separator[0]
            y1 = 0  # 从窗口顶部开始
            width = self.cursor_window.width - x1
            height = self.cursor_window.height
            return (x1, y1, width, height)
        
        # 备选方案：根据代码块位置估计
        if code_blocks:
            # 查找最右侧的代码块
            rightmost_block = max(code_blocks, key=lambda b: b[0])
            x1 = max(0, rightmost_block[0] - 50)  # 扩展边界
            y1 = 0
            width = self.cursor_window.width - x1
            height = self.cursor_window.height
            return (x1, y1, width, height)
        
        # 备选方案：使用固定比例
        # Cursor通常在右侧显示AI聊天
        x1 = int(self.cursor_window.width * 0.6)
        y1 = 0
        width = self.cursor_window.width - x1
        height = self.cursor_window.height
        return (x1, y1, width, height)
    
    def extract_text_from_region(self):
        """从识别的区域提取文本"""
        if not self.output_region:
            return None
            
        # 截取输出区域
        x, y, width, height = self.output_region
        window_x = self.cursor_window.left + x
        window_y = self.cursor_window.top + y
        
        # 截图指定区域
        region_image = pyautogui.screenshot(region=(window_x, window_y, width, height))
        
        # OCR识别文本
        text = pytesseract.image_to_string(region_image)
        return text
    
    def extract_using_clipboard(self):
        """使用剪贴板方法提取文本 (更可靠但需要模拟用户操作)"""
        if not self.output_region or not self.cursor_window:
            return None
        
        # 先保存当前剪贴板内容
        original_clipboard = pyperclip.paste()
            
        # 激活Cursor窗口
        try:
            self.cursor_window.activate()
            time.sleep(0.5)  # 等待窗口激活
            
            # 计算区域中心点
            x, y, width, height = self.output_region
            center_x = self.cursor_window.left + x + width // 2
            center_y = self.cursor_window.top + y + height // 2
            
            # 移动到区域并执行三击选择文本 (通常会选择整个段落)
            pyautogui.moveTo(center_x, center_y)
            pyautogui.click(clicks=3)
            time.sleep(0.2)
            
            # 复制到剪贴板
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)
            
            # 获取剪贴板文本
            text = pyperclip.paste()
            
            # 如果文本太短，尝试按ESC取消选择，然后按Ctrl+A全选
            if not text or len(text) < 20:
                pyautogui.press('escape')
                time.sleep(0.2)
                
                # 全选并复制
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.2)
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.3)
                
                # 再次获取剪贴板文本
                text = pyperclip.paste()
            
            # 按ESC取消选择
            pyautogui.press('escape')
            
            # 恢复原始剪贴板内容
            pyperclip.copy(original_clipboard)
            
            return text
            
        except Exception as e:
            self.status_update.emit(f"提取文本出错: {str(e)}")
            # 恢复原始剪贴板内容
            pyperclip.copy(original_clipboard)
            return None
    
    def run(self):
        """运行完整提取流程"""
        self.status_update.emit("开始捕获Cursor输出...")
        
        if not self.find_cursor_window():
            self.status_update.emit("未找到Cursor窗口")
            return None
            
        if not self.identify_output_region():
            self.status_update.emit("无法识别AI输出区域")
            return None
            
        # 优先使用剪贴板方法
        self.status_update.emit("正在提取文本...")
        text = self.extract_using_clipboard()
            
        # 如果剪贴板方法失败，尝试OCR
        if not text or len(text) < 10:
            self.status_update.emit("剪贴板提取失败，尝试OCR...")
            text = self.extract_text_from_region()
            
        if text:
            self.status_update.emit("成功提取文本")
            # 发送提取到的文本
            self.text_extracted.emit(text)
            return text
        else:
            self.status_update.emit("提取失败")
            return None 