import os, json
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv('.env.local')
client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'), timeout=20)

recs, _ = client.scroll(
    collection_name="diamantino_movimientos",
    limit=500,
    with_payload=True,
    with_vectors=False
)

print(f"Total puntos en diamantino_movimientos: {len(recs)}")

tipos = {}
personajes = {}
versiones = {}
sample_points = []

for r in recs:
    p = r.payload or {}
    t = p.get('tipo') or p.get('categoria') or p.get('tipo_movimiento')
    per = p.get('personaje')
    v = p.get('version') or p.get('episodio')
    tipos[t] = tipos.get(t, 0) + 1
    personajes[per] = personajes.get(per, 0) + 1
    versiones[v] = versiones.get(v, 0) + 1
    if len(sample_points) < 15:
        sample_points.append({'id': r.id, 'payload': p})

print("\nTipos de movimiento:", json.dumps(tipos, indent=2))
print("\nPersonajes:", json.dumps(personajes, indent=2))
print("\nVersiones / Episodios:", json.dumps(versiones, indent=2))
print("\nMuestra:", json.dumps(sample_points[:5], indent=2))

with open('forense_movimientos_analisis.json', 'w', encoding='utf-8') as f:
    json.dump({'total': len(recs), 'tipos': tipos, 'personajes': personajes, 'versiones': versiones, 'sample': sample_points}, f, indent=2)
