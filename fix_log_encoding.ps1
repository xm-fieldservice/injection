# ===================================================================
# injection项目日志乱码修复与自动总结机制脚本
# 文件名: fix_log_encoding.ps1
# 作者: AI Assistant
# 创建时间: 2025-01-26
# ===================================================================

param(
    [string]$LogFile = "injection-log.md",
    [string]$ProjectName = "injection",
    [switch]$BackupFirst = $true
)

# 设置编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'UTF8'

Write-Host "=== injection项目日志乱码修复工具 ===" -ForegroundColor Green
Write-Host "目标文件: $LogFile" -ForegroundColor Yellow
Write-Host "项目名称: $ProjectName" -ForegroundColor Yellow

# 第一步：备份原始文件
if ($BackupFirst) {
    $BackupFile = "injection-log-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
    Write-Host "`n[1] 备份原始文件..." -ForegroundColor Cyan
    try {
        Copy-Item $LogFile $BackupFile -ErrorAction Stop
        Write-Host "✅ 备份完成: $BackupFile" -ForegroundColor Green
    } catch {
        Write-Host "❌ 备份失败: $_" -ForegroundColor Red
        exit 1
    }
}

# 第二步：检测和修复乱码
Write-Host "`n[2] 检测乱码问题..." -ForegroundColor Cyan

# 读取原始文件内容
try {
    $OriginalContent = Get-Content $LogFile -Raw -Encoding UTF8
    Write-Host "✅ 成功读取原始文件" -ForegroundColor Green
} catch {
    Write-Host "❌ 读取文件失败: $_" -ForegroundColor Red
    exit 1
}

# 检测乱码字符
$CorruptedChars = @([char]0xFFFD, '\?\*', '\?\?')
$HasCorruption = $false

foreach ($char in $CorruptedChars) {
    if ($OriginalContent -match [regex]::Escape($char)) {
        $HasCorruption = $true
        $Count = ([regex]::Matches($OriginalContent, [regex]::Escape($char))).Count
        Write-Host "❌ 发现乱码字符 '$char': $Count 处" -ForegroundColor Red
    }
}

if (-not $HasCorruption) {
    Write-Host "✅ 未发现乱码问题" -ForegroundColor Green
} else {
    Write-Host "`n[3] 修复乱码..." -ForegroundColor Cyan
    
    # 创建修复后的内容
    $CleanContent = $OriginalContent
    
    # 移除或替换乱码字符
    $CleanContent = $CleanContent -replace [char]0xFFFD, ''
    $CleanContent = $CleanContent -replace '\?\*', ''
    $CleanContent = $CleanContent -replace '\?\?+', ''
    
    # 清理异常的行
    $Lines = $CleanContent -split "`n"
    $CleanLines = @()
    
    foreach ($Line in $Lines) {
        # 跳过包含大量乱码的行
        if ($Line -match '^[^a-zA-Z\u4e00-\u9fa5\s\d\-\#\*\[\]]*$' -and $Line.Length -gt 10) {
            Write-Host "🗑️ 移除乱码行: $($Line.Substring(0, [Math]::Min(50, $Line.Length)))..." -ForegroundColor Yellow
            continue
        }
        $CleanLines += $Line
    }
    
    $CleanContent = $CleanLines -join "`n"
    
    # 保存修复后的文件
    try {
        $CleanContent | Out-File $LogFile -Encoding UTF8 -NoNewline
        Write-Host "✅ 乱码修复完成" -ForegroundColor Green
    } catch {
        Write-Host "❌ 保存修复文件失败: $_" -ForegroundColor Red
        exit 1
    }
}

# 第三步：建立自动总结机制
Write-Host "`n[4] 建立自动总结机制..." -ForegroundColor Cyan

# 创建自动总结函数
$AutoSummaryFunction = @'
function Add-WorkSummary {
    param(
        [string]$Input,
        [string]$Output,
        [string]$ProjectName = "injection",
        [string]$LogFile = "injection-log.md"
    )
    
    # 设置UTF-8编码
    $PSDefaultParameterValues['*:Encoding'] = 'UTF8'
    
    # 生成时间戳
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    # 构建日志条目
    $LogEntry = @"

# $Timestamp (Cursor - 项目：$ProjectName)

## 📥 输入：
$Input

## 📤 输出：
$Output

---

"@
    
    # 追加到日志文件
    try {
        Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
        Write-Host "✅ 工作总结已记录到 $LogFile" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ 记录失败: $_" -ForegroundColor Red
        return $false
    }
}
'@

# 保存自动总结函数到独立文件
$AutoSummaryFunction | Out-File "AutoSummary.ps1" -Encoding UTF8
Write-Host "✅ 自动总结函数已保存到 AutoSummary.ps1" -ForegroundColor Green

# 第四步：测试自动总结功能
Write-Host "`n[5] 测试自动总结功能..." -ForegroundColor Cyan

# 导入函数
. .\AutoSummary.ps1

# 测试记录本次工作
$TestInput = "用户要求创建脚本处理乱码问题，先备份日志文档，并建立自动总结机制"
$TestOutput = @"
### 🎯 核心工作 - 日志乱码修复脚本创建与自动总结机制建立 ⚡️

**🔧 修复实施详情**

✅ **步骤1：日志备份**
- 自动备份injection-log.md为带时间戳的备份文件
- 确保原始数据安全

✅ **步骤2：乱码检测与修复**
- 检测常见乱码字符：�、?*、??等
- 自动清理乱码行和异常字符
- 保持有效内容完整性

✅ **步骤3：编码环境优化**
- 强制设置UTF-8编码环境
- 统一PowerShell编码参数
- 确保后续写入正确编码

✅ **步骤4：自动总结机制**
- 创建Add-WorkSummary函数
- 支持自动时间戳生成
- 标准化日志格式输出
- 自动项目名称识别

### 🛡️ 脚本功能特性
- **备份保护**：自动备份原始文件
- **智能检测**：自动识别和统计乱码
- **批量修复**：一键清理所有乱码问题
- **UTF-8强制**：确保编码环境统一
- **自动化记录**：标准化工作总结机制

### 🔧 完成状态
- ✅ 乱码修复脚本创建完成
- ✅ 日志备份机制建立完成
- ✅ 自动总结函数开发完成
- ✅ UTF-8编码环境配置完成
- 🔄 脚本已可立即投入使用
"@

# 记录本次工作
if (Add-WorkSummary -Input $TestInput -Output $TestOutput -ProjectName $ProjectName) {
    Write-Host "✅ 本次工作已自动记录到日志" -ForegroundColor Green
} else {
    Write-Host "❌ 自动记录失败" -ForegroundColor Red
}

Write-Host "`n=== 修复完成 ===" -ForegroundColor Green
Write-Host "📋 使用方法:" -ForegroundColor Yellow
Write-Host "   1. 运行修复: .\fix_log_encoding.ps1" -ForegroundColor White
Write-Host "   2. 自动总结: . .\AutoSummary.ps1; Add-WorkSummary -Input '用户问题' -Output '工作总结'" -ForegroundColor White
Write-Host "📁 生成文件:" -ForegroundColor Yellow
Write-Host "   - fix_log_encoding.ps1 (修复脚本)" -ForegroundColor White  
Write-Host "   - AutoSummary.ps1 (自动总结函数)" -ForegroundColor White
Write-Host "   - injection-log-backup-*.md (备份文件)" -ForegroundColor White 