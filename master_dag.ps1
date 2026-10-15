$ErrorActionPreference = "Stop"

function Write-DAGLog {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Stage = "CORE"
    )
    $TimeStamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$TimeStamp] [$Stage] $Message" -ForegroundColor $Color
}

function Invoke-DAGStage {
    param(
        [string]$Name,
        [string]$Description,
        [scriptblock]$Action
    )
    Write-Host "`n========================================================" -ForegroundColor Cyan
    Write-Host "[DAG STAGE] $Name" -ForegroundColor Cyan
    Write-Host "OBJETIVO: $Description" -ForegroundColor Gray
    Write-Host "========================================================" -ForegroundColor Cyan
    try {
        & $Action
        Write-DAGLog "FASE $Name COMPLETADA CON ÉXITO." "Green" $Name
    }
    catch {
        Write-DAGLog "FALLO CRÍTICO EN ${Name}: $_" "Red" $Name
        Write-DAGLog "Protocolo DAG detenido. Depura capa por capa." "Yellow" $Name
        Break
    }
}

# STAGE 0: PRE-FLIGHT AUDIT
Invoke-DAGStage -Name "STAGE 0: PRE-FLIGHT AUDIT" -Description "Validar permisos de Administrador y montaje de la nube G:" -Action {
    $IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $IsAdmin) {
        throw "El script requiere permisos de Administrador elevados."
    }
    Write-DAGLog "Privilegios de Administrador confirmados." "Green" "STAGE 0"

    $CloudDrive = Get-PSDrive -Name "G" -ErrorAction SilentlyContinue
    if ($CloudDrive) {
        $FreeGB = [math]::Round($CloudDrive.Free / 1GB, 2)
        Write-DAGLog "Unidad de nube G: detectada y en línea ($FreeGB GB libres)." "Green" "STAGE 0"
    } else {
        Write-DAGLog "Unidad G: no detectada. Trabajando en modo local." "Yellow" "STAGE 0"
    }
}

# STAGE 1: LIMPIEZA Y COMPACTACIÓN
Invoke-DAGStage -Name "STAGE 1: LIMPIEZA Y COMPACTACIÓN" -Description "Liberar temporales y compactar VHDX de WSL/Docker" -Action {
    Write-DAGLog "Vaciando temporales de sesión..." "Gray" "STAGE 1"
    Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
    Clear-RecycleBin -Force -ErrorAction SilentlyContinue

    Write-DAGLog "Deteniendo instancias de WSL..." "Yellow" "STAGE 1"
    wsl --shutdown

    $VhdxPath = "$env:LOCALAPPDATA\Docker\wsl\disk\docker_data.vhdx"
    if (Test-Path $VhdxPath) {
        $SizeGB = [math]::Round((Get-Item$VhdxPath).Length / 1GB, 2)
        Write-DAGLog "Compactando $VhdxPath ($SizeGB GB)..." "Cyan" "STAGE 1"
        
        $TmpFile = Join-Path$env:TEMP "compact_disk.txt"
        "select vdisk file=`"$VhdxPath`"`nattach vdisk readonly`ncompact vdisk`ndetach vdisk" | Set-Content -Path $TmpFile -Encoding ASCII
        diskpart /s $TmpFile | Out-Null
        Remove-Item $TmpFile -Force -ErrorAction SilentlyContinue
        Write-DAGLog "VHDX compactado y desvinculado correctamente." "Green" "STAGE 1"
    } else {
        Write-DAGLog "No se encontró el contenedor VHDX. Omitiendo." "DarkGray" "STAGE 1"
    }
}

