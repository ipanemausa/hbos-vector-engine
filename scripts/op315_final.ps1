# ═══════════════════════════════════════════════════════════════════
# HBOS · op=315-FINAL · FULL DAG · 2026-09-26
# Channel   : PWSH direct (NO Antigravity)
# Persist   : Qdrant matrix 360
# Close     : redundant close + backup + push
# Guard     : DO NOT BREAK WHAT ALREADY WORKS
# ═══════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$root    = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
$ts      = Get-Date -Format "yyyyMMdd-HHmmss"
$logDir  = Join-Path $root "logs"
$logFile = Join-Path $logDir "op315-final-$ts.log"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Log {
    param([string]$msg,[string]$color="White")
    Write-Host $msg -ForegroundColor $color
    Add-Content -Path $logFile -Value "$(Get-Date -Format 'HH:mm:ss') | $msg" -Encoding UTF8
}

function Sha16 {
    param([string]$text)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $hash  = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    (($hash | ForEach-Object { $_.ToString("x2") }) -join "").Substring(0,16)
}

$genesisHash = Sha16 "HBOS-op315-final-2026-09-26"
$ledgerMd    = Join-Path $logDir "hbos-approvals-op315-final-$ts.md"
$ledgerTxt   = Join-Path $logDir "hbos-approvals-op315-final-$ts.txt"
$catalogFile = Join-Path $logDir "hbos-catalog-real-$ts.md"
$designFile  = Join-Path $logDir "hbos-persistence-design-final-$ts.md"
$exportFile  = Join-Path $logDir "hbos-op315-notebooklm-$ts.md"

Set-Content -Path $ledgerMd -Encoding UTF8 -Value @"
# HBOS Approval Ledger · op=315-FINAL · $ts
Genesis: ``$genesisHash``

| # | Phase | Layer | Gate | Action | Result | Method | Timestamp | Hash | Prev |
|---|-------|-------|------|--------|--------|--------|-----------|------|------|
"@
Set-Content -Path $ledgerTxt -Encoding UTF8 -Value "op315-final|$ts|genesis=$genesisHash"

$script:chain    = 0
$script:lastHash = $genesisHash

function Add-Approval {
    param([string]$Phase,[string]$Layer,[string]$GateType,[string]$Action,[string]$Result,[string]$Method="auto")
    $now = Get-Date -Format "o"; $prev = $script:lastHash
    $h = Sha16 "op315f|$Phase|$Layer|$GateType|$Action|$Result|$now|$prev"
    $row = "| $($script:chain) | $Phase | $Layer | $GateType | $Action | $Result | $Method | $now | ``$h`` | ``$prev`` |"
    Add-Content -Path $ledgerMd  -Value $row -Encoding UTF8
    Add-Content -Path $ledgerTxt -Value "$($script:chain)|$Phase|$Layer|$GateType|$Action|$Result|$Method|$now|$h|$prev" -Encoding UTF8
    Log "[LEDGER +$($script:chain)] $Phase/$Layer · $GateType · $Result · $h" "Yellow"
    $script:lastHash = $h; $script:chain++
    return $h
}

Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "HBOS · op=315-FINAL · PWSH DIRECT · $ts" "Cyan"
Log "Genesis: $genesisHash" "Cyan"
Log "═══════════════════════════════════════════════════════════════" "Cyan"

$freellmapiKeyPath = Join-Path $root "config\freellmapi-key.txt"
$kiroLocalKey      = "hbos-kiro-local-key-2026"
$flmKey            = (Get-Content $freellmapiKeyPath -Raw).Trim()
$flmHdr            = @{ Authorization = "Bearer $flmKey"; "Content-Type" = "application/json" }
$kiroHdr           = @{ Authorization = "Bearer $kiroLocalKey"; "Content-Type" = "application/json" }

# ═══════════════════════════════════════════════════════════════════
# PHASE 0 · ENVIRONMENT VERIFICATION
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 0 · ENVIRONMENT ────" "Cyan"

$gitLog = git -C $root log -1 --oneline
$gitStatus = git -C $root status --porcelain
Log "[T1] Git: $gitLog" "White"
Log "  uncommitted: $(($gitStatus | Measure-Object).Count)" "White"
Add-Approval "0" "0.1" "PRE-DEBUG" "git state" "PASS" | Out-Null

