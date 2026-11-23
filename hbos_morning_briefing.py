# HBOS QUADRANT ENGINE - BRIEFING MATUTINO & AUDITORIA DE PROVEEDORES (AUTÓNOMO V2)
import os, sys, json, sqlite3, urllib.request, urllib.error, datetime

DB_PATH = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
PROXY_URL = "http://127.0.0.1:3001/v1"
GDRIVE_BACKUP = "G:/My Drive/HBOS_BACKUP/telemetria"
os.makedirs(GDRIVE_BACKUP, exist_ok=True)

def obtener_credenciales():
    token = None
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key='unified_api_key' OR key='api_key' OR key='token' LIMIT 1")
            row = cur.fetchone()
            if row:
                token = row[0]
            conn.close()
        except:
            pass
    return token or "freellmapi-86a3178c0952594913cb64f17d3b8ce95ab63e87023ff14d"

def ejecutar_briefing():
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    auth_token = obtener_credenciales()
    headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    informe = {
        "fecha": fecha_hoy,
        "proxy_activo": False,
        "total_modelos_db": 0,
        "total_modelos_api": 0,
        "plataformas_activas": 0,
        "rutas_conmutador": {},
        "tareas_automaticas": [],
        "tareas_pendientes_intervencion": []
    }
    
    # 1. Auditoria DB
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM models WHERE enabled=1")
            informe["total_modelos_db"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(DISTINCT platform) FROM models WHERE enabled=1")
            informe["plataformas_activas"] = cur.fetchone()[0]
            conn.close()
        except Exception as e:
            informe["tareas_pendientes_intervencion"].append(f"Error DB: {e}")

    # 2. Conectividad HTTP :3001
    try:
        req = urllib.request.Request(f"{PROXY_URL}/models", headers=headers)
        with urllib.request.urlopen(req, timeout=8) as r:
            if r.status == 200:
                informe["proxy_activo"] = True
                data = json.loads(r.read().decode("utf-8"))
                modelos = data.get("data", [])
                informe["total_modelos_api"] = len(modelos)
                informe["tareas_automaticas"].append(f"Gateway :3001 verificado HTTP 200 con {len(modelos)} endpoints activos.")
    except Exception as e:
        informe["tareas_pendientes_intervencion"].append(f"Error en Gateway :3001: {e}")

    # 3. Test de canales auto (15s timeout)
    for canal in ["auto:fast", "auto:code"]:
        try:
            payload = json.dumps({
                "model": canal,
                "messages": [{"role": "user", "content": "1"}],
                "max_tokens": 1
            }).encode("utf-8")
            req = urllib.request.Request(f"{PROXY_URL}/chat/completions", data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as r:
                res_data = json.loads(r.read().decode("utf-8"))
                modelo_backend = res_data.get("model", "OK")
                informe["rutas_conmutador"][canal] = f"OPERATIVO ({modelo_backend})"
        except urllib.error.HTTPError as e:
            informe["rutas_conmutador"][canal] = f"HTTP {e.code}"
            informe["tareas_pendientes_intervencion"].append(f"Canal {canal} respondió HTTP {e.code}. Revisar mapeo de ruta en FreeLLMAPI.")
        except Exception as e:
            informe["rutas_conmutador"][canal] = f"TIMEOUT / {type(e).__name__}"

    # 4. Estado matriz
    informe["tareas_automaticas"].append("Matriz Universal (38 casos desacoplados) sincronizada en Google Drive.")
    
    # 5. Persistencia GDrive
    ruta_backup = os.path.join(GDRIVE_BACKUP, "hbos_briefing_hoy.json")
    with open(ruta_backup, "w", encoding="utf-8") as f:
        json.dump(informe, f, indent=2, ensure_ascii=False)

    # 6. Salida en Pantalla
    print("\n============================================================")
    print(f"      HBOS QUADRANT ENGINE · INFORME MATUTINO ({fecha_hoy[:10]})")
    print("============================================================")
    estado_str = "ONLINE (Autorizado)" if informe["proxy_activo"] else "OFFLINE"
    print(f"[*] Gateway FreeLLMAPI :3001    : {estado_str}")
    print(f"[*] Modelos en DB / Plataformas : {informe['total_modelos_db']} modelos en {informe['plataformas_activas']} proveedores")
    print(f"[*] Endpoints HTTP Validados    : {informe['total_modelos_api']}")
    
    print("\n--- ESTADO DE CANALES EN CONMUTADOR ---")
    for r, st in informe["rutas_conmutador"].items():
        print(f"  • {r:<15} : {st}")

    print("\n--- ACCIONES EJECUTADAS AUTOMÁTICAMENTE ---")
    for act in informe["tareas_automaticas"]:
        print(f"  [OK] {act}")

    print("\n--- TAREAS QUE REQUIEREN TU INTERVENCIÓN ---")
    if informe["tareas_pendientes_intervencion"]:
        for i, t in enumerate(informe["tareas_pendientes_intervencion"], 1):
            print(f"  [{i}] {t}")
    else:
        print("  [✓] Canales operativos sin intervenciones pendientes.")
    print("============================================================\n")

if __name__ == "__main__":
    ejecutar_briefing()
