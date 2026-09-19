# ESTÁNDAR DE MEJORA DE CALIDAD BROADCAST EN HBOS-DIAMANTINO
**Especificaciones Técnicas Audiovisuales, Normalización EBU R128 y Pipeline Responsive**  
**Documento Canónico de Control de Calidad y Postproducción**  
**operation_id:** 188 | **Gobernanza:** Patrones P-04 v2, P-05, P-07, P-11 | **Ecosistema:** HBOS-Diamantino

---

## 1. PARÁMETROS MAESTROS DE CALIDAD DE VIDEO

| Parámetro | Especificación de Producción | Tolerancia / Límite |
| :--- | :--- | :--- |
| **Resolución Nativa** | 1920 × 1080 píxeles (Full HD) | Opcional 3840 × 2160 (4K UHD) |
| **Cadencia de Cuadros** | 30.00 fps constantes | Prohibido variable frame rate (VFR) |
| **Códec de Video** | H.264 (libx264, perfil High, nivel 4.2) | Prohibido formatos sin compresión temporal en web |
| **Espacio de Color** | Rec.709 (BT.709) con rango YUV420p | Cero degradación cromática en navegadores |
| **Bitrate de Video** | 8,000 kbps (1080p) / 18,000 kbps (4K) | Control de tasa CRF = 18 (calidad visual sin pérdidas perceptuales) |

---

## 2. PARÁMETROS MAESTROS DE CALIDAD DE AUDIO (PATRÓN P-04 v2)

1. **Loudness Integrado Objetivo:** `-14.0 LUFS` ($\pm 0.5$ LUFS).
2. **True Peak Máximo Absoluto:** `-1.0 dBTP` (evita distorsión inter-sample tras compresión lossy).
3. **Rango de Loudness (LRA):** `11.0 LU` (preserva la inteligibilidad de la voz y el impacto dinámico del BGM).
4. **Formato Maestro de Audio:** WAV PCM de 24 bits a 48,000 Hz estéreo.
5. **Ducking Automático (Patrón P-05):**
   - Cuando la voz está activa: BGM atenuada al **30% (-10 dB)**.
   - En silencios o transiciones escénicas: BGM recupera el **100% (0 dB)** con rampa suave de 0.3 segundos.

---

## 3. MATRIZ MULTIFORMATO RESPONSIVE (PATRÓN P-07)

A partir del master 16:9, el pipeline genera automáticamente los 4 formatos de distribución:

| Formato | Aspect Ratio | Resolución | Plataforma de Destino |
| :--- | :---: | :---: | :--- |
| **Horizontal** | `16:9` | 1920 × 1080 | YouTube Keynotes, Portales Web, Conferencias |
| **Vertical** | `9:16` | 1080 × 1920 | TikTok, YouTube Shorts, Instagram Reels |
| **Cuadrado** | `1:1` | 1080 × 1080 | Feed de Instagram, LinkedIn Posts, X (Twitter) |
| **Retrato** | `4:5` | 1080 × 1350 | Feed vertical optimizado para móviles |
