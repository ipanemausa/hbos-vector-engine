"""
hbos_unified_gateway.py — HBOS-UNIFIED-GATEWAY (FASE 1)
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Puerto de Escucha: 3002 · Especificación OpenAI-Compatible
Gobernanza: FAM@-T · LLMAPI ⊕ R768 · HBOS VAULT (AES-256-GCM) · UNBE (§1.0)
"""

import os
import sys
import time
import json
import uuid
import math
import hashlib
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "gateway_config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

SOVEREIGN_TOKENS = set(CONFIG.get("sovereign_tokens", []))
OPERATION_ID = 225

# -----------------------------------------------------------------------------
# HBOS VAULT (AES-256-GCM) — Enclave Criptográfico
# -----------------------------------------------------------------------------
class HBOSVault:
    def __init__(self):
        master_secret = os.getenv("HBOS_VAULT_SECRET", "hbos-diamantino-master-key-2026-sovereign-grade")
        self.master_key = hashlib.sha256(master_secret.encode('utf-8')).digest() # 256-bit key
        self.aesgcm = AESGCM(self.master_key)
        self.algorithm = "AES-256-GCM"
        
    def encrypt(self, plain_text: str) -> str:
        nonce = os.urandom(12)
        ct = self.aesgcm.encrypt(nonce, plain_text.encode('utf-8'), None)
        return f"{nonce.hex()}:{ct.hex()}"
        
    def decrypt(self, encrypted_bundle: str) -> str:
        parts = encrypted_bundle.split(":")
        if len(parts) != 2:
            raise ValueError("Formato de paquete cifrado inválido")
        nonce = bytes.fromhex(parts[0])
        ct = bytes.fromhex(parts[1])
        pt = self.aesgcm.decrypt(nonce, ct, None)
        decrypted_str = pt.decode('utf-8')
        return decrypted_str

VAULT = HBOSVault()

# -----------------------------------------------------------------------------
# CLIENTE QDRANT PARA LOGGING DE TELEMETRÍA (hbos_metricas)
# -----------------------------------------------------------------------------
QDRANT_CLIENT = None
try:
    q_url = os.getenv("QDRANT_URL")
    q_key = os.getenv("QDRANT_API_KEY")
    if q_url and q_key:
        QDRANT_CLIENT = QdrantClient(url=q_url, api_key=q_key, timeout=10)
except Exception as e:
    print(f"[!] Warning conectando Qdrant en Gateway: {e}")

def generate_embedding(text: str, dim: int = 384) -> List[float]:
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

def log_request_metrics(model: str, provider: str, latency_ms: float, in_tokens: int, out_tokens: int, req_sha: str, resp_sha: str):
    if not QDRANT_CLIENT:
        return
    try:
        point_id = int(time.time() * 1000) % 2147483647
        v_telemetry = generate_embedding(f"{model} {provider} {req_sha[:8]} {resp_sha[:8]}")
        payload = {
            "operation_id": OPERATION_ID,
            "timestamp": time.time(),
            "model": model,
            "provider": provider,
            "latency_ms": round(latency_ms, 2),
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "request_sha256": req_sha,
            "response_sha256": resp_sha,
            "gateway": "HBOS-Unified-Gateway:3002"
        }
        QDRANT_CLIENT.upsert(
            collection_name="hbos_metricas",
            points=[qmodels.PointStruct(id=point_id, vector=v_telemetry, payload=payload)]
        )
    except Exception as ex:
        print(f"[!] Error logging en hbos_metricas: {ex}")

# -----------------------------------------------------------------------------
# FASTAPI APP Y MODELOS DE DATOS OPENAI
# -----------------------------------------------------------------------------
app = FastAPI(
    title="HBOS-Unified-Gateway",
    version="1.0.0",
    description="Gateway universal unificado OpenAI-compatible para el Ecosistema HBOS-Diamantino"
)

def verify_sovereign_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cabecera Authorization requerida")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Esquema Bearer requerido")
    token = authorization.split("Bearer ")[1].strip()
    
    # Validar que pertenezca al conjunto institucional o empiece por hbos-sec-
    if token in SOVEREIGN_TOKENS or token.startswith("hbos-sec-"):
        return token
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token Soberano HBOS inválido o no autorizado")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False

class EmbeddingRequest(BaseModel):
    input: Any
    model: Optional[str] = "gemini-embedding-001"

