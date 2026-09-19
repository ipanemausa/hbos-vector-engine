import os
import sys
import json
import math
import shutil
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

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

print(">>> [TAREA 6 ACTUALIZACIÓN] Registrando P-17, L-09 y actualizando Ep04 con Bloque 0...")

qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")
client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=30)

# 1. P-17 en diamantino_patrones
p17_codigo = "P-17"
p17_nombre = "Modelo de Divulgacion con Credito"
p17_desc = "HBOS-Diamantino es una agencia de divulgación científica. Los hosts cristalinos NO descubren, EXPLICAN. Todo video NUEVO que presente descubrimientos de terceros DEBE incluir: (1) Nota de referencia al inicio. (2) Crédito al autor original. (3) Fuente oficial citada. (4) Aclaración de rol (host/analista). (5) Fuentes en pantalla. Sin esto → NO se publica."
vec_p17 = generate_embedding(f"{p17_codigo} {p17_nombre} {p17_desc}", dim=384)

client.upsert(
    collection_name="diamantino_patrones",
    points=[
        models.PointStruct(
            id=17,
            vector=vec_p17,
            payload={
                "codigo": p17_codigo,
                "nombre": p17_nombre,
                "descripcion": p17_desc,
                "operation_id": 71
            }
        )
    ]
)
print("[OK] P-17 registrado en diamantino_patrones (id=17).")

# 2. L-09 en diamantino_lecciones
l09_codigo = "L-09"
l09_nombre = "Falta de Nota de Referencia en Ep02/Ep03"
l09_desc = "Los videos Ep02 y Ep03 no incluyeron nota de referencia al autor original. Esto se corregirá en una fase posterior. Para TODOS los videos nuevos (Ep04+) es OBLIGATORIA."
vec_l09 = generate_embedding(f"{l09_codigo} {l09_nombre} {l09_desc}", dim=384)

client.upsert(
    collection_name="diamantino_lecciones",
    points=[
        models.PointStruct(
            id=9,
            vector=vec_l09,
            payload={
                "codigo": l09_codigo,
                "nombre": l09_nombre,
                "descripcion": l09_desc,
                "operation_id": 71
            }
        )
    ]
)
print("[OK] L-09 registrado en diamantino_lecciones (id=9).")

# 3. Actualizar _MANIFIESTO_HBOS_DIAMANTINO.md con Sección "Modelo de Divulgación con Crédito"
manifest_local = r"_MAESTRO\_MANIFIESTO_HBOS_DIAMANTINO.md"
manifest_drive = r"G:\My Drive\HBOS-Diamantino\_MAESTRO\_MANIFIESTO_HBOS_DIAMANTINO.md"

with open(manifest_local, "r", encoding="utf-8") as f:
    m_content = f.read()

seccion_divulgacion = """
---

## 7. MODELO DE DIVULGACIÓN CIENTÍFICA CON CRÉDITO CANÓNICO (PATRÓN P-17 / L-09)
HBOS-Diamantino opera formalmente como una **AGENCIA DE DIVULGACIÓN CIENTÍFICA**.
1. **Rol de los Hosts:** Los personajes cristalinos NO descubren, NO inventan y NUNCA se apropian de tecnologías de terceros. Los hosts cristalinos EXPLICAN, ANALIZAN y DIFUNDEN el avance humano.
2. **Requisitos de Publicación Mandatorios (Ep04 en adelante):**
   - **Nota de referencia al inicio:** Placa/locución en los primeros 5 segundos.
   - **Crédito inequívoco:** Mención explícita a los autores originales (ej. Google DeepMind, Demis Hassabis, John Jumper, David Baker, NVIDIA).
   - **Fuentes en pantalla:** Inserción de chips de referencia (Nature, Science, NobelPrize.org).
   - **Delimitación de Propiedad:** El sistema audiovisual, los avatares minerales y el sello son autoría de Guillermo Hoyos / HBOS-Diamantino; el avance científico pertenece a sus investigadores.
"""

if "## 7. MODELO DE DIVULGACIÓN" not in m_content:
    m_content = m_content.strip() + "\n" + seccion_divulgacion

with open(manifest_local, "w", encoding="utf-8") as f:
    f.write(m_content)
