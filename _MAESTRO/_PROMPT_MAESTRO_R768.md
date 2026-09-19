# HBOS-DIAMANTINO FACTORY v1.0 — PROMPT AGENTIC R768
### Ecosistema: HBOS-Diamantino · Arquitectura de Cómputo Soberano
### Arquitecto & Operador: Guillermo Hoyos — Embajador AsertiaNova
### Trazabilidad: Inmutable en Qdrant Cloud (R384 / R768)

---

## 1. GUARD RAIL HBOS
- **Único entorno operativo:** `hbos-vector-engine`
- **Prohibido:** `openclaw`, `openclaw-operativo-2026`, `hb-jewelry`, `b jewelry`
- **Google Drive (Fuente de Verdad):**
  - Producción: `G:\My Drive\HBOS-Diamantino\`
  - Banco de Assets: `G:\My Drive\Diamantini\`
- **Terminal Local:** PC sin GPU. Inferencia pesada SIEMPRE en Nube.
- **Voz:** PROHIBIDO TTS local (SAPI, Windows). EXCLUSIVAMENTE voces IA de Nube (ElevenLabs / OpenAI).
- **Factorización R768:** 87% de reducción en consumo de tokens y máxima precisión semántica.

---

## 2. FORMULACIÓN MATEMÁTICA R768

Sea el estado del video $V(t)$:

$$V(t) = \sum_{i} \left[ N_i \cdot A_i \cdot P_i \cdot E_i \cdot T_i \right]$$

donde:
- $N_i$: Narrativa $\in \{\text{intro}, \text{bloques}, \text{cierre}\}$
- $A_i$: Asset $\in \{\text{imagen}, \text{clip}, \text{audio}, \text{BGM}\}$
- $P_i$: Personaje $\in \{\text{Diamantino}, \text{Rubín}, \text{Zafir}, \text{Esmeralda}, \text{Citrilo}, \text{Grafito}, \text{Amatista}\}$
- $E_i$: Estética $\in \{\text{GTC Keynote}, \text{Cinematográfico 8K}, \text{Data Center Enterprise}\}$
- $T_i$: Trazabilidad $\in \{\text{operation\_id incremental en Qdrant}\}$

---

## 3. PROTOCOLO DE EJECUCIÓN POR GRUPOS (DAG)

- **GRUPO A (Infraestructura Base):**
  - R769: Vectorización en Qdrant (`diamantino_assets`, 384 dim, Cosine).
  - R770: Banco de 10 variantes por personaje en `G:\My Drive\Diamantini\[Personaje]\`.
  - R771: Manifiesto y Fichas en `_MAESTRO`.
  - *Checkpoint A: Aprobación humana.*

- **GRUPO B (Narrativa):**
  - R772: Guion técnico oficial en `01_Guion\guion_v1.md` (Español + Subtítulos inglés, fuentes citadas).
  - R773: Storyboard oficial en `02_Storyboard\storyboard_v1.json` (Mapeo plano ➔ asset).
  - *Checkpoint B: Aprobación humana.*

- **GRUPO C (Producción Audiovisual):**
  - R774: Animación con Wan21 en nube (`04_Clips_Wan21\epXX_plano_YY_wan21.mp4`).
  - R775: Audio con voces IA de nube en `03_Assets\Voces\` + BGM en `03_Assets\BGM\`.
  - *Checkpoint C: Aprobación humana.*

- **GRUPO D (Ensamblado y Publicación):**
  - R776: Edición final con FFmpeg a 1080p 30fps H.264 (`05_Master\` y `06_Publicado\`).
  - *Checkpoint D: Aprobación y video listo para emitir.*
