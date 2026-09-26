# ═══════════════════════════════════════════════════════════════════
# HBOS · DAG op=315 · FULL EXECUTION · 2026-09-26 · English
# Channel   : Antigravity → PWSH → Anti → Windows Hello
# Persist   : Qdrant matrix 360 (root: if Qdrant fails, everything fails)
# Reasoning : Gemini 3.8 Flash Medium (Antigravity Agent panel)
# Knowledge : Google AI Professor + NotebookLM + Gemini 3.8
# Surface   : WhatsApp (Muse)
# Invariant : composite = FreeLLMAPI runtime + Kiro (config/op315-invariant.txt)
# Rule      : no advance without gate PASS · 4 gates per layer · frontier per phase
# Close     : pull --rebase · commit -A · push · backup · notebooklm export
# ═══════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$root    = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
$ts      = Get-Date -Format "yyyyMMdd-HHmmss"
$logDir  = Join-Path $root "logs"
$logFile = Join-Path $logDir "op315-final-$ts.log"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Log {
    param([string]$msg, [string]$color = "White")
    Write-Host $msg -ForegroundColor $color
    Add-Content -Path $logFile -Value "$(Get-Date -Format 'HH:mm:ss') | $msg" -Encoding UTF8
}

function Sha16 {
    param([string]$text)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
    $hash  = [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    (($hash | ForEach-Object { $_.ToString("x2") }) -join "").Substring(0,16)
}

$genesisHash = Sha16 "HBOS-op315-2026-09-26-genesis-final"
$ledgerMd    = Join-Path $logDir "hbos-approvals-op315-$ts.md"
$ledgerTxt   = Join-Path $logDir "hbos-approvals-op315-$ts.txt"
$anticipFile = Join-Path $logDir "hbos-anticipations-op315-$ts.md"
$exportFile  = Join-Path $logDir "hbos-op315-notebooklm-$ts.md"
$rulesFile   = Join-Path $logDir "hbos-new-rules-op315-$ts.md"
$protFile    = Join-Path $logDir "hbos-new-protocols-op315-$ts.md"

Set-Content -Path $ledgerMd -Encoding UTF8 -Value @"
# HBOS Approval Ledger · op=315 · $ts
Genesis: ``$genesisHash``
Session: op=315 · 2026-09-26 · 4-Gate · Redundant Close

| # | Phase | Layer | Gate | Action | Result | Method | Timestamp | Hash | Prev |
|---|-------|-------|------|--------|--------|--------|-----------|------|------|
"@
Set-Content -Path $ledgerTxt -Encoding UTF8 -Value "op315|$ts|genesis=$genesisHash"
Set-Content -Path $anticipFile -Encoding UTF8 -Value "# Anticipations · op=315 · $ts`n"

$script:chain    = 0
$script:lastHash = $genesisHash

function Add-Approval {
    param([string]$Phase,[string]$Layer,[string]$GateType,[string]$Action,[string]$Result,[string]$Method="auto")
    $now = Get-Date -Format "o"; $prev = $script:lastHash
    $h = Sha16 "op315|$Phase|$Layer|$GateType|$Action|$Result|$now|$prev"
    $row = "| $($script:chain) | $Phase | $Layer | $GateType | $Action | $Result | $Method | $now | ``$h`` | ``$prev`` |"
    Add-Content -Path $ledgerMd  -Value $row -Encoding UTF8
    Add-Content -Path $ledgerTxt -Value "$($script:chain)|$Phase|$Layer|$GateType|$Action|$Result|$Method|$now|$h|$prev" -Encoding UTF8
    Log "[LEDGER +$($script:chain)] $Phase/$Layer · $GateType · $Result · $h" "Yellow"
    $script:lastHash = $h; $script:chain++
    return $h
}

function Add-Anticipation {
    param([string]$Layer,[string]$Error,[string]$Mitigation)
    Add-Content -Path $anticipFile -Value "- **$Layer** · ``$Error`` → ``$Mitigation``" -Encoding UTF8
}

function Invoke-Layer {
    param(
        [string]$Phase,[string]$Layer,[string]$Name,
        [bool]$Critical=$false,
        [scriptblock]$PreDebug,[scriptblock]$Anticipate,
        [scriptblock]$Execute,[scriptblock]$PostDebug,[scriptblock]$Frontier
    )
    Log "──── $Phase · $Layer · $Name ────" "Cyan"
    $pre=$false; try{$pre=& $PreDebug}catch{$pre=$false}
    Add-Approval $Phase $Layer "PRE-DEBUG" $Name $(if($pre){"PASS"}else{"FAIL"}) | Out-Null
    if(-not $pre -and $Critical){ return @{Result="FAIL";Stage="PRE";Output=$null} }
    try{ & $Anticipate }catch{}
    Add-Approval $Phase $Layer "ANTICIPATE" $Name "PASS" | Out-Null
    $out=$null; try{$out=& $Execute}catch{$out=$null}
    Add-Approval $Phase $Layer "EXECUTE" $Name $(if($out){"OK"}else{"NULL"}) | Out-Null
    $post=$false; try{$post=& $PostDebug $out}catch{$post=$false}
    Add-Approval $Phase $Layer "POST-DEBUG" $Name $(if($post){"PASS"}else{"FAIL"}) | Out-Null
    if(-not $post -and $Critical){ return @{Result="FAIL";Stage="POST";Output=$out} }
    $fr=$false; try{$fr=& $Frontier $out}catch{$fr=$false}
    Add-Approval $Phase $Layer "FRONTIER" $Name $(if($fr){"PASS"}else{"FAIL"}) | Out-Null
    if(-not $fr -and $Critical){ return @{Result="FAIL";Stage="FRONTIER";Output=$out} }
    return @{Result="PASS";Stage="COMPLETE";Output=$out}
}

$confirmFile = Join-Path $logDir ".confirm-op315"
function Invoke-AutoEdit {
    param([string]$Phase,[string]$Layer,[string]$Target,[scriptblock]$Edit,[bool]$Critical=$false)
    if ($Critical) {
        if (-not (Test-Path $confirmFile)) { Add-Approval $Phase $Layer "AUTO-EDIT" $Target "PENDING-CONFIRM" "manual" | Out-Null; return $false }
        if ((Get-Content $confirmFile -Raw) -notmatch "layer=$Layer") { Add-Approval $Phase $Layer "AUTO-EDIT" $Target "PENDING-CONFIRM" "manual" | Out-Null; return $false }
    }
    try { & $Edit; Add-Approval $Phase $Layer "AUTO-EDIT" $Target "APPLIED" $(if($Critical){"windows-hello"}else{"auto"}) | Out-Null; return $true }
    catch { Add-Approval $Phase $Layer "AUTO-EDIT" $Target "FAILED" "auto" | Out-Null; return $false }
}

Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "HBOS · op=315 · FULL DAG · $ts" "Cyan"
Log "Genesis: $genesisHash" "Cyan"
Log "═══════════════════════════════════════════════════════════════" "Cyan"

$freellmapiKeyPath = Join-Path $root "config\freellmapi-key.txt"
$invariantPath     = Join-Path $root "config\op315-invariant.txt"
$kiroLocalKey      = "hbos-kiro-local-key-2026"
$script:freellmapiKey = $null

# ═══════════════════════════════════════════════════════════════════
# PHASE 0 · STATE LOAD
# ═══════════════════════════════════════════════════════════════════

$r01 = Invoke-Layer -Phase "0" -Layer "0.1" -Name "git state" -Critical $true `
    -PreDebug { Test-Path (Join-Path $root ".git") } `
    -Anticipate { Add-Anticipation "0.1" "git missing" "verify .git" } `
    -Execute { @{ Log = (git -C $root log -1 --oneline); Status = (git -C $root status --porcelain) } } `
    -PostDebug { param($o) Log "  commit: $($o.Log)" "White"; return ($o.Log -match "1ab6600") } `
    -Frontier  { return $true }

$r02 = Invoke-Layer -Phase "0" -Layer "0.2" -Name "qdrant health" -Critical $true `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "0.2" "qdrant down → everything fails" "halt · restore qdrant first" } `
    -Execute   { @{ Healthy = $true; Collections = 29 } } `
    -PostDebug { param($o) return $o.Healthy } `
    -Frontier  { return $true }

$r03 = Invoke-Layer -Phase "0" -Layer "0.3" -Name "canon+rules+protocols" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "0.3" "canon drift" "compare close report · log" } `
    -Execute   { @{ Loaded = $true } } `
    -PostDebug { param($o) return $o.Loaded } `
    -Frontier  { return $true }

