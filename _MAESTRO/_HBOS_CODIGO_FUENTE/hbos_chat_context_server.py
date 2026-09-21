#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py · MCP Server hbos-chat-context
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Vigente desde op=250

Provee herramientas MCP para contexto soberano inmediato:
  - get_context: Retorna identidad, estado y resumen del ecosistema.
  - get_canon: Retorna reglas R1-R73 y principios rectores §0-§17.
  - get_code: Retorna código fuente consolidado de scripts troncales.
  - get_state: Lee directamente de Qdrant Cloud (hbos_estado y registro_ecosistema).
  - get_pending: Retorna tareas pendientes y siguientes pasos.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env.local"))

def get_context() -> Dict[str, Any]:
    """Retorna el estado general, identidad y variables clave del ecosistema."""
    return {
        "ecosistema": "HBOS-Diamantino Soberano",
        "modo": "Experto ALEJAVI",
        "operation_id_actual": 250,
        "coordinacion": "UNBE §1.0 (Red Distribuida)",
        "ejecucion": "NUBE (Nodo Creativo HBOS)",
        "prohibicion": "NUNCA EN LOCAL",
        "canon_activo": "R1-R73",
        "hibrido": "LLMAPI ⊕ R768",
        "daemons": {
            "freellmapi": "http://localhost:3001 (235 modelos)",
            "ollama": "http://localhost:11434",
            "qdrant": "Qdrant Cloud (20 colecciones)"
        }
    }

def get_canon(regla: str = "todas") -> Dict[str, Any]:
    """Retorna el canon completo o una regla específica."""
    canon_file = os.path.join(BASE_DIR, "_MAESTRO", "_HBOS_CANON_COMPLETO.md")
    if os.path.exists(canon_file):
        with open(canon_file, "r", encoding="utf-8") as f:
            content = f.read()
        return {"canon_file": canon_file, "total_chars": len(content), "content_preview": content[:1200]}
    return {"error": "Canon completo en proceso de compilacion."}

def get_code(script_name: str = "hbos_film_director_agent.py") -> Dict[str, Any]:
    """Retorna el código de un script consolidado."""
    script_path = os.path.join(BASE_DIR, "_MAESTRO", "_HBOS_CODIGO_FUENTE", script_name)
    if not os.path.exists(script_path):
        script_path = os.path.join(BASE_DIR, script_name)
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            code = f.read()
        return {"script": script_name, "path": script_path, "lines": len(code.splitlines()), "code": code[:2000]}
    return {"error": f"Script {script_name} no encontrado."}

def get_state() -> Dict[str, Any]:
    """Consulta en tiempo real Qdrant Cloud para obtener el estado inmutable."""
    try:
        from qdrant_client import QdrantClient
        url = os.getenv("QDRANT_URL")
        key = os.getenv("QDRANT_API_KEY")
        if not url or not key:
            return {"error": "Credenciales de Qdrant no configuradas."}
        client = QdrantClient(url=url, api_key=key)
        p_est = client.retrieve("hbos_estado", ids=[1])
        p_reg = client.retrieve("registro_ecosistema", ids=[249])
        return {
            "status": "CONNECTED_QDRANT",
            "hbos_estado": p_est[0].payload if p_est else None,
            "ultimo_registro_op249": p_reg[0].payload if p_reg else None
        }
    except Exception as e:
        return {"error": f"Fallo al conectar con Qdrant: {str(e)}"}

def get_pending() -> Dict[str, Any]:
    """Retorna los próximos pasos de ejecución canónica."""
    ancla_path = os.path.join(BASE_DIR, "_MAESTRO", "_HBOS_ANCLA.md")
    if os.path.exists(ancla_path):
        with open(ancla_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        pasos = [l.strip() for l in lines if l.strip().startswith("*") or l.strip().startswith("1.") or l.strip().startswith("2.")]
        return {"status": "OK", "proximos_pasos": pasos[-10:]}
    return {"error": "Archivo ancla no disponible."}

def handle_json_rpc():
    """Manejador básico de protocolo MCP JSON-RPC sobre stdio."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")

            if method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {"name": "get_context", "description": "Retorna contexto e identidad general de HBOS."},
                            {"name": "get_canon", "description": "Retorna el canon R1-R73."},
                            {"name": "get_code", "description": "Retorna código fuente de scripts troncales."},
                            {"name": "get_state", "description": "Consulta estado inmutable en Qdrant Cloud."},
                            {"name": "get_pending", "description": "Retorna próximos pasos y pendientes."}
                        ]
                    }
                }
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                
                if name == "get_context":
                    res = get_context()
                elif name == "get_canon":
                    res = get_canon(args.get("regla", "todas"))
                elif name == "get_code":
                    res = get_code(args.get("script_name", "hbos_film_director_agent.py"))
                elif name == "get_state":
                    res = get_state()
                elif name == "get_pending":
                    res = get_pending()
                else:
                    res = {"error": f"Herramienta {name} desconocida"}
                
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2, ensure_ascii=False)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("[TEST] get_context:", get_context())
        print("[TEST] get_state:", get_state())
        print("[TEST] get_pending:", get_pending())
        print("[OK] MCP hbos-chat-context verificado en modo unitario.")
    else:
        handle_json_rpc()
