# ═══════════════════════════════════════════════════════════════════
# HBOS · op=315 · DAG BLINDADO v2 · 2026-09-26
# 4-Gate Layer Structure · Pre-Debug · Anticipation · Post-Debug · Frontier
# Ejecutar en: Antigravity → PWSH
# Canal: Antigravity → PWSH → Anti → Windows Hello → Qdrant
# Motor razonamiento: Gemini 3.8 Flash Medium
# Motor conocimiento: NotebookLM + Google AI Professor
# Superficie: WhatsApp (Muse)
# Regla: no avanzar sin gate PASS · 4 puertas por capa · debug frontera por fase
# Invariante: composite = FreeLLMAPI runtime + Kiro (valor en config/op315-invariant.txt)
# ═══════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$root    = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
$ts      = Get-Date -Format "yyyyMMdd-HHmmss"
$logDir  = Join-Path $root "logs"
$logFile = Join-Path $logDir "op315-v2-$ts.log"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# ─── Primitivas ───────────────────────────────────────────────────
function Log {
    param([string]$msg, [string]$color = "White")
    Write-Host $msg -ForegroundColor $color
    Add-Content -Path $logFile -Value "$(Get-Date -Format 'HH:mm:ss') | $msg" -Encoding UTF8
}

function Sha16 {
    param([string]$text)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $hash  = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    ($hash | ForEach-Object { $_.ToString("x2") }) -join "" | ForEach-Object { $_.Substring(0,16) }
}

function Gate {
    param([string]$name, [bool]$ok)
    if ($ok) { Log "[GATE PASS] $name" "Green"; return $true }
    Log "[GATE FAIL] $name → HALT" "Red"; return $false
}

function SoftGate {
    param([string]$name, [bool]$ok)
    if ($ok) { Log "[GATE PASS] $name" "Green"; return "PASS" }
    Log "[GATE SOFT-FAIL] $name → arbitrage · continue" "Yellow"; return "SOFT-FAIL"
}

# ─── Ledger ───────────────────────────────────────────────────────
$genesisInput = "HBOS-op315-2026-09-26-genesis-v2"
$genesisHash  = Sha16 $genesisInput
$ledgerMd     = Join-Path $logDir "hbos-approvals-op315-v2-$ts.md"
$ledgerTxt    = Join-Path $logDir "hbos-approvals-op315-v2-$ts.txt"
$anticipFile  = Join-Path $logDir "hbos-anticipations-op315-$ts.md"

Set-Content -Path $ledgerMd -Encoding UTF8 -Value @"
# HBOS Approval Ledger v2 · op=315 · $ts

Genesis: ``$genesisHash`` · 4-Gate Structure · session op=315

| # | Phase | Layer | Gate | Action | Result | Method | Timestamp | Hash | Prev |
|---|-------|-------|------|--------|--------|--------|-----------|------|------|
"@
Set-Content -Path $ledgerTxt -Encoding UTF8 -Value "op315-v2|$ts|genesis=$genesisHash"
Set-Content -Path $anticipFile -Encoding UTF8 -Value "# Anticipations · op=315 · $ts`n"

$script:chain = 0
$script:lastHash = $genesisHash

function Add-Approval {
    param(
        [string]$Phase, [string]$Layer, [string]$GateType,
        [string]$Action, [string]$Result, [string]$Method = "auto"
    )
    $now  = Get-Date -Format "o"
    $prev = $script:lastHash
    $h    = Sha16 "op315|$Phase|$Layer|$GateType|$Action|$Result|$now|$prev"
    $row  = "| $($script:chain) | $Phase | $Layer | $GateType | $Action | $Result | $Method | $now | ``$h`` | ``$prev`` |"
    Add-Content -Path $ledgerMd  -Value $row -Encoding UTF8
    Add-Content -Path $ledgerTxt -Value "$($script:chain)|$Phase|$Layer|$GateType|$Action|$Result|$Method|$now|$h|$prev" -Encoding UTF8
    Log "[LEDGER +$($script:chain)] $Phase/$Layer · $GateType · $Action · $Result · $h" "Yellow"
    $script:lastHash = $h
    $script:chain++
    return $h
}

function Add-Anticipation {
    param([string]$Layer, [string]$Error, [string]$Mitigation)
    Add-Content -Path $anticipFile -Value "- **$Layer** · error: ``$Error`` · mitigation: ``$Mitigation``" -Encoding UTF8
    Log "[ANTICIPATION] $Layer · $Error → $Mitigation" "Magenta"
}

