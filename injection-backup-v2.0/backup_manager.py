#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
injection项目备份管理工具
用于维护、检查和清理项目的备份文件
"""

import os
import sys
import datetime
import shutil
import json
from pathlib import Path

class BackupManager:
    def __init__(self, project_dir=None):
        self.project_dir = project_dir or os.getcwd()
        self.project_name = self.detect_project_name()
        self.backup_dir = os.path.join(self.project_dir, "backups")
        self.ai_backup_dir = r"d:\ai-projects\backups"
        
    def detect_project_name(self):
        """自动检测项目名称"""
        dir_name = os.path.basename(self.project_dir)
        return dir_name if dir_name else "unknown"
    
    def status_report(self):
        """生成备份状态报告"""
        print(f"📊 {self.project_name} 项目备份状态报告")
        print("=" * 50)
        
        # 1. 检查备份目录
        if not os.path.exists(self.backup_dir):
            print("❌ 备份目录不存在")
            return
            
        print(f"📁 备份目录: {self.backup_dir}")
        
        # 2. 统计备份文件
        backup_files = []
        total_size = 0
        
        for file in os.listdir(self.backup_dir):
            if file.endswith('.md'):
                file_path = os.path.join(self.backup_dir, file)
                size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                backup_files.append((file, size, mtime))
                total_size += size
        
        backup_files.sort(key=lambda x: x[2], reverse=True)
        
        print(f"📈 备份文件总数: {len(backup_files)}")
        print(f"💾 总占用空间: {total_size / 1024 / 1024:.2f} MB")
        
        # 3. 列出最新的5个备份
        print("\n🕒 最近的备份文件:")
        for i, (filename, size, mtime) in enumerate(backup_files[:5]):
            time_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            size_kb = size // 1024
            backup_type = self.classify_backup_type(filename)
            print(f"  {i+1}. {filename} ({size_kb}KB, {time_str}) [{backup_type}]")
        
        # 4. 检查元数据文件
        print("\n🔍 元数据文件检查:")
        meta_files = [f for f in os.listdir(self.backup_dir) if f.startswith('backup_meta_')]
        for meta_file in meta_files:
            backup_type = meta_file.replace('backup_meta_', '').replace('.txt', '')
            corresponding_backup = f"{self.project_name}-log-incremental-{backup_type}.md"
            
            if corresponding_backup in [f[0] for f in backup_files]:
                print(f"  ✅ {backup_type}: 元数据和备份文件都存在")
            else:
                print(f"  ⚠️ {backup_type}: 有元数据但缺少备份文件")
        
        # 5. 检查AI项目目录备份
        print(f"\n🌐 AI项目目录备份检查:")
        if os.path.exists(self.ai_backup_dir):
            ai_backup_files = [f for f in os.listdir(self.ai_backup_dir) 
                             if f.startswith(f"{self.project_name}-log-incremental-")]
            if ai_backup_files:
                print(f"  ✅ 发现 {len(ai_backup_files)} 个AI项目目录备份")
                for file in ai_backup_files:
                    print(f"    - {file}")
            else:
                print("  ⚠️ AI项目目录没有发现备份文件")
        else:
            print("  ❌ AI项目备份目录不存在")
    
    def classify_backup_type(self, filename):
        """分类备份文件类型"""
        if "incremental" in filename:
            if "startup" in filename:
                return "启动增量"
            elif "backup-1" in filename:
                return "增量-1"
            elif "backup-2" in filename:
                return "增量-2"
            else:
                return "手动增量"
        elif "bak" in filename:
            return "整体备份(遗留)"
        elif "backup" in filename:
            return "脚本备份"
        else:
            return "未知类型"
    
    def cleanup_duplicates(self, dry_run=True):
        """清理重复和无用的备份文件"""
        print(f"🧹 清理重复备份文件 {'(预演模式)' if dry_run else '(执行模式)'}")
        print("=" * 50)
        
        cleanup_candidates = []
        
        # 1. 查找停止更新的bak文件
        for file in os.listdir(self.backup_dir):
            if file.endswith('.md') and 'bak' in file:
                file_path = os.path.join(self.backup_dir, file)
                mtime = os.path.getmtime(file_path)
                days_old = (datetime.datetime.now().timestamp() - mtime) / (24 * 3600)
                
                if days_old > 7:  # 超过7天未更新
                    cleanup_candidates.append((file_path, f"停止更新的bak文件 ({days_old:.1f}天前)"))
        
        # 2. 查找根目录的重复备份
        root_backups = [f for f in os.listdir(self.project_dir) 
                       if f.startswith(f"{self.project_name}-log-backup-") and f.endswith('.md')]
        
        if len(root_backups) > 2:  # 保留最新的2个
            root_backups.sort(key=lambda x: os.path.getmtime(os.path.join(self.project_dir, x)))
            for old_backup in root_backups[:-2]:
                file_path = os.path.join(self.project_dir, old_backup)
                cleanup_candidates.append((file_path, "根目录重复备份"))
        
        # 3. 显示清理计划
        if cleanup_candidates:
            print(f"发现 {len(cleanup_candidates)} 个可清理的文件:")
            total_size = 0
            for file_path, reason in cleanup_candidates:
                size = os.path.getsize(file_path)
                total_size += size
                size_mb = size / 1024 / 1024
                print(f"  🗑️ {os.path.basename(file_path)} ({size_mb:.2f}MB) - {reason}")
            
            print(f"\n💾 可释放空间: {total_size / 1024 / 1024:.2f} MB")
            
            if not dry_run:
                confirm = input("\n⚠️ 确定要删除这些文件吗？(y/N): ")
                if confirm.lower() == 'y':
                    deleted_count = 0
                    for file_path, reason in cleanup_candidates:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"✅ 已删除: {os.path.basename(file_path)}")
                        except Exception as e:
                            print(f"❌ 删除失败: {os.path.basename(file_path)} - {e}")
                    print(f"\n🎉 清理完成，删除了 {deleted_count} 个文件")
                else:
                    print("取消清理操作")
        else:
            print("✅ 没有发现需要清理的重复备份文件")
    
    def create_emergency_backup(self):
        """创建紧急完整备份"""
        log_file = os.path.join(self.project_dir, f"{self.project_name}-log.md")
        
        if not os.path.exists(log_file):
            print("❌ 找不到日志文件")
            return None
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{self.project_name}-log-emergency-{timestamp}.md"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        os.makedirs(self.backup_dir, exist_ok=True)
        
        try:
            shutil.copy2(log_file, backup_path)
            size = os.path.getsize(backup_path)
            size_mb = size / 1024 / 1024
            print(f"🚑 紧急备份创建成功: {backup_filename} ({size_mb:.2f}MB)")
            return backup_path
        except Exception as e:
            print(f"❌ 紧急备份创建失败: {e}")
            return None


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="injection项目备份管理工具")
    parser.add_argument("action", choices=["status", "cleanup", "emergency"], 
                       help="操作类型: status(状态报告), cleanup(清理重复), emergency(紧急备份)")
    parser.add_argument("--execute", action="store_true", 
                       help="执行清理操作（默认为预演模式）")
    parser.add_argument("--project-dir", type=str, 
                       help="项目目录路径（默认为当前目录）")
    
    args = parser.parse_args()
    
    manager = BackupManager(args.project_dir)
    
    if args.action == "status":
        manager.status_report()
    elif args.action == "cleanup":
        manager.cleanup_duplicates(dry_run=not args.execute)
    elif args.action == "emergency":
        manager.create_emergency_backup()
    

if __name__ == "__main__":
    main() 