# ============================================================
# HBOS · HOOK DE ENTRADA · op=307
# Auto-generado. No editar a mano.
# Detecta input crudo, aplica estrategia emergente.
# ============================================================

$global:HBOS_HOOK_ACTIVO = $true
$global:HBOS_FUERZA_EMERGENTE = 0

function Test-HbosInputCrudo {
    param([string]$Line)
    if ([string]::IsNullOrWhiteSpace($Line)) { return $false }
    $patrones = @(
        "^\s*#",
        "^\s*={3,}",
        "^\s*-{3,}",
        "^\s*\*{2,}",
        "^\s*`{3,}",
        "^\s*\[[A-Z]+\]",
        "^\s*(PRIMERA|FASE|CAPA|DAG|BLOQUE|ANCLA|CIERRE)\b",
        "^\s*(por favor|puedes|quiero|necesito|dame|haz|muestra)\b"
    )
    foreach ($p in $patrones) {
        if ($Line -match $p) { return $true }
    }
    $verbosPwsh = @(
        "Get-","Set-","New-","Remove-","Copy-","Move-","Start-","Stop-",
        "Invoke-","Test-","Select-","Where-","ForEach-","Write-","Read-",
        "Out-","Import-","Export-","Convert","Join-","Split-","Measure-",
        "Compare-","Sort-","Group-","Format-","Show-","Clear-","Add-"
    )
    foreach ($v in $verbosPwsh) {
        if ($Line -match "^\s*$v") { return $false }
    }
    if ($Line -match "^\s*(\.|&|cd|ls|dir|git|python|py|node|npm|docker|pwsh)\b") { return $false }
    if ($Line -match "^\s*\$") { return $false }
    if ($Line -match "^\s*\|") { return $false }
    if ($Line -match "^\s*\w+\s*=") { return $false }
    return $false
}

function Get-HbosEstrategiaEmergente {
    param([string]$Line, [int]$Fuerza)
    if ($Line -match "^\s*(HBOS|ANCLA|CIERRE|EMERGENCIA|FORZAR|OVERRIDE)\b") { return "FORZAR" }
    if ($Line -match "^\s*(no|stop|cancelar|abortar)\b") { return "BLOQUEA" }
    if ($Fuerza -ge 2) { return "FACTORIZA" }
    if ($Line.Length -gt 200) { return "FACTORIZA" }
    if ($Line -match "(===|```|##|\*\*)" -and $Line.Length -gt 80) { return "HIBRIDO" }
    return "BLOQUEA"
}

function hbos-factorize {
    param([Parameter(Mandatory=$true)][string]$Input)
    Write-Host "[HBOS] Factorizando: $Input" -ForegroundColor Cyan
    Write-Host "[HBOS] Enviar a FreeLLMAPI con: hbos-chat 'factoriza: $Input'" -ForegroundColor Gray
}

function hbos-force {
    param([Parameter(Mandatory=$true)][string]$Input)
    Write-Host "[HBOS] FORZANDO: $Input" -ForegroundColor Magenta
    Invoke-Expression $Input
}

# AddToHistoryHandler: marca input crudo, no lo ejecuta como comando
Set-PSReadLineOption -AddToHistoryHandler {
    param([string]$Line)
    if (Test-HbosInputCrudo -Line $Line) {
        Write-Host "[HBOS] Input crudo detectado. No ejecutado como comando." -ForegroundColor Yellow
        Write-Host "[HBOS] Usa: hbos-factorize 'tu input'  o  hbos-force 'tu input'" -ForegroundColor Yellow
        return $false
    }
    return $true
} -ErrorAction SilentlyContinue