with open(manifest_drive, "w", encoding="utf-8") as f:
    f.write(m_content)

print("[OK] Manifiesto actualizado con Sección 7 (Modelo de Divulgación con Crédito).")

# 4. Actualizar guion_v1.md de Ep04 incorporando BLOQUE 0 (NOTA DE REFERENCIA - 5s)
guion_ep04_file_local = r"Ep04\01_Guion\guion_v1.md"
guion_ep04_file_drive = r"G:\My Drive\HBOS-Diamantino\Ep04-MedicineAgentica\01_Guion\guion_v1.md"

with open(guion_ep04_file_local, "r", encoding="utf-8") as f:
    old_guion = f.read()

bloque_0 = """### [00:00 - 00:05] BLOQUE 0: NOTA DE REFERENCIA CANÓNICA (PATRÓN P-17)
**Visual:** Placa editorial de alta gama en fondo azul cuántico con tipografía blanca nítida y badges discretos de DeepMind y NobelPrize.org. Diamantino aparece en un marco lateral de autoridad sobria.  
**Texto en Pantalla / Voz en Off (Diamantino):**  
"NOTA DE REFERENCIA: Los descubrimientos presentados en este video son propiedad de sus respectivos autores. AlphaFold y modelos derivados pertenecen a Google DeepMind; el Premio Nobel de Química 2024 a Demis Hassabis, John Jumper y David Baker. HBOS-Diamantino actúa exclusivamente como host y agencia de divulgación científica. Nuestros avatares explican, no descubren."  
**English Subtitles:**  
"REFERENCE NOTICE: The scientific breakthroughs featured herein are the intellectual property of their original creators. AlphaFold belongs to Google DeepMind; the 2024 Nobel Prize in Chemistry to Demis Hassabis, John Jumper, and David Baker. HBOS-Diamantino acts solely as host and science communication agency. Our crystalline hosts explain; they do not discover."  
**Dato Técnico / Fuente:** Protocolo Editorial P-17 (Divulgación Científica con Crédito).

---

"""

if "BLOQUE 0: NOTA DE REFERENCIA" not in old_guion:
    # Insertar justo antes de la INTRODUCCIÓN
    new_guion = old_guion.replace("### [00:00 - 00:20] INTRODUCCIÓN", bloque_0 + "### [00:05 - 00:25] INTRODUCCIÓN")
    with open(guion_ep04_file_local, "w", encoding="utf-8") as f:
        f.write(new_guion)
    with open(guion_ep04_file_drive, "w", encoding="utf-8") as f:
        f.write(new_guion)
    print("[OK] guion_v1.md de Ep04 actualizado con BLOQUE 0 (Nota de Referencia P-17).")

# 5. Actualizar storyboard_v1.json de Ep04
sb_file_local = r"Ep04\02_Storyboard\storyboard_v1.json"
sb_file_drive = r"G:\My Drive\HBOS-Diamantino\Ep04-MedicineAgentica\02_Storyboard\storyboard_v1.json"

with open(sb_file_local, "r", encoding="utf-8") as f:
    sb_data = json.load(f)

if not any(p.get("plano") == 0 for p in sb_data.get("planos", [])):
    bloque_0_plano = {
        "plano": 0,
        "personaje": "Diamantino (Editorial)",
        "duracion_seg": 5.0,
        "tipo": "Nota de Referencia P-17",
        "movimiento_p14": "cabeza_asentir_arriba_30",
        "desplazamiento_p16": "placa_editorial_sobria",
        "prompt_wan21": "Clean scientific disclaimer title card with glowing crystalline frame, subtle blue quantum particles, acknowledging Google DeepMind and Nobel Prize authors with extreme prestige"
    }
    sb_data["planos"].insert(0, bloque_0_plano)
    with open(sb_file_local, "w", encoding="utf-8") as f:
        json.dump(sb_data, f, indent=2, ensure_ascii=False)
    with open(sb_file_drive, "w", encoding="utf-8") as f:
        json.dump(sb_data, f, indent=2, ensure_ascii=False)
    print("[OK] Storyboard de Ep04 actualizado con Plano 0 (Nota de Referencia).")

print("[OK] Tarea 6 Actualizada y registrada exitosamente.")
