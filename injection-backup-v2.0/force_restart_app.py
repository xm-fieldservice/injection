#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制重启应用并验证完整版思维导图
"""

import subprocess
import time
import os
import sys

def force_restart_app():
    """强制重启应用"""
    print("🔄 强制重启应用程序...")
    
    try:
        # 1. 查找并终止现有进程
        print("📋 查找现有Python进程...")
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python3.10.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'python3.10.exe' in result.stdout:
            print("🔍 发现运行中的Python进程:")
            lines = result.stdout.split('\n')
            for line in lines:
                if 'python3.10.exe' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        print(f"   PID: {pid}")
                        
                        # 终止进程
                        try:
                            subprocess.run(['taskkill', '/PID', pid, '/F'], 
                                         capture_output=True, shell=True)
                            print(f"✅ 成功终止进程 {pid}")
                        except Exception as e:
                            print(f"⚠️ 终止进程失败: {e}")
        else:
            print("ℹ️ 未发现运行中的Python进程")
            
        # 2. 等待进程完全退出
        print("⏳ 等待进程完全退出...")
        time.sleep(2)
        
        # 3. 验证依赖文件
        print("\n📁 验证jsMind依赖文件:")
        deps = [
            ("jsmind-local.html", "jsmind-local.html"),
            ("jsmind.js", "node_modules/jsmind/es6/jsmind.js"),
            ("jsmind.css", "node_modules/jsmind/style/jsmind.css"),
            ("jsmind.draggable-node.js", "node_modules/jsmind/es6/jsmind.draggable-node.js")
        ]
        
        all_exists = True
        for name, path in deps:
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"   ✅ {name}: {size:,} 字节")
            else:
                print(f"   ❌ {name}: 文件不存在")
                all_exists = False
        
        if not all_exists:
            print("⚠️ 部分依赖文件缺失，可能影响完整功能")
            return False
        
        # 4. 重新启动应用
        print("\n🚀 重新启动应用...")
        subprocess.Popen([sys.executable, 'injection_gui.py'])
        
        print("✅ 应用已重新启动")
        print("\n💡 请切换到 '🧠 思维导图' 选项卡查看效果")
        print("🎯 期待看到:")
        print("   - 🧠 jsMind 本地拖拽演示（中心节点）")
        print("   - 🚀 核心特性分支")
        print("   - 🔀 拖拽特性分支")
        print("   - 📋 应用场景分支") 
        print("   - ⭐ 技术优势分支")
        print("   - 完整的工具栏和详情面板")
        print("   - 三个工作区选项卡")
        
        return True
        
    except Exception as e:
        print(f"❌ 重启过程中出错: {e}")
        return False

if __name__ == "__main__":
    force_restart_app() 