# HBOS QUADRANT ENGINE - DISPATCHER UNIVERSAL MULTI-TENANT V4
import os, sys, json
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv(".env.local")
client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)

TAXONOMIA_FUNCIONES = {
    "adquisicion_y_ventas": ["venta", "campana", "comercial", "producto", "cliente", "conversion", "precio", "catalogo", "marketing", "joya"],
    "analitica_y_reportes": ["excel", "csv", "informe", "siniestro", "accidente", "tabla", "panel", "metricas", "calculo", "datos"],
    "formacion_y_capacitacion": ["leccion", "presentador", "educacion", "evaluacion", "diagnostica", "profesor", "curso", "guiahoy", "avatar"],
    "finanzas_y_auditoria": ["auditoria", "costo", "arancel", "margen", "conciliacion", "fiscal", "factura", "impuesto", "caja"],
    "cumplimiento_y_normativa": ["reclamacion", "manual", "consumidor", "ley", "norma", "boe", "garantia"]
}

def inferir_dominio(texto):
    t = texto.lower()
    for cat, palabras in TAXONOMIA_FUNCIONES.items():
        if any(p in t for p in palabras):
            return cat
    return "general"

def resolver_caso_uso(prompt_usuario, tenant_contexto="universal"):
    dom_inferido = inferir_dominio(prompt_usuario)
    res, _ = client.scroll(collection_name="casos_uso_hbos", limit=150, with_payload=True, with_vectors=False)
    
    mejor_caso = None
    mejor_score = -1
    palabras_query = set(prompt_usuario.lower().split())
    
    for p in res:
        payload = p.payload
        intencion = payload.get("intencion_negocio", "").lower()
        nombre = payload.get("caso_uso_nombre", "").lower()
        dominio = payload.get("dominio", "").lower()
        
        coincidencias = len(palabras_query.intersection(set((intencion + " " + nombre + " " + dominio).split())))
        score = coincidencias
        if dom_inferido in dominio:
            score += 4
            
        if score > mejor_score:
            mejor_score = score
            mejor_caso = p
            
    if mejor_caso:
        p = mejor_caso.payload
        orden_trabajo = {
            "caso_id": mejor_caso.id,
            "funcion_negocio_universal": p.get("dominio"),
            "tenant_aplicado": tenant_contexto,
            "caso_uso": p.get("caso_uso_nombre"),
            "intencion_detectada": p.get("intencion_negocio"),
            "pipeline_ejecutor": p.get("pipeline_asignado"),
            "parametros_runtime": {
                **p.get("parametros_default", {}),
                "ruteo_proxy": "http://127.0.0.1:3001/v1",
                "destino_backup": "G:/My Drive/HBOS_BACKUP/operaciones"
            },
            "formatos_salida": p.get("salidas_permitidas")
        }
        return orden_trabajo
        
    return {"error": "No se pudo clasificar la intencion"}

if __name__ == "__main__":
    consulta = sys.argv[1] if len(sys.argv) > 1 else "explicar propuesta comercial con video y graficos"
    tenant = sys.argv[2] if len(sys.argv) > 2 else "universal"
    print(json.dumps(resolver_caso_uso(consulta, tenant), indent=2, ensure_ascii=False))