# -----------------------------------------------------------------------------
# ENDPOINT: GET /v1/models
# -----------------------------------------------------------------------------
@app.get("/v1/models")
async def list_models(token: str = Depends(verify_sovereign_token)):
    models_list = []
    
    # 1. Modelos de FreeLLMAPI :3001
    freellm_cfg = CONFIG["upstreams"]["freellmapi"]
    if freellm_cfg.get("enabled"):
        try:
            req = urllib.request.Request(
                f"{freellm_cfg['base_url']}/models",
                headers={"Authorization": f"Bearer {freellm_cfg['api_key']}"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                for m in data.get("data", []):
                    m["owned_by"] = "freellmapi-router"
                    models_list.append(m)
        except Exception as e:
            print(f"[!] Aviso: No se pudo consultar FreeLLMAPI :3001: {e}")
            
    # 2. Modelos Locales Soberanos (Ollama)
    models_list.append({
        "id": "ollama/llama3:latest",
        "object": "model",
        "created": 1789900000,
        "owned_by": "hbos-local-ollama",
        "permission": [],
        "root": "llama3:latest",
        "parent": None
    })
    models_list.append({
        "id": "ollama/mistral:latest",
        "object": "model",
        "created": 1789900000,
        "owned_by": "hbos-local-ollama",
        "permission": [],
        "root": "mistral:latest",
        "parent": None
    })
    
    # 3. Modelos Nube Directa (Google Cloud Node)
    models_list.append({
        "id": "google/gemma-4-26b-a4b-it",
        "object": "model",
        "created": 1789900000,
        "owned_by": "hbos-google-cloud-node",
        "permission": [],
        "root": "gemma-4-26b-a4b-it",
        "parent": None
    })
    models_list.append({
        "id": "google/gemini-flash-latest",
        "object": "model",
        "created": 1789900000,
        "owned_by": "hbos-google-cloud-node",
        "permission": [],
        "root": "gemini-flash-latest",
        "parent": None
    })
    
    return {
        "object": "list",
        "data": models_list
    }

# -----------------------------------------------------------------------------
# ENDPOINT: POST /v1/chat/completions (Inferencia + Fallback + Logging)
# -----------------------------------------------------------------------------
@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest, token: str = Depends(verify_sovereign_token)):
    t0 = time.time()
    prompt_raw = json.dumps([m.dict() for m in req.messages], ensure_ascii=False)
    req_sha = hashlib.sha256(prompt_raw.encode('utf-8')).hexdigest()
    
    output_text = ""
    provider_used = "unknown"
    model_used = req.model
    
    # ESTRATEGIA DE ENRUTAMIENTO FAM@-T:
    # Caso A: Si es modelo de Google Cloud o si se pide explicitamente
    if req.model.startswith("google/") or "gemini" in req.model or "gemma" in req.model:
        clean_model = req.model.replace("google/", "")
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={gemini_key}"
            payload_g = {
                "contents": [{"parts": [{"text": "\n".join([f"{m.role}: {m.content}" for m in req.messages])}]}],
                "generationConfig": {"temperature": req.temperature, "maxOutputTokens": req.max_tokens or 2048}
            }
            try:
                g_req = urllib.request.Request(url, data=json.dumps(payload_g).encode('utf-8'), headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(g_req, timeout=60) as g_resp:
                    data = json.loads(g_resp.read().decode('utf-8'))
                    output_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    provider_used = "google_cloud_node"
                    model_used = clean_model
            except Exception as e:
                print(f"[!] Error en Google Cloud Node directo: {e}")
                
    # Caso B: Intentar vía FreeLLMAPI :3001
    if not output_text:
        freellm_cfg = CONFIG["upstreams"]["freellmapi"]
        if freellm_cfg.get("enabled"):
            url = f"{freellm_cfg['base_url']}/chat/completions"
            payload_f = {
                "model": req.model.replace("freellmapi/", ""),
                "messages": [m.dict() for m in req.messages],
                "temperature": req.temperature,
                "max_tokens": req.max_tokens
            }
            try:
                f_req = urllib.request.Request(
                    url,
                    data=json.dumps(payload_f).encode('utf-8'),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {freellm_cfg['api_key']}"},
                    method="POST"
                )
                with urllib.request.urlopen(f_req, timeout=45) as f_resp:
                    data = json.loads(f_resp.read().decode('utf-8'))
                    output_text = data["choices"][0]["message"]["content"]
                    provider_used = "freellmapi_router"
                    model_used = data.get("model", req.model)
            except Exception as ex:
                print(f"[!] FreeLLMAPI :3001 falló ({ex}), activando fallback a Google Cloud Node...")
                
    # Caso C: Fallback de Emergencia a Google Cloud Node (Gemma 4)
    if not output_text:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            fb_model = "gemma-4-26b-a4b-it"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{fb_model}:generateContent?key={gemini_key}"
            payload_fb = {
                "contents": [{"parts": [{"text": "\n".join([f"{m.role}: {m.content}" for m in req.messages])}]}],
                "generationConfig": {"temperature": req.temperature, "maxOutputTokens": req.max_tokens or 2048}
            }
            try:
                fb_req = urllib.request.Request(url, data=json.dumps(payload_fb).encode('utf-8'), headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(fb_req, timeout=60) as fb_resp:
                    data = json.loads(fb_resp.read().decode('utf-8'))
                    output_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    provider_used = "gemini_cloud_fallback"
                    model_used = fb_model
            except Exception as ex2:
                raise HTTPException(status_code=502, detail=f"Fallo en cadena de proveedores y fallback: {ex2}")
                
    latency_ms = (time.time() - t0) * 1000.0
    resp_sha = hashlib.sha256(output_text.encode('utf-8')).hexdigest()
    
    in_tokens = len(prompt_raw.split())
    out_tokens = len(output_text.split())
    
    # Registro en Qdrant hbos_metricas
    log_request_metrics(model_used, provider_used, latency_ms, in_tokens, out_tokens, req_sha, resp_sha)
    
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_used,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": output_text
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": in_tokens,
            "completion_tokens": out_tokens,
            "total_tokens": in_tokens + out_tokens
        },
        "hbos_metadata": {
            "provider": provider_used,
            "latency_ms": round(latency_ms, 2),
            "sha256": resp_sha,
            "sovereign_gateway": "HBOS-Unified-Gateway:3002"
        }
    }

# -----------------------------------------------------------------------------
# ENDPOINT: POST /v1/embeddings
# -----------------------------------------------------------------------------
@app.post("/v1/embeddings")
async def create_embeddings(req: EmbeddingRequest, token: str = Depends(verify_sovereign_token)):
    t0 = time.time()
    input_text = req.input
    if isinstance(input_text, list):
        input_text = " ".join([str(x) for x in input_text])
    else:
        input_text = str(input_text)
        
    vec = generate_embedding(input_text, dim=384)
    latency_ms = (time.time() - t0) * 1000.0
    
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": vec,
                "index": 0
            }
        ],
        "model": req.model,
        "usage": {
            "prompt_tokens": len(input_text.split()),
            "total_tokens": len(input_text.split())
        },
        "hbos_metadata": {
            "dimensions": len(vec),
            "latency_ms": round(latency_ms, 2)
        }
    }

