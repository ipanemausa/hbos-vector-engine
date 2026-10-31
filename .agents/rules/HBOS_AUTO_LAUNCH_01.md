---
trigger: always_on
description: REGLA DURA RULE_AUTO_LAUNCH_01 — Auto-Preview & Instant File Launch (Post-Render) para todo activo multimedia generado en HBOS Qdrant Engine.
---

# REGLA DURA: `RULE_AUTO_LAUNCH_01` (AUTO-PREVIEW & INSTANT FILE LAUNCH)

- **Identificador Canónico:** `RULE_AUTO_LAUNCH_01`
- **Directiva Obligatoria:** En cuanto cualquier agente o nodo finalice la generación de un activo multimedia (video `.mp4`, script `.py`/`.md`, subtítulos `.ass`, imagen `.png`/`.jpg` o locución de voz `.wav`/`.mp3`), el sistema ejecutable en Antigravity 2.0 **DEBE disparar de forma automática la apertura del archivo generado** utilizando:
  1. `os.startfile(str(vault_path))` / `Start-Process` apuntando directamente a la ruta en Google Drive (`G:\My Drive\HBOS_Qdrant_Engine\03_MEDIA_VAULT_FINAL\...`), y
  2. Previsualización embebida inmediata en el chat (`<agent-embed>` o artefacto interactivo autocontenido).
- **Prohibición Estricta:** PROHIBIDO dejar archivos huérfanos sin previsualización. El ciclo de cada escena o entregable E2E se considera incompleto hasta que el usuario (Guillermo) pueda ver y escuchar el resultado en pantalla de inmediato.

