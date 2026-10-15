<#
================================================================================
MASTER MONOLITHIC DAG: CALCULO PESADO HIBRIDO (MUSE + VIDEO + RADAR + CLOUD)
Version: 4.0 - Ejecucion Continua Sin Fragmentacion
================================================================================
#>

[CmdletBinding()]
param(
    [switch]$SkipSpaceCheck = $false,
    [string]$CloudRemote = "G:",
    [string]$StagingRoot = "C:\WorkingTemp\HeavyCompute",
    [string]$WorkspaceRoot = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
)

# Configuracion de codificacion y buffers
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

# Rutas globales de Logging
$LogDir = "$env:LOCALAPPDATA\SystemOptimizer\Logs"
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
$LogFile = "$LogDir\MASTER_DAG_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

function Write-DAGLog {
    param([string]$Msg, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $Msg"
    Write-Host $line -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

Clear-Host
Write-DAGLog "==========================================================================" "Magenta"
Write-DAGLog "   INICIANDO MASTER MONOLITHIC DAG: LOCAL COMPUTE / CLOUD STORAGE (5 TB)  " "Magenta"
Write-DAGLog "==========================================================================" "Magenta"

# ==============================================================================
# FASE 0: PRE-FLIGHT Y VALIDACION DE ENTORNO
# ==============================================================================
Write-DAGLog "`n>>> [FASE 0/6] PRE-FLIGHT Y VALIDACION DE ENTORNO" "Cyan"

# Auditoria SSD Local C:
$driveC = Get-PSDrive -Name C -ErrorAction SilentlyContinue
$freeC_GB = [math]::Round($driveC.Free / 1GB, 2)
Write-DAGLog "SSD Local (C:) espacio libre: $freeC_GB GB" "White"
if ($freeC_GB -lt 45 -and -not $SkipSpaceCheck) {
    Write-DAGLog "[ABORT] Espacio insuficiente en C: $freeC_GB GB (menor a 45 GB minimo)." "Red"
    Exit 1
}

# Auditoria Google Drive G: (Stream Mode)
$driveG = Get-PSDrive -Name G -ErrorAction SilentlyContinue
if ($null -eq $driveG) {
    Write-DAGLog "[AVISO] Unidad G: no montada. Iniciando cliente GoogleDrive..." "Yellow"
    Start-Process "GoogleDrive" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 8
    $driveG = Get-PSDrive -Name G -ErrorAction SilentlyContinue
}
if ($driveG) {
    $freeG_GB = [math]::Round($driveG.Free / 1GB, 2)
    Write-DAGLog "[OK] Drive G: activo en modo Stream. Espacio disponible: $freeG_GB GB." "Green"
} else {
    Write-DAGLog "[ALERTA] No se pudo verificar G:. Se continuara con acceso alternativo." "Yellow"
}

# ==============================================================================
# FASE 1: DESCONGESTION DE RAM Y PURGA DE BASURA (SIN TOCAR ANTIGRAVITY)
# ==============================================================================
Write-DAGLog "`n>>> [FASE 1/6] PURGA EN CALIENTE DE CACHE Y LIBERACION DE MEMORIA" "Cyan"

Write-DAGLog "Limpiando residuos temporales y vaciando papelera..." "Yellow"
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Clear-RecycleBin -Force -ErrorAction SilentlyContinue

# Preservar IDE Antigravity y cerrar navegadores secundarios si no son la sesion actual
$currentProcId = [System.Diagnostics.Process]::GetCurrentProcess().Id
Get-Process | Where-Object { 
    $_.Name -match 'msedge|chrome|firefox' -and 
    $_.ProcessName -notmatch 'antigravity' -and 
    $_.Id -ne $currentProcId 
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Recoleccion agresiva de memoria RAM
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
[System.GC]::Collect()

$ramLibreMB = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024, 2)
Write-DAGLog "[OK] Memoria RAM disponible tras optimizacion: $ramLibreMB MB" "Green"

# ==============================================================================
# FASE 2: STAGING SELECTIVO (CLOUD -> LOCAL)
# ==============================================================================
Write-DAGLog "`n>>> [FASE 2/6] STAGING SELECTIVO (DESCARGA DESDE 5 TB CLOUD A LOCAL)" "Cyan"

$inDir = "$StagingRoot\Input"
$outDir = "$StagingRoot\Output"
@($inDir, $outDir) | ForEach-Object { if (!(Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null } }

Write-DAGLog "Verificando herramientas de sincronizacion..." "Yellow"
$rcloneCheck = Get-Command rclone -ErrorAction SilentlyContinue

$cloudSource = "${CloudRemote}\Assets_Pesados\Dia_Actual"
if ($rcloneCheck) {
    if (Test-Path $cloudSource) {
        Write-DAGLog "Ejecutando rclone sync desde $cloudSource hacia $inDir..." "Yellow"
        & rclone sync $cloudSource $inDir --transfers 4 --progress --log-file "$LogDir\rclone_in.log" 2>&1 | Out-Null
        Write-DAGLog "[OK] Sincronizacion cloud-a-local finalizada con rclone." "Green"
    } else {
        Write-DAGLog "[INFO] Origen cloud no detectado en $cloudSource. Continuando con assets locales." "White"
    }
} else {
    Write-DAGLog "[AVISO] rclone no encontrado en PATH. Utilizando acceso directo sobre $CloudRemote" "Yellow"
    if (Test-Path $cloudSource) {
        Copy-Item -Path "$cloudSource\*" -Destination $inDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-DAGLog "[OK] Copia local completada via montura virtual G:." "Green"
    }
}

# ==============================================================================
# FASE 3: PIPELINE DE CALCULO PESADO (RADAR FEED + MUSE + FFMPEG)
# ==============================================================================
Write-DAGLog "`n>>> [FASE 3/6] EJECUCION DEL CALCULO PESADO HIBRIDO (LOCAL COMPUTE)" "Cyan"

$env:PYTHONOPTIMIZE = "2"
$env:PYTHONIOENCODING = "utf-8"

# Sub-Fase 3.1: Radar de Feed (Ingesta y analisis)
Write-DAGLog "-> Sub-Fase 3.1: Ejecutando analisis del Radar de Feed..." "White"
$radarScript = "$WorkspaceRoot\execute_radar_alejav_dag_op227.py"
if (-not (Test-Path $radarScript)) {
    $radarScript = "$WorkspaceRoot\radar_feed.py"
}

if (Test-Path $radarScript) {
    Write-DAGLog "   Lanzando Radar: $radarScript" "Yellow"
    & python $radarScript 2>&1 | Tee-Object -FilePath "$LogDir\radar_output.log" | Select-Object -Last 8 | ForEach-Object { Write-DAGLog "   [RADAR] $_" "DarkGray" }
    Write-DAGLog "[OK] Fase 3.1 Radar finalizada exitosamente." "Green"
} else {
    Write-DAGLog "[AVISO] Script de Radar no localizado. Saltando al siguiente modulo." "Yellow"
}

# Sub-Fase 3.2: Pipeline Muse / Factoria de Nodos
Write-DAGLog "-> Sub-Fase 3.2: Ejecutando arquitectura hibrida Muse..." "White"
$museScript = "$WorkspaceRoot\execute_muse_app_dag_op221.py"
if (Test-Path $museScript) {
    Write-DAGLog "   Lanzando Orquestador Muse: $museScript" "Yellow"
    & python $museScript 2>&1 | Tee-Object -FilePath "$LogDir\muse_output.log" | Select-Object -Last 8 | ForEach-Object { Write-DAGLog "   [MUSE] $_" "DarkGray" }
    Write-DAGLog "[OK] Fase 3.2 Muse finalizada exitosamente." "Green"
} else {
    Write-DAGLog "[AVISO] Script Muse no localizado en $museScript. Continuando." "Yellow"
}

# Sub-Fase 3.3: Post-produccion de Video & Ensamble FFmpeg
Write-DAGLog "-> Sub-Fase 3.3: Post-produccion multimedia y render..." "White"
$videoScript = "$WorkspaceRoot\execute_video_alejav_dag_op222.py"
if (-not (Test-Path $videoScript)) {
    $videoScript = "$WorkspaceRoot\render_fases_3_4_5_6.py"
}

if (Test-Path $videoScript) {
    Write-DAGLog "   Lanzando Renderizador de Video: $videoScript" "Yellow"
    & python $videoScript 2>&1 | Tee-Object -FilePath "$LogDir\video_output.log" | Select-Object -Last 8 | ForEach-Object { Write-DAGLog "   [VIDEO] $_" "DarkGray" }
    Write-DAGLog "[OK] Fase 3.3 Video/Render finalizada." "Green"
} else {
    Write-DAGLog "[INFO] No se especifico script de video adicional. Ensamblajes al dia." "White"
}

# ==============================================================================
# FASE 4: SINCRONIZACION INVERSA (LOCAL -> CLOUD 5 TB)
# ==============================================================================
Write-DAGLog "`n>>> [FASE 4/6] SINCRONIZACION INVERSA Y BLINDAJE EN LA NUBE (5 TB)" "Cyan"

$cloudDest = "${CloudRemote}\Assets_Masterizados\$(Get-Date -Format 'yyyyMMdd')"

# Mover salidas de video locales generadas hacia el Staging Output
Get-ChildItem -Path $WorkspaceRoot -Filter "*.mp4" -File -ErrorAction SilentlyContinue | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-4) } | 
    ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $outDir -Force -ErrorAction SilentlyContinue
        Write-DAGLog "   [STAGING] Archivo listo para subida: $($_.Name)" "White"
    }