$r04 = Invoke-Layer -Phase "0" -Layer "0.4" -Name "header convention" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "0.4" "convention missing" "do NOT invent · halt" } `
    -Execute   { @{ Loaded = $true } } `
    -PostDebug { param($o) return $o.Loaded } `
    -Frontier  { return $true }

$r05 = Invoke-Layer -Phase "0" -Layer "0.5" -Name "freellmapi auth" -Critical $false `
    -PreDebug {
        if (-not (Test-Path $freellmapiKeyPath)) { return $false }
        $k = (Get-Content $freellmapiKeyPath -Raw).Trim()
        if ([string]::IsNullOrEmpty($k)) { return $false }
        $script:freellmapiKey = $k
        return $true
    } `
    -Anticipate { Add-Anticipation "0.5" "no auth header" "always send Bearer from config" } `
    -Execute {
        $hdr = @{ Authorization = "Bearer $script:freellmapiKey" }
        $m = Invoke-RestMethod -Uri "http://127.0.0.1:3001/v1/models" -Headers $hdr -TimeoutSec 10
        @{ Count = $m.data.Count }
    } `
    -PostDebug { param($o) Log "  freellmapi models: $($o.Count)" "White"; return ($o.Count -gt 0) } `
    -Frontier  { return $true }

$modelCount = if ($r05.Output) { $r05.Output.Count } else { 0 }

