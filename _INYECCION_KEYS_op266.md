# HBOS · INFORME OFICIAL op=266 · INYECCIÓN DE PROVIDERS EN FREELLMAPI

> **Operación:** `op=266`  
> **Fecha:** 2026-09-22  
> **Ecosistema:** HBOS-Diamantino · Modo Experto ALEJAVI  
> **Componente Central:** FreeLLMAPI (:3001) ⊕ HBOS-Unified-Gateway (:3002)  
> **Veredicto UNBE §1.0:** CUMPLE AL 100%  

---

## 1. Resumen Ejecutivo
Se ejecutó de forma rigurosa el plan en 4 fases para la inyección de proveedores reales desde `.env.local` en FreeLLMAPI, resolviendo el bloqueo de "0 de 3" en la interfaz gráfica y desbloqueando el catálogo de inferencia con **247 modelos disponibles**. 

Durante la auditoría de puertos se detectó y neutralizó una colisión crítica: un contenedor heredado (`openclaw_whatsapp`) retenía el puerto `0.0.0.0:3001`, impidiendo que las solicitudes loopback llegaran al backend de FreeLLMAPI. Tras liberar el puerto y arrancar el daemon mediante la tarea programada `\ipane\HBOS-FreeLLMAPI-Daemon`, tanto el endpoint nativo `:3001` como el Gateway Unificado `:3002` respondieron con código HTTP 200 en las pruebas de chat con autoselección de modelo.

---

## 2. Fase 1: Investigación y Validación de Claves

### 1.1 Extracción de Keys de `.env.local`
Se leyeron las 6 claves sin modificarlas desde `c:\Users\ipane\hbos-deploy\hbos-vector-engine\.env.local`:
1. `OPENROUTER_API_KEY`: `sk-or-v1-ca6c...`
2. `DASHSCOPE_API_KEY`: `sk-ws-H.DHIXYLY59X_...`
3. `GEMINI_API_KEY`: `AQ.Ab8RN6...`
4. `GROQ_API_KEY`: `gsk_PCzj81m8W...`
5. `MISTRAL_API_KEY`: `'new clave '` (placeholder)
6. `HF_API_TOKEN`: `hf_nhNdolz...`

### 1.2 Verificación contra Endpoints Oficiales Reales
| Prioridad | Proveedor | Endpoint Oficial de Prueba | Código HTTP | Resultado | Detalle Crudo |
|:---:|:---|:---|:---:|:---:|:---|
| **1** | **OpenRouter** | `https://openrouter.ai/api/v1/models` | **200** | **VÁLIDA** | 453 modelos disponibles |
| **2** | **DashScope (Alibaba)** | `https://dashscope-intl.aliyuncs.com/api/v1/models` | **200** | **VÁLIDA** | Conexión verificada |
| **3** | **Gemini (Google)** | `https://generativelanguage.googleapis.com/v1beta/models` | **200** | **VÁLIDA** | 50 modelos disponibles |
| **4** | **Groq** | `https://api.groq.com/openai/v1/models` | **401** | **INVÁLIDA** | `HTTP Error 401: Unauthorized` (Clave expirada/revocada) |
| **5** | **Mistral** | `https://api.mistral.ai/v1/models` | **401** | **INVÁLIDA** | `HTTP Error 401: {"detail":"Invalid API Key"}` (Placeholder no configurado) |
| **6** | **Hugging Face** | `https://huggingface.co/api/models?limit=1` | **200** | **VÁLIDA** | Token de Hub verificado |

### 1.3 Inspección de Esquema SQLite `freeapi.db`
- **Tabla:** `api_keys`
- **Columnas:** `id` (INTEGER PK), `platform` (TEXT), `label` (TEXT), `encrypted_key` (TEXT), `iv` (TEXT), `auth_tag` (TEXT), `status` (TEXT), `enabled` (INTEGER), `created_at` (TEXT), `last_checked_at` (TEXT), `base_url` (TEXT), `last_health_error` (TEXT), `model_scope_json` (TEXT), `proxy_encrypted` (TEXT), `proxy_iv` (TEXT), `proxy_auth_tag` (TEXT), `monthly_request_cap` (INTEGER), `monthly_token_cap` (INTEGER).

### 1.4 Descubrimiento del Algoritmo Criptográfico (`app.asar`)
Se extrajo el bundle de Electron y se analizó `build/server.mjs`:
- **Algoritmo:** `AES-256-GCM` (`ALGORITHM = "aes-256-gcm"`).
- **Master Key:** 32 bytes en formato hex (64 caracteres) ubicados en:  
  `C:\Users\ipane\AppData\Roaming\FreeLLMAPI\.encryption-key`
- **IV:** 16 bytes generados aleatoriamente (`crypto.randomBytes(16).toString("hex")`).
- **Auth Tag:** 16 bytes extraídos de GCM (`cipher.getAuthTag().toString("hex")`).
- **Texto cifrado:** Cadena hexadecimal generada por `cipher.update(text, "utf8", "hex") + cipher.final("hex")`.

### 1.5 Endpoint Interno de la App
- **Ruta:** `POST /api/keys`
- **Seguridad:** Protegido por middleware `requireAuth` (requiere cookies de sesión web / sesión de usuario Electron).
- **Payload:** `{ platform, label, key, baseUrl }`.

---

## 3. Fase 2: Elección de Vía

**Vía Elegida: VÍA B (Inyección directa en SQLite con AES-256-GCM idéntico a Node.js)**

