# ==============================================================================
# HBOS QUADRANT ENGINE · CLOSED-LOOP RAG QUERY (ASD-STE100)
# ==============================================================================
import os, sys, json, time, hashlib, urllib.request, urllib.error

DB_PATH = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
PROXY_URL = "http://127.0.0.1:3001/v1"
QDRANT_HOST = "http://127.0.0.1:6333"
COLLECTION_NAME = "hbos_knowledge_r768"

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

def consultar_memoria_qdrant(pregunta, top_k=3):
    vector_query = generar_vector_r768(pregunta)
    url = f"{QDRANT_HOST}/collections/{COLLECTION_NAME}/points/search"
    payload = {
        "vector": vector_query,
        "limit": top_k,
        "with_payload": True
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    contexto = []
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            res = json.loads(r.read().decode("utf-8"))
            for punto in res.get("result", []):
                pl = punto.get("payload", {})
                score = punto.get("score", 0)
                contenido = pl.get("summary") or pl.get("output") or pl.get("content") or ""
                if contenido:
                    contexto.append(f"[Score: {score:.3f} | Fuente: {pl.get('source')}] {contenido}")
    except Exception as e:
        print(f"[!] Falla consulta Qdrant: {e}")
    return "\n---\n".join(contexto) if contexto else "Sin registros previos coincidentes."

def sintetizar_respuesta(pregunta, contexto_recuperado):
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    instruccion_ste = (
        "ACTÚA COMO ARQUITECTO JEFE DE HBOS QUADRANT ENGINE BAJO NORMA ASD-STE100. "
        "USA EXCLUSIVAMENTE EL CONTEXTO RECUPERADO DE LA MEMORIA VECTORIAL PARA RESPONDER. "
        "PROHIBIDO: Prohibido incluir notas de pensamiento, 'thinking process', introducciones o rellenos. "
        "ENTREGA ESTRICTAMENTE EN 3 LÍNEAS IMPERATIVAS: "
        "1. RESPUESTA TÉCNICA: "
        "2. REGLA O CONFIGURACIÓN APLICABLE: "
        "3. ACCIÓN INMEDIATA:"
    )
    
    prompt_usuario = (
        f"PREGUNTA DEL COMANDANTE: {pregunta}\n\n"
        f"MEMORIA RECUPERADA DE QDRANT (R768):\n{contexto_recuperado}"
    )
    
    body = {
        "model": "auto:fast",
        "messages": [
            {"role": "system", "content": instruccion_ste},
            {"role": "user", "content": prompt_usuario}
        ],
        "temperature": 0.0,
        "max_tokens": 450
    }
    
    req = urllib.request.Request(f"{PROXY_URL}/chat/completions", data=json.dumps(body).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            data = json.loads(res.read().decode("utf-8"))
            raw = data["choices"][0]["message"]["content"]
            if "</thought>" in raw:
                raw = raw.split("</thought>")[-1].strip()
            elif "Here's a thinking process:" in raw and "1." in raw:
                raw = "1." + raw.split("1.", 1)[1]
            return raw.strip()
    except Exception as e:
        return f"ERROR_INFERENCIA: {type(e).__name__}"

def main():
    if len(sys.argv) < 2:
        print("Uso: python hbos_query_rag.py <PREGUNTA_O_INSTRUCCION>")
        sys.exit(1)
        
    consulta = " ".join(sys.argv[1:])
    print("============================================================")
    print("   HBOS ENGINE · CONSULTA VECTORIAL RAG EN MEMORIA (R768)")
    print("============================================================")
    print(f"[*] Buscando contexto relevante en Qdrant (:6333)...")
    contexto = consultar_memoria_qdrant(consulta)
    
    print(f"[*] Sintetizando directiva en auto:fast (:3001)...")
    respuesta = sintetizar_respuesta(consulta, contexto)
    
    print("\n--- DICTAMEN DE MEMORIA CERRADA (ASD-STE100) ---")
    print(respuesta)
    print("-------------------------------------------------\n")

if __name__ == "__main__":
    main()
