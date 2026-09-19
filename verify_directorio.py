import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

pts = client.retrieve("hbos_directorio", ids=list(range(1, 8)))
print(f"Total componentes en 'hbos_directorio': {len(pts)}")
for p in sorted(pts, key=lambda x: x.id):
    pl = p.payload
    print(f"ID {p.id}: {pl['componente']} ({pl['tipo']})")
    print(f"   Local: {pl['ubicacion_local']}")
    print(f"   Nube:  {pl['ubicacion_nube']}")
    print(f"   Acceso: {pl['como_acceder']}")
    print(f"   Op ID: {pl['operation_id']}")
