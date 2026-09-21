# REGLA R59 · AISLAMIENTO TOTAL DE ASSETS Y VIDEOS
**Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**

## 1. PRINCIPIO FUNDAMENTAL (R59)
- **Aislamiento Estricto:** Cada video del ecosistema debe residir en su propio directorio autónomo y encapsulado.
- **Prohibición:** Queda terminantemente prohibido mezclar recursos audiovisuales (audios, backgrounds, frames, escenas) entre videos distintos.
- **Verificación Criptográfica Previa:** Antes de abrir o publicar cualquier material, se comprueba su coherencia formal, tamaño en bytes y hash criptográfico SHA-256 contrastado con su `metadata.json`.

---

## 2. ESTRUCTURA CANÓNICA OBLIGATORIA

```
assets/videos/<nombre_video>/
  ├── video_final.mp4      (Video master ensamblado)
  ├── thumbnail_master.jpg (Miniatura de alta definición)
  ├── audio/               (Pistas de voz, BGM y SFX aislados)
  ├── backgrounds/         (Fondos y canvas escénicos)
  ├── escenas/             (Clips y secuencias procesadas)
  ├── frames/              (Imágenes y fotogramas del storyboard)
  └── metadata.json        (Manifiesto técnico con SHA-256 e integridad)
```

---

## 3. INSTANCIA IMPLEMENTADA: `demis_hassabis_v2`
- **Ruta Raíz:** [`assets/videos/demis_hassabis_v2/`](file:///c:/Users/ipane/hbos-deploy/hbos-vector-engine/assets/videos/demis_hassabis_v2/)
- **Video Master:** `video_final.mp4` (72,787,044 bytes, 251.49s, 1080p, -14.0 LUFS).
- **Hash SHA-256:** `2291e97ab6a1949eea0ea4d5729f2729c2864ae258fa8779810cd93fea5dd505`.
- **Assets Aislados:** 12 audios, 1 background, 2 escenas y 10 frames de storyboard.
- **Manifiesto:** [`metadata.json`](file:///c:/Users/ipane/hbos-deploy/hbos-vector-engine/assets/videos/demis_hassabis_v2/metadata.json).
