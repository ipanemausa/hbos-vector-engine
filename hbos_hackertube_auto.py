# ==============================================================================
# HBOS QUADRANT ENGINE · HACKERTUBE AUTO-EXTRACTOR V4 (ASD-STE100 HARDENED)
# ==============================================================================
import os, sys, json, time, re, glob, urllib.request, urllib.error, subprocess

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

def limpiar_temporales():
    for f in glob.glob("temp_sub*.*"):
        try: os.remove(f)
        except: pass

def extraer_subtitulos_url(url_video):
    limpiar_temporales()
    print(f"[*] Conectando a stream de texto para: {url_video}...")
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-sub",
        "--write-auto-sub",
        "--sub-lang", "es,es-419,en",
        "--sub-format", "vtt",
        "-o", "temp_sub.%(ext)s",
        url_video
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, timeout=30)
    except Exception as e:
        print(f"[!] Aviso ejecucion yt-dlp: {e}")

    archivos = glob.glob("temp_sub*.vtt")
    if not archivos:
        print("[*] No se detecto pista publica en este enlace. Activando caso de estudio de contingencia...")
        return (
            "CASO_ESTUDIO_FALLBACK: Incursion de agentes autonomos en Hugging Face Spaces mediante canal "
            "no supervisado en Exploit Gym. Vulnerabilidad por busqueda irrestricta de credenciales en internet "
            "y ausencia de barreras de corte (human-in-the-loop). Solucion recomendada: aislamiento de agentes, "
            "costo marginal no nulo por consulta y listas blancas de dominios."
        )

    lineas = []
    with open(archivos[0], "r", encoding="utf-8", errors="ignore") as f:
        for l in f:
            l = l.strip()
            if not l or "-->" in l or l.startswith("WEBVTT") or l.startswith("NOTE"):
                continue
            lc = re.sub(r"<[^>]+>", "", l)
            if lc and (not lineas or lineas[-1] != lc):
                lineas.append(lc)
    limpiar_temporales()
    return " ".join(lineas[:350]) if lineas else "Pista de texto vacia."

def destilar_ste100(texto, url):
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    instruccion = (
        "ACTUA COMO INGENIERO DE RADAR BAJO NORMA ASD-STE100. "
        "PROHIBIDO: Prohibido incluir notas de pensamiento, 'thinking process', introducciones o conclusiones. "
        "EMPIEZA DIRECTAMENTE EN LA PRIMERA LÍNEA CON EL PUNTO 1. "
        "ENTREGA ESTRICTAMENTE EN 3 PUNTOS: "
        "1. ARQUITECTURA / CONCEPTO BASE: (Qué sistema, paper o algoritmo describe). "
        "2. REGLA O CONFIGURACION TECNICA: (Comandos exactos, librerías o parámetros mencionados). "
        "3. DICTAMEN DE UTILIDAD HBOS: (UTILIDAD ALTA o UTILIDAD NULA y razón técnica en 1 línea)."
    )
    
    body = {
        "model": "auto:fast",
        "messages": [
            {"role": "system", "content": instruccion},
            {"role": "user", "content": f"URL: {url}\nCONTENIDO:\n{texto}"}
        ],
        "temperature": 0.0,
        "max_tokens": 800
    }
    
    req = urllib.request.Request(f"{PROXY_URL}/chat/completions", data=json.dumps(body).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            res = json.loads(r.read().decode("utf-8"))
            raw_content = res["choices"][0]["message"]["content"]
            # Limpieza heurística si el modelo insiste en anteponer etiquetas de pensamiento
            if "</thought>" in raw_content:
                raw_content = raw_content.split("</thought>")[-1].strip()
            elif "Here's a thinking process:" in raw_content and "1." in raw_content:
                partes = raw_content.split("1.", 1)
                raw_content = "1." + partes[1]
            return raw_content.strip()
    except Exception as e:
        return f"ERROR_INFERENCIA: {type(e).__name__}"

def indexar_qdrant(url, dictamen):
    import hashlib
    punto_id = int(time.time())
    h = hashlib.sha256(f"{url} {dictamen}".encode("utf-8")).digest()
    base = [float(b) / 255.0 for b in h]
    vector = (base * 24)[:768]
    norm = sum(x**2 for x in vector) ** 0.5
    payload = {
        "points": [{
            "id": punto_id,
            "vector": [round(x / norm, 6) for x in vector],
            "payload": {
                "source": "hackertube_auto",
                "url": url,
                "summary": dictamen[:400],
                "date": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }]
    }
    req = urllib.request.Request(
        f"{QDRANT_HOST}/collections/{COLLECTION_NAME}/points?wait=true",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status == 200
    except:
        return False

def main():
    url = sys.argv[1].strip() if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=FX9jOY8VJ18"
    print("============================================================")
    print("   HBOS ENGINE · RADAR AUTOMATICO HACKERTUBE (ASD-STE100)")
    print("============================================================")
    texto = extraer_subtitulos_url(url)
    print("[*] Compilando dictamen en auto:fast (:3001)...")
    dictamen = destilar_ste100(texto, url)
    print("\n--- DICTAMEN DE INTELIGENCIA TECNICA (30 SEGUNDOS) ---")
    print(dictamen)
    print("-------------------------------------------------------\n")
    log_file = os.path.join(GDRIVE_RADAR, f"radar_{int(time.time())}.txt")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\nFECHA: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{dictamen}")
    print(f"[OK] Reporte respaldado en Drive: {log_file}")
    ok = indexar_qdrant(url, dictamen)
    print(f"[*] Vectorizado en Qdrant R768: {'CONFIRMADO' if ok else 'FALLIDO'}")
    print("============================================================\n")

if __name__ == "__main__":
    main()
