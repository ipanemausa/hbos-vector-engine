# HBOS op=315 · PERMANENT CANONICAL SEAL (launcher) - no prompts, no pipes, no secrets in text.
$ErrorActionPreference = "Stop"
$root = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
$keyFile = Join-Path $root "config\freellmapi-key.txt"
$core = Join-Path $root "scripts\op315_permanent_seal.py"
$env:PYTHONIOENCODING = "utf-8"

if (-not (Test-Path $keyFile)) { throw "ABORT: $keyFile missing (run guardar-key.ps1 once)" }
$key = [System.IO.File]::ReadAllText($keyFile).Trim()
if ($key.Length -lt 20) { throw "ABORT: key file looks empty" }

# 1) Persist at OS level (User registry) + current process
$vars = [ordered]@{
    FREELLMAPI_KEY = $key
    FREELLMAPI_URL = "http://127.0.0.1:3001"
    QDRANT_URL     = "http://127.0.0.1:6333"
}
foreach ($name in $vars.Keys) {
    [Environment]::SetEnvironmentVariable($name, $vars[$name], "User")
    Set-Item -Path ("Env:" + $name) -Value $vars[$name]
}
Write-Host "[ENV] User-scope persisted: FREELLMAPI_KEY (len $($key.Length)), FREELLMAPI_URL, QDRANT_URL" -ForegroundColor Green

# 2) Snapshot + L0.6 by chains/anchor + L0.7 EXCLUDED + ledger pre-seal
& python $core prepare
if ($LASTEXITCODE -ne 0) { throw "ABORT: L0.6 (10 chains + HBOS anchor) not met, ledger NOT sealed (exit $LASTEXITCODE)" }

# 3) Biometric capture, seal only on success
& python (Join-Path $root "solicitar_huella.py")
if ($LASTEXITCODE -ne 0) { throw "ABORT: biometric not confirmed, ledger left unsealed (pending file kept)" }

# 4) Seal + NotebookLM export
& python $core seal
if ($LASTEXITCODE -ne 0) { throw "ABORT: seal step failed (exit $LASTEXITCODE)" }
Write-Host "[OK] OP=315 sealed. Upload the *-PERM-SEAL-*.md in logs\ to NotebookLM." -ForegroundColor Cyan
