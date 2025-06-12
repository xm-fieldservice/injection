#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
选项卡调试脚本
用于详细检查选项卡的实际状态
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def debug_tabs():
    """调试选项卡问题"""
    print("=" * 60)
    print("开始调试选项卡问题...")
    print("=" * 60)
    
    # 导入主窗口
    from main import MainWindow
    
    # 创建主窗口实例
    main_window = MainWindow()
    main_window.show()
    
    def detailed_inspection():
        """详细检查"""
        print("\n🔍 开始详细检查...")
        
        try:
            # 检查布局管理器
            if not hasattr(main_window, 'layout_manager'):
                print("❌ main_window.layout_manager 不存在")
                return
            
            layout_manager = main_window.layout_manager
            print(f"✅ layout_manager 存在: {type(layout_manager)}")
            
            # 检查command_tabs
            if not hasattr(layout_manager, 'command_tabs'):
                print("❌ layout_manager.command_tabs 不存在")
                return
            
            command_tabs = layout_manager.command_tabs
            print(f"✅ command_tabs 存在: {type(command_tabs)}")
            
            # 详细检查选项卡
            tab_count = command_tabs.count()
            print(f"📊 实际选项卡数量: {tab_count}")
            
            if tab_count == 0:
                print("❌ 选项卡数量为0，这是问题所在！")
                return
            
            # 检查每个选项卡
            for i in range(tab_count):
                tab_text = command_tabs.tabText(i)
                tab_widget = command_tabs.widget(i)
                tab_enabled = command_tabs.isTabEnabled(i)
                tab_visible = command_tabs.isTabVisible(i) if hasattr(command_tabs, 'isTabVisible') else "未知"
                
                print(f"  选项卡 {i}:")
                print(f"    标题: '{tab_text}'")
                print(f"    Widget: {type(tab_widget) if tab_widget else 'None'}")
                print(f"    启用状态: {tab_enabled}")
                print(f"    可见状态: {tab_visible}")
                
                if tab_widget:
                    print(f"    Widget 可见: {tab_widget.isVisible()}")
                    print(f"    Widget 大小: {tab_widget.size()}")
            
            # 检查选项卡栏
            tab_bar = command_tabs.tabBar()
            if tab_bar:
                print(f"📋 TabBar 信息:")
                print(f"    TabBar 类型: {type(tab_bar)}")
                print(f"    TabBar 可见: {tab_bar.isVisible()}")
                print(f"    TabBar 大小: {tab_bar.size()}")
                print(f"    TabBar 计数: {tab_bar.count()}")
            
            # 检查父容器
            parent = command_tabs.parent()
            print(f"🏠 父容器信息:")
            print(f"    父容器类型: {type(parent) if parent else 'None'}")
            if parent:
                print(f"    父容器可见: {parent.isVisible()}")
                print(f"    父容器大小: {parent.size()}")
            
            # 检查具体的选项卡对象
            print(f"\n🔍 检查具体选项卡对象:")
            
            # 命令注入选项卡
            if hasattr(layout_manager, 'command_injection_tab'):
                print(f"    command_injection_tab: {type(layout_manager.command_injection_tab)}")
                print(f"    command_injection_tab 可见: {layout_manager.command_injection_tab.isVisible()}")
            else:
                print("    ❌ command_injection_tab 不存在")
            
            # 工具启动选项卡
            if hasattr(layout_manager, 'tool_launcher_tab'):
                print(f"    tool_launcher_tab: {type(layout_manager.tool_launcher_tab)}")
                print(f"    tool_launcher_tab 可见: {layout_manager.tool_launcher_tab.isVisible()}")
            else:
                print("    ❌ tool_launcher_tab 不存在")
            
            # 思维导图选项卡
            if hasattr(layout_manager, 'jsmind_tab'):
                print(f"    jsmind_tab: {type(layout_manager.jsmind_tab)}")
                print(f"    jsmind_tab 可见: {layout_manager.jsmind_tab.isVisible()}")
            else:
                print("    ❌ jsmind_tab 不存在")
            
            # 尝试手动切换到第三个选项卡
            if tab_count >= 3:
                print(f"\n🔄 尝试切换到第三个选项卡...")
                command_tabs.setCurrentIndex(2)
                current_index = command_tabs.currentIndex()
                print(f"    切换后当前索引: {current_index}")
                
                # 等待一下再检查
                QTimer.singleShot(500, lambda: print(f"    500ms后当前索引: {command_tabs.currentIndex()}"))
            
            # 检查选项卡样式
            print(f"\n🎨 选项卡样式检查:")
            style_sheet = command_tabs.styleSheet()
            print(f"    样式表长度: {len(style_sheet)} 字符")
            if style_sheet:
                print(f"    样式表预览: {style_sheet[:200]}...")
            
        except Exception as e:
            print(f"❌ 检查过程中出现异常: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 延迟执行检查
    QTimer.singleShot(1500, detailed_inspection)
    
    # 5秒后关闭
    QTimer.singleShot(5000, QApplication.quit)
    
    return main_window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        window = debug_tabs()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"调试脚本执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 