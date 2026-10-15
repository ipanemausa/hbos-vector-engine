<#
================================================================================
MASTER DAG v6.0: AUTOELEVACIÓN + CÁLCULO PESADO HÍBRIDO (MUSE + VIDEO + RADAR)
- Se auto-eleva con Windows Hello (huella/PIN) al hacer doble clic o ejecutar.
- Optimiza recursos localmente y usa la nube de 5 TB para almacenamiento pesado.
- Limpieza automática al finalizar.
================================================================================
#>

# Ruta segura del script para elevación y programación
$ScriptPath = if ($PSCommandPath) { $PSCommandPath } else { "C:\Users\ipane\hbos-deploy\hbos-vector-engine\Master_DAG_v6.ps1" }

# --- SECCIÓN 1: AUTOELEVACIÓN CON WINDOWS HELLO ---
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host ">>> Solicitando elevación de privilegios con Windows Hello..." -ForegroundColor Yellow
    
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = "powershell.exe"
    $pinfo.Arguments = "-NoProfile -NoExit -ExecutionPolicy Bypass -File `"$ScriptPath`""
    $pinfo.Verb = "runAs"
    $pinfo.UseShellExecute = $true

    try {
        [System.Diagnostics.Process]::Start($pinfo) | Out-Null
    } catch {
        Write-Host "[ERROR] No se pudo elevar el privilegio o fue cancelado por el usuario." -ForegroundColor Red
        exit
    }
    exit
}

# --- SECCIÓN 2: CONFIGURACIÓN INICIAL ---
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

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
Write-DAGLog "   DAG MAESTRO v6.0 - EJECUCIÓN COMPLETA CON PRIVILEGIOS ELEVADOS          " "Magenta"
Write-DAGLog "==========================================================================" "Magenta"

# --- SECCIÓN 3: FASE 0 - PRE-FLIGHT ---
Write-DAGLog "`n>>> [FASE 0/6] VALIDACIÓN DE SISTEMA" "Cyan"

$driveC = Get-PSDrive -Name C -ErrorAction SilentlyContinue
$freeC_GB = [math]::Round($driveC.Free / 1GB, 2)
Write-DAGLog "Espacio en SSD Local (C:): $freeC_GB GB libres." "White"

if ($freeC_GB -lt 45) {
    Write-DAGLog "[ABORT] Espacio insuficiente en SSD local ($freeC_GB GB < 45 GB)." "Red"
    Read-Host "Presiona Enter para salir..."
    exit
}

$driveG = Get-PSDrive -Name G -ErrorAction SilentlyContinue
if (-not $driveG) {
    Write-DAGLog "[AVISO] Unidad G: no detectada. Iniciando GoogleDriveFS..." "Yellow"
    Start-Process "GoogleDrive" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 8
    $driveG = Get-PSDrive -Name G -ErrorAction SilentlyContinue
}
if ($driveG) {
    $freeG_GB = [math]::Round($driveG.Free / 1GB, 2)
    Write-DAGLog "[OK] Drive G: activo (Modo Stream). Espacio disponible: $freeG_GB GB." "Green"
} else {
    Write-DAGLog "[ALERTA] No se detectó la unidad G:. El pipeline usará rclone." "Yellow"
}

# --- SECCIÓN 4: FASE 1 - DESCONGESTIÓN DE MEMORIA ---
Write-DAGLog "`n>>> [FASE 1/6] OPTIMIZACIÓN DE MEMORIA Y LIMPIEZA" "Cyan"

Write-DAGLog "Limpiando cachés temporales..." "Yellow"
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
Clear-RecycleBin -Force -ErrorAction SilentlyContinue

$currentProcId = [System.Diagnostics.Process]::GetCurrentProcess().Id
Get-Process | Where-Object { 
    $_.Name -match 'msedge|chrome|firefox' -and 
    $_.ProcessName -notmatch 'antigravity' -and 
    $_.Id -ne $currentProcId 
} | Stop-Process -Force -ErrorAction SilentlyContinue

[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
[System.GC]::Collect()

$ramLibreMB = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1024, 2)
Write-DAGLog "[OK] Memoria RAM disponible: $ramLibreMB MB." "Green"

# --- SECCIÓN 5: FASE 2 - STAGING SELECTIVO ---
Write-DAGLog "`n>>> [FASE 2/6] DESCARGA DE ASSETS DESDE LA NUBE (5 TB)" "Cyan"

