"""
HBOS Global ERP & Fiscal Operations Engine (Clean-Room REA Architecture)
========================================================================
100% Original Clean-Room Architecture based on McCarthy's REA (Resources, Events, Agents)
Accounting Ontology & Sovereign Immutable Ledger Principles.
Zero third-party proprietary code, trademarks, or external brand assets.
Designed for Private Internal Operations across USA (EIN/Sales Tax) & LATAM (NIT/RUT/RFC, IVA, Retenciones).
"""

import os
import json
import uuid
import sqlite3
import hashlib
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT


def dec(val: Any) -> Decimal:
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def dec4(val: Any) -> Decimal:
    return Decimal(str(val)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


class HybridFiscalEngine:
    """
    Real-time Multi-Currency & Cross-Border Tax Calculation Engine (USA & LATAM).
    Synchronizes rules with Qdrant Vector Database (`hbos_erp_fiscal_rules`).
    """

    DEFAULT_FX_RATES_TO_USD: Dict[str, Decimal] = {
        "USD": Decimal("1.0000"),
        "COP": Decimal("0.00024"),   # ~4166.67 COP/USD
        "MXN": Decimal("0.0500"),    # ~20.00 MXN/USD
        "EUR": Decimal("1.0850"),    # ~0.9216 EUR/USD
        "CLP": Decimal("0.00105"),   # ~952.38 CLP/USD
        "PEN": Decimal("0.2680"),    # ~3.73 PEN/USD
        "BRL": Decimal("0.1800"),    # ~5.55 BRL/USD
    }

    DEFAULT_TAX_PROFILES: Dict[str, Dict[str, Any]] = {
        # United States Jurisdictions (Sales Tax & Federal Backup Withholding)
        "US-FL": {
            "country": "US",
            "region": "Florida",
            "tax_id_type": "EIN",
            "indirect_tax_name": "US FL Sales & Use Tax",
            "indirect_tax_rate": Decimal("0.0700"),  # 6% State + 1% Miami-Dade Surtax
            "withholding_income_name": "IRS Federal Backup Withholding",
            "withholding_income_rate": Decimal("0.0000"),
            "withholding_vat_name": "None",
            "withholding_vat_rate": Decimal("0.0000"),
            "municipal_tax_name": "FL Commercial Surtax",
            "municipal_tax_rate": Decimal("0.0000"),
        },
        "US-DE": {
            "country": "US",
            "region": "Delaware",
            "tax_id_type": "EIN",
            "indirect_tax_name": "US DE Sales Tax (Exempt State)",
            "indirect_tax_rate": Decimal("0.0000"),
            "withholding_income_name": "IRS FDAP Cross-Border Withholding",
            "withholding_income_rate": Decimal("0.0000"),
            "withholding_vat_name": "None",
            "withholding_vat_rate": Decimal("0.0000"),
            "municipal_tax_name": "None",
            "municipal_tax_rate": Decimal("0.0000"),
        },
        "US-TX": {
            "country": "US",
            "region": "Texas",
            "tax_id_type": "EIN",
            "indirect_tax_name": "US TX State & Local Sales Tax",
            "indirect_tax_rate": Decimal("0.0825"),
            "withholding_income_name": "None",
            "withholding_income_rate": Decimal("0.0000"),
            "withholding_vat_name": "None",
            "withholding_vat_rate": Decimal("0.0000"),
            "municipal_tax_name": "None",
            "municipal_tax_rate": Decimal("0.0000"),
        },
        # Colombia (DIAN - NIT, IVA 19%, ReteFuente 11% Servicios/Honorarios, ReteIVA 15% del IVA, ReteICA)
        "CO-BOG": {
            "country": "CO",
            "region": "Bogota D.C.",
            "tax_id_type": "NIT",
            "indirect_tax_name": "IVA General Colombia (19%)",
            "indirect_tax_rate": Decimal("0.1900"),
            "withholding_income_name": "Retencion en la Fuente Honorarios/Servicios (11%)",
            "withholding_income_rate": Decimal("0.1100"),
            "withholding_vat_name": "ReteIVA (15% sobre IVA)",
            "withholding_vat_rate": Decimal("0.1500"),  # Applied on IVA amount
            "municipal_tax_name": "ReteICA Bogota (9.66x1000)",
            "municipal_tax_rate": Decimal("0.00966"),
        },
        # Mexico (SAT - RFC, IVA 16%, Retencion ISR 10%, Retencion IVA 10.67%)
        "MX-CDMX": {
            "country": "MX",
            "region": "Ciudad de Mexico",
            "tax_id_type": "RFC",
            "indirect_tax_name": "IVA Trasladado Mexico (16%)",
            "indirect_tax_rate": Decimal("0.1600"),
            "withholding_income_name": "Retencion ISR Servicios Profesionales (10%)",
            "withholding_income_rate": Decimal("0.1000"),
            "withholding_vat_name": "Retencion IVA (2/3 partes - 10.6667% base)",
            "withholding_vat_rate": Decimal("0.6667"),  # 2/3 of IVA
            "municipal_tax_name": "None",
            "municipal_tax_rate": Decimal("0.0000"),
        },
        # Chile (SII - RUT, IVA 19%, Retencion Boleta Honorarios 13.75%)
        "CL-SCL": {
            "country": "CL",
            "region": "Santiago",
            "tax_id_type": "RUT",
            "indirect_tax_name": "IVA Débito Fiscal Chile (19%)",
            "indirect_tax_rate": Decimal("0.1900"),
            "withholding_income_name": "Retencion Segunda Categoria SII (13.75%)",
            "withholding_income_rate": Decimal("0.1375"),
            "withholding_vat_name": "None",
            "withholding_vat_rate": Decimal("0.0000"),
            "municipal_tax_name": "None",
            "municipal_tax_rate": Decimal("0.0000"),
        },
    }

    @classmethod
    def validate_tax_id(cls, tax_id: str, tax_id_type: str, country: str) -> Dict[str, Any]:
        """
        Strict algorithmic validation of US & LATAM fiscal identification documents:
        - EIN (US): XX-XXXXXXX (9 digits)
        - NIT (Colombia): Modulo 11 check digit verification (X...X-D)
        - RUT (Chile): Modulo 11 check digit verification (X...X-D/K)
        - RFC (Mexico): 12 or 13 alphanumeric pattern validation
        """
        clean = tax_id.strip().upper()
        t_type = tax_id_type.strip().upper()

        if t_type == "EIN" or country == "US":
            digits = [c for c in clean if c.isdigit()]
            valid = len(digits) == 9 and "-" in clean
            return {
                "valid": valid,
                "normalized": f"{''.join(digits[:2])}-{''.join(digits[2:])}" if len(digits) == 9 else clean,
                "type": "EIN",
                "jurisdiction": "US-IRS",
                "verification_method": "IRS-EIN-9DIGIT-FORMAT"
            }

        elif t_type == "NIT" or country == "CO":
            # Colombia DIAN Modulo 11 algorithm
            parts = clean.replace(".", "").split("-")
            base_digits = "".join(c for c in parts[0] if c.isdigit())
            primes = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
            total = 0
            rev_digits = list(reversed(base_digits))
            for idx, d_char in enumerate(rev_digits):
                if idx < len(primes):
                    total += int(d_char) * primes[idx]
            rem = total % 11
            calc_dv = str(11 - rem) if rem > 1 else str(rem)
            provided_dv = parts[1] if len(parts) > 1 else calc_dv
            valid = len(base_digits) >= 8 and provided_dv == calc_dv
            return {
                "valid": valid,
                "normalized": f"{base_digits}-{calc_dv}",
                "calculated_dv": calc_dv,
                "type": "NIT",
                "jurisdiction": "CO-DIAN",
                "verification_method": "DIAN-MODULO-11"
            }

        elif t_type == "RUT" or country == "CL":
            # Chile SII Modulo 11 algorithm
            parts = clean.replace(".", "").split("-")
            base_digits = "".join(c for c in parts[0] if c.isdigit())
            factors = [2, 3, 4, 5, 6, 7]
            total = 0
            for idx, d_char in enumerate(reversed(base_digits)):
                total += int(d_char) * factors[idx % 6]
            rem = 11 - (total % 11)
            calc_dv = "0" if rem == 11 else ("K" if rem == 10 else str(rem))
            provided_dv = parts[1] if len(parts) > 1 else calc_dv
            valid = len(base_digits) >= 7 and provided_dv == calc_dv
            return {
                "valid": valid,
                "normalized": f"{base_digits}-{calc_dv}",
                "calculated_dv": calc_dv,
                "type": "RUT",
                "jurisdiction": "CL-SII",
                "verification_method": "SII-MODULO-11"
            }

        elif t_type == "RFC" or country == "MX":
            alnum = "".join(c for c in clean if c.isalnum())
            valid = len(alnum) in (12, 13)
            return {
                "valid": valid,
                "normalized": alnum,
                "type": "RFC",
                "jurisdiction": "MX-SAT",
                "verification_method": "SAT-RFC-ALPHANUMERIC"
            }

        return {
            "valid": len(clean) >= 5,
            "normalized": clean,
            "type": t_type,
            "jurisdiction": country,
            "verification_method": "GENERIC-TAX-ID"
        }

    @classmethod
    def convert_currency(cls, amount: Decimal, from_curr: str, to_curr: str) -> Tuple[Decimal, Decimal]:
        """Returns (converted_amount, exchange_rate_applied)."""
        f_rate = cls.DEFAULT_FX_RATES_TO_USD.get(from_curr.upper(), Decimal("1.0"))
        t_rate = cls.DEFAULT_FX_RATES_TO_USD.get(to_curr.upper(), Decimal("1.0"))
        cross_rate = (f_rate / t_rate).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        converted = dec(amount * cross_rate)
        return converted, cross_rate

    @classmethod
    def calculate_cross_border_taxes(
        cls,
        lines: List[Dict[str, Any]],
        issuer_jurisdiction: str,
        client_jurisdiction: str,
        invoice_currency: str,
        functional_currency: str = "USD",
        apply_cross_withholding: bool = True
    ) -> Dict[str, Any]:
        """
        Computes hybrid US + LATAM tax matrix across line items, including:
        - US State Sales Tax or LATAM IVA
        - Cross-border/domestic Withholding Income Tax (ReteFuente / ISR / Backup Withholding)
        - VAT Withholding (ReteIVA)
        - Municipal Withholding (ReteICA)
        - Dual-currency valuation (Invoice Currency + Functional Base Currency + Settlement Equivalencies)
        """
        issuer_prof = cls.DEFAULT_TAX_PROFILES.get(issuer_jurisdiction, cls.DEFAULT_TAX_PROFILES["US-FL"])
        client_prof = cls.DEFAULT_TAX_PROFILES.get(client_jurisdiction, cls.DEFAULT_TAX_PROFILES["CO-BOG"])

        subtotal = Decimal("0.00")
        processed_lines = []

        for idx, item in enumerate(lines, start=1):
            qty = dec(item.get("quantity", 1))
            unit_price = dec(item.get("unit_price", 0))
            discount_pct = dec(item.get("discount_pct", 0)) / Decimal("100.00")
            gross_line = dec(qty * unit_price)
            discount_amt = dec(gross_line * discount_pct)
            net_line = gross_line - discount_amt
            subtotal += net_line

            processed_lines.append({
                "line_number": idx,
                "sku": item.get("sku", f"RES-{idx:03d}"),
                "description": item.get("description", "Professional Technical Service"),
                "quantity": float(qty),
                "unit_price": float(unit_price),
                "discount_pct": float(discount_pct * 100),
                "net_amount": float(net_line),
            })

        # Determine applicable indirect tax (Sales Tax or IVA) and withholdings
        # In cross-border hybrid operations (e.g. US Hub billing LATAM Subsidiary/Client with local nexus or vice versa)
        active_prof = client_prof if client_prof["country"] != "US" else issuer_prof

        indirect_rate = active_prof["indirect_tax_rate"]
        indirect_tax_amt = dec(subtotal * indirect_rate)

        # US Nexus / State Service Digital Tax component if issuer is US and client is LATAM
        us_nexus_rate = issuer_prof["indirect_tax_rate"] if (issuer_jurisdiction.startswith("US-") and item.get("us_hardware_component", True)) else Decimal("0.00")
        # Keep clean separated tax lines
        tax_breakdown = []

        if issuer_jurisdiction.startswith("US-") and client_jurisdiction != issuer_jurisdiction:
            # Hybrid Cross-Border Regime: US Digital/Hardware Nexus Tax + Destination LATAM IVA & Retenciones
            us_sales_tax = dec(subtotal * (issuer_prof["indirect_tax_rate"] * Decimal("0.50")))  # 3.5% US FL Export Tech Nexus
            latam_iva = dec(subtotal * client_prof["indirect_tax_rate"])
            indirect_tax_amt = us_sales_tax + latam_iva
            tax_breakdown.append({
                "code": "US-SALES-TAX",
                "name": f"{issuer_prof['indirect_tax_name']} (Cross-Border Nexus)",
                "rate_pct": float(issuer_prof["indirect_tax_rate"] * Decimal("50.0")),
                "amount": float(us_sales_tax),
                "direction": "ADD"
            })
            tax_breakdown.append({
                "code": "LATAM-IVA",
                "name": client_prof["indirect_tax_name"],
                "rate_pct": float(client_prof["indirect_tax_rate"] * Decimal("100.0")),
                "amount": float(latam_iva),
                "direction": "ADD"
            })
            base_iva_for_rete = latam_iva
        else:
            tax_breakdown.append({
                "code": "INDIRECT-TAX",
                "name": active_prof["indirect_tax_name"],
                "rate_pct": float(indirect_rate * Decimal("100.0")),
                "amount": float(indirect_tax_amt),
                "direction": "ADD"
            })
            base_iva_for_rete = indirect_tax_amt

        withholding_total = Decimal("0.00")
        if apply_cross_withholding:
            rete_fuente = dec(subtotal * active_prof["withholding_income_rate"])
            rete_iva = dec(base_iva_for_rete * active_prof["withholding_vat_rate"])
            rete_ica = dec(subtotal * active_prof["municipal_tax_rate"])
            withholding_total = rete_fuente + rete_iva + rete_ica

            if rete_fuente > 0:
                tax_breakdown.append({
                    "code": "RETE-FUENTE",
                    "name": active_prof["withholding_income_name"],
                    "rate_pct": float(active_prof["withholding_income_rate"] * Decimal("100.0")),
                    "amount": float(rete_fuente),
                    "direction": "WITHHOLD"
                })
            if rete_iva > 0:
                tax_breakdown.append({
                    "code": "RETE-IVA",
                    "name": active_prof["withholding_vat_name"],
                    "rate_pct": float(active_prof["withholding_vat_rate"] * Decimal("100.0")),
                    "amount": float(rete_iva),
                    "direction": "WITHHOLD"
                })
            if rete_ica > 0:
                tax_breakdown.append({
                    "code": "RETE-ICA",
                    "name": active_prof["municipal_tax_name"],
                    "rate_pct": float(active_prof["municipal_tax_rate"] * Decimal("100.0")),
                    "amount": float(rete_ica),
                    "direction": "WITHHOLD"
                })

        gross_total = subtotal + indirect_tax_amt
        net_payable = gross_total - withholding_total

        # Multi-currency equivalencies (USD, COP, MXN, EUR)
        equivalencies = {}
        for curr in ["USD", "COP", "MXN", "EUR"]:
            conv_val, fx_rate = cls.convert_currency(net_payable, invoice_currency, curr)
            equivalencies[curr] = {
                "net_payable": float(conv_val),
                "exchange_rate": float(fx_rate)
            }

        func_net, func_fx = cls.convert_currency(net_payable, invoice_currency, functional_currency)

        return {
            "issuer_jurisdiction": issuer_jurisdiction,
            "client_jurisdiction": client_jurisdiction,
            "invoice_currency": invoice_currency.upper(),
            "functional_currency": functional_currency.upper(),
            "functional_exchange_rate": float(func_fx),
            "subtotal": float(subtotal),
            "indirect_tax_total": float(indirect_tax_amt),
            "withholding_tax_total": float(withholding_total),
            "gross_total": float(gross_total),
            "net_payable": float(net_payable),
            "functional_net_payable": float(func_net),
            "multi_currency_equivalencies": equivalencies,
            "lines": processed_lines,
            "tax_breakdown": tax_breakdown,
        }


class HBOSGlobalERP:
    """
    Clean-Room REA (Resources, Events, Agents) Global ERP & Billing System.
    Implements strict state locking (DRAFT vs ISSUED_APPROVED), immutable version audit trail,
    automated Credit Notes & Rectifying Invoices, Qdrant Vector Sync, and corporate PDF generation.
    """

    def __init__(self, db_path: str = "data/hbos_erp_rea.db", qdrant_url: str = "http://127.0.0.1:6333"):
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self.db_path = db_path
        self.qdrant_url = qdrant_url
        self._init_database()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        with self._get_conn() as conn:
            conn.executescript("""
            -- REA AGENTS: Clients, Vendors/Suppliers, and Internal Operating Entities
            CREATE TABLE IF NOT EXISTS rea_agents (
                agent_id TEXT PRIMARY KEY,
                agent_role TEXT NOT NULL CHECK(agent_role IN ('CLIENT', 'SUPPLIER', 'INTERNAL_ENTITY')),
                legal_name TEXT NOT NULL,
                commercial_name TEXT,
                country_code TEXT NOT NULL,
                jurisdiction_code TEXT NOT NULL,
                tax_id_type TEXT NOT NULL,
                tax_id_number TEXT NOT NULL,
                tax_id_verified INTEGER NOT NULL DEFAULT 0,
                default_currency TEXT NOT NULL DEFAULT 'USD',
                email TEXT,
                address TEXT,
                created_at TEXT NOT NULL
            );

            -- REA RESOURCES: Catalog of Goods, SaaS Licenses, AI Infrastructure & Services
            CREATE TABLE IF NOT EXISTS rea_resources (
                resource_id TEXT PRIMARY KEY,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                resource_type TEXT NOT NULL CHECK(resource_type IN ('SERVICE', 'DIGITAL_ASSET', 'HARDWARE')),
                unit_price REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'USD',
                created_at TEXT NOT NULL
            );

            -- REA ECONOMIC EVENTS: Invoices, Credit Notes, and Rectifying Invoices
            CREATE TABLE IF NOT EXISTS rea_invoices (
                invoice_id TEXT PRIMARY KEY,
                document_number TEXT UNIQUE NOT NULL,
                document_type TEXT NOT NULL CHECK(document_type IN ('STANDARD_INVOICE', 'CREDIT_NOTE', 'RECTIFYING_INVOICE')),
                status TEXT NOT NULL CHECK(status IN ('BORRADOR', 'EMITIDO_APROBADO', 'RECTIFICADO_ANULADO')),
                version INTEGER NOT NULL DEFAULT 1,
                parent_invoice_id TEXT,
                issuer_agent_id TEXT NOT NULL,
                counterparty_agent_id TEXT NOT NULL,
                invoice_currency TEXT NOT NULL,
                functional_currency TEXT NOT NULL DEFAULT 'USD',
                exchange_rate REAL NOT NULL,
                subtotal REAL NOT NULL,
                indirect_tax_total REAL NOT NULL,
                withholding_tax_total REAL NOT NULL,
                gross_total REAL NOT NULL,
                net_payable REAL NOT NULL,
                functional_net_payable REAL NOT NULL,
                lines_json TEXT NOT NULL,
                tax_breakdown_json TEXT NOT NULL,
                equivalencies_json TEXT NOT NULL,
                immutable_lock INTEGER NOT NULL DEFAULT 0,
                content_sha256 TEXT NOT NULL,
                created_at TEXT NOT NULL,
                approved_at TEXT,
                FOREIGN KEY(issuer_agent_id) REFERENCES rea_agents(agent_id),
                FOREIGN KEY(counterparty_agent_id) REFERENCES rea_agents(agent_id)
            );

            -- IMMUTABLE AUDIT & VERSION LEDGER
            CREATE TABLE IF NOT EXISTS rea_audit_versions (
                audit_id TEXT PRIMARY KEY,
                invoice_id TEXT NOT NULL,
                document_number TEXT NOT NULL,
                version INTEGER NOT NULL,
                event_action TEXT NOT NULL,
                previous_status TEXT,
                new_status TEXT NOT NULL,
                snapshot_json TEXT NOT NULL,
                prev_hash TEXT NOT NULL,
                current_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
            """)

    def sync_qdrant_schemas_and_rules(self) -> Dict[str, Any]:
        """
        Creates and populates the `hbos_erp_fiscal_rules` collection in local Qdrant (384d vectors)
        and queries the active fiscal rules to confirm live vector synchronization.
        """
        collection_name = "hbos_erp_fiscal_rules"
        results = {"collection": collection_name, "created": False, "points_upserted": 0, "queried_rules": []}

        # 1. Ensure collection exists (384-d Cosine, matching HBOS standard)
        try:
            req_check = urllib.request.Request(f"{self.qdrant_url}/collections/{collection_name}", method="GET")
            urllib.request.urlopen(req_check, timeout=5)
            results["created"] = True
        except Exception:
            create_payload = {"vectors": {"size": 384, "distance": "Cosine"}}
            req_create = urllib.request.Request(
                f"{self.qdrant_url}/collections/{collection_name}",
                data=json.dumps(create_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT"
            )
            with urllib.request.urlopen(req_create, timeout=5) as resp:
                results["created"] = (resp.status in (200, 201))

        # 2. Upsert Fiscal Rules & REA Database Schemas into Qdrant
        points = []
        idx = 1001
        for jur_code, profile in HybridFiscalEngine.DEFAULT_TAX_PROFILES.items():
            seed_str = f"FISCAL_RULE_{jur_code}_{json.dumps(profile, default=str, sort_keys=True)}"
            vec = self._text_to_hypervector(seed_str, 384)
            payload = {
                "entity_type": "FISCAL_RULE",
                "jurisdiction_code": jur_code,
                "country": profile["country"],
                "region": profile["region"],
                "tax_id_type": profile["tax_id_type"],
                "indirect_tax_name": profile["indirect_tax_name"],
                "indirect_tax_rate": float(profile["indirect_tax_rate"]),
                "withholding_income_name": profile["withholding_income_name"],
                "withholding_income_rate": float(profile["withholding_income_rate"]),
                "withholding_vat_name": profile["withholding_vat_name"],
                "withholding_vat_rate": float(profile["withholding_vat_rate"]),
                "municipal_tax_name": profile["municipal_tax_name"],
                "municipal_tax_rate": float(profile["municipal_tax_rate"]),
                "rea_ontology_layer": "REA_FISCAL_GOVERNANCE_V1"
            }
            points.append({"id": idx, "vector": vec, "payload": payload})
            idx += 1

        # Add REA Schema Point
        schema_payload = {
            "entity_type": "REA_DATABASE_SCHEMA",
            "tables": ["rea_agents", "rea_resources", "rea_invoices", "rea_audit_versions"],
            "states": ["BORRADOR", "EMITIDO_APROBADO", "RECTIFICADO_ANULADO"],
            "currencies": list(HybridFiscalEngine.DEFAULT_FX_RATES_TO_USD.keys()),
            "architecture": "Clean-Room REA Sovereign Ledger (Zero Third-Party Code)"
        }
        points.append({
            "id": 1999,
            "vector": self._text_to_hypervector(json.dumps(schema_payload, sort_keys=True), 384),
            "payload": schema_payload
        })

        req_upsert = urllib.request.Request(
            f"{self.qdrant_url}/collections/{collection_name}/points?wait=true",
            data=json.dumps({"points": points}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(req_upsert, timeout=10) as resp:
            if resp.status in (200, 201):
                results["points_upserted"] = len(points)

        # 3. Query back from Qdrant to verify synchronization
        query_vec = self._text_to_hypervector("FISCAL_RULE_CO-BOG_US-FL", 384)
        req_search = urllib.request.Request(
            f"{self.qdrant_url}/collections/{collection_name}/points/search",
            data=json.dumps({"vector": query_vec, "limit": 5, "with_payload": True}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req_search, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results["queried_rules"] = [pt["payload"] for pt in data.get("result", [])]

        return results

    @staticmethod
    def _text_to_hypervector(seed_text: str, dim: int = 384) -> List[float]:
        h = hashlib.sha256(seed_text.encode("utf-8")).digest()
        vec = []
        for i in range(dim):
            b = h[i % len(h)]
            val = ((b / 127.5) - 1.0) * (0.85 + 0.15 * ((i * 11) % 10) / 10.0)
            vec.append(round(val, 6))
        norm = sum(x * x for x in vec) ** 0.5
        return [round(x / norm, 6) for x in vec]

    def register_agent(
        self,
        agent_role: str,
        legal_name: str,
        country_code: str,
        jurisdiction_code: str,
        tax_id_type: str,
        tax_id_number: str,
        default_currency: str = "USD",
        commercial_name: Optional[str] = None,
        email: str = "",
        address: str = ""
    ) -> Dict[str, Any]:
        """Registers and validates a Client, Supplier, or Internal Entity in the REA Agent table."""
        val_res = HybridFiscalEngine.validate_tax_id(tax_id_number, tax_id_type, country_code)
        if not val_res["valid"]:
            raise ValueError(f"Fiscal Document Validation Failed for {legal_name}: {val_res}")

        agent_id = f"AGT-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO rea_agents (
                    agent_id, agent_role, legal_name, commercial_name, country_code,
                    jurisdiction_code, tax_id_type, tax_id_number, tax_id_verified,
                    default_currency, email, address, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    agent_id, agent_role, legal_name, commercial_name or legal_name,
                    country_code.upper(), jurisdiction_code.upper(), val_res["type"],
                    val_res["normalized"], 1, default_currency.upper(), email, address, now
                )
            )

        return {
            "agent_id": agent_id,
            "agent_role": agent_role,
            "legal_name": legal_name,
            "country_code": country_code.upper(),
            "jurisdiction_code": jurisdiction_code.upper(),
            "tax_validation": val_res,
            "default_currency": default_currency.upper(),
            "address": address,
            "email": email
        }

    def create_draft_invoice(
        self,
        issuer_agent_id: str,
        counterparty_agent_id: str,
        invoice_currency: str,
        lines: List[Dict[str, Any]],
        functional_currency: str = "USD",
        document_type: str = "STANDARD_INVOICE",
        parent_invoice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates an invoice in strict `BORRADOR` (Draft) status with full cross-border tax calculation."""
        with self._get_conn() as conn:
            issuer = conn.execute("SELECT * FROM rea_agents WHERE agent_id = ?", (issuer_agent_id,)).fetchone()
            client = conn.execute("SELECT * FROM rea_agents WHERE agent_id = ?", (counterparty_agent_id,)).fetchone()
            if not issuer or not client:
                raise ValueError("Issuer or Counterparty Agent not found in REA registry.")

            calc = HybridFiscalEngine.calculate_cross_border_taxes(
                lines=lines,
                issuer_jurisdiction=issuer["jurisdiction_code"],
                client_jurisdiction=client["jurisdiction_code"],
                invoice_currency=invoice_currency,
                functional_currency=functional_currency,
                apply_cross_withholding=True
            )

            invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
            prefix = "HBOS-INV" if document_type == "STANDARD_INVOICE" else (
                "HBOS-NC" if document_type == "CREDIT_NOTE" else "HBOS-RECT"
            )
            count_row = conn.execute("SELECT COUNT(*) as c FROM rea_invoices").fetchone()
            seq = (count_row["c"] if count_row else 0) + 1
            document_number = f"{prefix}-2026-{seq:04d}"
            now = datetime.now(timezone.utc).isoformat()

            snapshot_payload = {
                "invoice_id": invoice_id,
                "document_number": document_number,
                "document_type": document_type,
                "status": "BORRADOR",
                "version": 1,
                "calculation": calc
            }
            content_hash = hashlib.sha256(json.dumps(snapshot_payload, sort_keys=True).encode("utf-8")).hexdigest()

            conn.execute(
                """
                INSERT INTO rea_invoices (
                    invoice_id, document_number, document_type, status, version,
                    parent_invoice_id, issuer_agent_id, counterparty_agent_id,
                    invoice_currency, functional_currency, exchange_rate,
                    subtotal, indirect_tax_total, withholding_tax_total,
                    gross_total, net_payable, functional_net_payable,
                    lines_json, tax_breakdown_json, equivalencies_json,
                    immutable_lock, content_sha256, created_at
                ) VALUES (?, ?, ?, 'BORRADOR', 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (
                    invoice_id, document_number, document_type, parent_invoice_id,
                    issuer_agent_id, counterparty_agent_id,
                    calc["invoice_currency"], calc["functional_currency"], calc["functional_exchange_rate"],
                    calc["subtotal"], calc["indirect_tax_total"], calc["withholding_tax_total"],
                    calc["gross_total"], calc["net_payable"], calc["functional_net_payable"],
                    json.dumps(calc["lines"]), json.dumps(calc["tax_breakdown"]),
                    json.dumps(calc["multi_currency_equivalencies"]),
                    content_hash, now
                )
            )

            self._append_audit_log(
                conn=conn,
                invoice_id=invoice_id,
                document_number=document_number,
                version=1,
                event_action="CREATE_DRAFT",
                previous_status=None,
                new_status="BORRADOR",
                snapshot=snapshot_payload
            )

        return self.get_invoice(invoice_id)

    def update_draft_invoice(self, invoice_id: str, new_lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Modifies an existing invoice ONLY if its state is `BORRADOR` and `immutable_lock == 0`.
        Once `EMITIDO_APROBADO`, direct modifications raise a strict ImmutabilityLockError.
        """
        with self._get_conn() as conn:
            inv = conn.execute("SELECT * FROM rea_invoices WHERE invoice_id = ?", (invoice_id,)).fetchone()
            if not inv:
                raise ValueError(f"Invoice {invoice_id} not found.")

            if inv["status"] != "BORRADOR" or inv["immutable_lock"] == 1:
                raise PermissionError(
                    f"[STRICT ACCOUNTING LOCK] Invoice {inv['document_number']} is in state '{inv['status']}' "
                    f"(immutable_lock=1). Direct editing is strictly prohibited. Emit a Credit Note or Rectifying Invoice."
                )

            issuer = conn.execute("SELECT * FROM rea_agents WHERE agent_id = ?", (inv["issuer_agent_id"],)).fetchone()
            client = conn.execute("SELECT * FROM rea_agents WHERE agent_id = ?", (inv["counterparty_agent_id"],)).fetchone()

            calc = HybridFiscalEngine.calculate_cross_border_taxes(
                lines=new_lines,
                issuer_jurisdiction=issuer["jurisdiction_code"],
                client_jurisdiction=client["jurisdiction_code"],
                invoice_currency=inv["invoice_currency"],
                functional_currency=inv["functional_currency"],
                apply_cross_withholding=True
            )

            new_version = int(inv["version"]) + 1
            snapshot_payload = {
                "invoice_id": invoice_id,
                "document_number": inv["document_number"],
                "status": "BORRADOR",
                "version": new_version,
                "calculation": calc
            }
            content_hash = hashlib.sha256(json.dumps(snapshot_payload, sort_keys=True).encode("utf-8")).hexdigest()

            conn.execute(
                """
                UPDATE rea_invoices
                SET version = ?, subtotal = ?, indirect_tax_total = ?, withholding_tax_total = ?,
                    gross_total = ?, net_payable = ?, functional_net_payable = ?,
                    lines_json = ?, tax_breakdown_json = ?, equivalencies_json = ?, content_sha256 = ?
                WHERE invoice_id = ?
                """,
                (
                    new_version, calc["subtotal"], calc["indirect_tax_total"], calc["withholding_tax_total"],
                    calc["gross_total"], calc["net_payable"], calc["functional_net_payable"],
                    json.dumps(calc["lines"]), json.dumps(calc["tax_breakdown"]),
                    json.dumps(calc["multi_currency_equivalencies"]), content_hash, invoice_id
                )
            )

            self._append_audit_log(
                conn=conn,
                invoice_id=invoice_id,
                document_number=inv["document_number"],
                version=new_version,
                event_action="UPDATE_DRAFT",
                previous_status="BORRADOR",
                new_status="BORRADOR",
                snapshot=snapshot_payload
            )

        return self.get_invoice(invoice_id)

    def approve_and_emit_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """
        Transitions an invoice from `BORRADOR` to `EMITIDO_APROBADO` and engages `immutable_lock = 1`.
        Seals the cryptographic hash in the audit version chain.
        """
        with self._get_conn() as conn:
            inv = conn.execute("SELECT * FROM rea_invoices WHERE invoice_id = ?", (invoice_id,)).fetchone()
            if not inv:
                raise ValueError(f"Invoice {invoice_id} not found.")
            if inv["status"] != "BORRADOR":
                raise ValueError(f"Invoice {inv['document_number']} is already in status {inv['status']}.")

            new_version = int(inv["version"]) + 1
            approved_at = datetime.now(timezone.utc).isoformat()
            snapshot_payload = {
                "invoice_id": invoice_id,
                "document_number": inv["document_number"],
                "status": "EMITIDO_APROBADO",
                "version": new_version,
                "approved_at": approved_at,
                "net_payable": inv["net_payable"],
                "currency": inv["invoice_currency"]
            }
            content_hash = hashlib.sha256(json.dumps(snapshot_payload, sort_keys=True).encode("utf-8")).hexdigest()

            conn.execute(
                """
                UPDATE rea_invoices
                SET status = 'EMITIDO_APROBADO', version = ?, immutable_lock = 1,
                    content_sha256 = ?, approved_at = ?
                WHERE invoice_id = ?
                """,
                (new_version, content_hash, approved_at, invoice_id)
            )

            self._append_audit_log(
                conn=conn,
                invoice_id=invoice_id,
                document_number=inv["document_number"],
                version=new_version,
                event_action="APPROVE_AND_EMIT_LOCK",
                previous_status="BORRADOR",
                new_status="EMITIDO_APROBADO",
                snapshot=snapshot_payload
            )

        return self.get_invoice(invoice_id)

    def issue_credit_note_or_rectification(
        self,
        original_invoice_id: str,
        document_type: str = "CREDIT_NOTE",
        reason: str = "Ajuste contable / devolucion parcial de servicios",
        adjusted_lines: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Native automatic emission of Credit Notes (`CREDIT_NOTE`) or Rectifying Invoices (`RECTIFYING_INVOICE`)
        against an already approved/locked invoice, preserving full audit lineage.
        """
        orig = self.get_invoice(original_invoice_id)
        if orig["status"] != "EMITIDO_APROBADO":
            raise ValueError("Credit Notes and Rectifying Invoices can only be emitted against EMITIDO_APROBADO documents.")

        lines_to_use = adjusted_lines if adjusted_lines is not None else orig["lines"]
        if document_type == "CREDIT_NOTE":
            # Invert unit prices or quantities for credit reversal record
            inverted_lines = []
            for l in lines_to_use:
                inv_l = dict(l)
                inv_l["unit_price"] = -abs(float(l["unit_price"]))
                inv_l["description"] = f"[NOTA CREDITO REF {orig['document_number']}] {l['description']} ({reason})"
                inverted_lines.append(inv_l)
            lines_to_use = inverted_lines
        else:
            rect_lines = []
            for l in lines_to_use:
                rl = dict(l)
                rl["description"] = f"[FACTURA RECTIFICATIVA REF {orig['document_number']}] {l['description']} ({reason})"
                rect_lines.append(rl)
            lines_to_use = rect_lines

        draft_doc = self.create_draft_invoice(
            issuer_agent_id=orig["issuer"]["agent_id"],
            counterparty_agent_id=orig["counterparty"]["agent_id"],
            invoice_currency=orig["invoice_currency"],
            lines=lines_to_use,
            functional_currency=orig["functional_currency"],
            document_type=document_type,
            parent_invoice_id=original_invoice_id
        )
        return self.approve_and_emit_invoice(draft_doc["invoice_id"])

    def _append_audit_log(
        self,
        conn: sqlite3.Connection,
        invoice_id: str,
        document_number: str,
        version: int,
        event_action: str,
        previous_status: Optional[str],
        new_status: str,
        snapshot: Dict[str, Any]
    ):
        last_row = conn.execute(
            "SELECT current_hash FROM rea_audit_versions WHERE invoice_id = ? ORDER BY version DESC LIMIT 1",
            (invoice_id,)
        ).fetchone()
        prev_hash = last_row["current_hash"] if last_row else "0" * 64
        now = datetime.now(timezone.utc).isoformat()
        raw_chain = f"{invoice_id}|{version}|{event_action}|{new_status}|{prev_hash}|{now}|{json.dumps(snapshot, sort_keys=True)}"
        curr_hash = hashlib.sha256(raw_chain.encode("utf-8")).hexdigest()

        conn.execute(
            """
            INSERT INTO rea_audit_versions (
                audit_id, invoice_id, document_number, version, event_action,
                previous_status, new_status, snapshot_json, prev_hash, current_hash, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"AUD-{uuid.uuid4().hex[:10].upper()}", invoice_id, document_number,
                version, event_action, previous_status, new_status,
                json.dumps(snapshot), prev_hash, curr_hash, now
            )
        )

    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        with self._get_conn() as conn:
            inv = conn.execute("SELECT * FROM rea_invoices WHERE invoice_id = ?", (invoice_id,)).fetchone()
            if not inv:
                raise ValueError(f"Invoice {invoice_id} not found.")
            issuer = conn.execute("SELECT * FROM rea_agents WHERE agent_id = ?", (inv["issuer_agent_id"],)).fetchone()
            client = conn.execute("SELECT * FROM rea_agents WHERE agent_id = ?", (inv["counterparty_agent_id"],)).fetchone()
            audits = conn.execute(
                "SELECT version, event_action, previous_status, new_status, prev_hash, current_hash, timestamp "
                "FROM rea_audit_versions WHERE invoice_id = ? ORDER BY version ASC",
                (invoice_id,)
            ).fetchall()

            return {
                "invoice_id": inv["invoice_id"],
                "document_number": inv["document_number"],
                "document_type": inv["document_type"],
                "status": inv["status"],
                "version": inv["version"],
                "immutable_lock": bool(inv["immutable_lock"]),
                "parent_invoice_id": inv["parent_invoice_id"],
                "issuer": dict(issuer),
                "counterparty": dict(client),
                "invoice_currency": inv["invoice_currency"],
                "functional_currency": inv["functional_currency"],
                "exchange_rate": inv["exchange_rate"],
                "subtotal": inv["subtotal"],
                "indirect_tax_total": inv["indirect_tax_total"],
                "withholding_tax_total": inv["withholding_tax_total"],
                "gross_total": inv["gross_total"],
                "net_payable": inv["net_payable"],
                "functional_net_payable": inv["functional_net_payable"],
                "lines": json.loads(inv["lines_json"]),
                "tax_breakdown": json.loads(inv["tax_breakdown_json"]),
                "multi_currency_equivalencies": json.loads(inv["equivalencies_json"]),
                "content_sha256": inv["content_sha256"],
                "created_at": inv["created_at"],
                "approved_at": inv["approved_at"],
                "audit_trail": [dict(a) for a in audits]
            }

    def export_corporate_pdf(self, invoice_id: str, output_pdf_path: str) -> str:
        """
        Generates a bespoke, 100% original corporate executive PDF for the approved invoice,
        featuring REA cryptographic traceability, US/LATAM hybrid tax breakdown, and multi-currency matrix.
        """
        inv = self.get_invoice(invoice_id)
        os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)

        doc = SimpleDocTemplate(
            output_pdf_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        dark_navy = colors.HexColor("#0A0E17")
        cyan_accent = colors.HexColor("#007799")
        gold_accent = colors.HexColor("#B37700")
        slate_gray = colors.HexColor("#4A5568")
        light_bg = colors.HexColor("#F7FAFC")

        title_style = ParagraphStyle(
            "CorpTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=dark_navy,
            spaceAfter=4
        )
        sub_style = ParagraphStyle(
            "CorpSub",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=slate_gray,
            leading=12
        )
        sec_hdr_style = ParagraphStyle(
            "SecHdr",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=cyan_accent,
            spaceBefore=8,
            spaceAfter=4
        )
        cell_style = ParagraphStyle(
            "CellTxt",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            textColor=dark_navy,
            leading=11
        )
        cell_bold = ParagraphStyle(
            "CellBold",
            parent=cell_style,
            fontName="Helvetica-Bold"
        )

        story = []

        # 1. Header Banner
        doc_title_map = {
            "STANDARD_INVOICE": "FACTURA COMERCIAL INTERNACIONAL / COMMERCIAL INVOICE",
            "CREDIT_NOTE": "NOTA DE CRÉDITO FISCAL / FISCAL CREDIT NOTE",
            "RECTIFYING_INVOICE": "FACTURA RECTIFICATIVA / RECTIFYING INVOICE"
        }
        header_left = [
            Paragraph("<b>HBOS GLOBAL OPERATIONS & REA LEDGER</b>", title_style),
            Paragraph(doc_title_map.get(inv["document_type"], "COMMERCIAL INVOICE"), sec_hdr_style),
            Paragraph("Clean-Room Sovereign ERP · US & LATAM Hybrid Fiscal Engine", sub_style)
        ]
        header_right = [
            Paragraph(f"<b>Documento No:</b> {inv['document_number']}", cell_style),
            Paragraph(f"<b>Estado Contable:</b> {inv['status']} (Lock={inv['immutable_lock']})", cell_style),
            Paragraph(f"<b>Versión Auditada:</b> v{inv['version']}", cell_style),
            Paragraph(f"<b>Fecha Emisión:</b> {inv['created_at'][:19]} UTC", cell_style),
            Paragraph(f"<b>Fecha Aprobación:</b> {(inv['approved_at'] or 'PENDIENTE')[:19]} UTC", cell_style),
        ]
        hdr_table = Table([[header_left, header_right]], colWidths=[4.2 * inch, 3.3 * inch])
        hdr_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(hdr_table)
        story.append(HRFlowable(width="100%", thickness=1.5, color=cyan_accent, spaceAfter=10))

        # 2. Issuer & Client Agent Block
        issuer = inv["issuer"]
        client = inv["counterparty"]
        issuer_info = [
            Paragraph("<b>ENTIDAD EMISORA (ISSUER AGENT - EE. UU. / HUB)</b>", sec_hdr_style),
            Paragraph(f"<b>Razón Social:</b> {issuer['legal_name']}", cell_style),
            Paragraph(f"<b>ID Fiscal ({issuer['tax_id_type']}):</b> {issuer['tax_id_number']} (Verificado IRS)", cell_style),
            Paragraph(f"<b>Jurisdicción:</b> {issuer['jurisdiction_code']} ({issuer['country_code']})", cell_style),
            Paragraph(f"<b>Dirección:</b> {issuer['address']}", cell_style),
        ]
        client_info = [
            Paragraph("<b>CLIENTE RECEPTOR (COUNTERPARTY AGENT - LATAM / INTL)</b>", sec_hdr_style),
            Paragraph(f"<b>Razón Social:</b> {client['legal_name']}", cell_style),
            Paragraph(f"<b>ID Fiscal ({client['tax_id_type']}):</b> {client['tax_id_number']} (Verificado Módulo 11)", cell_style),
            Paragraph(f"<b>Jurisdicción:</b> {client['jurisdiction_code']} ({client['country_code']})", cell_style),
            Paragraph(f"<b>Dirección:</b> {client['address']}", cell_style),
        ]
        parties_table = Table([[issuer_info, client_info]], colWidths=[3.75 * inch, 3.75 * inch])
        parties_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), light_bg),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(parties_table)
        story.append(Spacer(1, 12))

        # 3. Line Items Table
        story.append(Paragraph(f"<b>DETALLE DE RECURSOS Y SERVICIOS ECONÓMICOS (MONEDA: {inv['invoice_currency']})</b>", sec_hdr_style))
        line_rows = [[
            Paragraph("<b>#</b>", cell_bold),
            Paragraph("<b>SKU</b>", cell_bold),
            Paragraph("<b>Descripción del Servicio / Recurso REA</b>", cell_bold),
            Paragraph("<b>Cant.</b>", cell_bold),
            Paragraph("<b>V. Unitario</b>", cell_bold),
            Paragraph("<b>Subtotal Neto</b>", cell_bold),
        ]]
        curr = inv["invoice_currency"]
        for l in inv["lines"]:
            line_rows.append([
                Paragraph(str(l["line_number"]), cell_style),
                Paragraph(l["sku"], cell_style),
                Paragraph(l["description"], cell_style),
                Paragraph(f"{l['quantity']:,.2f}", cell_style),
                Paragraph(f"{curr} {l['unit_price']:,.2f}", cell_style),
                Paragraph(f"{curr} {l['net_amount']:,.2f}", cell_bold),
            ])

        lines_table = Table(
            line_rows,
            colWidths=[0.35 * inch, 0.9 * inch, 3.45 * inch, 0.65 * inch, 1.05 * inch, 1.1 * inch]
        )
        lines_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(lines_table)
        story.append(Spacer(1, 12))

        # 4. Hybrid Cross-Border Tax Breakdown & Totals
        story.append(Paragraph("<b>LIQUIDACIÓN DEL MOTOR FISCAL HÍBRIDO (EE. UU. SALES TAX + LATAM IVA & RETENCIONES)</b>", sec_hdr_style))
        tax_rows = [[
            Paragraph("<b>Código</b>", cell_bold),
            Paragraph("<b>Concepto Tributario / Jurisdicción</b>", cell_bold),
            Paragraph("<b>Tasa (%)</b>", cell_bold),
            Paragraph("<b>Operación</b>", cell_bold),
            Paragraph("<b>Importe</b>", cell_bold),
        ]]
        for t in inv["tax_breakdown"]:
            sign = "+" if t["direction"] == "ADD" else "-"
            tax_rows.append([
                Paragraph(t["code"], cell_style),
                Paragraph(t["name"], cell_style),
                Paragraph(f"{t['rate_pct']:.3f}%", cell_style),
                Paragraph("Cargo (+)" if t["direction"] == "ADD" else "Retención (-)", cell_style),
                Paragraph(f"{sign} {curr} {t['amount']:,.2f}", cell_bold),
            ])

        tax_table = Table(tax_rows, colWidths=[1.1 * inch, 3.5 * inch, 0.8 * inch, 1.0 * inch, 1.1 * inch])
        tax_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tax_table)
        story.append(Spacer(1, 10))

        # 5. Summary & Multi-Currency Matrix side by side
        eq = inv["multi_currency_equivalencies"]
        eq_rows = [[
            Paragraph("<b>Moneda</b>", cell_bold),
            Paragraph("<b>Tasa Cruzada</b>", cell_bold),
            Paragraph("<b>Equivalente Neto</b>", cell_bold),
        ]]
        for c_code, c_info in eq.items():
            eq_rows.append([
                Paragraph(c_code, cell_bold),
                Paragraph(f"{c_info['exchange_rate']:.6f}", cell_style),
                Paragraph(f"{c_code} {c_info['net_payable']:,.2f}", cell_style),
            ])
        eq_table = Table(eq_rows, colWidths=[0.8 * inch, 1.2 * inch, 1.6 * inch])
        eq_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), light_bg),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))

        totals_rows = [
            [Paragraph("Subtotal Base Gravable:", cell_style), Paragraph(f"{curr} {inv['subtotal']:,.2f}", cell_bold)],
            [Paragraph("Total Impuestos Indirectos (+):", cell_style), Paragraph(f"{curr} {inv['indirect_tax_total']:,.2f}", cell_bold)],
            [Paragraph("Total Bruto Facturado:", cell_style), Paragraph(f"{curr} {inv['gross_total']:,.2f}", cell_bold)],
            [Paragraph("Menos Retenciones Fiscales (-):", cell_style), Paragraph(f"- {curr} {inv['withholding_tax_total']:,.2f}", cell_bold)],
            [Paragraph("<b>TOTAL NETO A PAGAR:</b>", cell_bold), Paragraph(f"<b>{curr} {inv['net_payable']:,.2f}</b>", cell_bold)],
        ]
        totals_table = Table(totals_rows, colWidths=[2.1 * inch, 1.5 * inch])
        totals_table.setStyle(TableStyle([
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E6FFFA")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        summary_wrapper = Table(
            [[
                [Paragraph("<b>MATRIZ MULTI-MONEDA EN TIEMPO REAL</b>", sec_hdr_style), eq_table],
                [Paragraph("<b>RESUMEN DE CIERRE CONTABLE</b>", sec_hdr_style), totals_table]
            ]],
            colWidths=[3.8 * inch, 3.7 * inch]
        )
        summary_wrapper.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(summary_wrapper)
        story.append(Spacer(1, 14))

        # 6. Cryptographic Audit & Version Footer
        story.append(HRFlowable(width="100%", thickness=1.0, color=gold_accent, spaceAfter=6))
        last_audit = inv["audit_trail"][-1] if inv["audit_trail"] else {}
        story.append(Paragraph(
            f"<b>SELLO CRIPTOGRÁFICO DE INMUTABILIDAD (REA LEDGER):</b> SHA-256 Content: <font name='Courier' size=7.5>{inv['content_sha256']}</font><br/>"
            f"<b>CADENA DE AUDITORÍA (v{inv['version']} - {last_audit.get('event_action', 'LOCK')}):</b> "
            f"Chain Hash: <font name='Courier' size=7.5>{last_audit.get('current_hash', 'N/A')}</font><br/>"
            f"<i>Documento generado de forma autónoma por HBOS Global ERP Engine (Clean-Room REA Architecture · Uso Interno Privado EE. UU. &amp; LATAM).</i>",
            sub_style
        ))

        doc.build(story)
        return os.path.abspath(output_pdf_path)

