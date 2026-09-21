"""
hbos_verify_unbe.py — VERIFICACIÓN FORMAL DE PROTOCOLO §1.0 UNBE
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
"""

import os
import hashlib
import json
import time
import urllib.request
import subprocess
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv('.env.local')

def verificar_unbe():
    print("=" * 70)
    print(">>> PROTOCOLO DE VERIFICACIÓN §1.0 UNBE (EJECUCIÓN RED DISTRIBUIDA) <<<")
    print("=" * 70)

    # 1. Tres réplicas físicas
    loc = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO\_FACTORIZACION_MAESTRA.md"
    drv = r"G:\My Drive\HBOS-Diamantino\_MAESTRO\_FACTORIZACION_MAESTRA.md"
    bak = r"c:\Users\ipane\backup_hbos\_MAESTRO\_FACTORIZACION_MAESTRA.md"

    h_loc = hashlib.sha256(open(loc, 'rb').read()).hexdigest() if os.path.exists(loc) else None
    h_drv = hashlib.sha256(open(drv, 'rb').read()).hexdigest() if os.path.exists(drv) else None
    h_bak = hashlib.sha256(open(bak, 'rb').read()).hexdigest() if os.path.exists(bak) else None

    triple_match = (h_loc == h_drv == h_bak) and (h_loc is not None)

    print(f"1. RÉPLICAS FÍSICAS (_FACTORIZACION_MAESTRA.md):")
    print(f"   • Local:  {h_loc}")
    print(f"   • Drive:  {h_drv}")
    print(f"   • Backup: {h_bak}")
    print(f"   • Coincidencia Triple 100%: {'[OK]' if triple_match else '[FAIL]'}")

    # 2. Qdrant Cloud
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=15)
    t0 = time.time()
    cols = [c.name for c in client.get_collections().collections]
    lat_qdrant = round(time.time() - t0, 3)
    qdrant_ok = len(cols) >= 17 and lat_qdrant < 1.0
    print(f"\n2. QDRANT CLOUD:")
    print(f"   • Colecciones: {len(cols)}/17 activas")
    print(f"   • Latencia:    {lat_qdrant}s (< 1.0s: {'[OK]' if lat_qdrant < 1.0 else '[FAIL]'})")

    # 3. FreeLLMAPI :3001
    api_key = "freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037"
    req = urllib.request.Request("http://127.0.0.1:3001/v1/models", headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode('utf-8'))
            models_cnt = len(data.get("data", []))
    except Exception as e:
        models_cnt = 0
    print(f"\n3. FREELLMAPI DAEMON (:3001):")
    print(f"   • Modelos disponibles: {models_cnt} (>= 3: {'[OK]' if models_cnt >= 3 else '[FAIL]'})")

    # 4. Servidores MCP
    mcp_config = r"C:\Users\ipane\.gemini\config\mcp_config.json"
    with open(mcp_config, "r", encoding="utf-8") as f:
        mcps = json.load(f).get("mcpServers", {})
    all_mcps_exist = all(os.path.exists(s.get("args", [""])[0]) for s in mcps.values())
    print(f"\n4. SERVIDORES MCP:")
    print(f"   • Servidores activos: {len(mcps)}/4 ({', '.join(mcps.keys())})")
    print(f"   • Archivos de entrada válidos: {'[OK]' if all_mcps_exist else '[FAIL]'}")

    # 5. Git Commit & Push a origin/main
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    origin_hash = subprocess.check_output(["git", "rev-parse", "origin/main"], text=True).strip()
    synced = (commit_hash == origin_hash)
    print(f"\n5. GIT REPOSITORIO & SINCRONIZACIÓN REMOTA:")
    print(f"   • Commit HEAD:        {commit_hash}")
    print(f"   • Commit origin/main: {origin_hash}")
    print(f"   • Sincronizado con origin/main: {'[OK]' if synced else '[FAIL]'}")

    # 6. Trazabilidad en Qdrant (registro_ecosistema y hbos_estado)
    pts_reg = client.retrieve("registro_ecosistema", ids=[232])
    pts_est = client.retrieve("hbos_estado", ids=[1])
    op_in_reg = len(pts_reg) > 0
    rango_est = pts_est[0].payload.get("operation_ids") or pts_est[0].payload.get("operaciones_completadas")
    print(f"\n6. TRAZABILIDAD INMUTABLE:")
    print(f"   • operation_id = 232 en registro_ecosistema: {'[OK]' if op_in_reg else '[FAIL]'}")
    print(f"   • hbos_estado (ID=1) rango activo:          {rango_est}")

    print("=" * 70)
    unbe_healthy = triple_match and qdrant_ok and (models_cnt >= 3) and all_mcps_exist and synced and op_in_reg
    print(f"[VEREDICTO UNBE]: {'EJECUCIÓN VÁLIDA EN UNBE · CUMPLE §1.0 AL 100%' if unbe_healthy else 'FALLO DE PROTOCOLO UNBE'}")
    print("=" * 70)
    return {
        "triple_match": triple_match,
        "sha256": h_loc,
        "qdrant_lat": lat_qdrant,
        "qdrant_cols": len(cols),
        "freellmapi_models": models_cnt,
        "mcps_count": len(mcps),
        "commit_hash": commit_hash,
        "synced": synced,
        "operation_id_registered": op_in_reg,
        "rango_activo": rango_est,
        "unbe_healthy": unbe_healthy
    }

if __name__ == "__main__":
    verificar_unbe()
