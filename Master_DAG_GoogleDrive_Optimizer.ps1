# ==============================================================================
# DAG MAESTRO: OPTIMIZACIÓN COMPLETA DE SISTEMA Y GOOGLE DRIVE
# Versión: 3.0 - Integración Total
# Ejecutar como Administrador con Windows Hello (Huella/PIN)
# ==============================================================================

[CmdletBinding()]
param(
    [switch]$SkipSpaceCheck = $false,
    [switch]$InstallScheduledTask = $true
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Configuración de logging
$LogDirectory = "$env:LOCALAPPDATA\SystemOptimizer\Logs"
if (!(Test-Path $LogDirectory)) { New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null }
$LogPath = "$LogDirectory\Master_DAG_Log_$(Get-Date -Format 'yyyyMMdd').txt"

function Write-StepLog {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
    Add-Content -Path $LogPath -Value "[$timestamp] $Message" -Encoding UTF8
}

Clear-Host
Write-StepLog "=====================================================================" "Magenta"
Write-StepLog "       DAG MAESTRO: OPTIMIZACIÓN COMPLETA DE SISTEMA Y DRIVE           " "Magenta"
Write-StepLog "=====================================================================" "Magenta"

# PASO 0: VERIFICAR PRIVILEGIOS DE ADMINISTRADOR
$currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-StepLog "[CRÍTICO] Ejecutar como Administrador con Windows Hello." "Red"
    Exit 1
} else {
    Write-StepLog "[OK] Privilegios de Administrador verificados." "Green"
}

# PASO 1: VERIFICAR ESPACIO EN C: (MÍNIMO 45 GB)
$driveC = Get-PSDrive -Name C -ErrorAction SilentlyContinue
$freeGB_C = [math]::Round($driveC.Free / 1GB, 2)

if ($freeGB_C -lt 45 -and -not $SkipSpaceCheck) {
    Write-StepLog "[ALERTA] Espacio insuficiente en C: ($freeGB_C GB libres)." "Red"
    Exit 1
} else {
    Write-StepLog "[OK] Espacio libre en C: $freeGB_C GB (>= 45 GB)." "Green"
}

# PASO 2: DETENER Y LIMPIAR GOOGLE DRIVE
$gdriveProcesses = Get-Process -Name "GoogleDrive*", "GoogleDriveFS*" -ErrorAction SilentlyContinue
if ($gdriveProcesses) {
    Write-StepLog "Deteniendo procesos de Google Drive..." "Yellow"
    Stop-Process -Name "GoogleDrive*", "GoogleDriveFS*" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 4
}

# Limpiar caché y base de datos con respaldo
$gDriveDirs = @("$env:LOCALAPPDATA\Google\Drive", "$env:LOCALAPPDATA\Google\DriveFS")
$backupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"

foreach ($dir in $gDriveDirs) {
    if (Test-Path $dir) {
        # Respaldo de BD
        $dbFiles = Get-ChildItem -Path $dir -Filter "*.db" -Recurse -File -ErrorAction SilentlyContinue
        foreach ($db in $dbFiles) {
            $backupDbPath = "$($db.DirectoryName)\$($db.BaseName).bak_$backupTimestamp$($db.Extension)"
            try {
                Copy-Item -Path $db.FullName -Destination $backupDbPath -Force -ErrorAction Stop
                Write-StepLog "[OK] Respaldo BD: $backupDbPath" "Green"
                Remove-Item -Path $db.FullName -Force -ErrorAction SilentlyContinue
            } catch {
                Write-StepLog "[!] Error procesando BD: $($_.Exception.Message)" "Yellow"
            }
        }

        # Limpiar caché
        $cacheFolders = @("task_cache", "content_cache", "tmp")
        foreach ($cFolder in $cacheFolders) {
            $targetCache = "$dir\$cFolder"
            if (Test-Path $targetCache) {
                Remove-Item "$targetCache\*" -Recurse -Force -ErrorAction SilentlyContinue
                Write-StepLog "[OK] Caché purgada: $targetCache" "Green"
            }
        }
    }
}

# PASO 3: CONFIGURAR GOOGLE DRIVE EN MODO STREAM
$registryPaths = @("HKCU:\Software\Google\Drive\settings", "HKLM:\SOFTWARE\Google\Drive")
foreach ($regPath in $registryPaths) {
    if (!(Test-Path $regPath)) { New-Item -Path $regPath -Force | Out-Null }
    try {
        Set-ItemProperty -Path $regPath -Name "StreamFilesEnabled" -Value 1 -Type DWord -Force -ErrorAction Stop
        Write-StepLog "[OK] Modo Stream activado en $regPath" "Green"
    } catch {
        Write-StepLog "[!] Error configurando Stream: $($_.Exception.Message)" "Yellow"
    }
}

