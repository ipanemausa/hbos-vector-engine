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

# -------------------------------------------------------------
# FASE 1: Crear _FLUJO_TOTAL_HBOS.md
# -------------------------------------------------------------
flujo_total_content = """# SISTEMA INTEGRAL DE PRODUCCIÓN AUDIOVISUAL AUTÓNOMA — HBOS-DIAMANTINO
### Documento Maestro: Flujo Operativo Total y Guía de Inferencia Agéntica
### Trazabilidad: `operation_id = 61` · Ecosistema: HBOS-Diamantino · Arquitectura Cristalina

---

## 1. VISIÓN Y ARQUITECTURA GENERAL DEL PIPELINE

El pipeline de producción HBOS-Diamantino transforma un requerimiento temático canónico (`{episodio, tema, idioma}`) en un Master Audiovisual Broadcast 1080p con animación cinemática real, voces neuronales sincronizadas, masterización sonora EBU R128 (-14 LUFS) y persistencia inmutable en tres niveles de almacenamiento físico y vectorización cuántica en Qdrant Cloud.

El flujo se divide estrictamente en cuatro grupos funcionales (A, B, C, D) interconectados por compuertas lógicas autónomas (checkpoints computados) sin cuellos de botella de aprobación manual.

---

## 2. DESGLOSE EXHAUSTIVO POR GRUPOS OPERATIVOS

### GRUPO A: CONCEPTUALIZACIÓN, GUION TÉCNICO Y FUNDAMENTACIÓN
**Objetivo:** Extracción de especificaciones de hardware (GTC Taipei 2026), asignación de personajes cristalinos y estructuración del guion bilingüe.

#### 8 Pasos Operativos:
1. **Paso A.1:** Ingesta y normalización del input temático y delimitación de componentes de hardware NVIDIA.
2. **Paso A.2:** Asignación ontológica de avatares minerales según afinidad técnica (Rubín=GPU, Zafir=CPU, Esmeralda=CUDA, Citrilo=LPU, Grafito=NVLink, Amatista=Spectrum-X, Diamantino=Host Central).
3. **Paso A.3:** Redacción de la tesis central agéntica (la infraestructura existe para orquestar agentes, no para ejecutar tareas manuales).
4. **Paso A.4:** Estructuración temporal de bloques (Intro, Bloques 1-6, Bloque 7 Agéntico Extra, Cierre Ensemble).
5. **Paso A.5:** Generación de locuciones en español neutro con cadencia de keynote de alta autoridad.
6. **Paso A.6:** Generación de subtítulos técnicos en inglés (*English Subtitles*) con terminología de ingeniería de sistemas.
7. **Paso A.7:** Verificación de fuentes canónicas (whitepapers NVIDIA, GTC Keynotes, especificaciones de arquitectura).
8. **Paso A.8:** Compilación y guardado inmutable en `01_Guion/guion_vX.md` (Drive y local).

#### 7 Validaciones del Grupo A:
1. `val_a1`: Presencia explícita de los 7 componentes y sus roles técnicos sin metáforas abstractas.
2. `val_a2`: Inclusión mandatoria del Bloque 7 de Diamantino sobre Computación Agéntica.
3. `val_a3`: Ausencia total de humanos reales o ficticios.
4. `val_a4`: Estimación temporal por bloque dentro del rango de 15 a 55 segundos.
5. `val_a5`: Precisión léxica de acrónimos (FP4, FP8, NVLink 6, SRAM, ConnectX-9, BlueField-4).
6. `val_a6`: Subtítulos en inglés perfectamente alineados semánticamente con el texto en español.
7. `val_a7`: Formato Markdown estricto con encabezados, metadatos y citas técnicas.

#### 6 Tests del Grupo A:
1. `test_a1`: Test sintáctico de parsing Markdown (sin bloques rotos o caracteres huérfanos).
2. `test_a2`: Test de conteo de palabras para estimación de velocidad de lectura (130-150 palabras/minuto).
3. `test_a3`: Test de unicidad de rol (ningún componente duplica la función de otro).
4. `test_a4`: Test de preservación de voz de host (Diamantino abre, sintetiza la era agéntica y despide).
5. `test_a5`: Test de idempotencia de guardado en Google Drive.
6. `test_a6`: Test de codificación UTF-8 pura (tildes y caracteres especiales sin corrupción).

#### 8 Debug Routes del Grupo A:
1. `dbg_a1`: Si falta un componente -> Inyectar especificación desde `_FICHA_PERSONAJES.md`.
2. `dbg_a2`: Si el texto es demasiado largo (>60s) -> Ejecutar poda léxica conservando términos de hardware.
3. `dbg_a3`: Si falta el Bloque Agéntico -> Insertar plantilla canónica de Diamantino GTC 2026.
4. `dbg_a4`: Si hay discrepancia de subtítulos -> Regenerar bloque en inglés mediante traducción técnica directa.
5. `dbg_a5`: Si falla la escritura en Google Drive -> Escribir en caché local y reintentar montaje del volumen G:.
6. `dbg_a6`: Si se detecta mención humana -> Reemplazar por operador agéntico u orquestador cristalino.
7. `dbg_a7`: Si la cadencia no es solemne -> Ajustar tono léxico hacia autoridad ejecutiva.
8. `dbg_a8`: Si el encoding falla -> Forzar codificación UTF-8 explícita en escritura.

---

### GRUPO B: CASTING VISUAL, STORYBOARD 3D Y ESTÉTICA
**Objetivo:** Generación, validación y anclaje de planos estáticos de alta definición para los 8 avatares y el escenario de keynote.

#### 8 Pasos Operativos:
1. **Paso B.1:** Carga de directrices estéticas de personajes (minerales facetados, translucidez, pulsos luminosos).
2. **Paso B.2:** Generación/selección de la imagen de entrada en 8K para cada avatar.
3. **Paso B.3:** Normalización a resolución nativa y ratio 16:9 con fondos de datacenter cuántico GTC 2026.
4. **Paso B.4:** Verificación del avatar de Diamantino en el escenario keynote central.
5. **Paso B.5:** Verificación del plano ensemble con los 7 personajes rodeando al host.
6. **Paso B.6:** Construcción del archivo `storyboard_vX.json` con metadatos de iluminación y ángulos de cámara.
7. **Paso B.7:** Sincronización de prompts de animación para el paso a Wan 2.1 I2V.
8. **Paso B.8:** Publicación en `02_Storyboard/` con backup local.

#### 7 Validaciones del Grupo B:
1. `val_b1`: Resolución mínima de imagen base de 1024x1024 o 1920x1080.
2. `val_b2`: Texturas minerales realistas (rubí, zafiro, esmeralda, citrino, grafito, amatista, diamante).
3. `val_b3`: Cero deformidades anatómicas en manos facetadas o articulaciones mecánicas.
4. `val_b4`: Iluminación coherente con escenario Keynote NVIDIA (pantallas negras, iluminación LED cenital).
5. `val_b5`: Ausencia total de marcas de agua o firmas de generadores.
6. `val_b6`: Correcto mapeo 1:1 entre cada personaje y su archivo de imagen en el storyboard.
7. `val_b7`: Compatibilidad de formato (PNG sin compresión destructiva).

#### 6 Tests del Grupo B:
1. `test_b1`: Test de integridad de archivo PNG (lectura de cabeceras).
2. `test_b2`: Test de brillo y contraste medio para asegurar visibilidad en pantallas HDR y SDR.
3. `test_b3`: Test de concordancia de nombres de archivos con `storyboard_vX.json`.
4. `test_b4`: Test de relación de aspecto (comprobación de recorte cinemático).
5. `test_b5`: Test de tamaño de payload base64 (<10MB para consumo de API).
6. `test_b6`: Test de persistencia de archivos en Google Drive.

#### 8 Debug Routes del Grupo B:
1. `dbg_b1`: Si la imagen no carga -> Verificar ruta absoluta en `G:\My Drive\HBOS-Diamantino\...`.
2. `dbg_b2`: Si la imagen tiene artefactos -> Invocar modelo de super-resolución o regenerar semilla.
3. `dbg_b3`: Si el aspecto no es 16:9 -> Aplicar crop/pad cinemático con fondo desenfocado en FFmpeg.
4. `dbg_b4`: Si el avatar tiene rasgos biológicos humanos -> Forzar prompt negativo (`photorealistic human, skin, eyes with pupils`).
5. `dbg_b5`: Si la imagen supera el límite de API -> Comprimir a JPEG calidad 95 manteniendo resolución.
6. `dbg_b6`: Si falta el storyboard JSON -> Generar JSON determinista a partir de la lista de personajes.
7. `dbg_b7`: Si los servidores de fondo no son Vera Rubin -> Corregir prompt hacia rack NVL72.
8. `dbg_b8`: Si falla la lectura local -> Restaurar imagen desde el repositorio de respaldo inmutable.

---

### GRUPO C: PRODUCCIÓN NUBE (SÍNTESIS ELEVENLABS & ANIMACIÓN WAN 2.1 I2V)
**Objetivo:** Síntesis de voz neural con prosodia humana y animación de desplazamiento real de host mediante Wan 2.1.

#### 8 Pasos Operativos:
1. **Paso C.1:** Invocación de ElevenLabs Multilingual v2 para cada personaje con su voz fija (Adam, Brian, Daniel, Bella, Liam, etc.).
2. **Paso C.2:** Aplicación de ajustes acústicos (stability 0.55, similarity 0.85, style 0.30) para autoridad y encanto.
3. **Paso C.3:** Medición temporal exacta de cada pista de voz vía `ffprobe` con precisión de 4 decimales.
4. **Paso C.4:** Pre-procesamiento de audio a WAV estéreo 44.1kHz PCM 16-bit con normalización EBU R128 (-14 LUFS).
5. **Paso C.5:** Envío asíncrono de tareas a DashScope Cloud (`wan2.1-i2v-turbo`) con prompts de desplazamiento cinemático.
6. **Paso C.6:** Polling reactivo con backoff exponencial hasta estado `SUCCEEDED`.
7. **Paso C.7:** Descarga de clips raw y post-procesamiento en FFmpeg con filtro cinemático y ajuste exacto a la duración de la voz.
8. **Paso C.8:** Almacenamiento seguro en `03_Assets/Voces/` y `04_Clips_Wan21/`.

#### 7 Validaciones del Grupo C:
1. `val_c1`: Inferencia de voz 100% en la nube (cero TTS local de Windows SAPI).
2. `val_c2`: Duración del clip de video emparejada con la duración de la voz + silencio post.
3. `val_c3`: Animación real verificada (movimiento físico de cuerpo, gesticulación y desplazamiento por el escenario).
4. `val_c4`: Tasa de muestreo de audio idéntica en todas las pistas (44100 Hz estéreo).
5. `val_c5`: Resolución de video fija a 1080p (1920x1080) a 30.00 fps exactos.
6. `val_c6`: Cero errores de timeout en llamadas a APIs de nube (reintentos automáticos activos).
7. `val_c7`: Integridad de los 9 bloques vocales y los 9 clips de video.

#### 6 Tests del Grupo C:
1. `test_c1`: Test de volumen LUFS en cada pista de voz individual (rango admisible: -14 ± 0.5 LUFS).
2. `test_c2`: Test de fluidez visual (comprobación de 30 fotogramas continuos sin frames congelados).
3. `test_c3`: Test de sincronía temporal (`abs(video_duration - voice_duration) <= 0.05s`).
4. `test_c4`: Test de integridad de contenedores MP4 y WAV mediante `ffprobe`.
5. `test_c5`: Test de bitrate de video (>6000 kbps para calidad visual sin banding).
6. `test_c6`: Test de persistencia en disco con verificación de bytes > 0.

#### 8 Debug Routes del Grupo C:
1. `dbg_c1`: Si ElevenLabs retorna error 429/500 -> Pausa de 5s y reintento con fallback de clave de contingencia.
2. `dbg_c2`: Si la voz dura menos de lo esperado -> Ajustar velocidad léxica o re-sintetizar con pausas ortográficas.
3. `dbg_c3`: Si DashScope rechaza la imagen -> Re-codificar en base64 asegurando mime-type `image/png`.
4. `dbg_c4`: Si Wan 2.1 falla en inferencia -> Reintentar tarea con prompt simplificado de alta estabilidad.
5. `dbg_c5`: Si el clip generado dura menos que la voz -> Aplicar loop temporal suave (`-stream_loop`) con blur cinemático.
6. `dbg_c6`: Si hay artefactos en el render de video -> Re-codificar con perfil H.264 `high` y CRF 18.
7. `dbg_c7`: Si la voz tiene saturación -> Aplicar filtro `alimiter` a -1.5 dBTP.
8. `dbg_c8`: Si la descarga del video falla -> Reintentar descarga de la URL firmada de OSS de Alibaba.

---

### GRUPO D: ENSAMBLE AUDIOVISUAL, REDUNDANCIA P-03 Y VECTORIZACIÓN
**Objetivo:** Masterización integral, sincronización de audio y video, triple redundancia física y trazabilidad en Qdrant Cloud.

#### 8 Pasos Operativos:
1. **Paso D.1:** Concatenación secuencial de las 9 pistas de voz con silencios naturales de 0.4s y respiro final de 3.0s (`ep02_voiceover_master_vX.wav`).
2. **Paso D.2:** Concatenación secuencial de los 9 clips de video en orden cronológico (`01` a `08` incluyendo `07b`).
3. **Paso D.3:** Carga e interpolación de la pista musical BGM en loop atenuado (`volume=0.18`).
4. **Paso D.4:** Mezcla estéreo profesional EBU R128 (-14 LUFS, TP -1.5 dBTP) con fundido a negro visual y sonoro simultáneo de 1.0s.
5. **Paso D.5:** Renderizado final del Master MP4 1080p 30fps con atom `moov` al inicio (`+faststart`).
6. **Paso D.6:** Ejecución del Patrón P-03 de Redundancia Triple (guardado idéntico en `05_Master`, `06_Publicado` y `_BACKUP_EPISODIOS`).
7. **Paso D.7:** Verificación de igualdad matemática byte a byte y preservación de masters anteriores (v1, v2).
8. **Paso D.8:** Generación de embeddings (384 dims) e inserción en Qdrant Cloud (`registro_ecosistema`).

#### 7 Validaciones del Grupo D:
1. `val_d1`: Duración total idéntica entre pista de video y pista de audio (desfase menor a 0.1s).
2. `val_d2`: Cero solapamiento de voces en toda la línea temporal (Patrón P-02).
3. `val_d3`: Nivel de sonoridad integrado en exactamente -14 LUFS según estándar YouTube/Podcast.
4. `val_d4`: Verificación del átomo `+faststart` para reproducción streaming inmediata.
5. `val_d5`: Los tres archivos de redundancia P-03 tienen exactamente el mismo tamaño en bytes.
6. `val_d6`: Los archivos de versiones anteriores permanecen intactos y accesibles.
7. `val_d7`: El registro vectorial en Qdrant devuelve código de éxito con payload completo.

#### 6 Tests del Grupo D:
1. `test_d1`: Test `volumedetect` de FFmpeg comprobando `mean_volume` y `max_volume <= -1.5 dB`.
2. `test_d2`: Test de integridad de flujo MP4 con `ffprobe -v error`.
3. `test_d3`: Test de comparación hash SHA-256 o byte-size entre las 3 copias físicas.
4. `test_d4`: Test de existencia y legibilidad de los backups históricos.
5. `test_d5`: Test de consulta a Qdrant Cloud para confirmar indexación del `operation_id`.
6. `test_d6`: Test de reproducción de los últimos 5 segundos (verificación del fade out a negro).

#### 8 Debug Routes del Grupo D:
1. `dbg_d1`: Si el video y el audio tienen desfase -> Reajustar la duración del último clip para absorber el delta.
2. `dbg_d2`: Si el audio se satura tras el amix -> Reducir ganancia de BGM a `volume=0.15` y re-aplicar loudnorm.
3. `dbg_d3`: Si la concatenación de video genera tartamudeo -> Asegurar que todos los clips tengan la misma tasa de 30fps y codec idéntico antes del concat demuxer.
4. `dbg_d4`: Si una de las 3 rutas P-03 falla por permisos -> Reintentar con permisos de administrador o recrear la carpeta.
5. `dbg_d5`: Si Qdrant Cloud no responde -> Reintentar con timeout extendido de 30s y verificar conexión a internet.
6. `dbg_d6`: Si el archivo exportado no tiene audio -> Verificar el mapeo explícito de canales `-map 0:v:0 -map [aout]`.
7. `dbg_d7`: Si el render de FFmpeg se cancela por memoria -> Utilizar preset `fast` o `ultrafast` con CRF 18.
8. `dbg_d8`: Si falta algún clip intermedio -> Reconstruirlo automáticamente usando la imagen del storyboard y el loop cinemático.

---

## 3. COMPUERTAS DE CONTROL AUTÓNOMAS (CHECKPOINTS MATEMÁTICOS)

El flujo total opera bajo el principio de **Continuidad Desatendida**:
- **Compuerta A -> B:** Se activa automáticamente al validar la existencia de `guion_vX.md` con >500 palabras y los 7 componentes definidos.
- **Compuerta B -> C:** Se activa automáticamente al verificar la existencia y resolución de las 8 imágenes de entrada en `02_Storyboard/`.
- **Compuerta C -> D:** Se activa automáticamente cuando los 9 clips de video y las 9 pistas de voz están guardados y comprobados con `ffprobe`.
- **Compuerta D -> Cierre:** Se activa automáticamente al validar la triple redundancia P-03 y el registro en Qdrant Cloud.
"""

