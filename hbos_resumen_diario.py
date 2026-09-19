"""
hbos_resumen_diario.py — GENERADOR AUTOMÁTICO DE RESÚMENES DIARIOS DE MEMORIA
Ecosistema: HBOS-Diamantino · Vector Engine
Trazabilidad: operation_id = 163 | Directiva Canónica ALEJAVI
"""

import os
import sys
import time
import shutil
import hashlib
import json
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

local_maestro = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO"
drive_maestro = r"G:\My Drive\HBOS-Diamantino\_MAESTRO"
backup_maestro = r"C:\Users\ipane\backup_hbos\_MAESTRO"

os.makedirs(local_maestro, exist_ok=True)
os.makedirs(drive_maestro, exist_ok=True)
os.makedirs(backup_maestro, exist_ok=True)

def generar_resumenes_diarios():
    t0 = time.time()
    print("==========================================================================")
    print(">>> [HBOS MEMORY] GENERADOR AUTOMÁTICO DE RESÚMENES DIARIOS (op 163) <<<")
    print("==========================================================================")
    
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_key = os.getenv("QDRANT_API_KEY")
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=20)
    
    # 1. Consultar hbos_estado en Qdrant con reintento ante micro-cortes DNS
    print("[*] Consultando estado consolidado en Qdrant Cloud (hbos_estado ID=1)...")
    punto = None
    for attempt in range(1, 4):
        try:
            punto = client.retrieve(collection_name="hbos_estado", ids=[1])
            if punto:
                break
        except Exception as err:
            print(f"[!] Intento {attempt}/3 falló por resolución de red ({err}). Reintentando en 2s...")
            time.sleep(2)
            
    if not punto:
        print("[!] Error: No se pudo recuperar el registro de estado en hbos_estado tras 3 intentos.")
        sys.exit(1)
        
    p = punto[0].payload
    fecha = p.get("fecha", datetime.datetime.now().strftime("%Y-%m-%d"))
    estado_gen = p.get("estado_general", "OPERATIVO")
    
    # 2. Construir _ESTADO_DIA.md
    md_estado = f"""# REPORTE OFICIAL DE ESTADO DEL DÍA — HBOS-DIAMANTINO
**Fecha:** {fecha}  
**Estado General:** {estado_gen}  
**Trazabilidad Canónica:** Operation IDs {p.get('operation_ids')}  
**Gobernanza:** {p.get('patrones_activos')} · {p.get('lecciones_activas')}  

---

## 1. ESTADO DE EPISODIOS
"""
    for ep, desc in p.get("episodios", {}).items():
        md_estado += f"- **{ep.upper()}:** {desc}\n"

    md_estado += "\n## 2. SALUD DE CUOTAS Y SERVICIOS EN NUBE\n"
    for prov, stat in p.get("cuotas", {}).items():
        md_estado += f"- **{prov.upper()}:** {stat}\n"

    md_estado += "\n## 3. CATÁLOGO DE AGENTES ACTIVOS\n"
    for ag in p.get("agentes_activos", []):
        md_estado += f"- {ag}\n"

    md_estado += "\n## 4. HITOS COMPLETADOS HOY\n"
    for idx, h in enumerate(p.get("hecho_hoy", []), 1):
        md_estado += f"{idx:02d}. {h}\n"

    md_estado += "\n## 5. PENDIENTES PRIORITARIOS\n"
    for idx, pend in enumerate(p.get("pendientes", []), 1):
        md_estado += f"[{idx}] {pend}\n"

    # 3. Construir _PENDIENTES.md
    md_pendientes = f"""# REGISTRO DE PENDIENTES PRIORITARIOS — HBOS-DIAMANTINO
**Fecha:** {fecha} | **Estado:** ABIERTO / PRIORIZADO  
**Directiva:** DAG + RAG + R768 | Cero improvisación  

---

## LISTA DE ACCIONES PENDIENTES
"""
    for idx, pend in enumerate(p.get("pendientes", []), 1):
        md_pendientes += f"""### [{idx}] {pend}
- **Criticidad:** Alta
- **Ecosistema:** HBOS-Diamantino
- **Próximo Paso:** Despacho cuando se renueve cuota o por conmutación a proveedor alternativo (FreeLLMAPI / CosyVoice2).

"""

    # 4. Construir _HECHO.md
    md_hecho = f"""# REGISTRO DE HITOS COMPLETADOS HOY — HBOS-DIAMANTINO
**Fecha:** {fecha} | **Trazabilidad:** Operation IDs {p.get('operation_ids')}  
**Auditoría:** Triple Redundancia P-03 + Inmutabilidad Qdrant Cloud  

---

## LOG DE HITOS Y ENTREGABLES VERIFICADOS
"""
    for idx, h in enumerate(p.get("hecho_hoy", []), 1):
        md_hecho += f"- **[{idx:02d}]** {h}\n"

    archivos = {
        "_ESTADO_DIA.md": md_estado,
        "_PENDIENTES.md": md_pendientes,
        "_HECHO.md": md_hecho
    }

    # 5. Escribir y sincronizar en Local, Drive y Backup
    resultados = {}
    print("[*] Escribiendo y sincronizando los 3 archivos en triple redundancia...")
    for fname, content in archivos.items():
        loc_path = os.path.join(local_maestro, fname)
        drv_path = os.path.join(drive_maestro, fname)
        bck_path = os.path.join(backup_maestro, fname)
        
        with open(loc_path, "w", encoding="utf-8") as f:
            f.write(content)
        shutil.copy2(loc_path, drv_path)
        shutil.copy2(loc_path, bck_path)
        
        # Verificar hash y bytes
        def get_h(p):
            with open(p, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest(), os.path.getsize(p)
                
        hl, sl = get_h(loc_path)
        hd, sd = get_h(drv_path)
        hb, sb = get_h(bck_path)
        assert hl == hd == hb, f"Error de redundancia en {fname}"
        
        resultados[fname] = {
            "ruta_local": loc_path,
            "ruta_drive": drv_path,
            "ruta_backup": bck_path,
            "bytes": sl,
            "sha256": hl
        }
        print(f"[OK] {fname}: {sl} bytes | SHA256: {hl[:16]}... (Triple redundancia verificada)")

    # 6. Vectorización en Qdrant (operation_id = 163)
    def generate_embedding(text, dim=384):
        import math
        vec = [0.0] * dim
        for i, word in enumerate(text.split()):
            h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 1.0 / (1.0 + (h % 10))
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        else:
            vec = [1.0 / math.sqrt(dim)] * dim
        return vec

    payload_op163 = {
        "operation_id": 163,
        "tarea": "TAREA 2 — CREAR RESUMEN DIARIO AUTOMÁTICO",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "archivos_generados": list(archivos.keys()),
        "detalles_archivos": resultados,
        "estado": "COMPLETADO"
    }

    vec_163 = generate_embedding("Tarea 2 operacion 163 Crear Resumen Diario Automatico ESTADO_DIA PENDIENTES HECHO", dim=384)
    client.upsert(
        collection_name="registro_ecosistema",
        points=[models.PointStruct(id=163, vector=vec_163, payload=payload_op163)]
    )
    print("[OK] operation_id = 163 registrado exitosamente en registro_ecosistema.")

    t_total = round(time.time() - t0, 3)
    print(f"[OK] Resumen diario completado en {t_total} seg.")
    return resultados, t_total

if __name__ == "__main__":
    generar_resumenes_diarios()
