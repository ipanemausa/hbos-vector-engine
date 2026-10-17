import socket
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('C:/Users/ipane/hbos-deploy/hbos-vector-engine/.env.local')

api_key = os.getenv('QDRANT_API_KEY')
raw_url = os.getenv('QDRANT_URL')
url = raw_url.rstrip(':6333').rstrip('/') if raw_url else 'https://38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io'

# MAPA DE DNS FORZADO (Bypass de DNS local)
DNS_MAP = {
    '38f50573-516c-4d44-a391-eb35457eeada.us-east4-0.gcp.cloud.qdrant.io': '34.186.107.230'
}

# Sobrescribir el resolvedor de sockets de Python
_orig_getaddrinfo = socket.getaddrinfo
socket.getaddrinfo = lambda host, port, *args, **kwargs: _orig_getaddrinfo(DNS_MAP.get(host, host), port, *args, **kwargs)

# Definir las colecciones canónicas de HBOS (384d)
EXPECTED_COLLECTIONS = {
    # Agentes de orquestación y producción
    "hbos-agent-go": "Gemini Orchestration (GO) - Cerebro central del enjambre",
    "hbos-agent-ga": "GPT Architect (GA) - Escritura de guiones y copywriting",
    "hbos-agent-fl": "Flow (FL) - Agente visual y de renderizado",
    "hbos-agent-vca": "Voice Cloning Agent (VCA) - Clonación de voz y audio",
    "hbos-agent-ytda": "YouTube Developer Agent (YTDA) - Publicación y SEO",
    "hbos-agent-gaisa": "Google AI Studio Agent (GAISA) - Investigación de IA",
    
    # Modelos y proveedores integrados
    "hbos-model-openai": "Modelos OpenAI y ChatGPT UI (intelligent free models)",
    "hbos-model-gemini": "Modelos Gemini y Google AI Pro",
    "hbos-model-flow": "Modelos de Flow (FL) para generación de video",
    "hbos-model-muse": "Modelos de Muse para asistencia creativa",
    
    # Colecciones de conocimiento y estado
    "hbos-vector": "Conocimiento general del sistema (384d)",
    "hbos-sessions": "Estado de las sesiones del enjambre (384d)",
    "hbos-transcripciones": "Transcripciones y conocimiento de Alejavi (384d)"
}

def check_and_create_collections():
    print("--- AUDITORÍA DE COLECCIONES EN QDRANT CLOUD ---")
    
    # 1. Listar colecciones existentes
    try:
        r = requests.get(f'{url}:6333/collections', headers={'api-key': api_key}, timeout=10)
        if r.status_code == 200:
            existing_cols = [c['name'] for c in r.json().get('result', {}).get('collections', [])]
            print(f"Colecciones existentes ({len(existing_cols)}):", existing_cols)
        else:
            print("Error listando colecciones:", r.text)
            return
    except Exception as e:
        print("Error de conexión:", e)
        return

    # Payload estándar 384d Cosine
    create_payload = {
        "vectors": {
            "size": 384,
            "distance": "Cosine"
        }
    }

    # 2. Verificar y crear colecciones faltantes
    for col_name, description in EXPECTED_COLLECTIONS.items():
        if col_name not in existing_cols:
            print(f"\n[!] Colección faltante: {col_name} - {description}")
            try:
                r_create = requests.put(
                    f'{url}:6333/collections/{col_name}',
                    headers={'api-key': api_key, 'Content-Type': 'application/json'},
                    json=create_payload,
                    timeout=10
                )
                if r_create.status_code in [200, 201]:
                    print(f"   [OK] Colección '{col_name}' creada correctamente (384d, Cosine).")
                else:
                    print(f"   [ERROR] No se pudo crear '{col_name}': {r_create.text}")
            except Exception as e:
                print(f"   [ERROR] Excepción creando '{col_name}': {e}")
        else:
            # Verificar la configuración de la colección existente
            try:
                r_info = requests.get(f'{url}:6333/collections/{col_name}', headers={'api-key': api_key}, timeout=10)
                if r_info.status_code == 200:
                    info = r_info.json().get('result', {}).get('config', {}).get('params', {}).get('vectors', {})
                    size = info.get('size', 'N/A')
                    distance = info.get('distance', 'N/A')
                    print(f"   [INFO] '{col_name}': Dimensión={size}, Métrica={distance}")
                    if size != 384:
                        print(f"   [ADVERTENCIA] La dimensión de '{col_name}' es {size}, pero la canónica es 384d. Reconfigurando...")
                        requests.delete(f'{url}:6333/collections/{col_name}', headers={'api-key': api_key})
                        requests.put(f'{url}:6333/collections/{col_name}', headers={'api-key': api_key, 'Content-Type': 'application/json'}, json=create_payload)
                        print(f"   [OK] Colección '{col_name}' reconfigurada a 384d.")
            except Exception as e:
                print(f"   [ERROR] Verificando '{col_name}': {e}")

    print("\n--- AUDITORÍA COMPLETADA ---")

if __name__ == "__main__":
    check_and_create_collections()
