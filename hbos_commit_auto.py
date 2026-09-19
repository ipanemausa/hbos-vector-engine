"""
hbos_commit_auto.py — COMMIT Y PUSH SEMÁNTICO CON TRAZABILIDAD R768
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Gobernanza: DAG R768 · Autopilot Total
Reglas: R2 (Trazabilidad), R9 (Git commit + push)
"""

import os
import sys
import subprocess
import argparse
import math
import hashlib
import json
import time
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

def get_git_status():
    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, encoding="utf-8")
    return res.stdout.strip()

def get_latest_commit_hash():
    res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, encoding="utf-8")
    return res.stdout.strip()

def commit_auto(operation_id=None, message="autopilot synchronization", no_push=False):
    print("=" * 65)
    print(">>> [HBOS COMMIT AUTO] EJECUTANDO COMMIT SEMÁNTICO Y PUSH <<<")
    print("=" * 65)

    status = get_git_status()
    if not status:
        print("[*] No hay cambios pendientes en Git. Repositorio limpio.")
        current_hash = get_latest_commit_hash()
        return current_hash, False

    # Obtener el operation_id si no fue provisto
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=15)
    if operation_id is None:
        try:
            pt = client.retrieve("hbos_estado", ids=[1])
            if pt:
                rango = pt[0].payload.get("operation_ids", "45 a 214")
                last_id = int(rango.split()[-1])
                operation_id = last_id + 1
            else:
                operation_id = 215
        except Exception:
            operation_id = 215

    commit_msg = f"chore(autopilot): DAG R768 op {operation_id} - {message}"
    print(f"[*] Mensaje de commit: '{commit_msg}'")

    # Git add
    print("[1/3] Ejecutando git add .")
    subprocess.run(["git", "add", "."], check=True)

    # Git commit
    print("[2/3] Ejecutando git commit...")
    res_c = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True, encoding="utf-8")
    print(res_c.stdout.strip())
    new_hash = get_latest_commit_hash()

    # Git push
    if not no_push:
        print(f"[3/3] Ejecutando git push origin main...")
        res_p = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, encoding="utf-8")
        if res_p.returncode == 0:
            print(f"[OK] Push exitoso a origin/main (Commit: {new_hash})")
        else:
            print(f"[!] Alerta en push: {res_p.stderr.strip()}")
    else:
        print("[*] Push omitido por flag --no-push.")

    # Registrar en Qdrant registro_ecosistema
    try:
        t_reg = f"Commit automático semántico (op {operation_id}): {commit_msg} | Commit: {new_hash}"
        client.upsert(
            collection_name="registro_ecosistema",
            points=[models.PointStruct(id=operation_id, vector=generate_embedding(t_reg), payload={
                "operation_id": operation_id,
                "tipo": "git_commit_auto",
                "commit_hash": new_hash,
                "mensaje": commit_msg,
                "fecha": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "estado": "OK"
            })]
        )
        print(f"[OK] operation_id={operation_id} registrado en registro_ecosistema.")
    except Exception as e:
        print(f"[!] Error registrando en Qdrant: {e}")

    print("=" * 65)
    print(f"[OK] COMMIT SOBERANO COMPLETADO: {new_hash} (op {operation_id})")
    print("=" * 65)
    return new_hash, True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HBOS Commit Auto R768")
    parser.add_argument("--op", type=int, default=None, help="Operation ID explícito")
    parser.add_argument("--msg", type=str, default="autopilot synchronization", help="Mensaje del commit")
    parser.add_argument("--no-push", action="store_true", help="No ejecutar git push")
    args = parser.parse_args()

    commit_auto(operation_id=args.op, message=args.msg, no_push=args.no_push)
