#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查思维导图文件加载状态
"""

import os

def check_mindmap_files():
    """检查思维导图文件的加载优先级"""
    print("🔍 检查思维导图文件加载状态...")
    
    # 按照layout_manager.py中的优先级检查
    simple_path = os.path.join(os.getcwd(), 'mindmap-simple.html')
    standalone_path = os.path.join(os.getcwd(), 'jsmind-standalone.html')
    original_path = os.path.join(os.getcwd(), 'jsmind-local.html')
    
    print(f"\n📁 文件存在状态:")
    files = [
        ("mindmap-simple.html (优先级1)", simple_path),
        ("jsmind-standalone.html (优先级2)", standalone_path),
        ("jsmind-local.html (优先级3)", original_path)
    ]
    
    will_load = None
    for name, path in files:
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        print(f"   {name}: {'✅' if exists else '❌'} ({size} 字节)")
        
        if exists and will_load is None:
            will_load = (name, path)
    
    print(f"\n🎯 根据优先级，将加载: {will_load[0] if will_load else '无文件'}")
    
    if will_load:
        # 检查文件内容
        name, path = will_load
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n🔍 文件内容分析 ({name}):")
        
        if 'mindmap-simple.html' in name:
            checks = [
                ("自包含实现", "mindmapData" in content),
                ("渲染函数", "function renderMindmap" in content),
                ("节点操作", "function addChildNode" in content),
                ("无外部依赖", "unpkg.com" not in content and "node_modules" not in content)
            ]
        elif 'standalone' in name:
            checks = [
                ("jsMind库引用", "jsmind" in content.lower()),
                ("CDN依赖", "unpkg.com" in content),
                ("思维导图数据", "mindData" in content)
            ]
        else:
            checks = [
                ("本地依赖", "node_modules" in content),
                ("jsMind引用", "jsmind" in content.lower())
            ]
        
        for check_name, result in checks:
            print(f"   {check_name}: {'✅' if result else '❌'}")
    
    return will_load

if __name__ == "__main__":
    check_mindmap_files() 