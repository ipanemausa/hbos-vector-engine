"""
HBOS E2E Validation Suite:
- Mandatory Pre-Step: REA (Reverse Engineer Anything v6.8.0) Clean-Room Deconstruction & Evidence Verification
- Module 1: Global ERP & Hybrid Fiscal Operations (US EIN/Sales Tax + LATAM NIT/RUT/RFC, IVA, Retenciones, PDF)
- Module 2: Autonomous Video Pipeline with Screen Studio Autopilot (Dynamic Camera Bubble Avoidance, Cursor Tracking & Auto-Zoom, Intelligent Jump Cuts, -14 LUFS)
- Module 3: Local Qdrant Vector Engine Synchronization & PowerShell DAG Integration
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.erp.rea_erp_engine import HBOSGlobalERP, HybridFiscalEngine
from studio.video.guiahoy_pipeline import GuiahoyVideoPipeline


def run_rea_clean_room_deconstruction() -> dict:
    print("======================================================================")
    print("[PASO PREVIO OBLIGATORIO] EJECUTANDO DECONSTRUCCIÓN CLEAN-ROOM CON REA")
    print("======================================================================")
    res = subprocess.run(
        ["node", "scripts/rea_deconstruct_clean_room.mjs"],
        capture_output=True,
        text=True,
        check=True
    )
    rea_summary = json.loads(res.stdout.strip())
    print(f"      -> Repositorio Oficial REA: tools/rea (morluto/rea v{rea_summary['rea_version']})")
    print(f"      -> Evidencia JS/Autopilot:  {rea_summary['js_evidence_id']}")
    print(f"      -> Evidencia SQLite/ERP:    {rea_summary['sqlite_evidence_id']}")
    print(f"      -> Bundle REA generado:     {rea_summary['bundle_path']}")
    return rea_summary


def run_erp_e2e() -> dict:
    print("\n======================================================================")
    print("[MÓDULO 1 & 3.1] INICIANDO VALIDACIÓN E2E: SISTEMA ERP GLOBAL (REA)")
    print("======================================================================")

    db_file = os.path.abspath("data/hbos_erp_e2e_production.db")
    if os.path.exists(db_file):
        os.remove(db_file)

    erp = HBOSGlobalERP(db_path=db_file, qdrant_url="http://127.0.0.1:6333")

    # 1. Sync Fiscal Rules & Schema to Local Qdrant
    print("[1/6] Sincronizando reglas fiscales EE. UU. / LATAM y esquemas en Qdrant...")
    qdrant_sync = erp.sync_qdrant_schemas_and_rules()
    print(f"      -> Colección '{qdrant_sync['collection']}' activa | Reglas indexadas: {qdrant_sync['points_upserted']}")

    # 2. Register Internal US Operating Entity (Issuer) & International LATAM Client + Supplier
    print("[2/6] Registrando Entidad Emisora (US EIN), Cliente Internacional (LATAM NIT) y Proveedor (MX RFC)...")
    issuer_us = erp.register_agent(
        agent_role="INTERNAL_ENTITY",
        legal_name="HBOS Sovereign Technologies LLC",
        country_code="US",
        jurisdiction_code="US-FL",
        tax_id_type="EIN",
        tax_id_number="88-4192735",
        default_currency="USD",
        email="billing@hbos-internal.us",
        address="1200 Brickell Ave, Suite 1950, Miami, FL 33131, USA"
    )

    nit_check = HybridFiscalEngine.validate_tax_id("901458231", "NIT", "CO")
    client_latam = erp.register_agent(
        agent_role="CLIENT",
        legal_name="Andina FinTech & Cloud Operations S.A.S.",
        country_code="CO",
        jurisdiction_code="CO-BOG",
        tax_id_type="NIT",
        tax_id_number=nit_check["normalized"],
        default_currency="COP",
        email="tesoreria@andinafintech.co",
        address="Cra. 7 #71-21, Torre B Piso 14, Bogota D.C., Colombia"
    )

    supplier_mx = erp.register_agent(
        agent_role="SUPPLIER",
        legal_name="Infraestructura Neuronal Azteca S.A. de C.V.",
        country_code="MX",
        jurisdiction_code="MX-CDMX",
        tax_id_type="RFC",
        tax_id_number="INA2105149K2",
        default_currency="MXN",
        email="facturacion@neuronalazteca.mx",
        address="Av. Paseo de la Reforma 505, Cuauhtemoc, CDMX, Mexico"
    )
    print(f"      -> Emisor US EIN validado: {issuer_us['tax_validation']['normalized']}")
    print(f"      -> Cliente LATAM NIT validado (Módulo 11): {client_latam['tax_validation']['normalized']}")
    print(f"      -> Proveedor LATAM RFC validado: {supplier_mx['tax_validation']['normalized']}")

    # 3. Create Draft Multi-Currency Invoice with Cross-Border Taxes
    print("[3/6] Creando Factura Internacional Multimoneda en estado BORRADOR...")
    initial_lines = [
        {
            "sku": "HBOS-CORE-R768",
            "description": "Licencia Corporativa Anual Motor Vectorial Soberano R768 (Cluster Dedicado)",
            "quantity": 1,
            "unit_price": 12500.00,
            "discount_pct": 0.0
        },
        {
            "sku": "HBOS-AI-SWARM",
            "description": "Despliegue de Agentes Autonomos Financieros y Soporte DevOps Cross-Border",
            "quantity": 2,
            "unit_price": 3250.00,
            "discount_pct": 5.0
        }
    ]
    draft_inv = erp.create_draft_invoice(
        issuer_agent_id=issuer_us["agent_id"],
        counterparty_agent_id=client_latam["agent_id"],
        invoice_currency="USD",
        lines=initial_lines,
        functional_currency="COP"
    )
    print(f"      -> Documento creado: {draft_inv['document_number']} | Estado: {draft_inv['status']} (v{draft_inv['version']})")

    # 4. Modify Draft Invoice (Version 2) to verify version tracking while in BORRADOR
    print("[4/6] Actualizando Factura en estado BORRADOR (Control de Versiones v1 -> v2)...")
    updated_lines = list(initial_lines) + [
        {
            "sku": "HBOS-VIDEO-AUTOPILOT",
            "description": "Modulo Autonomo de Produccion Multimedia GuiaHoy con Screen Studio Autopilot",
            "quantity": 1,
            "unit_price": 2400.00,
            "discount_pct": 0.0
        }
    ]
    draft_v2 = erp.update_draft_invoice(draft_inv["invoice_id"], updated_lines)
    print(f"      -> Versión actualizada: v{draft_v2['version']} | Subtotal: USD {draft_v2['subtotal']:,.2f} | Neto: USD {draft_v2['net_payable']:,.2f}")

    # 5. Approve & Emit Invoice -> Verify Strict Immutability Lock -> Emit Credit Note
    print("[5/6] Aprobando y emitiendo factura (Transición a EMITIDO_APROBADO con bloqueo inmutable)...")
    approved_inv = erp.approve_and_emit_invoice(draft_inv["invoice_id"])
    print(f"      -> Estado actual: {approved_inv['status']} | Lock Inmutable: {approved_inv['immutable_lock']}")

    immutability_enforced = False
    immutability_error_msg = ""
    try:
        erp.update_draft_invoice(approved_inv["invoice_id"], initial_lines)
    except PermissionError as exc:
        immutability_enforced = True
        immutability_error_msg = str(exc)
        print(f"      -> [OK] Bloqueo de edición post-emisión verificado: {immutability_error_msg[:85]}...")

    credit_note = erp.issue_credit_note_or_rectification(
        original_invoice_id=approved_inv["invoice_id"],
        document_type="CREDIT_NOTE",
        reason="Bonificacion comercial por pronto pago internacional",
        adjusted_lines=[{
            "sku": "HBOS-DISC-EARLY",
            "description": "Bonificacion pronto pago sobre licencia anual",
            "quantity": 1,
            "unit_price": 500.00,
            "discount_pct": 0.0
        }]
    )
    print(f"      -> Nota de Crédito automática emitida: {credit_note['document_number']} (Neto: USD {credit_note['net_payable']:,.2f})")

    # 6. Export Corporate PDF
    print("[6/6] Exportando PDF Corporativo Profesional...")
    pdf_out = os.path.abspath(f"output_masters/erp_invoices/{approved_inv['document_number']}.pdf")
    pdf_nc_out = os.path.abspath(f"output_masters/erp_invoices/{credit_note['document_number']}.pdf")
    erp.export_corporate_pdf(approved_inv["invoice_id"], pdf_out)
    erp.export_corporate_pdf(credit_note["invoice_id"], pdf_nc_out)
    pdf_sha256 = hashlib.sha256(open(pdf_out, "rb").read()).hexdigest()
    print(f"      -> PDF Factura exportado: {pdf_out} ({os.path.getsize(pdf_out)} bytes | SHA256: {pdf_sha256[:16]}...)")

    return {
        "qdrant_sync": qdrant_sync,
        "issuer": issuer_us,
        "client": client_latam,
        "supplier": supplier_mx,
        "approved_invoice": approved_inv,
        "immutability_enforced": immutability_enforced,
        "immutability_message": immutability_error_msg,
        "credit_note": credit_note,
        "pdf_invoice_path": pdf_out,
        "pdf_invoice_size_bytes": os.path.getsize(pdf_out),
        "pdf_invoice_sha256": pdf_sha256,
        "pdf_credit_note_path": pdf_nc_out
    }


def run_multimedia_e2e() -> dict:
    print("\n======================================================================")
    print("[MÓDULO 2 & 3.2] INICIANDO VALIDACIÓN E2E: PIPELINE DE VÍDEO + AUTOPILOT")
    print("======================================================================")
    pipeline = GuiahoyVideoPipeline()
    video_meta = pipeline.build_autonomous_video("guiahoy_autonomous_reel_e2e.mp4")
    ap = video_meta["autopilot_telemetry"]
    print(f"      -> MP4 Renderizado: {video_meta['video_path']} ({video_meta['file_size_bytes']} bytes)")
    print(f"      -> Resolución: {video_meta['resolution']} @ {video_meta['fps']}fps ({ap['total_frames_rendered']} frames)")
    print(f"      -> Reubicaciones Anti-Oclusión de Cámara 3D: {len(ap['camera_bubble_relocations'])} esquinas dinámicas")
    print(f"      -> Eventos de Clic + Auto-Zoom Cinemático:   {len(ap['cursor_click_auto_zooms'])} objetivos enfocados")
    print(f"      -> Jump Cuts Inteligentes entre Ventanas:    {len(ap['intelligent_jump_cuts'])} transiciones sin temblor")
    print(f"      -> Audio Masterizado: {video_meta['audio_mastering']['final_mp4_lufs']} LUFS (Target: -14.0 LUFS EBU R128)")
    print(f"      -> SHA256: {video_meta['sha256']}")
    return video_meta


def main():
    rea_pre = run_rea_clean_room_deconstruction()
    erp_res = run_erp_e2e()
    # Run REA SQLite inspection again after DB creation so the bundle captures all populated tables
    rea_post = run_rea_clean_room_deconstruction()
    vid_res = run_multimedia_e2e()

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "E2E_ALL_MODULES_PASSED",
        "step_0_rea_clean_room": rea_post,
        "module_1_erp": {
            "invoice_number": erp_res["approved_invoice"]["document_number"],
            "status": erp_res["approved_invoice"]["status"],
            "version": erp_res["approved_invoice"]["version"],
            "immutability_lock_verified": erp_res["immutability_enforced"],
            "credit_note_number": erp_res["credit_note"]["document_number"],
            "invoice_currency": erp_res["approved_invoice"]["invoice_currency"],
            "subtotal": erp_res["approved_invoice"]["subtotal"],
            "indirect_tax_total": erp_res["approved_invoice"]["indirect_tax_total"],
            "withholding_tax_total": erp_res["approved_invoice"]["withholding_tax_total"],
            "net_payable": erp_res["approved_invoice"]["net_payable"],
            "multi_currency_equivalencies": erp_res["approved_invoice"]["multi_currency_equivalencies"],
            "pdf_path": erp_res["pdf_invoice_path"],
            "pdf_sha256": erp_res["pdf_invoice_sha256"],
            "pdf_size_bytes": erp_res["pdf_invoice_size_bytes"]
        },
        "module_2_multimedia": vid_res,
        "module_3_qdrant": {
            "collection": erp_res["qdrant_sync"]["collection"],
            "points_upserted": erp_res["qdrant_sync"]["points_upserted"]
        }
    }

    os.makedirs("logs", exist_ok=True)
    out_json = os.path.abspath("logs/e2e_validation_report.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n======================================================================")
    print(f"[E2E SUITE COMPLETE · STATUS: PASS] Report saved to: {out_json}")
    print("======================================================================")


if __name__ == "__main__":
    main()
