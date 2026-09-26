# ═══════════════════════════════════════════════════════════════════
# HBOS · DRIFT DIAGNOSIS ONLY · READ-ONLY · NO COMMITS · NO BACKUPS
# ═══════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$root    = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
$ts      = Get-Date -Format "yyyyMMdd-HHmmss"
$logDir  = Join-Path $root "logs"
$logFile = Join-Path $logDir "op315-drift-$ts.log"
$driftReport = Join-Path $logDir "hbos-op315-drift-$ts.md"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Log {
    param([string]$msg,[string]$color="White")
    Write-Host $msg -ForegroundColor $color
    Add-Content -Path $logFile -Value "$(Get-Date -Format 'HH:mm:ss') | $msg" -Encoding UTF8
}

$kiroLocalKey = "hbos-kiro-local-key-2026"
$yesterdayReference = 326

Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "HBOS · DRIFT DIAGNOSIS · READ-ONLY · $ts" "Cyan"
Log "═══════════════════════════════════════════════════════════════" "Cyan"

# ─── 1. Git state ────────────────────────────────────────────────
Log "`n[1] GIT STATE" "Cyan"
Log "  commit: $(git -C $root log -1 --oneline)" "White"
$gitStatus = git -C $root status --porcelain
Log "  uncommitted files: $(($gitStatus | Measure-Object).Count)" "White"
$gitStatus | Select-Object -First 20 | ForEach-Object { Log "    $_" "White" }

# ─── 2. FreeLLMAPI runtime (with auth) ───────────────────────────
Log "`n[2] FREELLMAPI /v1/models (no filter)" "Cyan"
$keyPath = Join-Path $root "config\freellmapi-key.txt"
$key = (Get-Content $keyPath -Raw).Trim()
$hdr = @{ Authorization = "Bearer $key" }
$all = Invoke-RestMethod -Uri "http://127.0.0.1:3001/v1/models" -Headers $hdr -TimeoutSec 10
$runtimeCount = $all.data.Count
Log "  runtime total: $runtimeCount" "Green"

# ─── 3. By category ──────────────────────────────────────────────
Log "`n[3] FREELLMAPI by category" "Cyan"
$cats = @{}
foreach ($c in @("chat","embeddings","image","video","audio","fusion")) {
    try {
        $r = Invoke-RestMethod -Uri "http://127.0.0.1:3001/v1/models?category=$c" -Headers $hdr -TimeoutSec 8
        $cats[$c] = $r.data.Count
        Log "  $c : $($r.data.Count)" "White"
    } catch {
        $cats[$c] = -1
        Log "  $c : error (endpoint may not support filter)" "Yellow"
    }
}

# ─── 4. Kiro ─────────────────────────────────────────────────────
Log "`n[4] KIRO /v1/models" "Cyan"
$kiroCount = 0
$kiroIds = @()
try {
    $khdr = @{ Authorization = "Bearer $kiroLocalKey" }
    $k = Invoke-RestMethod -Uri "http://127.0.0.1:10088/v1/models" -Headers $khdr -TimeoutSec 10
    $kiroCount = $k.data.Count
    $kiroIds = $k.data | ForEach-Object { $_.id }
    Log "  kiro count: $kiroCount" "Green"
    $kiroIds | ForEach-Object { Log "    - $_" "White" }
} catch {
    Log "  kiro ERROR: $_" "Red"
}

# ─── 5. freeapi.db ───────────────────────────────────────
Log "`n[5] FREEAPI.DB CATALOG" "Cyan"
$dbPath = "$env:APPDATA\FreeLLMAPI\freeapi.db"
if (Test-Path $dbPath) {
    $py = @"
import sqlite3
c = sqlite3.connect(r'$dbPath').cursor()
c.execute('SELECT COUNT(*) FROM models'); print('  catalog total:', c.fetchone()[0])
c.execute('SELECT COUNT(*) FROM models WHERE enabled=1'); print('  catalog enabled:', c.fetchone()[0])
try:
    c.execute('SELECT platform, COUNT(*) FROM models GROUP BY platform')
    for row in c.fetchall(): print('  platform', row[0], '=', row[1])
except Exception as e: print('  platform query err:', e)
try:
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print('  tables:', [r[0] for r in c.fetchall()])
except Exception as e: print('  tables err:', e)
"@
    $py | Out-File -FilePath (Join-Path $logDir "drift-db-$ts.py") -Encoding UTF8
    python (Join-Path $logDir "drift-db-$ts.py")
} else {
    Log "  freeapi.db not found at $dbPath" "Red"
}

# ─── 6. Backup check ─────────────────────────────────────────────
Log "`n[6] YESTERDAY BACKUP" "Cyan"
$bkp = Join-Path $root "_BACKUPS\hbos-op314-final-20260925-211156.zip"
if (Test-Path $bkp) {
    $sz = (Get-Item $bkp).Length
    Log "  exists ($([math]::Round($sz/1GB,2)) GB)" "Green"
} else {
    Log "  MISSING: $bkp" "Red"
}
Log "  other recent backups:" "White"
Get-ChildItem (Join-Path $root "_BACKUPS") -Filter "*.zip" -ErrorAction SilentlyContinue | 
    Sort-Object LastWriteTime -Descending | Select-Object -First 5 | 
    ForEach-Object { Log "    $($_.Name) · $([math]::Round($_.Length/1GB,2)) GB · $($_.LastWriteTime)" "White" }

# ─── 7. Drift computation ────────────────────────────────────────
Log "`n[7] DRIFT" "Cyan"
$composite = $runtimeCount + $kiroCount
$drift = $composite - $yesterdayReference
Log "  runtime: $runtimeCount" "White"
Log "  kiro:    $kiroCount" "White"
Log "  composite: $composite" "Yellow"
Log "  yesterday: $yesterdayReference" "Yellow"
Log "  DRIFT: $drift" $(if([math]::Abs($drift) -gt 10){"Red"}else{"Green"})

# ─── 8. Write report ─────────────────────────────────────────────
$rep = @(
    "# Drift Report · op=315 · $ts",
    "",
    "## Summary",
    "- Yesterday reference: $yesterdayReference",
    "- FreeLLMAPI runtime: $runtimeCount",
    "- Kiro: $kiroCount",
    "- Composite today: $composite",
    "- DRIFT: $drift",
    "",
    "## Category breakdown",
    ""
)
foreach ($k in $cats.Keys) { $rep += "- $k : $($cats[$k])" }
$rep += ""
$rep += "## Kiro models"
foreach ($id in $kiroIds) { $rep += "- $id" }
Set-Content -Path $driftReport -Value ($rep -join "`n") -Encoding UTF8

Log "`n═══════════════════════════════════════════════════════════════" "Cyan"
Log "DRIFT DIAGNOSIS COMPLETE" "Cyan"
Log "Report: $driftReport" "Cyan"
Log "Log:    $logFile" "Cyan"
Log "→ paste raw output back to chat" "Yellow"
Log "→ NOTHING WAS WRITTEN · NOTHING WAS COMMITTED" "Green"
Log "═══════════════════════════════════════════════════════════════" "Cyan"
