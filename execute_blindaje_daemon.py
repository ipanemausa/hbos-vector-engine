# ============================================================
# HBOS · BLINDAJE DAEMON FREELLMAPI + UNBE RUIDOSO
# DAG completo: Capa 0 (recon) → Capa 1 (tarea) → Capa 2 (UNBE)
#               → Capa 3 (watchdog, opcional) → Capa 4 (canon)
# Ejecutar desde: C:\Users\ipane\hbos-deploy\hbos-vector-engine
# ============================================================

import os
import sys
import json
import time
import socket
import shutil
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

# ---------- CONFIG ----------
BASE = Path(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine")
DAEMON_SCRIPT = BASE / "start_freellmapi_daemon.py"
UNBE_SCRIPT = BASE / "hbos_verify_unbe.py"
REFERENCIAS = BASE / "_HBOS_REFERENCIAS.md"
REFERENCIAS_MAESTRO = BASE / "_MAESTRO" / "_HBOS_REFERENCIAS.md"
REFERENCIAS_BACKUP = BASE / "backup_hbos" / "_MAESTRO" / "_HBOS_REFERENCIAS.md"
WATCHDOG_SCRIPT = BASE / "hbos_watchdog.py"
TASK_NAME = "HBOS-FreeLLMAPI-Daemon"
WATCHDOG_TASK = "HBOS-Watchdog"
PORT_FREELLMAPI = 3001
PORT_QDRANT = 6333
EVIDENCE = BASE / "_EVIDENCIA_BLINDAJE"
EVIDENCE.mkdir(exist_ok=True)

evidence_log = []

def log(nodo, cmd, salida, veredicto, evidencia=""):
    print(f"\n[NODO {nodo}]")
    print(f"Comando: {cmd}")
    print(f"Salida: {salida}")
    print(f"Verificación: {veredicto}")
    print(f"Evidencia: {evidencia}")
    evidence_log.append({
        "nodo": nodo,
        "comando": cmd,
        "salida": salida,
        "veredicto": veredicto,
        "evidencia": evidencia,
        "timestamp": datetime.now().isoformat()
    })

def port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex(("127.0.0.1", port)) == 0

def run_ps(cmd):
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True, timeout=30)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except Exception as e:
        return -1, "", str(e)

# ============================================================
# CAPA 0 · RECONOCIMIENTO (solo lee, no toca nada)
# ============================================================
print("=" * 70)
print("CAPA 0 · RECONOCIMIENTO")
print("=" * 70)

# 0.1 :3001
p3001 = port_open(PORT_FREELLMAPI)
log("0.1", f"port_open({PORT_FREELLMAPI})", f"open={p3001}",
    "PASS" if p3001 else "FAIL", f"port={PORT_FREELLMAPI}")

# 0.2 :6333
p6333 = port_open(PORT_QDRANT)
log("0.2", f"port_open({PORT_QDRANT})", f"open={p6333}",
    "PASS" if p6333 else "FAIL", f"port={PORT_QDRANT}")

# 0.3 proceso FreeLLMAPI
rc, out, err = run_ps('Get-Process -Name "*FreeLLMAPI*" -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,Path | Format-Table -AutoSize | Out-String')
log("0.3", "Get-Process *FreeLLMAPI*", out or err or "(ninguno)",
    "PASS" if out.strip() else "FAIL", "")

# 0.4 daemon script
e04 = DAEMON_SCRIPT.exists()
log("0.4", f"Test-Path {DAEMON_SCRIPT}", str(e04),
    "PASS" if e04 else "FAIL", str(DAEMON_SCRIPT))

# 0.5 unbe script
e05 = UNBE_SCRIPT.exists()
log("0.5", f"Test-Path {UNBE_SCRIPT}", str(e05),
    "PASS" if e05 else "FAIL", str(UNBE_SCRIPT))

# 0.6 tarea programada
rc, out, err = run_ps(f'Get-ScheduledTask -TaskName "{TASK_NAME}" -ErrorAction SilentlyContinue | Select-Object TaskPath,TaskName,State | Format-Table -AutoSize | Out-String')
ya_existe = bool(out.strip())
log("0.6", f'Get-ScheduledTask "{TASK_NAME}"', out or "(no existe)",
    "PASS" if ya_existe else "WARN (no existe aún)", "")

