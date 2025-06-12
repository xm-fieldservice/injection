#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断思维导图选项卡状态
"""

import sys
import os

def diagnose_mindmap_status():
    """诊断思维导图选项卡状态"""
    print("🔍 诊断思维导图选项卡状态...")
    
    # 1. 检查文件状态
    html_path = os.path.join(os.getcwd(), 'jsmind-local.html')
    print(f"\n📁 文件状态:")
    print(f"   路径: {html_path}")
    print(f"   存在: {'✅' if os.path.exists(html_path) else '❌'}")
    
    if os.path.exists(html_path):
        file_size = os.path.getsize(html_path)
        print(f"   大小: {file_size:,} 字节")
        
        # 检查文件内容关键字
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        keywords = ['jsmind', 'DOCTYPE html', 'draggable', 'export', 'import']
        print(f"   关键词检查:")
        for keyword in keywords:
            count = content.lower().count(keyword.lower())
            print(f"     {keyword}: {count} 次")
    
    # 2. 检查布局管理器代码
    layout_file = 'layout_manager.py'
    print(f"\n🔧 布局管理器检查:")
    print(f"   文件: {layout_file}")
    print(f"   存在: {'✅' if os.path.exists(layout_file) else '❌'}")
    
    if os.path.exists(layout_file):
        with open(layout_file, 'r', encoding='utf-8') as f:
            layout_content = f.read()
        
        # 检查关键代码段
        checks = [
            ('QWebEngineView导入', 'from PyQt5.QtWebEngineWidgets import QWebEngineView'),
            ('jsmind选项卡创建', 'self.jsmind_tab = QWidget()'),
            ('HTML文件加载', 'jsmind-local.html'),
            ('选项卡添加', '🧠 思维导图'),
            ('WebEngine视图', 'QWebEngineView()')
        ]
        
        for name, keyword in checks:
            found = keyword in layout_content
            print(f"     {name}: {'✅' if found else '❌'}")
            if not found:
                # 尝试查找相似的代码
                similar_keywords = [
                    keyword.lower(),
                    keyword.replace('QWebEngineView', 'WebEngine'),
                    keyword.replace('self.', ''),
                ]
                for similar in similar_keywords:
                    if similar in layout_content.lower():
                        print(f"       相似代码: {similar}")
                        break
    
    # 3. 检查Python环境
    print(f"\n🐍 Python环境检查:")
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        print("     QWebEngineView: ✅ 可用")
    except ImportError as e:
        print(f"     QWebEngineView: ❌ 不可用 - {e}")
    
    try:
        from PyQt5.QtWidgets import QTextBrowser
        print("     QTextBrowser: ✅ 可用")
    except ImportError as e:
        print(f"     QTextBrowser: ❌ 不可用 - {e}")
    
    # 4. 检查正在运行的进程
    print(f"\n🏃 进程状态:")
    try:
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python*'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            python_processes = [line for line in lines if 'python' in line.lower()]
            print(f"     Python进程数: {len(python_processes)}")
            for proc in python_processes:
                if proc.strip():
                    print(f"       {proc.strip()}")
        else:
            print("     无法检查进程状态")
    except Exception as e:
        print(f"     进程检查错误: {e}")
    
    print(f"\n📋 诊断总结:")
    print("   1. 如果文件存在但选项卡空白，可能是热重载问题")
    print("   2. 如果WebEngine不可用，会回退到TextBrowser")
    print("   3. 建议重启应用程序以确保代码生效")
    
    return True

if __name__ == "__main__":
    diagnose_mindmap_status() 