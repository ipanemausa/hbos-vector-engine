# Google AI · Aprendizaje acompañado · 24SEP2026

## Fuente
Video: Adiós Tutoriales... Google te Regala un PROFESOR con IA GRATIS
URL: https://www.youtube.com/watch?v=MDZoiwPl2QU&t=117s
Canal: Alejavi
Fecha: 24/09/2026

## Capacidades documentadas
- 01:17 Gemini 3.8 Live → https://aistudio.google.com/live
- 04:33 Aprendizaje acompañado (núcleo)
- 06:18 Gemini Live mobile
- 07:30 Investigaciones por voz
- 08:33 OpenStax recursos académicos
- 11:33 Shorts educativos
- 13:33 Ubicaciones globales
- 15:11 Aprendizaje inmersivo → https://gemini.google.com/immersive-view
- 17:30 Diseña app didáctica → https://stitch.google.com/
- 20:03 Crear curso interactivo → https://notebook.google.com/
- 23:03 Buscador inteligente → https://www.google.com/ai
- 26:44 Informes interactivos
- 29:27 Crear materiales

## Patrón a emular en HBOS (NO dependencia)
Input multimodal → FreeLLMAPI razona → Arbitraje auto →
Output interactivo → Registro Qdrant/Git/Drive

## Mapeo HBOS
| Google AI | Equivalente HBOS |
|-----------|------------------|
| Gemini 3.8 Live | FreeLLMAPI auto:reasoning + auto:vision |
| Buscador inteligente | hbos-run "tarea" "auto:reasoning" |
| Notebook | hbos_conocimiento + R768 |
| OpenStax | Vectorización .md maestros |
| Stitch | Antigravity + patrón operador |
| Vista Inmersiva | Pipeline AnchorVivo (Ep05) |
| Aprendizaje acompañado | Perfil aprendizaje FreeLLMAPI |

## Rol del asistente
NO dar bloques fraccionados. SÍ bloques completos por fase.
NO confirmar sin verificación real. SÍ verificar con evidencia cruda.

ANCLADO · 92426Tarde · op=304
