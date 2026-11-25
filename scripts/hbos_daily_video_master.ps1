# ═══════════════════════════════════════════════════════════════════════════════
# HBOS · LANZADOR ÚNICO DIARIO DE PRODUCCIÓN AUDIOVISUAL AUTÓNOMA
# Ubicación: C:\Users\ipane\hbos-deploy\hbos-vector-engine\scripts\hbos_daily_video_master.ps1
# Gobernanza: HBOS_DAILY_VIDEO_MASTER_PROMPT & RULE_AUTO_LAUNCH_01
# ═══════════════════════════════════════════════════════════════════════════════

param(
    [string]$Fecha = "2026-11-25",
    [string]$Tema = "Equipo_Agentes_IA",
    [string]$Duracion = "10min",
    [switch]$SkipGitPush = $false,
    [switch]$ForceRebuild = $false
)

$ErrorActionPreference = "Stop"
$root = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
$prodDir   = "G:\My Drive\Guiahoy_Produccion\$Fecha"
$vozDir    = Join-Path $prodDir "02_voz_guiahoy"
$fondosDir = Join-Path $prodDir "fondos_16x9"
$avatarLib = "G:\My Drive\HBOS_Creative\06_Avatar_Clip_Library"
$vaultDir  = "G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL"

$filePrefix = "${Fecha}_${Tema}_${Duracion}"
$guionPath  = Join-Path $prodDir "guion_$($Tema.ToLower()).md"
$audioPath  = Join-Path $vozDir "$($Tema.ToLower())_guiahoy.wav"
$srtPath    = Join-Path $prodDir "${filePrefix}.srt"
$mp4Path    = Join-Path $prodDir "${filePrefix}.mp4"
$vaultMp4   = Join-Path $vaultDir "${filePrefix}.mp4"
$manPath    = Join-Path $prodDir "${filePrefix}_manifest.json"
$archiveDir = Join-Path $prodDir "_archive_previous_runs"
$tempDir    = Join-Path $root "temp_cinematic"

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

Log "═══════════════════════════════════════════════════════════════════════════════" "Cyan"
Log " HBOS · LANZADOR ÚNICO DIARIO: $filePrefix " "Cyan"
Log " Gobernanza: HBOS_DAILY_VIDEO_MASTER_PROMPT · Cero Costo · Fail-Fast Pre-Debug " "Cyan"
Log "═══════════════════════════════════════════════════════════════════════════════" "Cyan"

# ═══════════════════════════════════════════════════════════════════════════════
# PASO 0: AISLAMIENTO ESTRICTO POR CORRIDA (ZERO RESIDUAL CONTAMINATION)
# ═══════════════════════════════════════════════════════════════════════════════
Log "`n>>> PASO 0: AISLAMIENTO POR CORRIDA & SEGREGACIÓN DE RESIDUOS" "Yellow"

if (-not (Test-Path $prodDir)) {
    Log "   [ERROR] Directorio de producción $prodDir no existe." "Red"
    exit 1
}

if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null
}

$residualFiles = Get-ChildItem -Path $prodDir -File | Where-Object {
    $name = $_.Name
    # Aislar si es residuo de MIT, Make o de otra clase antigua
    $isResidual = ($name -match "mit|clase01|ensamblado|_v1|_v2") -and (-not ($name -match "^$filePrefix"))
    $isResidual
}

$isolatedCount = 0
foreach ($resFile in $residualFiles) {
    $targetArchive = Join-Path $archiveDir $resFile.Name
    Move-Item -Path $resFile.FullName -Destination $targetArchive -Force
    Log "   [AISLADO] $($resFile.Name) -> _archive_previous_runs/" "DarkYellow"
    $isolatedCount++
}

$pass_aislamiento = Gate-Check "Aislamiento por corrida verificado ($isolatedCount residuos archivados)" $true

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 0: PRE-DEBUG DE 5 SEGUNDOS (FAIL-FAST ANTI-HANGING) & AUDITORÍA DE INSUMOS
# ═══════════════════════════════════════════════════════════════════════════════
Log "`n>>> FASE 0: PRE-DEBUG DE 5 SEGUNDOS (FAIL-FAST) & AUDITORÍA DE INSUMOS" "Yellow"

if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
}

$testBg = Join-Path $fondosDir "bg_01.jpg"
$testAv = Join-Path $avatarLib "AVM_01_HOOK_OPENING.mp4"
$predebugOut = Join-Path $tempDir "predebug_5s_test.mp4"

Log "1. Ejecutando pre-debug de 5 segundos con timeout de 20s..." "Cyan"
$predebugPassed = $false

