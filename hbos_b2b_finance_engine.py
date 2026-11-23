# ==============================================================================
# HBOS QUADRANT ENGINE · PRODUCTO B2B: AUDITORÍA FINANCIERA AUTOMATIZADA
# ==============================================================================
import os, sys, json, urllib.request, urllib.error, datetime

DB_PATH = r"C:\Users\ipane\AppData\Roaming\FreeLLMAPI\freeapi.db"
PROXY_URL = "http://127.0.0.1:3001/v1"
OUTPUT_DIR = "G:/My Drive/HBOS_BACKUP/reportes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def obtener_token():
    import sqlite3
    token = None
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key='unified_api_key' LIMIT 1")
            row = cur.fetchone()
            if row: token = row[0]
            conn.close()
        except: pass
    return token or "freellmapi-86a3178c0952594913cb64f17d3b8ce95ab63e87023ff14d"

def calcular_metricas_base(datos):
    ventas = datos["ventas_brutas"]
    costo_ventas = datos["costo_mercancia"]
    gastos_operacion = datos["gastos_operativos"]
    mermas_descuentos = datos["mermas_y_descuentos"]
    
    ventas_netas = ventas - mermas_descuentos
    utilidad_bruta = ventas_netas - costo_ventas
    margen_bruto_pct = round((utilidad_bruta / ventas_netas) * 100, 2) if ventas_netas > 0 else 0.0
    
    ebitda = utilidad_bruta - gastos_operacion
    margen_ebitda_pct = round((ebitda / ventas_netas) * 100, 2) if ventas_netas > 0 else 0.0
    
    return {
        "ventas_netas": ventas_netas,
        "utilidad_bruta": utilidad_bruta,
        "margen_bruto_pct": margen_bruto_pct,
        "ebitda": ebitda,
        "margen_ebitda_pct": margen_ebitda_pct
    }

def generar_dictamen_ejecutivo(datos_cliente, metricas):
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    instruccion_sistema = (
        "Actúa como Consultor Financiero Senior para Juntas Directivas. "
        "Aplica estándar ASD-STE100: oraciones concisas, voz activa, datos numéricos precisos. "
        "Estructura el dictamen en 3 secciones estrictas: "
        "1. DIAGNÓSTICO DE RENTABILIDAD (análisis de margen bruto y EBITDA). "
        "2. FOCOS ROJOS DE TESORERÍA (riesgos detectados en costos o mermas). "
        "3. PLAN DE ACCIÓN INMEDIATO (3 decisiones operativas en orden de prioridad)."
    )
    
    resumen_cifras = (
        f"Empresa: {datos_cliente['nombre_empresa']}\n"
        f"Sector: {datos_cliente['sector']}\n"
        f"Ventas Brutas: ${datos_cliente['ventas_brutas']:,.2f}\n"
        f"Mermas/Descuentos: ${datos_cliente['mermas_y_descuentos']:,.2f}\n"
        f"Ventas Netas: ${metricas['ventas_netas']:,.2f}\n"
        f"Costo de Mercancía (COGS): ${datos_cliente['costo_mercancia']:,.2f}\n"
        f"Utilidad Bruta: ${metricas['utilidad_bruta']:,.2f} ({metricas['margen_bruto_pct']}%)\n"
        f"Gastos Operativos (OPEX): ${datos_cliente['gastos_operativos']:,.2f}\n"
        f"EBITDA: ${metricas['ebitda']:,.2f} ({metricas['margen_ebitda_pct']}%)\n"
    )
    
    body = {
        "model": "auto:fast",
        "messages": [
            {"role": "system", "content": instruccion_sistema},
            {"role": "user", "content": f"Genera la auditoría ejecutiva con base en estos datos:\n\n{resumen_cifras}"}
        ],
        "temperature": 0.2,
        "max_tokens": 550
    }
    
    req = urllib.request.Request(f"{PROXY_URL}/chat/completions", data=json.dumps(body).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            data = json.loads(res.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error en generación de dictamen: {type(e).__name__}"

def ejecutar_auditoria():
    print("============================================================")
    print("   HBOS ENGINE · AUDITORÍA FINANCIERA EJECUTIVA B2B")
    print("============================================================")
    
    # Caso real de prueba: Empresa comercial de retail / joyería
    datos_comerciales = {
        "nombre_empresa": "Distribuciones & Retail Santa María S.A.S.",
        "sector": "Comercio Minorista / Joyería y Accesorios",
        "ventas_brutas": 85000000.0,
        "mermas_y_descuentos": 4200000.0,
        "costo_mercancia": 48500000.0,
        "gastos_operativos": 18200000.0
    }
    
    print(f"[*] Procesando balance operativo para: {datos_comerciales['nombre_empresa']}")
    metricas = calcular_metricas_base(datos_comerciales)
    
    print("[*] Generando dictamen estratégico en auto:fast (:3001)...")
    dictamen = generar_dictamen_ejecutivo(datos_comerciales, metricas)
    
    # Consolidación del informe final
    fecha_reporte = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    contenido_markdown = f"""# REPORTE DE AUDITORÍA Y SALUD FINANCIERA B2B
**Cliente:** {datos_comerciales['nombre_empresa']}  
**Sector:** {datos_comerciales['sector']}  
**Fecha:** {fecha_reporte}  
**Motor:** HBOS Quadrant Finance Engine  

---

## 1. RESUMEN DE INDICADORES CLAVE (KPIs)

| Indicador Financiero | Valor Monetario (COP) | Margen (%) |
| :--- | :--- | :--- |
| **Ventas Netas** | ${metricas['ventas_netas']:,.2f} | 100.00% |
| **Costo de Mercancía (COGS)** | ${datos_comerciales['costo_mercancia']:,.2f} | {round((datos_comerciales['costo_mercancia']/metricas['ventas_netas'])*100, 2)}% |
| **Utilidad Bruta** | ${metricas['utilidad_bruta']:,.2f} | **{metricas['margen_bruto_pct']}%** |
| **Gastos Operativos (OPEX)** | ${datos_comerciales['gastos_operativos']:,.2f} | {round((datos_comerciales['gastos_operativos']/metricas['ventas_netas'])*100, 2)}% |
| **EBITDA Operativo** | ${metricas['ebitda']:,.2f} | **{metricas['margen_ebitda_pct']}%** |

---

## 2. EVALUACIÓN Y DICTAMEN DE JUNTA DIRECTIVA

{dictamen}

---
*Reporte confidencial generado por HBOS Quadrant Autonomous Engine.*
"""
    
    archivo_salida = os.path.join(OUTPUT_DIR, "auditoria_financiera_santa_maria.md")
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(contenido_markdown)
        
    print("\n------------------------------------------------------------")
    print(dictamen)
    print("------------------------------------------------------------\n")
    print(f"[OK] Reporte B2B consolidado y guardado en:\n     {archivo_salida}")
    print("============================================================\n")

if __name__ == "__main__":
    ejecutar_auditoria()
