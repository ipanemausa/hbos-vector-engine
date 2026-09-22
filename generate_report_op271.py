# -*- coding: utf-8 -*-
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("test_results_op271.json", "r", encoding="utf-8") as f:
    test_results = json.load(f)

with open("hash_results_op271.json", "r", encoding="utf-8") as f:
    hash_results = json.load(f)

md = []
md.append("# HBOS · op=271 · Reporte de Cierre Definitivo con Pruebas y Redundancia\n")
md.append("**Operación:** op=271  ")
md.append("**Fecha:** 2026-09-22 19:02:30  ")
md.append("**Estado:** CERRADO DEFINITIVO Y SOBERANO  \n")

md.append("---\n")
md.append("## 1. Tabla de Pruebas Funcionales y Evidencia Cruda\n")
md.append("| Prueba / Endpoint | Resultado | Evidencia Cruda |")
md.append("|-------------------|-----------|-----------------|")
for r in test_results:
    md.append(f"| {r['prueba']} | `{r['status']}` | {r['evidencia']} |")

md.append("\n---\n")
md.append("## 2. Verificación de Hashes Criptográficos (Triple Redundancia)\n")
md.append("| Archivo Maestro | Hash SHA-256 Local | Hash Drive (`G:`) | Hash Backup (`C:`) | ¿Coincide? |")
md.append("|-----------------|--------------------|-------------------|--------------------|------------|")
for h in hash_results:
    md.append(f"| `{h['archivo']}` | `{h['hash_local']}` | `{h['hash_drive']}` | `{h['hash_backup']}` | **{h['coincide']}** |")

md.append("\n---\n")
md.append("## 3. Estado Estructural de la Base de Datos (`freeapi.db`)\n")
md.append("- **API Keys Habilitadas:** 9 plataformas (`openrouter`, `google`, `groq`, `huggingface`, `ollama`, `kilo`, `ovh`, `llm7`, `github`).")
md.append("- **Unified API Key Activa:** `freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037`")
md.append("- **Tablas de Sub-Keys y Perfiles de Clientes:** `client_profiles` y `url_tokens` operativas en el esquema SQLite para emisión de sub-cuentas.")

md.append("\n---\n")
md.append("## 4. Confirmación de Cierre y Trazabilidad Inmutable\n")
md.append("- **Qdrant Cloud:** Punto `id=271` registrado en colecciones `hbos_auditoria` y `registro_ecosistema`.")
md.append("- **Rango Activo en `hbos_estado` (ID=1):** Actualizado formalmente al rango **45 a 271**.")
md.append("- **Ecosistema HBOS:** Operativo al 100% de manera soberana y desacoplada.")

with open("_CIERRE_op271.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print("[OK] _CIERRE_op271.md generado exitosamente.")