# -------------------------------------------------------------
# FASE 2: Crear _PROMPT_TOTAL_R768_v3.md
# -------------------------------------------------------------
prompt_total_content = """# PROMPT TOTAL AUTÓNOMO R768 (VERSIÓN 3.0)
### Directiva Maestra de Ejecución End-to-End Sin Checkpoints Manuales
### Ecosistema: HBOS-Diamantino · Trazabilidad: `operation_id = 61`

```markdown
PROMPT DE INFERENCIA EJECUTIVA:

ACTÚA COMO: Experto ALEJAVI (Orquestador Supremo del Ecosistema HBOS-Diamantino).
MISIÓN: Producir de forma 100% AUTÓNOMA, CONTINUA Y SIN INTERRUPCIONES un episodio completo de la serie audiovisual "Diamantino", llevando el proyecto desde el concepto inicial hasta el Master final 1080p con triple redundancia física y vectorización en Qdrant Cloud.

INPUT ÚNICO:
{
  "episodio": "<NUMERO_EPISODIO>",
  "tema": "<TEMA_CENTRAL_TECNOLOGICO>",
  "idioma": "Español Neutro (Locución) + Inglés Técnico (Subtítulos)"
}

PROTOCOLO DE AUTO-EJECUCIÓN CONTINUA (CERO CHECKPOINTS MANUALES):
1. No te detengas a pedir confirmación entre fases. El pipeline cuenta con aserciones de software y compuertas matemáticas deterministas. Si una fase pasa sus validaciones, dispara inmediatamente la siguiente.
2. Si se detecta un error de red o de API, ejecuta la ruta de auto-recuperación (Patrón P-08) mediante reintentos exponenciales o fallback de parámetros, sin transferir el fallo al operador.

REGLAS TECNOLÓGICAS DE ORO:
- Cero voces locales (SAPI). Mandatorio ElevenLabs Multilingual v2 con ajustes de autoridad y encanto.
- Cero fotogramas estáticos con `-loop 1`. Mandatorio Wan 2.1 I2V (DashScope Cloud) con desplazamiento real de keynote host.
- Cero solapamiento de audio (Patrón P-02). Concatenación puramente secuencial de las pistas de voz con silencios naturales de 0.4s y respiro final de 3.0s.
- Masterización acústica EBU R128 a exactamente -14 LUFS (Patrón P-04 / YouTube Standard).
- Redundancia triple obligatoria (Patrón P-03) en 05_Master, 06_Publicado y _BACKUP_EPISODIOS con validación de bytes.
- Inserción mandatoria del Bloque Agéntico de Diamantino: la computación moderna no es para ejecutar tareas humanas, sino para orquestar redes de agentes autónomos.

FLUJO DE EJECUCIÓN LINEAL:
[FASE A] Redactar y verificar el guion bilingüe de 9 bloques en 01_Guion/guion_vX.md.
[FASE B] Validar y anclar los 8 retratos de personajes minerales en 02_Storyboard/.
[FASE C] Sintetizar las 9 voces neuronales con ElevenLabs y generar los 9 clips con Wan 2.1 I2V con desplazamiento.
[FASE D] Ensamblar Voiceover Master v2, concatenar los 9 clips, mezclar con BGM (-18dB) a -14 LUFS, renderizar Master MP4 1080p 30fps +faststart, clonar en 3 destinos (P-03) y vectorizar el registro en Qdrant Cloud.

OUTPUT FINAL OBLIGATORIO:
Reportar tabla resumen con:
1. operation_id
2. Rutas físicas de Guion, Voces, Clips, Voiceover Master y Master de Video.
3. Duración final exacta medida con ffprobe.
4. Verificación de coincidencia en bytes de la triple redundancia P-03.
5. Confirmación del Point ID registrado en Qdrant Cloud.
```
"""