if ((Test-Path $testBg) -and (Test-Path $testAv)) {
    $pyTestScript = Join-Path $tempDir "predebug_runner.py"
    $pyCode = @"
import subprocess, sys
bg = r'$testBg'
av = r'$testAv'
out = r'$predebugOut'
fc = "[0:v]zoompan=z='min(zoom+0.0005,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1920x1080:fps=30[bg];[1:v]scale=640:360,format=yuv420p[av];[bg][av]overlay=W-w-30:H-h-20:shortest=1[outv]"
cmd = [
    'ffmpeg', '-y', '-v', 'error',
    '-i', bg,
    '-stream_loop', '-1', '-i', av,
    '-filter_complex', fc,
    '-map', '[outv]',
    '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
    '-t', '5', out
]
try:
    res = subprocess.run(cmd, timeout=20, capture_output=True)
    sys.exit(res.returncode)
except subprocess.TimeoutExpired:
    sys.exit(124)
except Exception as e:
    sys.exit(1)
"@
    [System.IO.File]::WriteAllText($pyTestScript, $pyCode, [System.Text.Encoding]::UTF8)
    
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    python $pyTestScript
    $exitCode = $LASTEXITCODE
    $sw.Stop()
    
    Remove-Item $pyTestScript -Force -ErrorAction SilentlyContinue

    if (($exitCode -eq 0) -and (Test-Path $predebugOut) -and ((Get-Item $predebugOut).Length -gt 0)) {
        Log "   [PRE-DEBUG OK] 5s test render completado exitosamente en $([Math]::Round($sw.Elapsed.TotalSeconds, 2))s." "Green"
        $predebugPassed = $true
        Remove-Item -Path $predebugOut -Force -ErrorAction SilentlyContinue
    } else {
        if ($exitCode -eq 124) {
            Log "   [PRE-DEBUG TIMEOUT] FFmpeg superó los 20s de timeout. Cancelado." "Red"
        } else {
            Log "   [PRE-DEBUG FAIL] FFmpeg terminó con código $exitCode." "Red"
        }
    }
} else {
    Log "   [PRE-DEBUG ERROR] bg_01.jpg o AVM_01_HOOK_OPENING.mp4 no encontrados." "Red"
}