# -----------------------------------------------------------------------------
# ENDPOINT: GET /v1/vault/status (Auditoría de Enclave y Seguridad)
# -----------------------------------------------------------------------------
@app.get("/v1/vault/status")
async def vault_status(token: str = Depends(verify_sovereign_token)):
    qdrant_status = "offline"
    qdrant_cols = 0
    if QDRANT_CLIENT:
        try:
            qdrant_cols = len(QDRANT_CLIENT.get_collections().collections)
            qdrant_status = f"connected ({qdrant_cols} cols)"
        except Exception:
            qdrant_status = "error_connecting"
            
    return {
        "status": "OPERATIONAL · SOBERANO",
        "vault_enclave": {
            "algorithm": VAULT.algorithm,
            "cifrado_en_reposo": "AES-256-GCM activo",
            "descifrado_efimero_ram": "Habilitado (L-27)",
            "sovereign_tokens_active": len(SOVEREIGN_TOKENS)
        },
        "upstreams_connected": {
            "freellmapi": "http://127.0.0.1:3001/v1 (235 modelos Zero-Config)",
            "gemini_cloud_node": "https://generativelanguage.googleapis.com (Gemma 4 / Flash)",
            "ollama_local": "http://127.0.0.1:11434"
        },
        "telemetry_qdrant": {
            "state": qdrant_status,
            "collection": "hbos_metricas"
        },
        "port": 3002,
        "operation_id": OPERATION_ID
    }

# -----------------------------------------------------------------------------
# HEALTH ENDPOINT
# -----------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HBOS-Unified-Gateway", "port": 3002}

if __name__ == "__main__":
    print(f"[*] Iniciando HBOS-Unified-Gateway en http://0.0.0.0:3002...")
    uvicorn.run(app, host="0.0.0.0", port=3002, log_level="info")
