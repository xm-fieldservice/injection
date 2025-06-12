# injection Project Log Manager
# Auto archive and size monitoring

param(
    [string]$Action = "check",
    [int]$MaxSizeMB = 1,
    [int]$KeepArchives = 12
)

$LogFile = "injection-log.md"
$MaxSizeBytes = $MaxSizeMB * 1MB

function Get-LogFileStatus {
    if (-not (Test-Path $LogFile)) {
        Write-Host "ERROR: Log file not found: $LogFile" -ForegroundColor Red
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
    
    Write-Host "Log File Status Report - injection-log.md" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor DarkGray
    Write-Host "File Size: $($status.SizeMB) MB ($($status.Size) bytes)" -ForegroundColor White
    Write-Host "Lines Count: $($status.Lines) lines" -ForegroundColor White
    Write-Host "Last Modified: $($status.LastModified)" -ForegroundColor White
    
    if ($status.NeedsArchive) {
        Write-Host "WARNING: File size exceeds $MaxSizeMB MB - Archive recommended" -ForegroundColor Yellow
    } else {
        $remaining = [math]::Round(($MaxSizeBytes - $status.Size) / 1KB, 0)
        Write-Host "OK: File size normal, can grow about $remaining KB more" -ForegroundColor Green
    }
}

function Invoke-Archive {
    $status = Get-LogFileStatus
    if (-not $status) { return }
    
    $timestamp = Get-Date -Format "yyyy-MM"
    $archiveFile = "injection-log-archive-$timestamp.md"
    
    $counter = 1
    $originalArchiveFile = $archiveFile
    while (Test-Path $archiveFile) {
        $archiveFile = $originalArchiveFile -replace ".md$", "-$counter.md"
        $counter++
    }
    
    Write-Host "Starting archive process..." -ForegroundColor Yellow
    Write-Host "Source: $LogFile ($($status.SizeMB) MB)" -ForegroundColor White
    Write-Host "Archive: $archiveFile" -ForegroundColor White
    
    try {
        Copy-Item $LogFile $archiveFile -Force
        
        $newLogHeader = @"
# injection Project Work Log

> This is the work log for injection project, recording all development processes, 
> problem solving and feature implementations.
> 
> Start Time: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
> Previous logs archived to: $archiveFile
> 
> ## Log Format Guidelines
> - Use timestamp headers after each work session
> - Use interactive block format to record input/output
> - Maintain UTF-8 encoding

---

"@
        
        $newLogHeader | Out-File $LogFile -Encoding UTF8
        
        Write-Host "SUCCESS: Archive completed!" -ForegroundColor Green
        Write-Host "Archive file: $archiveFile ($($status.SizeMB) MB)" -ForegroundColor Cyan
        Write-Host "New log file created" -ForegroundColor Cyan
        
        $archives = Get-ChildItem "injection-log-archive-*.md" | Sort-Object LastWriteTime -Descending
        if ($archives.Count -gt 0) {
            Write-Host "`nArchive History:" -ForegroundColor Cyan
            $archives | ForEach-Object {
                $sizeMB = [math]::Round($_.Length / 1MB, 2)
                Write-Host "  $($_.Name) - $sizeMB MB - $($_.LastWriteTime.ToString('yyyy-MM-dd'))" -ForegroundColor Gray
            }
        }
        
    } catch {
        Write-Host "ERROR: Archive failed - $($_.Exception.Message)" -ForegroundColor Red
    }
}

switch ($Action.ToLower()) {
    "check" {
        Show-LogStatus
    }
    "archive" {
        Show-LogStatus
        Write-Host ""
        Invoke-Archive
    }
    default {
        Write-Host "Usage:" -ForegroundColor Cyan
        Write-Host "  .\LogManager_Simple.ps1 check     # Check log status" -ForegroundColor White
        Write-Host "  .\LogManager_Simple.ps1 archive   # Execute archive" -ForegroundColor White
    }
} 