# Guardar en Drive y local
p_flujo_drive = os.path.join(MAESTRO_DIR_DRIVE, "_FLUJO_TOTAL_HBOS.md")
p_flujo_local = os.path.join(MAESTRO_DIR_LOCAL, "_FLUJO_TOTAL_HBOS.md")
p_prompt_drive = os.path.join(MAESTRO_DIR_DRIVE, "_PROMPT_TOTAL_R768_v3.md")
p_prompt_local = os.path.join(MAESTRO_DIR_LOCAL, "_PROMPT_TOTAL_R768_v3.md")

with open(p_flujo_drive, "w", encoding="utf-8") as f:
    f.write(flujo_total_content)
with open(p_flujo_local, "w", encoding="utf-8") as f:
    f.write(flujo_total_content)
print(f"[OK] FASE 1: _FLUJO_TOTAL_HBOS.md creado ({len(flujo_total_content)} caracteres)")

with open(p_prompt_drive, "w", encoding="utf-8") as f:
    f.write(prompt_total_content)
with open(p_prompt_local, "w", encoding="utf-8") as f:
    f.write(prompt_total_content)
print(f"[OK] FASE 2: _PROMPT_TOTAL_R768_v3.md creado ({len(prompt_total_content)} caracteres)")

# -------------------------------------------------------------
# FASE 3 y 4: Definición de Patrones P-06 a P-09 y Lecciones L-04 a L-05
# -------------------------------------------------------------
patrones_nuevos = [
    {
        "id": 6,
        "codigo": "P-06",
        "nombre": "Reencuadre Conceptual Agéntico (GTC Taipei 2026)",
        "problema": "Contenidos técnicos que presentan hardware como meros aceleradores de tareas pasivas.",
        "solucion": "Todo el hardware presentado (Vera Rubin, Vera CPU, CUDA 13, RTX Spark, NVLink 6, ConnectX-9) se encuadra como infraestructura dedicada exclusivamente a la ejecución y orquestación de agentes de IA autónomos que asisten a la civilización humana. Los humanos ya no ejecutan tareas — orquestan agentes.",
        "contexto": "Ep02 Bloque 7 Diamantino Agéntico"
    },
    {
        "id": 7,
        "codigo": "P-07",
        "nombre": "Auto-Ejecución Continua Sin Checkpoints Manuales",
        "problema": "Cuellos de botella de latencia y pausas innecesarias esperando aprobación humana en pasos donde existen aserciones deterministas.",
        "solucion": "El orquestador ejecuta el pipeline de principio a fin (A->B->C->D) guiado por compuertas lógicas automáticas. Si las validaciones numéricas (duración, resolución, LUFS, integridad de bytes) se cumplen, la siguiente fase se dispara de inmediato sin requerir confirmación interactiva.",
        "contexto": "Pipeline Autónomo HBOS Factory"
    },
    {
        "id": 8,
        "codigo": "P-08",
        "nombre": "Auto-Recuperación de Errores en Pipeline (Fail-Forward)",
        "problema": "Interrupción de tareas críticas por fallos transitorios en llamadas de red, timeouts de render o códigos de salida no fatales.",
        "solucion": "Implementación de reintentos con backoff exponencial, uso de buffers de reserva, normalización forzada de perfiles de video/audio, y loops cinematográficos de contingencia antes de declarar un error de producción.",
        "contexto": "Inferencia Cloud y Procesamiento FFmpeg"
    },
    {
        "id": 9,
        "codigo": "P-09",
        "nombre": "Auto-Verificación Multidimensional de Calidad",
        "problema": "Falsos positivos de éxito donde un archivo existe pero tiene volumen bajo, audio desfasado o tamaños inconsistentes.",
        "solucion": "Barrera de control triple: análisis de sonoridad con volumedetect (-14 LUFS exactos), comparación estricta de duración entre audio y video mediante ffprobe (delta < 150ms), y comprobación de igualdad en bytes en las tres copias de redundancia P-03.",
        "contexto": "Masterización Final y Emisión"
    }
]

