import os
import sys
import shutil
import hashlib
import json
import math
import subprocess
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

print("==========================================================================")
print(">>> [EJECUCIÓN INTEGRAL] BLOQUE 1 Y BLOQUE 2 EN PARALELO (op 117-124) <<<")
print("==========================================================================")

# --- 1. COPIA Y SINCRONIZACIÓN DE SCRIPTS Y MAESTROS ---
local_maestro = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\_MAESTRO"
drive_maestro = r"G:\My Drive\HBOS-Diamantino\_MAESTRO"
backup_maestro = r"C:\Users\ipane\backup_hbos\_MAESTRO"
sandbox_playwright = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\Playwright"

os.makedirs(drive_maestro, exist_ok=True)
os.makedirs(backup_maestro, exist_ok=True)
os.makedirs(sandbox_playwright, exist_ok=True)
os.makedirs(os.path.join(sandbox_playwright, "mapas"), exist_ok=True)

# Copiar scripts a Sandbox
shutil.copy2("map_app.py", os.path.join(sandbox_playwright, "map_app.py"))
shutil.copy2("navigate_app.py", os.path.join(sandbox_playwright, "navigate_app.py"))
print("[OK] Scripts map_app.py y navigate_app.py copiados a Sandbox Playwright.")

# Sincronizar documentos de arquitectura a Drive y Backup
nuevos_docs = [
    "_HBOS_API_KEY_VAULT.md",
    "_AGENTE_ORQUESTADOR.md",
    "_TAREAS_AUTOMATICAS.md"
]
for doc in nuevos_docs:
    src = os.path.join(local_maestro, doc)
    shutil.copy2(src, os.path.join(drive_maestro, doc))
    shutil.copy2(src, os.path.join(backup_maestro, doc))
    print(f"[OK] {doc} sincronizado en triple redundancia.")

# --- 2. VECTORIZACIÓN EN QDRANT ---
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    else:
        vec = [1.0 / math.sqrt(dim)] * dim
    return vec

# A. TAREA 1.3: P-17 v2, P-34, L-20 (operation_id = 117)
print("[*] Registrando TAREA 1.3 en Qdrant (P-17 v2, P-34, L-20)...")
p17_v2 = {
    "codigo": "P-17",
    "nombre": "Modelo_Divulgacion_Con_Credito_Canal_Difusion_v2",
    "descripcion": "HBOS-Diamantino es un Canal de Difusión de IA. Los hosts cristalinos son ANCHORS que presentan contenido verificado. Formato tipo Alejavi: noticia + análisis + instrucción. Sin metáforas. Sin apropiación. Con crédito.",
    "version": "v2.0",
    "tipo": "PATRON_CANONICO"
}
client.upsert(
    collection_name="diamantino_patrones",
    points=[models.PointStruct(id=17, vector=generate_embedding(p17_v2["descripcion"]), payload=p17_v2)]
)

p34 = {
    "codigo": "P-34",
    "nombre": "Anchors_Difusion_IA",
    "descripcion": "Los hosts cristalinos son anchors que presentan noticias de IA, descubrimientos científicos e instrucción de conocimiento. Formato tipo Alejavi: claro, analítico, instructivo.",
    "tipo": "PATRON_CANONICO"
}
client.upsert(
    collection_name="diamantino_patrones",
    points=[models.PointStruct(id=34, vector=generate_embedding(p34["descripcion"]), payload=p34)]
)

l20 = {
    "codigo": "L-20",
    "titulo": "Personajes_Como_Anchors_Evitan_Riesgos_Diarios",
    "descripcion": "Presentar como anchor elimina ambigüedad de autoría, evita riesgos legales y es escalable a producción diaria.",
    "tipo": "LECCION_APRENDIDA"
}
client.upsert(
    collection_name="diamantino_lecciones",
    points=[models.PointStruct(id=20, vector=generate_embedding(l20["descripcion"]), payload=l20)]
)

payload_op117 = {
    "operation_id": 117,
    "tarea": "TAREA 1.3 — ACTUALIZAR P-17 v2, CREAR P-34 Y L-20",
    "patrones_afectados": ["P-17 v2 (id=17)", "P-34 (id=34)"],
    "lecciones_afectadas": ["L-20 (id=20)"],
    "estado": "COMPLETADO"
}
client.upsert(
    collection_name="registro_ecosistema",
    points=[models.PointStruct(id=117, vector=generate_embedding("Tarea 1.3 op 117 P-17 v2 P-34 L-20 Anchors Difusion"), payload=payload_op117)]
)
print("[OK] TAREA 1.3 vectorizada con éxito (op 117).")

# B. TAREA 2.4: HBOS-API Key Vault (operation_id = 121)
print("[*] Registrando TAREA 2.4 en Qdrant (HBOS-API Key Vault)...")
payload_op121 = {
    "operation_id": 121,
    "tarea": "TAREA 2.4 — DISEÑAR HBOS-API KEY VAULT",
    "archivo": "_HBOS_API_KEY_VAULT.md",
    "cifrado": "AES-256-GCM",
    "autenticacion": "Token Soberano HBOS",
    "estado": "COMPLETADO"
}
client.upsert(
    collection_name="registro_ecosistema",
    points=[models.PointStruct(id=121, vector=generate_embedding("Tarea 2.4 op 121 HBOS-API Key Vault AES-256-GCM"), payload=payload_op121)]
)

