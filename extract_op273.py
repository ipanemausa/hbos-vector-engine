import os
import json
import sqlite3
from dotenv import load_dotenv

# Load env for Qdrant
load_dotenv(r'C:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local')

data = {}

# 1. FREELMAPI DB
db_path = os.path.expandvars(r'%APPDATA%\FreeLLMAPI\freeapi.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1.1 models enabled=1
    cur.execute("SELECT id, model_id, display_name, platform, intelligence_rank, speed_rank, context_window FROM models WHERE enabled=1")
    cols = ['id', 'model_id', 'display_name', 'platform', 'intelligence_rank', 'speed_rank', 'context_window']
    data['models_enabled'] = [dict(zip(cols, row)) for row in cur.fetchall()]
    
    # 1.2 fallback_config
    cur.execute("SELECT id, model_db_id, priority, enabled FROM fallback_config")
    cols_fb = ['id', 'model_db_id', 'priority', 'enabled']
    data['fallback_config'] = [dict(zip(cols_fb, row)) for row in cur.fetchall()]
    
    # 1.3 client_profiles
    cur.execute("SELECT id, name, enabled FROM client_profiles")
    cols_cp = ['id', 'name', 'enabled']
    data['client_profiles'] = [dict(zip(cols_cp, row)) for row in cur.fetchall()]
    
    # 1.4 api_keys (masked)
    cur.execute("SELECT id, platform, label, status, enabled FROM api_keys")
    cols_ak = ['id', 'platform', 'label', 'status', 'enabled']
    data['api_keys'] = [dict(zip(cols_ak, row)) for row in cur.fetchall()]
    
    # 1.5 embedding_models
    cur.execute("SELECT id, family, platform, model_id, dimensions FROM embedding_models")
    cols_em = ['id', 'family', 'platform', 'model_id', 'dimensions']
    data['embedding_models'] = [dict(zip(cols_em, row)) for row in cur.fetchall()]
    
    # 1.6 media_models
    cur.execute("SELECT id, platform, model_id, modality FROM media_models")
    cols_mm = ['id', 'platform', 'model_id', 'modality']
    data['media_models'] = [dict(zip(cols_mm, row)) for row in cur.fetchall()]
    conn.close()
else:
    data['error_db'] = f"DB not found at {db_path}"

# 2. QDRANT
from qdrant_client import QdrantClient
try:
    qc = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'), timeout=20)
    
    # 2.1 hbos_canon
    canon_info = qc.get_collection('hbos_canon')
    canon_count = canon_info.points_count
    # sample or range
    data['hbos_canon'] = {'count': canon_count}
    
    # 2.2 hbos_estado
    p1 = qc.retrieve('hbos_estado', ids=[1])
    data['hbos_estado'] = p1[0].payload if p1 else None
    
    # 2.3 hbos_auditoria (ultimas 10)
    audit_points, _ = qc.scroll('hbos_auditoria', limit=100)
    audit_points_sorted = sorted(audit_points, key=lambda p: p.id, reverse=True)[:10]
    data['hbos_auditoria_ultimas_10'] = [{'id': p.id, 'payload': p.payload} for p in audit_points_sorted]
    
    # 2.4 hbos_referencias
    ref_info = qc.get_collection('hbos_referencias')
    data['hbos_referencias'] = {'count': ref_info.points_count}
    
    # 2.5 registro_ecosistema (ultimas 10)
    eco_points, _ = qc.scroll('registro_ecosistema', limit=100)
    eco_points_sorted = sorted(eco_points, key=lambda p: p.id, reverse=True)[:10]
    data['registro_ecosistema_ultimas_10'] = [{'id': p.id, 'payload': p.payload} for p in eco_points_sorted]

except Exception as e:
    data['error_qdrant'] = str(e)

# 3. REPO
# 3.1 routing_rules_295.json
rules_path = r'C:\Users\ipane\hbos-deploy\hbos-vector-engine\routing_rules_295.json'
if os.path.exists(rules_path):
    with open(rules_path, 'r', encoding='utf-8') as f:
        rr = json.load(f)
    if isinstance(rr, list):
        data['routing_rules'] = {'total': len(rr), 'primeras_10': rr[:10]}
    elif isinstance(rr, dict):
        data['routing_rules'] = {'keys': list(rr.keys()), 'total': len(rr.get('rules', [])), 'primeras_10': rr.get('rules', [])[:10]}
else:
    data['routing_rules'] = 'Not found'

# 3.2 _HBOS_REFERENCIAS.md
ref_md_path = r'C:\Users\ipane\hbos-deploy\hbos-vector-engine\_HBOS_REFERENCIAS.md'
if os.path.exists(ref_md_path):
    with open(ref_md_path, 'r', encoding='utf-8') as f:
        data['hbos_referencias_md'] = f.read()
else:
    data['hbos_referencias_md'] = 'Not found'

# 3.3 _MAESTRO/*.md primeras 20 lineas
maestro_dir = r'C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO'
maestro_samples = {}
if os.path.exists(maestro_dir):
    for fn in sorted(os.listdir(maestro_dir)):
        if fn.endswith('.md'):
            fp = os.path.join(maestro_dir, fn)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = [f.readline() for _ in range(20)]
                    maestro_samples[fn] = ''.join(lines).strip()
            except Exception as e:
                maestro_samples[fn] = f'Error: {e}'
data['maestro_samples'] = maestro_samples

with open('extracted_op273.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("[OK] Datos extraidos y guardados en extracted_op273.json")
print("Models enabled:", len(data.get('models_enabled', [])))
print("Fallbacks:", len(data.get('fallback_config', [])))
print("Client profiles:", len(data.get('client_profiles', [])))
print("API keys:", len(data.get('api_keys', [])))
print("Embedding models:", len(data.get('embedding_models', [])))
print("Media models:", len(data.get('media_models', [])))
print("Qdrant canon count:", data.get('hbos_canon', {}).get('count'))
print("Qdrant estado:", data.get('hbos_estado'))
print("Qdrant auditoria count:", len(data.get('hbos_auditoria_ultimas_10', [])))
print("Qdrant referencias count:", data.get('hbos_referencias', {}).get('count'))
print("Qdrant ecosistema count:", len(data.get('registro_ecosistema_ultimas_10', [])))
print("Maestro samples count:", len(data.get('maestro_samples', {})))