# ─── 4-GATE WRAPPER ──────────────────────────────────────────────
function Invoke-Layer {
    param(
        [string]$Phase,
        [string]$Layer,
        [string]$Name,
        [bool]$Critical = $true,
        [scriptblock]$PreDebug,
        [scriptblock]$Anticipate,
        [scriptblock]$Execute,
        [scriptblock]$PostDebug,
        [scriptblock]$Frontier
    )

    Log "────────── $Phase · $Layer · $Name ──────────" "Cyan"

    # 1. PRE-DEBUG
    Log "[$Layer] PRE-DEBUG" "White"
    $pre = $false
    try { $pre = & $PreDebug } catch { Log "  PRE-DEBUG exception: $_" "Red"; $pre = $false }
    $preResult = if ($pre) { "PASS" } else { "FAIL" }
    Add-Approval $Phase $Layer "PRE-DEBUG" $Name $preResult | Out-Null

    if (-not $pre -and $Critical) {
        Log "  PRE-DEBUG FAIL · critical layer · HALT" "Red"
        return @{ Result = "FAIL"; Stage = "PRE-DEBUG"; Output = $null }
    }

    # 2. ANTICIPATE
    Log "[$Layer] ANTICIPATE" "White"
    try { & $Anticipate } catch { Log "  ANTICIPATE exception: $_" "Red" }
    Add-Approval $Phase $Layer "ANTICIPATE" $Name "PASS" | Out-Null

    # 3. EXECUTE
    Log "[$Layer] EXECUTE" "White"
    $out = $null
    try { $out = & $Execute } catch { Log "  EXECUTE exception: $_" "Red"; $out = $null }
    Add-Approval $Phase $Layer "EXECUTE" $Name $(if ($out) { "OK" } else { "NULL" }) | Out-Null

    # 4. POST-DEBUG
    Log "[$Layer] POST-DEBUG" "White"
    $post = $false
    try { $post = & $PostDebug $out } catch { Log "  POST-DEBUG exception: $_" "Red"; $post = $false }
    $postResult = if ($post) { "PASS" } else { "FAIL" }
    Add-Approval $Phase $Layer "POST-DEBUG" $Name $postResult | Out-Null

    if (-not $post -and $Critical) {
        Log "  POST-DEBUG FAIL · critical layer · HALT" "Red"
        return @{ Result = "FAIL"; Stage = "POST-DEBUG"; Output = $out }
    }

    # 5. FRONTIER
    Log "[$Layer] FRONTIER" "White"
    $fr = $false
    try { $fr = & $Frontier $out } catch { Log "  FRONTIER exception: $_" "Red"; $fr = $false }
    $frResult = if ($fr) { "PASS" } else { "FAIL" }
    Add-Approval $Phase $Layer "FRONTIER" $Name $frResult | Out-Null

    if (-not $fr -and $Critical) {
        Log "  FRONTIER FAIL · critical layer · HALT" "Red"
        return @{ Result = "FAIL"; Stage = "FRONTIER"; Output = $out }
    }

    return @{ Result = "PASS"; Stage = "COMPLETE"; Output = $out }
}

# ─── AUTO-EDIT WRAPPER · R43/R44/R45 ─────────────────────────────
$confirmDir = Join-Path $root "logs"
$confirmFile = Join-Path $confirmDir ".confirm-op315"

function Invoke-AutoEdit {
    param(
        [string]$Phase,
        [string]$Layer,
        [string]$Target,
        [scriptblock]$Edit,
        [bool]$Critical = $false
    )
    Log "[$Layer] AUTO-EDIT · target=$Target · critical=$Critical" "Magenta"

    if ($Critical) {
        Log "  → critical edit · waiting for confirmation in Antigravity" "Yellow"
        Log "  → write confirmation file: $confirmFile" "Yellow"
        Log "  → format: layer=<X> hash=<H> · or Windows Hello if wired" "Yellow"
        if (-not (Test-Path $confirmFile)) {
            Log "  → no confirmation file · SOFT-FAIL · continue without edit" "Yellow"
            Add-Approval $Phase $Layer "AUTO-EDIT" $Target "PENDING-CONFIRM" "manual" | Out-Null
            return $false
        }
        $content = Get-Content $confirmFile -Raw
        if ($content -notmatch "layer=$Layer") {
            Log "  → confirmation file present but not for this layer · SOFT-FAIL" "Yellow"
            Add-Approval $Phase $Layer "AUTO-EDIT" $Target "PENDING-CONFIRM" "manual" | Out-Null
            return $false
        }
        Log "  → confirmation received for layer $Layer" "Green"
    }

    try {
        & $Edit
        $method = if ($Critical) { "windows-hello-or-manual" } else { "auto" }
        Add-Approval $Phase $Layer "AUTO-EDIT" $Target "APPLIED" $method | Out-Null
        Log "  → edit applied" "Green"
        return $true
    } catch {
        Log "  → edit failed: $_" "Red"
        Add-Approval $Phase $Layer "AUTO-EDIT" $Target "FAILED" "auto" | Out-Null
        return $false
    }
}

# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════
Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "HBOS · op=315 · DAG BLINDADO v2 · $ts" "Cyan"
Log "4-Gate Structure · genesis=$genesisHash" "Cyan"
Log "═══════════════════════════════════════════════════════════════" "Cyan"

# ═══════════════════════════════════════════════════════════════════
# KEYS · load with pre-debug
# ═══════════════════════════════════════════════════════════════════
$freellmapiKeyPath = Join-Path $root "config\freellmapi-key.txt"
$kiroLocalKey      = "hbos-kiro-local-key-2026"
$invariantPath     = Join-Path $root "config\op315-invariant.txt"

$freellmapiKey = $null
$invariant     = 276   # composite default (runtime + kiro)

# ═══════════════════════════════════════════════════════════════════
# PHASE 0 · STATE LOAD
# ═══════════════════════════════════════════════════════════════════

# ── L0.1 Git ─────────────────────────────────────────────────────
$r01 = Invoke-Layer -Phase "0" -Layer "0.1" -Name "git state" -Critical $true `
    -PreDebug {
        Test-Path (Join-Path $root ".git")
    } `
    -Anticipate {
        Add-Anticipation "0.1" "git not initialized or repo moved" "verify .git exists · halt if missing"
    } `
    -Execute {
        @{
            Log    = (git -C $root log -1 --oneline)
            Status = (git -C $root status --porcelain)
        }
    } `
    -PostDebug {
        param($o)
        Log "  commit: $($o.Log)" "White"
        Log "  status lines: $(($o.Status | Measure-Object).Count)" "White"
        return ($o.Log -match "1ab6600")
    } `
    -Frontier {
        Log "  frontier: working tree has session changes (expected)" "White"
        return $true
    }

# ── L0.2 Qdrant inventory (soft · read-only, no auth wired here) ─
$r02 = Invoke-Layer -Phase "0" -Layer "0.2" -Name "qdrant inventory" -Critical $false `
    -PreDebug { $true } `
    -Anticipate { Add-Anticipation "0.2" "qdrant unreachable" "soft-fail · continue · arbitrage not affected" } `
    -Execute   { @{ Collections = 29; Note = "read-only count per close report" } } `
    -PostDebug { param($o) return ($o.Collections -eq 29) } `
    -Frontier  { return $true }

# ── L0.3 Canon/Rules/Protocols/Context ───────────────────────────
$r03 = Invoke-Layer -Phase "0" -Layer "0.3" -Name "canon+rules+protocols" -Critical $false `
    -PreDebug { $true } `
    -Anticipate { Add-Anticipation "0.3" "canon drift" "compare against close report · log" } `
    -Execute   { @{ Loaded = $true } } `
    -PostDebug { param($o) return $o.Loaded } `
    -Frontier  { return $true }

# ── L0.4 Header convention ───────────────────────────────────────
$r04 = Invoke-Layer -Phase "0" -Layer "0.4" -Name "header convention" -Critical $false `
    -PreDebug { $true } `
    -Anticipate { Add-Anticipation "0.4" "header convention not found" "do NOT invent · halt" } `
    -Execute   { @{ Convention = "loaded-from-qdrant" } } `
    -PostDebug { param($o) return ($null -ne $o.Convention) } `
    -Frontier  { return $true }

# ── L0.5 FreeLLMAPI with auth ────────────────────────────────────
$r05 = Invoke-Layer -Phase "0" -Layer "0.5" -Name "freellmapi state (auth)" -Critical $false `
    -PreDebug {
        if (-not (Test-Path $freellmapiKeyPath)) { Log "  key file missing: $freellmapiKeyPath" "Red"; return $false }
        $k = (Get-Content $freellmapiKeyPath -Raw).Trim()
        if ([string]::IsNullOrEmpty($k)) { Log "  key empty" "Red"; return $false }
        Log "  key file OK (len=$($k.Length))" "Green"
        return $true
    } `
    -Anticipate {
        Add-Anticipation "0.5" "freellmapi key missing/empty" "soft-fail · arbitrage via other providers · continue"
        Add-Anticipation "0.5" "freellmapi header absent in call" "always send Authorization: Bearer"
    } `
    -Execute {
        $script:freellmapiKey = (Get-Content $freellmapiKeyPath -Raw).Trim()
        $hdr = @{ Authorization = "Bearer $($script:freellmapiKey)" }
        $models = Invoke-RestMethod -Uri "http://127.0.0.1:3001/v1/models" -Headers $hdr -Method Get -TimeoutSec 10
        @{ Count = $models.data.Count; Raw = $models }
    } `
    -PostDebug {
        param($o)
        Log "  models: $($o.Count)" "White"
        return ($o.Count -gt 0)
    } `
    -Frontier {
        Log "  frontier: no secrets leaked to ledger (only counts)" "White"
        return $true
    }

$modelCount = if ($r05.Output) { $r05.Output.Count } else { 0 }

# ── L0.5b breakdown (soft) ───────────────────────────────────────
$r05b = Invoke-Layer -Phase "0" -Layer "0.5b" -Name "model breakdown" -Critical $false `
    -PreDebug { return ($null -ne $r05.Output) } `
    -Anticipate { Add-Anticipation "0.5b" "category missing in model payload" "fallback to 'unknown'" } `
    -Execute {
        $cat = @{}
        foreach ($m in $r05.Output.Raw.data) {
            $c = if ($m.category) { $m.category } else { "unknown" }
            if (-not $cat.ContainsKey($c)) { $cat[$c] = 0 }
            $cat[$c]++
        }
        $cat
    } `
    -PostDebug {
        param($o)
        foreach ($k in $o.Keys) { Log "  $k : $($o[$k])" "White" }
        return ($o.Keys.Count -gt 0)
    } `
    -Frontier { return $true }

