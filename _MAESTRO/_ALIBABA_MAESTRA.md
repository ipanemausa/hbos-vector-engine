# _ALIBABA_MAESTRA.md — Capa E: Auditoría e Integración del Ecosistema Alibaba Cloud
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 232 | **Fecha:** 2026-09-21 | **Versión:** v1.3 Canónica | **Estado:** ✅ AUDITORÍA COMPLETADA · PLAN DE REACTIVACIÓN  
> **Canon:** Arquitectura Desacoplada (§D) · Capa E (Alibaba / Bailian)

---

## 1. Auditoría del Ecosistema Previo Alibaba Cloud
A partir de la inspección del histórico del repositorio (`openclaw-orchestrator.js`, `_PLAN_MAESTRO_PROMPTS_R768.md` y `.env.local`), se determinan con precisión los elementos de la Capa E:

* **Plataforma:** Alibaba Cloud Model Studio (Bailian / DashScope International).
* **Endpoint API:** `https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
* **Región de Servicio:** `ap-southeast-1` (Singapur).
* **Credencial en Entorno:** `DASHSCOPE_API_KEY` (configurada en `.env.local`).
* **Bucket OSS de Salida:** `dashscope-result-sgp.oss-ap-southeast-1.aliyuncs.com`.
* **Modelos Empleados:**
  * **Video:** `wan2.1-i2v-turbo` (generación cinematográfica 720p/1080p a partir de imágenes del storyboard).
  * **Audio/Voz:** `qwen3-tts-flash` (síntesis de voz complementaria de alta velocidad).
  * **LLM:** `qwen-plus`, `qwen-turbo` y familias Qwen 2.5.

---

## 2. Diagnóstico del Estado Actual de Cuota
* **Incidencia:** La cuota promocional gratuita de 90 días fue consumida (`AllocationQuota.FreeTierOnly: The free quota has been exhausted`).
* **Clips Producidos Históricamente:** `plano_00` (5s) y `plano_01` (20s) fueron generados con éxito bajo esta API.

---

## 3. Plan de Reactivación y Soberanía Comercial
Para reactivar la generación nativa masiva de Wan 2.1 sin bloqueos:
1. **Asociación Comercial:** Migrar la cuenta de Alibaba Cloud DashScope bajo la sombrilla `IPANEMAMARKETINGUSA@gmail.com` (Capa A).
2. **Modalidad Post-Pago / Recarga:** Cargar saldo operativo de **$10 a $20 USD** (costo aproximado de renderizado Wan 2.1 turbo: ~$0.04 por clip de 5s).
3. **Respaldo Inmediato:** Mientras no se aplique la recarga, el pipeline utiliza el motor local FFmpeg Ken Burns de alta definición sobre los renders 8K del storyboard, garantizando continuidad productiva a costo $0.00 USD.