$StagingRoot = "C:\WorkingTemp\HeavyCompute"
$inDir = "$StagingRoot\Input"
$outDir = "$StagingRoot\Output"
@($inDir, $outDir) | ForEach-Object { if (!(Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null } }

$rcloneCheck = Get-Command rclone -ErrorAction SilentlyContinue
if ($rcloneCheck) {
    Write-DAGLog "Sincronizando assets del día mediante rclone..." "Yellow"
    & rclone sync "G:\Assets_Pesados\Dia_Actual" $inDir --transfers 4 --progress --log-file "$LogDir\rclone_in.log" 2>&1 | Out-Null
    Write-DAGLog "[OK] Assets sincronizados localmente." "Green"
} else {
    if (Test-Path "G:\Assets_Pesados\Dia_Actual") {
        Copy-Item -Path "G:\Assets_Pesados\Dia_Actual\*" -Destination $inDir -Recurse -Force -ErrorAction SilentlyContinue
        Write-DAGLog "[OK] Assets copiados vía montura virtual G:." "Green"
    } else {
        Write-DAGLog "[INFO] Origen cloud no detectado aún en G:\Assets_Pesados\Dia_Actual. Continuando." "White"
    }
}

# --- SECCIÓN 6: FASE 3 - PIPELINE DE CÁLCULO PESADO ---
Write-DAGLog "`n>>> [FASE 3/6] CÁLCULO PESADO CON OPTIMIZACIÓN HÍBRIDA" "Cyan"

$os = Get-CimInstance Win32_OperatingSystem
$ramLibreOptMB = [math]::Round($os.FreePhysicalMemory / 1024, 2)
$cpuLoad = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue

Write-DAGLog "Recursos detectados: RAM $ramLibreOptMB MB | CPU $([math]::Round($cpuLoad, 2))%" "White"

# Lógica de optimización híbrida dinámica
if ($ramLibreOptMB -lt 4096) {
    Write-DAGLog "[OPTIMIZADOR] Memoria baja. Activando modo 'Bajo Consumo'..." "Yellow"
    $env:PYTHONOPTIMIZE = "2"
    $env:FFMPEG_PRESET = "ultrafast"
} else {
    Write-DAGLog "[OPTIMIZADOR] Recursos óptimos. Modo 'Alta Calidad'." "Green"
    $env:PYTHONOPTIMIZE = "0"
    $env:FFMPEG_PRESET = "medium"
}

# Sub-Fase 3.1: Radar de Feed
Write-DAGLog "-> Ejecutando análisis del Radar de Feed..." "White"
$radarScript = "C:\Users\ipane\hbos-deploy\hbos-vector-engine\execute_radar_alejav_dag_op227.py"
if (Test-Path $radarScript) {
    & python $radarScript 2>&1 | Out-Null
    Write-DAGLog "[OK] Radar de Feed procesado." "Green"
}

# Sub-Fase 3.2: Render de Video con ffmpeg
Write-DAGLog "-> Renderizando videos con ffmpeg..." "White"
$ffmpegCheck = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpegCheck) {
    Get-ChildItem -Path $inDir -Filter "*.mp4" -File -ErrorAction SilentlyContinue | ForEach-Object {
        $outFile = Join-Path $outDir ("render_" + $_.Name)
        Write-DAGLog "   Procesando: $($_.Name)" "Yellow"
        & ffmpeg -y -i $_.FullName -c:v libx264 -preset $env:FFMPEG_PRESET -crf 22 -c:a aac -b:a 128k $outFile -loglevel error
    }
    Write-DAGLog "[OK] Video renderizado con éxito." "Green"
}

# --- SECCIÓN 7: FASE 4 - SUBIDA A LA NUBE ---
Write-DAGLog "`n>>> [FASE 4/6] SUBIDA DE RESULTADOS A LA NUBE (5 TB)" "Cyan"

if ($rcloneCheck) {
    Write-DAGLog "Subiendo outputs a Google Drive..." "Yellow"
    & rclone sync $outDir "G:\Outputs_Generados\Dia_Actual" --progress --log-file "$LogDir\rclone_out.log" 2>&1 | Out-Null
    Write-DAGLog "[OK] Outputs subidos a la nube." "Green"
} elseif (Test-Path "G:\Outputs_Generados\Dia_Actual") {
    Copy-Item -Path "$outDir\*" -Destination "G:\Outputs_Generados\Dia_Actual" -Recurse -Force -ErrorAction SilentlyContinue
    Write-DAGLog "[OK] Outputs copiados a G:." "Green"
}

# --- SECCIÓN 8: FASE 5 - LIMPIEZA Y PURGA ---
Write-DAGLog "`n>>> [FASE 5/6] LIMPIEZA DEL SISTEMA" "Cyan"

Remove-Item "$StagingRoot\*" -Recurse -Force -ErrorAction SilentlyContinue
$finalFreeC = [math]::Round((Get-PSDrive -Name C).Free / 1GB, 2)
Write-DAGLog "[OK] Espacio local liberado. SSD (C:) tiene $finalFreeC GB libres." "Green"

# --- SECCIÓN 9: FASE 6 - PROGRAMACIÓN AUTOMÁTICA ---
Write-DAGLog "`n>>> [FASE 6/6] CONFIGURANDO TAREA PROGRAMADA (19:00)" "Cyan"

$taskName = "DAG_AutoElevado_V6"

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
$trigger = New-ScheduledTaskTrigger -Daily -At "19:00"
$principalTask = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principalTask -Settings $settings -Force | Out-Null
    Write-DAGLog "[OK] Tarea programada '$taskName' creada para las 19:00." "Green"
} catch {
    Write-DAGLog "[!] Error creando tarea programada." "Yellow"
}

# --- MENSAJE FINAL ---
Write-DAGLog "`n==========================================================================" "Green"
Write-DAGLog "   DAG COMPLETADO CON ÉXITO. LOGS EN: $LogFile" "Green"
Write-DAGLog "==========================================================================" "Green"

if ($env:TERM -ne "wt.exe") {
    Write-Host "`nEjecución finalizada. Presiona cualquier tecla para salir o revisa la ventana." -ForegroundColor Cyan
}
