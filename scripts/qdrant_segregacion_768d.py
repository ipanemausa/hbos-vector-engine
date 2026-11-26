"""
HBOS QDRANT 768D SEGREGATION SCHEMA (Fase 2)
Arquitectura segregada estilo Karpathy:
- Mínima, explícita y transparente.
- 5 Nodos con vectores 768d (Cosine).
- Trazabilidad estricta: SHA256, ruta absoluta validada y estado (approved / deprecated).
"""

import json
import urllib.request
import hashlib
import os

QDRANT_HOST = "http://localhost:6333"

# Definición canónica de las 5 colecciones segregadas en 768d
COLLECTIONS_SCHEMA = {
    "hbos_nodo_texto_768d": {
        "descripcion": "Guiones aprobados, prompts narrativos y transcripciones SRT",
        "vector_size": 768,
        "distance": "Cosine"
    },
    "hbos_nodo_voz_768d": {
        "descripcion": "Masters de voz clonada aprobados de Guillermo Alonso Hoyos / Guía Hoy (-14 LUFS)",
        "vector_size": 768,
        "distance": "Cosine"
    },
    "hbos_nodo_avatar_768d": {
        "descripcion": "Activos de presentador / avatar con canal alfa y transparencia (PNG/WebM)",
        "vector_size": 768,
        "distance": "Cosine"
    },
    "hbos_nodo_video_768d": {
        "descripcion": "Clips de escena base, fondos y capas gráficas de análisis",
        "vector_size": 768,
        "distance": "Cosine"
    },
    "hbos_nodo_maestro_manifest_768d": {
        "descripcion": "Manifiesto vinculante E2E que enlaza los IDs exactos aprobados de cada nodo",
        "vector_size": 768,
        "distance": "Cosine"
    }
}

def qdrant_request(endpoint, method="GET", data=None):
    url = f"{QDRANT_HOST}{endpoint}"
    req = urllib.request.Request(url, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
        encoded = json.dumps(data).encode("utf-8")
        req.data = encoded
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        return {"error": e.code, "message": err_msg}

def calcular_sha256(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        return None
    h = hashlib.sha256()
    with open(ruta_archivo, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def auditar_qdrant_vivo():
    print("=== AUDITORÍA REAL QDRANT (http://localhost:6333) ===")
    res = qdrant_request("/collections")
    if "result" not in res:
        print("Error conectando a Qdrant:", res)
        return
    
    colecciones = res["result"]["collections"]
    print(f"Total colecciones activas: {len(colecciones)}\n")
    print(f"{'Colección':<35} | {'Dim':<6} | {'Distancia':<8} | {'Puntos':<7} | {'Diagnóstico':<20}")
    print("-" * 85)
    
    for c in colecciones:
        cname = c["name"]
        info = qdrant_request(f"/collections/{cname}")["result"]
        v_params = info.get("config", {}).get("params", {}).get("vectors", {})
        if isinstance(v_params, dict) and "size" in v_params:
            size = v_params["size"]
            dist = v_params["distance"]
        else:
            size = "Multi/N/A"
            dist = "N/A"
        pts = info.get("points_count", 0)
        
        if size == 768:
            diag = "OK (768d Activo)"
        elif size == 384:
            diag = "LEGACY (Requiere migración)"
        elif size == 3072:
            diag = "DESAJUSTE (3072d Legacy)"
        else:
            diag = "REVISAR"
            
        print(f"{cname:<35} | {str(size):<6} | {dist:<8} | {str(pts):<7} | {diag:<20}")

def inicializar_colecciones_segregadas(dry_run=True):
    print(f"\n=== {'SIMULACIÓN' if dry_run else 'APLICACIÓN'} DEL ESQUEMA SEGREGADO 768D ===")
    for cname, conf in COLLECTIONS_SCHEMA.items():
        payload = {
            "vectors": {
                "size": conf["vector_size"],
                "distance": conf["distance"]
            }
        }
        if dry_run:
            print(f"[DRY-RUN] PUT /collections/{cname} -> {payload}")
        else:
            res = qdrant_request(f"/collections/{cname}", method="PUT", data=payload)
            print(f"[CREAR] {cname}: {res.get('status', res)}")

if __name__ == "__main__":
    auditar_qdrant_vivo()
    inicializar_colecciones_segregadas(dry_run=True)
