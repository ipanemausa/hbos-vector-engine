import hashlib
import json
import os
import shutil
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
WORKSPACE_RADAR = BASE_DIR / "workspace_radar"
DRIVE_MIRROR = Path(r"G:\My Drive\HBOS_Qdrant_Engine\workspace_radar")
LOG_PATH = BASE_DIR / "config" / "pipeline_execution_log.json"

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "hbos_universal_footprint"
VECTOR_DIM = 768

RECORDS = [
    {
        "filename": "ficha_eafit_2026-11-19.md",
        "agent_target": "entity_alignment",
        "entity": "Universidad EAFIT",
        "exposure_tier": "public_safe",
        "topic_tags": ["criterio_ia", "auditoria_salidas", "costo_cero", "semilleros", "intro_2_0"],
        "summary_1line": "Piloto acotado de auditoría y criterio crítico en IA con costo cero en licencias para Intro 2.0 y Semilleros EAFIT.",
        "content_markdown": """# Ficha de Alineación Institucional: Universidad EAFIT
**Frente:** Intro 2.0 y Semilleros de Investigación
**Identidad pública:** Guillermo Alonso Hoyos / Guía Hoy
**Enfoque:** Rigor metodológico, verificación de salidas y costo cero en licencias

## 1. Radiología de la Entidad en el Ecosistema Nacional
* **Reto estructural:** Integrar la inteligencia artificial en procesos de iniciación universitaria e investigación formativa sin comprometer el rigor académico, la trazabilidad de fuentes ni la capacidad crítica del estudiante.
* **Indicador clave:** Calidad verificable en productos de semilleros, retención temprana y pertinencia investigativa conectada con problemas reales del entorno.

## 2. Brecha que no cubre el mercado actual
* **Falta de protocolos de auditoría:** Las capacitaciones tradicionales enseñan a generar borradores rápidos, pero no entregan un método estructurado para detectar errores lógicos, sesgos o fuentes inventadas.
* **Fricción por licenciamiento:** Dependencia de suscripciones individuales pagas que fragmentan el acceso entre grupos y semilleros.

## 3. Piloto de Entrada (Costo Cero en Licencias)
Laboratorio acotado de máximo 2 sesiones sobre un caso real de Intro 2.0 o semillero de investigación, aplicando una matriz de auditoría paso a paso para validar hipótesis y salidas asistidas por IA con costo cero en licencias.
""",
    },
    {
        "filename": "ficha_ucc_mauricio_2026-11-19.md",
        "agent_target": "entity_alignment",
        "entity": "UCC - Mauricio Morales Saldarriaga",
        "exposure_tier": "public_safe",
        "topic_tags": ["criterio_ia", "auditoria_salidas", "costo_cero", "competencias_academicas"],
        "summary_1line": "Piloto de auditoría de salidas de IA y validación de criterio en proyectos académicos con costo cero en licencias para UCC.",
        "content_markdown": """# Ficha de Alineación Institucional: Universidad Cooperativa de Colombia (UCC)
**Interlocutor de referencia:** Mauricio Morales Saldarriaga
**Identidad pública:** Guillermo Alonso Hoyos / Guía Hoy
**Enfoque:** Competencias verificables, auditoría humana y costo cero en licencias

## 1. Radiología de la Entidad en el Ecosistema Nacional
* **Reto estructural:** Escalar la adopción práctica de herramientas digitales e inteligencia artificial dentro de un modelo multicampus y de gobernanza cooperativa, equilibrando cobertura amplia con rigor académico y formación por competencias.
* **Indicador clave:** Tasa de graduación oportuna, cumplimiento verificable de competencias en aula e índice de inserción laboral y pertinencia profesional en el tejido productivo regional y nacional.

## 2. Brecha que no cubre el mercado actual
* **Barrera presupuestal:** Las licencias propietarias por usuario resultan insostenibles para escalar masivamente entre estudiantes y docentes.
* **Ausencia de auditoría académica:** Los cursos convencionales no entregan un método práctico para detectar errores de máquina y validar el criterio humano en entregas asistidas por IA.
* **Desconexión operativa:** Exceso de teoría desconectada de proyectos integradores, trabajos de grado y semilleros reales.

## 3. Piloto de Entrada (Costo Cero en Licencias)
Protocolo práctico de auditoría y verificación de salidas de IA en proyectos integradores o semilleros de investigación de la UCC, ejecutado en máximo 2 sesiones sobre un caso real existente y sin requerir licencias pagas.
""",
    },
    {
        "filename": "ficha_ruta_n_2026-11-19.md",
        "agent_target": "entity_alignment",
        "entity": "Ruta N Medellín",
        "exposure_tier": "public_safe",
        "topic_tags": ["criterio_ia", "auditoria_salidas", "costo_cero", "productividad_pymes"],
        "summary_1line": "Piloto verificable de adopción de IA con criterio y costo cero en licencias para Ruta N Medellín.",
        "content_markdown": """# Ficha de Alineación Institucional: Ruta N Medellín
**Frente:** Ecosistema Público, Startups y Mipymes
**Identidad pública:** Guillermo Alonso Hoyos / Guía Hoy
**Enfoque:** Productividad medible, verificación operativa y costo cero en licencias

## 1. Radiología de la Entidad en el Ecosistema Nacional
* **Reto estructural:** Acelerar la transformación tecnológica y la competitividad de las mipymes y emprendimientos del ecosistema antioqueño, superando la fragmentación y la baja adopción efectiva de tecnologías emergentes.
* **Indicador clave:** Tasa de supervivencia, escala y crecimiento de las empresas acompañadas, medido por generación de ingresos y productividad operativa.

## 2. Brecha que no cubre el mercado actual
* **Costo de licenciamiento:** Herramientas propietarias con tarifas recurrentes en dólares que frenan la adopción en mipymes y emprendimientos tempranos.
* **Falta de método de verificación:** Riesgo operativo al llevar salidas no auditadas directamente a clientes o procesos internos.
* **Teoría sin aterrizaje:** Contenidos genéricos desconectados de los flujos diarios de venta, operación y control.

## 3. Piloto de Entrada (Costo Cero en Licencias)
Laboratorio práctico de verificación de IA de costo cero para emprendedores del ecosistema Ruta N, centrado en auditar y optimizar procesos reales (atención comercial, análisis operativo o documentación) en máximo 2 sesiones con métricas verificables.
""",
    },
    {
        "filename": "ficha_comfama_2026-11-19.md",
        "agent_target": "entity_alignment",
        "entity": "Comfama Antioquia",
        "exposure_tier": "public_safe",
        "topic_tags": ["criterio_ia", "auditoria_salidas", "costo_cero", "empleabilidad_pymes"],
        "summary_1line": "Taller práctico de adopción de IA con criterio humano y costo cero en licencias para empresas afiliadas a Comfama Antioquia.",
        "content_markdown": """# Ficha de Alineación Institucional: Comfama Antioquia
**Frente:** Empleabilidad, Educación y Empresas Afiliadas
**Identidad pública:** Guillermo Alonso Hoyos / Guía Hoy
**Enfoque:** Criterio humano, productividad sostenible y costo cero en licencias

## 1. Radiología de la Entidad en el Ecosistema Nacional
* **Reto estructural:** Alinear la formación del talento y la productividad de las empresas afiliadas con las demandas reales del mercado regional, impulsando un desarrollo competitivo y sostenible en Antioquia.
* **Indicador clave:** Tasa de empleabilidad de beneficiarios capacitados e índice de productividad y retención del talento en las empresas afiliadas.

## 2. Brecha que no cubre el mercado actual
* **Costo de herramientas propietarias:** Inviable para presupuestos operativos de pequeñas y medianas empresas afiliadas.
* **Pérdida de criterio humano:** Dependencia acrítica de respuestas automatizadas sin protocolos internos de revisión.
* **Desconexión cotidiana:** Formación abstracta alejada de los procesos administrativos y productivos diarios.

## 3. Piloto de Entrada (Costo Cero en Licencias)
Taller práctico de adopción de IA de costo cero para equipos administrativos y operativos de empresas afiliadas, aplicando un protocolo de auditoría y validación humana sobre procesos reales en máximo 2 sesiones conjuntas.
""",
    },
    {
        "filename": "guion_pilar_proyectos_ia_verificabilidad_2026-11-19.md",
        "agent_target": "guiahoy_studio",
        "entity": "GENERAL",
        "exposure_tier": "public_safe",
        "topic_tags": [
            "metodo_proyectos",
            "criterio_ia",
            "auditoria_salidas",
            "costo_cero",
            "guiahoy",
            "ecosistema_colaborativo",
        ],
        "summary_1line": "Guion metodológico de Guía Hoy de 7 minutos para generar proyectos con IA mediante un proceso de 4 pasos auditables, verificables y con costo cero en licencias.",
        "content_markdown": """# Guion Pilar Guía Hoy: Proyectos con IA — De la Velocidad a la Verificabilidad
**Identidad pública:** Guillermo Alonso Hoyos / Guía Hoy
**Duración objetivo:** 7 minutos
**Enfoque:** Método universal auditable, costo cero en licencias y colaboración abierta por ecosistema (Educación, Micro y Macro)

## 1. Título y Gancho Inicial (0:00 – 0:30)
> "Hoy, generar un proyecto con inteligencia artificial es rápido, pero extremadamente frágil. Sin un método de auditoría estricto, lo que se obtiene es una ilusión de avance: propuestas que colapsan en la primera revisión, cálculos con errores lógicos y planes desconectados de los indicadores reales.
>
> Si usted lidera una empresa, una institución o un equipo académico, sabe que la velocidad sin criterio es un riesgo operativo. En los próximos 7 minutos le mostraré qué está fallando hoy, qué proponemos, qué solucionamos y cómo se genera cualquier proyecto con un método de 4 pasos auditables y costo cero en licencias."

## 2. Estructura del Episodio

### Bloque 1: Qué está fallando hoy (0:30 – 2:00)
* **Narración:** El error de confiar ciegamente en la primera respuesta rápida. Los equipos usan herramientas para redactar propuestas, informes o procesos, pero al no existir un marco de validación previo, los resultados carecen de trazabilidad y fracasan frente a la evaluación de directivos, comités o clientes.
* **En pantalla:** Pantalla dividida con el avatar de **Guillermo Alonso Hoyos** y mascota guía señalando con láser. A la izquierda, un texto generado a toda velocidad; a la derecha, una alerta de *"Falta de auditoría / Sin trazabilidad"*.

### Bloque 2: Qué proponemos (2:00 – 3:30)
* **Narración:** Pasar de la IA como caja negra a la IA como motor de ejecución auditada. Proponemos un marco donde la herramienta acelera la estructura, pero el ser humano aplica el criterio gerencial, ético y técnico en cada punto crítico, operando con recursos de costo cero para eliminar barreras presupuestales.
* **En pantalla:** Diagrama limpio de tres nodos: `Generación controlada` -> `Puerta de Auditoría Humana (Criterio)` -> `Activo Verificable`.

### Bloque 3: Qué solucionamos y cómo colabora con el ecosistema (3:30 – 5:00)
* **Narración:** Eliminamos tres fugas críticas: el retrabajo por errores ocultos, la pérdida de rigor institucional y el gasto innecesario en licencias pagas. Además, cada entidad o empresa que aplica este estándar resuelve su propia coyuntura y aporta un caso real probado que fortalece el ecosistema en tres niveles: rigor en educación, productividad en la micro y pequeña empresa, y progreso colectivo a escala regional y nacional.
* **En pantalla:** Lista de verificación dinámica: `[X] Trazabilidad verificable` | `[X] Costo cero en licencias` | `[X] Rigor aplicable en educación y empresa` | `[X] Impacto colaborativo de ecosistema`.

### Bloque 4: Cómo se genera cualquier proyecto en 4 pasos auditables (5:00 – 6:30)
* **Narración:**
  1. **Paso 1 — Definición acotada del problema:** fijar el objetivo real y los criterios de éxito medibles antes de abrir cualquier herramienta.
  2. **Paso 2 — Ejecución modular con límites estrictos:** dividir el proyecto en bloques pequeños con reglas claras para evitar desviaciones.
  3. **Paso 3 — Auditoría independiente de salidas:** verificar fuentes, coherencia lógica y cumplimiento de reglas; lo que no pasa revisión se corrige o se descarta en el acto.
  4. **Paso 4 — Validación humana y entrega tangible:** aprobar el resultado bajo un estándar claro y convertirlo en un activo operativo reproducible.
* **En pantalla:** 4 columnas numeradas (1 a 4): `Definición` -> `Ejecución acotada` -> `Auditoría` -> `Activo sellado`.

## 3. Cierre Sobrio de Autoridad (6:30 – 7:00)
> "La inteligencia artificial no va a reemplazar el criterio humano; va a desplazar a quienes no auditen sus propios procesos. El futuro de cualquier proyecto no se gana con respuestas rápidas, sino con resultados verificables que resuelven problemas reales y elevan el nivel de todo el entorno.
>
> Si desea aplicar este método sobre una coyuntura concreta de su institución o empresa y sumar un caso probado a esta red de aprendizaje abierto, conversemos.
>
> **Guillermo Alonso Hoyos / Guía Hoy.**"
""",
    },
]


