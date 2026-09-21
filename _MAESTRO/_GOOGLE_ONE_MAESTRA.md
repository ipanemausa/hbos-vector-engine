# _GOOGLE_ONE_MAESTRA.md — Capa C: Almacenamiento Masivo y Réplicas (5TB)
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 232 | **Fecha:** 2026-09-21 | **Versión:** v1.3 Canónica | **Estado:** ✅ ESTRUCTURA DE ALMACENAMIENTO CANÓNICA  
> **Canon:** Arquitectura Desacoplada (§D) · Capa C (Almacenamiento) · Patrón P-03 (Triple Redundancia)

---

## 1. Definición y Topología del Almacenamiento
La **Capa C (Almacenamiento)** provee la infraestructura en la nube para persistir activos multimedia masivos, checkpoints de modelos y respaldos inmutables:

* **Capacidad Contratada:** 5 TB (Google One / Google Workspace).
* **Cuenta Titular (Facturación):** `IPANEMAMARKETINGUSA@gmail.com` (Capa A).
* **Cuenta Beneficiaria (Operativa):** `hbos@gmail.com` (Capa B), mediante grupo familiar o unidad compartida.
* **Montaje Local:** `G:\My Drive\HBOS-Diamantino` vía Google Drive for Desktop.

---

## 2. Asignación de Cuotas y Directorios
| Subdirectorio en Drive | Propósito | Volumen Estimado |
| :--- | :--- | :--- |
| `_MAESTRO/` | Réplica 2 de documentación canónica inmutable (SHA256 estricto) | < 50 MB |
| `_SANDBOX/FreeLLMAPI/` | Binarios portables y entornos de ejecución de 235 modelos | ~3.5 GB |
| `Ep01` a `Ep04` | Videos master 1080p/4K, clips Wan 2.1, pistas de voz y BGM | ~150 GB |
| `assets/avatar/` | Retratos maestros HD, videos de presentación y speech sintetizado | ~20 GB |
| `backups_vectoriales/` | Snapshots periódicos de las 20 colecciones de Qdrant Cloud | ~10 GB |
| `model_checkpoints/` | Checkpoints de Wan 2.1, CosyVoice2 y pesos de modelos abiertos | ~500 GB |
| **Reserva Libre** | Escalabilidad para producción de series de video de 50+ episodios | ~4.3 TB |

---

## 3. Protocolo de Sincronización Inmutable
* Los archivos maestros en `_MAESTRO` deben coincidir exactamente en SHA256 entre `Local`, `Drive` y `Backup`.
* La sincronización se ejecuta tras cada operación mediante scripts automáticos (`shutil.copy2`), auditados por `hbos_verify_unbe.py`.
