import os, sys, json, time
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv('.env.local')

client = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'), timeout=25)

print("=== PLANO A: Audit hbos_canon ===")
pts_canon = client.get_collection("hbos_canon").points_count
print(f"Total puntos en hbos_canon: {pts_canon}")

recs_canon, _ = client.scroll("hbos_canon", limit=200, with_payload=True)
canon_ids = [r.id for r in recs_canon]
print(f"Rango de IDs en hbos_canon: min={min(canon_ids)}, max={max(canon_ids)}")

doctrina_ids = [101, 102, 103, 104, 105, 106, 107, 108, 109]
present_doctrina = [r for r in recs_canon if r.id in doctrina_ids]
print(f"Doctrina IDs presentes ({len(present_doctrina)}/9): {[r.id for r in present_doctrina]}")
for r in present_doctrina:
    p = r.payload or {}
    print(f"  ID {r.id}: {p.get('regla') or p.get('nombre') or p.get('codigo')} -> {p.get('titulo') or p.get('descripcion')}")

# Contar reglas R1 a R76
reglas_r = [r for r in recs_canon if r.id <= 76]
print(f"Puntos <= 76: {len(reglas_r)}")

print("\n=== PLANO B & C: Audit diamantino_movimientos & P-14-07b ===")
pts_movs = client.get_collection("diamantino_movimientos").points_count
print(f"Total puntos en diamantino_movimientos: {pts_movs}")

# Chequear ID=321 (P-14-07b)
p321 = client.retrieve("diamantino_movimientos", [321])
if p321:
    print(f"P-14-07b ID=321 encontrado: {p321[0].payload.get('id')} / {p321[0].payload.get('nombre')}")
    print(f"  Archivo: {p321[0].payload.get('archivo_master')} | Hash: {p321[0].payload.get('sha256')}")
else:
    print("[FAIL] P-14-07b no encontrado en ID=321")

print("\n=== PLANO F: Audit recursos_hbos & links ===")
pts_rec = client.get_collection("recursos_hbos").points_count
print(f"Total puntos en recursos_hbos: {pts_rec}")

recs_recursos, _ = client.scroll("recursos_hbos", limit=200, with_payload=True)
sample_recursos = [r.payload for r in recs_recursos[:5]]
print("Muestra recursos_hbos keys:", list(sample_recursos[0].keys()) if sample_recursos else "None")
print("Muestra tipo/categoria recursos_hbos:", set(r.payload.get('tipo') or r.payload.get('categoria') for r in recs_recursos))

# Buscar links especificos
found_dh = []
found_chibi = []
for r in recs_recursos:
    p_str = json.dumps(r.payload).lower()
    if 'c0gerqtnnfe' in p_str:
        found_dh.append(r.id)
    if 'zsab8k0ms-y' in p_str or 'chibi' in p_str:
        found_chibi.append(r.id)

print(f"Link DH (C0gErQtnNFE) en recursos_hbos: {found_dh}")
print(f"Link Chibi (ZsaB8K0Ms-Y) en recursos_hbos: {found_chibi}")

# Buscar links en todo el repo
print("\n=== PLANO I: Audit Estado Global ===")
p_est = client.retrieve("hbos_estado", [1])
print(f"hbos_estado ID=1: {p_est[0].payload if p_est else 'None'}")
p_reg = client.retrieve("registro_ecosistema", [259])
print(f"registro_ecosistema op=259: {p_reg[0].payload.get('tipo') if p_reg else 'None'}")