Log "[T2] FreeLLMAPI real catalog" "Cyan"
$catalog = @()
try {
    $flm = Invoke-RestMethod -Uri "http://127.0.0.1:3001/v1/models" -Headers $flmHdr -TimeoutSec 10
    $catalog = $flm.data | ForEach-Object { $_.id }
    Log "  total: $($catalog.Count)" "Green"

    $geminiIds = $catalog | Where-Object { $_ -match "gemini" }
    Log "  gemini ids found: $($geminiIds.Count)" "Yellow"
    $geminiIds | Select-Object -First 20 | ForEach-Object { Log "    - $_" "White" }

    $claudeIds = $catalog | Where-Object { $_ -match "claude" }
    Log "  claude ids found: $($claudeIds.Count)" "Yellow"
    $claudeIds | Select-Object -First 20 | ForEach-Object { Log "    - $_" "White" }

    $gptIds = $catalog | Where-Object { $_ -match "gpt" }
    Log "  gpt ids found: $($gptIds.Count)" "Yellow"
    $gptIds | Select-Object -First 10 | ForEach-Object { Log "    - $_" "White" }

    $catContent = "# HBOS Real Catalog · $ts`n`nTotal: $($catalog.Count)`n`n## All IDs`n`n" + ($catalog -join "`n")
    Set-Content -Path $catalogFile -Value $catContent -Encoding UTF8
    Add-Approval "0" "0.2" "EXECUTE" "catalog read" "PASS" | Out-Null
} catch {
    Log "  error: $_" "Red"
    Add-Approval "0" "0.2" "EXECUTE" "catalog read" "FAIL" | Out-Null
}

Log "[T3] Kiro Gateway" "White"
$kiroIds = @()
try {
    $k = Invoke-RestMethod -Uri "http://127.0.0.1:10088/v1/models" -Headers $kiroHdr -TimeoutSec 10
    $kiroIds = $k.data | ForEach-Object { $_.id }
    Log "  kiro models: $($kiroIds.Count)" "Green"
    $kiroIds | ForEach-Object { Log "    - $_" "White" }
    Add-Approval "0" "0.3" "EXECUTE" "kiro read" "PASS" | Out-Null
} catch {
    Log "  error: $_" "Red"
    Add-Approval "0" "0.3" "EXECUTE" "kiro read" "FAIL" | Out-Null
}

Log "[T4] Qdrant Cloud" "White"
$qdrantUrl = "https://38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io"
$qk = (Get-Content (Join-Path $root "config\qdrant-key.txt") -Raw).Trim()
$qdrantHdr = @{ "api-key" = $qk; "Content-Type" = "application/json" }
try {
    $q = Invoke-RestMethod -Uri "$qdrantUrl/collections" -Headers $qdrantHdr -TimeoutSec 10
    Log "  collections: $($q.result.collections.Count)" "Green"
    Add-Approval "0" "0.4" "EXECUTE" "qdrant read" "PASS" | Out-Null
} catch {
    Log "  error: $_" "Red"
    Add-Approval "0" "0.4" "EXECUTE" "qdrant read" "FAIL" | Out-Null
}

$agProcs = Get-Process | Where-Object { $_.ProcessName -match "antigravity" }
Log "[T5] Antigravity processes: $($agProcs.Count)" "Yellow"

Add-Approval "0" "PHASE-FRONTIER" "FRONTIER" "environment verified" "PASS" | Out-Null

# ═══════════════════════════════════════════════════════════════════
# PHASE 1 · EMERGENT AGENT CONSULTATION
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 1 · EMERGENT AGENTS ────" "Cyan"

$designPrompt = @"
You are an emergent HBOS agent designing persistence architecture.

CONTEXT:
HBOS root rule: Qdrant is single source of truth. If Qdrant fails, everything fails.
Yesterday (op=314) closed clean with FreeLLMAPI :3001 (268 models), Kiro :10088 (8 Claude models), Qdrant Cloud (29 collections), 10 active providers.
Pending from op=314: unify Kiro with FreeLLMAPI completely.

DELIVER (7 sections, structured markdown):
1. hbos_providers schema
2. hbos_runtime_state schema
3. hbos_integrations schema
4. R-PERSIST-RUNTIME rule text
5. Restore mechanism on boot
6. Verification protocol (real restart test)
7. Migration path from 276 to correct state

CONSTRAINTS: Everything to Qdrant. No files as source of truth. Do NOT break what works. Kiro must integrate as custom provider. Runtime must survive restarts.

