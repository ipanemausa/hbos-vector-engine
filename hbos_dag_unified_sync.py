# ==============================================================================
# HBOS QUADRANT ENGINE · DAG UNIFICADO DE INVESTIGACIÓN, PULL Y AUTO-UPDATE (V5)
# ==============================================================================
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
            cur.execute("SELECT value FROM settings WHERE key='unified_api_key' LIMIT 1")
            row = cur.fetchone()
            if row:
                token = row[0]
            conn.close()
        except:
            pass
    return token or "freellmapi-86a3178c0952594913cb64f17d3b8ce95ab63e87023ff14d"

def fase_0_handshake():
    token = obtener_credenciales()
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(f"{PROXY_URL}/models", headers=headers)
    with urllib.request.urlopen(req, timeout=8) as r:
        if r.status == 200:
            return token, True
    return token, False

def fase_1_y_2_muse_update_db():
    modelos_a_sincronizar = [
        ("electronhub", "qwen3.6-27b", "Qwen 3.6 27B", 88, 92),
        ("cohere", "cohere/north-mini-code:free", "Cohere North Mini Code", 85, 95),
        ("nvidia", "nvidia/nemotron-3-ultra-550b-a55b", "Nemotron 3 Ultra 550B", 94, 80),
        ("cloudflare", "deepseek-r1:free", "DeepSeek R1 Free", 95, 75)
    ]
    
    inyectados = 0
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        for platform, model_id, display_name, intel_rank, spd_rank in modelos_a_sincronizar:
            # Buscar por la clave compuesta exacta (platform, model_id)
            cur.execute("SELECT id FROM models WHERE platform = ? AND model_id = ?", (platform, model_id))
            row = cur.fetchone()
            if row:
                cur.execute("""
                    UPDATE models 
                    SET display_name = ?, intelligence_rank = ?, speed_rank = ?, enabled = 1
                    WHERE id = ?
                """, (display_name, intel_rank, spd_rank, row[0]))
            else:
                cur.execute("""
                    INSERT INTO models (
                        platform, model_id, display_name, intelligence_rank, speed_rank, 
                        enabled, source, size_label, monthly_token_budget, endpoint_scope
                    )
                    VALUES (?, ?, ?, ?, ?, 1, 'muse_radar', 'cloud', 'unlimited', '')
                """, (platform, model_id, display_name, intel_rank, spd_rank))
            inyectados += 1
            
        conn.commit()
        conn.close()
    return inyectados

def fase_3_smoke_test(token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resultados = {}
    for canal in ["auto:fast", "auto:code"]:
        try:
            payload = json.dumps({
                "model": canal,
                "messages": [{"role": "user", "content": "1"}],
                "max_tokens": 1
            }).encode("utf-8")
            req = urllib.request.Request(f"{PROXY_URL}/chat/completions", data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=25) as r:
                res = json.loads(r.read().decode("utf-8"))
                resultados[canal] = f"OPERATIVO ({res.get('model', 'OK')})"
        except Exception as e:
            resultados[canal] = f"ERROR ({type(e).__name__})"
    return resultados

def ejecutar_dag_completo():
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n============================================================")
    print(f"   HBOS QUADRANT ENGINE · DAG DE SINCRONIZACIÓN AUTOMÁTICA")
    print("============================================================")
    
    token, online = fase_0_handshake()
    print(f"[*] Fase 0 (Handshake)   : {'Gateway :3001 ONLINE' if online else 'OFFLINE'}")
    if not online:
        print("[!] Abortando DAG: Gateway 3001 no respondió.")
        return

    actualizados = fase_1_y_2_muse_update_db()
    print(f"[*] Fase 1 & 2 (Muse DB) : {actualizados} modelos actualizados/inyectados en freeapi.db")

    test_res = fase_3_smoke_test(token)
    print("[*] Fase 3 (Smoke Test)  :")
    for canal, estado in test_res.items():
        print(f"    • {canal:<15} : {estado}")

    telemetria = {
        "timestamp": fecha_hoy,
        "gateway_status": "ONLINE",
        "modelos_actualizados": actualizados,
        "canales_verificados": test_res
    }
    ruta_gdrive = os.path.join(GDRIVE_BACKUP, "dag_sync_report.json")
    with open(ruta_gdrive, "w", encoding="utf-8") as f:
        json.dump(telemetria, f, indent=2, ensure_ascii=False)
        
    print(f"[*] Fase 4 (Persistencia): Reporte consolidado en G:\\My Drive\\HBOS_BACKUP\\")
    print("============================================================\n")

if __name__ == "__main__":
    ejecutar_dag_completo()
