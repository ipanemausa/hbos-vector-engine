# ==============================================================================
# HBOS QUADRANT ENGINE · PROTOCOLO ASD-STE100 & PERILLA DE ESFUERZO (KARPATHY)
# ==============================================================================
import os, sys, json, time, hashlib, urllib.request, urllib.error

DB_PATH = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
PROXY_URL = "http://127.0.0.1:3001/v1"
QDRANT_HOST = "http://127.0.0.1:6333"
COLLECTION_NAME = "hbos_knowledge_r768"
GDRIVE_LOGS = "G:/My Drive/HBOS_BACKUP/telemetria"
os.makedirs(GDRIVE_LOGS, exist_ok=True)

def obtener_token():
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

def generar_vector_r768(texto):
    h = hashlib.sha256(texto.encode("utf-8")).digest()
    base = [float(b) / 255.0 for b in h]
    vector = (base * 24)[:768]
    norm = sum(x**2 for x in vector) ** 0.5
    return [round(x / norm, 6) for x in vector]

def registrar_en_qdrant(comando_verbo, dictamen_ste):
    punto_id = int(time.time())
    vector = generar_vector_r768(f"{comando_verbo} {dictamen_ste}")
    payload = {
        "points": [{
            "id": punto_id,
            "vector": vector,
            "payload": {
                "source": "hbos_ste100_core",
                "verbo": comando_verbo,
                "output": dictamen_ste[:400],
                "standard": "ASD-STE100",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }]
    }
    url = f"{QDRANT_HOST}/collections/{COLLECTION_NAME}/points?wait=true"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status == 200
    except:
        return False

def compilar_estocastico_ste100(verbo_accion, contexto_tecnico, nivel_esfuerzo=1):
    """
    Perilla de Esfuerzo (Karpathy):
    Nivel 1: auto:fast (Obrero crucero, latencia minima)
    Nivel 2: auto:code (Compilacion formal de software)
    Nivel 3: auto:reasoning (Test-Time compute / Resolucion de fallas)
    """
    canales = {1: "auto:fast", 2: "auto:code", 3: "auto:reasoning"}
    modelo_objetivo = canales.get(nivel_esfuerzo, "auto:fast")
    
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Cabecera de Aviacion ASD-STE100 Estricta
    sistema_ste100 = (
        "ACTÚA COMO INGENIERO DE CABINA Y COMPILADOR ESTOCÁSTICO BAJO NORMA ASD-STE100. "
        "REGLAS OBLIGATORIAS: "
        "1. Escribe solo oraciones cortas (máximo 20 palabras). "
        "2. Usa exclusivamente voz activa y verbos imperativos directos. "
        "3. Emite una sola instrucción u orden por línea. "
        "4. Prohibida toda introducción, saludo, cortesía, metáfora o conclusión. "
        "5. Salida directa: 1) ACCIÓN, 2) REGLA DETERMINISTA, 3) VERIFICACIÓN."
    )
    
    payload = {
        "model": modelo_objetivo,
        "messages": [
            {"role": "system", "content": sistema_ste100},
            {"role": "user", "content": f"ORDEN DIRECTA: {verbo_accion}\nCONTEXTO OPERATIVO: {contexto_tecnico}"}
        ],
        "temperature": 0.0, # Minima dispersión estocástica para rigor técnico
        "max_tokens": 400
    }
    
    req = urllib.request.Request(f"{PROXY_URL}/chat/completions", data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res["choices"][0]["message"]["content"], modelo_objetivo
    except Exception as e:
        return f"FALLO_CANAL: {type(e).__name__}", modelo_objetivo

def main():
    if len(sys.argv) < 3:
        print("Uso: python hbos_ste100_core.py <VERBO_ACCION> <CONTEXTO_TECNICO> [NIVEL_ESFUERZO 1-3]")
        sys.exit(1)
        
    verbo = sys.argv[1].upper()
    contexto = sys.argv[2]
    esfuerzo = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    print(f"[*] CABINA HBOS: Iniciando protocolo ASD-STE100 (Perilla Esfuerzo: {esfuerzo})...")
    dictamen, canal_usado = compilar_estocastico_ste100(verbo, contexto, esfuerzo)
    
    print(f"\n--- DIRECTIVA ASD-STE100 [{canal_usado}] ---")
    print(dictamen)
    print("--------------------------------------------------\n")
    
    # Asentamiento en memoria vectorial y disco
    ok_qdrant = registrar_en_qdrant(verbo, dictamen)
    print(f"[*] Persistencia Vectorial Qdrant (R768): {'CONFIRMADA' if ok_qdrant else 'FALLIDA'}")
    
    log_path = os.path.join(GDRIVE_LOGS, "ste100_directives.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{canal_usado}] ORDEN: {verbo}\n{dictamen}\n")
    print(f"[*] Bitacora inmutable actualizada en Google Drive.")

if __name__ == "__main__":
    main()
