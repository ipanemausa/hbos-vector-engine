# PROTOCOLO MAESTRO DE BÚSQUEDA EN CASCADA (HBOS R768)
**Resolución Determinista: Local vs Drive vs Sandbox vs Qdrant**  
**Documento Canónico de Arquitectura y Gobernanza**  
**operation_id:** 174 | **Versión:** 1.0.0 | **Ecosistema:** HBOS-Diamantino

---

## 1. OBJETIVO Y PRINCIPIO ARQUITECTÓNICO

Eliminar de raíz la ambigüedad operativa de Antigravity y de los agentes de IA al buscar herramientas, código fuente, assets audiovisuales, ejecutables o memoria histórica.

> **Principio Canónico ALEJAVI:**  
> Ningún agente debe adivinar ni improvisar la ubicación de un componente. La búsqueda se ejecuta siempre en orden estricto de cascada (Paso 1 a 5), consultando el directorio canónico indexado en la colección vectorial `hbos_directorio`.

---

## 2. FLUJO DE BÚSQUEDA EN CASCADA DE 5 PASOS

```mermaid
flowchart TD
    A[Inicio Requerimiento] --> B[Paso 1: Workspace Local]
    B -- ¿Existe? -->|SÍ| C[Ejecutar en Local]
    B -- NO --> D[Paso 2: Google Drive Persistente]
    D -- ¿Existe? -->|SÍ| E[Consumir Stream / Sync]
    D -- NO --> F[Paso 3: HBOS SANDBOX Aislado]
    F -- ¿Existe? -->|SÍ| G[Ejecutar en Sandbox Desacoplado]
    F -- NO --> H[Paso 4: Qdrant Cloud Memoria]
    H -- ¿Existe? -->|SÍ| I[Recuperar Payload / Vector RAG]
    H -- NO --> J[Paso 5: Reportar Incidencia Canónica]
```

### PASO 1 — Espacio Local de Trabajo (Workspace)
- **Ámbito:** Código fuente activo, scripts operacionales, herramientas de renderizado y configuración directa.
- **Ruta Raíz:** `c:\Users\ipane\hbos-deploy\hbos-vector-engine\`
- **Qué buscar aquí:**
  - Scripts Python (`execute_*.py`, `hbos_estado.py`, `hbos_resumen_diario.py`).
  - Archivos maestros de arquitectura (`_MAESTRO\*.md`).
  - Variables de entorno locales y credenciales cifradas (`.env.local`).
- **Criterio de Éxito:** Si el archivo o ejecutable existe en el workspace, se usa directamente.

### PASO 2 — Google Drive Persistente (Assets & Renders)
- **Ámbito:** Assets pesados, renders maestros finales, backups globales y kits audiovisuales.
- **Ruta Raíz Montada:** `G:\My Drive\HBOS-Diamantino\`
- **Qué buscar aquí:**
  - Videos finales multiformato de episodios (`diamantino\ep02\render\`, `diamantino\ep03\render\`).
  - Voiceovers WAV / MP3 generados por TTS (`diamantino\ep02\audio\`).
  - Pistas BGM maestras (`diamantino\ep01\prompts\music_prompt.txt`).
- **Mecanismo de Acceso:** Path virtual montado o MCP `gdrive`.

### PASO 3 — HBOS SANDBOX Aislado (Apps Externas & Venvs)
- **Ámbito:** Ejecutables binarios externos, herramientas de terceros y entornos virtuales aislados para evitar la contaminación del workspace principal.
- **Ruta Raíz:** `G:\My Drive\HBOS-Diamantino\_SANDBOX\`
- **Qué buscar aquí:**
  - Servidor local portable FreeLLMAPI: `_SANDBOX\FreeLLMAPI\app\FreeLLMAPI.exe`.
  - Entorno virtual de Playwright: `_SANDBOX\Playwright\.venv\`.
  - Servidores MCP aislados: `_SANDBOX\MCPs\`.
- **Criterio de Ejecución:** Siempre desacoplado (`IsDaemon: true` o subprocesos sin bloquear).

### PASO 4 — Qdrant Cloud (Memoria Vectorial & Directorio)
- **Ámbito:** Conocimiento consolidado, lecciones aprendidas, catálogo de patrones y resolución de rutas dinámicas.
- **Endpoint:** Cluster Cloud `https://d03a1188-3ca9-48fb-b856-fbf377f0a8fc.us-east4-0.gcp.cloud.qdrant.io`
- **Colecciones a Consultar:**
  1. `hbos_directorio`: Mapa canónico de componentes y puertos (ID 1 a 7).
  2. `diamantino_patrones`: Gobernanza técnica activa (P-01 a P-54).
  3. `diamantino_lecciones`: Heurísticas y mitigación de errores (L-01 a L-40).
  4. `diamantino_agentes`: Registro de agentes internos y externos (ID 1 a 10).
  5. `hbos_estado`: Estado consolidado del ecosistema (ID=1).

### PASO 5 — Reporte de Falla / Ausencia Canónica
- Si un recurso no se localiza tras agotar los 4 niveles previos:
  - **PROHIBIDO:** Inventar rutas, asumir defaults inexistentes o descargar binarios no autorizados.
  - **OBLIGATORIO:** Registrar el fallo con `operation_id`, detallar los 4 niveles verificados e informar al usuario solicitando confirmación.

---

## 3. MATRIZ CANÓNICA DE RESOLUCIÓN DE COMPONENTES

| Componente | Nivel Primario | Ruta / Identificador | Mecanismo de Invocación |
| :--- | :---: | :--- | :--- |
| **FreeLLMAPI** | Paso 3 (Sandbox) / Paso 4 | `_SANDBOX\FreeLLMAPI\app\FreeLLMAPI.exe` | MCP `hbos-freellmapi` (`http://localhost:3001`) |
| **Playwright Engine** | Paso 3 (Sandbox) | `_SANDBOX\Playwright\.venv\Scripts\python.exe` | Scripts `map_app.py`, `navigate_app.py` |
| **Estado HBOS** | Paso 1 / Paso 4 | `hbos_estado.py` / Qdrant `hbos_estado` | `python hbos_estado.py` (< 1 seg) |
| **Resumen Diario** | Paso 1 / Paso 2 | `_ESTADO_DIA.md`, `_PENDIENTES.md`, `_HECHO.md` | `python hbos_resumen_diario.py` (Triple Redundancia) |
| **Episodios Masters**| Paso 2 (Drive) | `G:\My Drive\HBOS-Diamantino\diamantino\` | Streams y backups verificados SHA256 |
| **Directorio HBOS** | Paso 4 (Qdrant) | Colección `hbos_directorio` (IDs 1-7) | Python `qdrant_client` |

---

## 4. GOBERNANZA Y REGLA DE ORO

> [!IMPORTANT]
> Todo nuevo componente, script o asset creado en el ecosistema debe ser inmediatamente clasificado dentro de este protocolo de 5 pasos e indexado en la colección `hbos_directorio` en Qdrant con su respectivo `operation_id`.
