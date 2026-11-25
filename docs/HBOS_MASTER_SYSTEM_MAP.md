# HBOS MASTER SYSTEM MAP · MAPA MAESTRO VIVO DEL ECOSISTEMA
**Versión:** 2.0.0 Canónica · **Fecha de Emisión:** 2026-11-25  
**Autoridad:** Guillermo Alonso Hoyos (Guía Hoy) & Antigravity 2.0 HBOS Engine  
**Gobernanza:** `HBOS_PRODUCTION_DAG_01` · `RULE_AUTO_LAUNCH_01` · Qdrant como Fuente de Verdad  

---

## 1. Colecciones Qdrant Activas (Fuente Canónica de Verdad)

Qdrant opera de forma híbrida: **Local Engine** (`http://127.0.0.1:6333`) y **Cloud Cluster** (`us-east4-0.gcp.cloud.qdrant.io`).

| Colección Qdrant | Vector Dim | Métrica | Función Canónica |
| :--- | :---: | :---: | :--- |
| `canon_video_hbos_r768` | 768 | Cosine | Metadatos maestros, hashes SHA-256 y rutas de entregables de video HBOS |
| `canon_video_hbos` | 384 | Cosine | Índice ligero de consulta rápida y cross-referencing de video |
| `hbos-voice-profiles_r768` | 768 | Cosine | Perfiles biométricos y guardarraíles acústicos (f0 = 109.2 Hz, Guiahoy) |
| `hbos-voice-profiles` | 384 | Cosine | Enrutamiento acústico de síntesis y drama tags |
| `hbos_knowledge_r768` | 768 | Cosine | Base de conocimiento institucional y documentos de arquitectura |
| `hbos_erp_fiscal_rules_r768` | 768 | Cosine | Reglas impositivas, facturación y contratos de servicios agénticos |
| `casos_uso_hbos` | 384 | Cosine | Casos de uso de negocio (Argon 4 Cases, automatizaciones) |
| `sistema_casos_hbos` | 384 | Cosine | Clasificación sectorial y matriz de retorno operativo |
| `hbos_nodo_video_768d` | 768 | Cosine | Nodos desagregados de composición visual y fondos 16:9 |
| `hbos_nodo_voz_768d` | 768 | Cosine | Nodos de pistas de locución, transcripciones fonéticas CTC |
| `hbos_nodo_texto_768d` | 768 | Cosine | Guiones, biblias y bloques modulares sincronizados |
| `hbos_nodo_avatar_768d` | 768 | Cosine | Catálogo de poses 3D RGBA con canal alfa y anclaje anti-oclusión |
| `hbos_nodo_maestro_manifest_768d` | 768 | Cosine | Manifiestos unificados E2E de compilación |
| `marito_hoyos_hbos` | 384 | Cosine | Perfil y activos canónicos de avatar mascota / presentador |
| `registro_ecosistema_r768` | 768 | Cosine | Ledger inmutable de transacciones y estados de producción |

---

## 2. Árbol de Rutas Canónicas en Google Drive (`G:\My Drive`)

Estructura estricta sin duplicidades ni archivos huérfanos:

```
G:\My Drive\
├── Guiahoy_Produccion\
│   └── 2026-11-25\                                  <-- Área de Producción Activa del Día
│       ├── 02_voz_guiahoy\
│       │   └── equipo_agentes_ia_guiahoy.wav        <-- Audio Maestro Exclusivo (-14 LUFS, 48kHz mono)
│       ├── fondos_16x9\
│       │   ├── bg_01.jpg .. bg_10.jpg               <-- 10 Fondos Futuristas 1920x1080 Dedicados
│       ├── guion_equipo_agentes_ia.md               <-- Guion Maestro (10 Bloques Estructurados)
│       ├── block_timings.json                       <-- Tiempos Exactos ffprobe por Bloque
│       ├── 2026-11-25_Equipo_Agentes_IA_10min.srt   <-- Subtítulos Sincronizados
│       ├── 2026-11-25_Equipo_Agentes_IA_10min.mp4   <-- Entregable de Video 1080p 30fps H.264
│       └── 2026-11-25_Equipo_Agentes_IA_10min_manifest.json <-- Manifiesto de Integridad SHA-256
│
├── Avatar Guillermo - transparencias\               <-- Catálogo de 200 Poses 3D RGBA Transparentes
│   ├── avatar-pose-t-arms-open-narrower.png
│   ├── avatar-pose-t-calm-both.png
│   ├── avatar-pose-t-chin-stroke-L.png
│   ├── avatar-pose-t-arms-open-palms-up.png
│   ├── avatar-pose-t-chin-stroke-R.png
│   ├── avatar-pose-t-arms-open-wider.png
│   ├── avatar-pose-t-arms-open-palms-front.png
│   ├── avatar-pose-t-both-thumbs-up.png
│   └── avatar-pose-t-hands-clasped.png
│
├── HBOS_Qdrant_Engine\
│   ├── 00_CORE_BIBLIAS\                             <-- Biblias de Arquitectura y Conocimiento
│   │   ├── BIBLIA-CLON-VOZ-GUIAHOY-2026-10-30.md
│   │   └── INDICE-MAESTRO-WORKSPACE.md
│   └── 03_MEDIA_VAULT_FINAL\                        <-- Bóveda Inmutable de Medios
│       ├── Guiahoy_CLONE_REF_90s_48k.wav            <-- Master de Referencia Vocal Canónica
│       ├── 2026-11-25_Equipo_Agentes_IA_10min.mp4   <-- Copia Espejo de Seguridad
│       └── Guiahoy_voice_clone_manifest.json
│
└── HBOS_Creative\
    └── 02_Voice_Profiles\                           <-- Perfiles de Voz y Entrenamientos
```

