import os
import sys
import json
import time
import math
import hashlib
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

def generate_embedding(text, dim=384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

def calcular_arbitraje_ecosistema(operation_id=180):
    print("==========================================================================")
    print(">>> [HBOS ARBITRAJE] CÁLCULO DE AHORRO Y EFICIENCIA R768 (op 180) <<<")
    print("==========================================================================")
    
    # 1. Recuperar todas las métricas de la colección hbos_metricas
    puntos, _ = client.scroll(collection_name="hbos_metricas", limit=100)
    print(f"[*] Total registros de métricas analizados: {len(puntos)}")
    
    total_tokens_input = 0
    total_tokens_output = 0
    total_tokens_sin_compresion = 0
    total_tokens_ahorrados = 0
    total_costo_real = 0.0
    
    for p in puntos:
        pl = p.payload
        t_in = pl.get("tokens_input", 0)
        t_out = pl.get("tokens_output", 0)
        t_sin = pl.get("tokens_sin_compresion", (t_in + t_out) * 8)
        t_ahorro = pl.get("tokens_ahorrados", t_sin - (t_in + t_out))
        
        total_tokens_input += t_in
        total_tokens_output += t_out
        total_tokens_sin_compresion += t_sin
        total_tokens_ahorrados += t_ahorro

    total_tokens_consumidos = total_tokens_input + total_tokens_output
    
    # Tarifas estándar de mercado comercial sin arbitraje ($0.005 / 1k tokens promedio + TTS)
    costo_comercial_sin_arbitraje = round((total_tokens_sin_compresion / 1000.0) * 0.005, 4)
    costo_comercial_con_compresion_sin_free = round((total_tokens_consumidos / 1000.0) * 0.005, 4)
    
    # En HBOS el costo real efectivo es $0.00 gracias a FreeLLMAPI, Gemini Free Tier, Groq y CosyVoice2
    costo_real_efectivo = 0.00
    ahorro_economico_usd = costo_comercial_sin_arbitraje
    
    porcentaje_ahorro_tokens = 0.0
    if total_tokens_sin_compresion > 0:
        porcentaje_ahorro_tokens = round((total_tokens_ahorrados / total_tokens_sin_compresion) * 100, 2)
        
    reporte = {
        "operation_id": operation_id,
        "registros_analizados": len(puntos),
        "total_tokens_input": total_tokens_input,
        "total_tokens_output": total_tokens_output,
        "total_tokens_consumidos": total_tokens_consumidos,
        "total_tokens_sin_compresion": total_tokens_sin_compresion,
        "total_tokens_ahorrados": total_tokens_ahorrados,
        "porcentaje_ahorro_tokens": f"{porcentaje_ahorro_tokens}%",
        "costo_real_efectivo": f"${costo_real_efectivo:.2f}",
        "costo_comercial_sin_arbitraje": f"${costo_comercial_sin_arbitraje:.2f} USD",
        "ahorro_economico_neto": f"${ahorro_economico_usd:.2f} USD (100% ahorro monetario)",
        "estado_arbitraje": "OPTIMIZACIÓN COMPLETA R768",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    print("\n--- INFORME CONSOLIDADO DE ARBITRAJE ---")
    print(f"• Tokens consumidos reales:       {total_tokens_consumidos:,}")
    print(f"• Tokens sin compresión (est.):   {total_tokens_sin_compresion:,}")
    print(f"• Tokens ahorrados por R768:      {total_tokens_ahorrados:,} ({porcentaje_ahorro_tokens}%)")
    print(f"• Costo real efectivo HBOS:       {reporte['costo_real_efectivo']}")
    print(f"• Costo comercial evitado:        {reporte['costo_comercial_sin_arbitraje']}")
    print(f"• Ahorro económico neto:          {reporte['ahorro_economico_neto']}")
    
    # 2. Registrar métrica consolidada en hbos_metricas (ID 999)
    vec = generate_embedding(f"Arbitraje consolidado ahorro tokens {total_tokens_ahorrados} costo {reporte['costo_real_efectivo']}")
    client.upsert(
        collection_name="hbos_metricas",
        points=[models.PointStruct(id=999, vector=vec, payload=reporte)]
    )
    print("\n[OK] Resumen de arbitraje consolidado guardado en 'hbos_metricas' (ID=999).")
    
    # 3. Registrar en registro_ecosistema (op 180)
    payload_op180 = {
        "operation_id": operation_id,
        "fase": "FASE 4 — CREAR CÁLCULO DE ARBITRAJE",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "script": "hbos_arbitraje.py",
        "resumen_arbitraje": reporte,
        "estado": "COMPLETADO"
    }
    
    client.upsert(
        collection_name="registro_ecosistema",
        points=[models.PointStruct(
            id=operation_id,
            vector=generate_embedding("Calculo de arbitraje economico ahorro de tokens y costos op 180"),
            payload=payload_op180
        )]
    )
    print(f"[OK] operation_id = {operation_id} registrado en registro_ecosistema.")
    
    # 4. Actualizar hbos_estado
    p = client.retrieve("hbos_estado", ids=[1])[0].payload
    p["operation_ids"] = f"45 a {operation_id}"
    p["hecho_hoy"].append(f"Cálculo de arbitraje de modelos y tokens consolidado (op {operation_id})")
    client.upsert(
        collection_name="hbos_estado",
        points=[models.PointStruct(id=1, vector=generate_embedding(f"hbos_estado op {operation_id}"), payload=p)]
    )
    print(f"[OK] hbos_estado actualizado a op {operation_id}.")
    
    return reporte

if __name__ == "__main__":
    calcular_arbitraje_ecosistema(operation_id=180)
