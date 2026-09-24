# HBOS · Funciones portables
function hbos-chat {
    param([Parameter(Mandatory=$true)][string]$prompt, [string]$model = "auto")
    $body = @{ model = $model; messages = @(@{ role = "user"; content = $prompt }) } | ConvertTo-Json -Depth 5 -Compress
    $headers = @{ "Authorization" = "Bearer freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037"; "Content-Type" = "application/json" }
    try {
        Invoke-WebRequest -Uri "http://127.0.0.1:3001/v1/chat/completions" -Method POST -Headers $headers -Body $body -UseBasicParsing | Select-Object -ExpandProperty Content
    } catch { Write-Host "[HBOS] Error hbos-chat: $($_.Exception.Message)" -ForegroundColor Red }
}

function hbos-estado {
    $py = "C:\Users\ipane\AppData\Local\Programs\Python\Python313\python.exe"
    if (-not (Test-Path $py)) { $py = "python" }
    $dbPath = "$env:APPDATA\FreeLLMAPI\freeapi.db"
    if (-not (Test-Path $dbPath)) { Write-Host "[HBOS] DB no encontrada" -ForegroundColor Red; return }
    & $py -c @"
import sqlite3
c = sqlite3.connect(r'$dbPath').cursor()
c.execute('SELECT COUNT(*) FROM api_keys WHERE enabled=1'); p = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM models'); m = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM profiles'); pr = c.fetchone()[0]
print(f'  Providers: {p} | Modelos: {m} | Profiles: {pr}')
"@
}

function hbos-ops {
    $py = "C:\Users\ipane\AppData\Local\Programs\Python\Python313\python.exe"
    if (-not (Test-Path $py)) { $py = "python" }
    $dbPath = "$env:APPDATA\FreeLLMAPI\freeapi.db"
    if (-not (Test-Path $dbPath)) { return }
    & $py -c @"
import sqlite3
c = sqlite3.connect(r'$dbPath').cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%op%'")
print('  Tablas op:', [r[0] for r in c.fetchall()])
"@
}
