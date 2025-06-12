#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实例配置清理工具
用于管理和清理多个注入工具实例的配置文件
"""

import os
import glob
import json
from datetime import datetime, timedelta

def list_instance_configs():
    """列出所有实例配置文件"""
    config_files = glob.glob('config_instance_*.json')
    
    if not config_files:
        print("📂 未找到实例配置文件")
        return []
    
    print(f"📂 找到 {len(config_files)} 个实例配置文件:")
    print("-" * 50)
    
    configs = []
    for config_file in config_files:
        try:
            # 提取实例ID
            instance_id = config_file.replace('config_instance_', '').replace('.json', '')
            
            # 读取配置信息
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 获取文件修改时间
            mod_time = datetime.fromtimestamp(os.path.getmtime(config_file))
            
            # 提取关键信息
            target_window_title = config.get('target_window_title', '未设置')
            target_position = config.get('target_position')
            log_file = config.get('log_file', '未设置')
            
            config_info = {
                'file': config_file,
                'instance_id': instance_id,
                'mod_time': mod_time,
                'target_window_title': target_window_title,
                'target_position': target_position,
                'log_file': log_file,
                'is_calibrated': bool(target_position)
            }
            
            configs.append(config_info)
            
            # 显示配置信息
            status = "✅ 已校准" if config_info['is_calibrated'] else "❌ 未校准"
            print(f"🔧 实例 {instance_id}")
            print(f"   状态: {status}")
            print(f"   目标: {target_window_title}")
            print(f"   位置: {target_position}")
            print(f"   日志: {os.path.basename(log_file) if log_file != '未设置' else '未设置'}")
            print(f"   修改: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
        except Exception as e:
            print(f"❌ 读取配置文件 {config_file} 失败: {e}")
    
    return configs

def list_theme_configs():
    """列出所有主题配置目录"""
    theme_dirs = glob.glob('config_instance_*/')
    
    if not theme_dirs:
        print("🎨 未找到主题配置目录")
        return []
    
    print(f"🎨 找到 {len(theme_dirs)} 个主题配置目录:")
    print("-" * 50)
    
    theme_configs = []
    for theme_dir in theme_dirs:
        try:
            instance_id = theme_dir.replace('config_instance_', '').replace('/', '')
            theme_config_file = os.path.join(theme_dir, 'theme_config.json')
            
            if os.path.exists(theme_config_file):
                with open(theme_config_file, 'r', encoding='utf-8') as f:
                    theme_config = json.load(f)
                
                instance_themes = theme_config.get('instance_themes', {})
                
                theme_info = {
                    'dir': theme_dir,
                    'instance_id': instance_id,
                    'themes': instance_themes
                }
                
                theme_configs.append(theme_info)
                
                print(f"🎨 实例 {instance_id} 主题配置:")
                for tid, theme in instance_themes.items():
                    theme_icon = {'blue': '🔵', 'red': '🔴', 'green': '🟢', 'orange': '🟠'}.get(theme, '⚪')
                    print(f"   {theme_icon} {tid}: {theme}")
            else:
                print(f"⚠️ 实例 {instance_id}: 主题配置文件不存在")
            
            print()
            
        except Exception as e:
            print(f"❌ 读取主题配置 {theme_dir} 失败: {e}")
    
    return theme_configs

def clean_old_configs(hours=24):
    """清理指定小时前的旧配置"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    # 清理实例配置文件
    config_files = glob.glob('config_instance_*.json')
    cleaned_files = []
    
    for config_file in config_files:
        try:
            mod_time = datetime.fromtimestamp(os.path.getmtime(config_file))
            if mod_time < cutoff_time:
                os.remove(config_file)
                cleaned_files.append(config_file)
                print(f"🗑️ 已删除旧配置: {config_file}")
        except Exception as e:
            print(f"❌ 删除配置文件 {config_file} 失败: {e}")
    
    # 清理主题配置目录
    theme_dirs = glob.glob('config_instance_*/')
    cleaned_dirs = []
    
    for theme_dir in theme_dirs:
        try:
            mod_time = datetime.fromtimestamp(os.path.getmtime(theme_dir))
            if mod_time < cutoff_time:
                import shutil
                shutil.rmtree(theme_dir)
                cleaned_dirs.append(theme_dir)
                print(f"🗑️ 已删除旧主题配置: {theme_dir}")
        except Exception as e:
            print(f"❌ 删除主题配置目录 {theme_dir} 失败: {e}")
    
    if cleaned_files or cleaned_dirs:
        print(f"\n✅ 清理完成: 删除了 {len(cleaned_files)} 个配置文件和 {len(cleaned_dirs)} 个主题目录")
    else:
        print(f"\n📂 没有找到 {hours} 小时前的旧配置文件")

def reset_all_configs():
    """重置所有实例配置"""
    print("⚠️ 这将删除所有实例配置文件和主题配置！")
    confirm = input("确认要继续吗？(y/N): ").lower().strip()
    
    if confirm != 'y':
        print("❌ 操作已取消")
        return
    
    # 删除所有实例配置文件
    config_files = glob.glob('config_instance_*.json')
    for config_file in config_files:
        try:
            os.remove(config_file)
            print(f"🗑️ 已删除: {config_file}")
        except Exception as e:
            print(f"❌ 删除失败: {config_file} - {e}")
    
    # 删除所有主题配置目录
    theme_dirs = glob.glob('config_instance_*/')
    for theme_dir in theme_dirs:
        try:
            import shutil
            shutil.rmtree(theme_dir)
            print(f"🗑️ 已删除: {theme_dir}")
        except Exception as e:
            print(f"❌ 删除失败: {theme_dir} - {e}")
    
    print("✅ 所有实例配置已重置")

def main():
    """主函数"""
    while True:
        print("\n" + "="*60)
        print("🔧 注入工具实例配置管理器")
        print("="*60)
        print("1. 📂 查看所有实例配置")
        print("2. 🎨 查看所有主题配置")
        print("3. 🗑️ 清理24小时前的旧配置")
        print("4. 🗑️ 清理指定时间前的配置")
        print("5. ⚠️ 重置所有配置")
        print("6. 🚪 退出")
        print("="*60)
        
        choice = input("请选择操作 (1-6): ").strip()
        
        if choice == '1':
            print("\n📂 实例配置文件列表:")
            print("="*60)
            list_instance_configs()
            
        elif choice == '2':
            print("\n🎨 主题配置列表:")
            print("="*60)
            list_theme_configs()
            
        elif choice == '3':
            print("\n🗑️ 清理24小时前的配置:")
            print("="*60)
            clean_old_configs(24)
            
        elif choice == '4':
            try:
                hours = int(input("请输入小时数: "))
                print(f"\n🗑️ 清理{hours}小时前的配置:")
                print("="*60)
                clean_old_configs(hours)
            except ValueError:
                print("❌ 无效的小时数")
                
        elif choice == '5':
            print("\n⚠️ 重置所有配置:")
            print("="*60)
            reset_all_configs()
            
        elif choice == '6':
            print("👋 再见！")
            break
            
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main() 