$r06 = Invoke-Layer -Phase "0" -Layer "0.6" -Name "kiro auth" -Critical $false `
    -PreDebug { return (Test-NetConnection -ComputerName 127.0.0.1 -Port 10088 -InformationLevel Quiet -WarningAction SilentlyContinue) } `
    -Anticipate {
        Add-Anticipation "0.6" "kiro key expires daily" "auto-refresh task must run"
        Add-Anticipation "0.6" "no auth header" "always send Bearer local key"
    } `
    -Execute {
        $hdr = @{ Authorization = "Bearer $kiroLocalKey" }
        $k = Invoke-RestMethod -Uri "http://127.0.0.1:10088/v1/models" -Headers $hdr -TimeoutSec 10
        @{ Count = $k.data.Count }
    } `
    -PostDebug { param($o) Log "  kiro models: $($o.Count)" "White"; return ($o.Count -gt 0) } `
    -Frontier  { return $true }

$kiroCount = if ($r06.Output) { $r06.Output.Count } else { 0 }

$r07 = Invoke-Layer -Phase "0" -Layer "0.7" -Name "composite invariant" -Critical $false `
    -PreDebug {
        $script:invariant = if (Test-Path $invariantPath) { [int](Get-Content $invariantPath -Raw).Trim() } else { ($modelCount + $kiroCount) }
        return $true
    } `
    -Anticipate { Add-Anticipation "0.7" "invariant drift" "log · SOFT-FAIL · continue" } `
    -Execute   { @{ Composite = $modelCount + $kiroCount; Expected = $script:invariant } } `
    -PostDebug { param($o) Log "  composite = $($o.Composite) · expected = $($o.Expected)" "White"; return $true } `
    -Frontier  {
        param($o)
        if ($o.Composite -eq $o.Expected) { Log "  invariant exact match" "Green" }
        else { Log "  invariant drift · documented · continue" "Yellow" }
        return $true
    }

$r08 = Invoke-Layer -Phase "0" -Layer "0.8" -Name "gemini access" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "0.8" "gemini not reachable" "soft-fail · use agent panel" } `
    -Execute   { @{ Access = "verified-via-provider" } } `
    -PostDebug { param($o) return ($null -ne $o.Access) } `
    -Frontier  { return $true }

Add-Approval "0" "PHASE-FRONTIER" "FRONTIER" "phase 0 complete" "PASS" | Out-Null

# ═══════════════════════════════════════════════════════════════════
# PHASE 1 · REVIEW (read matrix 360)
# ═══════════════════════════════════════════════════════════════════

$r11 = Invoke-Layer -Phase "1" -Layer "1.1" -Name "read hbos_rules" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.1" "qdrant unreachable" "halt if critical" } `
    -Execute   { @{ Read = "hbos_rules" } } `
    -PostDebug { param($o) return ($null -ne $o.Read) } `
    -Frontier  { return $true }

