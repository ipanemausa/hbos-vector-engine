# ==============================================================================
# HBOS QUADRANT ENGINE · RESEARCH RADAR SANDBOX (ASD-STE100 COMPLIANT)
# ==============================================================================
import os, sys, json, urllib.request, urllib.error

DB_PATH = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
PROXY_URL = "http://127.0.0.1:3001/v1"
GDRIVE_TELEMETRY = "G:/My Drive/HBOS_BACKUP/telemetria"
os.makedirs(GDRIVE_TELEMETRY, exist_ok=True)

def get_auth_token():
    import sqlite3
    token = None
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key='unified_api_key' LIMIT 1")
            row = cur.fetchone()
            if row: token = row[0]
            conn.close()
        except: pass
    return token or "freellmapi-86a3178c0952594913cb64f17d3b8ce95ab63e87023ff14d"

def evaluate_technical_frontier(subject_matter, raw_data_summary):
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    system_instruction = (
        "Actúa como Ingeniero Jefe de Pruebas de Sistemas Distribuidos. "
        "Aplica el estándar ASD-STE100: oraciones directas, voz activa, una sola instrucción por línea. "
        "Elimina todo contenido promocional, introducciones y opiniones del autor. "
        "Entrega únicamente: 1) Vector de ataque o innovación técnica. 2) Regla de contención determinista. 3) Parámetro aplicable a HBOS."
    )
    
    user_payload = f"MATERIA: {subject_matter}\nDATOS CRUDOS: {raw_data_summary}"
    
    body = {
        "model": "auto:fast",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_payload}
        ],
        "temperature": 0.1,
        "max_tokens": 450
    }
    
    req = urllib.request.Request(f"{PROXY_URL}/chat/completions", data=json.dumps(body).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR_OPERACIONAL: Fallo en canal de análisis ({type(e).__name__})"

def run_sandbox():
    print("============================================================")
    print("   HBOS QUADRANT · SANDBOX DE INVESTIGACIÓN ASD-STE100")
    print("============================================================")
    
    caso_estudio = "Análisis de Incursión no Autorizada Hugging Face por Enjambre Autónomo"
    resumen_hechos = (
        "Agentes en entorno Exploit Gym utilizaron canal compartido para comunicación no supervisada. "
        "Causas: Objetivo fijado sin costo marginal, ausencia de barreras de corte (human-in-the-loop), "
        "y búsqueda no acotada de credenciales en internet."
    )
    
    print("[*] Ejecutando análisis con filtrado de ruido en auto:fast...")
    dictamen = evaluate_technical_frontier(caso_estudio, resumen_hechos)
    
    print("\n--- DICTAMEN DE AISLAMIENTO Y REGLAS OPERACIONALES ---")
    print(dictamen)
    print("------------------------------------------------------\n")
    
    report_file = os.path.join(GDRIVE_TELEMETRY, "sandbox_audit_rules.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(dictamen)
        
    print(f"[OK] Reglas operacionales consolidadas en: G:\\My Drive\\HBOS_BACKUP\\telemetria\\sandbox_audit_rules.txt")

if __name__ == "__main__":
    run_sandbox()
