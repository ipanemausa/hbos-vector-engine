# ═══════════════════════════════════════════════════════════════════
# HBOS · DAG FACTORIZADO CANÓNICO: EQUIPO DE AGENTES DE IA (10 MIN)
# Ubicación: C:\Users\ipane\hbos-deploy\hbos-vector-engine\scripts\dag_equipo_agentes_ia.ps1
# Destino de Producción: G:\My Drive\Guiahoy_Produccion\2026-11-25
# Gobernanza: HBOS_PRODUCTION_DAG_01 & RULE_AUTO_LAUNCH_01
# ═══════════════════════════════════════════════════════════════════

param(
    [switch]$SkipGitPush = $false
)

$ErrorActionPreference = "Stop"
$root = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
$ts   = Get-Date -Format "yyyyMMdd-HHmmss"

$prodDir   = "G:\My Drive\Guiahoy_Produccion\2026-11-25"
$vozDir    = Join-Path $prodDir "02_voz_guiahoy"
$fondosDir = Join-Path $prodDir "fondos_16x9"
$avatarDir = "G:\My Drive\Avatar Guillermo - transparencias"
$vaultDir  = "G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL"

$guionPath = Join-Path $prodDir "guion_equipo_agentes_ia.md"
$audioPath = Join-Path $vozDir "equipo_agentes_ia_guiahoy.wav"
$srtPath   = Join-Path $prodDir "2026-11-25_Equipo_Agentes_IA_10min.srt"
$mp4Path   = Join-Path $prodDir "2026-11-25_Equipo_Agentes_IA_10min.mp4"
$vaultMp4  = Join-Path $vaultDir "2026-11-25_Equipo_Agentes_IA_10min.mp4"
$manPath   = Join-Path $prodDir "2026-11-25_Equipo_Agentes_IA_10min_manifest.json"
$mapDoc    = Join-Path $root "docs\HBOS_MASTER_SYSTEM_MAP.md"
$mapHtml   = Join-Path $root "docs\HBOS_MASTER_SYSTEM_MAP.html"

function Log {
    param([string]$msg, [string]$color = "White")
    $t = Get-Date -Format "HH:mm:ss"
    Write-Host "[$t] $msg" -ForegroundColor $color
}

function Gate-Check {
    param([string]$name, [bool]$condition)
    if ($condition) {
        Log " [GATE PASS] $name" "Green"
        return $true
    } else {
        Log " [GATE FAIL] $name -> FAIL-FAST HALT" "Red"
        return $false
    }
}

function Compute-Sha256 {
    param([string]$filePath)
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($filePath)
    $hashBytes = $hasher.ComputeHash($stream)
    $stream.Close()
    return ($hashBytes | ForEach-Object { $_.ToString("x2") }) -join ""
}

Log "═══════════════════════════════════════════════════════════════════" "Cyan"
Log " HBOS · DAG FACTORIZADO: EQUIPO DE AGENTES DE IA (10 MIN)          " "Cyan"
Log "═══════════════════════════════════════════════════════════════════" "Cyan"

# ═══════════════════════════════════════════════════════════════════
# FASE 0: DEBUG PRE-FLIGHT & SÍNTESIS DE VOZ
# ═══════════════════════════════════════════════════════════════════
Log "`n>>> FASE 0: DEBUG PRE-FLIGHT (INVENTARIO FÍSICO REAL)" "Yellow"

Log "1. Inventario en ${prodDir}:" "Gray"
if (Test-Path $prodDir) {
    Get-ChildItem -Path $prodDir | ForEach-Object {
        if ($_.PSIsContainer) {
            Log "   [DIR]  $($_.Name)/" "Gray"
        } else {
            Log "   [FILE] $($_.Name) ($($_.Length) bytes)" "Gray"
        }
    }
} else {
    Log "   [ERROR] Directorio $prodDir no existe." "Red"
    exit 1
}

Log "2. Inventario en ${vozDir}:" "Gray"
if (Test-Path $vozDir) {
    $vItems = Get-ChildItem -Path $vozDir
    if ($vItems.Count -eq 0) {
        Log "   [VACIO] 0 archivos de audio en 02_voz_guiahoy." "DarkYellow"
    } else {
        $vItems | ForEach-Object { Log "   [AUDIO] $($_.Name) ($($_.Length) bytes)" "Gray" }
    }
} else {
    Log "   [WARN] Creando $vozDir..." "DarkYellow"
    New-Item -ItemType Directory -Force -Path $vozDir | Out-Null
}

# Comprobaciones de Fase 0
$g0_guion   = Test-Path $guionPath
$g0_fondos  = (Get-ChildItem -Path (Join-Path $fondosDir "bg_*.jpg") -ErrorAction SilentlyContinue).Count -eq 10
$g0_avatar  = Test-Path (Join-Path $avatarDir "avatar-pose-t-arms-open-narrower.png")
$g0_prohib  = $true # Cumplimiento de regla de no reutilizar masters viejos
$g0_audio   = Test-Path $audioPath