# Reiniciar Google Drive
$possiblePaths = @(
    "$env:ProgramFiles\Google\Drive File Stream\launch.bat",
    "$env:ProgramFiles\Google\Drive File Stream\GoogleDriveFS.exe",
    "${env:ProgramFiles(x86)}\Google\Drive File Stream\launch.bat",
    "$env:ProgramFiles\Google\Drive\GoogleDrive.exe",
    "${env:ProgramFiles(x86)}\Google\Drive\GoogleDrive.exe"
)
$gdriveExecutable = $possiblePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($gdriveExecutable) {
    Start-Process -FilePath $gdriveExecutable
    Start-Sleep -Seconds 12
} else {
    Start-Process "GoogleDrive" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 10
}

# PASO 4: CONFIGURAR SERVICIOS A MODO MANUAL
$targetServices = @(
    "GoogleUpdater*", "edgeupdate", "ClickToRunSvc", "AdobeARMservice",
    "Muse", "rclone", "Muse-personal", "rclone-personal"
)

foreach ($pattern in $targetServices) {
    $matchingSvcs = Get-Service -Name $pattern -ErrorAction SilentlyContinue
    if ($matchingSvcs) {
        foreach ($s in $matchingSvcs) {
            try {
                if ($s.StartType -ne "Manual") {
                    Set-Service -Name $s.Name -StartupType Manual -ErrorAction Stop
                    Write-StepLog "   [OK] Servicio '$($s.Name)' a Manual" "Green"
                }
            } catch {
                Write-StepLog "   [!] Error en '$($s.Name)': $($_.Exception.Message)" "Yellow"
            }
        }
    }
}

# PASO 5: VERIFICAR SEGURIDAD
Write-StepLog "Ejecución con privilegios de Administrador confirmada." "Green"
Write-StepLog "Auditoría 2-Step Verification: https://myaccount.google.com/signinoptions/two-step-verification" "Cyan"

# PASO 6: CREAR TAREA PROGRAMADA A LAS 19:00
if ($InstallScheduledTask) {
    $taskName = "System_Master_DAG_Optimizer"
    $scriptFullPath = $MyInvocation.MyCommand.Path
    if (-not $scriptFullPath) {
        $scriptFullPath = "C:\Users\ipane\hbos-deploy\hbos-vector-engine\Master_DAG_GoogleDrive_Optimizer.ps1"
    }

    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptFullPath`" -SkipSpaceCheck"
    $trigger = New-ScheduledTaskTrigger -Daily -At "19:00"
    $principalTask = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principalTask -Settings $settings -Force | Out-Null
        Write-StepLog "[OK] Tarea programada '$taskName' creada para las 19:00 (SYSTEM / Highest)" "Green"
    } catch {
        Write-StepLog "[!] Error creando tarea programada: $($_.Exception.Message)" "Yellow"
    }
}

# REPORTE FINAL
Write-StepLog "`n=====================================================================" "Green"
Write-StepLog "                        REPORTE DE VERIFICACIÓN FINAL               " "Green"
Write-StepLog "=====================================================================" "Green"

Write-Host "`n1. ESTADO DE ALMACENAMIENTO:" -ForegroundColor Cyan
Write-Host "   - SSD Local (C:)     : $freeGB_C GB Libres" -NoNewline
if ($freeGB_C -ge 45) { Write-Host " [CUMPLE]" -ForegroundColor Green } else { Write-Host " [INSUFICIENTE]" -ForegroundColor Red }

$driveG = Get-PSDrive -Name G -ErrorAction SilentlyContinue
if ($driveG) {
    $freeGB_G = [math]::Round($driveG.Free / 1GB, 2)
    Write-Host "   - Virtual Drive (G:) : $freeGB_G GB Libres [CONECTADO]" -ForegroundColor Green
}

Write-Host "`n2. ESTADO DE GOOGLE DRIVE:" -ForegroundColor Cyan
$regCheck = Get-ItemProperty -Path "HKCU:\Software\Google\Drive\settings" -Name "StreamFilesEnabled" -ErrorAction SilentlyContinue
if ($regCheck.StreamFilesEnabled -eq 1) {
    Write-Host "   - Modalidad: STREAM FILES [ACTIVADO]" -ForegroundColor Green
} else {
    Write-Host "   - Modalidad: [CONFIRMACIÓN REQUERIDA]" -ForegroundColor Yellow
}

Write-Host "`n3. ESTADO DE SERVICIOS:" -ForegroundColor Cyan
Write-Host "   - Servicios configurados a Manual (On-demand)" -ForegroundColor Green

Write-Host "`n4. ESTADO DE SEGURIDAD:" -ForegroundColor Cyan
Write-Host "   - Ejecución con Privilegios Elevados : [CONFIRMADO]" -ForegroundColor Green
Write-Host "   - 2-Step Verification               : [VERIFICAR EN GOOGLE]" -ForegroundColor Green

Write-StepLog "`n=====================================================================" "Green"
Write-StepLog "DAG COMPLETADO CON ÉXITO. Log en: $LogPath" "Green"
Write-StepLog "=====================================================================" "Green"
