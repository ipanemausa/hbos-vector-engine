import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const BASE_URL = 'http://127.0.0.1:3001';
const UNIFIED_API_KEY = 'freellmapi-70a0cfeb7458ecb31077fe5f0b1646069da621ebb16ff037';

const server = new Server(
  {
    name: 'hbos-freellmapi',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'list_models',
        description: 'Lista los modelos disponibles en el servidor local FreeLLMAPI (localhost:3001).',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'chat',
        description: 'Envía un prompt de chat a FreeLLMAPI y devuelve la respuesta generada.',
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
      const resp = await fetch(BASE_URL + '/v1/models', {
        headers: {
          'Authorization': 'Bearer ' + UNIFIED_API_KEY,
          'Accept': 'application/json'
        }
      });
      if (resp.ok) {
        const data = await resp.json();
        return {
          content: [{ type: 'text', text: JSON.stringify(data, null, 2) }],
        };
      } else {
        return {
          content: [{ type: 'text', text: 'FreeLLMAPI /v1/models status: ' + resp.status + ' ' + resp.statusText }],
        };
      }
    } catch (err) {
      return {
        isError: true,
        content: [{ type: 'text', text: 'Error conectando con FreeLLMAPI: ' + err.message }],
      };
    }
  }

  if (name === 'chat') {
    try {
      const model = (args && args.model) ? args.model : 'default';
      const prompt = (args && args.prompt) ? args.prompt : '';
      const payload = {
        model: model,
        messages: [{ role: 'user', content: prompt }]
      };
      const resp = await fetch(BASE_URL + '/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + UNIFIED_API_KEY
        },
        body: JSON.stringify(payload)
      });
      const data = await resp.text();
      return {
        content: [{ type: 'text', text: data }],
      };
    } catch (err) {
      return {
        isError: true,
        content: [{ type: 'text', text: 'Error en chat FreeLLMAPI: ' + err.message }],
      };
    }
  }

  if (name === 'tts') {
    try {
      const text = (args && args.text) ? args.text : '';
      const model = (args && args.model) ? args.model : 'default-tts';
      const resp = await fetch(BASE_URL + '/v1/audio/speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + UNIFIED_API_KEY
        },
        body: JSON.stringify({ input: text, model: model })
      });
      return {
        content: [{ type: 'text', text: 'TTS Solicitado a FreeLLMAPI. Status: ' + resp.status }],
      };
    } catch (err) {
      return {
        isError: true,
        content: [{ type: 'text', text: 'Error en tts FreeLLMAPI: ' + err.message }],
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