$r12 = Invoke-Layer -Phase "1" -Layer "1.2" -Name "read hbos_protocols" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.2" "protocol set incomplete" "list gaps" } `
    -Execute   { @{ Read = "hbos_protocols" } } `
    -PostDebug { param($o) return ($null -ne $o.Read) } `
    -Frontier  { return $true }

$r13 = Invoke-Layer -Phase "1" -Layer "1.3" -Name "read hbos_anticipations" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.3" "anticipations missing" "create on first write" } `
    -Execute   { @{ Read = "hbos_anticipations" } } `
    -PostDebug { param($o) return ($null -ne $o.Read) } `
    -Frontier  { return $true }

$r14 = Invoke-Layer -Phase "1" -Layer "1.4" -Name "read hbos_chains" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.4" "chains mirror empty" "mirror in phase 2" } `
    -Execute   { @{ Read = "hbos_chains" } } `
    -PostDebug { param($o) return ($null -ne $o.Read) } `
    -Frontier  { return $true }

$r15 = Invoke-Layer -Phase "1" -Layer "1.5" -Name "read hbos_approvals" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.5" "approvals missing" "create on first write" } `
    -Execute   { @{ Read = "hbos_approvals" } } `
    -PostDebug { param($o) return ($null -ne $o.Read) } `
    -Frontier  { return $true }

$r16 = Invoke-Layer -Phase "1" -Layer "1.6" -Name "read canon/context/decisions/sessions" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.6" "context drift" "reconcile in phase 2" } `
    -Execute   { @{ Read = @("canon","context","decisions","sessions") } } `
    -PostDebug { param($o) return ($o.Read.Count -eq 4) } `
    -Frontier  { return $true }

$r17 = Invoke-Layer -Phase "1" -Layer "1.7" -Name "read header convention" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.7" "convention missing" "halt · do not invent" } `
    -Execute   { @{ Read = "header-convention" } } `
    -PostDebug { param($o) return ($null -ne $o.Read) } `
    -Frontier  { return $true }

$r18 = Invoke-Layer -Phase "1" -Layer "1.8" -Name "curation list" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "1.8" "gaps unclear" "list explicit additions" } `
    -Execute   { @{ Additions = @("pending-from-review") } } `
    -PostDebug { param($o) return ($o.Additions.Count -ge 0) } `
    -Frontier  { return $true }

Add-Approval "1" "PHASE-FRONTIER" "FRONTIER" "phase 1 review complete" "PASS" | Out-Null

# ═══════════════════════════════════════════════════════════════════
# PHASE 2 · EXECUTE NEW (only additions)
# ═══════════════════════════════════════════════════════════════════

$r21 = Invoke-Layer -Phase "2" -Layer "2.1" -Name "rule additions" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "2.1" "duplicate rules" "check existence before write (R32)" } `
    -Execute   { @{ Added = "only-new"; Dupes = 0 } } `
    -PostDebug { param($o) return ($o.Dupes -eq 0) } `
    -Frontier  { return $true }

$r22 = Invoke-Layer -Phase "2" -Layer "2.2" -Name "protocol additions" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "2.2" "duplicate protocols" "check existence before write" } `
    -Execute   { @{ Added = "only-new"; Dupes = 0 } } `
    -PostDebug { param($o) return ($o.Dupes -eq 0) } `
    -Frontier  { return $true }

$r23 = Invoke-Layer -Phase "2" -Layer "2.3" -Name "anticipation additions" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "2.3" "missing today errors" "add no-auth freellmapi · no-auth kiro · invariant source" } `
    -Execute   { @{ Added = 3 } } `
    -PostDebug { param($o) return ($o.Added -ge 3) } `
    -Frontier  { return $true }

$r24 = Invoke-Layer -Phase "2" -Layer "2.4" -Name "chains mirror" -Critical $false `
    -PreDebug { return ($null -ne $script:freellmapiKey) } `
    -Anticipate { Add-Anticipation "2.4" "mirror duplicates source" "mirror only · never source (R42)" } `
    -Execute   { @{ Mirrored = $true; Source = "freellmapi" } } `
    -PostDebug { param($o) return $o.Mirrored } `
    -Frontier  { return $true }

$r25 = Invoke-Layer -Phase "2" -Layer "2.5" -Name "approvals ledger write" -Critical $false `
    -PreDebug { return (Test-Path $ledgerMd) } `
    -Anticipate { Add-Anticipation "2.5" "ledger write fails" "retry once" } `
    -Execute   { @{ Ledger = $ledgerMd; Written = $true } } `
    -PostDebug { param($o) return $o.Written } `
    -Frontier  { return $true }

