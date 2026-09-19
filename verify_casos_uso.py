import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
pts = client.retrieve("diamantino_casos_uso", ids=list(range(1, 8)))

print(f"Total tareas en 'diamantino_casos_uso': {len(pts)}")
for p in sorted(pts, key=lambda x: x.id):
    pl = p.payload
    print(f"ID {p.id}: {pl['tarea']}")
    print(f"   Modelo Principal: {pl['modelo_principal']}")
    print(f"   Alternativas:     {', '.join(pl['alternativas'])}")
    print(f"   Compresión:       {pl['compresion']}")
    print(f"   Cuándo usar:      {pl['cuando_usar']}")
    print(f"   Fallback:         {pl['fallback']}")
    print(f"   Arbitraje:        {pl['arbitraje']}")
