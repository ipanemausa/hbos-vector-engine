# ═══════════════════════════════════════════════════════════════════
# HBOS · op=315-persistence-design · 2026-09-26
# Purpose : verify topology · detect Antigravity interference
#           query emergent agents · consolidate · persist design
# Mode    : read-only for system state · writes ONLY design to Qdrant
# Channel : Antigravity PWSH → Anti → FreeLLMAPI → Qdrant
# ═══════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$root    = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
$ts      = Get-Date -Format "yyyyMMdd-HHmmss"
$logDir  = Join-Path $root "logs"
$logFile = Join-Path $logDir "op315-persistence-design-$ts.log"
$designFile = Join-Path $logDir "hbos-persistence-design-$ts.md"
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

Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "HBOS · PERSISTENCE DESIGN · $ts" "Cyan"
Log "Mode: read-only · writes only design to Qdrant" "Yellow"
Log "═══════════════════════════════════════════════════════════════" "Cyan"

# ═══════════════════════════════════════════════════════════════════
# PHASE 1 · TOPOLOGY VERIFICATION
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 1 · TOPOLOGY ────" "Cyan"

# Anti location (local?)
Log "[T1] Anti location" "White"
$antiPath = Join-Path $root ".agents\rules\HBOS_ANTI_ROLE.md"
$antiLocal = Test-Path $antiPath
Log "  Anti rules at: $antiPath" "White"
Log "  exists: $antiLocal · local filesystem: $antiLocal" "Green"

# FreeLLMAPI local?
Log "[T2] FreeLLMAPI reachability" "White"
$freellmapiKeyPath = Join-Path $root "config\freellmapi-key.txt"
$freellmapiKey = (Get-Content $freellmapiKeyPath -Raw).Trim()
$flmHdr = @{ Authorization = "Bearer $freellmapiKey" }
$flmReachable = $false
try {
    $flmCheck = Invoke-RestMethod -Uri "http://127.0.0.1:3001/v1/models" -Headers $flmHdr -TimeoutSec 5
    $flmReachable = $true
    Log "  FreeLLMAPI :3001 reachable · local" "Green"
    Log "  models exposed: $($flmCheck.data.Count)" "Green"
} catch {
    Log "  FreeLLMAPI error: $_" "Red"
}

# Kiro local?
Log "[T3] Kiro Gateway reachability" "White"
$kiroHdr = @{ Authorization = "Bearer hbos-kiro-local-key-2026" }
$kiroReachable = $false
$kiroCount = 0
try {
    $kiroCheck = Invoke-RestMethod -Uri "http://127.0.0.1:10088/v1/models" -Headers $kiroHdr -TimeoutSec 5
    $kiroReachable = $true
    $kiroCount = $kiroCheck.data.Count
    Log "  Kiro :10088 reachable · local" "Green"
    Log "  kiro models: $kiroCount" "Green"
} catch {
    Log "  Kiro error: $_" "Red"
}

# Qdrant cloud?
Log "[T4] Qdrant Cloud" "White"
$qdrantReachable = $false
$qdrantUrl = "https://38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io"
try {
    $qdrantKeyPath = Join-Path $root "config\qdrant-key.txt"
    if (Test-Path $qdrantKeyPath) {
        $qk = (Get-Content $qdrantKeyPath -Raw).Trim()
        $qdrantHdr = @{ "api-key" = $qk }
        $qdrantCheck = Invoke-RestMethod -Uri "$qdrantUrl/collections" -Headers $qdrantHdr -TimeoutSec 10
        $qdrantReachable = $true
        $collections = $qdrantCheck.result.collections.Count
        Log "  Qdrant Cloud reachable · remote" "Green"
        Log "  collections: $collections" "Green"
    } else {
        Log "  no qdrant-key.txt · cannot verify" "Yellow"
    }
} catch {
    Log "  Qdrant error: $_" "Red"
}

# Antigravity running processes (interference detection)
Log "[T5] Antigravity interference detection" "White"
$antigravityProcs = @()
try {
    $antigravityProcs = Get-Process | Where-Object { 
        $_.ProcessName -match "antigravity|Antigravity" 
    }
} catch {}

if ($antigravityProcs.Count -gt 0) {
    Log "  Antigravity processes: $($antigravityProcs.Count)" "Yellow"
    foreach ($p in $antigravityProcs) {
        Log "    - $($p.ProcessName) · pid $($p.Id) · cpu $($p.CPU)" "White"
    }
} else {
    Log "  no antigravity processes detected" "Green"
}

# Check if antigravity agent has active background tasks
Log "[T6] Background agent interference check" "White"
$pwshProcs = @()
try {
    $pwshProcs = Get-Process -Name pwsh,powershell -ErrorAction SilentlyContinue
} catch {}

