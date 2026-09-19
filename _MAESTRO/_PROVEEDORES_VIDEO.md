# PROVEEDORES DE VIDEO — HBOS-DIAMANTINO
**Ecosistema Soberano HBOS-Diamantino · Trazabilidad: operation_id = 206**
**Gobernanza:** Triple Redundancia Física (Workspace Local + Google Drive + Backup Local)
**Fecha:** 2026-09-19 | **Autor:** Experto ALEJAVI

---

## 1. Proveedores con Credencial Presente en el Ecosistema

### 1.1. Fal.ai Cloud (Saldo de Activación: $5 - $10 USD)
- **Modelos Disponibles:** 33 modelos de video espacial-temporal en catálogo activo:
  - `fal-ai/kling-video/v3/pro/image-to-video` (Kling Video v3 Pro)
  - `fal-ai/kling-video/v2.5-turbo/pro/image-to-video`
  - `fal-ai/kling-video/v3/standard/image-to-video`
  - `minimax/h3-max/image-to-video`
  - `minimax/h3-max-turbo/image-to-video`
  - `alibaba/wan-3.0-prime/reference-to-video`
  - `fal-ai/veo3.1/fast/image-to-video`
  - `bytedance/seedance-2.5/image-to-video`
  - Fast SVD y +25 arquitecturas generativas adicionales.
- **Ventaja Competitiva:** Máxima diversidad de arquitecturas de video del mercado, menor latencia y alta concurrencia serverless.
- **Continuidad para Ep04:** Media (alberga Wan 3.0 y Kling v3, pero el render base de los planos 00 y 01 de Ep04 fue calibrado en Wan 2.1).
- **Recomendación Estratégica:** Ideal para la serie regular a partir de Ep05+, permitiendo experimentación de planos dinámicos con Kling y Veo 3.1.

### 1.2. Alibaba Cloud DashScope (Saldo de Activación: $5 - $20 USD)
- **Modelos Disponibles:**
  - `wan2.1-i2v-turbo` (Image-to-Video 720p/1080p Turbo)
  - `wan2.1-t2v-turbo` (Text-to-Video)
  - `wan3.0` / CosyVoice2 / Qwen-VL.
- **Ventaja Competitiva:** Continuidad estética 100% idéntica a los planos 00 y 01 de Demis Hassabis (Ep04). Pipeline Python local (`generate_ep04_wan21_clips.py`) ya probado, auditado y calibrado a nivel de prompt y semilla.
- **Continuidad para Ep04:** **Total (10/10)**.
- **Recomendación Estratégica:** Indispensable para cerrar Ep04 con calidad de autor Paramount v6 sin rupturas estilísticas.

### 1.3. Hugging Face Inference Router (Plan Pago / Dedicated Endpoints)
- **Modelos Disponibles:** Modelos Open Source en el Hub (Wan 2.1 T2V Diffusers, Stable Video Diffusion, MiniMax Lora ComfyUI).
- **Ventaja Competitiva:** Sin vendor lock-in, modelos abiertos.
- **Continuidad para Ep04:** Media.
- **Recomendación Estratégica:** Menor prioridad; la inferencia serverless gratuita no incluye GPU pesada y los Inference Endpoints requieren pago por hora de GPU dedicada.

---

## 2. Proveedores sin Credencial Configurada

### 2.1. Replicate (Modelo Pay-Per-Use)
- **Modelos Disponibles:** +100 modelos de video (Kling, Luma Dream Machine, Runway, Wan 2.1).
- **Costo:** Pago por segundo de GPU.
- **Recomendación:** Requiere creación de cuenta nueva y registro de tarjeta de crédito.

### 2.2. Runway API (Modelo Pay-Per-Use)
- **Modelos Disponibles:** Gen-2, Gen-3 Alpha Turbo.
- **Costo:** Basado en créditos de video.
- **Recomendación:** Alta calidad pero costo significativamente más elevado por segundo generado.

### 2.3. Luma Labs Dream Machine API (Modelo Pay-Per-Use)
- **Modelos Disponibles:** Luma Dream Machine (Ray 1 y Ray 2).
- **Costo:** Pago por generación.
- **Recomendación:** Excelente para cinemática de cámara, pero sin clave actual.

---

## 3. Recomendación Estratégica Final

### 3.1. Para Ep04 (Continuidad Inmediata y Calidad Canónica):
- **Opción:** Recargar cuota en Alibaba Cloud DashScope ($5 - $20 USD).
- **Razón Técnica:** Los clips 00 y 01 ya fueron generados con `wan2.1-i2v-turbo`. El storyboard v2 (10 planos) y las composiciones visuales bio-cuánticas P-12 están calibradas exactamente para los pesos de Wan 2.1. Permite ensamblar Ep04 hoy mismo con coherencia perfecta.

### 3.2. Para Episodios Futuros (Ep05+ y Escala Masiva):
- **Opción:** Recargar balance en Fal.ai ($5 - $10 USD en `fal.ai/dashboard/billing`).
- **Razón Técnica:** Desbloquea 33 modelos de video con una sola API key ya integrada (`FAL_API_KEY`), incluyendo Kling v3 Pro y MiniMax H3.

### 3.3. Estrategia Canónica Óptima HBOS:
1. **Recargar ambos proveedores (~$10 - $30 USD inversión total):**
   - **DashScope:** Cierra Ep04 de inmediato sin salto visual en los 8 planos restantes.
   - **Fal.ai:** Desbloquea la suite completa de 33 modelos para Ep05 en adelante.
2. **Arbitraje Multi-Modelo Activo:** El orquestador soberano (`hbos_orquestador.py`) enrutará automáticamente la tarea de video entre DashScope y Fal.ai según la cuota y la estética requerida en cada guion.
