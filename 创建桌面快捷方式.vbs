Set objShell = WScript.CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' 获取当前脚本所在目录
currentDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' 获取桌面路径
desktopPath = objShell.SpecialFolders("Desktop")

' 设置快捷方式路径和名称
shortcutPath = desktopPath & "\提示词注入工具.lnk"

' 创建快捷方式对象
Set objShortcut = objShell.CreateShortcut(shortcutPath)

' 设置快捷方式属性
objShortcut.TargetPath = currentDir & "\桌面启动.bat"
objShortcut.WorkingDirectory = currentDir
objShortcut.Description = "提示词注入工具 - 桌面快捷启动"
objShortcut.IconLocation = currentDir & "\icon.png,0"

' 保存快捷方式
objShortcut.Save

' 显示成功消息
WScript.Echo "桌面快捷方式创建成功！" & vbCrLf & _
            "快捷方式名称: 提示词注入工具" & vbCrLf & _
            "位置: " & desktopPath & vbCrLf & vbCrLf & _
            "现在可以双击桌面图标启动程序了！" 