"""
hbos_watchdog.py — DAEMON VIGILANTE Y MONITOR CONTINUO DE SALUD SOBERANA
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Gobernanza: DAG R768 · Autopilot Total
"""

import os
import sys
import time
import json
import subprocess
import argparse
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

CONFIG_PATH = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.hbos_autopilot.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "schedule": {"watchdog_interval_minutes": 30}
    }

def run_single_check():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [WATCHDOG] Ejecutando inspección de salud...")
    
    # 1. Healthcheck rápido
    res_h = subprocess.run(["python", "hbos_healthcheck.py", "--fast", "--json"], capture_output=True, text=True, encoding="utf-8")
    
    drift_detected = False
    try:
        report = json.loads(res_h.stdout)
        status = report.get("overall_status", "UNKNOWN")
        print(f"  • Estado detectado: {status} ({report.get('elapsed_seconds', 0)}s)")
        if status == "DRIFT_REPAIR_NEEDED":
            drift_detected = True
    except Exception:
        if "DRIFT_DETECTED" in res_h.stdout or "DRIFT_REPAIR_NEEDED" in res_h.stdout:
            drift_detected = True

    # 2. Si hay drift, auto-reparar
    if drift_detected:
        print("  [!] DRIFT DETECTADO. Disparando protocolo hbos_repair.py...")
        res_r = subprocess.run(["python", "hbos_repair.py"], capture_output=True, text=True, encoding="utf-8")
        print("  [OK] Reparación completada:")
        for line in res_r.stdout.splitlines()[-5:]:
            print("    ", line)
        
        # Disparar commit automático de sincronización
        print("  [*] Sincronizando en Git con hbos_commit_auto.py...")
        subprocess.run(["python", "hbos_commit_auto.py", "--msg", "watchdog auto-repair triple redundancy drift"], check=False)
    else:
        print("  [OK] Cero drift. Sistema íntegro.")

    return drift_detected

def start_watchdog(interval_seconds=1800, run_once=False):
    print("=" * 65)
    print(f">>> [HBOS WATCHDOG] DAEMON VIGILANTE INICIADO (Intervalo: {interval_seconds}s) <<<")
    print("=" * 65)

    if run_once:
        run_single_check()
        print("[*] Modo --once finalizado.")
        return

    try:
        while True:
            run_single_check()
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n[*] Watchdog detenido por señal de interrupción.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HBOS Watchdog R768")
    parser.add_argument("--once", action="store_true", help="Ejecutar un único ciclo de verificación y salir")
    parser.add_argument("--interval", type=int, default=None, help="Intervalo en segundos entre chequeos")
    args = parser.parse_args()

    cfg = load_config()
    default_interval = cfg.get("schedule", {}).get("watchdog_interval_minutes", 30) * 60
    interval = args.interval if args.interval is not None else default_interval

    start_watchdog(interval_seconds=interval, run_once=args.once)
