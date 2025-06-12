# 修复layout_manager.py的缩进问题
import re

def fix_indentation():
    with open('layout_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复force_save_layout函数的缩进问题
    content = re.sub(
        r'(\s+)def force_save_layout\(self\):',
        r'    def force_save_layout(self):',
        content
    )
    
    # 修复所有缩进问题
    lines = content.split('\n')
    fixed_lines = []
    in_function = False
    
    for i, line in enumerate(lines):
        if 'def force_save_layout(self):' in line:
            fixed_lines.append('    def force_save_layout(self):')
            in_function = True
        elif in_function and line.strip() == '' and i + 1 < len(lines) and 'def ' in lines[i + 1]:
            # 函数结束
            fixed_lines.append(line)
            in_function = False
        elif in_function and line.strip():
            # 在force_save_layout函数内部，确保正确缩进
            if line.startswith('        '):
                fixed_lines.append(line)
            elif line.strip().startswith('"""'):
                fixed_lines.append('        """' + line.strip()[3:])
            elif line.strip():
                fixed_lines.append('        ' + line.strip())
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    with open('layout_manager.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 缩进问题已修复")

if __name__ == "__main__":
    fix_indentation() 