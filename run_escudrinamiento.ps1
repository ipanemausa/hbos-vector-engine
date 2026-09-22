# ============================================================
# HBOS - ESCUDRINAMIENTO TOTAL - OMNIROUTER + API PROPIA + TODO
# ============================================================
$ErrorActionPreference = "Continue"
$sep = "=" * 78
$base = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
$brainDir = "C:\Users\ipane\.gemini\antigravity-ide\brain"
$appData = "$env:APPDATA\FreeLLMAPI"
$dbPath = "$appData\freeapi.db"
$py = "C:\Users\ipane\AppData\Local\Programs\Python\Python313\python.exe"
$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
$reporte = Join-Path $base "_ESCUDRIÑAMIENTO_$fecha.md"

Set-Location $base

function L {
    param([string]$msg, [string]$color = "Gray")
    Write-Host $msg -ForegroundColor $color
    Add-Content -Path $reporte -Value $msg -Encoding utf8
}

function Section {
    param([string]$titulo)
    L ""
    L $sep "Cyan"
    L $titulo "Cyan"
    L $sep "Cyan"
}

L "# HBOS - ESCUDRINAMIENTO TOTAL"
L "**Fecha:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
L "**Reporte:** ``$reporte``"
L ""

# ============================================================
# SECCION 1 - OMNIROUTER
# ============================================================
Section "1. OMNIROUTER"

L "## 1. OMNIROUTER"
L ""

# 1.1 - Archivos con "omni" en el nombre (disco C:)
L "### 1.1 - Archivos con 'omni' en el nombre"
$omniFiles = @()
foreach ($dir in @("C:\Users\ipane", "C:\Program Files", "C:\Program Files (x86)")) {
    if (Test-Path $dir) {
        $omniFiles += Get-ChildItem -Path "$dir\*" -Recurse -Depth 4 -Filter "*omni*" -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch "node_modules|\.git|Windows|Temp" }
    }
}
$omniFiles | Select-Object FullName, Length, LastWriteTime -Unique |
    Sort-Object FullName | Format-Table -AutoSize | Out-String | ForEach-Object { L $_ }

# 1.2 - Menciones en el repo
L "### 1.2 - Menciones a 'omni' en el repo"
$omniRefs = Get-ChildItem $base -Include "*.py","*.md","*.json","*.js","*.txt","*.ps1" -Recurse -ErrorAction SilentlyContinue |
    Select-String "omni" -ErrorAction SilentlyContinue
L "  Total: $($omniRefs.Count) menciones"
$omniRefs | Select-Object -First 30 | ForEach-Object {
    L "  $($_.Filename):$($_.LineNumber)"
    $line = $_.Line.Trim()
    if ($line.Length -gt 130) { $line = $line.Substring(0,130) + "..." }
    L "    $line"
}

# 1.3 - Menciones en brain
L ""
L "### 1.3 - Menciones a 'omni' en Antigravity brain"
if (Test-Path $brainDir) {
    $brainHits = Get-ChildItem $brainDir -Filter "*.jsonl" -Recurse -ErrorAction SilentlyContinue |
        Select-String "omnirouter|omni.?router" -ErrorAction SilentlyContinue
    L "  Total: $($brainHits.Count) menciones"
    $brainHits | Select-Object -First 10 | ForEach-Object {
        L "  $($_.Filename):$($_.LineNumber)"
        $line = $_.Line.Trim()
        if ($line.Length -gt 200) { $line = $line.Substring(0,200) + "..." }
        L "    $line"
    }
}

# 1.4 - Esta corriendo?
L ""
L "### 1.4 - Puertos en escucha"
$ports = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalPort -gt 1024 -and $_.LocalPort -lt 10000 } |
    Sort-Object LocalPort -Unique
foreach ($p in $ports) {
    $proc = Get-Process -Id $p.OwningProcess -ErrorAction SilentlyContinue
    L "  :$($p.LocalPort) -> $($proc.ProcessName) (PID $($p.OwningProcess))"
}

# 1.5 - Docker
L ""
L "### 1.5 - Docker Contenedores"
$dockerPs = docker ps -a --format "{{.Names}} | {{.Image}} | {{.Status}} | {{.Ports}}" 2>&1
$dockerPs | ForEach-Object { L "  $_" }

# ============================================================
# SECCION 2 - API PROPIA / SUB-KEYS
# ============================================================
Section "2. API PROPIA / SUB-KEYS"

L "## 2. API PROPIA / SUB-KEYS"
L ""

# 2.1 - Tablas de la DB relacionadas
L "### 2.1 - Tablas de freeapi.db"
$outQ1 = & $py (Join-Path $base "escudri_q1_db.py") 2>&1
$outQ1 | ForEach-Object { L "  $_" }

