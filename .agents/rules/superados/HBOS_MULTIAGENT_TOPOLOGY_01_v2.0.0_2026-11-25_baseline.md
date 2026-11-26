# ESTÁNDAR DEFINITIVO HBOS QUADRANT v2.0: `HBOS_MULTIAGENT_TOPOLOGY_01`

- **Identificador Canónico:** `HBOS_MULTIAGENT_TOPOLOGY_01`
- **Versión:** `v2.0` (Red Multi-Agente Completa — Todos los Agentes, MCPs y Skills del Entorno Unificados)
- **Ecosistema:** HBOS Quadrant · Antigravity IDE (`c:\Users\ipane\hbos-deploy\hbos-vector-engine`)
- **Principio Rector:** Ejecución nativa local sin Docker, cero costo recurrente (`0 SaaS Tax`), persistencia limpia en `G:\My Drive` y **cero `PASS` simulados**.

---

## 1. Núcleo Productivo (5 Agentes Core) + 3 Capas Transversales Integradas

Ningún agente, servidor MCP o capacidad del entorno queda aislado fuera de la red:

| Nodo / Rol | Agentes, MCPs y Skills Integrados | Responsabilidad en el Sistema | Gate Ligero de Salida |
|---|---|---|---|
| **1 · Pre-Flight & Guardrails** | `Fase 0` + MCP **`gdrive`** (fallback nativo a `rclone gdrive:` y `G:\My Drive` montado) | Verificar binarios (`python`, `ffmpeg`, `ffprobe`), encoders, Qdrant, rutas en Drive y bloquear residuos previos (MIT / pistas viejas). | Existencia física, peso `> 0`, duración de audio real (`debug_fase0.json`). |
| **2 · Semántico 768D & Memoria Canónica** | `Fase 1` + `all-mpnet-base-v2` (768D local) + `Qdrant localhost:6333` + MCP **`hbos-chat-context`** (`get_canon`, `get_state`, `get_pending`, `get_code`) | Factorizar guion/activos en **768D exactos**, recuperar estado canónico entre sesiones, indexar Qdrant y emitir timeline sin huecos. | `dim == 768`, `0` NaN/Inf, cobertura exacta `0 -> N` frames (`timeline_768.json`). |
| **3 · Director de Arte 3D & Activos** | Subagente **`image-generator`** (fan-out paralelo) + MCPs **`hbos-diamantino` / `diamantini-imagenes`** + skill **`rea-hiperframes-fish-mass-producer`** | Generar escenas 3D limpias `16:9` (cero texto/marcas), gestionar activos gráficos de Diamantino, recortar *letterbox* y despejar tercio derecho. | `10/10` escenas `1920x1080`, `0` texto residual (`scenes_manifest.json`). |
| **4 · Motor Avatar, Audio & Render 60fps** | Fases 2–3 OpenCV C++ `uint8` + **`guiahoy-video-producer`** + MCP **`open-weight-models`** (`generate_jam_audio`, `invoke_pinokio_flow`) + **`runpod` / `runpod-mcp` / `runpodctl` / `flash`** | Usar exclusivamente poses RGBA oficiales con sonrisa natural en **`G:\My Drive\AVATAR_OFICIAL_GUILLERMO_TRANSPARENCIAS\`** (cero clips viejos distorsionados ni `jaw_shift`), calcular envolvente vocal `60 fps` y animar labios reales (`Wav2Lip` / `LatentSync`) sobre escena 3D despejada. | `0` ventanas congeladas `>0.5s`, fidelidad facial intacta, conteo exacto de frames y clips de control. |
| **5 · Auditor QA Multimodal & Entrega** | Gate 3→4 (visión sobre PNGs QA) + `ffprobe`/`blackdetect`/`silencedetect`/continuidad + **`generative_ui`** + `RULE_AUTO_LAUNCH_01` | Validar visualmente que no haya solapamiento/texto residual, verificar sincronía A/V exacta (`± 0.05 s`), sellar `SHA-256` en Qdrant y abrir entregable. | Video == Audio (`± 0.05 s`), `0` negros/freezes, `REPORTE_AUDITORIA_FINAL.json`. |
| **6 · Navegación Web & Captura Autenticada** | Subagente **`browser`** (Chrome DevTools) | Operar interfaces web autenticadas (Google Drive web, Muse, HuggingFace Spaces, pasarelas de login OAuth) cuando una API MCP falla o requiere UI. | Captura o artefacto descargado verificado en almacenamiento local/Drive. |
| **7 · Investigación Profunda & Automatización** | Subagentes **`research`** y **`self`** + **`run_workflow`** (Python fan-out) + **`reverse-engineer-anything`** + **`automation`** (`/schedule`) + **`conversations`** | Descomponer auditorías masivas de código, ingeniería inversa, flujos programados recurrentes y gestión de sesiones sin saturar el contexto principal. | Resumen trazable o artefacto verificado sin pollings bloqueantes. |
| **8 · Consejo Multi-Modelo & Arbitraje 429** | MCP **`hbos-freellmapi`** (`openai/gpt-oss-120b` Groq/CF, `gemini-2.5-flash`, `codestral-latest`, `command-a-03-2025`, `tts`) + **`open-weight-models`** (`query_gemini_free`, `query_deepseek_r1`, `query_groq_coder`, `query_qwen3_max`, `query_kimi`) + **`ollama`** (`localhost:11434` offline) + **`mumo`** (deliberación cruzada GPT/Claude/Gemini/Grok/DeepSeek) | Aportar segunda opinión cruzada entre familias de modelos (auditando guiones, contratos JSON y código FFmpeg) y relevar automáticamente cualquier límite `HTTP 429`. | Dictamen verificado o conmutación registrada en `fallback_used`. |

---

## 2. Contrato Ligero de Handoff (JSON Schema Estándar)

Todo relevo entre nodos emite un manifiesto compacto sin burocracia:

```json
{
  "agent_id": "nodo_X",
  "phase": "FASE_X",
  "status": "PASS | FAIL | BLOCKED",
  "cause": null,
  "fallback_used": "none | local_alt | mcp_open_weight | browser_ui | runpod_flash | mumo_panel",
  "verified_metrics": {
    "duration_sec": 414.276,
    "frames": 24856,
    "resolution": "1920x1080",
    "fps": 60,
    "embedding_dim": 768
  },
  "artifacts": ["ruta/exacta/en/G_My_Drive"]
}
```

* Regla de transición: Si `status != "PASS"`, el siguiente nodo **no arranca** y aplica la matriz de arbitraje.

---

## 3. Blindaje de Handoffs y Matriz de Arbitraje (`HTTP 429` / Fallos / `exit != 0`)

PROHIBIDO simular `PASS`, ocultar códigos de error o quedarse colgado. Ante `RESOURCE_EXHAUSTED` (`HTTP 429`), fallos OAuth (`invalid_grant`) o salidas `!= 0`:

1. **Nivel 1 — Fallback Nativo Local:** Conmutar a herramienta local determinista (`rclone gdrive:` si falla MCP `gdrive`; `all-mpnet-base-v2` local para 768D; `libx264` si QSV deriva; `ollama` offline si cae red; OpenCV/Pillow local para limpieza visual).
2. **Nivel 2 — Escalamiento Multi-Modelo `0 SaaS Tax`:** Conmutar entre **`hbos-freellmapi`** (`openai/gpt-oss-120b` en Groq o Cloudflare, `gemini-2.5-flash`, `codestral-latest`) y **`open-weight-models`** (`query_deepseek_r1`, `query_groq_coder`, `query_qwen3_max`, `query_gemini_free`), o abrir panel **`mumo`** cuando el operador requiera deliberación multi-laboratorio.
3. **Nivel 3 — Cómputo Remoto GPU (`runpod` / `flash`) o UI (`browser`):** Descargar cargas GPU pesadas a Runpod con persistencia `rclone` hacia Drive, o delegar al subagente `browser` sesiones que exijan autenticación interactiva.
4. **Nivel 4 — Cierre Explícito `FAIL` / `BLOCKED`:** Si ningún nivel resuelve el bloqueo (ej. OAuth pendiente del usuario o ausencia de insumo irreemplazable en Fase 0), detener con `"status": "BLOCKED"` o `"FAIL"` reportando la **causa exacta**.

---

## 4. Cero Setbacks, Carril Separado y `0 SaaS Tax`

* **Protección de corridas validadas:** Quedan protegidos contra ediciones en caliente los activos sellados (`414.276 s` / `24,856–24,857` cuadros a `60 fps`, `escenas_3d_clean/`, `Qdrant` y entregables en `G:\My Drive`).
* **Carril aislado para mejoras:** Toda idea nueva o refactorización se prueba en carril aislado / siguiente ciclo sin alterar una corrida en progreso.
* **Nativo local sin Docker:** Windows 11 + PowerShell 7 + Python + FFmpeg + Qdrant local + `G:\My Drive` (`0 SaaS Tax`).