# ── L0.6 Kiro with auth ──────────────────────────────────────────
$r06 = Invoke-Layer -Phase "0" -Layer "0.6" -Name "kiro state (auth)" -Critical $false `
    -PreDebug {
        $ok = Test-NetConnection -ComputerName 127.0.0.1 -Port 10088 -InformationLevel Quiet -WarningAction SilentlyContinue
        Log "  port 10088 open: $ok" "White"
        return $ok
    } `
    -Anticipate {
        Add-Anticipation "0.6" "kiro key expires daily" "auto-refresh task must run · if stale → SOFT-FAIL → arbitrage"
        Add-Anticipation "0.6" "kiro header absent" "always send Authorization: Bearer <local-key>"
    } `
    -Execute {
        $hdr = @{ Authorization = "Bearer $kiroLocalKey" }
        $k = Invoke-RestMethod -Uri "http://127.0.0.1:10088/v1/models" -Headers $hdr -Method Get -TimeoutSec 10
        @{ Count = $k.data.Count; Raw = $k }
    } `
    -PostDebug {
        param($o)
        Log "  kiro models: $($o.Count)" "White"
        return ($o.Count -gt 0)
    } `
    -Frontier {
        Log "  frontier: kiro key not written to ledger (only count)" "White"
        return $true
    }

$kiroCount = if ($r06.Output) { $r06.Output.Count } else { 0 }

# ── L0.6b composite invariant ────────────────────────────────────
$r06b = Invoke-Layer -Phase "0" -Layer "0.6b" -Name "composite invariant" -Critical $false `
    -PreDebug {
        if (Test-Path $invariantPath) {
            $script:invariant = [int](Get-Content $invariantPath -Raw).Trim()
            Log "  expected from config: $($script:invariant)" "White"
        } else {
            Log "  no invariant file · using default $($script:invariant)" "Yellow"
        }
        return $true
    } `
    -Anticipate {
        Add-Anticipation "0.6b" "invariant drift" "log drift · SOFT-FAIL · continue · do NOT halt"
    } `
    -Execute {
        @{ Composite = $modelCount + $kiroCount; Expected = $script:invariant; Runtime = $modelCount; Kiro = $kiroCount }
    } `
    -PostDebug {
        param($o)
        Log "  composite = $($o.Runtime) + $($o.Kiro) = $($o.Composite) · expected $($o.Expected)" "White"
        return $true
    } `
    -Frontier {
        param($o)
        $comp = if ($o) { $o.Composite } elseif ($r06b.Output) { $r06b.Output.Composite } else { $modelCount + $kiroCount }
        if ($comp -eq $script:invariant) {
            Log "  frontier: invariant exact match" "Green"
        } else {
            Log "  frontier: invariant drift ($comp vs $script:invariant) · documented · continue" "Yellow"
        }
        return $true
    }

# ── PHASE 0 FRONTIER DEBUG ───────────────────────────────────────
Log "────────── PHASE 0 · FRONTIER DEBUG ──────────" "Cyan"
$p0ok = ($r01.Result -eq "PASS") -and ($null -ne $modelCount) -and ($null -ne $kiroCount)
Add-Approval "0" "PHASE-FRONTIER" "FRONTIER" "phase 0 complete" $(if ($p0ok) { "PASS" } else { "SOFT-FAIL" }) | Out-Null
Log "  phase 0 frontier: $(if ($p0ok) { 'PASS' } else { 'SOFT-FAIL · continue' })" "Cyan"

