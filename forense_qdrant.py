import os, sys, json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv('.env.local')

client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'), prefer_grpc=False, timeout=30)

results = {}

# 1. Search registro_ecosistema for video, anchor, demis, ep02, ep03, ep04
print("[*] Searching registro_ecosistema...")
try:
    recs, _ = client.scroll(
        collection_name="registro_ecosistema",
        limit=500,
        with_payload=True,
        with_vectors=False
    )
    video_ops = []
    for r in recs:
        payload = r.payload or {}
        p_str = json.dumps(payload).lower()
        if any(w in p_str for w in ['video', 'anchor', 'demis', 'ep02', 'ep03', 'ep04', 'movimiento', 'v1', 'v2', 'v3']):
            video_ops.append({
                'id': r.id,
                'op': payload.get('op') or payload.get('operation_id'),
                'tipo': payload.get('tipo'),
                'fecha': payload.get('fecha') or payload.get('timestamp'),
                'desc': payload.get('descripcion') or payload.get('description') or payload.get('resumen'),
                'payload_keys': list(payload.keys()),
                'payload': payload
            })
    results['registro_ecosistema_matches'] = video_ops
    print(f"Found {len(video_ops)} matching operations in registro_ecosistema")
except Exception as e:
    results['registro_ecosistema_error'] = str(e)
    print(f"Error in registro_ecosistema: {e}")

# 2. Search diamantino_assets
print("[*] Searching diamantino_assets...")
try:
    recs, _ = client.scroll(
        collection_name="diamantino_assets",
        limit=500,
        with_payload=True,
        with_vectors=False
    )
    assets = []
    for r in recs:
        payload = r.payload or {}
        assets.append({
            'id': r.id,
            'payload': payload
        })
    results['diamantino_assets'] = assets
    print(f"Found {len(assets)} in diamantino_assets")
except Exception as e:
    results['diamantino_assets_error'] = str(e)
    print(f"Error in diamantino_assets: {e}")

# 3. Search diamantino_movimientos
print("[*] Searching diamantino_movimientos...")
try:
    recs, _ = client.scroll(
        collection_name="diamantino_movimientos",
        limit=500,
        with_payload=True,
        with_vectors=False
    )
    movs = []
    for r in recs:
        payload = r.payload or {}
        movs.append({
            'id': r.id,
            'payload': payload
        })
    results['diamantino_movimientos_sample'] = movs[:30]
    results['diamantino_movimientos_count'] = len(movs)
    print(f"Found {len(movs)} in diamantino_movimientos")
except Exception as e:
    results['diamantino_movimientos_error'] = str(e)
    print(f"Error in diamantino_movimientos: {e}")

# 4. Search hbos_metricas
print("[*] Searching hbos_metricas...")
try:
    recs, _ = client.scroll(
        collection_name="hbos_metricas",
        limit=500,
        with_payload=True,
        with_vectors=False
    )
    mets = []
    for r in recs:
        payload = r.payload or {}
        mets.append({
            'id': r.id,
            'payload': payload
        })
    results['hbos_metricas'] = mets
    print(f"Found {len(mets)} in hbos_metricas")
except Exception as e:
    results['hbos_metricas_error'] = str(e)
    print(f"Error in hbos_metricas: {e}")

with open('forense_qdrant.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
print("[OK] Saved forense_qdrant.json")