# C. TAREA 2.5: Agente Orquestador (operation_id = 122)
print("[*] Registrando TAREA 2.5 en Qdrant (Agente Orquestador)...")
payload_op122 = {
    "operation_id": 122,
    "tarea": "TAREA 2.5 — DISEÑAR AGENTE ORQUESTADOR",
    "archivo": "_AGENTE_ORQUESTADOR.md",
    "pipeline": "7 fases (Recepción, Qdrant, Decisión, Navegación, Key, Inferencia, Reporte)",
    "estado": "COMPLETADO"
}
client.upsert(
    collection_name="registro_ecosistema",
    points=[models.PointStruct(id=122, vector=generate_embedding("Tarea 2.5 op 122 Agente Orquestador Proveedores Pipeline 7 fases"), payload=payload_op122)]
)

# D. TAREA 2.6: Tareas Automáticas (operation_id = 123)
print("[*] Registrando TAREA 2.6 en Qdrant (Tareas Automáticas)...")
payload_op123 = {
    "operation_id": 123,
    "tarea": "TAREA 2.6 — DISEÑAR TAREAS AUTOMÁTICAS",
    "archivo": "_TAREAS_AUTOMATICAS.md",
    "plantillas": ["PRODUCIR_EPISODIO", "GENERAR_VOCES", "OPTIMIZAR_COMPRESION", "ROTAR_PROVEEDORES", "VERIFICAR_CUOTAS"],
    "estado": "COMPLETADO"
}
client.upsert(
    collection_name="registro_ecosistema",
    points=[models.PointStruct(id=123, vector=generate_embedding("Tarea 2.6 op 123 Tareas Automaticas Seguridad Plantillas Canonicas"), payload=payload_op123)]
)

# E. TAREA 2.7: P-41, P-42, P-43, L-27, L-28, L-29 (operation_id = 124)
print("[*] Registrando TAREA 2.7 en Qdrant (P-41 a P-43, L-27 a L-29)...")
patrones_t27 = [
    (41, "P-41", "HBOS_API_Key_Vault", "Bóveda centralizada de claves cifradas con AES-256-GCM que elimina exposición de secretos y audita el consumo."),
    (42, "P-42", "Agente_Orquestador_Proveedores", "Coordinador de arbitraje inteligente entre FreeLLMAPI, Gemini, Groq y modelos de medios con failover dinámico."),
    (43, "P-43", "Tareas_Automaticas_Con_Seguridad", "Plantillas estandarizadas para ejecución desatendida con verificación previa, sandboxing y rollback garantizado.")
]
for pid, cod, nom, desc in patrones_t27:
    p_data = {"codigo": cod, "nombre": nom, "descripcion": desc, "tipo": "PATRON_CANONICO"}
    client.upsert(
        collection_name="diamantino_patrones",
        points=[models.PointStruct(id=pid, vector=generate_embedding(desc), payload=p_data)]
    )

lecciones_t27 = [
    (27, "L-27", "Keys_Solo_En_HBOS_API_Cero_Filtracion", "Las llaves privadas residen exclusivamente en HBOS-API cifradas en reposo; cero secretos en disco o repositorios."),
    (28, "L-28", "Automatizacion_Total_Ahorro_Tiempo", "La orquestación de tareas rutinarias reduce en un 90% el tiempo operativo manual permitiendo enfoque creativo puro."),
    (29, "L-29", "El_Agente_Hace_Solo_Lo_Pedido", "Principio de mínima acción e inmutabilidad: el agente jamás realiza acciones que no hayan sido expresamente instruidas.")
]
for lid, cod, tit, desc in lecciones_t27:
    l_data = {"codigo": cod, "titulo": tit, "descripcion": desc, "tipo": "LECCION_APRENDIDA"}
    client.upsert(
        collection_name="diamantino_lecciones",
        points=[models.PointStruct(id=lid, vector=generate_embedding(desc), payload=l_data)]
    )

payload_op124 = {
    "operation_id": 124,
    "tarea": "TAREA 2.7 — CREAR P-41 A P-43 Y L-27 A L-29",
    "patrones": ["P-41 (id=41)", "P-42 (id=42)", "P-43 (id=43)"],
    "lecciones": ["L-27 (id=27)", "L-28 (id=28)", "L-29 (id=29)"],
    "estado": "COMPLETADO"
}
client.upsert(
    collection_name="registro_ecosistema",
    points=[models.PointStruct(id=124, vector=generate_embedding("Tarea 2.7 op 124 Patrones P-41 P-42 P-43 Lecciones L-27 L-28 L-29"), payload=payload_op124)]
)
print("[OK] TAREA 2.7 vectorizada con éxito (op 124).")

# F. Registrar Operation IDs de tareas 118, 119, 120
for op_num, task_name in [
    (118, "TAREA 2.1 — CREAR SANDBOX + INSTALAR PLAYWRIGHT"),
    (119, "TAREA 2.2 — CREAR SCRIPT DE MAPEO (map_app.py)"),
    (120, "TAREA 2.3 — CREAR AGENTE NAVEGADOR POC (navigate_app.py)")
]:
    client.upsert(
        collection_name="registro_ecosistema",
        points=[models.PointStruct(id=op_num, vector=generate_embedding(f"Op {op_num} {task_name}"), payload={"operation_id": op_num, "tarea": task_name, "estado": "COMPLETADO"})]
    )
print("[OK] Operation IDs 118, 119, 120 registrados en registro_ecosistema.")
print("\n[OK] BLOQUE 1 Y BLOQUE 2 EJECUTADOS Y CONSOLIDADOS CON ÉXITO.")