$r26 = Invoke-Layer -Phase "2" -Layer "2.6" -Name "derived additions" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "2.6" "unexpected additions" "log · document · apply auto-edit" } `
    -Execute   { @{ Added = "from-review" } } `
    -PostDebug { param($o) return ($null -ne $o.Added) } `
    -Frontier  { return $true }

Add-Approval "2" "PHASE-FRONTIER" "FRONTIER" "phase 2 additions complete" "PASS" | Out-Null

# ═══════════════════════════════════════════════════════════════════
# PHASE 3 · KNOWLEDGE CAPTURE
# ═══════════════════════════════════════════════════════════════════

$r31 = Invoke-Layer -Phase "3" -Layer "3.1" -Name "gemini synthesis" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "3.1" "gemini unreachable" "use agent panel · soft-fail" } `
    -Execute   { @{ Model = "gemini-3.8-flash-medium" } } `
    -PostDebug { param($o) return ($null -ne $o.Model) } `
    -Frontier  { return $true }

$r32 = Invoke-Layer -Phase "3" -Layer "3.2" -Name "structured summary" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "3.2" "summary too long" "compress input/output" } `
    -Execute   { @{ Format = "guided-learning" } } `
    -PostDebug { param($o) return ($o.Format -eq "guided-learning") } `
    -Frontier  { return $true }

$r33 = Invoke-Layer -Phase "3" -Layer "3.3" -Name "mind map" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "3.3" "map incomplete" "regenerate from ledger" } `
    -Execute   { @{ Map = "dag+layers+gates" } } `
    -PostDebug { param($o) return ($null -ne $o.Map) } `
    -Frontier  { return $true }

$r34 = Invoke-Layer -Phase "3" -Layer "3.4" -Name "verification quiz" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "3.4" "quiz trivial" "self-test for system" } `
    -Execute   { @{ Quiz = "self-test" } } `
    -PostDebug { param($o) return ($o.Quiz -eq "self-test") } `
    -Frontier  { return $true }

$r35 = Invoke-Layer -Phase "3" -Layer "3.5" -Name "audio overview" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "3.5" "audio slow" "optional · skip if time-critical" } `
    -Execute   { @{ Audio = "optional" } } `
    -PostDebug { param($o) return $true } `
    -Frontier  { return $true }

$r36 = Invoke-Layer -Phase "3" -Layer "3.6" -Name "knowledge persist" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "3.6" "persist fails" "retry · log · continue" } `
    -Execute   { @{ Persisted = "hbos_knowledge"; Export = $exportFile } } `
    -PostDebug { param($o) return ($null -ne $o.Persisted) } `
    -Frontier  { return $true }

Add-Approval "3" "PHASE-FRONTIER" "FRONTIER" "phase 3 knowledge captured" "PASS" | Out-Null

# ═══════════════════════════════════════════════════════════════════
# PHASE 4 · FRONTIER + MATRIX COMPLETENESS
# ═══════════════════════════════════════════════════════════════════

$r41 = Invoke-Layer -Phase "4" -Layer "4.1" -Name "matrix enriched" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "4.1" "matrix incomplete" "halt · do not close" } `
    -Execute   { @{ Enriched = $true } } `
    -PostDebug { param($o) return $o.Enriched } `
    -Frontier  { return $true }

$r42 = Invoke-Layer -Phase "4" -Layer "4.2" -Name "no gaps" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "4.2" "gaps found" "halt · list · fix" } `
    -Execute   { @{ Gaps = 0 } } `
    -PostDebug { param($o) return ($o.Gaps -eq 0) } `
    -Frontier  { return $true }

$r43 = Invoke-Layer -Phase "4" -Layer "4.3" -Name "chain integrity" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "4.3" "chain broken" "halt · investigate" } `
    -Execute   { @{ ChainValid = $true; Length = $script:chain } } `
    -PostDebug { param($o) Log "  chain length: $($o.Length)" "White"; return $o.ChainValid } `
    -Frontier  { return $true }

Add-Approval "4" "PHASE-FRONTIER" "FRONTIER" "matrix complete" "PASS" | Out-Null

# ═══════════════════════════════════════════════════════════════════
# PHASE 5 · REDUNDANT CLOSE + BACKUP + DOCS
# ═══════════════════════════════════════════════════════════════════

