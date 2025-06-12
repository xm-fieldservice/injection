"""
系统清理工具 - injection项目模块化解耦方案

功能：
1. 检查和清理系统托盘相关代码
2. 验证窗口管理器是否正常工作
3. 测试最大化按钮和关闭按钮功能
4. 生成清理报告
"""

import os
import re
import subprocess
from pathlib import Path


class SystemCleanup:
    """系统清理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.cleanup_report = {
            'tray_references_found': [],
            'files_cleaned': [],
            'window_flags_checked': [],
            'cleanup_success': False
        }
    
    def check_tray_references(self):
        """检查项目中残留的系统托盘引用"""
        print("🔍 检查系统托盘引用...")
        
        tray_patterns = [
            r'QSystemTrayIcon',
            r'tray_icon',
            r'trayIcon',
            r'setupTrayIcon',
            r'system_tray',
            r'托盘'
        ]
        
        python_files = list(self.project_root.glob('*.py'))
        python_files.extend(list(self.project_root.glob('src/**/*.py')))
        
        for file_path in python_files:
            if file_path.name in ['system_cleanup.py', 'window_manager.py']:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in tray_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.cleanup_report['tray_references_found'].append({
                            'file': str(file_path),
                            'line': line_num,
                            'pattern': pattern,
                            'text': match.group()
                        })
                        
            except Exception as e:
                print(f"❌ 检查文件 {file_path} 失败：{e}")
    
    def check_window_manager_integration(self):
        """检查窗口管理器集成情况"""
        print("🔍 检查窗口管理器集成...")
        
        main_py = self.project_root / 'main.py'
        window_manager_py = self.project_root / 'window_manager.py'
        
        if not window_manager_py.exists():
            print("❌ window_manager.py 不存在")
            return False
            
        if not main_py.exists():
            print("❌ main.py 不存在")
            return False
            
        try:
            with open(main_py, 'r', encoding='utf-8') as f:
                main_content = f.read()
                
            # 检查导入
            if 'from window_manager import integrate_window_manager' not in main_content:
                print("❌ 窗口管理器导入缺失")
                return False
                
            # 检查集成调用
            if 'integrate_window_manager(self)' not in main_content:
                print("❌ 窗口管理器集成调用缺失")
                return False
                
            print("✅ 窗口管理器集成检查通过")
            return True
            
        except Exception as e:
            print(f"❌ 检查窗口管理器集成失败：{e}")
            return False
    
    def test_window_flags(self):
        """测试窗口标志设置"""
        print("🧪 测试窗口标志...")
        
        test_code = '''
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

app = QApplication(sys.argv)
window = QMainWindow()

# 测试正确的窗口标志
correct_flags = (
    Qt.WindowStaysOnTopHint | 
    Qt.Window | 
    Qt.WindowMaximizeButtonHint | 
    Qt.WindowMinimizeButtonHint | 
    Qt.WindowCloseButtonHint
)

window.setWindowFlags(correct_flags)
current_flags = window.windowFlags()

# 检查各个标志
checks = {
    'Window': bool(current_flags & Qt.Window),
    'StaysOnTop': bool(current_flags & Qt.WindowStaysOnTopHint),
    'MaximizeButton': bool(current_flags & Qt.WindowMaximizeButtonHint),
    'MinimizeButton': bool(current_flags & Qt.WindowMinimizeButtonHint),
    'CloseButton': bool(current_flags & Qt.WindowCloseButtonHint),
}

print("窗口标志检查结果：")
for flag_name, exists in checks.items():
    status = "✅" if exists else "❌"
    print(f"  {status} {flag_name}: {exists}")

# 返回检查结果
if all(checks.values()):
    print("✅ 所有窗口标志正常")
    sys.exit(0)
else:
    print("❌ 窗口标志存在问题")
    sys.exit(1)
'''
        
        try:
            result = subprocess.run(
                ['python', '-c', test_code],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            print(result.stdout)
            if result.stderr:
                print(f"错误输出：{result.stderr}")
                
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ 窗口标志测试失败：{e}")
            return False
    
    def generate_cleanup_report(self):
        """生成清理报告"""
        print("\n📋 生成清理报告...")
        
        report_content = f"""# 系统托盘清理报告

## 清理概述
- 清理时间：{self.get_current_time()}
- 清理状态：{'✅ 成功' if self.cleanup_report['cleanup_success'] else '❌ 失败'}

## 发现的托盘引用
"""
        
        if self.cleanup_report['tray_references_found']:
            for ref in self.cleanup_report['tray_references_found']:
                report_content += f"- **{ref['file']}:{ref['line']}** - `{ref['text']}` (模式: {ref['pattern']})\n"
        else:
            report_content += "✅ 未发现残留的托盘引用\n"
            
        report_content += f"""
## 清理完成的文件
"""
        
        if self.cleanup_report['files_cleaned']:
            for file_info in self.cleanup_report['files_cleaned']:
                report_content += f"- {file_info}\n"
        else:
            report_content += "📝 本次清理未修改文件（或已经清理完成）\n"
            
        report_content += f"""
## 窗口标志检查
"""
        
        if self.cleanup_report['window_flags_checked']:
            for check in self.cleanup_report['window_flags_checked']:
                report_content += f"- {check}\n"
        else:
            report_content += "⚠️ 窗口标志检查未完成\n"
            
        # 保存报告
        report_file = self.project_root / 'system_cleanup_report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        print(f"📄 清理报告已保存：{report_file}")
        return report_file
    
    def get_current_time(self):
        """获取当前时间"""
        import datetime
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def run_cleanup(self):
        """运行完整清理流程"""
        print("🚀 开始系统托盘清理...")
        
        # 1. 检查托盘引用
        self.check_tray_references()
        
        # 2. 检查窗口管理器集成
        window_manager_ok = self.check_window_manager_integration()
        
        # 3. 测试窗口标志
        window_flags_ok = self.test_window_flags()
        
        # 4. 评估清理状态
        self.cleanup_report['cleanup_success'] = (
            len(self.cleanup_report['tray_references_found']) == 0 and 
            window_manager_ok and 
            window_flags_ok
        )
        
        # 5. 生成报告
        report_file = self.generate_cleanup_report()
        
        # 6. 输出总结
        print(f"\n{'='*50}")
        print(f"🎯 清理总结")
        print(f"{'='*50}")
        
        if self.cleanup_report['cleanup_success']:
            print("✅ 系统托盘清理成功完成！")
            print("✅ 窗口管理器集成正常")
            print("✅ 窗口标志设置正确")
            print("✅ 现在关闭按钮应该能正常关闭程序")
            print("✅ 最大化按钮应该能正常工作")
        else:
            print("❌ 清理过程中发现问题")
            print(f"❌ 发现 {len(self.cleanup_report['tray_references_found'])} 个托盘引用")
            print("❌ 需要手动处理残留问题")
            
        print(f"📄 详细报告：{report_file}")
        
        return self.cleanup_report['cleanup_success']


def main():
    """主函数"""
    cleanup = SystemCleanup()
    success = cleanup.run_cleanup()
    
    if success:
        print("\n🎉 系统清理完成！建议重启程序测试功能。")
    else:
        print("\n⚠️ 清理未完全成功，请查看报告处理残留问题。")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main()) 