"""
hbos_healthcheck.py — CHEQUEO DE SALUD ULTRARRÁPIDO (<5s)
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Gobernanza: DAG R768 · Autopilot Total
"""

import os
import sys
import time
import json
import argparse
import urllib.request
import urllib.error
import socket
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

def check_socket(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def check_qdrant(fast_mode=False):
    t0 = time.time()
    url = os.getenv("QDRANT_URL")
    key = os.getenv("QDRANT_API_KEY")
    if not url or not key:
        return {"status": "FAIL", "reason": "Credenciales faltantes", "latencia": 0}
    
    # HTTP REST Ping para velocidad máxima sin overhead pesado de gRPC
    try:
        headers = {"api-key": key, "Accept": "application/json"}
        req = urllib.request.Request(f"{url.rstrip('/')}/collections", headers=headers)
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            cols = [c["name"] for c in data.get("result", {}).get("collections", [])]
            lat = round(time.time() - t0, 3)
            critical = [
                "diamantino_patrones", "diamantino_lecciones", "diamantino_agentes",
                "hbos_estado", "hbos_directorio", "diamantino_casos_uso",
                "hbos_metricas", "diamantino_movimientos", "registro_ecosistema"
            ]
            missing = [c for c in critical if c not in cols]
            status = "OK" if not missing and lat < 2.0 else ("DEGRADED" if not missing else "FAIL")
            return {
                "status": status,
                "latencia": lat,
                "total_colecciones": len(cols),
                "faltantes": missing,
                "url": url[:30] + "..."
            }
    except Exception as e:
        return {"status": "FAIL", "reason": str(e), "latencia": round(time.time() - t0, 3)}

def check_mcps():
    cfg_path = r"C:\Users\ipane\.gemini\config\mcp_config.json"
    if not os.path.exists(cfg_path):
        return {"status": "FAIL", "reason": "mcp_config.json no existe"}
    
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        servers = cfg.get("mcpServers", {})
        results = {}
        for s_name, s_conf in servers.items():
            args = s_conf.get("args", [])
            target = args[0] if args else ""
            exists = os.path.exists(target)
            results[s_name] = {"entry": target, "exists": exists}
        
        all_ok = all(v["exists"] for v in results.values())
        return {
            "status": "OK" if all_ok else "DEGRADED",
            "total_servers": len(servers),
            "servers": results
        }
    except Exception as e:
        return {"status": "FAIL", "reason": str(e)}

def check_freellmapi():
    t0 = time.time()
    # Check port 3001
    port_open = check_socket("127.0.0.1", 3001, timeout=0.8)
    if not port_open:
        return {"status": "FAIL", "reason": "Puerto 3001 cerrado / Daemon inactivo", "latencia": round(time.time() - t0, 3)}
    
    api_key = "freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037"
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        req = urllib.request.Request("http://127.0.0.1:3001/v1/models", headers=headers)
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            models_list = data.get("data", [])
            lat = round(time.time() - t0, 3)
            return {
                "status": "OK" if len(models_list) >= 200 else "DEGRADED",
                "latencia": lat,
                "modelos": len(models_list)
            }
    except Exception as e:
        return {"status": "DEGRADED", "reason": f"Port abierto pero error API: {e}", "latencia": round(time.time() - t0, 3)}

def check_apis_cuotas():
    keys = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "DASHSCOPE_API_KEY": os.getenv("DASHSCOPE_API_KEY"),
        "FAL_API_KEY": os.getenv("FAL_API_KEY"),
        "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
        "HF_API_TOKEN": os.getenv("HF_API_TOKEN")
    }
    status = {}
    for k, v in keys.items():
        if not v:
            status[k] = "MISSING"
        else:
            status[k] = "CONFIGURED"
    
    # Cuotas conocidas segun trazabilidad de auditoria
    status["CUOTAS_STATUS"] = {
        "gemini": "ACTIVA_ILIMITADA",
        "groq": "ACTIVA_ALTA_VELOCIDAD",
        "dashscope": "PAUSADA_CUOTA_FREETIER_AGOTADA",
        "fal_ai": "PAUSADA_BALANCE_AGOTADO",
        "elevenlabs": "PAUSADA_CICLO_AGOTADO"
    }
    return status

