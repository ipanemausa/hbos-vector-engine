<#
.SYNOPSIS
    Test completo del sistema HBOS-FreeLLMAPI.
.DESCRIPTION
    Verifica autenticacion, prueba los 9 providers healthy, prueba 5 modelos
    especificos y genera un reporte JSON con latencias y estados.
.NOTES
    Autocontenido. Sin dependencias externas. PowerShell 5.1+ / 7+.
#>

[CmdletBinding()]
param(
    [string]$BaseUrl   = 'http://127.0.0.1:3001/v1',
    [string]$ApiKey    = '$env:FREELLMAPI_KEY',
    [string]$ProjectRoot = 'C:\Users\ipane\hbos-deploy\hbos-vector-engine',
    [int]$TimeoutSec   = 20
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

function Write-Header([string]$Text) {
    Write-Host ''
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ('=' * 78) -ForegroundColor DarkCyan
}
function Write-Ok   ([string]$t) { Write-Host "  [OK]   $t" -ForegroundColor Green }
function Write-Ko   ([string]$t) { Write-Host "  [KO]   $t" -ForegroundColor Red }
function Write-Warn ([string]$t) { Write-Host "  [WARN] $t" -ForegroundColor Yellow }
function Write-Info ([string]$t) { Write-Host "  [INFO] $t" -ForegroundColor Gray }

$script:Headers = @{
    'Authorization' = "Bearer $ApiKey"
    'Content-Type'  = 'application/json'
    'Accept'        = 'application/json'
}

function Invoke-ApiRequest {
    param(
        [Parameter(Mandatory)][string]$Method,
        [Parameter(Mandatory)][string]$Path,
        [object]$Body = $null
    )
    $uri = "$BaseUrl$Path"
    $sw  = [System.Diagnostics.Stopwatch]::StartNew()
    $result = [ordered]@{
        ok         = $false
        status     = 0
        latency_ms = 0
        body       = $null
        raw        = $null
        error      = $null
    }
    try {
        $params = @{
            Uri             = $uri
            Method          = $Method
            Headers         = $script:Headers
            TimeoutSec      = $TimeoutSec
            UseBasicParsing = $true
        }
        if ($null -ne $Body) {
            $params['Body'] = ($Body | ConvertTo-Json -Depth 10 -Compress)
        }
        $resp = Invoke-WebRequest @params
        $sw.Stop()
        $result.status     = [int]$resp.StatusCode
        $result.latency_ms = [int]$sw.ElapsedMilliseconds
        $result.raw        = $resp.Content
        try { $result.body = $resp.Content | ConvertFrom-Json } catch { $result.body = $null }
        $result.ok = ($result.status -ge 200 -and $result.status -lt 300)
    }
    catch {
        $sw.Stop()
        $result.latency_ms = [int]$sw.ElapsedMilliseconds
        $result.error      = $_.Exception.Message
        if ($_.Exception.Response) {
            try { $result.status = [int]$_.Exception.Response.StatusCode } catch { $result.status = -1 }
            try {
                $stream = $_.Exception.Response.GetResponseStream()
                if ($stream) {
                    $reader = New-Object System.IO.StreamReader($stream)
                    $result.raw = $reader.ReadToEnd()
                    $reader.Close()
                    try { $result.body = $result.raw | ConvertFrom-Json } catch {}
                }
            } catch {}
        } else {
            $result.status = -1
        }
    }
    return [pscustomobject]$result
}

function Get-ChatContent($body) {
    if ($null -eq $body) { return $null }
    try {
        if ($body.choices -and $body.choices.Count -gt 0) {
            $msg = $body.choices[0].message
            if ($msg -and $msg.content) { return [string]$msg.content }
            if ($body.choices[0].text) { return [string]$body.choices[0].text }
        }
    } catch {}
    return $null
}

function Shorten([string]$s, [int]$max = 80) {
    if ([string]::IsNullOrEmpty($s)) { return '' }
    $s = $s -replace '\s+', ' '
    if ($s.Length -le $max) { return $s }
    return $s.Substring(0, $max - 3) + '...'
}

$Providers = @(
    @{ id = 10; platform = 'openrouter';  label = 'HBOS OpenRouter Key';        model = 'meta-llama/llama-3.3-70b-instruct:free' }
    @{ id = 12; platform = 'google';      label = 'HBOS Google Gemini Key';     model = 'gemini-2.5-flash' }
    @{ id = 13; platform = 'huggingface'; label = 'HBOS HuggingFace Hub Token'; model = 'meta-llama/Llama-3.2-3B-Instruct' }
    @{ id = 14; platform = 'ollama';      label = 'HBOS Ollama Local';          model = 'gpt-oss:120b' }
    @{ id = 15; platform = 'kilo';        label = 'FreeLLMAPI KILO Free Tier';  model = 'nvidia/nemotron-3-ultra-550b-a55b:free' }
    @{ id = 16; platform = 'ovh';         label = 'FreeLLMAPI OVH Free Tier';   model = 'Qwen3.5-397B-A17B' }
    @{ id = 17; platform = 'llm7';        label = 'FreeLLMAPI LLM7 Free Tier';  model = 'codestral-latest' }
    @{ id = 18; platform = 'groq';        label = 'HBOS Groq Key (Ultra-Fast)'; model = 'groq/compound' }
    @{ id = 19; platform = 'github';      label = 'HBOS GitHub Models';         model = 'openai/gpt-oss-20b' }
)

$SpecificModels = @(
    'gemini-2.5-flash',
    '@cf/meta/llama-3.3-70b-instruct-fp8-fast',
    'groq/compound',
    'gpt-oss:120b',
    'nvidia/nemotron-3-ultra-550b-a55b:free'
)

$TestPrompt = 'Responde unicamente con la palabra: PONG'

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$report = [ordered]@{
    timestamp       = (Get-Date).ToString('o')
    base_url        = $BaseUrl
    project_root    = $ProjectRoot
    auth_test       = $null
    provider_tests  = @()
    model_tests     = @()
    summary         = [ordered]@{
        auth_ok              = $false
        models_count         = 0
        providers_ok         = 0
        providers_ko         = 0
        models_ok            = 0
        models_ko            = 0
    }
}

Write-Header '1) TEST DE AUTENTICACION - GET /v1/models'
$authResp = Invoke-ApiRequest -Method 'GET' -Path '/models'
$modelsCount = 0
$modelsList  = @()

if ($authResp.ok -and $authResp.body -and $authResp.body.data) {
    $modelsList  = @($authResp.body.data)
    $modelsCount = $modelsList.Count
    Write-Ok "Autenticacion correcta (HTTP $($authResp.status)) - $modelsCount modelos - $($authResp.latency_ms) ms"
    if ($modelsCount -ge 200) {
        Write-Ok "Modelos devueltos >= 200 [ESPERADO: 316]"
        $report.summary.auth_ok = $true
    } else {
        Write-Warn "Modelos devueltos < 200 ($modelsCount). Revisar DB."
    }
} else {
    Write-Ko "Fallo autenticacion: HTTP $($authResp.status) - $($authResp.error)"
}

$report.auth_test = [ordered]@{
    status     = $authResp.status
    latency_ms = $authResp.latency_ms
    ok         = $authResp.ok
    models     = $modelsCount
    error      = $authResp.error
}
$report.summary.models_count = $modelsCount

Write-Header '2) TEST POR PROVIDER (9 healthy)'
foreach ($p in $Providers) {
    $payload = @{
        model    = $p.model
        messages = @(@{ role = 'user'; content = $TestPrompt })
        max_tokens = 16
        stream   = $false
    }
    $r = Invoke-ApiRequest -Method 'POST' -Path '/chat/completions' -Body $payload
    $content = Get-ChatContent $r.body
    $status = if ($r.ok -and $content) { 'OK' } else { 'KO' }
    $color  = if ($status -eq 'OK') { 'Green' } else { 'Red' }
    $line   = "{0,-14} {1,-45} {2,6} ms  {3}" -f $p.platform, $p.model, $r.latency_ms, $status
    Write-Host "  $line" -ForegroundColor $color
    if ($status -eq 'KO') {
        $errMsg = if ($r.error) { $r.error } else { "HTTP $($r.status)" }
        Write-Info "    -> $errMsg"
        if ($r.body.error.message) { Write-Info "    -> $($r.body.error.message)" }
    } else {
        Write-Info "    -> $(Shorten $content 100)"
    }
    $report.provider_tests += [ordered]@{
        provider_id = $p.id; platform = $p.platform; label = $p.label
        model = $p.model; status = $status; http_status = $r.status
        latency_ms = $r.latency_ms; response = $content; error = $r.error
    }
    if ($status -eq 'OK') { $report.summary.providers_ok++ } else { $report.summary.providers_ko++ }
}

Write-Header '3) TEST DE MODELOS ESPECIFICOS'
foreach ($m in $SpecificModels) {
    $payload = @{
        model    = $m
        messages = @(@{ role = 'user'; content = $TestPrompt })
        max_tokens = 16
        stream   = $false
    }
    $r = Invoke-ApiRequest -Method 'POST' -Path '/chat/completions' -Body $payload
    $content = Get-ChatContent $r.body
    $status = if ($r.ok -and $content) { 'OK' } else { 'KO' }
    $color  = if ($status -eq 'OK') { 'Green' } else { 'Red' }
    $line   = "{0,-55} {1,6} ms  {2}" -f $m, $r.latency_ms, $status
    Write-Host "  $line" -ForegroundColor $color
    if ($status -eq 'KO') {
        $errMsg = if ($r.error) { $r.error } else { "HTTP $($r.status)" }
        Write-Info "    -> $errMsg"
        if ($r.body.error.message) { Write-Info "    -> $($r.body.error.message)" }
    } else {
        Write-Info "    -> $(Shorten $content 100)"
    }
    $report.model_tests += [ordered]@{
        model = $m; status = $status; http_status = $r.status
        latency_ms = $r.latency_ms; response = $content; error = $r.error
    }
    if ($status -eq 'OK') { $report.summary.models_ok++ } else { $report.summary.models_ko++ }
}

Write-Header '4) REPORTE FINAL'
$allRows = @()
foreach ($t in $report.provider_tests) {
    $allRows += [pscustomobject]@{ Modelo=$t.model; Provider=$t.platform; LatenciaMs=$t.latency_ms; Status=$t.status; Respuesta=Shorten $t.response 35 }
}
foreach ($t in $report.model_tests) {
    $allRows += [pscustomobject]@{ Modelo=$t.model; Provider='(specific)'; LatenciaMs=$t.latency_ms; Status=$t.status; Respuesta=Shorten $t.response 35 }
}
if ($allRows.Count -gt 0) { $allRows | Format-Table -AutoSize | Out-String -Width 220 | Write-Host }

Write-Host ''
Write-Host "  RESUMEN:" -ForegroundColor Cyan
Write-Host ("    Auth OK          : {0}" -f $report.summary.auth_ok) -ForegroundColor Gray
Write-Host ("    Modelos API      : {0} (DB=316)" -f $report.summary.models_count) -ForegroundColor Gray
Write-Host ("    Providers OK/KO  : {0}/{1}" -f $report.summary.providers_ok, $report.summary.providers_ko) -ForegroundColor Gray
Write-Host ("    Modelos  OK/KO   : {0}/{1}" -f $report.summary.models_ok, $report.summary.models_ko) -ForegroundColor Gray

$backupDir = Join-Path $ProjectRoot '_BACKUPS'
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
$reportPath = Join-Path $backupDir "test_report_$timestamp.json"
try {
    $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Ok "Reporte guardado: $reportPath"
} catch {
    Write-Ko "Error guardando reporte: $($_.Exception.Message)"
}
Write-Host ''
Write-Host '  Test completado.' -ForegroundColor Cyan

