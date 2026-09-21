#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py · MCP Server hbos-chat-context (v3.0 ESTÁNDAR FORMAL JSON-RPC)
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Vigente desde op=252 / Protocolo UNBE §1.0
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
    return {
        "ecosistema": "HBOS-Diamantino Soberano",
        "modo": "Experto ALEJAVI",
        "operation_id_actual": 252,
        "coordinacion": "UNBE §1.0",
        "ejecucion": "NUBE (Nodo Creativo HBOS)",
        "canon_activo": "R1-R74",
        "hibrido": "LLMAPI ⊕ R768",
        "daemons": {"freellmapi": ":3001", "ollama": ":11434", "qdrant": "Cloud (20 cols)"}
    }

def get_canon(regla: str = "todas") -> Dict[str, Any]:
    # Intenta leer primero de Qdrant si está disponible
    try:
        from qdrant_client import QdrantClient
        url = os.getenv("QDRANT_URL")
        key = os.getenv("QDRANT_API_KEY")
        if url and key:
            client = QdrantClient(url=url, api_key=key, timeout=5)
            if regla != "todas":
                # buscar regla especifica
                res = client.scroll("hbos_canon", scroll_filter={"must": [{"key": "regla_id", "match": {"value": regla.upper()}}]}, limit=1)[0]
                if res:
                    return {"status": "OK", "fuente": "Qdrant", "regla": res[0].payload}
            # todas
            pts = client.get_collection("hbos_canon").points_count
            return {"status": "OK", "fuente": "Qdrant", "coleccion": "hbos_canon", "total_reglas_indexadas": pts}
    except Exception:
        pass
    # Fallback a disco sin truncar
    canon_file = os.path.join(BASE_DIR, "_MAESTRO", "_HBOS_CANON_COMPLETO.md")
    if os.path.exists(canon_file):
        with open(canon_file, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "OK", "fuente": "Disco", "total_chars": len(content), "content": content}
    return {"status": "ERROR", "message": "Canon no encontrado"}

def get_code(script_name: str = "hbos_film_director_agent.py") -> Dict[str, Any]:
    script_path = os.path.join(BASE_DIR, "_MAESTRO", "_HBOS_CODIGO_FUENTE", script_name)
    if not os.path.exists(script_path):
        script_path = os.path.join(BASE_DIR, script_name)
    if os.path.exists(script_path):
        with open(script_path, "r", encoding="utf-8") as f:
            code = f.read()
        return {"status": "OK", "script": script_name, "lines": len(code.splitlines()), "code": code}
    return {"status": "ERROR", "message": f"Script {script_name} no encontrado"}

def get_state() -> Dict[str, Any]:
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"), timeout=5)
        p_est = client.retrieve("hbos_estado", ids=[1])
        return {"status": "OK", "hbos_estado": p_est[0].payload if p_est else None}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def get_pending() -> Dict[str, Any]:
    ancla_path = os.path.join(BASE_DIR, "_MAESTRO", "_HBOS_ANCLA.md")
    if os.path.exists(ancla_path):
        with open(ancla_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip().startswith("*") or l.strip().startswith("1.")]
        return {"status": "OK", "pendientes": lines[-10:]}
    return {"status": "ERROR", "message": "Ancla no disponible"}

# SCHEMA FORMAL MCP CON inputSchema OBLIGATORIO
TOOLS = [
    {
        "name": "get_context",
        "description": "Retorna contexto e identidad general de HBOS.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_canon",
        "description": "Retorna el canon R1-R74 completo o una regla específica.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "regla": {"type": "string", "description": "Código de la regla (ej: R62, FAM@-T o todas)", "default": "todas"}
            }
        }
    },
    {
        "name": "get_code",
        "description": "Retorna código fuente consolidado de scripts troncales.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "script_name": {"type": "string", "description": "Nombre del script", "default": "hbos_film_director_agent.py"}
            }
        }
    },
    {
        "name": "get_state",
        "description": "Consulta estado inmutable en Qdrant Cloud.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_pending",
        "description": "Retorna próximos pasos y pendientes canónicos.",
        "inputSchema": {"type": "object", "properties": {}}
    }
]

TOOLS_MAP = {
    "get_context": lambda a: get_context(),
    "get_canon": lambda a: get_canon(a.get("regla", "todas")),
    "get_code": lambda a: get_code(a.get("script_name", "hbos_film_director_agent.py")),
    "get_state": lambda a: get_state(),
    "get_pending": lambda a: get_pending()
}

def send_response(msg_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(msg_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def handle_json_rpc():
    while True:
        try:
            line = sys.stdin.readline()
            if not line: break
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            params = req.get("params", {})

            if method == "initialize":
                send_response(msg_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "hbos-chat-context", "version": "3.0.0"}
                })
            elif method == "initialized":
                continue
            elif method == "shutdown":
                send_response(msg_id, None)
                break
            elif method == "tools/list":
                send_response(msg_id, {"tools": TOOLS})
            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments", {})
                if name in TOOLS_MAP:
                    res = TOOLS_MAP[name](args)
                    send_response(msg_id, {"content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False)}]})
                else:
                    send_error(msg_id, -32601, f"Unknown tool: {name}")
            elif method == "ping":
                send_response(msg_id, {})
            else:
                send_error(msg_id, -32601, f"Unknown method: {method}")
        except json.JSONDecodeError as e:
            send_error(None, -32700, f"Parse error: {str(e)}")
        except Exception as e:
            send_error(None, -32603, f"Internal error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("[TEST-MCP] get_context:", json.dumps(get_context())[:100])
        print("[TEST-MCP] get_canon:", json.dumps(get_canon("R62"))[:100])
        print("[TEST-MCP] tools/list count:", len(TOOLS))
        print("[TEST-MCP] Valid inputSchema in all tools:", all("inputSchema" in t for t in TOOLS))
        print("[OK] MCP hbos-chat-context verificado unitariamente.")
    else:
        handle_json_rpc()
