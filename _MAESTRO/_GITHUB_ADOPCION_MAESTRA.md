# _GITHUB_ADOPCION_MAESTRA.md — Capa D: Control de Versiones, Repositorio y CI/CD
> **Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI**  
> **Operación:** 232 | **Fecha:** 2026-09-21 | **Versión:** v1.3 Canónica | **Estado:** ✅ EN PRODUCCIÓN · SINCRONIZADO  
> **Canon:** Arquitectura Desacoplada (§D) · Capa D (Repositorio)

---

## 1. Topología del Repositorio
La **Capa D (Repositorio)** es la fuente única de verdad para el código, scripts de orquestación y documentos maestros del ecosistema:

* **Repositorio Remoto:** `https://github.com/ipanemausa/hbos-vector-engine.git`
* **Organización / Propietario:** `ipanemausa`
* **Rama Principal Canónica:** `main` (protegida contra commits no firmados o regresiones).
* **Autenticación Git:** Personal Access Token / SSH vinculado a la cuenta matriz.

---

## 2. Invariantes de Control de Versiones (R2, R9)
1. **R2 · Trazabilidad Semántica:** Cada commit debe explicitar el número de operación (`op=XXX`) y describir las mutaciones realizadas en los subsistemas.
2. **R9 · Push Inmediato:** Toda operación exitosa concluye con commit y push a `origin/main`.
3. **Invariante de Exclusión de Binarios:** Archivos de video pesados (`.mp4`), WAV crudos y directorios scratch están excluidos vía `.gitignore` y son persistidos en Google Drive (Capa C). El repositorio mantiene únicamente código fuente, prompts, configuraciones y documentación.

---

## 3. Plan de Adopción de GitHub Actions
* **Workflow 1 · `unbe-healthcheck.yml`:** Ejecución programada (cron) de verificación de endpoints públicos y consistencia del DAG.
* **Workflow 2 · `qdrant-backup.yml`:** Disparo de snapshots vectoriales hacia almacenamiento seguro.