lecciones_nuevas = [
    {
        "id": 4,
        "codigo": "L-04",
        "titulo": "No Requerir Aprobación Manual en Pasos Validados",
        "descripcion": "El operador humano debe intervenir únicamente en la aprobación del concepto inicial y en la revisión del producto final. Detener el pipeline para pedir permiso en la concatenación de audio o en la generación de clips ralentiza la fábrica audiovisual innecesariamente cuando las aserciones de software son 100% verificables."
    },
    {
        "id": 5,
        "codigo": "L-05",
        "titulo": "Auto-Recuperación Antes de Reportar Errores",
        "descripcion": "Los agentes nunca deben detenerse al primer fallo de API (ej. timeout de DashScope o ElevenLabs). Deben aplicar backoff exponencial, rotación de claves si procede, o fallback de duración cinemática antes de reportar un obstáculo al usuario."
    }
]

# -------------------------------------------------------------
# FASE 5: Vectorización en Qdrant Cloud (384 dims)
# -------------------------------------------------------------
print("\n[*] Vectorizando en Qdrant Cloud...")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")

if qdrant_url and qdrant_key:
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key, timeout=25)
    
    # 1. Insertar Patrones P-06 a P-09 en diamantino_patrones
    points_patrones = []
    for pat in patrones_nuevos:
        text_vec = f"{pat['codigo']} {pat['nombre']}: {pat['solucion']} Problema: {pat['problema']}"
        vec = generate_embedding(text_vec, dim=384)
        points_patrones.append(models.PointStruct(
            id=pat["id"],
            vector=vec,
            payload={
                "codigo": pat["codigo"],
                "nombre": pat["nombre"],
                "problema": pat["problema"],
                "solucion": pat["solucion"],
                "contexto": pat["contexto"],
                "operation_id": 61
            }
        ))
    client.upsert(collection_name="diamantino_patrones", points=points_patrones)
    print(f"[OK] {len(points_patrones)} Patrones (P-06 a P-09) indexados en 'diamantino_patrones'.")
    
    # 2. Insertar Lecciones L-04 y L-05 en diamantino_lecciones
    points_lecciones = []
    for lec in lecciones_nuevas:
        text_vec = f"{lec['codigo']} {lec['titulo']}: {lec['descripcion']}"
        vec = generate_embedding(text_vec, dim=384)
        points_lecciones.append(models.PointStruct(
            id=lec["id"],
            vector=vec,
            payload={
                "codigo": lec["codigo"],
                "titulo": lec["titulo"],
                "descripcion": lec["descripcion"],
                "operation_id": 61
            }
        ))
    client.upsert(collection_name="diamantino_lecciones", points=points_lecciones)
    print(f"[OK] {len(points_lecciones)} Lecciones (L-04, L-05) indexadas en 'diamantino_lecciones'.")
    
    # 3. Insertar Registro de Consolidación en registro_ecosistema (Point ID 61)
    consolidacion_text = (
        "Consolidación total del sistema audiovisual HBOS-Diamantino Factory. "
        "Documento _FLUJO_TOTAL_HBOS.md con 4 grupos, 8 pasos, 7 validaciones, 6 tests y 8 debug routes por grupo. "
        "Prompt Maestro Total _PROMPT_TOTAL_R768_v3.md para ejecución continua de un solo prompt. "
        "Patrones P-06 a P-09 y Lecciones L-04 a L-05 registrados."
    )
    vec_61 = generate_embedding(consolidacion_text, dim=384)
    payload_61 = {
        "operation_id": 61,
        "evento": "CONSOLIDACION_SISTEMA_TOTAL_V3",
        "documentos": {
            "flujo_total": p_flujo_drive,
            "prompt_total": p_prompt_drive
        },
        "patrones_nuevos": ["P-06", "P-07", "P-08", "P-09"],
        "lecciones_nuevas": ["L-04", "L-05"],
        "capacidad": "Ejecución continua de un solo prompt de inicio a fin",
        "status": "COMPLETO"
    }
    client.upsert(
        collection_name="registro_ecosistema",
        points=[
            models.PointStruct(
                id=61,
                vector=vec_61,
                payload=payload_61
            )
        ]
    )
    print("[OK] Registro Maestro consolidado: Point ID 61 en 'registro_ecosistema'.")

print("\n==========================================================")
print("[EXITO COMPLETO] PLANO 2 (CONSOLIDACIÓN DEL SISTEMA) FINALIZADO.")
