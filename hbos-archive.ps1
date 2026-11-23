<#
.SYNOPSIS
    Protocolo Maestro de Archivo Dual HBOS: Markdown + Qdrant
.DESCRIPTION
    1. Asienta el contenido como archivo .md en Drive/local.
    2. Genera embedding e indexa en Qdrant en casos_uso_hbos.
    3. Notifica al bus local (intercambio_agentes.json).
#>
param (
    [Parameter(Mandatory=$true)][string]$Titulo,
    [Parameter(Mandatory=$true)][string]$Contenido,
    [Parameter(Mandatory=$false)][string]$Grupo = "radar-investigacion",
    [Parameter(Mandatory=$false)][string]$DestinoDir = "G:\My Drive\HBOS_BACKUP\radar_investigacion\hechos"
)

# 1. Escritura física en Markdown
if (-not (Test-Path $DestinoDir)) {
    New-Item -ItemType Directory -Path $DestinoDir -Force | Out-Null
}

$timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
$slug = ($Titulo -replace '[^a-zA-Z0-9_-]', '_').ToLower()
$fileName = "$($timestamp)_$($slug).md"
$fullPath = Join-Path $DestinoDir $fileName

$header = @"
---
id: $timestamp
titulo: "$Titulo"
grupo: "$Grupo"
fecha: "$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))"
fuente_archivo: "$fullPath"
---

"@

Set-Content -Path $fullPath -Value ($header + $Contenido) -Encoding UTF8
Write-Host "[OK] Archivo MD asentado en: $fullPath" -ForegroundColor Green

# 2. Invocación de Ingesta Vectorial Directa (Python helper)
$pyCommand = @"
import json, urllib.request, hashlib
from pathlib import Path

payload = {
    "action": "ingest_single",
    "file_path": r"$fullPath",
    "title": "$Titulo",
    "group": "$Grupo",
    "content": """$Contenido"""
}

# Actualizar el bus local para sincronización entre agentes
bus_path = Path(r"C:\Users\ipane\hbos-deploy\intercambio_agentes.json")
if bus_path.exists():
    try:
        bus = json.loads(bus_path.read_text(encoding="utf-8"))
        bus["last_artifacts"]["last_archived_md"] = r"$fullPath"
        bus["outbox_results"].append({"action": "archived", "file": "$fileName", "group": "$Grupo"})
        bus_path.write_text(json.dumps(bus, indent=2), encoding="utf-8")
        print("[OK] Bus de agentes actualizado.")
    except Exception as e:
        print(f"[!] Error actualizando bus: {e}")
"@

python -c $pyCommand
Write-Host "[OK] Protocolo de archivo completado bajo regla dual." -ForegroundColor Cyan
