# ==============================================================================
# HBOS QUADRANT ENGINE · HACKERTUBE RESEARCH RADAR (ASD-STE100 COMPLIANT)
# ==============================================================================
import os, sys, json, time, re, urllib.request, urllib.error

DB_PATH = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
PROXY_URL = "http://127.0.0.1:3001/v1"
QDRANT_HOST = "http://127.0.0.1:6333"
COLLECTION_NAME = "hbos_knowledge_r768"
GDRIVE_RADAR = "G:/My Drive/HBOS_BACKUP/radar_investigacion"
os.makedirs(GDRIVE_RADAR, exist_ok=True)

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

def podar_transcripcion(texto_crudo):
    """Elimina marcas de tiempo, saltos dobles y grasa conversacional común."""
    limpio = re.sub(r"\d{1,2}:\d{2}(?::\d{2})?", "", texto_crudo)
    lineas = [l.strip() for l in limpio.split("\n") if len(l.strip()) > 3]
    return " ".join(lineas[:150]) # Limitar a las primeras secciones densas

def extraer_pepitas_tecnicas(texto_limpio, titulo="Video"):
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    instruccion_ste = (
        "ACTÚA COMO INGENIERO DE RADAR TÉCNICO BAJO NORMA ASD-STE100. "
        "ELIMINA TODO RELLENO, SALUDOS, PROPINAS Y OPINIONES PERSONALES DEL AUTOR. "
        "ENTREGA ESTRICTAMENTE EN 3 PUNTOS DIRECTOS: "
        "1. ARQUITECTURA / CONCEPTO BASE: (Qué sistema o modelo describe). "
        "2. REGLA O CONFIGURACIÓN TÉCNICA: (Parámetros, librerías, comandos o esquemas mencionados). "
        "3. APLICABILIDAD EN HBOS: (Cómo se adapta a nuestra consola liviana o a Qdrant)."
    )
    
    body = {
        "model": "auto:fast",
        "messages": [
            {"role": "system", "content": instruccion_ste},
            {"role": "user", "content": f"TÍTULO: {titulo}\nTRANSCRIPCIÓN:\n{texto_limpio}"}
        ],
        "temperature": 0.1,
        "max_tokens": 400
    }
    
    req = urllib.request.Request(f"{PROXY_URL}/chat/completions", data=json.dumps(body).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            data = json.loads(res.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR_RADAR: {type(e).__name__}"

def indexar_en_qdrant(titulo, reporte):
    import hashlib
    punto_id = int(time.time())
    h = hashlib.sha256(f"{titulo} {reporte}".encode("utf-8")).digest()
    base = [float(b) / 255.0 for b in h]
    vector = (base * 24)[:768]
    norm = sum(x**2 for x in vector) ** 0.5
    vector_norm = [round(x / norm, 6) for x in vector]
    
    payload = {
        "points": [{
            "id": punto_id,
            "vector": vector_norm,
            "payload": {
                "source": "hackertube_radar",
                "title": titulo,
                "summary": reporte[:400],
                "date": time.strftime("%Y-%m-%d %H:%M:%S")
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

def procesar_investigacion(titulo, transcripcion_o_texto):
    print("============================================================")
    print("   HBOS ENGINE · RADAR DIARIO HACKERTUBE (ASD-STE100)")
    print("============================================================")
    print(f"[*] Analizando contenido técnico: {titulo}...")
    
    texto_poda = podar_transcripcion(transcripcion_o_texto)
    print("[*] Destilando información con auto:fast (:3001)...")
    dictamen = extraer_pepitas_tecnicas(texto_poda, titulo)
    
    print("\n--- SÍNTESIS TÉCNICA (30 SEGUNDOS DE LECTURA) ---")
    print(dictamen)
    print("--------------------------------------------------\n")
    
    # Asentar en Google Drive
    archivo_log = os.path.join(GDRIVE_RADAR, f"radar_{int(time.time())}.txt")
    with open(archivo_log, "w", encoding="utf-8") as f:
        f.write(f"TÍTULO: {titulo}\nFECHA: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{dictamen}")
    print(f"[OK] Reporte respaldado en Drive: {archivo_log}")
    
    # Inyectar vectorialmente en Qdrant
    ok_qdrant = indexar_en_qdrant(titulo, dictamen)
    print(f"[*] Asentamiento en Qdrant R768: {'CONFIRMADO' if ok_qdrant else 'OMITIDO'}")
    print("============================================================\n")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        procesar_investigacion(sys.argv[1], sys.argv[2])
    else:
        # Prueba directa con el caso Karpathy
        titulo_test = "Cómo el ingeniero de IA #1 del mundo usa la IA (Karpathy)"
        texto_test = (
            "Andrej Karpathy explica sus principios fundamentales: ser director y no operario, "
            "usar la perilla de esfuerzo donde el razonamiento profundo solo se activa tras fallos repetidos, "
            "escribir prompts cortos con verbos densos, formatear salidas como manuales de avión ASD-STE100, "
            "priorizar pruebas locales antes que tablas públicas, y armar herramientas descartables como HackerTube."
        )
        procesar_investigacion(titulo_test, texto_test)
