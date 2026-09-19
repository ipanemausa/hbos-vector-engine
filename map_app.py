"""
map_app.py — SCRIPT DE MAPEO AUTÓNOMO DE APLICACIONES (PLAYWRIGHT)
Ecosistema: HBOS-Diamantino · Vector Engine
Trazabilidad: operation_id = 119 | Sandbox Aislado
"""

import os
import sys
import json
import time
import datetime
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

MAPS_DIR = os.path.join(os.path.dirname(__file__), "mapas")
os.makedirs(MAPS_DIR, exist_ok=True)

def map_application(app_name: str, start_url: str, headless: bool = True):
    print(f"[*] Iniciando mapeo autónomo para '{app_name}' en: {start_url}")
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    app_map = {
        "app": app_name,
        "version": "1.0",
        "start_url": start_url,
        "timestamp": timestamp,
        "rutas_detectadas": [],
        "elementos": []
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        
        try:
            page.goto(start_url, timeout=30000, wait_until="networkidle")
            time.sleep(2)
            
            # Detectar botones interactivos
            buttons = page.query_selector_all("button, [role='button'], input[type='button'], input[type='submit']")
            print(f"[*] Botones detectados: {len(buttons)}")
            for idx, btn in enumerate(buttons):
                text = (btn.inner_text() or btn.get_attribute("value") or btn.get_attribute("aria-label") or f"btn_{idx}").strip()
                selector = btn.get_attribute("id") or btn.get_attribute("name") or btn.get_attribute("class") or f"button:nth-of-type({idx+1})"
                app_map["elementos"].append({
                    "tipo": "boton",
                    "texto": text,
                    "selector": f"#{selector}" if not selector.startswith("#") and not ":" in selector else selector,
                    "visible": btn.is_visible(),
                    "habilitado": btn.is_enabled()
                })
                
            # Detectar enlaces y rutas
            links = page.query_selector_all("a[href]")
            print(f"[*] Enlaces/rutas detectadas: {len(links)}")
            for link in links:
                href = link.get_attribute("href")
                text = (link.inner_text() or link.get_attribute("aria-label") or "").strip()
                if href and not href.startswith("javascript:") and not href == "#":
                    app_map["rutas_detectadas"].append({
                        "texto": text,
                        "ruta": href,
                        "selector": f"a[href='{href}']"
                    })
                    
            # Detectar inputs y toggles
            inputs = page.query_selector_all("input[type='checkbox'], input[type='text'], input[type='password'], select")
            for inp in inputs:
                t = inp.get_attribute("type") or "select"
                ident = inp.get_attribute("id") or inp.get_attribute("name") or "input"
                app_map["elementos"].append({
                    "tipo": f"input_{t}",
                    "identificador": ident,
                    "selector": f"#{ident}" if ident else t
                })
                
        except Exception as e:
            print(f"[!] Error durante la inspección de la app: {e}")
            app_map["error"] = str(e)
        finally:
            browser.close()
            
    out_file = os.path.join(MAPS_DIR, f"MAPA_{app_name.upper()}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(app_map, f, indent=2, ensure_ascii=False)
        
    print(f"[OK] Mapeo completado y guardado en: {out_file}")
    return app_map

if __name__ == "__main__":
    app = sys.argv[1] if len(sys.argv) > 1 else "TEST_APP"
    url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:3000"
    map_application(app, url)
