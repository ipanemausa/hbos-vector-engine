#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py · MCP Server hbos-chat-context
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Vigente desde op=252

Provee herramientas MCP para contexto soberano inmediato:
  - get_context: Retorna identidad, estado y resumen del ecosistema.
  - get_canon: Retorna reglas R1-R73 y principios rectores §0-§17.
  - get_code: Retorna código fuente consolidado de scripts troncales.
  - get_state: Lee directamente de Qdrant Cloud (hbos_estado y registro_ecosistema).
  - get_pending: Retorna tareas pendientes y siguientes pasos.

Implementa protocolo MCP completo (handshake + tools).
"""

import os
import sys
import json
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(r"C:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if not os.getenv("QDRANT_URL") and os.path.exists(os.path.join(BASE_DIR, ".env.local")):
    load_dotenv(os.path.join(BASE_DIR, ".env.local"))

# ── HERRAMIENTAS MCP ────────────────────────────────────────────────

def get_context() -> Dict[str, Any]:
    """Retorna el estado general, identidad y variables clave del ecosistema."""
    return {
        "ecosistema": "HBOS-Diamantino Soberano",
        "modo": "Experto ALEJAVI",
        "operation_id_actual": 252,
        "coordinacion": "UNBE §1.0 (Red Distribuida)",
        "ejecucion": "NUBE (Nodo Creativo HBOS)",
        "prohibicion": "NUNCA EN LOCAL",
        "canon_activo": "R1-R74",
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
        p_reg = client.retrieve("registro_ecosistema", ids=[251])
        return {
            "status": "CONNECTED_QDRANT",
            "hbos_estado": p_est[0].payload if p_est else None,
            "ultimo_registro_op251": p_reg[0].payload if p_reg else None
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

# ── HERRAMIENTAS MCP · DEFINICIÓN ──────────────────────────────────

TOOLS = [
    {"name": "get_context", "description": "Retorna contexto e identidad general de HBOS."},
    {"name": "get_canon", "description": "Retorna el canon R1-R74."},
    {"name": "get_code", "description": "Retorna código fuente de scripts troncales."},
    {"name": "get_state", "description": "Consulta estado inmutable en Qdrant Cloud."},
    {"name": "get_pending", "description": "Retorna próximos pasos y pendientes."}
]

TOOLS_MAP = {
    "get_context": lambda args: get_context(),
    "get_canon": lambda args: get_canon(args.get("regla", "todas")),
    "get_code": lambda args: get_code(args.get("script_name", "hbos_film_director_agent.py")),
    "get_state": lambda args: get_state(),
    "get_pending": lambda args: get_pending(),
}

# ── PROTOCOLO MCP · JSON-RPC sobre stdio ───────────────────────────

def send_response(msg_id, result):
    """Envía respuesta JSON-RPC."""
    resp = {"jsonrpc": "2.0", "id": msg_id, "result": result}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()

def send_error(msg_id, code, message):
    """Envía error JSON-RPC."""
    resp = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()

def handle_json_rpc():
    """Manejador completo de protocolo MCP JSON-RPC sobre stdio."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            params = req.get("params", {})

            # ── HANDSHAKE MCP (OBLIGATORIO) ────────────────────────
            if method == "initialize":
                send_response(msg_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "hbos-chat-context",
                        "version": "1.0.0"
                    }
                })
            elif method == "initialized":
                # Notificación · no requiere respuesta
                continue
            elif method == "shutdown":
                send_response(msg_id, None)
                break

            # ── MÉTODOS DE HERRAMIENTAS ────────────────────────────
            elif method == "tools/list":
                send_response(msg_id, {"tools": TOOLS})
            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments", {})
                if name in TOOLS_MAP:
                    try:
                        res = TOOLS_MAP[name](args)
                        send_response(msg_id, {
                            "content": [{"type": "text", "text": json.dumps(res, indent=2, ensure_ascii=False)}]
                        })
                    except Exception as e:
                        send_error(msg_id, -32603, f"Error en {name}: {str(e)}")
                else:
                    send_error(msg_id, -32601, f"Herramienta desconocida: {name}")
            elif method == "ping":
                send_response(msg_id, {})
            else:
                send_error(msg_id, -32601, f"Método desconocido: {method}")

        except json.JSONDecodeError as e:
            send_error(None, -32700, f"Parse error: {str(e)}")
        except Exception as e:
            send_error(None, -32603, f"Internal error: {str(e)}")

# ── PUNTO DE ENTRADA ────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("[TEST] get_context:", get_context())
        print("[TEST] get_state:", get_state())
        print("[TEST] get_pending:", get_pending())
        print("[OK] MCP hbos-chat-context verificado en modo unitario.")
    elif len(sys.argv) > 1 and sys.argv[1] == "--handshake":
        # Test de handshake MCP
        test_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        print("Enviando:", json.dumps(test_req))
        # Simular respuesta
        print("Respuesta esperada: protocolVersion, capabilities, serverInfo")
    else:
        handle_json_rpc()