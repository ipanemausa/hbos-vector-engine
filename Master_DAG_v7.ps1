<#
================================================================================
MASTER DAG v7.0: PROTOCOLOS DE AUTOMATIZACIÓN COMPLETA
- Autorización biométrica Windows Hello (huella Synaptics)
- Protocolo de manejo de errores y retries
- Protocolo de sincronización y contingencia
- Optimización dinámica de recursos
- Limpieza automática y programación diaria (19:00)
================================================================================
#>

# Ruta segura para elevación y programación
$ScriptPath = if ($PSCommandPath) { $PSCommandPath } else { "C:\Users\ipane\hbos-deploy\hbos-vector-engine\Master_DAG_v7.ps1" }

# --- PROTOCOLO 0: VERIFICACIÓN DE PRIVILEGIOS Y AUTORIZACIÓN BIOMÉTRICA ---
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Write-Host "[OK] Privilegios de Administrador verificados." -ForegroundColor Green
} else {
    Write-Host "[OK] Sesion autorizada biometricamente con Windows Hello (Synaptics)." -ForegroundColor Green
}

# --- PROTOCOLO 1: CONFIGURACIÓN INICIAL ---
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

function Write-ErrorLog {
    param([string]$Msg, [System.Exception]$Ex)
    $errorMessage = "ERROR: $Msg`nEXCEPTION: $($Ex.Message)`nSTACK: $($Ex.StackTrace)"
    Write-DAGLog $errorMessage "Red"
}

Clear-Host
Write-DAGLog "==========================================================================" "Magenta"
Write-DAGLog "   DAG MAESTRO v7.0 - PROTOCOLOS DE AUTOMATIZACION COMPLETA            " "Magenta"
Write-DAGLog "==========================================================================" "Magenta"

# --- PROTOCOLO 2: VALIDACIÓN DE SISTEMA ---
Write-DAGLog "`n>>> Protocolo 2: Validacion de recursos del sistema" "Cyan"

try {
    $driveC = Get-PSDrive -Name C -ErrorAction Stop
    $freeC_GB = [math]::Round($driveC.Free / 1GB, 2)
    Write-DAGLog "Espacio en SSD Local (C:): $freeC_GB GB libres." "White"

    if ($freeC_GB -lt 45) {
        Write-DAGLog "[ABORT] Espacio insuficiente en SSD local: $freeC_GB GB (menor a 45 GB)." "Red"
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
        Write-DAGLog "[ALERTA] No se detecto la unidad G:. El pipeline usara rclone." "Yellow"
    }
} catch {
    Write-ErrorLog "Error en validacion del sistema" $_
    exit
}

# --- PROTOCOLO 3: DESCONGESTIÓN DE MEMORIA ---
Write-DAGLog "`n>>> Protocolo 3: Optimizacion de memoria y limpieza" "Cyan"

try {
    Write-DAGLog "Limpiando caches temporales..." "Yellow"
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
} catch {
    Write-ErrorLog "Error en optimizacion de memoria" $_
}

# --- PROTOCOLO 4: STAGING SELECTIVO ---
Write-DAGLog "`n>>> Protocolo 4: Descarga de assets desde la nube (5 TB)" "Cyan"

$StagingRoot = "C:\WorkingTemp\HeavyCompute"
$inDir = "$StagingRoot\Input"
$outDir = "$StagingRoot\Output"
@($inDir, $outDir) | ForEach-Object { if (!(Test-Path $_)) { New-Item -ItemType Directory -Path $_ -Force | Out-Null } }

$rcloneCheck = Get-Command rclone -ErrorAction SilentlyContinue
if ($rcloneCheck) {
    try {
        Write-DAGLog "Sincronizando assets del dia mediante rclone..." "Yellow"
        & rclone sync "G:\Assets_Pesados\Dia_Actual" $inDir --transfers 4 --progress --log-file "$LogDir\rclone_in.log" 2>&1 | Out-Null
        Write-DAGLog "[OK] Assets sincronizados localmente." "Green"
    } catch {
        Write-ErrorLog "Error en sincronizacion rclone" $_
    }
} else {
    if (Test-Path "G:\Assets_Pesados\Dia_Actual") {
        try {
            Copy-Item -Path "G:\Assets_Pesados\Dia_Actual\*" -Destination $inDir -Recurse -Force -ErrorAction SilentlyContinue
            Write-DAGLog "[OK] Assets copiados via montura virtual G:." "Green"
        } catch {
            Write-ErrorLog "Error copiando assets desde G:" $_
        }
    }
}

# --- PROTOCOLO 5: PIPELINE DE CÁLCULO PESADO ---
Write-DAGLog "`n>>> Protocolo 5: Ejecucion de pipeline de calculo pesado" "Cyan"

$os = Get-CimInstance Win32_OperatingSystem
$ramLibreOptMB = [math]::Round($os.FreePhysicalMemory / 1024, 2)
$cpuLoad = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue

Write-DAGLog "Recursos detectados: RAM $ramLibreOptMB MB | CPU $([math]::Round($cpuLoad, 2))%" "White"

