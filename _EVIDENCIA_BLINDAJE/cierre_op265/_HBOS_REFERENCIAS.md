

---

## Blindaje Daemon FreeLLMAPI (op=262, 2026-09-22T14:12:34.637959)

- **Tarea programada:** `HBOS-FreeLLMAPI-Daemon` · trigger at log on · restart 3x/1min · RunLevel Highest / User Namespace
- **Script daemon:** `C:\Users\ipane\hbos-deploy\hbos-vector-engine\start_freellmapi_daemon.py`
- **Chequeo ruidoso:** `C:\Users\ipane\hbos-deploy\hbos-vector-engine\hbos_verify_unbe.py` · falla con exit 1 si :3001 o :6333 caídos
- **Watchdog:** `C:\Users\ipane\hbos-deploy\hbos-vector-engine\hbos_watchdog.py` (opcional, ver bloque en blindaje)
- **Puertos:** FreeLLMAPI :3001 · Qdrant :6333
- **Verificación:** `Get-ScheduledTask -TaskName "HBOS-FreeLLMAPI-Daemon"` + `Get-NetTCPConnection -LocalPort 3001`
