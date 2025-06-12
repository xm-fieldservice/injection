#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

def diagnose_webchannel():
    """诊断WebChannel实现问题"""
    
    print("🔍 WebChannel实现诊断")
    print("=" * 50)
    
    # 检查文件存在性
    html_file = "jsmind-local.html"
    py_file = "layout_manager.py"
    
    print(f"📁 文件检查:")
    print(f"  HTML文件存在: {os.path.exists(html_file)}")
    print(f"  Python文件存在: {os.path.exists(py_file)}")
    
    if not os.path.exists(html_file):
        print("❌ HTML文件不存在!")
        return
    
    # 检查HTML文件内容
    print(f"\n📄 HTML文件分析:")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    webchannel_checks = [
        ("QWebChannel库引用", 'qwebchannel.js' in html_content),
        ("initWebChannel函数", 'function initWebChannel()' in html_content),
        ("showNodeDetails函数", 'function showNodeDetails(' in html_content),
        ("sendNodeDetailsToQt函数", 'function sendNodeDetailsToQt(' in html_content),
        ("WebChannel初始化", 'new QWebChannel(' in html_content),
        ("pyqt_bridge对象", 'pyqt_bridge' in html_content),
    ]
    
    for check_name, result in webchannel_checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}: {result}")
    
    # 检查Python文件内容
    if os.path.exists(py_file):
        print(f"\n🐍 Python文件分析:")
        with open(py_file, 'r', encoding='utf-8') as f:
            py_content = f.read()
        
        python_checks = [
            ("JavaScriptBridge类", 'class JavaScriptBridge(' in py_content),
            ("QWebChannel导入", 'from PyQt5.QtWebChannel import QWebChannel' in py_content),
            ("WebChannel设置", 'setWebChannel(' in py_content),
            ("节点详情信号", 'node_details_received = pyqtSignal(' in py_content),
            ("updateNodeDetails方法", 'def updateNodeDetails(' in py_content),
            ("on_node_details_received方法", 'def on_node_details_received(' in py_content),
        ]
        
        for check_name, result in python_checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}: {result}")
    
    # 诊断建议
    print(f"\n💡 诊断建议:")
    all_html_ok = all(result for _, result in webchannel_checks)
    all_python_ok = all(result for _, result in python_checks) if os.path.exists(py_file) else False
    
    if all_html_ok and all_python_ok:
        print("  ✅ WebChannel实现看起来完整")
        print("  🔧 问题可能在于:")
        print("     1. 应用没有重启，仍在使用旧版本的HTML")
        print("     2. WebView缓存问题")
        print("     3. JavaScript控制台中有错误")
        print("     4. WebChannel对象注册时机问题")
    elif not all_html_ok:
        print("  ❌ HTML文件中WebChannel实现不完整")
        print("  🔧 需要检查JavaScript代码")
    elif not all_python_ok:
        print("  ❌ Python文件中WebChannel实现不完整") 
        print("  🔧 需要检查PyQt代码")
    
    print(f"\n🚀 建议的解决步骤:")
    print("  1. 强制重启应用程序")
    print("  2. 清除WebView缓存")
    print("  3. 检查JavaScript控制台错误")
    print("  4. 确认WebChannel对象注册成功")

if __name__ == "__main__":
    diagnose_webchannel() 