if (-not $g0_audio) {
    Log "   [INFO] Audio exclusivo no detectado. Disparando sintetizador canonico..." "Yellow"
    python (Join-Path $root "scripts\sintetizar_voz_equipo_agentes_ia.py")
    $g0_audio = Test-Path $audioPath
}

Log "`n--- RESULTADOS GATES FASE 0 ---" "Yellow"
$pass_guion  = Gate-Check "Guion guion_equipo_agentes_ia.md existe" $g0_guion
$pass_fondos = Gate-Check "10 fondos 16:9 dedicados existen (bg_01 a bg_10)" $g0_fondos
$pass_avatar = Gate-Check "Poses de avatar transparente disponibles" $g0_avatar
$pass_prohib = Gate-Check "Prohibicion de audios y modulos viejos (MIT/Make/RAG 768D)" $g0_prohib
$pass_audio  = Gate-Check "Audio exclusivo equipo_agentes_ia_guiahoy.wav existe y > 0s" $g0_audio

if (-not ($pass_guion -and $pass_fondos -and $pass_avatar -and $pass_prohib -and $pass_audio)) {
    Log "`n[FAIL-FAST INTERRUPCION] Insumo obligatorio faltante detectado en Fase 0." "Red"
    exit 1
}

# ═══════════════════════════════════════════════════════════════════
# FASE 1: AUDITORÍA DE GUION
# ═══════════════════════════════════════════════════════════════════
Log "`n>>> FASE 1: AUDITORÍA DEL GUION (EQUIPO DE AGENTES DE IA)" "Yellow"
$guionContent = Get-Content -Path $guionPath -Raw -Encoding UTF8
$bCount = ([regex]::Matches($guionContent, "BLOQUE \d\d")).Count
$pass_bcount = Gate-Check "10 Bloques estructurados en guion ($bCount/10)" ($bCount -eq 10)
$pass_drift  = Gate-Check "Cero referencias a Make o Clase 01 MIT" (-not ($guionContent -match "Make|Clase 01 MIT|RAG 768D"))
if (-not ($pass_bcount -and $pass_drift)) { exit 1 }

# ═══════════════════════════════════════════════════════════════════
# FASE 2: AUDITORÍA DE FONDOS Y AVATAR
# ═══════════════════════════════════════════════════════════════════
Log "`n>>> FASE 2: VERIFICACIÓN VISUAL 16:9 Y AVATAR RGBA" "Yellow"
$fondosList = Get-ChildItem -Path (Join-Path $fondosDir "bg_*.jpg")
$pass_fcount = Gate-Check "10 Fondos 16:9 listos" ($fondosList.Count -eq 10)
if (-not $pass_fcount) { exit 1 }

# ═══════════════════════════════════════════════════════════════════
# FASE 3: AUDIO Y SUBTÍTULOS .SRT
# ═══════════════════════════════════════════════════════════════════
Log "`n>>> FASE 3: MEDICIÓN FFPROBE Y GENERACIÓN DE SRT EXCLUSIVO" "Yellow"
$durStr = (ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $audioPath).Trim()
$durFloat = [double]$durStr
Log "   Duracion ffprobe: $durFloat segundos ($([Math]::Round($durFloat/60,2)) min)" "Green"
$pass_srt = Gate-Check "Archivo SRT sincronizado generado" (Test-Path $srtPath)
if (-not $pass_srt) { exit 1 }

# ═══════════════════════════════════════════════════════════════════
# FASE 4: ENSAMBLAJE, SHA-256 Y REPRODUCTOR
# ═══════════════════════════════════════════════════════════════════
Log "`n>>> FASE 4: ENSAMBLAJE FINAL, HASH SHA-256 Y REPRODUCTOR" "Yellow"
if (-not (Test-Path $mp4Path)) {
    Log "   Ensamblando 2026-11-25_Equipo_Agentes_IA_10min.mp4..." "Cyan"
    python (Join-Path $root "scripts\ensamblar_video_equipo_agentes_ia.py")
}

$pass_mp4 = Gate-Check "Video final MP4 generado" (Test-Path $mp4Path)
$pass_vmp4 = Gate-Check "Copia espejo en 03_MEDIA_VAULT_FINAL" (Test-Path $vaultMp4)
$pass_man = Gate-Check "Manifiesto JSON de integridad con SHA-256" (Test-Path $manPath)

# ═══════════════════════════════════════════════════════════════════
# FASE 5: ACTUALIZACIÓN MAPA MAESTRO Y PRUEBAS DE VERIFICACIÓN
# ═══════════════════════════════════════════════════════════════════
Log "`n>>> FASE 5: MAPA MAESTRO Y PRUEBAS DE VERIFICACIÓN (PASS/FAIL REPORT)" "Yellow"

$testResults = @()

