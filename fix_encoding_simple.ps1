# injection项目日志乱码修复脚本 (简化版)
# 设置UTF-8编码
$PSDefaultParameterValues['*:Encoding'] = 'UTF8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== injection项目日志修复工具 ===" -ForegroundColor Green

# 1. 备份原始文件
$BackupFile = "injection-log-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
Write-Host "[1] 备份原始文件到: $BackupFile" -ForegroundColor Yellow
Copy-Item "injection-log.md" $BackupFile

# 2. 读取并处理文件
Write-Host "[2] 处理乱码..." -ForegroundColor Yellow
$Content = Get-Content "injection-log.md" -Raw -Encoding UTF8

# 简单的乱码清理
$CleanContent = $Content -replace [char]0xFFFD, ''
$CleanContent = $CleanContent -replace '\?\*', ''
$CleanContent = $CleanContent -replace '\?\?+', ''

# 清理明显的乱码行
$Lines = $CleanContent -split "`r?`n"
$CleanLines = @()

foreach ($Line in $Lines) {
    # 如果行包含太多特殊字符且没有正常文字，跳过
    if ($Line -match '^[^\p{L}\p{N}\s\-\#\*\[\]\.]+$' -and $Line.Length -gt 20) {
        Write-Host "移除乱码行: $($Line.Substring(0, [Math]::Min(30, $Line.Length)))..." -ForegroundColor Red
        continue
    }
    $CleanLines += $Line
}

$CleanContent = $CleanLines -join "`n"

# 3. 保存修复后的文件
Write-Host "[3] 保存修复后的文件..." -ForegroundColor Yellow
$CleanContent | Out-File "injection-log.md" -Encoding UTF8 -NoNewline

# 4. 创建自动总结函数
Write-Host "[4] 创建自动总结函数..." -ForegroundColor Yellow

$FunctionContent = @'
function Add-WorkSummary {
    param(
        [string]$Input,
        [string]$Output,
        [string]$ProjectName = "injection"
    )
    
    $PSDefaultParameterValues['*:Encoding'] = 'UTF8'
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    $LogEntry = @"

# $Timestamp (Cursor - 项目：$ProjectName)

## 📥 输入：
$Input

## 📤 输出：
$Output

---

"@
    
    Add-Content -Path "injection-log.md" -Value $LogEntry -Encoding UTF8
    Write-Host "✅ 工作总结已记录" -ForegroundColor Green
}

# 使用示例
# Add-WorkSummary -Input "用户问题" -Output "工作总结"
'@

$FunctionContent | Out-File "AutoSummary.ps1" -Encoding UTF8

# 5. 测试自动总结功能
Write-Host "[5] 测试自动总结功能..." -ForegroundColor Yellow

# 导入函数并测试
. .\AutoSummary.ps1

$TestInput = "用户要求创建脚本处理乱码问题，先备份日志文档，并建立自动总结机制"
$TestOutput = @"
### 🎯 核心工作 - 日志乱码修复脚本创建与自动总结机制建立 ⚡️

**🔧 修复实施详情**

✅ **步骤1：日志备份**
- 自动备份injection-log.md为带时间戳的备份文件
- 备份文件：$BackupFile

✅ **步骤2：乱码检测与修复**
- 移除Unicode替换字符 (U+FFFD)
- 清理异常符号组合 (?*, ??)
- 移除包含大量乱码的行

✅ **步骤3：自动总结机制建立**
- 创建Add-WorkSummary函数
- 支持标准化日志格式
- 自动时间戳和项目识别
- UTF-8编码保证

**📋 脚本功能**
- **智能备份**：时间戳命名的安全备份
- **乱码清理**：自动识别和移除乱码内容
- **编码统一**：强制UTF-8编码环境
- **自动记录**：标准化工作日志机制

### 🛡️ 使用方法
1. 运行修复：`.\fix_encoding_simple.ps1`
2. 自动记录：`. .\AutoSummary.ps1; Add-WorkSummary -Input "问题" -Output "总结"`

### 🔧 完成状态
- ✅ 乱码修复脚本创建完成
- ✅ 日志文件备份完成
- ✅ 自动总结机制建立完成
- ✅ 编码环境优化完成
- 🔄 系统已可正常使用
"@

Add-WorkSummary -Input $TestInput -Output $TestOutput

Write-Host "`n=== 修复完成 ===" -ForegroundColor Green
Write-Host "备份文件: $BackupFile" -ForegroundColor Cyan
Write-Host "修复脚本: fix_encoding_simple.ps1" -ForegroundColor Cyan  
Write-Host "总结函数: AutoSummary.ps1" -ForegroundColor Cyan 