def deterministic_embedding(text: str, dim: int = VECTOR_DIM) -> list[float]:
    values = []
    counter = 0
    raw = text.encode("utf-8")
    while len(values) < dim:
        digest = hashlib.sha256(raw + counter.to_bytes(4, "little")).digest()
        for i in range(0, len(digest), 4):
            if len(values) >= dim:
                break
            chunk = int.from_bytes(digest[i : i + 4], "little", signed=False)
            values.append((chunk / 2147483647.5) - 1.0)
        counter += 1
    norm = sum(v * v for v in values) ** 0.5 or 1.0
    return [round(v / norm, 6) for v in values]


def qdrant_request(method: str, path: str, payload: dict | None = None) -> dict:
    url = f"{QDRANT_URL}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ensure_collection() -> None:
    try:
        qdrant_request("GET", f"/collections/{COLLECTION_NAME}")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            qdrant_request(
                "PUT",
                f"/collections/{COLLECTION_NAME}",
                {"vectors": {"size": VECTOR_DIM, "distance": "Cosine"}},
            )
        else:
            raise


def append_execution_log(entry: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOG_PATH.exists():
        try:
            existing = json.loads(LOG_PATH.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = [existing]
        except json.JSONDecodeError:
            existing = []
    else:
        existing = []
    existing.append(entry)
    LOG_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    WORKSPACE_RADAR.mkdir(parents=True, exist_ok=True)
    drive_available = DRIVE_MIRROR.parent.exists()
    if drive_available:
        DRIVE_MIRROR.mkdir(parents=True, exist_ok=True)

    ensure_collection()
    points = []
    committed_files = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for item in RECORDS:
        canonical_file = WORKSPACE_RADAR / item["filename"]
        canonical_file.write_text(item["content_markdown"], encoding="utf-8")

        mirror_file = DRIVE_MIRROR / item["filename"]
        if drive_available:
            shutil.copy2(canonical_file, mirror_file)

        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, str(canonical_file)))
        embed_source = f"{item['entity']} | {item['summary_1line']} | {' '.join(item['topic_tags'])}"
        points.append(
            {
                "id": point_id,
                "vector": deterministic_embedding(embed_source, VECTOR_DIM),
                "payload": {
                    "status": "COMMITTED",
                    "agent_target": item["agent_target"],
                    "canonical_path": str(canonical_file),
                    "drive_mirror_path": str(mirror_file),
                    "entity": item["entity"],
                    "exposure_tier": item["exposure_tier"],
                    "topic_tags": item["topic_tags"],
                    "summary_1line": item["summary_1line"],
                    "content_markdown": item["content_markdown"],
                    "committed_at": now_iso,
                },
            }
        )
        committed_files.append(str(canonical_file))

    upsert_res = qdrant_request(
        "PUT",
        f"/collections/{COLLECTION_NAME}/points?wait=true",
        {"points": points},
    )

    log_entry = {
        "timestamp": now_iso,
        "pipeline": "hbos_universal_footprint_batch_commit",
        "collection": COLLECTION_NAME,
        "vector_dim": VECTOR_DIM,
        "records_committed": len(points),
        "drive_synced": drive_available,
        "files": committed_files,
        "qdrant_status": upsert_res.get("status", "unknown"),
    }
    append_execution_log(log_entry)
    print(json.dumps(log_entry, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