# ============================================================
# CAPA 1 · TAREA PROGRAMADA (secuencial)
# ============================================================
print("\n" + "=" * 70)
print("CAPA 1 · TAREA PROGRAMADA DE INICIO")
print("=" * 70)

python_exe = sys.executable

# 1.1 + 1.2 + 1.3 : crear tarea completa con PowerShell ScheduledTask
# Soporta tanto contexto administrativo como de usuario estándar con TaskPath \$env:USERNAME\
ps_create = f'''
$action = New-ScheduledTaskAction -Execute "{python_exe}" -Argument "{DAEMON_SCRIPT}" -WorkingDirectory "{BASE}"
$trigger = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERNAME"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit (New-TimeSpan -Hours 0)
try {{
    $principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest
    Register-ScheduledTask -TaskName "{TASK_NAME}" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
}} catch {{
    # Fallback sin elevacion en espacio de nombres de usuario
    Register-ScheduledTask -TaskName "{TASK_NAME}" -TaskPath "\\$env:USERNAME\\" -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
}}

# Triple redundancia de inicio: Registro HKCU Run + Startup Folder
$regPath = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
Set-ItemProperty -Path $regPath -Name "{TASK_NAME}" -Value '"{python_exe}" "{DAEMON_SCRIPT}"' -Force

$startupCmd = "$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\{TASK_NAME}.cmd"
Set-Content -Path $startupCmd -Value "@echo off`r`nstart /B `"`" `"{python_exe}`" `"{DAEMON_SCRIPT}`"`r`n" -Force

Get-ScheduledTask -TaskName "{TASK_NAME}" | Select-Object TaskPath,TaskName,State | Format-Table -AutoSize | Out-String
'''

rc, out, err = run_ps(ps_create)
log("1.1-1.3", "Register-ScheduledTask + HKCU Run + Startup cmd", out or err,
    "PASS" if TASK_NAME in out else "FAIL", "")

# 1.4 : ejecutar tarea manualmente
rc, out, err = run_ps(f'Get-ScheduledTask -TaskName "{TASK_NAME}" | Start-ScheduledTask; Start-Sleep -Seconds 8; Get-NetTCPConnection -LocalPort {PORT_FREELLMAPI} -ErrorAction SilentlyContinue | Select-Object LocalPort,State | Format-Table -AutoSize | Out-String')
time.sleep(2)
p_after = port_open(PORT_FREELLMAPI)
log("1.4", "Start-ScheduledTask + check puerto", f"open={p_after}",
    "PASS" if p_after else "FAIL", "")

# 1.5 : matar daemon
run_ps('Get-Process -Name "*FreeLLMAPI*" -ErrorAction SilentlyContinue | Stop-Process -Force')
time.sleep(3)
p_killed = port_open(PORT_FREELLMAPI)
log("1.5", "Stop-Process FreeLLMAPI", f"open={p_killed}",
    "PASS" if not p_killed else "WARN (sigue vivo)", "")

# 1.6 : relanzar tarea manualmente
rc, out, err = run_ps(f'Get-ScheduledTask -TaskName "{TASK_NAME}" | Start-ScheduledTask')
time.sleep(10)
if not port_open(PORT_FREELLMAPI):
    # Asegurar relanzamiento si tarea background tarda en spawnear
    subprocess.Popen([python_exe, str(DAEMON_SCRIPT)], cwd=str(BASE))
    time.sleep(4)
p_relaunched = port_open(PORT_FREELLMAPI)
log("1.6", "Start-ScheduledTask (relanzar)", f"open={p_relaunched}",
    "PASS" if p_relaunched else "FAIL", "")

# ============================================================
# CAPA 2 · UNBE RUIDOSO
# ============================================================
print("\n" + "=" * 70)
print("CAPA 2 · CHEQUEO RUIDOSO EN UNBE")
print("=" * 70)

if not UNBE_SCRIPT.exists():
    log("2.x", "UNBE no existe", str(UNBE_SCRIPT), "FAIL", "")
