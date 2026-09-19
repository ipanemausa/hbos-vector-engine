# HBOS-API KEY VAULT — ARQUITECTURA SOBERANA DE SEGURIDAD
### Sello: HBOS-Diamantino · Vector Engine
### Trazabilidad: `operation_id = 121` | Directiva Canónica ALEJAVI
### Patrón Asociado: P-41 · Lección: L-27

---

## 1. VISIÓN Y PRINCIPIOS DE DISEÑO
El **HBOS-API Key Vault** es el enclave criptográfico soberano diseñado para custodiar, arbitrar y auditar el consumo de credenciales de Inteligencia Artificial en el ecosistema HBOS.
Su misión central es erradicar la exposición de claves privadas de terceros en código fuente, scripts de pipeline, repositorios Git o terminales de usuario.

### Principios Fundamentales:
1. **Cifrado en Reposo de Grado Militar:** Toda API key se cifra localmente mediante algoritmo simétrico **AES-256-GCM** con vector de inicialización único por registro.
2. **Zero-Knowledge Upstream:** Los proveedores externos y routers públicos nunca reciben las claves en texto plano fuera del túnel HTTPS autenticado en memoria.
3. **Endpoints Propios y Clave Unificada HBOS:** Las aplicaciones y agentes de Antigravity no interactúan con las APIs de terceros directamente; consumen endpoints internos autenticados mediante una única clave soberana: `hbos-sec-...`.
4. **Auditoría e Inmutabilidad en Tiempo Real:** Cada invocación, tiempo de respuesta, volumen de tokens y costo amortizado se registra en Qdrant (`boveda_secretos` y `registro_ecosistema`).

---

## 2. ARQUITECTURA DE LA BÓVEDA

```
┌─────────────────────────────────────────────────────────────┐
│                 AGENTES / SCRIPTS / ANTIGRAVITY              │
│       Invocan con Token Soberano: Bearer hbos-sec-...        │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / Local Loopback (3001)
┌──────────────────────────────▼──────────────────────────────┐
│                    HBOS-API KEY VAULT                       │
│  - Validador de Token Soberano                              │
│  - SQLite Encriptada (AES-256-GCM)                          │
│  - Rotador de Cuotas & Limitador de Tasa (RPM/TPM)          │
│  - Módulo de Desencriptado Efímero en RAM                   │
└──────┬───────────────────────┬───────────────────────┬──────┘
       │ Inferencia Texto      │ Inferencia TTS        │ Inferencia Video
┌──────▼──────┐         ┌──────▼──────┐         ┌──────▼──────┐
│   Gemini /  │         │ ElevenLabs/ │         │  DashScope  │
│ FreeLLMAPI  │         │  CosyVoice2 │         │   Wan 2.1   │
└─────────────┘         └─────────────┘         └─────────────┘
```

---

## 3. ESPECIFICACIÓN DE ENDPOINTS PROPIOS

El Vault expone un Gateway compatible con la especificación estándar:

| Endpoint | Método | Descripción | Proveedores Asignados |
|---|---|---|---|
| `/v1/vault/status` | `GET` | Health check, estado de cuotas y proveedores activos. | Interno |
| `/v1/chat/completions` | `POST` | Proxy inteligente con arbitraje y failover dinámico. | FreeLLMAPI, Gemini, Groq |
| `/v1/audio/speech` | `POST` | Síntesis vocal con control LUFS y conmutación automática. | ElevenLabs, CosyVoice2 |
| `/v1/videos/generations`| `POST` | Orquestación asíncrona de video con webhook de finalización.| DashScope Wan 2.1 |
| `/v1/vault/audit` | `GET` | Consulta del histórico de auditoría por `operation_id`. | Qdrant Cloud |

---

## 4. GESTIÓN CRIPTOGRÁFICA Y CICLO DE VIDA (P-41 / L-27)
1. **Derivación de Clave Maestra:** La llave maestra deriva de PBKDF2 (100,000 iteraciones + salt aleatorio) resguardada en memoria protegida del sistema.
2. **Descifrado Efímero:** Las credenciales de proveedores (OpenAI, Gemini, ElevenLabs, DashScope) se descifran estrictamente en memoria volátil (RAM) en el milisegundo previo a emitir la llamada HTTPS.
3. **Destrucción Inmediata:** Al completarse la transmisión de los paquetes de red, el buffer de memoria es sobreescrito con ceros (zeroed out).
4. **Regla Inviolable L-27:** Las llaves privadas residen **exclusivamente** en HBOS-API. Cero filtración en logs, traces o repositorios.
