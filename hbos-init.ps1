# HBOS · Init portable · corre desde cualquier punto de entrada
param([switch]$Silencioso)
function Get-HbosRoot {
    $d = Get-Location
    while ($d -and $d.Path -ne $d.Root.Path) {
        if (Test-Path (Join-Path $d.Path "hbos_run.ps1")) { return $d.Path }
        $d = $d.Parent
    }
    foreach ($f in @("C:\Users\ipane\hbos-deploy\hbos-vector-engine", "$env:USERPROFILE\hbos-deploy\hbos-vector-engine")) {
        if (Test-Path (Join-Path $f "hbos_run.ps1")) { return $f }
    }
    return $null
}
$root = Get-HbosRoot
if (-not $root) { Write-Host "[HBOS] ERROR: raiz no encontrada" -ForegroundColor Red; return }
$global:HBOS_ROOT = $root
Set-Location $root
. (Join-Path $root "hbos_run.ps1")
. (Join-Path $root "hbos_funciones.ps1")
$ops = & (Join-Path $root "hbos_ops.ps1") -Silencioso
$commit = (git -C $root log -1 --format="%h" 2>$null)
$global:HBOS_OPS = $ops
$global:HBOS_COMMIT = $commit
if (-not $Silencioso) {
    Write-Host "[HBOS] Raiz: $root" -ForegroundColor Green
    hbos-estado
    Write-Host "[HBOS] Op: $ops | Commit: $commit" -ForegroundColor Gray
    Write-Host "[HBOS] Funciones: hbos-run, hbos-chat, hbos-estado, hbos-ops" -ForegroundColor Gray
}