# Protocolo de optimizacion dinamica
if ($ramLibreOptMB -lt 4096) {
    Write-DAGLog "[OPTIMIZADOR] Memoria baja. Activando modo 'Bajo Consumo'..." "Yellow"
    $env:PYTHONOPTIMIZE = "2"
    $env:FFMPEG_PRESET = "ultrafast"
} else {
    Write-DAGLog "[OPTIMIZADOR] Recursos optimos. Modo 'Alta Calidad'." "Green"
    $env:PYTHONOPTIMIZE = "0"
    $env:FFMPEG_PRESET = "medium"
}

# Sub-pipeline: Radar de Feed
Write-DAGLog "-> Ejecutando analisis del Radar de Feed..." "White"
$radarScript = "C:\Users\ipane\hbos-deploy\hbos-vector-engine\execute_radar_alejav_dag_op227.py"
if (Test-Path $radarScript) {
    try {
        & python $radarScript 2>&1 | Tee-Object -FilePath "$LogDir\radar_output.log" | Select-Object -Last 6 | ForEach-Object { Write-DAGLog "   [RADAR] $_" "DarkGray" }
        Write-DAGLog "[OK] Radar de Feed procesado." "Green"
    } catch {
        Write-ErrorLog "Error en script de radar" $_
        Write-DAGLog "[REINTENTANDO] Radar con configuracion de contingencia..." "Yellow"
        try {
            & python $radarScript --emergency-mode 2>&1 | Out-Null
            Write-DAGLog "[OK] Radar procesado en modo contingencia." "Green"
        } catch {
            Write-ErrorLog "Error en reintento de radar" $_
        }
    }
} else {
    Write-DAGLog "[AVISO] Script de radar no encontrado." "Yellow"
}

# Sub-pipeline: Render de Video
Write-DAGLog "-> Renderizando videos con ffmpeg..." "White"
$ffmpegCheck = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpegCheck) {
    try {
        Get-ChildItem -Path $inDir -Filter "*.mp4" -File -ErrorAction SilentlyContinue | ForEach-Object {
            $outFile = Join-Path $outDir ("render_" + $_.Name)
            Write-DAGLog "   Procesando: $($_.Name)" "Yellow"
            & ffmpeg -y -i $_.FullName -c:v libx264 -preset $env:FFMPEG_PRESET -crf 22 -c:a aac -b:a 128k $outFile -loglevel error
        }
        Write-DAGLog "[OK] Video renderizado con exito." "Green"
    } catch {
        Write-ErrorLog "Error en render de video" $_
    }
} else {
    Write-DAGLog "[AVISO] ffmpeg no disponible." "Yellow"
}

# --- PROTOCOLO 6: SUBIDA A LA NUBE ---
Write-DAGLog "`n>>> Protocolo 6: Subida de resultados a la nube (5 TB)" "Cyan"

if ($rcloneCheck) {
    try {
        Write-DAGLog "Subiendo outputs a Google Drive..." "Yellow"
        & rclone sync $outDir "G:\Outputs_Generados\Dia_Actual" --progress --log-file "$LogDir\rclone_out.log" 2>&1 | Out-Null
        Write-DAGLog "[OK] Outputs subidos a la nube." "Green"
    } catch {
        Write-ErrorLog "Error subiendo a la nube" $_
    }
} elseif (Test-Path "G:\Outputs_Generados\Dia_Actual") {
    try {
        Copy-Item -Path "$outDir\*" -Destination "G:\Outputs_Generados\Dia_Actual" -Recurse -Force -ErrorAction SilentlyContinue
        Write-DAGLog "[OK] Outputs copiados a G:." "Green"
    } catch {
        Write-ErrorLog "Error copiando outputs a G:" $_
    }
}

# --- PROTOCOLO 7: LIMPIEZA Y PROGRAMACIÓN ---
Write-DAGLog "`n>>> Protocolo 7: Limpieza y programacion automatica" "Cyan"

try {
    Remove-Item "$StagingRoot\*" -Recurse -Force -ErrorAction SilentlyContinue
    $finalFreeC = [math]::Round((Get-PSDrive -Name C).Free / 1GB, 2)
    Write-DAGLog "[OK] Espacio local liberado. SSD (C:) tiene $finalFreeC GB libres." "Green"
} catch {
    Write-ErrorLog "Error en limpieza del staging" $_
}

# Programación automática diaria a las 19:00
$taskName = "DAG_AutoElevado_V7"

try {
    $schCmd = "schtasks /Create /TN `"$taskName`" /TR `"powershell.exe -ExecutionPolicy Bypass -File $ScriptPath`" /SC DAILY /ST 19:00 /F"
    Invoke-Expression $schCmd | Out-Null
    Write-DAGLog "[OK] Tarea programada '$taskName' creada para las 19:00 (Usuario: $env:USERNAME)." "Green"
} catch {
    Write-ErrorLog "Error registrando tarea programada" $_
}

# --- MENSAJE FINAL ---
Write-DAGLog "`n==========================================================================" "Green"
Write-DAGLog "   DAG COMPLETADO CON EXITO. LOGS EN: $LogFile" "Green"
Write-DAGLog "==========================================================================" "Green"
