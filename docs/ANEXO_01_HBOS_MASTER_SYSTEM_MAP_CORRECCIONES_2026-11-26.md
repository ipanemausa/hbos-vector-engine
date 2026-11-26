# ANEXO 01 · CORRECCIONES AL MAPA MAESTRO Y CANON HBOS (2026-11-26)

- **Identificador:** `ANEXO_01_HBOS_MASTER_SYSTEM_MAP_CORRECCIONES_2026-11-26`
- **Naturaleza:** Anexo aditivo y reversible (Regla F2 / Addendum 2026-11-26). Los 4 documentos base (`HBOS_MULTIAGENT_TOPOLOGY_01.md`, `HBOS_PRODUCTION_DAG_01.md`, `HBOS_MASTER_SYSTEM_MAP.md`, `HBOS_MASTER_SYSTEM_MAP.html`) permanecen **intactos (solo lectura)**; sus copias de respaldo de línea base reposan en `docs/superados/` y `.agents/rules/superados/`.
- **Fuente Única de Verdad (F1):** **HBOS Quadrant Vector Engine (Vercel + Qdrant Cloud)**. Todo estado, flujo, ledger de videos e índice de archivos vive en Quadrant Cloud (`registro_ecosistema_r768`, `canon_video_hbos_r768`). `MAPA-VIVO\mapa.html` es una vista generada automáticamente desde Quadrant, nunca editada a mano.

---

## 1. Corrección de Espacios Vectoriales Qdrant (768d Canónico)

- **Canon (F4):** El modelo canónico de embeddings es **`gemini-embedding-2`** vía API/Gateway con **`"dimensions": 768`** (métrica `Cosine`). `all-mpnet-base-v2` local NO es el embedder canónico.
- **Discrepancia Medida (`DISC-01`):**
  - *Documento Base (`HBOS_MASTER_SYSTEM_MAP.md` §1):* lista `casos_uso_hbos` en `384d` y mantiene colecciones paralelas `384d`.
  - *Instrucción v2:* indica que `casos_uso_hbos` fue unificado a `768d` (`1,064` puntos el 2026-11-21).
  - *Medición en vivo (2026-11-26, Qdrant Cloud):* `casos_uso_hbos` en el cluster Cloud responde con `dim=384`, `pts=70` (y `omnirouter_hbos.js` línea 103 define `VECTOR_SIZE = 384`).
  - *Acción Aditiva:* Las nuevas colecciones canónicas de trazabilidad y video se operan en **768d Cosine (`gemini-embedding-2`)** en Qdrant Cloud: `registro_ecosistema_r768` y `canon_video_hbos_r768`. La discrepancia queda registrada en Quadrant (`DISC-01`) hasta migración explícita y verificada de `casos_uso_hbos` en Cloud.

---

## 2. Estado Real de Componentes con Sonda en Vivo (F3 · 2026-11-26)

Regla F3: ningún componente puede declararse `ACTIVO` sin sonda en vivo del mismo día (timestamp ISO + respuesta). Lo no sondeado permanece como `POR CONSTATAR`.

| Componente | Lugar (F10) | Estado | Timestamp Sonda | Evidencia Medida |
| :--- | :---: | :---: | :--- | :--- |
| **HBOS Vector Engine (Vercel)** | `CLOUD` | **ACTIVO** | `2026-11-26T06:41:09-05:00` | `GET /v1/health` -> HTTP `200`, `HEALTHY`, `47` colecciones |
| **Qdrant Cloud Cluster** | `CLOUD` | **ACTIVO** | `2026-11-26T06:41:09-05:00` | `GET /collections` -> HTTP `200`, `768d` ledger activo |
| **gemini-embedding-2 (768d)** | `CLOUD` | **ACTIVO** | `2026-11-26T06:41:09-05:00` | `:embedContent` (`outputDimensionality: 768`) -> HTTP `200`, `dims=768` |
| **hbos-freellmapi (:3001)** | `PC` | **ACTIVO** | `2026-11-26T06:41:10-05:00` | `GET /v1/models` (auth Bearer) -> HTTP `200`, `283` modelos (resuelve 404 del 2026-11-25) |
| **Docker Engine** | `PC` | **DISABLED (F5)** | `2026-11-26T06:41:09-05:00` | `0` procesos Docker corriendo; autostart deshabilitado por orden de Guillermo |
| **Qdrant Local (:6333)** | `PC` | **OFF (F5)** | `2026-11-26T06:41:09-05:00` | Timeout / connection refused en `:6333`; prohibido arrancarlo en esta tarea |
| **MUMO (Consejo Multi-Modelo)** | `CLOUD` | **PENDING (F7)** | `2026-11-25` | Identidad creada; sesión geo-bloqueada (`?geo=blocked`). No enrutar trabajo real |
| **VoxCPM2 Plus Space** | `CLOUD` | **POR CONSTATAR** | `2026-11-26T06:41:09-05:00` | No sondeado en vivo en esta corrida |
| **Anthropic MCP Direct File Upload** | `CLOUD` | **POR CONSTATAR** | `2026-11-26T06:41:09-05:00` | En despliegue (F13); no sondeado en vivo en esta corrida |
| **Canal directo Archer -> Antigravity** | `PC+CLOUD` | **PENDING (F9)** | `2026-11-26` | Solo registrado en Quadrant; construcción futura |