# STAGE 2: REACTIVACIÓN Y LEVANTAMIENTO
Invoke-DAGStage -Name "STAGE 2: INFRAESTRUCTURA DE SERVICIOS" -Description "Reiniciar WSL, Docker Engine y contenedores" -Action {
    Write-DAGLog "Reactivando subsistema WSL..." "Cyan" "STAGE 2"
    wsl --status | Out-Null

    $DockerRunning = docker info 2>$null
    if (-not $DockerRunning) {
        Write-DAGLog "Arrancando Docker Desktop..." "Yellow" "STAGE 2"
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 12
    }

    $ProjectDir = "$env:USERPROFILE\hbos-deploy\hbos-vector-engine"
    if (Test-Path "$ProjectDir\docker-compose.yml") {
        Write-DAGLog "Levantando servicios definidos en compose..." "Cyan" "STAGE 2"
        Set-Location $ProjectDir
        docker compose up -d
        Write-DAGLog "Contenedores Docker levantados." "Green" "STAGE 2"
    } else {
        Write-DAGLog "No hay docker-compose.yml en $ProjectDir. Saltando orquestación." "DarkGray" "STAGE 2"
    }
}

# STAGE 3: ESCANEO Y PROBING DE PUERTOS
Invoke-DAGStage -Name "STAGE 3: PORT PROBING & HEALTH" -Description "Inspeccionar endpoints (Ollama, Qdrant, FastAPI HBOS)" -Action {
    $Endpoints = @(
        @{ Port = 11434; Service = "Local LLM (Ollama)"; Required = $false },
        @{ Port = 6333;  Service = "Qdrant REST API";     Required = $true },
        @{ Port = 6334;  Service = "Qdrant gRPC API";     Required = $false },
        @{ Port = 8000;  Service = "HBOS FastAPI Engine"; Required = $false }
    )

    foreach ($ep in $Endpoints) {
        $IsOpen = (Test-NetConnection -ComputerName "localhost" -Port $ep.Port -InformationLevel Quiet -WarningAction SilentlyContinue)
        if ($IsOpen) {
            Write-DAGLog "[OPEN] Puerto $($ep.Port) ($($ep.Service)): EN LÍNEA." "Green" "STAGE 3"
        } else {
            if ($ep.Required) {
                throw "El servicio crítico $($ep.Service) en el puerto $($ep.Port) no responde."
            } else {
                Write-DAGLog "[CLOSED] Puerto $($ep.Port) ($($ep.Service)): Inactivo (Opcional)." "DarkGray" "STAGE 3"
            }
        }
    }
}

# STAGE 4: AUDITORÍA DE ARCHIVOS E INTEGRIDAD
Invoke-DAGStage -Name "STAGE 4: AUDITORÍA DE ARCHIVOS" -Description "Validar estructura .env, manifiestos y empaquetado" -Action {
    $ProjectDir = "$env:USERPROFILE\hbos-deploy\hbos-vector-engine"
    $MandatoryFiles = @(".env", "package.json")

    foreach ($file in $MandatoryFiles) {
        $Path = Join-Path $ProjectDir $file
        if (Test-Path $Path) {
            $Size = (Get-Item $Path).Length
            Write-DAGLog "[INTEGRIDAD OK] $file presente ($Size bytes)." "Green" "STAGE 4"
        } else {
            Write-DAGLog "[ADVERTENCIA] Falta el archivo: $file" "Yellow" "STAGE 4"
        }
    }
}

# STAGE 5: REPORTE FORENSE FINAL
Invoke-DAGStage -Name "STAGE 5: REPORTE FORENSE FINAL" -Description "Resumen global de recursos y cierre del protocolo" -Action {
    $DiskC = Get-PSDrive C
    $UsedC = [math]::Round($DiskC.Used / 1GB, 2)
    $FreeC = [math]::Round($DiskC.Free / 1GB, 2)

    Write-Host "`n========================================================" -ForegroundColor Green
    Write-Host "     HBOS MASTER PROTOCOL: EJECUCIÓN SATISFACTORIA      " -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host "Disco Local C: $UsedC GB en uso / $FreeC GB libres." -ForegroundColor White
    
    $DiskG = Get-PSDrive G -ErrorAction SilentlyContinue
    if ($DiskG) {
        $UsedG = [math]::Round($DiskG.Used / 1GB, 2)
        $FreeG = [math]::Round($DiskG.Free / 1GB, 2)
        Write-Host "Nube G: $UsedG GB en uso / $FreeG GB libres." -ForegroundColor White
    }

    Write-Host "`nPara operar el motor ejecuta:" -ForegroundColor Yellow
    Write-Host "  hbos-run 'tu tarea' 'auto:reasoning'`n" -ForegroundColor White
}
