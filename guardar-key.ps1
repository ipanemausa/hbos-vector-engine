# guardar-key.ps1
# Lee la key del portapapeles y la inyecta en:
#   1. config\freellmapi-key.txt
#   2. .env (variable FREELLMAPI_KEY)
#   3. gateway_config.json (upstreams.freellmapi.api_key)
#   4. $env:FREELLMAPI_KEY (sesion actual)

$key = (Get-Clipboard).Trim()

if ($key -notlike "freellmapi-*") {
    Write-Host "[KO] Portapapeles sin key freellmapi-. Longitud: $($key.Length)" -ForegroundColor Red
    exit 1
}

$root = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"

# 1. freellmapi-key.txt
$null = New-Item -ItemType Directory -Force -Path "$root\config"
$key | Out-File "$root\config\freellmapi-key.txt" -Encoding utf8 -NoNewline
Write-Host "[OK] freellmapi-key.txt" -ForegroundColor Green

# 2. .env (anade o reemplaza FREELLMAPI_KEY)
$envFile = "$root\.env"
if (Test-Path $envFile) {
    $content = Get-Content $envFile -Raw
    if ($content -match "FREELLMAPI_KEY=") {
        $content = $content -replace "FREELLMAPI_KEY=.*", "FREELLMAPI_KEY=`"$key`""
    } else {
        $content = $content.TrimEnd() + "`nFREELLMAPI_KEY=`"$key`"`n"
    }
} else {
    $content = "FREELLMAPI_KEY=`"$key`"`n"
}
Set-Content -Path $envFile -Value $content -Encoding UTF8
Write-Host "[OK] .env" -ForegroundColor Green

# 3. gateway_config.json
$gwFile = "$root\gateway_config.json"
if (Test-Path $gwFile) {
    $json = Get-Content $gwFile -Raw | ConvertFrom-Json
    if ($json.upstreams.freellmapi) {
        $json.upstreams.freellmapi.api_key = $key
    }
    $json | ConvertTo-Json -Depth 10 | Set-Content -Path $gwFile -Encoding UTF8
    Write-Host "[OK] gateway_config.json" -ForegroundColor Green
}

# 4. sesion actual
$env:FREELLMAPI_KEY = $key
Write-Host "[OK] `$env:FREELLMAPI_KEY" -ForegroundColor Green

Write-Host "`n[OK] Key inyectada en 4 destinos. Longitud: $($key.Length)" -ForegroundColor Cyan
