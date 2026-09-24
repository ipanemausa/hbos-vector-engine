# HBOS · REPARACIÓN ROUTING · op=301

## Problema detectado

- HuggingFace: HTTP 403 (token roto/revocado).
- Google: HTTP 503 (saturado).
- Cooldowns activos: 6.
- Cadenas apuntaban a HuggingFace.

## Solución aplicada

1. Verificación token HuggingFace.
2. Limpieza de cooldowns.
3. Reconfiguración de cadenas con OpenRouter + Google.

## Estado final

- Cooldowns: 0.
- Cadenas: reconfiguradas.
- Uso: auto + OpenRouter.

Fecha: 20260924_120318