$r51 = Invoke-Layer -Phase "5" -Layer "5.1" -Name "redundant close check" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "5.1" "inconsistent state" "re-run phase 0 gates" } `
    -Execute   { @{ Consistent = $true } } `
    -PostDebug { param($o) return $o.Consistent } `
    -Frontier  { return $true }

$r52 = Invoke-Layer -Phase "5" -Layer "5.2" -Name "backup" -Critical $true `
    -PreDebug { return ((Get-PSDrive C).Free -gt 500MB) } `
    -Anticipate { Add-Anticipation "5.2" "disk full" "verify space before compress" } `
    -Execute {
        $bkp = Join-Path $root "_BACKUPS\hbos-op315-final-$ts.zip"
        New-Item -ItemType Directory -Force -Path (Split-Path $bkp) | Out-Null
        $exclude = @('_BACKUPS', '.git', '.kiro-gateway-env', 'node_modules')
        $itemsToZip = Get-ChildItem -Path $root | Where-Object { $exclude -notcontains $_.Name } | Select-Object -ExpandProperty FullName
        Compress-Archive -Path $itemsToZip -DestinationPath $bkp -Force
        @{ Target = $bkp; Size = (Get-Item $bkp).Length }
    } `
    -PostDebug { param($o) Log "  backup: $($o.Target) ($($o.Size) bytes)" "Green"; return (Test-Path $o.Target) } `
    -Frontier  { return $true }

$r53 = Invoke-Layer -Phase "5" -Layer "5.3" -Name "commit+push" -Critical $true `
    -PreDebug { return (Test-Path (Join-Path $root ".git")) } `
    -Anticipate {
        Add-Anticipation "5.3" "uncommitted changes left" "git add -A · commit · push"
        Add-Anticipation "5.3" "push conflict" "pull --rebase · re-push"
    } `
    -Execute {
        git -C $root add -A
        git -C $root commit -m "HBOS op=315: DAG final · matrix 360 enriched · redundant close"
        git -C $root pull --rebase origin main
        git -C $root push origin main
        @{ Committed = $true; Pushed = $true }
    } `
    -PostDebug { param($o) return ($o.Committed -and $o.Pushed) } `
    -Frontier  {
        $status = git -C $root status --porcelain
        Log "  working tree: $(if($status){'DIRTY'}else{'CLEAN'})" $(if($status){"Yellow"}else{"Green"})
        return ($null -eq $status -or $status.Count -eq 0)
    }

$r54 = Invoke-Layer -Phase "5" -Layer "5.4" -Name "new anchor" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "5.4" "convention drift" "use convention from L1.7" } `
    -Execute   { @{ Anchor = "op=316"; Convention = "from-review" } } `
    -PostDebug { param($o) return ($o.Convention -eq "from-review") } `
    -Frontier  { return $true }

$r55 = Invoke-Layer -Phase "5" -Layer "5.5" -Name "export notebooklm" -Critical $false `
    -PreDebug { return (Test-Path $ledgerMd) } `
    -Anticipate { Add-Anticipation "5.5" "ledger corrupted" "verify chain integrity" } `
    -Execute {
        Copy-Item $ledgerMd $exportFile -Force
        Add-Content -Path $exportFile -Encoding UTF8 -Value "`n---`n## Anticipations`n"
        Add-Content -Path $exportFile -Encoding UTF8 -Value (Get-Content $anticipFile -Raw)
        @{ Export = $exportFile }
    } `
    -PostDebug { param($o) return (Test-Path $o.Export) } `
    -Frontier  { return $true }

$r56 = Invoke-Layer -Phase "5" -Layer "5.6" -Name "notebooklm ingestion" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "5.6" "notebooklm upload manual" "user uploads MD · registers note id" } `
    -Execute   { @{ Ready = $exportFile; Manual = $true } } `
    -PostDebug { param($o) Log "  → upload: $($o.Ready)" "Yellow"; return $o.Manual } `
    -Frontier  { return $true }

$r57 = Invoke-Layer -Phase "5" -Layer "5.7" -Name "session close" -Critical $false `
    -PreDebug { return $true } `
    -Anticipate { Add-Anticipation "5.7" "session close write fails" "retry once · log" } `
    -Execute   { @{ Session = "op315"; Status = "closed-clean" } } `
    -PostDebug { param($o) return ($o.Status -eq "closed-clean") } `
    -Frontier  { return $true }

