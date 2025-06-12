#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题重新分配工具
强制为所有实例重新分配不同的主题
"""

import os
import glob
import json
import shutil

def reset_all_themes():
    """重置所有主题配置，强制重新分配"""
    print("🎨 开始重置所有主题配置...")
    
    # 删除所有主题配置目录
    theme_dirs = glob.glob('config_instance_*/')
    for theme_dir in theme_dirs:
        try:
            shutil.rmtree(theme_dir)
            print(f"🗑️ 已删除主题配置: {theme_dir}")
        except Exception as e:
            print(f"❌ 删除失败: {theme_dir} - {e}")
    
    # 删除旧的共享主题配置
    shared_config = 'config/theme_config.json'
    if os.path.exists(shared_config):
        try:
            os.remove(shared_config)
            print(f"🗑️ 已删除共享主题配置: {shared_config}")
        except Exception as e:
            print(f"❌ 删除失败: {shared_config} - {e}")
    
    print("✅ 主题配置重置完成")
    print("📋 下次启动工具时，各实例将自动分配不同主题")

def force_assign_themes():
    """强制为现有实例分配不同主题"""
    print("🎨 开始强制分配主题...")
    
    # 查找所有实例配置文件
    config_files = glob.glob('config_instance_*.json')
    
    if not config_files:
        print("❌ 未找到任何实例配置文件")
        return
    
    # 提取实例ID
    instance_ids = []
    for config_file in config_files:
        instance_id = config_file.replace('config_instance_', '').replace('.json', '')
        instance_ids.append(instance_id)
    
    print(f"📂 找到 {len(instance_ids)} 个实例: {instance_ids}")
    
    # 主题分配顺序
    themes = ['blue', 'red', 'green', 'orange']
    theme_names = {
        'blue': '🔵 蓝色主题',
        'red': '🔴 红色主题', 
        'green': '🟢 绿色主题',
        'orange': '🟠 橙色主题'
    }
    
    # 为每个实例分配主题
    for i, instance_id in enumerate(instance_ids):
        theme = themes[i % len(themes)]  # 循环分配
        
        # 创建实例主题配置目录
        theme_dir = f'config_instance_{instance_id}'
        os.makedirs(theme_dir, exist_ok=True)
        
        # 创建主题配置文件
        theme_config = {
            'instance_themes': {
                instance_id: theme
            }
        }
        
        theme_config_file = os.path.join(theme_dir, 'theme_config.json')
        with open(theme_config_file, 'w', encoding='utf-8') as f:
            json.dump(theme_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 实例 {instance_id} 分配主题: {theme_names[theme]}")
    
    print("🎊 主题分配完成！重启工具实例查看效果")

def show_current_assignments():
    """显示当前主题分配情况"""
    print("🎨 当前主题分配情况:")
    print("-" * 50)
    
    theme_dirs = glob.glob('config_instance_*/')
    
    if not theme_dirs:
        print("📂 未找到主题配置")
        return
    
    theme_names = {
        'blue': '🔵 蓝色主题',
        'red': '🔴 红色主题', 
        'green': '🟢 绿色主题',
        'orange': '🟠 橙色主题'
    }
    
    for theme_dir in theme_dirs:
        instance_id = theme_dir.replace('config_instance_', '').replace('/', '')
        theme_config_file = os.path.join(theme_dir, 'theme_config.json')
        
        if os.path.exists(theme_config_file):
            try:
                with open(theme_config_file, 'r', encoding='utf-8') as f:
                    theme_config = json.load(f)
                
                instance_themes = theme_config.get('instance_themes', {})
                if instance_id in instance_themes:
                    theme = instance_themes[instance_id]
                    theme_display = theme_names.get(theme, f"❓ {theme}")
                    print(f"🔧 实例 {instance_id}: {theme_display}")
                else:
                    print(f"⚠️ 实例 {instance_id}: 主题未分配")
                    
            except Exception as e:
                print(f"❌ 实例 {instance_id}: 读取配置失败 - {e}")
        else:
            print(f"📂 实例 {instance_id}: 配置文件不存在")

def main():
    """主函数"""
    while True:
        print("\n" + "="*50)
        print("🎨 主题重新分配工具")
        print("="*50)
        print("1. 📋 查看当前主题分配")
        print("2. 🔄 强制重新分配主题")
        print("3. 🗑️ 重置所有主题配置")
        print("4. 🚪 退出")
        print("="*50)
        
        choice = input("请选择操作 (1-4): ").strip()
        
        if choice == '1':
            print()
            show_current_assignments()
            
        elif choice == '2':
            print()
            force_assign_themes()
            
        elif choice == '3':
            print()
            confirm = input("⚠️ 确认要重置所有主题配置吗？(y/N): ").lower().strip()
            if confirm == 'y':
                reset_all_themes()
            else:
                print("❌ 操作已取消")
                
        elif choice == '4':
            print("👋 再见！")
            break
            
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main() 