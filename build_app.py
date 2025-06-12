import os
import sys
import shutil
import subprocess
import datetime

def main():
    print("开始打包提示词注入工具...")
    
    # 创建打包目录
    build_dir = "build"
    dist_dir = "dist"
    package_name = "提示词注入工具"
    
    # 清理旧的构建文件
    if os.path.exists(build_dir):
        print(f"清理 {build_dir} 目录...")
        shutil.rmtree(build_dir)
    
    if os.path.exists(dist_dir):
        print(f"清理 {dist_dir} 目录...")
        shutil.rmtree(dist_dir)
    
    # 确保必要的目录存在
    for dir_path in ["config", "logs"]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    # 检查配置文件是否存在，如果不存在则创建默认配置
    if not os.path.exists("config/config.json"):
        with open("config/config.json", "w", encoding="utf-8") as f:
            f.write('{\n    "target_window": null,\n    "target_position": null,\n    "target_window_title": null,\n    "log_file": "logs/commands.md"\n}')
    
    if not os.path.exists("config/templates.json"):
        with open("config/templates.json", "w", encoding="utf-8") as f:
            f.write('{\n    "scenes": {}\n}')
    
    # 使用PyInstaller打包应用
    print("使用PyInstaller打包应用...")
    
    # 构建PyInstaller命令
    pyinstaller_cmd = [
        "pyinstaller",
        "--name", package_name,
        "--windowed",  # 无控制台窗口
        "--icon=icon.png",  # 应用图标
        "--add-data", "icon.png;.",  # 添加图标文件
        "--add-data", "config;config",  # 添加配置目录
        "--add-data", "images;images",  # 添加图片目录
        "--add-data", "resources;resources",  # 添加资源目录
        "main.py"  # 主程序入口
    ]
    
    # 执行PyInstaller命令
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("PyInstaller打包完成！")
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller打包失败: {e}")
        return
    except FileNotFoundError:
        print("错误: PyInstaller未安装。请运行 'pip install pyinstaller' 安装。")
        return
    
    # 复制额外的文件到dist目录
    print("复制额外文件...")
    
    # 创建日志目录
    os.makedirs(os.path.join(dist_dir, package_name, "logs"), exist_ok=True)
    
    # 创建README文件
    with open(os.path.join(dist_dir, package_name, "README.txt"), "w", encoding="utf-8") as f:
        f.write(f"""提示词注入工具
==========
版本: 1.0.0
打包日期: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

使用说明:
1. 双击运行"{package_name}.exe"启动程序
2. 使用校准功能选择目标窗口
3. 编写命令并使用注入功能

注意事项:
- 首次使用时需要设置API密钥
- 日志文件保存在logs目录下
- 配置文件保存在config目录下
""")
    
    # 创建压缩包
    output_zip = f"{package_name}_{datetime.datetime.now().strftime('%Y%m%d')}.zip"
    print(f"创建压缩包: {output_zip}")
    
    shutil.make_archive(
        os.path.join(dist_dir, package_name),  # 压缩包名称（不含扩展名）
        'zip',  # 压缩格式
        dist_dir,  # 源目录
        package_name  # 要压缩的目录
    )
    
    print(f"打包完成! 输出文件:")
    print(f"1. 可执行程序: {os.path.join(dist_dir, package_name, package_name + '.exe')}")
    print(f"2. 压缩包: {os.path.join(dist_dir, output_zip)}")

if __name__ == "__main__":
    main()
