# -*- coding: utf-8 -*-
# injection项目日志管理器
# 功能：自动归档、大小监控、备份管理

param(
    [string]$Action = "check",  # check, archive, cleanup
    [int]$MaxSizeMB = 1,       # 最大文件大小(MB)
    [int]$KeepArchives = 12    # 保留归档数量
)

# 强制UTF-8编码
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'UTF8'

$LogFile = "injection-log.md"
$MaxSizeBytes = $MaxSizeMB * 1MB

function Get-LogFileStatus {
    if (-not (Test-Path $LogFile)) {
        Write-Host "❌ 日志文件不存在: $LogFile" -ForegroundColor Red
        return $null
    }
    
    $file = Get-Item $LogFile
    $sizeMB = [math]::Round($file.Length / 1MB, 2)
    $lines = (Get-Content $LogFile | Measure-Object -Line).Lines
    
    $status = @{
        Size = $file.Length
        SizeMB = $sizeMB
        Lines = $lines
        LastModified = $file.LastWriteTime
        NeedsArchive = $file.Length -gt $MaxSizeBytes
    }
    
    return $status
}

function Show-LogStatus {
    $status = Get-LogFileStatus
    if (-not $status) { return }
    
    Write-Host "📊 injection-log.md 状态报告" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    Write-Host "文件大小: $($status.SizeMB) MB ($($status.Size) 字节)" -ForegroundColor White
    Write-Host "行数统计: $($status.Lines) 行" -ForegroundColor White
    Write-Host "最后修改: $($status.LastModified)" -ForegroundColor White
    
    if ($status.NeedsArchive) {
        Write-Host "⚠️  文件大小超过 $MaxSizeMB MB，建议归档" -ForegroundColor Yellow
    } else {
        $remaining = [math]::Round(($MaxSizeBytes - $status.Size) / 1KB, 0)
        Write-Host "✅ 文件大小正常，还可增长约 $remaining KB" -ForegroundColor Green
    }
}

function Invoke-Archive {
    $status = Get-LogFileStatus
    if (-not $status) { return }
    
    # 生成归档文件名
    $timestamp = Get-Date -Format "yyyy-MM"
    $archiveFile = "injection-log-archive-$timestamp.md"
    
    # 检查是否已存在同名归档
    $counter = 1
    $originalArchiveFile = $archiveFile
    while (Test-Path $archiveFile) {
        $archiveFile = $originalArchiveFile -replace ".md$", "-$counter.md"
        $counter++
    }
    
    Write-Host "📦 开始归档日志文件..." -ForegroundColor Yellow
    Write-Host "源文件: $LogFile ($($status.SizeMB) MB)" -ForegroundColor White
    Write-Host "归档文件: $archiveFile" -ForegroundColor White
    
    try {
        # 复制到归档文件
        Copy-Item $LogFile $archiveFile -Force
        
        # 创建新的日志文件头部
        $newLogHeader = @"
# injection项目工作日志

> 这是injection项目的工作日志，记录所有开发过程、问题解决和功能实现。
> 
> 📅 日志开始时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
> 📦 前期日志已归档至: $archiveFile
> 
> ## 日志格式说明
> - 每次工作后使用时间戳标题
> - 使用交互块格式记录输入输出
> - 保持UTF-8编码

---

"@
        
        # 创建新日志文件
        $newLogHeader | Out-File $LogFile -Encoding UTF8
        
        Write-Host "✅ 归档完成！" -ForegroundColor Green
        Write-Host "📁 归档文件: $archiveFile ($($status.SizeMB) MB)" -ForegroundColor Cyan
        Write-Host "📄 新日志文件已创建" -ForegroundColor Cyan
        
        # 显示归档列表
        $archives = Get-ChildItem "injection-log-archive-*.md" | Sort-Object LastWriteTime -Descending
        if ($archives.Count -gt 0) {
            Write-Host "`n📚 历史归档列表:" -ForegroundColor Cyan
            $archives | ForEach-Object {
                $sizeMB = [math]::Round($_.Length / 1MB, 2)
                Write-Host "  $($_.Name) - $sizeMB MB - $($_.LastWriteTime.ToString('yyyy-MM-dd'))" -ForegroundColor Gray
            }
        }
        
    } catch {
        Write-Host "❌ 归档失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Invoke-Cleanup {
    Write-Host "🧹 清理历史归档..." -ForegroundColor Yellow
    
    $archives = Get-ChildItem "injection-log-archive-*.md" | Sort-Object LastWriteTime -Descending
    
    if ($archives.Count -le $KeepArchives) {
        Write-Host "✅ 归档数量在限制内 ($($archives.Count)/$KeepArchives)" -ForegroundColor Green
        return
    }
    
    $toDelete = $archives | Select-Object -Skip $KeepArchives
    
    Write-Host "📋 需要删除 $($toDelete.Count) 个旧归档:" -ForegroundColor Yellow
    $toDelete | ForEach-Object {
        Write-Host "  - $($_.Name) ($($_.LastWriteTime.ToString('yyyy-MM-dd')))" -ForegroundColor Gray
    }
    
    $confirm = Read-Host "确认删除这些文件？(y/N)"
    if ($confirm -eq 'y' -or $confirm -eq 'Y') {
        $toDelete | ForEach-Object {
            Remove-Item $_.FullName -Force
            Write-Host "🗑️  已删除: $($_.Name)" -ForegroundColor Red
        }
        Write-Host "✅ 清理完成！" -ForegroundColor Green
    } else {
        Write-Host "❌ 清理已取消" -ForegroundColor Yellow
    }
}

# 主执行逻辑
switch ($Action.ToLower()) {
    "check" {
        Show-LogStatus
    }
    "archive" {
        Show-LogStatus
        Write-Host ""
        Invoke-Archive
    }
    "cleanup" {
        Invoke-Cleanup
    }
    default {
        Write-Host "使用方法:" -ForegroundColor Cyan
        Write-Host "  .\LogManager.ps1 check     # 检查日志状态" -ForegroundColor White
        Write-Host "  .\LogManager.ps1 archive   # 执行归档" -ForegroundColor White
        Write-Host "  .\LogManager.ps1 cleanup   # 清理旧归档" -ForegroundColor White
    }
} 