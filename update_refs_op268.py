# -*- coding: utf-8 -*-
from datetime import datetime
from pathlib import Path

BASE = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
refs = [
    BASE / "_HBOS_REFERENCIAS.md",
    BASE / "_MAESTRO" / "_HBOS_REFERENCIAS.md",
    BASE / "backup_hbos" / "_MAESTRO" / "_HBOS_REFERENCIAS.md"
]

seccion = f"""

---

## Auditoría de Redes Sociales y Marketing (op=268, {datetime.now().isoformat()})

- **Operación:** Diagnóstico integral de los 10 canales bajo el handle unificado `@ipanemamarketingusa`.
- **Topología de Canales:** Instagram, TikTok, Facebook, Threads, Telegram, Discord, LinkedIn, YouTube, X, GitHub.
- **Arquitectura de Identidad:** Capa A Sombrilla (`IPANEMAMARKETINGUSA@gmail.com`) vs Capa B Núcleo (`hbos@gmail.com` / `hbos.ecosystem@gmail.com`).
- **Roles de Marca:** Álex (Avatar comercial sintético ~35 años) vs Diamantino (Mascota mineral no-humanizada).
- **Inventario:** Ep01-Ep04, Demis Hassabis v2, 4 formatos responsive (16:9, 9:16, 1:1, 4:5), 45 audios, 39 guiones/prompts, 95 imágenes.
- **Monetización:** Marketplace Soberano (:3002/marketplace) en 4 niveles ($0, $27, $97/m, $1,500). Plan 30-60-90 activo.
- **Trazabilidad:** Qdrant Cloud actualizado al rango 45 a 268. Documento canónico: `_AUDITORIA_RRSS_op268.md`.
"""

for p in refs:
    if p.parent.exists():
        mode = "a" if p.exists() else "w"
        with open(p, mode, encoding="utf-8") as f:
            f.write(seccion)
        print(f"[OK] Actualizado {p}")