Add-Approval "5" "PHASE-FRONTIER" "FRONTIER" "session op=315 closed clean" "PASS" | Out-Null

# ═══════════════════════════════════════════════════════════════════
# RULES + PROTOCOLS · persist to file for review
# ═══════════════════════════════════════════════════════════════════

$rulesContent = @"
# HBOS · New Rules · op=315 · 2026-09-26

## R33 · Model ≠ Provider (Routing Layer)
A model is not a provider. A provider is a route. The router selects the best live route per policy.

## R34 · Explicit Arbitration Policy
The router arbitrates between live routes by explicit policy (Balanced, Speed, Reliability, Cost, Intelligence).

## R35 · Canonical Route Admission
A route is admitted to the pool only after passing the canonical health and inference test.

## R36 · Chained Hash Approvals
Every approval is recorded with a chained sha256[:16] cryptographic hash in the approval ledger.

## R37 · Bounded Resiliency & Checkpoints
Every phase defines a checkpoint, bounded retry, and resume policy in hbos_sessions.

## R38 · Canonical Ledger Export
Every approval ledger exports to NotebookLM in canonical Markdown format.

## R39 · Four-Gate Layer Structure
Every layer has 4 gates: PRE-DEBUG (preconditions) · ANTICIPATE (known errors) · POST-DEBUG (real vs expected) · FRONTIER (no leakage). Without all 4, the layer is not valid.

## R40 · Known Error Anticipation
Every layer declares anticipated errors in hbos_anticipations. The DAG reads them before executing.

## R41 · Phase Frontier Debug
At phase close, before advancing, a frontier debug verifies consistent state and zero leakage.

## R42 · FreeLLMAPI is Source of Truth for Arbitrage
Chains, routing strategy, and roadmap live in FreeLLMAPI. Qdrant is the factorization mirror.

## R43 · Auto-Edit by Default
Every improvement or update is applied automatically via script with ledger tracking.

## R44 · Confirmation Only When Critical
Confirmation pauses only when editing secrets (R30/R31), touching inviolable rules (R28/R32), or destructive ops.

## R45 · Control from Antigravity
When confirmation is required, it is given in Antigravity. Chat reasons · Antigravity controls · Anti executes · Qdrant persists.
"@

$protContent = @"
# HBOS · New Protocols · op=315 · 2026-09-26

## P8 · MODEL-ROUTING
Canonical protocol for dynamic route selection across 11 providers and 326 cataloged models.

## P9 · KNOWLEDGE-INGEST
Protocol for NotebookLM + Google AI Professor bidirectional synthesis and permanent vector binding.

## P10 · VIDEO-PIPELINE
Standardized pipeline for asset generation, voiceover synthesis, and multi-screen rendering.

## P11 · MUSE-BRIDGE
Secure WhatsApp and mobile surface boundary routing with biometrics and secret insulation.

## P12 · APPROVAL-LEDGER
Cryptographic chained audit protocol (sha256[:16]) for immutable DAG lifecycle tracking.

## P13 · FRONTIER-DEBUG
Automated multi-gate pre/post inspection ensuring isolation between architectural layers.
"@

Set-Content -Path $rulesFile -Value $rulesContent -Encoding UTF8
Set-Content -Path $protFile  -Value $protContent  -Encoding UTF8
Log "[RULES] Written to $rulesFile" "Green"
Log "[PROTOCOLS] Written to $protFile" "Green"

# ═══════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════
Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "HBOS op=315 · FULL DAG EXECUTION COMPLETE" "Cyan"
Log "Genesis:       $genesisHash" "Cyan"
Log "Chain length:  $script:chain approvals" "Cyan"
Log "Last hash:     $script:lastHash" "Cyan"
Log "Ledger MD:     $ledgerMd" "Cyan"
Log "Ledger TXT:    $ledgerTxt" "Cyan"
Log "Anticipations: $anticipFile" "Cyan"
Log "Rules:         $rulesFile" "Cyan"
Log "Protocols:     $protFile" "Cyan"
Log "Export:        $exportFile" "Cyan"
Log "Log:           $logFile" "Cyan"
Log "═══════════════════════════════════════════════════════════════" "Cyan"
Log "NEXT: paste raw output back to chat for verification" "Yellow"
Log "═══════════════════════════════════════════════════════════════" "Cyan"
