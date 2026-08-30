import vectorEngine from "./vector_engine.js";

const casos = [
  { id: 1, descripcion: "Ir al grano en documentos largos", herramientas: ["Google AI Studio"], modelos: ["Gemini"], categoria: "vida_cotidiana" },
  { id: 2, descripcion: "Asistente de compras con filtros dinámicos", herramientas: ["ChatGPT"], modelos: ["GPT"], categoria: "vida_cotidiana" },
  { id: 3, descripcion: "Planificar el día con matriz de urgencia", herramientas: ["ChatGPT"], modelos: ["GPT"], categoria: "vida_cotidiana" },
  { id: 4, descripcion: "Segunda opinión rápida", herramientas: ["ChatGPT"], modelos: ["GPT"], categoria: "vida_cotidiana" },
  { id: 5, descripcion: "Mejorar fotografías", herramientas: ["Nano Banana Pro"], modelos: ["Imagen"], categoria: "vida_cotidiana" },
  { id: 6, descripcion: "Identificar imágenes", herramientas: ["IA multimodal"], modelos: ["Qwen"], categoria: "vida_cotidiana" },
  { id: 7, descripcion: "Ayuda visual con manuales", herramientas: ["Gemini"], modelos: ["Gemini"], categoria: "vida_cotidiana" },
  { id: 8, descripcion: "Crear apps personales", herramientas: ["Canvas Gemini"], modelos: ["Gemini"], categoria: "vida_cotidiana" },
  { id: 9, descripcion: "Recomendaciones por voz", herramientas: ["Llamadas IA"], modelos: ["Gemini"], categoria: "vida_cotidiana" },
  { id: 10, descripcion: "Asistencia por videollamada", herramientas: ["Gemini"], modelos: ["Gemini"], categoria: "vida_cotidiana" },
  { id: 11, descripcion: "Planificar viajes", herramientas: ["Gemini"], modelos: ["Gemini"], categoria: "vida_cotidiana" },
  { id: 12, descripcion: "Resúmenes diarios", herramientas: ["Tareas recurrentes"], modelos: ["Perplexity"], categoria: "vida_cotidiana" },
  { id: 13, descripcion: "Música personalizada", herramientas: ["Suno AI"], modelos: ["Suno"], categoria: "vida_cotidiana" },
  { id: 14, descripcion: "Previsión de inversión", herramientas: ["Canvas Gemini"], modelos: ["Gemini"], categoria: "vida_cotidiana" },
  { id: 15, descripcion: "Desactivar entrenamiento de modelos", herramientas: ["Ajustes"], modelos: [], categoria: "trabajo" },
  { id: 16, descripcion: "Currículum perfecto", herramientas: ["IA"], modelos: ["DeepSeek"], categoria: "trabajo" },
  { id: 17, descripcion: "Prototipado rápido", herramientas: ["Stitch"], modelos: [], categoria: "trabajo" },
  { id: 18, descripcion: "Contenido de marca", herramientas: ["Pomegi"], modelos: [], categoria: "trabajo" },
  { id: 19, descripcion: "Agilizar emails", herramientas: ["Gemini"], modelos: ["Gemini"], categoria: "trabajo" },
  { id: 20, descripcion: "Auditar web", herramientas: ["Antigravity"], modelos: ["DeepSeek"], categoria: "trabajo" },
  { id: 21, descripcion: "Organizar archivos", herramientas: ["Manus"], modelos: [], categoria: "trabajo" },
  { id: 22, descripcion: "Locutar textos", herramientas: ["ElevenLabs"], modelos: [], categoria: "trabajo" },
  { id: 23, descripcion: "Organizar información", herramientas: ["NotebookLM"], modelos: [], categoria: "trabajo" },
  { id: 24, descripcion: "Simular entrevistas", herramientas: ["IA"], modelos: ["Gemini"], categoria: "trabajo" },
  { id: 25, descripcion: "Simplificar datos en dashboards", herramientas: ["Canvas Gemini"], modelos: ["Gemini"], categoria: "trabajo" },
  { id: 26, descripcion: "Resúmenes de reuniones", herramientas: ["ClickUp"], modelos: [], categoria: "trabajo" },
  { id: 27, descripcion: "Presentaciones profesionales", herramientas: ["Canvas Gemini"], modelos: ["Gemini"], categoria: "trabajo" },
  { id: 28, descripcion: "Modo estudio con profesor paciente", herramientas: ["IA"], modelos: ["DeepSeek"], categoria: "aprendizaje" },
  { id: 29, descripcion: "Investigación profunda", herramientas: ["NotebookLM"], modelos: ["Perplexity"], categoria: "aprendizaje" },
  { id: 30, descripcion: "Simplificar vídeos", herramientas: ["Google AI Studio"], modelos: ["Whisper"], categoria: "aprendizaje" },
  { id: 31, descripcion: "Memorizar con técnicas", herramientas: ["ChatGPT"], modelos: ["GPT"], categoria: "aprendizaje" },
  { id: 32, descripcion: "Autoevaluación con flashcards", herramientas: ["IA"], modelos: ["Gemini"], categoria: "aprendizaje" },
  { id: 33, descripcion: "Mapas mentales", herramientas: ["NotebookLM"], modelos: [], categoria: "aprendizaje" },
  { id: 34, descripcion: "Apps educativas", herramientas: ["NotebookLM"], modelos: ["Gemini"], categoria: "aprendizaje" },
  { id: 35, descripcion: "Ayuda experta 24/7", herramientas: ["Google AI Studio"], modelos: ["Gemini"], categoria: "crecimiento" },
  { id: 36, descripcion: "Plan de carrera", herramientas: ["IA"], modelos: ["DeepSeek"], categoria: "crecimiento" },
  { id: 37, descripcion: "Apps low-code", herramientas: ["Horizon"], modelos: [], categoria: "crecimiento" },
  { id: 38, descripcion: "Crear IAs propias", herramientas: ["Google AI Studio"], modelos: ["Gemini"], categoria: "crecimiento" },
  { id: 39, descripcion: "Aprender idiomas", herramientas: ["IA"], modelos: ["Gemini"], categoria: "crecimiento" },
  { id: 40, descripcion: "Practicar idiomas con voz", herramientas: ["ElevenLabs"], modelos: [], categoria: "crecimiento" },
  { id: 41, descripcion: "Automatizar Google", herramientas: ["n8n"], modelos: [], categoria: "crecimiento" },
  { id: 42, descripcion: "Automatizaciones escalables", herramientas: ["n8n", "Make", "Zapier"], modelos: [], categoria: "crecimiento" },
  { id: 43, descripcion: "Animar historias", herramientas: ["Google Flow"], modelos: [], categoria: "crecimiento" },
  { id: 44, descripcion: "Sincronizar miles de apps", herramientas: ["Make", "Zapier"], modelos: [], categoria: "crecimiento" },
  { id: 45, descripcion: "Crear IAs propias", herramientas: ["Google AI Studio"], modelos: ["Gemini"], categoria: "crecimiento" }
];

await vectorEngine.init();

for (const c of casos) {
  await vectorEngine.addCase(c.id, c.descripcion, c.herramientas, c.modelos, c.categoria);
  console.log(`Caso ${c.id} cargado`);
}

console.log("45 casos cargados");