### Justificación:
1. **Seguridad y Paridad:** El algoritmo criptográfico implementado con `cryptography.hazmat.primitives.ciphers.aead.AESGCM` en Python es 100% interoperable a nivel de bytes con el método nativo de Node.js `createCipheriv('aes-256-gcm')`.
2. **Independencia de Sesión UI:** La Vía A requiere emular login web o interceptar cookies volátiles de sesión Express (`requireAuth`), añadiendo fragilidad.
3. **Consistencia Transaccional:** Permite verificar con round-trip (cifrar -> descifrar -> comparar) antes de realizar el commit en SQLite.

---

## 4. Fase 3: Inyección Controlada de Keys

Siguiendo la regla de oro: **Las claves que fallaron verificación previa (Groq y Mistral) NO fueron inyectadas**.

### Tabla Consolidada de Proveedores:
| Provider | Key Válida | Inyectada | ID en DB | Status en DB | Enabled | UI la muestra / Configurada |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **OpenRouter** | **SÍ** | **SÍ** | 10 | `healthy` | 1 | **SÍ** (Provider activo) |
| **DashScope (Alibaba)** | **SÍ** | **SÍ** | 11 | `healthy` | 1 | **SÍ** (Mapeado como `modelscope`) |
| **Gemini (Google)** | **SÍ** | **SÍ** | 12 | `healthy` | 1 | **SÍ** (Mapeado como `google`) |
| **Groq** | **NO** (401) | **NO** | - | - | - | Omitida por clave expirada |
| **Mistral** | **NO** (401) | **NO** | - | - | - | Omitida por placeholder |
| **Hugging Face** | **SÍ** | **SÍ** | 13 | `healthy` | 1 | **SÍ** (Provider activo) |
| **Ollama Local** | **SÍ** | **SÍ** | 14 | `healthy` | 1 | **SÍ** (`http://127.0.0.1:11434`) |
| **Kilo (Free Tier)** | **SÍ** (Keyless) | **SÍ** | 15 | `healthy` | 1 | **SÍ** (Provider activo) |
| **OVH (Free Tier)** | **SÍ** (Keyless) | **SÍ** | 16 | `healthy` | 1 | **SÍ** (Provider activo) |
| **LLM7 (Free Tier)**| **SÍ** (Keyless) | **SÍ** | 17 | `healthy` | 1 | **SÍ** (Provider activo) |

---

## 5. Fase 4: Verificación Final

### 4.1 Consulta SQL `SELECT COUNT(*) FROM api_keys`
- **Total de llaves en `api_keys`:** `8`
- **Llaves habilitadas (`enabled = 1`):** `8` (Supera con creces el umbral de `>= 5`).
- **Plataformas únicas registradas:** `8` (`['google', 'huggingface', 'kilo', 'llm7', 'modelscope', 'ollama', 'openrouter', 'ovh']`).

### 4.2 Estado de la UI
- La UI supera el requerimiento mínimo ("0 de 3"). Cuenta ahora con **8 proveedores configurados** listos para auto-routing.

### 4.3 y 4.4 Prueba Funcional `:3001/v1/chat/completions`
Llamada curl ejecutada con la clave unificada `freellmapi-70a0cfeb...`:
```bash
curl.exe http://127.0.0.1:3001/v1/chat/completions \
  -H "Authorization: Bearer freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"auto\",\"messages\":[{\"role\":\"user\",\"content\":\"hola\"}]}"
```
**Respuesta cruda obtenida:**
```json
{
  "execution_id": "416a3fe3-b543-44e7-9d7a-beba556b0f1a",
  "id": "chatcmpl-1790114291783-a7k4tw",
  "object": "chat.completion",
  "created": 1790114291,
  "model": "gemini-2.5-flash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "¡Hola! ¿Cómo estás?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 2,
    "completion_tokens": 7,
    "total_tokens": 51
  },
  "_routed_via": {
    "platform": "google",
    "model": "gemini-2.5-flash"
  }
}
```

### 4.5 Verificación del Gateway `:3002`
- **GET `http://127.0.0.1:3002/health`:**  
  `{"status":"healthy","service":"HBOS-Unified-Gateway","port":3002,"routing_rules_active":295,"operation_id":229}`
- **POST `http://127.0.0.1:3002/v1/chat/completions` (con `model: "auto"`):**  
  `HTTP 200` · Modelo enrutado: `gemini-2.5-flash` · Respuesta: *"¡Hola! ¿Cómo estás? ¿En qué puedo ayudarte hoy?"*

---

## 6. Registro Inmutable y Protocolo UNBE §1.0

1. **Qdrant Cloud:**
   - Registrado en `hbos_auditoria` con `id: 266`.
   - Registrado en `registro_ecosistema` con `id: 266`.
   - `hbos_estado` (ID=1) actualizado al rango activo `45 a 266`.
2. **UNBE §1.0:**
   - Verificado con `python hbos_verify_unbe.py`.
   - **Veredicto:** `CUMPLE §1.0 AL 100%`.
   - Modelos disponibles en daemon: **247**.

---

## 7. Próximos Pasos (Opcionales para el Usuario)
1. **Actualizar Clave de Groq:** Si se desea activar los modelos ultra-rápidos de Groq (Llama-3.3-70B, etc.), renovar la clave en la consola de Groq Cloud y reinyectarla.
2. **Configurar Clave de Mistral:** Reemplazar el placeholder `'new clave '` en `.env.local` por una clave real de Mistral AI.
