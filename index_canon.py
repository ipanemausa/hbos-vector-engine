import os, sys, re, hashlib, math, json
from dotenv import load_dotenv
load_dotenv(r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")

from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')

q_url = os.getenv("QDRANT_URL")
q_key = os.getenv("QDRANT_API_KEY")

if not q_url or not q_key:
    print("[ERROR] Credenciales Qdrant ausentes en .env.local")
    sys.exit(1)

client = QdrantClient(url=q_url, api_key=q_key, timeout=30)
COLLECTION_NAME = "hbos_canon"
DIM = 384

def generate_embedding(text: str, dim: int = 384) -> list:
    """Generador de embeddings determinista ponderado normalizado L2."""
    vec = [0.0] * dim
    words = text.lower().split()
    if not words:
        return [1.0 / math.sqrt(dim)] * dim
    for i, word in enumerate(words):
        # Hash de palabra con contexto de posición
        h = int(hashlib.sha256(f"{word}_{i % 7}".encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        weight = 1.0 + (1.0 / (1.0 + (h % 11)))
        vec[idx] += weight
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

# 1. Asegurar colección hbos_canon
existing = [c.name for c in client.get_collections().collections]
if COLLECTION_NAME not in existing:
    print(f"[*] Creando colección '{COLLECTION_NAME}' (dim={DIM}, distance=Cosine)...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=DIM, distance=models.Distance.COSINE)
    )
    print(f"[OK] Colección '{COLLECTION_NAME}' creada exitosamente.")
else:
    print(f"[*] Colección '{COLLECTION_NAME}' ya existe.")

# 2. Parsear _HBOS_CANON_COMPLETO.md
canon_file = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO\_HBOS_CANON_COMPLETO.md"
with open(canon_file, "r", encoding="utf-8") as f:
    text = f.read()

points = []
point_id = 1

# Extraer Reglas R1 a R73 con Regex
# Formato: * **R1 · Idempotencia:** Toda operación...
pattern_reglas = re.compile(r'\*\s+\*\*(R\d+)\s+[·•\-]\s+([^:]+):\*\*\s+(.+)')

for line in text.splitlines():
    m = pattern_reglas.match(line.strip())
    if m:
        rid, nombre, detalle = m.group(1), m.group(2).strip(), m.group(3).strip()
        num = int(rid.replace("R", ""))
        full_rule_text = f"{rid} · {nombre}: {detalle}"
        vec = generate_embedding(f"{rid} {nombre} {detalle}", DIM)
        h = hashlib.sha256(full_rule_text.encode('utf-8')).hexdigest()
        
        payload = {
            "regla_id": rid,
            "numero": num,
            "nombre": nombre,
            "texto": detalle,
            "texto_completo": full_rule_text,
            "categoria": "Reglas Duras",
            "fuente": "_HBOS_CANON_COMPLETO.md",
            "sha256": h
        }
        points.append(models.PointStruct(id=num, vector=vec, payload=payload))

# Añadir R74 explícitamente si no está
r74_file = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO\_R74_PROBAR_MCP_AISLAMIENTO_MAESTRA.md"
r74_text = "Todo MCP nuevo o modificado debe probarse en aislamiento antes de añadirlo a mcp_config.json."
if os.path.exists(r74_file):
    with open(r74_file, "r", encoding="utf-8") as f:
        r74_raw = f.read()
    r74_text = r74_raw.strip()

points.append(models.PointStruct(
    id=74,
    vector=generate_embedding("R74 Probar MCP Nuevos en Aislamiento " + r74_text, DIM),
    payload={
        "regla_id": "R74",
        "numero": 74,
        "nombre": "Probar MCP Nuevos en Aislamiento",
        "texto": r74_text[:500],
        "texto_completo": f"R74 · Probar MCP Nuevos en Aislamiento: {r74_text[:500]}",
        "categoria": "Reglas Duras",
        "fuente": "_R74_PROBAR_MCP_AISLAMIENTO_MAESTRA.md",
        "sha256": hashlib.sha256(r74_text.encode('utf-8')).hexdigest()
    }
))

# 3. Añadir Doctrina Canónica (R768, FAM@-T, DAG, H_ALT, §0, §D, §16)
doctrina_items = [
    (101, "DOCTRINA_R768", "Factorización R768", "Factorización R768: 87% de reducción en consumo de tokens y máxima precisión semántica. V(t) = sum(N_i * A_i * P_i * E_i * T_i). R14 · R768 No Consecutivo: dimensionalidad formal."),
    (102, "DOCTRINA_FAM_T", "FAM@-T Navegación Total", "FAM@-T es la máxima abstracción operativa del Ecosistema Soberano HBOS. No selecciona operadores aislados; navega el ENTORNO TOTAL proyectando tareas directamente en el espacio vectorial 384d (distancia Coseno en Qdrant Cloud). FAM@-T: T x ENTORNO TOTAL -> OUTPUT_HIBRIDO. R19: Navegación consciente de la totalidad."),
    (103, "DOCTRINA_DAG", "Grafo Dirigido Acíclico DAG", "§3 · DAG = GRAFO DIRIGIDO ACÍCLICO DE FACTORIZACIONES. El flujo del sistema se ejecuta en estricto orden topológico. Las fases concurrentes corren en hilos independientes y convergen en nodos de integración formal. Workflow definitivo de 10 fases."),
    (104, "DOCTRINA_H_ALT", "Mecánica Dialéctica H_ALT", "H_ALT es la mecánica algorítmica de auto-superación del ecosistema. Genera alternativas ortogonales, las somete a prueba empírica en NUBE con blindaje anti-caché y sintetiza una variante emergente D. Conmutación determinista ante caídas de proveedores sin degradar el canon."),
    (105, "PRINCIPIO_RECTOR", "§0 Principio Rector Soberano", "CREAS SIEMPRE EN NUBE. COORDINAS EN UNBE. NUNCA EN LOCAL. PC local = terminal sin GPU."),
    (106, "DESACOPLAMIENTO_D", "§D Desacoplamiento por Capas (0-13)", "Capa 0: Infraestructura, Capa 1: Canon, Capa 2: Código, Capa 3: MCP, Capa 4: Agentes, Capa 5: Pipeline, Capa 6: Distribución, Capa 7: Community, Capa 8: Monetización, Capa 9: PI, Capa 10: Seguridad, Capa 11: Creador, Capa 12: Representante legal, Capa 13: Abogado."),
    (107, "PROMPT_RECTOR", "Prompt Conceptual Rector", "PROMPT CONCEPTUAL AGÉNTICO CREATIVO · EJECUCIÓN TOTAL · FAM@-T · LLMAPI ⊕ R768 · DAG · H_ALT · NO-REGRESIÓN. Subproyecto: Producción de Video · Workflow Definitivo v2.0.")
]

for doc_id, codigo, nombre, contenido in doctrina_items:
    points.append(models.PointStruct(
        id=doc_id,
        vector=generate_embedding(f"{codigo} {nombre} {contenido}", DIM),
        payload={
            "regla_id": codigo,
            "numero": doc_id,
            "nombre": nombre,
            "texto": contenido,
            "texto_completo": f"{nombre}: {contenido}",
            "categoria": "Doctrina y Principios",
            "fuente": "_HBOS_CANON_COMPLETO.md",
            "sha256": hashlib.sha256(contenido.encode('utf-8')).hexdigest()
        }
    ))

print(f"[*] Total puntos preparados para indexar: {len(points)}")

# 4. Upsert por batches
batch_size = 25
for i in range(0, len(points), batch_size):
    batch = points[i:i+batch_size]
    client.upsert(collection_name=COLLECTION_NAME, points=batch)
    print(f"   - Indexados puntos {i+1} a {min(i+batch_size, len(points))} OK")

# 5. Verificación Empírica de Búsqueda
print("\n=== VERIFICACIÓN EMPÍRICA DE BÚSQUEDA VECTORIAL ===")

def test_query(q_str):
    q_vec = generate_embedding(q_str, DIM)
    hits = client.search(collection_name=COLLECTION_NAME, query_vector=q_vec, limit=2)
    print(f"\n[QUERY]: '{q_str}'")
    for h in hits:
        pl = h.payload
        print(f"  -> Score: {h.score:.4f} | ID: {h.id} | [{pl.get('regla_id')}] {pl.get('nombre')}")
        print(f"     Texto: {pl.get('texto')[:140]}...")

test_query("FAM@-T navegación del entorno total")
test_query("R62 anchors vivos 420 movimientos")
test_query("R58 veracidad total hechos cientificos")

print("\n[P2_INDEX_CANON_COMPLETED]: OK")
