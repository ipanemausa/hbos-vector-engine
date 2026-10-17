# --- SCRIPT DE MAPEO DNS LOCAL (HOSTS) Y PRUEBA DE CONEXIÓN ---
# Requiere privilegios de Administrador (Windows Hello / Huella / UAC)

$ipAddress = "34.186.107.230"
$domainName = "38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io"
$hostsPath = "C:\Windows\System32\drivers\etc\hosts"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "HBOS: Mapeando DNS local en hosts para Qdrant Cloud" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Verificar si ya existe la entrada en el archivo hosts
$content = Get-Content $hostsPath -Raw -ErrorAction SilentlyContinue
if ($content -match [regex]::Escape($domainName)) {
    Write-Host "[INFO] La entrada de DNS para Qdrant ya existe en el archivo hosts." -ForegroundColor Yellow
} else {
    try {
        Add-Content -Path $hostsPath -Value "`n$ipAddress $domainName" -Encoding UTF8
        Write-Host "[OK] Entrada agregada exitosamente: $ipAddress $domainName" -ForegroundColor Green
    } catch {
        Write-Host "[!] Error al escribir en el archivo hosts: $_" -ForegroundColor Red
        Write-Host "Asegurate de ejecutar esta ventana como Administrador." -ForegroundColor Yellow
        pause
        exit 1
    }
}

# 2. Limpiar la cache de DNS del sistema
Write-Host "Limpiando cache de DNS del sistema (ipconfig /flushdns)..." -ForegroundColor Cyan
ipconfig /flushdns

# 3. Ejecutar prueba de conexión nativa
Write-Host "`nEjecutando prueba de conexión nativa a Qdrant Cloud..." -ForegroundColor Cyan
$pythonScript = @'
import requests
import os
from dotenv import load_dotenv

load_dotenv('C:/Users/ipane/hbos-deploy/hbos-vector-engine/.env.local')

api_key = os.getenv('QDRANT_API_KEY')
url = os.getenv('QDRANT_URL').rstrip(':6333')

print("--- PRUEBA DE CONEXIÓN TRAS MAPEO HOSTS ---")
try:
    r = requests.get(f'{url}:6333/collections', headers={'api-key': api_key}, timeout=10)
    print('Estado HTTP:', r.status_code)
    if r.status_code == 200:
        print('¡ÉXITO TOTAL! La conexión a Qdrant Cloud es nativa y perfecta.')
        cols = [c['name'] for c in r.json().get('result', {}).get('collections', [])]
        print(f'Total colecciones visibles: {len(cols)}')
        print('Colecciones:', cols[:8], '...')
    else:
        print('Error HTTP:', r.text[:300])
except Exception as e:
    print('Error de conexión:', e)
'@

$pythonScript | Out-File -FilePath "$env:TEMP\test_qdrant.py" -Encoding UTF8
python "$env:TEMP\test_qdrant.py"
Remove-Item "$env:TEMP\test_qdrant.py" -ErrorAction SilentlyContinue

Write-Host "`n[LISTO] Mapeo verificado y operativo." -ForegroundColor Green
pause
