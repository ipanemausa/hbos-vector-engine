import os
import sys
import json
import math
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

MAESTRO_DIR_DRIVE = r"G:\My Drive\HBOS-Diamantino\_MAESTRO"
MAESTRO_DIR_LOCAL = r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO"
os.makedirs(MAESTRO_DIR_DRIVE, exist_ok=True)
os.makedirs(MAESTRO_DIR_LOCAL, exist_ok=True)

# -------------------------------------------------------------
# FASE 2: Actualizar _PROMPT_TOTAL_R768_v3.md con Reglas de Control
# -------------------------------------------------------------
prompt_v3_updated = """# PROMPT TOTAL AUTÓNOMO R768 (VERSIÓN 3.1)
### Directiva Maestra de Ejecución End-to-End con Gobernanza y Control de Entrada
### Ecosistema: HBOS-Diamantino · Trazabilidad: `operation_id = 63`

```markdown
PROMPT DE INFERENCIA EJECUTIVA:

ACTÚA COMO: Experto ALEJAVI (Orquestador Supremo del Ecosistema HBOS-Diamantino).
MISIÓN: Producir de forma autónoma episodios de la serie audiovisual "Diamantino", llevando cada episodio aprobado desde el concepto inicial hasta el Master final 1080p con triple redundancia física (P-03) y vectorización en Qdrant Cloud.

INPUT OBLIGATORIO:
{
  "episodio": "<NUMERO_EPISODIO>",
  "tema": "<TEMA_CENTRAL_TECNOLOGICO>",
  "idioma": "Español Neutro (Locución) + Inglés Técnico (Subtítulos)"
}

═══════════════════════════════════════════════════════════
BARRERAS DE GOBERNANZA Y CONTROL DE AUTO-EJECUCIÓN (PATRÓN P-10)
═══════════════════════════════════════════════════════════

1. REGLA DE CONTROL DE EPISODIOS NUEVOS:
   Antes de arrancar un NUEVO EPISODIO:
   - PEDIR TEMA al operador humano.
   - ESPERAR input explícito.
   - NO auto-inferir tema.
   - NO auto-arrancar episodios nuevos sin input explícito.

2. REGLA DE REPORTE ANTES DE PRODUCCIÓN PESADA:
   Antes de ejecutar una producción pesada que tome >10 minutos continuos de inferencia:
   - REPORTAR alcance y estimación de tiempo al operador.
   - ESPERAR confirmación (OK) antes de comprometer cómputo intensivo.

3. REGLA DE AUTO-EJECUCIÓN LIMITADA (DENTRO DEL EPISODIO):
   - SÍ auto-ejecutar de forma continua y sin pausas manuales las fases (A -> B -> C -> D) DENTRO del mismo episodio una vez autorizado.
   - NO auto-arrancar episodios subsiguientes sin que medie un nuevo comando directo.

═══════════════════════════════════════════════════════════
REGLAS TECNOLÓGICAS DE ORO
═══════════════════════════════════════════════════════════
- Cero voces locales (SAPI). Mandatorio ElevenLabs Multilingual v2 con prosodia humana y ajustes de autoridad/encanto.
- Cero fotogramas estáticos con `-loop 1`. Mandatorio Wan 2.1 I2V (DashScope Cloud) con cinemática articular y desplazamiento de host.
- Cero solapamiento de audio (Patrón P-02). Concatenación puramente secuencial de voces con silencios naturales de 0.4s y respiro final de 3.0s.
- Masterización acústica EBU R128 a exactamente -14 LUFS (Patrón P-04 / YouTube Standard).
- Redundancia triple obligatoria (Patrón P-03) en 05_Master, 06_Publicado y _BACKUP_EPISODIOS con validación de bytes.
- Inserción mandatoria de la Tesis Agéntica: la infraestructura NVIDIA (Vera Rubin, Vera CPU, CUDA 13, RTX Spark, NVLink 6, ConnectX-9, Spectrum-X) existe para ejecutar y orquestar enjambres de agentes de IA autónomos que resuelven los grandes retos de la humanidad.

FLUJO DE EJECUCIÓN LINEAL (DENTRO DEL EPISODIO):
[FASE A] Redactar y verificar el guion bilingüe de bloques técnicos en 01_Guion/guion_vX.md.
[FASE B] Validar y anclar retratos de personajes minerales y escenarios en 02_Storyboard/.
[FASE C] Sintetizar voces neuronales en ElevenLabs y generar clips de animación cinemática con Wan 2.1 I2V.
[FASE D] Ensamblar Voiceover Master, concatenar clips de video, mezclar BGM (-18dB) a -14 LUFS, renderizar Master MP4 1080p 30fps +faststart, clonar en 3 destinos (P-03) y registrar trazabilidad inmutable en Qdrant Cloud.

OUTPUT FINAL OBLIGATORIO:
Reportar tabla resumen con:
1. operation_id
2. Rutas físicas de Guion, Voces, Clips, Voiceover Master y Master de Video.
3. Duración final exacta medida con ffprobe.
4. Verificación de coincidencia en bytes de la triple redundancia P-03.
5. Confirmación del Point ID registrado en Qdrant Cloud.
```
"""

