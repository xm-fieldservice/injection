#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
追踪选项卡变化的脚本
监控选项卡数量变化，找出第三个选项卡何时消失
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def trace_tab_changes():
    """追踪选项卡变化"""
    print("=" * 60)
    print("开始追踪选项卡变化...")
    print("=" * 60)
    
    # 导入主窗口
    from main import MainWindow
    
    # 创建主窗口实例
    main_window = MainWindow()
    main_window.show()
    
    # 追踪变量
    previous_tab_count = 0
    check_count = 0
    
    def check_tabs():
        """检查选项卡状态"""
        nonlocal previous_tab_count, check_count
        check_count += 1
        
        try:
            if hasattr(main_window, 'layout_manager') and hasattr(main_window.layout_manager, 'command_tabs'):
                command_tabs = main_window.layout_manager.command_tabs
                current_tab_count = command_tabs.count()
                
                # 检查是否有变化
                if current_tab_count != previous_tab_count:
                    print(f"\n🔄 检查 #{check_count}: 选项卡数量变化 {previous_tab_count} -> {current_tab_count}")
                    
                    # 详细记录当前状态
                    for i in range(current_tab_count):
                        tab_text = command_tabs.tabText(i)
                        print(f"    选项卡 {i}: '{tab_text}'")
                    
                    # 特别检查第三个选项卡
                    if current_tab_count >= 3:
                        print(f"    ✅ 第三个选项卡存在: '{command_tabs.tabText(2)}'")
                    else:
                        print(f"    ❌ 第三个选项卡缺失！")
                    
                    previous_tab_count = current_tab_count
                else:
                    # 即使数量没变，也检查第三个选项卡是否存在
                    if check_count % 10 == 0:  # 每10次检查打印一次状态
                        if current_tab_count >= 3:
                            print(f"✅ 检查 #{check_count}: 保持3个选项卡")
                        else:
                            print(f"❌ 检查 #{check_count}: 仍然只有{current_tab_count}个选项卡")
            else:
                print(f"⚠️ 检查 #{check_count}: layout_manager 或 command_tabs 不存在")
                
        except Exception as e:
            print(f"❌ 检查 #{check_count} 失败: {str(e)}")
    
    # 高频监控 - 每100ms检查一次，持续10秒
    timer = QTimer()
    timer.timeout.connect(check_tabs)
    timer.start(100)  # 100ms间隔
    
    # 10秒后停止监控并关闭应用
    def stop_monitoring():
        timer.stop()
        print(f"\n📊 监控完成，共检查了 {check_count} 次")
        print("即将关闭应用...")
        QTimer.singleShot(1000, QApplication.quit)
    
    QTimer.singleShot(10000, stop_monitoring)  # 10秒后停止
    
    return main_window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        window = trace_tab_changes()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"追踪脚本执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 