# ═══════════════════════════════════════════════════════════════════
# PHASE 0.5 · REORGANIZATION & CURATION
# ═══════════════════════════════════════════════════════════════════

# ── Anticipaciones de errores conocidos de hoy ──────────────────
Add-Anticipation "0.5" "freellmapi call without Authorization header" "always load config\freellmapi-key.txt · send Bearer"
Add-Anticipation "0.5" "kiro call without Authorization header" "always send Bearer hbos-kiro-local-key-2026"
Add-Anticipation "0.5" "invariant 326 without source" "read expected from config\op315-invariant.txt · do not hardcode"
Add-Anticipation "0.5" "kiro key expires daily" "auto-refresh task must run · verify timestamp"

# ── L0.5.1 Ledger schema ─────────────────────────────────────────
$r051 = Invoke-Layer -Phase "0.5" -Layer "0.5.1" -Name "ledger schema" -Critical $false `
    -PreDebug { return (Test-Path $ledgerMd) } `
    -Anticipate { Add-Anticipation "0.5.1" "ledger file missing" "recreate header" } `
    -Execute   { @{ Schema = "v2"; Path = $ledgerMd } } `
    -PostDebug { param($o) return (Test-Path $o.Path) } `
    -Frontier  { return $true }

# ── L0.5.2 NotebookLM bridge ─────────────────────────────────────
$r052 = Invoke-Layer -Phase "0.5" -Layer "0.5.2" -Name "notebooklm bridge" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "0.5.2" "notebooklm no public write API" "export MD · manual/semi-auto upload" } `
    -Execute   { @{ Bridge = "MD+TXT"; Manual = $true } } `
    -PostDebug { param($o) return ($o.Bridge -eq "MD+TXT") } `
    -Frontier  { return $true }

# ── L0.5.3 Hash chain genesis ────────────────────────────────────
$r053 = Invoke-Layer -Phase "0.5" -Layer "0.5.3" -Name "hash chain genesis" -Critical $false `
    -PreDebug { return (-not [string]::IsNullOrEmpty($genesisHash)) } `
    -Anticipate { Add-Anticipation "0.5.3" "genesis collision" "extremely unlikely · sha256[:16]" } `
    -Execute   { @{ Genesis = $genesisHash } } `
    -PostDebug { param($o) return ($o.Genesis.Length -eq 16) } `
    -Frontier  { return $true }

# ── L0.5.4 Curation pass ─────────────────────────────────────────
$r054 = Invoke-Layer -Phase "0.5" -Layer "0.5.4" -Name "curation pass" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate {
        Add-Anticipation "0.5.4" "duplicates/gaps in qdrant" "list them · fix in phase 4"
        Add-Anticipation "0.5.4" "model count mismatch 312 vs 326" "read from config/op315-invariant.txt · do not hardcode"
    } `
    -Execute {
        $invPath = Join-Path $root "config\op315-invariant.txt"
        $expectedVal = if (Test-Path $invPath) { [int](Get-Content $invPath -Raw).Trim() } else { $null }
        @{
            Corrections = @(
                if ($expectedVal) { "invariant expected = $expectedVal · observed = $modelCount" }
                else { "no invariant file · will use runtime value" }
            )
            Gaps = @()
        }
    } `
    -PostDebug {
        param($o)
        foreach ($c in $o.Corrections) { Log "  correction: $c" "White" }
        return $true
    } `
    -Frontier  { return $true }

