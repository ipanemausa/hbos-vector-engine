import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { DatabaseSync } from 'node:sqlite';
import os from 'node:os';
import path from 'node:path';

const BASE_URL = 'http://127.0.0.1:3001';
const OLLAMA_URL = 'http://127.0.0.1:11434';
const UNIFIED_API_KEY = 'freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037';
const DB_PATH = path.join(process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming'), 'FreeLLMAPI', 'freeapi.db');

const server = new Server(
  {
    name: 'hbos-freellmapi',
    version: '2.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Helper para pausas asíncronas
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Reintentos automáticos con retroceso progresivo (Resiliencia ante arranque en frío)
async function fetchWithRetry(url, options, maxRetries = 3, delayMs = 600) {
  let lastErr = null;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const resp = await fetch(url, options);
      return resp;
    } catch (err) {
      lastErr = err;
      if (attempt < maxRetries) {
        console.error(`[hbos-freellmapi] Intento ${attempt}/${maxRetries} falló (${err.message}). Reintentando en ${delayMs}ms...`);
        await sleep(delayMs);
        delayMs = Math.round(delayMs * 1.5);
      }
    }
  }
  throw lastErr;
}

// Fallback directo a SQLite: Lee freeapi.db si el daemon HTTP aún no levantó el socket
function getModelsFromSqlite() {
  try {
    const db = new DatabaseSync(DB_PATH, { openReadOnly: true });
    const stmt = db.prepare('SELECT model_id, display_name, platform, context_window, enabled FROM models WHERE enabled=1');
    const rows = stmt.all();
    db.close();

    const data = rows.map((r) => ({
      id: r.model_id,
      object: 'model',
      created: 0,
      owned_by: r.platform,
      name: r.display_name,
      context_window: r.context_window,
      context_length: r.context_window,
      available: true,
      unavailable_reason: null,
      source: 'sqlite_direct_fallback'
    }));

    return {
      object: 'list',
      data: data,
      _meta: {
        total: data.length,
        source: 'sqlite_direct_fallback',
        timestamp: new Date().toISOString(),
        note: 'Recuperado directamente de freeapi.db con node:sqlite mientras el daemon HTTP :3001 iniciaba.'
      }
    };
  } catch (err) {
    console.error('[hbos-freellmapi] Error en getModelsFromSqlite:', err.message);
    return null;
  }
}

// Fallback a Ollama local (:11434) si FreeLLMAPI :3001 está temporalmente no disponible
async function tryOllamaChat(model, prompt) {
  try {
    console.error('[hbos-freellmapi] Intentando fallback de emergencia a Ollama local (:11434)...');
    const resp = await fetch(`${OLLAMA_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: model && model !== 'default' && model !== 'auto' ? model : 'llama3',
        messages: [{ role: 'user', content: prompt }],
        stream: false
      })
    });
    if (resp.ok) {
      const data = await resp.json();
      return {
        id: 'chatcmpl-ollama-fallback',
        object: 'chat.completion',
        model: data.model || model,
        choices: [
          {
            index: 0,
            message: { role: 'assistant', content: data.message?.content || '' },
            finish_reason: 'stop'
          }
        ],
        _routed_via: { platform: 'ollama_local_fallback', model: data.model }
      };
    }
  } catch (e) {
    console.error('[hbos-freellmapi] Fallback a Ollama no disponible:', e.message);
  }
  return null;
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'list_models',
        description: 'Lista los modelos disponibles en FreeLLMAPI con tolerancia a fallos y fallback directo a SQLite.',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'chat',
        description: 'Envía un prompt de chat a FreeLLMAPI con retry automático y fallback a Ollama local si :3001 está en frío.',
        inputSchema: {
          type: 'object',
          properties: {
            prompt: { type: 'string', description: 'El mensaje o prompt a enviar' },
            model: { type: 'string', description: 'Nombre del modelo a usar (opcional)' },
          },
          required: ['prompt'],
        },
      },
      {
        name: 'tts',
        description: 'Genera audio a partir de texto usando los motores TTS configurados en FreeLLMAPI.',
        inputSchema: {
          type: 'object',
          properties: {
            text: { type: 'string', description: 'Texto a sintetizar en audio' },
            model: { type: 'string', description: 'Modelo TTS (opcional)' },
          },
          required: ['text'],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'list_models') {
    try {
      const resp = await fetchWithRetry(BASE_URL + '/v1/models', {
        headers: {
          'Authorization': 'Bearer ' + UNIFIED_API_KEY,
          'Accept': 'application/json'
        }
      }, 3, 500);

      if (resp.ok) {
        const data = await resp.json();
        return {
          content: [{ type: 'text', text: JSON.stringify(data, null, 2) }],
        };
      }
    } catch (err) {
      console.error('[hbos-freellmapi] :3001 no respondió a list_models tras reintentos. Activando fallback SQLite...');
    }

    // Fallback garantizado: si HTTP falla, leer directamente SQLite freeapi.db
    const fallbackData = getModelsFromSqlite();
    if (fallbackData) {
      return {
        content: [{ type: 'text', text: JSON.stringify(fallbackData, null, 2) }],
      };
    }

    return {
      isError: false,
      content: [{ type: 'text', text: 'FreeLLMAPI se encuentra iniciando el servicio. Por favor espere unos segundos e intente nuevamente.' }],
    };
  }

  if (name === 'chat') {
    const model = (args && args.model) ? args.model : 'auto';
    const prompt = (args && args.prompt) ? args.prompt : '';
    const payload = {
      model: model,
      messages: [{ role: 'user', content: prompt }]
    };

    try {
      const resp = await fetchWithRetry(BASE_URL + '/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + UNIFIED_API_KEY
        },
        body: JSON.stringify(payload)
      }, 3, 500);

      if (resp.ok) {
        const data = await resp.text();
        return {
          content: [{ type: 'text', text: data }],
        };
      }
    } catch (err) {
      console.error('[hbos-freellmapi] :3001 no respondió a chat tras reintentos. Evaluando fallback alternativo...');
    }

    // Intento de fallback a Ollama local
    const ollamaResp = await tryOllamaChat(model, prompt);
    if (ollamaResp) {
      return {
        content: [{ type: 'text', text: JSON.stringify(ollamaResp, null, 2) }],
      };
    }

    // Respuesta degradada limpia (nunca crashea el protocolo MCP)
    return {
      isError: false,
      content: [{
        type: 'text',
        text: JSON.stringify({
          status: 'SERVICE_INITIALIZING',
          message: 'FreeLLMAPI (:3001) está inicializando sus proveedores de IA tras el arranque del sistema. Intente de nuevo en 5 segundos.',
          retry_suggested: true
        }, null, 2)
      }],
    };
  }

  if (name === 'tts') {
    try {
      const text = (args && args.text) ? args.text : '';
      const model = (args && args.model) ? args.model : 'default-tts';
      const resp = await fetchWithRetry(BASE_URL + '/v1/audio/speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + UNIFIED_API_KEY
        },
        body: JSON.stringify({ input: text, model: model })
      }, 2, 500);

      return {
        content: [{ type: 'text', text: 'TTS Solicitado a FreeLLMAPI. Status: ' + resp.status }],
      };
    } catch (err) {
      return {
        isError: false,
        content: [{ type: 'text', text: 'TTS no disponible mientras FreeLLMAPI inicia: ' + err.message }],
      };
    }
  }

  throw new Error('Tool no reconocida: ' + name);
});

async function run() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

run().catch((err) => {
  console.error('Fatal error en hbos-freellmapi MCP server:', err);
  process.exit(1);
});