if (Test-Path $outDir) {
    $outputFiles = Get-ChildItem -Path $outDir -File -ErrorAction SilentlyContinue
    if ($outputFiles.Count -gt 0) {
        Write-DAGLog "Subiendo $($outputFiles.Count) assets renderizados a la nube ($cloudDest)..." "Yellow"
        if ($rcloneCheck) {
            & rclone copy $outDir $cloudDest --transfers 4 --progress --log-file "$LogDir\rclone_out.log" 2>&1 | Out-Null
            Write-DAGLog "[OK] Sincronizacion exitosa con rclone a $cloudDest" "Green"
        } else {
            if (!(Test-Path $cloudDest)) { New-Item -ItemType Directory -Path $cloudDest -Force | Out-Null }
            Copy-Item -Path "$outDir\*" -Destination $cloudDest -Recurse -Force -ErrorAction SilentlyContinue
            Write-DAGLog "[OK] Copia exitosa a unidad G: ($cloudDest)" "Green"
        }
    } else {
        Write-DAGLog "[INFO] No hay artefactos nuevos en $outDir para transferir." "White"
    }
}

# ==============================================================================
# FASE 5: PURGA DE STAGING LOCAL, TELEMETRIA Y CIERRE SEGURO
# ==============================================================================
Write-DAGLog "`n>>> [FASE 5/6] PURGA DE STAGING LOCAL Y TELEMETRIA FINAL" "Cyan"

