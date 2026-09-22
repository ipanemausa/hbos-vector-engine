import json

data = json.load(open('forense_qdrant_ecosistema.json', encoding='utf-8'))
for d in data:
    op = d.get('op')
    if op in [244, 245, 247, 248, 249, 250, 257, 258]:
        print(f"=== OP={op} ===")
        print(f"Tipo: {d.get('tipo')}")
        print(f"Fecha: {d.get('fecha')}")
        print(f"Desc: {d.get('desc')}")
        p = d.get('payload', {})
        for k in ['video_id', 'sha256', 'archivo', 'master', 'rules']:
            if k in p:
                print(f"  {k}: {p[k]}")