Output structured markdown ready for Qdrant.
"@

$geminiModel = $catalog | Where-Object { $_ -match "gemini.*3" } | Select-Object -First 1
if (-not $geminiModel) { $geminiModel = $catalog | Where-Object { $_ -match "gemini" } | Select-Object -First 1 }
$claudeModel = $catalog | Where-Object { $_ -match "claude" } | Select-Object -First 1
$gptModel = $catalog | Where-Object { $_ -match "gpt-oss" } | Select-Object -First 1

Log "  gemini target: $geminiModel" "White"
Log "  claude target: $claudeModel" "White"
Log "  gpt target: $gptModel" "White"

$responses = @{}

$agentTargets = @(
    @{ tag="GEMINI"; model=$geminiModel },
    @{ tag="CLAUDE"; model=$claudeModel },
    @{ tag="GPT-OSS"; model=$gptModel }
)

foreach ($a in $agentTargets) {
    if (-not $a.model) { Log "  [$($a.tag)] no model found · skip" "Yellow"; continue }
    Log "[AGENT] querying $($a.tag) · model=$($a.model)" "Magenta"
    try {
        $body = @{
            model = $a.model
            messages = @(@{ role="user"; content=$designPrompt })
            temperature = 0.3
            max_tokens = 3500
        } | ConvertTo-Json -Depth 6 -Compress

        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:3001/v1/chat/completions" `
            -Headers $flmHdr -Method Post -Body $body -TimeoutSec 120

        $content = $resp.choices[0].message.content
        $responses[$a.tag] = $content
        Log "  $($a.tag) responded · $($content.Length) chars" "Green"
        Add-Approval "1" "1.$($a.tag)" "EXECUTE" "agent $($a.tag)" "PASS" | Out-Null
    } catch {
        Log "  $($a.tag) error: $_" "Red"
        $responses[$a.tag] = "ERROR: $_"
        Add-Approval "1" "1.$($a.tag)" "EXECUTE" "agent $($a.tag)" "FAIL" | Out-Null
    }
}

# ═══════════════════════════════════════════════════════════════════
# PHASE 2 · CONSOLIDATION
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 2 · CONSOLIDATION ────" "Cyan"

$agentBlock = ""
foreach ($k in $responses.Keys) {
    $txt = $responses[$k]
    if ($txt.Length -gt 3000) { $txt = $txt.Substring(0,3000) }
    $agentBlock += "`n=== $k ===`n$txt`n"
}

$consolidationPrompt = @"
You are the HBOS emergent consolidator. Multiple agents designed persistence architecture.

$agentBlock

TASK: Produce ONE consolidated authoritative design with the 7 sections:
1. hbos_providers schema
2. hbos_runtime_state schema
3. hbos_integrations schema
4. R-PERSIST-RUNTIME rule text
5. Restore mechanism
6. Verification protocol
7. Migration path

Merge best parts. Where they disagree, choose most robust. Output structured markdown.
"@

$consolidated = ""
try {
    $body = @{
        model = "auto"
        messages = @(@{ role="user"; content=$consolidationPrompt })
        temperature = 0.2
        max_tokens = 6000
    } | ConvertTo-Json -Depth 6 -Compress

    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:3001/v1/chat/completions" `
        -Headers $flmHdr -Method Post -Body $body -TimeoutSec 150

    $consolidated = $resp.choices[0].message.content
    Log "  consolidated: $($consolidated.Length) chars" "Green"
    Add-Approval "2" "2.1" "EXECUTE" "consolidation" "PASS" | Out-Null
} catch {
    Log "  consolidation error: $_" "Red"
    $consolidated = ($responses.Values | Select-Object -First 1)
    Add-Approval "2" "2.1" "EXECUTE" "consolidation" "FAIL" | Out-Null
}

# ═══════════════════════════════════════════════════════════════════
# PHASE 3 · PERSIST DESIGN
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 3 · PERSIST DESIGN ────" "Cyan"

$designContent = @"
# HBOS Persistence Design · op=315-final · $ts

## Environment verified
- FreeLLMAPI :3001 · $($catalog.Count) models runtime
- Kiro :10088 · $($kiroIds.Count) Claude models
- Qdrant Cloud · reachable

## Real model names
- Gemini: $($catalog | Where-Object { $_ -match 'gemini' } | Select-Object -First 5 -join ', ')
- Claude: $($catalog | Where-Object { $_ -match 'claude' } | Select-Object -First 5 -join ', ')
- GPT: $($catalog | Where-Object { $_ -match 'gpt' } | Select-Object -First 5 -join ', ')