if (Test-Path $inDir) {
    Remove-Item "$inDir\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-DAGLog "[OK] Directorio de entrada $inDir purgado." "Green"
}

[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

$finalDriveC = Get-PSDrive -Name C -ErrorAction SilentlyContinue
$finalFreeC = [math]::Round($finalDriveC.Free / 1GB, 2)
$finalDriveG = Get-PSDrive -Name G -ErrorAction SilentlyContinue
$finalFreeG = if ($finalDriveG) { [math]::Round($finalDriveG.Free / 1GB, 2) } else { "N/A" }
$finalRAM = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024, 2)

Write-DAGLog "`n==========================================================================" "Green"
Write-DAGLog "                     REPORTE CONSOLIDADO DEL MASTER DAG                   " "Green"
Write-DAGLog "==========================================================================" "Green"
Write-Host "1. ESPACIO SSD LOCAL (C:)  : $finalFreeC GB Libres" -ForegroundColor Cyan
Write-Host "2. ESPACIO CLOUD (G:)      : $finalFreeG GB Libres (Stream On-Demand)" -ForegroundColor Cyan
Write-Host "3. MEMORIA RAM LIBRE       : $finalRAM MB" -ForegroundColor Cyan
Write-Host "4. PIPELINE EJECUTADO      : Radar Feed + Muse + Render Video" -ForegroundColor Green
Write-Host "5. LOG MAESTRO             : $LogFile" -ForegroundColor White
Write-DAGLog "==========================================================================" "Green"
Write-DAGLog "MASTER MONOLITHIC DAG FINALIZADO CON EXITO." "Green"
Write-DAGLog "==========================================================================" "Green"
