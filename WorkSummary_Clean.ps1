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

# $timestamp (Cursor - 椤圭洰锛?projectName)

## 馃摜 杈撳叆锛?
$Input

## 馃摛 杈撳嚭锛?
$Output

---
"@
    
    [System.IO.File]::AppendAllText($logFile, $logEntry, [System.Text.Encoding]::UTF8)
    Write-Host "Summary added successfully" -ForegroundColor Green
}