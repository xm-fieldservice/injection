function Add-WorkSummary {
    param(
        [string]$Input,
        [string]$Output,
        [string]$ProjectName = "injection"
    )
    
    $PSDefaultParameterValues['*:Encoding'] = 'UTF8'
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    $LogEntry = @"

# $Timestamp (Cursor - 椤圭洰锛?ProjectName)

## 馃摜 杈撳叆锛?
$Input

## 馃摛 杈撳嚭锛?
$Output

---

"@
    
    Add-Content -Path "injection-log.md" -Value $LogEntry -Encoding UTF8
    Write-Host "鉁?宸ヤ綔鎬荤粨宸茶褰? -ForegroundColor Green
}

# 浣跨敤绀轰緥
# Add-WorkSummary -Input "鐢ㄦ埛闂" -Output "宸ヤ綔鎬荤粨"
