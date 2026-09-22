# HBOS · op=271 · Auditoría de Providers Faltantes y Catálogo PLATFORMS

**Operación:** op=271  
**Fecha:** 2026-09-22 19:02:00  
**Ecosistema:** FreeLLMAPI (:3001) ⊕ HBOS Unified Gateway (:3002) ⊕ Qdrant Cloud

---

## 1. Cruz de Plataformas: PLATFORMS Enum vs Keys Disponibles

El enum interno de FreeLLMAPI define **28 plataformas**. A continuación se documenta el estado riguroso de cada una:

| # | Provider / Plataforma | Key en Entorno Local | Estado en FreeLLMAPI (:3001) | URL de Registro / Consola Oficial |
|---|----------------------|----------------------|------------------------------|-----------------------------------|
| 1 | **openrouter** | `sk-or-v1-...d4a5` | `healthy` (enabled=1, ID 10) | https://openrouter.ai/keys |
| 2 | **modelscope** | `sk-ws-...bNex` | `invalid` (enabled=0, ID 11) | https://modelscope.cn |
| 3 | **google** | `AQ.Ab8RN...VA8Q` | `healthy` (enabled=1, ID 12) | https://aistudio.google.com/app/apikey |
| 4 | **huggingface** | `hf_nhNdo...ztIi` | `healthy` (enabled=1, ID 13) | https://huggingface.co/settings/tokens |
| 5 | **ollama** | Conexión local (:11434) | `healthy` (enabled=1, ID 14) | http://localhost:11434 |
| 6 | **kilo** | Tier gratuito nativo | `healthy` (enabled=1, ID 15) | https://api.kilo.ai |
| 7 | **ovh** | Tier gratuito nativo | `healthy` (enabled=1, ID 16) | https://endpoints.kepler.ai.cloud.ovh.net |
| 8 | **llm7** | Tier gratuito nativo | `healthy` (enabled=1, ID 17) | https://llm7.io |
| 9 | **groq** | `gsk_PCzj...78dI` | `healthy` (enabled=1, ID 18) | https://console.groq.com/keys |
| 10 | **github** | `gho_qd...vKdA` | `healthy` (enabled=1, ID 19) | https://github.com/settings/tokens |
| 11 | **cerebras** | No configurada | Sin key | https://cloud.cerebras.ai |
| 12 | **sail** | No configurada | Sin key | https://sailresearch.com |
| 13 | **electronhub** | No configurada | Sin key | https://electronhub.ai |
| 14 | **experiential** | No configurada | Sin key | https://experientiallabs.ai |
| 15 | **router9** | No configurada | Sin key | https://router9.ai |
| 16 | **septor** | No configurada | Sin key | https://septorlabs.com |
| 17 | **clod** | No configurada | Sin key | https://clod.io |
| 18 | **speechify** | No configurada (TTS) | Sin key | https://speechify.com/api |
| 19 | **blaze** | No configurada | Sin key | https://blazeapi.org |
| 20 | **lucidity** | No configurada | Sin key | https://lucidity.sh |
| 21 | **logfare** | No configurada | Sin key | https://logfare.ai |
| 22 | **bai** | No configurada | Sin key | https://api.b.ai |
| 23 | **radeon** | No configurada | Sin key | https://developer.amd.com.cn/radeon |
| 24 | **nvidia** | No configurada | Sin key | https://build.nvidia.com |
| 25 | **mistral** | Placeholder no válido | Sin key válida | https://console.mistral.ai/api-keys |
| 26 | **cohere** | No configurada | Sin key | https://dashboard.cohere.com/api-keys |
| 27 | **cloudflare** | No configurada | Sin key (`account_id:token`) | https://dash.cloudflare.com/ai |
| 28 | **zhipu** | No configurada | Sin key | https://open.bigmodel.cn |
| 29 | **pollinations** | Cuenta requerida | Sin key | https://pollinations.ai |
| 30 | **opencode** | No configurada | Sin key | https://opencode.ai |

---

## 2. Veredicto de Inyección op=271

- **Regla Estricta Cumplida:** Cero invención de claves y cero inyección de claves 401/403.
- **Proveedores Activos y Saludables en DB:** 9 plataformas (`openrouter`, `google`, `groq`, `huggingface`, `ollama`, `kilo`, `ovh`, `llm7`, `github`).
- **Próximos Pasos de Expansión:** Para habilitar Cerebras, NVIDIA NIM o Mistral, basta con obtener una clave gratuita en sus respectivas consolas indicadas arriba e inyectarla con el script maestro.
