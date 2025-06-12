# -*- coding: utf-8 -*-
# Final Encoding Fix Script
# Created: 2025-01-26
# Purpose: Clean up all encoding issues in injection project

# Force UTF-8 encoding for PowerShell
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'UTF8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'UTF8'

# Set console code page to UTF-8
chcp 65001 | Out-Null

$LogFile = "injection-log.md"
$BackupFile = "injection-log-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"

Write-Host "=== Starting Final Encoding Fix ===" -ForegroundColor Green

# Step 1: Create backup
Write-Host "[1] Creating backup: $BackupFile" -ForegroundColor Yellow
Copy-Item $LogFile $BackupFile -Force

# Step 2: Read file with correct encoding and clean up
Write-Host "[2] Reading and cleaning file..." -ForegroundColor Yellow
$content = Get-Content $LogFile -Raw -Encoding UTF8

# Remove various types of corrupted characters
$cleanContent = $content -replace '[﻿����]', '' # BOM and replacement chars
$cleanContent = $cleanContent -replace '[\uFFFD\uFEFF]', '' # Unicode replacement chars
$cleanContent = $cleanContent -replace '[鈿★笍鈿?鉁?馃敡馃搵馃洝锔?馃挕馃攧馃摜馃摛]', '' # Corrupted emoji
$cleanContent = $cleanContent -replace '椤圭洰锛?', '项目：' # Fix specific corrupted text
$cleanContent = $cleanContent -replace '杈撳叆锛?', '输入：'
$cleanContent = $cleanContent -replace '杈撳嚭锛?', '输出：'

# Clean up lines with heavy corruption
$lines = $cleanContent -split "`n"
$cleanLines = @()

foreach ($line in $lines) {
    # Skip lines that are heavily corrupted (contain too many question marks or weird chars)
    if ($line -match '[锛?娴?鍒?璧?鍙?闄?璁?鎬?绯?閰?鎸?娣?鎻?鍒?鐩?鐞?寮?鍏?缁?鏈?鎶?澶?搴?璁?鍔?]' -and $line.Length -gt 20) {
        # Skip heavily corrupted lines
        continue
    }
    $cleanLines += $line
}

$finalContent = $cleanLines -join "`n"

# Step 3: Save cleaned file
Write-Host "[3] Saving cleaned file..." -ForegroundColor Yellow
[System.IO.File]::WriteAllText($LogFile, $finalContent, [System.Text.Encoding]::UTF8)

# Step 4: Create proper summary function
Write-Host "[4] Creating summary function..." -ForegroundColor Yellow

# Create the summary script content
$summaryContent = @'
# -*- coding: utf-8 -*-
# Auto Summary Function for injection project
# UTF-8 encoding enforced

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'UTF8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'UTF8'

function Add-WorkSummary {
    param(
        [string]$Input = "",
        [string]$Output = ""
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $projectName = "injection"
    $logFile = "injection-log.md"
    
    $logEntry = @"

# $timestamp (Cursor - 项目：$projectName)

## 📥 输入：
$Input

## 📤 输出：
$Output

---
"@
    
    [System.IO.File]::AppendAllText($logFile, $logEntry, [System.Text.Encoding]::UTF8)
    Write-Host "Summary added successfully" -ForegroundColor Green
}

Export-ModuleMember -Function Add-WorkSummary
'@

# Save the summary script
[System.IO.File]::WriteAllText("WorkSummary_UTF8.ps1", $summaryContent, [System.Text.Encoding]::UTF8)

Write-Host "=== Fix Completed ===" -ForegroundColor Green
Write-Host "Backup: $BackupFile" -ForegroundColor Cyan
Write-Host "Summary function: WorkSummary_UTF8.ps1" -ForegroundColor Cyan

# Test the summary function
Write-Host "[5] Testing summary function..." -ForegroundColor Yellow
. .\WorkSummary_UTF8.ps1
Add-WorkSummary -Input "测试UTF-8编码功能" -Output "编码修复脚本测试成功" 