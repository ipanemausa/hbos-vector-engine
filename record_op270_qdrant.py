import os
from datetime import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

load_dotenv(r'C:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local')
qc = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'), timeout=20)

payload = {
    'op': 270,
    'tipo': 'hibrido_llmapi_drive_r768',
    'descripcion': 'Sistema híbrido: memoria LLMAPI comprimida R768 + tar.gz → Drive + Backup',
    'timestamp': datetime.now().isoformat(),
    'tarball': r'G:\My Drive\HBOS-Diamantino\_BACKUP_LLMAPI\llmapi_20260922_182824.tar.gz',
    'tamano_mb': round(1.0233039855957, 2),
    'ratio_compresion': 90.8,
}
qc.upsert(collection_name='hbos_auditoria', points=[PointStruct(id=270, vector=[0.0]*384, payload=payload)])
qc.upsert(collection_name='registro_ecosistema', points=[PointStruct(id=270, vector=[0.0]*384, payload=payload)])
print('[OK] op=270 registrado en Qdrant')
try:
    qc.set_payload(collection_name='hbos_estado', payload={'rango': '45 a 270'}, points=[1])
    print('[OK] hbos_estado actualizado a 45-270')
except Exception as e:
    print(f'[!] hbos_estado: {e}')