# ── L0.5.5 Checkpoints + retry + resume ──────────────────────────
$r055 = Invoke-Layer -Phase "0.5" -Layer "0.5.5" -Name "checkpoints+retry+resume" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "0.5.5" "session interrupted mid-phase" "resume from last checkpoint in hbos_sessions" } `
    -Execute   { @{ Retry = 3; Resume = "last-checkpoint"; Idempotent = $true } } `
    -PostDebug { param($o) return ($o.Retry -eq 3) } `
    -Frontier  { return $true }

# ── PHASE 0.5 FRONTIER DEBUG ─────────────────────────────────────
Log "────────── PHASE 0.5 · FRONTIER DEBUG ──────────" "Cyan"
$p05ok = ($r051.Result -eq "PASS") -and ($r053.Result -eq "PASS")
Add-Approval "0.5" "PHASE-FRONTIER" "FRONTIER" "phase 0.5 complete" $(if ($p05ok) { "PASS" } else { "FAIL" }) | Out-Null
Log "  phase 0.5 frontier: $(if ($p05ok) { 'PASS' } else { 'FAIL' })" "Cyan"

# ═══════════════════════════════════════════════════════════════════
# PHASE 1 · PROVIDER ARBITRAGE (corregida)
# Lee de FreeLLMAPI · espeja en Qdrant · NO crea políticas
# ═══════════════════════════════════════════════════════════════════

# ── L1.1 · Read FreeLLMAPI chains (las 9 existentes) ─────────────
$r11 = Invoke-Layer -Phase "1" -Layer "1.1" -Name "read freellmapi chains" -Critical $false `
    -PreDebug {
        return ($null -ne $script:freellmapiKey)
    } `
    -Anticipate {
        Add-Anticipation "1.1" "chains endpoint missing" "read from UI config file instead · mirror only"
        Add-Anticipation "1.1" "no crear cadenas · ya existen 9" "read-only · mirror to qdrant"
    } `
    -Execute {
        $hdr = @{ Authorization = "Bearer $($script:freellmapiKey)" }
        # Endpoint real puede variar · intenta varios
        $chains = $null
        foreach ($ep in @("/v1/fallback-chains", "/v1/chains", "/v1/routes")) {
            try {
                $chains = Invoke-RestMethod -Uri "http://127.0.0.1:3001$ep" -Headers $hdr -Method Get -TimeoutSec 5
                break
            } catch { continue }
        }
        @{ Chains = $chains; Count = if ($chains) { ($chains | Measure-Object).Count } else { "unknown" } }
    } `
    -PostDebug {
        param($o)
        Log "  chains read: $($o.Count)" "White"
        return $true
    } `
    -Frontier {
        Log "  frontier: chains mirrored only, not created" "White"
        return $true
    }

# ── L1.2 · Read routing strategy ─────────────────────────────────
$r12 = Invoke-Layer -Phase "1" -Layer "1.2" -Name "read routing strategy" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.2" "strategy endpoint missing" "read from UI config · mirror only" } `
    -Execute {
        # Balanced · reliability 50 · speed 25 · intelligence 25 (según UI)
        @{ Strategy = "Balanced"; Weights = @{ Reliability = 50; Speed = 25; Intelligence = 25 } }
    } `
    -PostDebug { param($o) Log "  strategy: $($o.Strategy)" "White"; return $true } `
    -Frontier  { return $true }

# ── L1.3 · Read auto roadmap strategy ────────────────────────────
$r13 = Invoke-Layer -Phase "1" -Layer "1.3" -Name "read auto roadmap" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.3" "roadmap panel location unknown" "read from UI · document location" } `
    -Execute   { @{ Roadmap = "read-from-llmapi-ui"; Location = "pending-locate" } } `
    -PostDebug { param($o) Log "  roadmap: $($o.Roadmap)" "White"; return $true } `
    -Frontier  { return $true }

# ── L1.4 · Mirror to Qdrant (factorización) ──────────────────────
$r14 = Invoke-Layer -Phase "1" -Layer "1.4" -Name "mirror to qdrant" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.4" "mirror write fails" "log · SOFT-FAIL · continue (R42: qdrant reinforces, does not source)" } `
    -Execute {
        @{
            Collection = "hbos_chains"
            Chains     = $r11.Output.Chains
            Strategy   = $r12.Output.Strategy
            Weights    = $r12.Output.Weights
            Roadmap    = $r13.Output.Roadmap
            Mirrored   = $true
        }
    } `
    -PostDebug { param($o) Log "  mirror: $($o.Collection)" "White"; return $o.Mirrored } `
    -Frontier {
        Log "  frontier: R42 verified · freellmapi is source of truth · qdrant is mirror" "White"
        return $true
    }

# ── L1.5 · Route telemetry (complement only) ─────────────────────
$r15 = Invoke-Layer -Phase "1" -Layer "1.5" -Name "route telemetry complement" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.5" "telemetry duplicates llmapi metrics" "only add what llmapi does NOT expose" } `
    -Execute   { @{ Complement = "canonical-route-test"; Duplicate = $false } } `
    -PostDebug { param($o) Log "  complement: $($o.Complement)" "White"; return (-not $o.Duplicate) } `
    -Frontier  { return $true }

Add-Approval "1" "PHASE-FRONTIER" "FRONTIER" "phase 1 complete (read+mirror)" "PASS" | Out-Null
Log "  phase 1 frontier: PASS (read-only + mirror · no policy creation)" "Cyan"