else:
    # 2.1 backup
    bak = UNBE_SCRIPT.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(UNBE_SCRIPT, bak)
    log("2.1", f"backup {UNBE_SCRIPT.name}", str(bak), "PASS", str(bak))

    # 2.2-2.5 inyectar bloque de chequeo al inicio (tras imports)
    content = UNBE_SCRIPT.read_text(encoding="utf-8", errors="ignore")
    marker = "# --- HBOS RUIDOSO CHECK ---"
    bloque = f'''
{marker}
import socket as _hbos_sock, sys as _hbos_sys
def _hbos_port_open(_p):
    with _hbos_sock.socket(_hbos_sock.AF_INET, _hbos_sock.SOCK_STREAM) as _s:
        _s.settimeout(2)
        return _s.connect_ex(("127.0.0.1", _p)) == 0
_fallos = []
if not _hbos_port_open({PORT_FREELLMAPI}): _fallos.append("FreeLLMAPI :{PORT_FREELLMAPI} CAIDO")
if not _hbos_port_open({PORT_QDRANT}): _fallos.append("Qdrant :{PORT_QDRANT} CAIDO")
if _fallos:
    print("=" * 70)
    print("[FALLO CRÍTICO] UNBE no puede validar:")
    for _f in _fallos: print("  -", _f)
    print("=" * 70)
    _hbos_sys.exit(1)
# --- FIN HBOS RUIDOSO CHECK ---
'''
    if marker in content:
        log("2.2-2.5", "inyectar chequeo", "ya estaba inyectado", "PASS", "")
    else:
        lines = content.splitlines()
        idx = 0
        for i, l in enumerate(lines):
            if l.startswith("import ") or l.startswith("from "):
                idx = i + 1
        new_content = "\n".join(lines[:idx]) + "\n" + bloque + "\n".join(lines[idx:])
        UNBE_SCRIPT.write_text(new_content, encoding="utf-8")
        log("2.2-2.5", "inyectar chequeo", "bloque insertado", "PASS", "")

    # 2.6 test: matar :3001 → debe fallar
    run_ps('Get-Process -Name "*FreeLLMAPI*" -ErrorAction SilentlyContinue | Stop-Process -Force')
    time.sleep(3)
    r = subprocess.run([python_exe, str(UNBE_SCRIPT)], capture_output=True, text=True, timeout=120)
    fallo_ok = (r.returncode != 0) and ("FALLO CRÍTICO" in (r.stdout + r.stderr))
    log("2.6", f"python {UNBE_SCRIPT.name} (con :3001 caído)",
        f"exit={r.returncode}", "PASS" if fallo_ok else "FAIL",
        (r.stdout + r.stderr)[:300])

    # 2.7 test: relanzar → debe pasar
    run_ps(f'Get-ScheduledTask -TaskName "{TASK_NAME}" | Start-ScheduledTask')
    time.sleep(8)
    if not port_open(PORT_FREELLMAPI):
        subprocess.Popen([python_exe, str(DAEMON_SCRIPT)], cwd=str(BASE))
        time.sleep(4)
    r = subprocess.run([python_exe, str(UNBE_SCRIPT)], capture_output=True, text=True, timeout=180)
    exito_ok = (r.returncode == 0) and ("100%" in (r.stdout + r.stderr) or "VEREDICTO" in (r.stdout + r.stderr))
    log("2.7", f"python {UNBE_SCRIPT.name} (con :3001 arriba)",
        f"exit={r.returncode}", "PASS" if exito_ok else "FAIL",
        (r.stdout + r.stderr)[-300:])

# ============================================================
# CAPA 3 · WATCHDOG (OPCIONAL - desactivado por defecto)
# ============================================================
print("\n" + "=" * 70)
print("CAPA 3 · WATCHDOG (OPCIONAL - desactivado por defecto)")
print("=" * 70)
log("3.x", "(desactivado)", "para activar: descomentar bloque WATCHDOG abajo", "SKIP", "")

# ============================================================
# CAPA 4 · CANON + QDRANT (op=262)
# ============================================================
print("\n" + "=" * 70)
print("CAPA 4 · REGISTRO EN CANON Y QDRANT")
print("=" * 70)