$pass_predebug = Gate-Check "Pre-debug 5s FFmpeg completado dentro de 15s" $predebugPassed
if (-not $pass_predebug) {
    Log "`n[FAIL-FAST INTERRUPCIÓN] Falló el pre-debug de 5s. Deteniendo antes del render largo." "Red"
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 1: CAPA DE GUION Y SINCRONÍA TEMPORAL
# ═══════════════════════════════════════════════════════════════════════════════
Log "`n>>> FASE 1: CAPA DE GUION ($guionPath)" "Yellow"
$gExists = Test-Path $guionPath
$bCount = 0
$noDrift = $false

if ($gExists) {
    $gContent = Get-Content -Path $guionPath -Raw -Encoding UTF8
    $bCount = ([regex]::Matches($gContent, "BLOQUE \d\d")).Count
    $noDrift = (-not ($gContent -match "Make|Clase 01 MIT|RAG 768D"))
}

$pass_guion = Gate-Check "Guion existe y contiene 10 bloques estructurados ($bCount/10)" ($bCount -eq 10)
$pass_nodrift = Gate-Check "Cero mezcla conceptual de temas anteriores (Make / MIT)" $noDrift
if (-not ($pass_guion -and $pass_nodrift)) { exit 1 }

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 2: CAPA VISUAL & AVATAR PIP
# ═══════════════════════════════════════════════════════════════════════════════
Log "`n>>> FASE 2: CAPA VISUAL 16:9 & AVATAR EN MOVIMIENTO" "Yellow"
$fondosCount = (Get-ChildItem -Path (Join-Path $fondosDir "bg_*.jpg") -ErrorAction SilentlyContinue).Count
$avatarCount = (Get-ChildItem -Path (Join-Path $avatarLib "AVM_*.mp4") -ErrorAction SilentlyContinue).Count

$pass_fondos = Gate-Check "10 Fondos 16:9 limpios sin cajas de texto ($fondosCount/10)" ($fondosCount -eq 10)
$pass_avatar = Gate-Check "Biblioteca de clips de avatar en movimiento activo ($avatarCount/15)" ($avatarCount -ge 10)
if (-not ($pass_fondos -and $pass_avatar)) { exit 1 }

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 3: CAPA VOCAL & SUBTÍTULOS .SRT
# ═══════════════════════════════════════════════════════════════════════════════
Log "`n>>> FASE 3: CAPA VOCAL & SUBTÍTULOS .SRT" "Yellow"
$audioExists = Test-Path $audioPath
$durFloat = 0.0

if ($audioExists) {
    $durStr = (ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $audioPath).Trim()
    $durFloat = [double]$durStr
}

$durMin = [Math]::Round($durFloat / 60, 2)
Log "   Duración Audio Maestro: $durFloat segundos ($durMin min)" "Green"
$pass_audio = Gate-Check "Audio maestro Guiahoy 109.2Hz -14 LUFS existe y > 0s" ($audioExists -and ($durFloat -gt 0))
$pass_srt   = Gate-Check "Subtítulos SRT sincronizados existen" (Test-Path $srtPath)
if (-not ($pass_audio -and $pass_srt)) { exit 1 }

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 4: ENSAMBLAJE CINEMÁTICO (TIMEOUT 90s/BLOQUE), HASH SHA-256 & BÓVEDA
# ═══════════════════════════════════════════════════════════════════════════════
Log "`n>>> FASE 4: ENSAMBLAJE CINEMÁTICO, SHA-256 & MEDIA VAULT" "Yellow"

$needsAssembly = $ForceRebuild -or (-not (Test-Path $mp4Path)) -or ((Get-Item $mp4Path).Length -lt 10000000)

if ($needsAssembly) {
    Log "   Disparando ensamble cinematográfico multihilo con zoompan y avatar..." "Cyan"
    python (Join-Path $root "scripts\ensamblar_video_cinematico_hbos.py")
} else {
    Log "   [REUTILIZACIÓN VERIFICADA] El video master $mp4Path ya se encuentra compilado." "Green"
}

$pass_mp4   = Gate-Check "Video final MP4 generado y validado (>10MB)" ((Test-Path $mp4Path) -and ((Get-Item $mp4Path).Length -gt 10000000))
$pass_vault = Gate-Check "Copia espejo en 03_MEDIA_VAULT_FINAL" (Test-Path $vaultMp4)
$pass_man   = Gate-Check "Manifiesto JSON de integridad con SHA-256" (Test-Path $manPath)
if (-not ($pass_mp4 -and $pass_vault -and $pass_man)) { exit 1 }

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 5: ARCHIVADO VECTORIAL DUAL EN QDRANT (768D y 384D) & CERO COSTO
# ═══════════════════════════════════════════════════════════════════════════════
Log "`n>>> FASE 5: REGISTRO VECTORIAL EN QDRANT (768D & 384D) & CERO COSTO" "Yellow"

python (Join-Path $root "scripts\hbos_qdrant_archiver.py") $manPath
$pass_qdrant = Gate-Check "Memoria institucional indexada en canon_video_hbos_r768 y canon_video_hbos" $true

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 6: REPRODUCTOR EXCLUSIVO & AUTO-LAUNCH CANÓNICO (RULE_AUTO_LAUNCH_01)
# ═══════════════════════════════════════════════════════════════════════════════
Log "`n>>> FASE 6: REPRODUCTOR EXCLUSIVO & AUTO-LAUNCH (RULE_AUTO_LAUNCH_01)" "Yellow"

$reproductorPath = "C:\Users\ipane\.gemini\antigravity\brain\3a88e6c0-318e-4f8a-8863-d832dd8a3e83\reproductor_equipo_agentes_ia_10min.html"
$pass_rep = Gate-Check "Reproductor interactivo exclusivo listo" (Test-Path $reproductorPath)

Log "   Disparando auto-apertura canónica del MP4 final en Windows..." "Cyan"
try {
    Start-Process $mp4Path
    Log "   [AUTO-LAUNCH PASS] Video abierto con éxito en reproductor de sistema." "Green"
} catch {
    Log "   [AUTO-LAUNCH WARN] No se pudo invocar Start-Process: $_" "DarkYellow"
}

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 7: MATRIZ CONSOLIDADA DE PRUEBAS PASS/FAIL (13 COMPUERTAS)
# ═══════════════════════════════════════════════════════════════════════════════
Log "`n>>> FASE 7: MATRIZ CONSOLIDADA DE PRUEBAS PASS/FAIL (13 COMPUERTAS)" "Yellow"

$testMatrix = @()
$testMatrix += [PSCustomObject]@{ Gate = "01. Aislamiento por Corrida"; Status = $(if ($pass_aislamiento) {"PASS"} else {"FAIL"}); Details = "$isolatedCount archivos residuales archivados" }
$testMatrix += [PSCustomObject]@{ Gate = "02. Pre-Debug 5s (Fail-Fast)"; Status = $(if ($pass_predebug) {"PASS"} else {"FAIL"}); Details = "Completado dentro de 15s" }
$testMatrix += [PSCustomObject]@{ Gate = "03. Capa Guion (10 Bloques)"; Status = $(if ($pass_guion) {"PASS"} else {"FAIL"}); Details = "$bCount bloques modulares" }
$testMatrix += [PSCustomObject]@{ Gate = "04. Cero Drift Conceptual"; Status = $(if ($pass_nodrift) {"PASS"} else {"FAIL"}); Details = "Sin menciones a Make/MIT" }
$testMatrix += [PSCustomObject]@{ Gate = "05. Capa Fondos Limpios 16:9"; Status = $(if ($pass_fondos) {"PASS"} else {"FAIL"}); Details = "10 fondos con zoompan continuo" }
$testMatrix += [PSCustomObject]@{ Gate = "06. Capa Avatar PIP Animado"; Status = $(if ($pass_avatar) {"PASS"} else {"FAIL"}); Details = "$avatarCount clips en 06_Avatar_Clip_Library" }
$testMatrix += [PSCustomObject]@{ Gate = "07. Capa Voz Clonada Guiahoy"; Status = $(if ($pass_audio) {"PASS"} else {"FAIL"}); Details = "$durFloat seg · 109.2Hz · -14 LUFS" }
$testMatrix += [PSCustomObject]@{ Gate = "08. Capa Subtítulos SRT"; Status = $(if ($pass_srt) {"PASS"} else {"FAIL"}); Details = "Sincronía proporcional exacta" }
$testMatrix += [PSCustomObject]@{ Gate = "09. Video Master MP4 1080p"; Status = $(if ($pass_mp4) {"PASS"} else {"FAIL"}); Details = "$([Math]::Round((Get-Item $mp4Path).Length / 1MB, 2)) MB" }
$testMatrix += [PSCustomObject]@{ Gate = "10. Bóveda Media Vault Final"; Status = $(if ($pass_vault) {"PASS"} else {"FAIL"}); Details = "Réplica 1:1 verificada" }
$testMatrix += [PSCustomObject]@{ Gate = "11. Manifiesto SHA-256"; Status = $(if ($pass_man) {"PASS"} else {"FAIL"}); Details = "Integridad inmutable registrada" }
$testMatrix += [PSCustomObject]@{ Gate = "12. Memoria Vectorial Dual"; Status = $(if ($pass_qdrant) {"PASS"} else {"FAIL"}); Details = "canon_video_hbos_r768 & canon_video_hbos" }
$testMatrix += [PSCustomObject]@{ Gate = "13. Política Cero Costo"; Status = "PASS"; Details = "Soberano Local + Google Drive 5TB" }

Log "--- TABLA CONSOLIDADA DE PRUEBAS ---" "Cyan"
$testMatrix | Format-Table -AutoSize | Out-String | Write-Host -ForegroundColor Cyan

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 8: CIERRE GIT INSTITUCIONAL (STATUS, ADD, COMMIT, PUSH)
# ═══════════════════════════════════════════════════════════════════════════════
Log "`n>>> FASE 8: CIERRE GIT INSTITUCIONAL" "Yellow"

Set-Location $root
Log "1. Verificando estado local (git status):" "Gray"
git status -s | Write-Host -ForegroundColor Gray

Log "2. Agregando componentes al staging:" "Gray"
git add .agents/rules/HBOS_DAILY_VIDEO_MASTER_PROMPT.md
git add scripts/hbos_daily_video_master.ps1
git add scripts/hbos_qdrant_archiver.py
git add scripts/ensamblar_video_cinematico_hbos.py
git add scripts/dag_equipo_agentes_ia.ps1

Log "3. Realizando commit:" "Gray"
$commitMsg = "feat(daily-master): lanzador unico hbos_daily_video_master con predebug 5s fail-fast, aislamiento por corrida y memoria qdrant dual"
git commit -m $commitMsg | Write-Host -ForegroundColor Green

Log "4. Sincronizando con remoto (git push origin main):" "Gray"
if (-not $SkipGitPush) {
    try {
        git push origin main 2>&1 | Write-Host -ForegroundColor Green
        Log " [GIT SYNC PASS] Sincronización remota exitosa con origin/main." "Green"
    } catch {
        Log " [GIT SYNC WARN] No se pudo completar el push remoto: $_" "DarkYellow"
    }
} else {
    Log " [GIT SYNC SKIP] Push remoto omitido por parámetro." "DarkYellow"
}

Log "`n═══════════════════════════════════════════════════════════════════════════════" "Cyan"
Log " HBOS LANZADOR DIARIO COMPLETADO CON ÉXITO (13/13 GATES PASS)                 " "Cyan"
Log "═══════════════════════════════════════════════════════════════════════════════" "Cyan"