# 2.2 - Settings de la DB
L ""
L "### 2.2 - Settings clave"
$outQ2 = & $py (Join-Path $base "escudri_q2_settings.py") 2>&1
$outQ2 | ForEach-Object { L "  $_" }

# 2.3 - Referencias en repo
L ""
L "### 2.3 - Menciones de sub-keys / API propia en repo"
$apiRefs = Get-ChildItem $base -Include "*.py","*.md","*.json","*.txt" -Recurse -ErrorAction SilentlyContinue |
    Select-String "api.?propia|sub.?key|client.?profile|create.?client|api.?hija|unified.?key" -ErrorAction SilentlyContinue
L "  Total: $($apiRefs.Count)"
$apiRefs | Select-Object -First 20 | ForEach-Object {
    L "  $($_.Filename):$($_.LineNumber)"
    $line = $_.Line.Trim()
    if ($line.Length -gt 130) { $line = $line.Substring(0,130) + "..." }
    L "    $line"
}

# ============================================================
# SECCION 3 - ENDPOINTS Y CONFIG DE LA APP
# ============================================================
Section "3. ENDPOINTS Y CONFIG DE LA APP"

L "## 3. ENDPOINTS DE LA APP"
L ""

# 3.1 - Endpoints disponibles
L "### 3.1 - Endpoints probados"
$endpoints = @("models", "providers", "keys", "settings", "clients", "tokens", "url_tokens", "profiles", "agents", "analytics", "config", "health", "status")
foreach ($ep in $endpoints) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:3001/api/$ep" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        L "  [OK] /api/$ep -> $($r.StatusCode)"
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        if ($code -eq 404) {
            L "  [--] /api/$ep -> 404"
        } else {
            L "  [!] /api/$ep -> $code"
        }
    }
}

# 3.2 - Buscar en el codigo de la app (server.mjs)
L ""
L "### 3.2 - Endpoints en server.mjs"
$outQ3 = & $py (Join-Path $base "escudri_q3_routes.py") 2>&1
$outQ3 | ForEach-Object { L "  $_" }

# 3.3 - PLATFORMS enum
L ""
L "### 3.3 - Enum PLATFORMS"
$outQ4 = & $py (Join-Path $base "escudri_q4_platforms.py") 2>&1
$outQ4 | ForEach-Object { L "  $_" }

# ============================================================
# SECCION 4 - HISTORIAL DE ANTIGRAVITY
# ============================================================
Section "4. HISTORIAL DE ANTIGRAVITY"

L "## 4. HISTORIAL DE ANTIGRAVITY"
L ""

if (Test-Path $brainDir) {
    L "### 4.1 - Conversaciones recientes"
    Get-ChildItem $brainDir -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 10 | ForEach-Object {
        L "  $($_.Name) . $($_.LastWriteTime)"
    }

    L ""
    L "### 4.2 - Terminos clave buscados"
    foreach ($term in @("omnirouter", "api propia", "sub-key", "client_profile", "url_token", "unified_key", "create api", "crear api")) {
        $hits = Get-ChildItem $brainDir -Filter "*.jsonl" -Recurse -ErrorAction SilentlyContinue |
            Select-String $term -SimpleMatch -ErrorAction SilentlyContinue
        L "  '$term' -> $($hits.Count) menciones"
    }
}

# ============================================================
# SECCION 5 - GIT LOG
# ============================================================
Section "5. GIT LOG"

L "## 5. GIT LOG"
L ""
L "### 5.1 - Commits relacionados"
git --no-pager log --all --oneline --grep="api" --grep="key" --grep="client" --grep="token" --grep="omni" -i 2>&1 |
    Select-Object -First 30 | ForEach-Object { L "  $_" }

L ""
L "### 5.2 - Archivos cambiados en ultimos 20 commits"
git --no-pager log --name-status --oneline -20 2>&1 | Select-Object -First 60 | ForEach-Object { L "  $_" }

# ============================================================
# RESUMEN
# ============================================================
Section "RESUMEN"

L "## RESUMEN"
L ""
L "  Reporte completo: ``$reporte``"
L ""
L "  OmniRouter: ver Seccion 1"
L "  API propia: ver Seccion 2"
L "  Endpoints: ver Seccion 3"
L "  Antigravity: ver Seccion 4"
L "  Git: ver Seccion 5"
L ""
L "**FIN ESCUDRINAMIENTO**"

Write-Host "`n$sep" -ForegroundColor Green
Write-Host "ESCUDRINAMIENTO COMPLETADO" -ForegroundColor Green
Write-Host "Reporte: $reporte" -ForegroundColor Green
Write-Host "$sep" -ForegroundColor Green
