param([switch]$Silencioso)
$root = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
$opsFile = Join-Path $root "_OPS.md"
$gitOp = $null
try {
    $log = git -C $root log --all --grep="op=" --format="%s" 2>$null | Select-Object -First 1
    if ($log -match "op=(\d+)") { $gitOp = [int]$Matches[1] }
} catch { }
$fileOp = $null
if (Test-Path $opsFile) {
    $c = Get-Content $opsFile -Raw
    if ($c -match "op=(\d+)") { $fileOp = [int]$Matches[1] }
}
$op = if ($fileOp -and $gitOp) { [Math]::Max($fileOp, $gitOp) } elseif ($fileOp) { $fileOp } else { $gitOp }
if ($Silencioso) { return $op }
if ($op) { Write-Host "[HBOS] Op real: $op (git=$gitOp file=$fileOp)" -ForegroundColor Green } else { Write-Host "[HBOS] Op no disponible" -ForegroundColor Yellow }