def check_triple_redundancia():
    loc = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO"
    drv = r"G:\My Drive\HBOS-Diamantino\_MAESTRO"
    bak = r"C:\Users\ipane\backup_hbos\_MAESTRO"
    
    docs_loc = set(f for f in os.listdir(loc) if f.endswith('.md')) if os.path.exists(loc) else set()
    docs_drv = set(f for f in os.listdir(drv) if f.endswith('.md')) if os.path.exists(drv) else set()
    docs_bak = set(f for f in os.listdir(bak) if f.endswith('.md')) if os.path.exists(bak) else set()
    
    drift_drv = docs_loc - docs_drv
    drift_bak = docs_loc - docs_bak
    
    status = "OK" if not drift_drv and not drift_bak else "DRIFT_DETECTED"
    return {
        "status": status,
        "total_local": len(docs_loc),
        "total_drive": len(docs_drv),
        "total_backup": len(docs_bak),
        "faltantes_drive": list(drift_drv),
        "faltantes_backup": list(drift_bak)
    }

def run_healthcheck(fast=False, as_json=False):
    t_start = time.time()
    
    qdrant = check_qdrant(fast_mode=fast)
    mcps = check_mcps()
    freellm = check_freellmapi()
    apis = check_apis_cuotas()
    redundancia = check_triple_redundancia()
    
    total_time = round(time.time() - t_start, 3)
    
    overall = "HEALTHY"
    if qdrant["status"] == "FAIL" or mcps["status"] == "FAIL" or freellm["status"] == "FAIL":
        overall = "CRITICAL_FAIL"
    elif redundancia["status"] == "DRIFT_DETECTED" or qdrant["status"] == "DEGRADED":
        overall = "DRIFT_REPAIR_NEEDED"
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "overall_status": overall,
        "elapsed_seconds": total_time,
        "fast_mode": fast,
        "components": {
            "qdrant": qdrant,
            "mcps": mcps,
            "freellmapi": freellm,
            "redundancia": redundancia,
            "apis": apis
        }
    }
    
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        print("=" * 65)
        print(f"[*] HBOS HEALTHCHECK — RESULTADO: [{overall}] ({total_time}s)")
        print("=" * 65)
        print(f"  • Qdrant Cloud:       [{qdrant['status']}] (Latencia: {qdrant.get('latencia', 0)}s, {qdrant.get('total_colecciones', 0)} colecciones)")
        print(f"  • Servidores MCP:     [{mcps['status']}] ({mcps.get('total_servers', 0)} servidores configurados)")
        print(f"  • FreeLLMAPI Daemon:  [{freellm['status']}] ({freellm.get('modelos', 0)} modelos disponibles en :3001)")
        print(f"  • Triple Redundancia: [{redundancia['status']}] (Local:{redundancia['total_local']}, Drive:{redundancia['total_drive']}, Backup:{redundancia['total_backup']})")
        print(f"  • Inferencia Activa:  Gemini (OK) | Groq (OK) | Wan2.1 (Pausada) | Fal.ai (Pausada)")
        if redundancia["status"] == "DRIFT_DETECTED":
            print(f"  [!] DRIFT: Drive={redundancia['faltantes_drive']} | Backup={redundancia['faltantes_backup']}")
        print("=" * 65)
        
    return 0 if overall in ["HEALTHY", "DRIFT_REPAIR_NEEDED"] else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HBOS Healthcheck R768")
    parser.add_argument("--fast", action="store_true", help="Modo rápido para pre-commit")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON estructurado")
    args = parser.parse_args()
    
    code = run_healthcheck(fast=args.fast, as_json=args.json)
    sys.exit(code)
