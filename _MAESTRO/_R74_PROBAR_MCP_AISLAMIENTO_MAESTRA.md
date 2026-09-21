# R74 · PROBAR MCP NUEVOS EN AISLAMIENTO

## Regla
Todo MCP nuevo (o modificación de uno existente) debe:
  1. Probarse en aislamiento (sin añadirlo al `mcp_config.json`)
  2. Verificar que carga config correctamente
  3. Verificar que arranca sin error
  4. Verificar que responde a las funciones básicas
  5. Solo entonces añadirse al `mcp_config.json`
  6. Solo entonces reiniciarse Antigravity
  7. Verificar que carga con los demás

## Razón
El 21/09/2026, el MCP `hbos-chat-context` (server Python) causó un
conflicto en Antigravity porque no cargaba `.env.local` correctamente
desde el `cwd` de Antigravity.

Los MCP node existentes (gdrive, hbos-diamantino, diamantini-imagenes,
hbos-freellmapi) usan `env` en el JSON, no `.env.local`.

El server Python nuevo usa `load_dotenv()` y fallaba porque el `cwd`
de Antigravity no era el workspace.

## Lección
Los MCP nuevos (especialmente de tipo diferente: Python vs Node) deben
probarse en aislamiento antes de añadirlos al JSON.

## Protocolo
Para añadir un MCP nuevo:
  1. Desarrollar el server en `mcp/<nombre>/`
  2. Probar en aislamiento: `python mcp/<nombre>/server.py --test`
  3. Verificar que carga config correctamente (env, dotenv, etc.)
  4. Verificar que arranca sin error
  5. Verificar que responde a las funciones básicas
  6. Añadir al `mcp_config.json`
  7. Reiniciar Antigravity
  8. Verificar que carga con los demás

## Vigencia
Desde op=251.

## Documento canónico
`_MAESTRO/_R74_PROBAR_MCP_AISLAMIENTO_MAESTRA.md`