---

## 3. Canon de Voz y Avatar (F4 y F14)

- **Voz Canónica (F4):** **VoxCPM2 Plus** (`ref-video08`, master `-14.0 LUFS`, `48 kHz mono`).
  - **VETO ABSOLUTO:** `F5-TTS` queda **VETADO** (licencia `CC-BY-NC`, no monetizable) y voces genéricas SAPI prohibidas. Esto corrige aditivamente la Prohibición A de `HBOS_PRODUCTION_DAG_01.md` (`DISC-03`).
- **Avatar Canónico (F4):** La **ruta fotográfica** (stills aprobados + movimiento procedural + boca por amplitud + WebM alfa) es la única ruta **VERIFICADA Y CANÓNICA**. La prohibición real aplica contra avatares congelados en un PNG estático sin movimiento.
- **Carril Experimental Colab (F14):** Lip-sync / Wav2Lip / LatentSync / Colab permanecen **UNPROVEN** (`DISC-04`). Google Colab solo puede usarse en un **carril experimental aislado**:
  1. Nunca toca una corrida en progreso ni sustituye la ruta fotográfica canónica.
  2. **Pre-verificación obligatoria en Fase 0** de cada archivo de media antes de subir (integridad, formato, tamaño) por el antecedente de dos caídas con `INVALID_MEDIA (error 2011)` el 2026-11-25.
  3. Solo se adopta tras **verificación ciega**: rostro 100% reconocible como Guillermo, proporciones `1.87 m` intactas, movimiento continuo real, fondo claro.
  4. Todo resultado entra a Quadrant marcado como `EXPERIMENTAL` con evidencia.

---

## 4. Ledger de Builds "Equipo de Agentes de IA" (`DISC-05`)

Ninguna versión se oculta ni se declara silenciosamente "la final"; todas conviven registradas en `canon_video_hbos_r768`:
1. **`v1_archer_407s`**: `INSUMOS-PANEL\EQUIPO-DE-AGENTES-video-final.mp4` (`407.656 s`, 19 imágenes neón, SHA-256 `817aef913daf64be4737fa5687eef829d3c1ef9856da7bfa6a7850474bbebb88`).
2. **`v1_antigravity_10min`**: `2026-11-25_Equipo_Agentes_IA_10min.mp4` (citado `424.4 s` en mapa, medido `455.767 s`, SHA-256 `7e0f0cef35bb1bac247f20cdd6c6c0018baa169b1a8ccdbdcd7fcc955f575a25`).
3. **`v1_antigravity_3d_60fps`**: `EQUIPO-DE-AGENTES-3D-CINEMATICO-FINAL.mp4` (`414.276 s`, 60 fps, SHA-256 `694702e426629a1cace1dc586e8390c26e6df9c3121c1e4cc11381bd05da01de`).
4. **`v2_panel_choreography`**: Derivado de `v1_archer_407s` con coreografía de panel de 10 módulos (`Fase 3`). Guillermo elige la versión canónica final.

---

## 5. Regla Git, Topología Split, Flujo Único, Cápsula F12 y Upgrade MCP F13

- **Git & Secretos (Fase 4 + F8/R30):** Todo commit/push exige **PRE-DEBUG SECRET SCAN** (patrones + entropía) sobre todo el árbol a commitear. Cualquier hallazgo **DETIENE** el commit/push (`HALT`) sin tocar credenciales ni publicar secretos (`DISC-07`: hallazgo previo en `seed_recursos_hbos.js:10`).
- **Topología Split PC <-> CLOUD (F10):** Toda etapa del flujo declara explícitamente su lugar (`PC` o `CLOUD`) y su punto de verificación SHA-256 en frontera. Si no se conoce dónde vive el insumo o su hash en llegada, `HALT`.
- **Un Solo Flujo Maestro (F11):** El esqueleto (`factores + DAG + PRE/POST + split + Quadrant + versionado + cierre verificado`) rige **todos** los nodos de HBOS (`creative_video`, `financial`, `planning`, `direction`, `control`, `organization`, `project_feasibility_analysis`, `source_analysis`).
- **El Hilo Vive en Quadrant (F12):** Ningún estado depende de la memoria de sesión del agente. Antes de cerrar o reiniciar se escribe la **Cápsula de Handoff** en Quadrant Cloud + `ESTADO-HILO.md`.
- **Anthropic MCP Upgrade (F13):** Los modelos Claude del consejo operan con MCP como sub-agentes colaborativos mediante: (a) **Tasks** (fases largas asíncronas en segundo plano), (b) **Elicitation** (pausas humanas reales en cada gate de Guillermo, nunca auto-aprobación), (c) **Skills over MCP** (protocolos empaquetados como skills).
- **Reversibilidad:** Para revertir cualquier punto de este anexo basta restaurar el hash de vista desde `docs/superados/` y consultar los registros históricos en Quadrant sin borrar ni alterar los documentos base de solo lectura.