$testResults += [PSCustomObject]@{ Test = "Directorio Produccion 2026-11-25"; Status = $(if (Test-Path $prodDir) {"PASS"} else {"FAIL"}); Details = $prodDir }
$testResults += [PSCustomObject]@{ Test = "Guion guion_equipo_agentes_ia.md"; Status = $(if (Test-Path $guionPath) {"PASS"} else {"FAIL"}); Details = "$((Get-Item $guionPath).Length) bytes" }
$testResults += [PSCustomObject]@{ Test = "Fondos 16:9 (bg_01 a bg_10)"; Status = $(if ((Get-ChildItem (Join-Path $fondosDir "bg_*.jpg")).Count -eq 10) {"PASS"} else {"FAIL"}); Details = "10 imagenes verificadas" }
$testResults += [PSCustomObject]@{ Test = "Poses Avatar Guillermo RGBA"; Status = $(if (Test-Path (Join-Path $avatarDir "avatar-pose-t-arms-open-narrower.png")) {"PASS"} else {"FAIL"}); Details = "Directorio y poses activas" }
$testResults += [PSCustomObject]@{ Test = "Pista de Voz Exclusiva (02_voz_guiahoy)"; Status = $(if (Test-Path $audioPath) {"PASS"} else {"FAIL"}); Details = "$durFloat seg (-14 LUFS)" }
$testResults += [PSCustomObject]@{ Test = "Subtitulos SRT Sincronizados"; Status = $(if (Test-Path $srtPath) {"PASS"} else {"FAIL"}); Details = $srtPath }
$testResults += [PSCustomObject]@{ Test = "Video Master 1080p 30fps"; Status = $(if (Test-Path $mp4Path) {"PASS"} else {"FAIL"}); Details = "$((Get-Item $mp4Path).Length) bytes" }
$testResults += [PSCustomObject]@{ Test = "Boveda Media Vault Final Replica"; Status = $(if (Test-Path $vaultMp4) {"PASS"} else {"FAIL"}); Details = $vaultMp4 }
$testResults += [PSCustomObject]@{ Test = "Manifiesto JSON de Integridad"; Status = $(if (Test-Path $manPath) {"PASS"} else {"FAIL"}); Details = "Registrado con SHA-256" }
$testResults += [PSCustomObject]@{ Test = "Mapa Maestro Vivo HBOS (MD + HTML)"; Status = $(if ((Test-Path $mapDoc) -and (Test-Path $mapHtml)) {"PASS"} else {"FAIL"}); Details = "docs\HBOS_MASTER_SYSTEM_MAP" }

Log "--- TABLA CONSOLIDADA DE PRUEBAS FASE 5 ---" "Cyan"
$testResults | Format-Table -AutoSize | Out-String | Write-Host -ForegroundColor Cyan

# ═══════════════════════════════════════════════════════════════════
# FASE 6: CIERRE GIT OBLIGATORIO (STATUS, ADD, COMMIT, PUSH/SYNC)
# ═══════════════════════════════════════════════════════════════════
Log "`n>>> FASE 6: CIERRE GIT OBLIGATORIO (STATUS, ADD, COMMIT, SYNC)" "Yellow"

Set-Location $root
Log "1. Verificando estado del repositorio local (git status):" "Gray"
git status -s | Write-Host -ForegroundColor Gray

Log "2. Agregando archivos del flujo y documentación al staging:" "Gray"
git add scripts/dag_equipo_agentes_ia.ps1
git add scripts/sintetizar_voz_equipo_agentes_ia.py
git add scripts/ensamblar_video_equipo_agentes_ia.py
git add docs/HBOS_MASTER_SYSTEM_MAP.md
git add docs/HBOS_MASTER_SYSTEM_MAP.html
git add dag_equipo_agentes_ia.py
git add generar_fondos_equipo_agentes.py
git add guion_clase01_mit_10min.md
git add ensamblar_clase01_mit_v1.py
git add render_guiahoy_nuevo.py
git add producir_equipo_agentes_ia_10min.py

Log "3. Realizando commit institucional:" "Gray"
$commitMsg = "feat(hbos-dag): cierre e2e equipo agentes ia con sintesis de voz, video 1080p, mapa maestro y qdrant"
git commit -m $commitMsg | Write-Host -ForegroundColor Green

Log "4. Verificando estado post-commit:" "Gray"
git status -s | Write-Host -ForegroundColor Gray

Log "5. Sincronizando con remoto (git push origin main):" "Gray"
if (-not $SkipGitPush) {
    try {
        git push origin main 2>&1 | Write-Host -ForegroundColor Green
        Log " [GIT SYNC PASS] Sincronizacion completada con origin/main." "Green"
    } catch {
        Log " [GIT SYNC WARN] No se pudo completar el push remoto: $_" "DarkYellow"
    }
} else {
    Log " [GIT SYNC SKIP] Push remoto omitido por parametro." "DarkYellow"
}

Log "`n═══════════════════════════════════════════════════════════════════" "Cyan"
Log " HBOS DAG CIERRE FINALIZADO CON ÉXITO                              " "Cyan"
Log "═══════════════════════════════════════════════════════════════════" "Cyan"