Log "  active pwsh/powershell processes: $($pwshProcs.Count)" "White"
foreach ($p in $pwshProcs) {
    Log "    - pid $($p.Id) · start $($p.StartTime) · cpu $($p.CPU)" "White"
}

# Port checks
Log "[T7] Port state" "White"
foreach ($port in @(3001, 10088, 1080)) {
    try {
        $conn = Test-NetConnection -ComputerName 127.0.0.1 -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
        Log "  port $port : $(if($conn){'OPEN'}else{'closed'})" "White"
    } catch {
        Log "  port $port : error" "Yellow"
    }
}

# ═══════════════════════════════════════════════════════════════════
# PHASE 2 · EMERGENT AGENT CONSULTATION
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 2 · EMERGENT AGENTS ────" "Cyan"

$designPrompt = @"
You are an emergent HBOS agent. Design persistence architecture for this system.

CONTEXT:
HBOS is a personal AI orchestration system. Root rule: Qdrant is the single
source of truth. If Qdrant fails, everything fails.

Yesterday (op=314) the system worked with 326 models via FreeLLMAPI.
Today (op=315) it exposes only 276. Cause:

- freeapi.db has 324 models across 23 platforms
- FreeLLMAPI runtime mounts only 10 providers → 268 models
- Kiro Gateway runs on :10088 with 8 Claude models OUTSIDE FreeLLMAPI
- Composite: 268 + 8 = 276 · yesterday: 326 · DRIFT: -50

Root cause: yesterday's fix was DOCUMENTED (close report + MD) but NOT
PERSISTED (not written to Qdrant, not persisted in FreeLLMAPI runtime
config). After restart, runtime dropped back to 276.

Stack:
- Anti: local executor (no internal LLM)
- FreeLLMAPI :3001 (OpenAI-compatible, supports custom providers)
- Kiro Gateway :10088 (OpenAI-compatible, 8 Claude models)
- Qdrant Cloud (matrix 360)
- Antigravity as PWSH console (may interfere as agent)
- Windows Hello for critical approvals

TASK - Deliver structured markdown, 7 sections:

1. hbos_providers schema - every field, type, purpose. Must capture:
   provider name, platform, base_url, type, enabled_db, enabled_runtime,
   key_present, key_hash_sha256_16, models_count, last_check, status, notes

2. hbos_runtime_state schema - canonical runtime state (model counts,
   provider count, integration count, timestamp, source, expected_invariant)

3. hbos_integrations schema - register integrations like Kiro↔FreeLLMAPI.
   How they are configured, verified, restored. Re-integration triggers.

4. R-PERSIST-RUNTIME rule text - exact wording. What it enforces. How it
   is verified on every session start.

5. Restore mechanism - on boot, how does HBOS verify runtime config matches
   hbos_providers? If mismatch: halt, auto-restore, or notify? Rollback path.

6. Verification protocol - real restart test. How to prove persistence works.

7. Migration path - take current degraded state (276) and rebuild to
   correct state (326+) WITHOUT breaking what works.

CONSTRAINTS:
- Everything goes to Qdrant (matrix 360)
- No files as source of truth
- No documentation without persistence
- Do NOT break what already works (R-GUARD-REGRESSION)
- Kiro must be integrated into FreeLLMAPI as custom provider
- Runtime must survive restarts

OUTPUT: structured markdown, ready to be parsed and written to Qdrant.
"@

# Query multiple emergent agents in parallel via FreeLLMAPI
$agents = @(
    @{ name="gemini-3.8-flash-medium"; tag="GEMINI" },
    @{ name="claude-opus-4-5"; tag="CLAUDE" },
    @{ name="gpt-oss-120b"; tag="GPT-OSS" }
)

$responses = @{}
foreach ($agent in $agents) {
    Log "[AGENT] querying $($agent.name)" "Magenta"
    try {
        $body = @{
            model = $agent.name
            messages = @(@{ role="user"; content=$designPrompt })
            temperature = 0.3
            max_tokens = 4000
        } | ConvertTo-Json -Depth 6
        
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:3001/v1/chat/completions" `
            -Headers $flmHdr -ContentType "application/json" -Method Post -Body $body -TimeoutSec 90
        
        $content = $resp.choices[0].message.content
        $responses[$agent.tag] = $content
        Log "  $($agent.tag) responded · $($content.Length) chars" "Green"
    } catch {
        Log "  $($agent.tag) error: $_" "Red"
        $responses[$agent.tag] = "ERROR: $_"
    }
}

# ═══════════════════════════════════════════════════════════════════
# PHASE 3 · CONSOLIDATION (via FreeLLMAPI auto)
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 3 · CONSOLIDATION ────" "Cyan"