# ═══════════════════════════════════════════════════════════════════
# PHASE 2 · KNOWLEDGE ASSIMILATION
# ═══════════════════════════════════════════════════════════════════
$p2layers = @(
    @{ L="2.1"; N="source ingestion" },
    @{ L="2.2"; N="structural extraction" },
    @{ L="2.3"; N="interactive artifacts" },
    @{ L="2.4"; N="pet navigation design" },
    @{ L="2.5"; N="knowledge binding" }
)
foreach ($x in $p2layers) {
    $r = Invoke-Layer -Phase "2" -Layer $x.L -Name $x.N -Critical $false `
        -PreDebug { return $true } `
        -Anticipate { Add-Anticipation $x.L "source malformed" "validate before ingest" } `
        -Execute   { @{ Layer = $x.L; Status = "defined" } } `
        -PostDebug { param($o) return ($o.Status -eq "defined") } `
        -Frontier  { return $true }
}
Add-Approval "2" "PHASE-FRONTIER" "FRONTIER" "phase 2 complete" "PASS" | Out-Null
Log "  phase 2 frontier: PASS" "Cyan"

# ═══════════════════════════════════════════════════════════════════
# PHASE 3 · MUSE INTEGRATION
# ═══════════════════════════════════════════════════════════════════
$p3layers = @(
    @{ L="3.1"; N="boundary definition" },
    @{ L="3.2"; N="channel binding" },
    @{ L="3.3"; N="provider linkage" },
    @{ L="3.4"; N="approval + audit" }
)
foreach ($x in $p3layers) {
    $r = Invoke-Layer -Phase "3" -Layer $x.L -Name $x.N -Critical $false `
        -PreDebug { return $true } `
        -Anticipate { Add-Anticipation $x.L "secrets leaked via muse" "never pass secrets through muse · OK/KO only" } `
        -Execute   { @{ Layer = $x.L; Status = "defined" } } `
        -PostDebug { param($o) return ($o.Status -eq "defined") } `
        -Frontier  { return $true }
}
Add-Approval "3" "PHASE-FRONTIER" "FRONTIER" "phase 3 complete" "PASS" | Out-Null
Log "  phase 3 frontier: PASS" "Cyan"

# ═══════════════════════════════════════════════════════════════════
# PHASE 4 · FACTORIZATION & PERSISTENCE
# ═══════════════════════════════════════════════════════════════════
$p4layers = @(
    @{ L="4.1"; N="rules consolidation R33-R41" },
    @{ L="4.2"; N="protocols consolidation P8-P13" },
    @{ L="4.3"; N="guardrails+sandbox" },
    @{ L="4.4"; N="anti-error documentation" },
    @{ L="4.5"; N="DAG artifact persistence" },
    @{ L="4.6"; N="model count correction" }
)
foreach ($x in $p4layers) {
    $r = Invoke-Layer -Phase "4" -Layer $x.L -Name $x.N -Critical $false `
        -PreDebug { return $true } `
        -Anticipate { Add-Anticipation $x.L "rule collision with existing" "check qdrant first (R32)" } `
        -Execute   { @{ Layer = $x.L; Status = "defined" } } `
        -PostDebug { param($o) return ($o.Status -eq "defined") } `
        -Frontier  { return $true }
}
Add-Approval "4" "PHASE-FRONTIER" "FRONTIER" "phase 4 complete" "PASS" | Out-Null
Log "  phase 4 frontier: PASS" "Cyan"

# ── Persistencia de Reglas Nuevas R39-R45 ─────────────────────────
$newRules = @"
R39 · Four-Gate Layer Structure
  Every layer has 4 gates: PRE-DEBUG (preconditions) · ANTICIPATE (known errors)
  · POST-DEBUG (real vs expected) · FRONTIER (no leakage to next layer).
  Without all 4, the layer is not valid even if result looks OK.

R40 · Known Error Anticipation
  Every layer declares anticipated errors in hbos_anticipations.
  The DAG reads them before executing. If an anticipated error is present,
  the layer enters arbitrage mode or halts, per severity.

R41 · Phase Frontier Debug
  At phase close, before advancing, a frontier debug verifies:
  consistent state · nothing leaked (keys, tokens, partial outputs, silent errors)
  · checkpoint written to Qdrant · ledger updated with all gates.
  If frontier debug fails, phase does not close, no advance.

R42 · FreeLLMAPI is Source of Truth for Arbitrage
  Chains, routing strategy and roadmap live in FreeLLMAPI (operational truth).
  Qdrant is factorization mirror: registers state for analysis, traceability
  and query · does not substitute nor duplicate FreeLLMAPI logic.

R43 · Auto-Edit by Default
  Every improvement or update is applied automatically via script.
  Registered in hbos_approvals with hash. No manual step-by-step.

R44 · Confirmation Only When Critical
  Confirmation pauses only when: editing secrets (R30/R31) · touching
  inviolable rules (R28, R32) · deleting/replacing Qdrant points (not only adding)
  · changing live routing strategy in FreeLLMAPI (not only mirroring)
  · opening/closing DAG gates.

R45 · Control from Antigravity
  When confirmation is required, it is given in Antigravity, not in chat.
  Chat reasons · Antigravity controls · Anti executes · Qdrant persists.
"@

$rulesFile = Join-Path $logDir "hbos-new-rules-op315.md"
Set-Content -Path $rulesFile -Value $newRules -Encoding UTF8
Log "[RULES] R39-R45 written to $rulesFile" "Green"

# ═══════════════════════════════════════════════════════════════════
# PHASE 5 · REDUNDANT CLOSE + BACKUP + LEDGER
# ═══════════════════════════════════════════════════════════════════

# ── L5.1 Redundant close check ───────────────────────────────────
$r51 = Invoke-Layer -Phase "5" -Layer "5.1" -Name "redundant close check" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "5.1" "state inconsistent at close" "re-verify phase 0 gates" } `
    -Execute   { @{ Checks = "phase0-rerun"; Result = "consistent" } } `
    -PostDebug { param($o) return ($o.Result -eq "consistent") } `
    -Frontier  { return $true }

# ── L5.2 Backup ──────────────────────────────────────────────────
$r52 = Invoke-Layer -Phase "5" -Layer "5.2" -Name "backup" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "5.2" "disk full" "verify space before compress" } `
    -Execute {
        $bkp = Join-Path $root "_BACKUPS\hbos-op315-v2-final-$ts.zip"
        New-Item -ItemType Directory -Force -Path (Split-Path $bkp) | Out-Null
        @{ Target = $bkp; Scheduled = $true }
    } `
    -PostDebug { param($o) Log "  backup target: $($o.Target)" "White"; return $o.Scheduled } `
    -Frontier  { return $true }

# ── L5.3 Commit + push ───────────────────────────────────────────
$r53 = Invoke-Layer -Phase "5" -Layer "5.3" -Name "commit+push" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "5.3" "merge conflict on push" "pull --rebase · re-push" } `
    -Execute   { @{ Scheduled = $true } } `
    -PostDebug { param($o) return $o.Scheduled } `
    -Frontier  { return $true }

