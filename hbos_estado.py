"""
hbos_estado.py — CONSULTA INSTANTÁNEA DE HBOS MEMORY (ESTADO SOBERANO)
Ecosistema: HBOS-Diamantino · Vector Engine
Trazabilidad: operation_id = 161 | Directiva Canónica ALEJAVI
"""

import os
import sys
import time
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

def consultar_estado_hbos():
    t0 = time.time()
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_key = os.getenv("QDRANT_API_KEY")
    
    if not qdrant_url or not qdrant_key:
        print("[!] ERROR: Credenciales de Qdrant no encontradas en .env.local")
        sys.exit(1)
        
    client = None
    punto = None
    last_err = None
    for attempt in range(3):
        try:
            client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=15)
            punto = client.retrieve(collection_name="hbos_estado", ids=[1])
            if punto:
                break
        except Exception as e:
            last_err = e
            time.sleep(0.8)
    
    if not punto:
        if last_err:
            print(f"[!] Error al consultar Qdrant Cloud: {last_err}")
        else:
            print("[!] No se encontró el registro de estado en 'hbos_estado'.")
        sys.exit(1)

    p = punto[0].payload
    t_query = round(time.time() - t0, 3)

    print("=" * 70)
    print("   >>> HBOS-DIAMANTINO MEMORY — REPORTE DE ESTADO DEL SISTEMA <<<")
    print("=" * 70)
    print(f"[*] Fecha: {p.get('fecha')} | Estado General: {p.get('estado_general')}")
    print(f"[*] Tiempo de respuesta Qdrant Cloud: {t_query} seg\n")
    
    print("--- [1. EPISODIOS ACTIVOS] ---")
    for ep, desc in p.get("episodios", {}).items():
        print(f"  • {ep.upper()}: {desc}")
        
    print("\n--- [2. GOBERNANZA TÉCNICA] ---")
    print(f"  • Patrones Activos:  {p.get('patrones_activos')}")
    print(f"  • Lecciones Activas: {p.get('lecciones_activas')}")
    print(f"  • Operaciones:       Operation IDs {p.get('operation_ids')}")
    
    print("\n--- [3. CATÁLOGO DE AGENTES (1-10)] ---")
    for ag in p.get("agentes_activos", []):
        print(f"  • {ag}")
        
    print("\n--- [4. SALUD DE CUOTAS] ---")
    for prov, stat in p.get("cuotas", {}).items():
        print(f"  • {prov.upper()}: {stat}")
        
    print("\n--- [5. HECHO HOY (HITOS COMPLETADOS)] ---")
    for idx, h in enumerate(p.get("hecho_hoy", []), 1):
        print(f"  {idx:02d}. {h}")
        
    print("\n--- [6. PENDIENTES INMEDIATOS] ---")
    for pend in p.get("pendientes", []):
        print(f"  {pend}")
        
    print("=" * 70)
    total_time = round(time.time() - t0, 3)
    print(f"[OK] Memoria consultada con éxito en {total_time} seg. Cero pérdida de contexto.")
    print("=" * 70)
    return p, total_time

if __name__ == "__main__":
    consultar_estado_hbos()
