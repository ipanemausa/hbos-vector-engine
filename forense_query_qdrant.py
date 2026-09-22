import os, time, json
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv('.env.local')

client = None
for attempt in range(6):
    try:
        client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'), prefer_grpc=False, timeout=30)
        _ = client.get_collections()
        print("[OK] Connected to Qdrant")
        break
    except Exception as e:
        print(f"Retry {attempt+1}: {e}")
        time.sleep(2)

if client:
    try:
        recs, _ = client.scroll(
            collection_name="registro_ecosistema",
            limit=500,
            with_payload=True,
            with_vectors=False
        )
        ops_matching = []
        for r in recs:
            p = r.payload or {}
            p_str = json.dumps(p).lower()
            if any(k in p_str for k in ['video', 'demis', 'anchor', 'movimiento', 'ep02', 'ep03', 'ep04']):
                ops_matching.append({
                    'id': r.id,
                    'op': p.get('op') or p.get('operation_id'),
                    'tipo': p.get('tipo'),
                    'fecha': p.get('fecha') or p.get('timestamp'),
                    'desc': p.get('descripcion') or p.get('description'),
                    'payload': p
                })
        with open('forense_qdrant_ecosistema.json', 'w', encoding='utf-8') as f:
            json.dump(ops_matching, f, indent=2)
        print(f"[OK] Found {len(ops_matching)} matches in registro_ecosistema")
    except Exception as e:
        print(f"Error scrolling: {e}")
