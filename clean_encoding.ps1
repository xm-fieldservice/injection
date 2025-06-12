# Clean Encoding Script - Simple Version
# Purpose: Remove corrupted encoding from injection-log.md

# Force UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

$LogFile = "injection-log.md"
$BackupFile = "injection-log-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"

Write-Host "=== Clean Encoding Process ===" -ForegroundColor Green

# Create backup
Write-Host "[1] Creating backup..." -ForegroundColor Yellow
Copy-Item $LogFile $BackupFile -Force

# Read file content
Write-Host "[2] Reading file..." -ForegroundColor Yellow
$rawContent = [System.IO.File]::ReadAllText($LogFile, [System.Text.Encoding]::UTF8)

# Remove corrupted characters using Unicode codepoints
Write-Host "[3] Cleaning corrupted characters..." -ForegroundColor Yellow
$cleanContent = $rawContent

# Remove Unicode replacement characters
$cleanContent = $cleanContent -replace '\uFFFD', ''
$cleanContent = $cleanContent -replace '\uFEFF', ''

# Remove corrupted emoji patterns
$cleanContent = $cleanContent -replace '[\u2014-\u2015\u2018-\u201F\u2026\u2030\u2032-\u2037\u2039-\u203A\u203C-\u203D\u2047-\u2049\u204E-\u2052\u2057\u205F-\u2063\u2070-\u2079\u207A-\u207F\u2080-\u208E\u20A0-\u20B9\u20D0-\u20FF\u2100-\u214F\u2150-\u218F\u2190-\u21FF\u2200-\u22FF\u2300-\u23FF\u2400-\u243F\u2440-\u245F\u2460-\u24FF\u2500-\u257F\u2580-\u259F\u25A0-\u25FF\u2600-\u26FF\u2700-\u27BF]', ''

# Split into lines and filter
$lines = $cleanContent -split "`r?`n"
$cleanLines = @()

foreach ($line in $lines) {
    # Skip lines with excessive non-ASCII characters that indicate corruption
    $nonAsciiCount = 0
    for ($i = 0; $i -lt $line.Length; $i++) {
        if ([int]$line[$i] -gt 127) {
            $nonAsciiCount++
        }
    }
    
    # If more than 70% of characters are non-ASCII and line is long, likely corrupted
    if ($line.Length -gt 20 -and $nonAsciiCount / $line.Length -gt 0.7) {
        Write-Host "Skipping corrupted line: $($line.Substring(0, [Math]::Min(50, $line.Length)))..." -ForegroundColor Red
        continue
    }
    
    $cleanLines += $line
}

$finalContent = $cleanLines -join "`n"

# Save cleaned file
Write-Host "[4] Saving cleaned file..." -ForegroundColor Yellow
[System.IO.File]::WriteAllText($LogFile, $finalContent, [System.Text.Encoding]::UTF8)

# Create clean summary function
Write-Host "[5] Creating summary function..." -ForegroundColor Yellow
$summaryFunction = @'
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

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
'@

[System.IO.File]::WriteAllText("WorkSummary_Clean.ps1", $summaryFunction, [System.Text.Encoding]::UTF8)

Write-Host "=== Process Complete ===" -ForegroundColor Green
Write-Host "Backup file: $BackupFile" -ForegroundColor Cyan
Write-Host "Summary script: WorkSummary_Clean.ps1" -ForegroundColor Cyan

# Test the function
Write-Host "[6] Testing summary function..." -ForegroundColor Yellow
. .\WorkSummary_Clean.ps1
Add-WorkSummary -Input "Encoding cleanup test" -Output "Clean encoding script completed successfully" 