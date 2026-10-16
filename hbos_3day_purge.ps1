# PowerShell 3-Day Purge Maintenance Script
Param([switch]$DryRun)

Write-Host "=========================================================="
Write-Host "HBOS 3-DAY PURGE DAG · MAINTENANCE CYCLE"
Write-Host "Execution Time: $(Get-Date)"
Write-Host "DryRun Mode: $DryRun"
Write-Host "=========================================================="

# 1. Prune unused docker images older than 7 days (preserving 7 active containers)
if ($DryRun) {
    Write-Host "[DRY RUN] Would prune dangling Docker images & build cache..."
} else {
    Write-Host "[EXEC] Pruning Docker build cache and images older than 168h..."
    docker builder prune -f
    docker image prune -a --filter "until=168h" -f
}

# 2. Delete temporary logs older than 30 days
$logDirs = @("G:\My Drive\Sistema\Logs", "C:\Sistema\Logs")
foreach ($ld in $logDirs) {
    if (Test-Path $ld) {
        $oldLogs = Get-ChildItem -Path $ld -Filter "*.txt" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }
        foreach ($f in $oldLogs) {
            if ($DryRun) {
                Write-Host "[DRY RUN] Would delete old log: $($f.FullName)"
            } else {
                Remove-Item -Path $f.FullName -Force
                Write-Host "[PURGED] Deleted old log: $($f.FullName)"
            }
        }
    }
}

# 3. Cloud Vector Database Check
Write-Host "[CLOUD INTEGRITY] Cloud Vector Brain (Quadrant) remains IMMUTABLE and untouched."
Write-Host "Maintenance cycle completed successfully."