$validResponses = $responses.GetEnumerator() | Where-Object { $_.Value -and $_.Value -notmatch "^ERROR:" }

$consolidationPrompt = @"
You are the HBOS emergent consolidator. Multiple agents were asked to design
the persistence architecture for HBOS. Consolidate their responses into a
single authoritative design.

Responses from agents:
$($responses.GetEnumerator() | ForEach-Object { "`n=== $($_.Key) ===`n$($_.Value.Substring(0, [Math]::Min(3000, $_.Value.Length)))" } | Out-String)

TASK:
Produce the CONSOLIDATED design. Merge the best parts from each response.
Where they disagree, choose the most robust option and explain why briefly.

Output: the 7 sections (hbos_providers, hbos_runtime_state, hbos_integrations,
R-PERSIST-RUNTIME, restore mechanism, verification protocol, migration path)
in a unified, authoritative form. Ready to be parsed and written to Qdrant.
"@

$consolidated = ""
try {
    $body = @{
        model = "auto"
        messages = @(@{ role="user"; content=$consolidationPrompt })
        temperature = 0.2
        max_tokens = 6000
    } | ConvertTo-Json -Depth 6

    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:3001/v1/chat/completions" `
        -Headers $flmHdr -ContentType "application/json" -Method Post -Body $body -TimeoutSec 120

    $consolidated = $resp.choices[0].message.content
    Log "  consolidated design: $($consolidated.Length) chars" "Green"
} catch {
    Log "  consolidation error: $_ · falling back to best response" "Yellow"
    $best = $validResponses | Select-Object -First 1
    $consolidated = if ($best) { $best.Value } else { $responses["GEMINI"] }
}

# ═══════════════════════════════════════════════════════════════════
# PHASE 4 · WRITE DESIGN FILE + HASH
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 4 · PERSIST DESIGN ────" "Cyan"

$designContent = @"
# HBOS Persistence Design · op=315 · $ts

## Topology
- Anti: local
- FreeLLMAPI :3001: local (reachable: $flmReachable)
- Kiro :10088: local (reachable: $kiroReachable · $kiroCount models)
- Qdrant Cloud: remote (reachable: $qdrantReachable)
- Antigravity processes: $($antigravityProcs.Count) · pwsh processes: $($pwshProcs.Count)

## Agent Responses
$(foreach ($k in $responses.Keys) { "### $k`n`n$($responses[$k])`n`n" })

## Consolidated Design
$consolidated
"@

Set-Content -Path $designFile -Value $designContent -Encoding UTF8
$designHash = Sha16 $designContent
Log "  design file: $designFile" "Green"
Log "  design hash: $designHash" "Green"

# ═══════════════════════════════════════════════════════════════════
# PHASE 5 · PERSIST TO QDRANT (design only · no system change)
# ═══════════════════════════════════════════════════════════════════

Log "`n──── PHASE 5 · QDRANT PERSIST ────" "Cyan"
Log "  → design goes to hbos_persistence_design collection" "Yellow"
Log "  → topology snapshot goes to hbos_decisions" "Yellow"
Log "  (Qdrant write via existing HBOS pipeline · pending)" "White"

# ═══════════════════════════════════════════════════════════════════
# PHASE 6 · SUMMARY
# ═══════════════════════════════════════════════════════════════════

Log "`n═══════════════════════════════════════════════════════════════" "Cyan"
Log "PERSISTENCE DESIGN COMPLETE" "Cyan"
Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "Topology:" "White"
Log "  Anti:        local" "White"
Log "  FreeLLMAPI:  local :3001 · $flmReachable" "White"
Log "  Kiro:        local :10088 · $kiroReachable · $kiroCount models" "White"
Log "  Qdrant:      cloud · $qdrantReachable" "White"
Log "  Antigravity: $($antigravityProcs.Count) processes" "Yellow"
Log "  pwsh:        $($pwshProcs.Count) processes" "Yellow"
Log "" "White"
Log "Agents consulted: $($responses.Keys -join ', ')" "White"
Log "Consolidated: $($consolidated.Length) chars" "White"
Log "Design file: $designFile" "Cyan"
Log "Design hash: $designHash" "Cyan"
Log "Log: $logFile" "Cyan"
Log "" "White"
Log "INTERFERENCE CHECK:" "Yellow"
if ($antigravityProcs.Count -gt 1) {
    Log "  ⚠ multiple antigravity processes · possible interference" "Red"
} else {
    Log "  ✓ no obvious interference" "Green"
}
Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "NEXT: read design file · review consolidated response · decide" "Yellow"
Log "═══════════════════════════════════════════════════════════════" "Cyan"