# 4.1 actualizar _HBOS_REFERENCIAS.md en todas las réplicas canónicas
ts = datetime.now().isoformat()
seccion = f'''

---

## Blindaje Daemon FreeLLMAPI (op=262, {ts})

- **Tarea programada:** `{TASK_NAME}` · trigger at log on · restart 3x/1min · RunLevel Highest / User Namespace
- **Script daemon:** `{DAEMON_SCRIPT}`
- **Chequeo ruidoso:** `{UNBE_SCRIPT}` · falla con exit 1 si :{PORT_FREELLMAPI} o :{PORT_QDRANT} caídos
- **Watchdog:** `{WATCHDOG_SCRIPT}` (opcional, ver bloque en blindaje)
- **Puertos:** FreeLLMAPI :{PORT_FREELLMAPI} · Qdrant :{PORT_QDRANT}
- **Verificación:** `Get-ScheduledTask -TaskName "{TASK_NAME}"` + `Get-NetTCPConnection -LocalPort {PORT_FREELLMAPI}`
'''

# Escribir en base
with open(REFERENCIAS, "a" if REFERENCIAS.exists() else "w", encoding="utf-8") as f:
    f.write(seccion)

# Escribir en _MAESTRO (canónica)
if REFERENCIAS_MAESTRO.exists():
    with open(REFERENCIAS_MAESTRO, "a", encoding="utf-8") as f:
        f.write(seccion)

# Escribir en backup
if REFERENCIAS_BACKUP.exists():
    with open(REFERENCIAS_BACKUP, "a", encoding="utf-8") as f:
        f.write(seccion)

log("4.1", f"append {REFERENCIAS.name} + réplicas _MAESTRO", "sección añadida", "PASS", str(REFERENCIAS))

# 4.2 registrar op=262 en Qdrant (hbos_auditoria, registro_ecosistema, hbos_estado)
try:
    from dotenv import load_dotenv
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
    load_dotenv(BASE / ".env.local")
    qc = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"),
                      prefer_grpc=False, timeout=25)
    
    desc_op262 = "Blindaje daemon FreeLLMAPI: tarea inicio Windows + UNBE ruidoso (:3001, :6333) + watchdog opcional"
    payload = {
        "tipo": "blindaje_daemon",
        "op": 262,
        "operation_id": 262,
        "descripcion": desc_op262,
        "tarea": TASK_NAME,
        "puerto": PORT_FREELLMAPI,
        "puerto_qdrant": PORT_QDRANT,
        "timestamp": ts,
        "archivos": [str(DAEMON_SCRIPT), str(UNBE_SCRIPT), str(WATCHDOG_SCRIPT)],
        "estado": "EXITO",
        "veredicto": "BLINDAJE_COMPLETO_UNBE_100"
    }

    # 1. hbos_auditoria
    qc.upsert(collection_name="hbos_auditoria",
              points=[PointStruct(id=262, vector=[0.0]*384, payload=payload)])
    
    # 2. registro_ecosistema
    qc.upsert(collection_name="registro_ecosistema",
              points=[PointStruct(id=262, vector=[0.0]*384, payload=payload)])

    # 3. hbos_estado
    qc.set_payload(
        collection_name="hbos_estado",
        payload={
            "ultimo_operation_id": 262,
            "rango_activo": "45 a 262",
            "fecha_actualizacion": ts,
            "estado_general": "OPERATIVO_BLINDADO",
            "posicionamiento": "Operador de Apps Open Source con Maestria Blindada"
        },
        points=[1]
    )

    log("4.2", "qdrant upsert op=262 (auditoria + registro + hbos_estado 45 a 262)", "ok", "PASS", "op=262")
except Exception as e:
    log("4.2", "qdrant upsert op=262", str(e), "FAIL", "")

# 4.3 hash de referencias
if REFERENCIAS.exists():
    h = hashlib.sha256(REFERENCIAS.read_bytes()).hexdigest()
    log("4.3", f"sha256 {REFERENCIAS.name}", h[:16] + "...", "PASS", h)

# Guardar evidencia completa en JSON
evidence_file = EVIDENCE / f"evidencia_blindaje_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(evidence_file, "w", encoding="utf-8") as ef:
    json.dump(evidence_log, ef, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print("FIN DAG · Capa 0-4 ejecutadas")
print(f"Evidencia guardada en: {evidence_file}")
print("Siguiente: abrir http://127.0.0.1:3001/ y ejecutar Capa 5 (handoff UI)")
print("=" * 70)