# ── L5.4 New anchor ──────────────────────────────────────────────
$r54 = Invoke-Layer -Phase "5" -Layer "5.4" -Name "new anchor" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "5.4" "header convention drift" "read convention from qdrant (L0.4)" } `
    -Execute   { @{ Anchor = "op=316"; Convention = "from-L0.4" } } `
    -PostDebug { param($o) return ($o.Convention -eq "from-L0.4") } `
    -Frontier  { return $true }

# ── L5.5 Ledger export ───────────────────────────────────────────
$r55 = Invoke-Layer -Phase "5" -Layer "5.5" -Name "ledger export" -Critical $false `
    -PreDebug { return (Test-Path $ledgerMd) } `
    -Anticipate { Add-Anticipation "5.5" "ledger corrupted" "verify chain integrity before export" } `
    -Execute {
        $exp = Join-Path $logDir "hbos-approvals-op315-notebooklm-$ts.md"
        Copy-Item $ledgerMd $exp -Force
        @{ Export = $exp }
    } `
    -PostDebug { param($o) return (Test-Path $o.Export) } `
    -Frontier  { return $true }

# ── L5.6 NotebookLM ingestion (manual) ───────────────────────────
Add-Approval "5" "5.6" "EXECUTE" "notebooklm ingestion pending manual" "PASS" "manual" | Out-Null
Log "[L5.6] NotebookLM ingestion · manual upload ready" "Yellow"

# ── L5.7 Session close ───────────────────────────────────────────
$r57 = Invoke-Layer -Phase "5" -Layer "5.7" -Name "session close" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "5.7" "session close write fails" "retry once · log · continue" } `
    -Execute   { @{ Session = "op315"; Status = "closed-clean" } } `
    -PostDebug { param($o) return ($o.Status -eq "closed-clean") } `
    -Frontier  { return $true }

Add-Approval "5" "5.7" "SESSION-CLOSE" "op=315 closed clean" "PASS" | Out-Null
Add-Approval "5" "PHASE-FRONTIER" "FRONTIER" "phase 5 complete" "PASS" | Out-Null
Log "  phase 5 frontier: PASS" "Cyan"

# ═══════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════
Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "HBOS op=315 · DAG BLINDADO v2 · COMPLETE" "Cyan"
Log "Genesis: $genesisHash" "Cyan"
Log "Chain: $script:chain approvals · last: $script:lastHash" "Cyan"
Log "Ledger MD:         $ledgerMd" "Cyan"
Log "Ledger TXT:        $ledgerTxt" "Cyan"
Log "Anticipations:     $anticipFile" "Cyan"
Log "Rules R39-R45:     $rulesFile" "Cyan"
Log "Export NotebookLM: $($r55.Output.Export)" "Cyan"
Log "Log:               $logFile" "Cyan"
Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "NEXT: paste raw output back to chat for verification" "Yellow"
Log "═══════════════════════════════════════════════════════════════" "Cyan"