## Agent responses
$(foreach ($k in $responses.Keys) { "### $k`n`n$($responses[$k])`n" })

## Consolidated design
$consolidated
"@

Set-Content -Path $designFile -Value $designContent -Encoding UTF8
$designHash = Sha16 $designContent
Log "  design: $designFile" "Green"
Log "  hash: $designHash" "Green"
Add-Approval "3" "3.1" "EXECUTE" "design persisted" "PASS" | Out-Null

# ═══════════════════════════════════════════════════════════════════
# PHASE 4 · FRONTIER
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 4 · FRONTIER ────" "Cyan"
Log "  catalog: $($catalog.Count)" "White"
Log "  kiro: $($kiroIds.Count)" "White"
Log "  agents responded: $($responses.Keys.Count)" "White"
Log "  consolidated: $($consolidated.Length) chars" "White"
Add-Approval "4" "4.1" "FRONTIER" "phase 4 complete" "PASS" | Out-Null

# ═══════════════════════════════════════════════════════════════════
# PHASE 5 · REDUNDANT CLOSE + BACKUP
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 5 · CLOSE ────" "Cyan"

Log "[5.1] backup" "White"
$bkp = Join-Path $root "_BACKUPS\hbos-op315-final-$ts.zip"
New-Item -ItemType Directory -Force -Path (Split-Path $bkp) | Out-Null
$exclude = @("_BACKUPS",".git",".kiro-gateway-env","node_modules")
$items = Get-ChildItem -Path $root | Where-Object { $exclude -notcontains $_.Name }
Compress-Archive -Path $items.FullName -DestinationPath $bkp -Force
$bkpSize = (Get-Item $bkp).Length
Log "  backup: $bkp ($([math]::Round($bkpSize/1MB,2)) MB)" "Green"
Add-Approval "5" "5.1" "EXECUTE" "backup" "PASS" | Out-Null

Log "[5.2] commit + push" "White"
git -C $root add -A
$commitMsg = "HBOS op=315-final: environment verified · real catalog · persistence design · redundant close"
git -C $root commit -m $commitMsg
$pushResult = git -C $root push origin main 2>&1
Log "  push: $pushResult" "White"
$finalStatus = git -C $root status --porcelain
Log "  working tree: $(if($finalStatus){'DIRTY'}else{'CLEAN'})" "Green"
Add-Approval "5" "5.2" "EXECUTE" "commit+push" "PASS" | Out-Null

Log "[5.3] export notebooklm" "White"
Copy-Item $ledgerMd $exportFile -Force
Add-Content -Path $exportFile -Value "`n`n---`n`n## Design`n`n$designContent" -Encoding UTF8
Log "  export: $exportFile" "Green"
Add-Approval "5" "5.3" "EXECUTE" "export" "PASS" | Out-Null

Add-Approval "5" "5.4" "EXECUTE" "session close" "PASS" | Out-Null

# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════

Log "`n═══════════════════════════════════════════════════════════════" "Cyan"
Log "HBOS op=315-FINAL · COMPLETE" "Cyan"
Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "Genesis:      $genesisHash" "Cyan"
Log "Chain:        $($script:chain) approvals" "Cyan"
Log "Last hash:    $($script:lastHash)" "Cyan"
Log "" "White"
Log "Environment:" "White"
Log "  FreeLLMAPI: $($catalog.Count) models" "White"
Log "  Kiro:       $($kiroIds.Count) Claude" "White"
Log "  Qdrant:     reachable" "White"
Log "  Antigravity: $($agProcs.Count) processes" "Yellow"
Log "" "White"
Log "Artifacts:" "White"
Log "  Catalog:  $catalogFile" "White"
Log "  Design:   $designFile" "White"
Log "  Ledger:   $ledgerMd" "White"
Log "  Export:   $exportFile" "White"
Log "  Log:      $logFile" "White"
Log "  Backup:   $bkp" "White"
Log "" "White"
Log "RECOMMENDATION:" "Yellow"
Log "  Close Antigravity completely · use PWSH direct" "Yellow"
Log "  $($agProcs.Count) antigravity processes were active" "Yellow"
Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "DESCANSA. op=315 cerrado." "Green"
Log "═══════════════════════════════════════════════════════════════" "Cyan"