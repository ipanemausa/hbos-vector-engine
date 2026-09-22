"""
navigate_app.py — AGENTE NAVEGADOR DE APPS CON CONSULTA A QDRANT
Ecosistema: HBOS-Diamantino · Vector Engine
Trazabilidad: operation_id = 120 | Sandbox Aislado
"""

import os
import sys
import json
import time
import math
import hashlib
import datetime
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

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

def navigate_and_execute(app_name: str, task_description: str, base_url: str = "http://localhost:3000", headless: bool = True):
    print(f"[*] Iniciando navegación autónoma para tarea: '{task_description}' en app '{app_name}'")
    
    # 1. Consultar Qdrant para obtener la ruta y selector
    client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=25)
    query_vec = generate_embedding(f"{app_name} {task_description}", dim=384)
    
    search_res = client.search(
        collection_name="diamantino_apps",
        query_vector=query_vec,
        limit=3
    )
    
    if not search_res:
        print("[!] No se encontraron rutas registradas en 'diamantino_apps' para esta tarea.")
        return {"status": "FAILED", "error": "No matching route in Qdrant"}
        
    best_match = search_res[0].payload
    print(f"[*] Mejor coincidencia en Qdrant: Ruta='{best_match.get('ruta')}', Selector='{best_match.get('selector')}'")
    
    target_path = best_match.get("ruta", "/")
    target_selector = best_match.get("selector", "body")
    target_url = base_url.rstrip("/") + ("/" + target_path.lstrip("/") if target_path != "/" else "")
    
    result = {
        "app": app_name,
        "tarea": task_description,
        "url_objetivo": target_url,
        "selector": target_selector,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "pasos": [],
        "exito": False
    }
    
    # 2. Navegar con Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            print(f"[*] Navegando a: {target_url}")
            page.goto(target_url, timeout=30000, wait_until="networkidle")
            result["pasos"].append(f"Navegacion a {target_url} exitosa")
            
            # Verificar selector
            element = page.wait_for_selector(target_selector, timeout=10000)
            if element:
                result["pasos"].append(f"Elemento objetivo {target_selector} detectado")
                if element.is_enabled():
                    # Si es botón o interactuable, simular clic
                    tag = element.evaluate("el => el.tagName.toLowerCase()")
                    if tag in ["button", "a", "input"]:
                        element.click()
                        result["pasos"].append(f"Interaccion click sobre {target_selector} ejecutada")
                result["exito"] = True
            else:
                result["pasos"].append(f"Elemento {target_selector} no encontrado en DOM")
                
        except Exception as e:
            print(f"[!] Error de navegacion: {e}")
            result["error"] = str(e)
        finally:
            browser.close()
            
    print(f"[*] Resultado final: Exito={result['exito']}")
    return result

if __name__ == "__main__":
    app = sys.argv[1] if len(sys.argv) > 1 else "TEST_APP"
    task = sys.argv[2] if len(sys.argv) > 2 else "verificar estado inicial"
    navigate_and_execute(app, task)
