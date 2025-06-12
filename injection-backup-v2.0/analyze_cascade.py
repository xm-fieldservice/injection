import uiautomation as auto
import time
import sys

def print_element_info(element, indent=0):
    """打印元素信息"""
    if not element:
        return
    
    indent_str = '  ' * indent
    print(f"{indent_str}控件类型: {element.ControlTypeName}")
    print(f"{indent_str}名称: {element.Name}")
    print(f"{indent_str}类名: {element.ClassName}")
    print(f"{indent_str}自动化ID: {element.AutomationId}")
    print(f"{indent_str}边界: {element.BoundingRectangle}")
    
    # 检查是否支持文本模式
    if element.GetTextPattern():
        try:
            text = element.GetTextPattern().DocumentRange.GetText(100)  # 获取前100个字符
            if text:
                print(f"{indent_str}文本内容: {text[:100]}...")
        except:
            pass
    
    # 检查是否支持值模式
    if element.GetValuePattern():
        try:
            value = element.GetValuePattern().Value
            if value:
                print(f"{indent_str}值内容: {value[:100]}...")
        except:
            pass

def analyze_cascade_window():
    """分析Cascade窗口"""
    print("正在查找Cascade窗口...")
    
    # 尝试多个可能的窗口标题
    possible_titles = ["Cascade", "Codeium", "AI Assistant", "ChatGPT", "Claude", "Chrome Legacy Window"]
    cascade_window = None
    
    for title in possible_titles:
        windows = auto.WindowControl(RegexName=f".*{title}.*").GetWindows()
        if windows:
            cascade_window = windows[0]
            print(f"找到窗口: {cascade_window.Name}")
            break
    
    if not cascade_window:
        print("未找到Cascade窗口，正在枚举所有可见窗口...")
        all_windows = auto.GetRootControl().GetChildren()
        visible_windows = [w for w in all_windows if w.IsTopLevel() and w.IsVisible]
        
        print("\n可见窗口列表:")
        for i, window in enumerate(visible_windows):
            print(f"{i+1}. {window.Name} ({window.ClassName})")
        
        try:
            choice = int(input("\n请选择Cascade窗口编号: "))
            if 1 <= choice <= len(visible_windows):
                cascade_window = visible_windows[choice-1]
            else:
                print("无效的选择")
                return
        except:
            print("无效的输入")
            return
    
    print("\n===== Cascade窗口信息 =====")
    print_element_info(cascade_window)
    
    print("\n===== 查找可能的输出区域 =====")
    
    # 查找所有可能的文本控件
    text_controls = cascade_window.FindAllControls(lambda c: c.ControlType in [
        auto.ControlType.Edit,
        auto.ControlType.Document,
        auto.ControlType.Text,
        auto.ControlType.List,
        auto.ControlType.ListItem,
        auto.ControlType.Custom
    ])
    
    if text_controls:
        print(f"找到 {len(text_controls)} 个可能的文本控件")
        
        # 按面积排序
        text_controls.sort(key=lambda c: c.BoundingRectangle.width() * c.BoundingRectangle.height(), reverse=True)
        
        for i, control in enumerate(text_controls[:5]):  # 只显示前5个最大的控件
            print(f"\n--- 文本控件 {i+1} ---")
            print_element_info(control)
            
            # 尝试获取子元素
            children = control.GetChildren()
            if children:
                print(f"  子元素数量: {len(children)}")
                for j, child in enumerate(children[:3]):  # 只显示前3个子元素
                    print(f"\n  -- 子元素 {j+1} --")
                    print_element_info(child, indent=2)
    else:
        print("未找到可能的文本控件")
    
    print("\n===== 分析完成 =====")
    print("请根据以上信息确定哪个控件是Cascade的输出区域")
    print("然后可以使用控件类型、名称、类名和自动化ID来定位该控件")

if __name__ == "__main__":
    print("Cascade窗口分析工具")
    print("请确保Cascade窗口已打开且可见")
    input("按Enter键继续...")
    
    try:
        analyze_cascade_window()
    except Exception as e:
        print(f"分析过程出错: {str(e)}")
    
    input("\n分析完成，按Enter键退出...")
