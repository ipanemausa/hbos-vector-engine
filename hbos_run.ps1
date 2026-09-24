# HBOS · Función de consulta con routing automático
function hbos-run {
    param(
        [string]$Tarea,
        [string]$Cadena = "auto"
    )
    
    $headers = @{
        "Authorization" = "Bearer freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        model = $Cadena
        messages = @(@{ role = "user"; content = $Tarea })
    } | ConvertTo-Json -Compress
    
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:3001/v1/chat/completions" `
            -Method POST -Headers $headers -Body $body -UseBasicParsing -TimeoutSec 60
        
        $res = $r.Content | ConvertFrom-Json
        Write-Host "Modelo: $($res.model) | Ruta: $($res._routed_via.platform)" -ForegroundColor Gray
        Write-Host $res.choices[0].message.content -ForegroundColor White
    } catch {
        Write-Host "FAIL: $_" -ForegroundColor Red
    }
}

# Alias
Set-Alias -Name hbos -Value hbos-run -Force

Write-Host "[HBOS] Funcion hbos-run cargada" -ForegroundColor Green
Write-Host "[HBOS] Uso: hbos-run 'tu tarea' 'auto:reasoning'" -ForegroundColor Gray
