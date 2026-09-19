import os
import sys
import math
import hashlib
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    else:
        vec = [1.0 / math.sqrt(dim)] * dim
    return vec

client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'), timeout=25)

# 1. P-18, P-19, P-20 en diamantino_patrones
patrones = [
    {
        "id": 18,
        "codigo": "P-18",
        "nombre": "Modelo de Voz — Una Sola Voz Narrativa",
        "descripcion": "Varios hosts aparecen visualmente en pantalla, pero una sola voz narrativa (Diamantino / Adam) unifica la locución completa para optimizar cuota de nube ElevenLabs y asegurar coherencia editorial.",
        "operation_id": 68
    },
    {
        "id": 19,
        "codigo": "P-19",
        "nombre": "División Local vs Nube",
        "descripcion": "Antigravity busca en local (config). El trabajo creativo está 100% en nube (voces, clips, imágenes). Verificar ambos. Si no está en local → buscar en nube. Si no está en nube → crear en nube.",
        "operation_id": 68
    },
    {
        "id": 20,
        "codigo": "P-20",
        "nombre": "Encarrilamiento Explícito de Antigravity",
        "descripcion": "Antigravity busca en local por defecto. Para trabajo creativo, reforzar en CADA prompt: (1) Trabajo creativo 100% en NUBE. (2) PROHIBIDO TTS local. (3) PROHIBIDO ffmpeg -loop 1. (4) Assets en DRIVE, no local. (5) Solo ffmpeg de ensamblado permitido en local.",
        "operation_id": 68
    }
]

for p in patrones:
    vec = generate_embedding(f"{p['codigo']} {p['nombre']} {p['descripcion']}", dim=384)
    client.upsert(
        collection_name="diamantino_patrones",
        points=[
            models.PointStruct(
                id=p["id"],
                vector=vec,
                payload=p
            )
        ]
    )
    print(f"[OK] {p['codigo']} registrado (ID {p['id']})")

# 2. L-10, L-11 en diamantino_lecciones
lecciones = [
    {
        "id": 10,
        "codigo": "L-10",
        "nombre": "Las Keys Trial Expiran",
        "descripcion": "Las keys trial de ElevenLabs expiran en ~24h o agotan cuota rápidamente. Solución: crear keys permanentes (Caducidad: Nunca), recargar créditos y optimizar guiones con voz narrativa unificada (P-18).",
        "operation_id": 68
    },
    {
        "id": 11,
        "codigo": "L-11",
        "nombre": "Antigravity Busca en Local por Defecto",
        "descripcion": "El agente busca en local, pero el trabajo creativo está en nube. Solución: P-20 (encarrilamiento explícito de Antigravity en cada instrucción).",
        "operation_id": 68
    }
]

for l in lecciones:
    vec = generate_embedding(f"{l['codigo']} {l['nombre']} {l['descripcion']}", dim=384)
    client.upsert(
        collection_name="diamantino_lecciones",
        points=[
            models.PointStruct(
                id=l["id"],
                vector=vec,
                payload=l
            )
        ]
    )
    print(f"[OK] {l['codigo']} registrado (ID {l['id']})")

# 3. Actualizar _MANIFIESTO_HBOS_DIAMANTINO.md
manifiesto_path = os.path.join("_MAESTRO", "_MANIFIESTO_HBOS_DIAMANTINO.md")
with open(manifiesto_path, "r", encoding="utf-8") as f:
    manifiesto_content = f.read()

secciones_nuevas = """
---

## 8. PROPIEDAD INTELECTUAL Y DELIMITACIÓN DE MARCA (SELLO CANÓNICO)
1. **Propiedad de Conceptos Científicos:** Los descubrimientos de modelos biológicos (AlphaFold, AlphaMissense, AlphaProteo) pertenecen a Google DeepMind y a los galardonados con el Premio Nobel de Química 2024 (Demis Hassabis, John Jumper, David Baker).
2. **Propiedad del Ecosistema Audiovisual:** El universo conceptual mineral, los avatares anfitriones (Diamantino, Rubín, Zafir, Esmeralda, Citrilo, Grafito, Amatista), la dirección de arte, los shaders cristalinos y el sistema agéntico DAG/RAG son propiedad exclusiva de Guillermo Hoyos / HBOS-Diamantino.
3. **Misión Editorial:** Transmitir conocimiento científico de vanguardia a escala global con máxima fidelidad técnica, atribución rigurosa y calidad cinematográfica.

---

## 9. GOBERNANZA ARQUITECTÓNICA: DIVISIÓN LOCAL VS NUBE (PATRONES P-19, P-20 / L-10, L-11)
1. **Entorno Local Restringido:**
   - Exclusivo para orquestación de comandos, lectura/escritura de configs (.env.local), scripts de pipeline y stitching/ensamblado técnico con FFmpeg.
   - Prohibición terminante de síntesis local (SAPI TTS) o simulaciones estáticas de video (ffmpeg -loop 1).
2. **Inferencia Creativa 100% en Nube:**
   - Voces: ElevenLabs Cloud API (normalizadas a P-04 v2: -14 LUFS, TP -1.0 dBTP).
   - Video: DashScope Wan 2.1 I2V Cloud para animación continua real.
   - Imágenes: Gemini Cloud / Nano Banana en Google Drive.
   - Memoria: Qdrant Cloud (colecciones de vectores y trazabilidad de operaciones).
   - Almacenamiento Maestro: Google Drive (`G:\\My Drive\\HBOS-Diamantino\\`).
3. **Modelo de Voz Unificada (P-18):**
   - Varios avatares minerales comparten el encuadre visual guiados por un único host narrador (Diamantino / Adam), garantizando sobriedad expositiva y eficiencia en consumo de créditos de nube.
"""

if "## 8. PROPIEDAD INTELECTUAL" not in manifiesto_content:
    manifiesto_content = manifiesto_content.strip() + "\n" + secciones_nuevas
    with open(manifiesto_path, "w", encoding="utf-8") as f:
        f.write(manifiesto_content)
    print(f"[OK] Manifiesto actualizado en {manifiesto_path}")
    
    # Sincronizar con Drive
    drive_manifiesto = os.path.join(r"G:\My Drive\HBOS-Diamantino\_MAESTRO", "_MANIFIESTO_HBOS_DIAMANTINO.md")
    with open(drive_manifiesto, "w", encoding="utf-8") as f:
        f.write(manifiesto_content)
    print(f"[OK] Manifiesto sincronizado en Drive: {drive_manifiesto}")

# 4. Registrar operation_id = 68 en registro_ecosistema
vec_op68 = generate_embedding("Tarea 2 operacion 68 P-19 P-20 L-10 L-11 Local vs Nube Encarrilamiento Manifiesto", dim=384)
client.upsert(
    collection_name="registro_ecosistema",
    points=[
        models.PointStruct(
            id=68,
            vector=vec_op68,
            payload={
                "operation_id": 68,
                "tarea": "TAREA 2 — P-19 + P-20 (LOCAL vs NUBE + ENCARRILAMIENTO)",
                "patrones_creados": ["P-18", "P-19", "P-20"],
                "lecciones_creadas": ["L-10", "L-11"],
                "manifiesto_actualizado": True,
                "estado": "COMPLETADO"
            }
        )
    ]
)
print("[OK] operation_id = 68 registrado en registro_ecosistema.")
