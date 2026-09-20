# _ESCUCHA_MAESTRA.md — Módulo de Escucha, Transcripción y Sensorium Acústico HBOS
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 228 | **Fecha:** 2026-09-20 | **Estado:** CONSTRUIDO · VERIFICADO · EN PRODUCCIÓN  
> **Script Operativo:** `hbos_audio_listener.py` | **Motor de Descarga:** `yt-dlp` (2026.07.04)

---

## 1. Misión del Módulo de Escucha
Permitir a HBOS actuar como un **radar perceptivo continuo** capaz de escuchar, descargar streams de audio de fuentes de frontera (canales de YouTube como ALEJAVI, podcasts técnicos, conferencias) y procesarlos mediante el pipeline matemático R768.

---

## 2. Evaluación H_ALT de Métodos de Transcripción (§16.3)
1. **ALT_A (Whisper Local):** 100% privado y soberano, pero demanda VRAM dedicada cuando la GPU está ocupada generando video en ComfyUI.
2. **ALT_B (Gemini API Multimodal):** Máxima precisión y contexto masivo (1M tokens), ideal para análisis conceptual y timestamps precisos.
3. **ALT_C (FreeLLMAPI Router :3001):** Costo cero, router de múltiples motores y balanceo dinámico.

**Síntesis Dialéctica Adoptada:** El pipeline utiliza Whisper local si la GPU está ociosa, conmutando automáticamente al router FreeLLMAPI o Gemini API si se requiere procesamiento en paralelo masivo sin degradar el rendimiento local.

---

## 3. Pipeline Operativo F -> C -> H
1. **F (Factorizar):** Extracción de texto crudo y segmentación en proposiciones atómicas ortogonales.
2. **C (Comprimir):** Supresión de muletillas y redundancias informacionales (ahorro >= 60% en tokens).
3. **H (Hibridar):** Generación de embeddings en espacio R384 e indexación en colecciones Qdrant (`diamantino_lecciones` y `registro_ecosistema`).
