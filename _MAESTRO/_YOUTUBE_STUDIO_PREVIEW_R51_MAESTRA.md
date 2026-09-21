# REGLA R51 · PREVIEW YOUTUBE STUDIO EN PANTALLA 3 Y AUTORIZACIÓN BIOMÉTRICA
**Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**

## 1. PRINCIPIO RECTOR (R51)
- La publicación y revisión del contenido audiovisual exige inspección sensorial humana directa antes de cualquier dispersión pública.
- Antigravity proyecta y gestiona la visualización del video master en la **Pantalla 3** (Monitor 3: `x=-1920, y=0, 1280x720`).
- Si existe OAuth configurado $\to$ subida de borrador privado y apertura de edición directa en YouTube Studio.
- Si no hay OAuth local configurado $\to$ apertura de la URL soberana de YouTube Studio (`https://studio.youtube.com`), registro de metadatos locales y carga de borrador auditada.
- **Aprobación Biométrica Obligatoria (R37 + R42):** Interfaz síncrona `HBOSAuthUI` con Windows Hello para autorizar la transición del preview a publicación.
- **Publicación:** Estrictamente supeditada al veredicto afirmativo del operador.

---

## 2. PARÁMETROS DEL ASSET MAESTRO (EPISODIO 04)
- **Video Master:** `assets/videos/demis_hassabis_final.mp4` (69.42 MB, 251.49s, 1080p, -14.0 LUFS).
- **Hash SHA-256:** `2291e97ab6a1949eea0ea4d5729f2729c2864ae258fa8779810cd93fea5dd505`.
- **Thumbnail:** `assets/videos/demis_hassabis_youtube_thumb.jpg` (1280x720).
- **Canal Soberano:** `@ipanemamarketingusa`.
- **Modo de Privacidad:** `private` (Borrador de Inspección).

---

## 3. TRAZABILIDAD Y REGISTRO DE EJECUCIÓN
- **Script Motor:** [`hbos_youtube_studio_preview.py`](file:///c:/Users/ipane/hbos-deploy/hbos-vector-engine/hbos_youtube_studio_preview.py)
- **Registro Auditor:** [`youtube_studio_preview_log.json`](file:///c:/Users/ipane/hbos-deploy/hbos-vector-engine/youtube_studio_preview_log.json)
- **Estado de Aprobación:** `PREVIEW_APPROVED` (Biométricamente verificado con Windows Hello).
