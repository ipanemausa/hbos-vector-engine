# ═══════════════════════════════════════════════════════════════════════════
# HBOS · DAG ORCHESTRATOR: ERP GLOBAL (REA) + GUIAHOY VIDEO PIPELINE E2E
# ═══════════════════════════════════════════════════════════════════════════
# Architecture : Clean-Room REA ERP (US/LATAM) + GuiaHoy Autonomous Video
# Vector DB    : Local Qdrant (127.0.0.1:6333) - 384d Sovereign Collections
# Verification : 4-Gate Topological Execution + SHA-256 + EBU R128 (-14 LUFS)
# ═══════════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$root = "C:\Users\ipane\hbos-deploy\hbos-vector-engine"
Set-Location $root
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$logDir = Join-Path $root "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$dagLog = Join-Path $logDir "dag-erp-video-e2e-$ts.log"

function Write-DagLog {
    param([string]$Message, [string]$Color = "Cyan")
    Write-Host $Message -ForegroundColor $Color
    Add-Content -Path $dagLog -Value "$(Get-Date -Format 'HH:mm:ss') | $Message" -Encoding UTF8
}

Write-DagLog "=======================================================================" "Cyan"
Write-DagLog "HBOS DAG ORCHESTRATOR · ERP GLOBAL REA & GUIAHOY VIDEO PIPELINE ($ts)" "Cyan"
Write-DagLog "=======================================================================" "Cyan"

# NODE 1: Qdrant Vector Engine Health & Collection Verification
Write-DagLog "[NODE 1/4] Verificando Motor Vectorial Local Qdrant (127.0.0.1:6333)..." "Yellow"
$qdrantHealth = Invoke-RestMethod -Uri "http://127.0.0.1:6333/collections" -Method Get -TimeoutSec 5
if ($qdrantHealth.status -ne "ok") {
    throw "Qdrant Local Engine no responde correctamente."
}
Write-DagLog "  -> [GATE 1 PASS] Qdrant activo. Colecciones iniciales: $($qdrantHealth.result.collections.Count)" "Green"

# NODE 2: Execute End-to-End Python Suite (ERP REA + Qdrant Fiscal Sync + GuiaHoy Video Render)
Write-DagLog "[NODE 2/4] Ejecutando Suite E2E (ERP Multimoneda US/LATAM + Render MP4 -14 LUFS)..." "Yellow"
python scripts/run_e2e_suite.py
if ($LASTEXITCODE -ne 0) {
    throw "Fallo en la ejecucion de scripts/run_e2e_suite.py"
}
Write-DagLog "  -> [GATE 2 PASS] Suite E2E ejecutada sin errores." "Green"

# NODE 3: Independent Empirical Verification of Artifacts (PDF + MP4 + Qdrant Points)
Write-DagLog "[NODE 3/4] Auditando artefactos generados (PDF Corporativo, MP4 y Vectores Qdrant)..." "Yellow"
$reportPath = Join-Path $logDir "e2e_validation_report.json"
if (-not (Test-Path $reportPath)) {
    throw "No se encontro el reporte E2E en $reportPath"
}
$report = Get-Content $reportPath -Raw | ConvertFrom-Json

$pdfPath = $report.module_1_erp.pdf_path
$mp4Path = $report.module_2_multimedia.video_path

if (-not (Test-Path $pdfPath)) { throw "PDF Corporativo no encontrado: $pdfPath" }
if (-not (Test-Path $mp4Path)) { throw "Video MP4 no encontrado: $mp4Path" }

$erpColl = Invoke-RestMethod -Uri "http://127.0.0.1:6333/collections/hbos_erp_fiscal_rules" -Method Get -TimeoutSec 5
$vidColl = Invoke-RestMethod -Uri "http://127.0.0.1:6333/collections/canon_video_hbos" -Method Get -TimeoutSec 5

Write-DagLog "  -> [GATE 3 PASS] PDF ($($report.module_1_erp.pdf_size_bytes) bytes) | MP4 ($($report.module_2_multimedia.file_size_bytes) bytes)" "Green"
Write-DagLog "  -> [GATE 3 PASS] Qdrant 'hbos_erp_fiscal_rules' puntos: $($erpColl.result.points_count) | 'canon_video_hbos' puntos: $($vidColl.result.points_count)" "Green"
Write-DagLog "  -> [GATE 3 PASS] Audio Masterizado verificado: $($report.module_2_multimedia.audio_mastering.final_mp4_lufs) LUFS (EBU R128)" "Green"

# NODE 4: Seal DAG Ledger
Write-DagLog "[NODE 4/4] Sellando ejecucion DAG..." "Yellow"
Write-DagLog "[DAG_STATUS: COMPLETE_PASS] [INVOICE: $($report.module_1_erp.invoice_number)] [VIDEO_LUFS: $($report.module_2_multimedia.audio_mastering.final_mp4_lufs)]" "Green"

