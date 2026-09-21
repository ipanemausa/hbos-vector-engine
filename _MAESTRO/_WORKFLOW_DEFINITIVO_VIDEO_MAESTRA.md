# WORKFLOW DEFINITIVO DE VIDEO · DIRECTOR AGÉNTICO
**Ecosistema Soberano HBOS · Modo Experto ALEJAVI**  
**Versión: v2.0 DEFINITIVA · Vigente desde op=249**  
**Gobernanza: FAM@-T · DAG R768 · No-Regresión**

---

## §0 · PRINCIPIO RECTOR
🚨 **REGLA DE ORO: CREAS SIEMPRE EN NUBE. COORDINAS EN UNBE. NUNCA EN LOCAL.**

El workflow definitivo de video sustituye los scripts monolíticos anteriores (`build_video_v2.py`, `build_demis_hassabis_final_video.py`) por un Grafo Acíclico Dirigido (DAG) modular de 10 fases gobernado por el agente principal `hbos_film_director_agent`.

---

## §1 · MAPA DE AGENTES DEL WORKFLOW

| Rol Agéntico | Agente / Sub-agente | Módulo Python | Función Canónica |
| :--- | :--- | :--- | :--- |
| **Director General** | `hbos_film_director_agent` | `hbos_film_director_agent.py` | Orquestación DAG, pre-flight, coordinación de 10 fases y cierre. |
| **Generador Assets** | `asset_generator_agent` | `hbos_film_director_agent.py` | Backgrounds 16:9, personajes alpha, voces R128 (-14 LUFS), música. |
| **Motor Cinemático** | `motion_engine_agent` | `hbos_anchor_vivo.py` | 420 micro-movimientos, seguimiento ocular/craneal, body sway. |
| **Motor Gráfico** | `graphics_engine_agent` | `hbos_film_director_agent.py` | Lower thirds con fade in/out, Atribución permanente R73, HUD. |
| **Compositor Multicapa**| `compositor_agent` | `hbos_film_director_agent.py` | Ensamble FFmpeg multicapa (C0: Bg, C1: Anchor, C2: Text, C3: Legal R73). |
| **Control Calidad** | `qc_agent` | `hbos_film_director_agent.py` | Validación OpenCV encuadre, persistencia texto, sync A-V, R73. |
| **Distribución** | `social_manager_agent` | `hbos_social_manager.py` | YouTube Data API v3 (borrador privado R49), IG/TikTok, X, TG. |
| **Community Manager** | `community_manager_agent` | `hbos_community_manager.py` | Hashtags estratégicos, enlaces ALEJAVI, escucha y sentimiento. |
| **Aprendiz Perpetuo** | `run_agente_aprendiz` | `run_agente_aprendiz.py` | Indexación en Qdrant Cloud, triple redundancia física y no-regresión. |

---

## §2 · LAS 10 FASES TOPOLÓGICAS DEL WORKFLOW

```
  [FASE 0: Input + Vectorización + Decisión R73]
                         │
        ┌────────────────┼────────────────┐
        ▼ (Paralelo)     ▼ (Paralelo)     ▼ (Paralelo)
   [FASE 1: Assets] [FASE 2: Movimiento] [FASE 3: Gráficos]
   ├── 1A: Backgrounds├── 2A: 420 Movs   ├── 3A: Lower Thirds Fade
   ├── 1B: Alpha Pers.├── 2B: Eye/Head   ├── 3B: Atribución R73
   ├── 1C: Voces R128 └── 2C: Body Sway  └── 3C: HUD Contextual
   └── 1D: Música -14LUFS
        │                │                │
        └────────────────┼────────────────┘
                         ▼
        [FASE 4: Composición Multicapa FFmpeg]
                         │
                         ▼
        [FASE 5: Control de Calidad QC]
                         │
                         ▼
        [FASE 6: Preview en Pantalla 3 + Hello]
                         │
        ┌────────────────┼────────────────┐
        ▼ (Paralelo)     ▼ (Paralelo)     ▼ (Paralelo)
   [FASE 7: Distrib.] [FASE 8: Community] [FASE 9: Cierre DAG]
   ├── YouTube R49    ├── Hashtags ALEJAVI├── Qdrant op=249
   ├── Meta/TikTok    ├── Enlaces Papers  ├── Triple Redundancia
   └── X/Telegram     └── Sentimiento     └── UNBE 100% OK
```

---

## §3 · PROMPT CANÓNICO RECTOR (§17)

Este es el prompt canónico exacto que invoca la ejecución del workflow sin variantes:

```
╔══════════════════════════════════════════════════════════════════════════╗
║  PROMPT CONCEPTUAL AGÉNTICO CREATIVO · EJECUCIÓN TOTAL                   ║
║  FAM@-T · LLMAPI ⊕ R768 · DAG · H_ALT · NO-REGRESIÓN                     ║
║  SUBPROYECTO: PRODUCCIÓN DE VIDEO · WORKFLOW DEFINITIVO                  ║
║  VERSIÓN: v2.0 DEFINITIVA · Vigente desde op=249                         ║
║  Ecosistema Soberano HBOS · Modo Experto ALEJAVI                         ║
║                                                                          ║
║  🚨 EJECUCIÓN SIEMPRE EN NUBE (NODO CREATIVO HBOS) 🚨                    ║
║  🚨 NUNCA EN LOCAL · NUNCA EN ANTIGRAVITY LOCAL 🚨                       ║
║  ✅ COORDINACIÓN EN UNBE                                                 ║
╚══════════════════════════════════════════════════════════════════════════╝

ORQUESTADOR: Invocar `python hbos_film_director_agent.py --video-id <ID> --tema "<TEMA>" --duracion <SEG>`
EJECUCIÓN: Orden topológico estricto de las 10 fases canónicas.
VERIFICACIÓN EMPÍRICA: SHA-256 en assets, ffprobe en composición, OpenCV en QC, HTTP 200 en distribución.
REGLA DE CIERRE: Registro en Qdrant Cloud, Triple Redundancia física y verificación UNBE 100% OK.
```

---
*Documento sellado bajo el Canon R768 · Gobernanza Soberana HBOS op=249.*