---

## 3. Matriz de Agentes y Enrutador Free (Zero Cost / High Throughput)

Arquitectura agéntica orquestada para desacoplar el procesamiento pesado de la máquina local:

```
                  ┌───────────────────────────────┐
                  │      AGENTE COORDINADOR       │
                  │ (Descomposición DAG & Control)│
                  └──────────────┬────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│AGENTE INVESTIGADOR│   │ AGENTE EJECUTOR  │    │  AGENTE AUDITOR  │
│(Datos, Cero Bias)│    │(Código, Contenido│    │ (Cero Alucinación│
└──────────────────┘    │ y Renderizado)   │    │  & QA Estricto)  │
                        └──────────────────┘    └──────────────────┘
```

### Proveedores y Modelos Disponibles en el Router:
1. **Groq (Inferencia Ultra Rápida):** Llama 3.3 70B Versatile, DeepSeek-R1-Distill-Llama-70B.
2. **Google Gemini:** Gemini 2.5 Flash, Gemini 2.5 Flash-Lite (Ventana de contexto de 1M tokens).
3. **Mistral AI:** Codestral Latest (256k contexto para tareas de programación).
4. **Ollama Local (Offline / Privacidad):** Modelos locales servidos en `http://localhost:11434`.
5. **Acoustic & Media Routers:** SAPI / Fish Audio / FFmpeg nativo sin latencia.

---

## 4. Plugins y Herramientas Locales Operativas

| Plugin / Tool MCP | Servidor MCP | Estado | Descripción Funcional |
| :--- | :--- | :---: | :--- |
| `hbos-freellmapi` | Local Port 3001 / STDIO | **ACTIVO** | Enrutador unificado de inferencia multi-proveedor |
| `hbos-diamantino` | Filesystem STDIO | **ACTIVO** | Gestión documental y lectura/escritura de activos |
| `diamantini-imagenes`| Filesystem STDIO | **ACTIVO** | Catálogos de imágenes y verificación de transparencias |
| `gdrive` | Google Workspace MCP | **ACTIVO** | Integración y sincronización con Google Drive |
| `ollama_ollama-engine-hub`| Engine Hub STDIO | **ACTIVO** | Control y despacho de modelos offline locales |
| `open-weight-models`| OpenWeight Hub STDIO | **ACTIVO** | Inferencia directa con modelos abiertos y R1 |
| `rea-hiperframes-fish`| Antigravity Skill | **ACTIVO** | Pipeline de producción masiva con guardarraíles acústicos |
| `guiahoy-video-producer`| Antigravity Skill | **ACTIVO** | Pipeline de subtitulado animado, recortes y autozoom |

---

## 5. Estado Verificado de Proyectos y Capas HBOS

| Proyecto | Capa Texto (Guion) | Capa Visual (16:9 + Avatar) | Capa Acústica (-14 LUFS) | Capa Video (MP4) | Qdrant Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Clase 01 MIT** *(Histórico)* | DONE | DONE | DONE | DONE | Registrado |
| **Video Nube Creativo** *(Histórico)*| DONE | DONE | DONE | DONE | Registrado |
| **Equipo de Agentes de IA** *(2026-11-25)* | **DONE (10 Bloques)** | **DONE (10 Fondos + RGBA)** | **DONE (424.4s Master)** | **DONE (1080p 30fps)** | **INDEXADO** |

---
*Documento vivo sincronizado por Antigravity 2.0 y HBOS Vector Engine.*