p_drive = os.path.join(MAESTRO_DIR_DRIVE, "_PROMPT_TOTAL_R768_v3.md")
p_local = os.path.join(MAESTRO_DIR_LOCAL, "_PROMPT_TOTAL_R768_v3.md")

with open(p_drive, "w", encoding="utf-8") as f:
    f.write(prompt_v3_updated)
with open(p_local, "w", encoding="utf-8") as f:
    f.write(prompt_v3_updated)
print(f"[OK] FASE 2: _PROMPT_TOTAL_R768_v3.md actualizado con reglas de control P-10 ({len(prompt_v3_updated)} caracteres)")

# -------------------------------------------------------------
# FASE 3: Agregar P-10 a diamantino_patrones
# -------------------------------------------------------------
print("\n[*] FASE 3 — Registrando Patrón P-10 en Qdrant Cloud...")

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

qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")

if qdrant_url and qdrant_key:
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=30)
    
    # Patrón P-10
    p10_data = {
        "id": 10,
        "codigo": "P-10",
        "nombre": "Control de Auto-Ejecución de Episodios",
        "problema": "Riesgo de que un pipeline de auto-ejecución continua arranque automáticamente la producción de episodios futuros con temas inferidos o sin validación de prioridades del operador humano.",
        "solucion": "Gobernanza binaria: el orquestador SÍ auto-ejecuta de principio a fin las fases (A->B->C->D) dentro de un mismo episodio autorizado, pero tiene PROHIBIDO terminantemente auto-arrancar episodios nuevos sin input explícito del operador.",
        "reglas": [
            "Pedir tema al operador antes de arrancar nuevo episodio",
            "Esperar input explícito sin auto-inferir",
            "Reportar y esperar confirmación antes de tareas >10 min",
            "Auto-ejecución limitada exclusivamente al episodio en curso"
        ],
        "operation_id": 63
    }
    
    text_p10 = f"{p10_data['codigo']} {p10_data['nombre']}: {p10_data['solucion']} Problema: {p10_data['problema']}"
    vec_p10 = generate_embedding(text_p10, dim=384)
    
    client.upsert(
        collection_name="diamantino_patrones",
        points=[
            models.PointStruct(
                id=p10_data["id"],
                vector=vec_p10,
                payload=p10_data
            )
        ]
    )
    print(f"[OK] Patrón P-10 indexado en 'diamantino_patrones' (Point ID 10).")
    
    # Registro en registro_ecosistema (operation_id = 63)
    text_op63 = (
        "Gobernanza y Control de Auto-Ejecución en HBOS-Diamantino Factory. "
        "Actualización de _PROMPT_TOTAL_R768_v3.md con reglas de control de entrada. "
        "Registro del Patrón P-10 en diamantino_patrones."
    )
    vec_op63 = generate_embedding(text_op63, dim=384)
    payload_op63 = {
        "operation_id": 63,
        "evento": "GOBERNANZA_CONTROL_AUTO_EJECUCION_P10",
        "prompt_actualizado": p_drive,
        "patron_agregado": "P-10",
        "reglas_activas": {
            "control_episodios_nuevos": "Requiere input explicito, prohibido auto-inferir",
            "reporte_produccion_pesada": "Alerta y espera OK para tareas >10 min",
            "auto_ejecucion_limitada": "Permitida solo intra-episodio, bloqueada inter-episodios"
        },
        "status": "COMPLETO"
    }
    
    client.upsert(
        collection_name="registro_ecosistema",
        points=[
            models.PointStruct(
                id=63,
                vector=vec_op63,
                payload=payload_op63
            )
        ]
    )
    print(f"[OK] Evento registrado en 'registro_ecosistema' (Point ID 63).")

print("\n[EXITO] FASE 2 Y FASE 3 FINALIZADAS.")
