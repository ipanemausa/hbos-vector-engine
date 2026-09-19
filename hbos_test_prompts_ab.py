"""
hbos_test_prompts_ab.py — A/B TEST AUTOMATIZADO DE PROMPTS
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Inspirado en la mecánica de prueba automática de la app LLMAPI
Trazabilidad: operation_id = 216
"""

import os
import sys
import json
import time
import urllib.request
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
TEMPERATURE = 0.2
MAX_OUTPUT_TOKENS = 4000
SEED = 42

def ejecutar_inferencia(prompt_texto, label="PROMPT"):
    print(f"[*] Lanzando {label} contra modelo={MODEL_NAME} (temp={TEMPERATURE}, seed={SEED})...")
    t0 = time.time()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt_texto}]}],
        "generationConfig": {
            "temperature": TEMPERATURE,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "topP": 0.95
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                texto = data['candidates'][0]['content']['parts'][0]['text']
                elapsed = round(time.time() - t0, 3)
                print(f"[OK] {label} completado en {elapsed}s ({len(texto.split())} palabras, {len(texto)} chars).")
                return texto, elapsed
        except Exception as e:
            print(f"[!] Reintento {attempt+1}/{max_attempts} para {label}: {e}")
            time.sleep(2)
            if attempt == max_attempts - 1:
                raise RuntimeError(f"Fallo definitivo ejecutando {label}: {e}")

def main():
    print("==========================================================================")
    print(">>> [HBOS PROMPT A/B TEST] EJECUTOR AUTOMÁTICO ESTILO LLMAPI (op 216) <<<")
    print("==========================================================================")
    print(f"• Proveedor:  Google AI Studio API")
    print(f"• Modelo:     {MODEL_NAME}")
    print(f"• Parámetros: temperature={TEMPERATURE}, max_tokens={MAX_OUTPUT_TOKENS}, seed={SEED}")
    print(f"• Formato:    Markdown canónico §0–§10\n")

    os.makedirs("prompts", exist_ok=True)

    # 1. Cargar Input para Variante A
    with open("G:/My Drive/HBOS-Diamantino/_MAESTRO/_PROMPT_TOTAL_R768_v3.md", "r", encoding="utf-8") as f:
        r768_text = f.read()

    reporte_215 = """
REPORTE FINAL OPERACIÓN 215 (HBOS AUTOPILOT TOTAL R768):
- Estado: HEALTHY en 5/5 subsistemas (Qdrant 17 colecciones, 4 MCPs, FreeLLMAPI localhost:3001 con 237 modelos).
- Redundancia triple: 42 documentos en Local, Drive _MAESTRO y Backup con coincidencia exacta de bytes.
- Salud de cuotas: Gemini activa, Groq activa, DashScope pausada HTTP 403, Fal.ai agotada, ElevenLabs pausada.
- Factoría Diamantino: Ep02/Ep03 completados responsive, Ep04 con 10 voces masterizadas EBU R128 (-14 LUFS).
- Watchdog, Healthcheck y Auto-Repair validados en producción desatendida.
"""

    prompt_a_completo = f"""ACTÚA COMO: Experto ALEJAVI (Orquestador Supremo del Ecosistema Soberano HBOS-Diamantino).
MISIÓN: Producir directamente el PROMPT CONCEPTUAL AGÉNTICO MAESTRO R769 completo y ejecutable.

INPUT EMPÍRICO DE CONSOLIDACIÓN:
--- PROMPT MAESTRO R768 ---
{r768_text}

--- REPORTE FINAL OP=215 ---
{reporte_215}

INSTRUCCIÓN:
Genera directamente el Prompt Conceptual Agéntico Maestro R769 estructurado estrictamente en las 11 secciones canónicas (§0 a §10):
§0 · IDENTIDAD Y ROL
§1 · TAREA CERO OBLIGATORIA
§2 · ARQUITECTURA DE CÓMPUTO SOBERANO Y BARRERAS FÍSICAS
§3 · COMPONENTES DEL ECOSISTEMA Y DIRECTORIO CANÓNICO
§4 · MOTOR DE DECISIÓN Y ARBITRAJE DE MODELOS
§5 · MOTOR AUDIOVISUAL CANÓNICO (FACTORÍA DIAMANTINO)
§6 · PROTOCOLO AUTOPILOT Y SELF-REPAIR DESATENDIDO
§7 · GOBERNANZA, INVARIANTES Y BARRERAS DE ENTRADA (PATRÓN P-10)
§8 · FORMULACIÓN MATEMÁTICA Y MATRIZ VECTORIAL R768
§9 · ESQUEMA DE TRAZABILIDAD Y REGISTRO INMUTABLE
§10 · PROTOCOLO DE SALIDA Y ENTREGABLES OBLIGATORIOS

REGLAS: Cero placeholders, cero fracciones, completamente autocontenido y listo para ejecución desatendida.
"""

    # 2. Cargar Input para Variante B
    prompt_b_completo = """ACTÚA COMO: Experto ALEJAVI (Orquestador Supremo del Ecosistema Soberano HBOS-Diamantino).
MISIÓN: Conceptualizar el salto evolutivo R768 → R769 mediante investigación conceptual previa.

INPUT CONCEPTUAL:
Pregunta de investigación ontológica: "¿Qué significa auto-evolucionar el sistema en el Ecosistema Soberano HBOS-Diamantino?".

INSTRUCCIÓN EN 2 PARTES:
PARTE I · INVESTIGACIÓN CONCEPTUAL PREVIA:
Define con rigor ontológico, sistémico y matemático qué significa auto-evolucionar el sistema en HBOS:
1. Autopoiesis computacional bajo invariantes topológicas (respeto inquebrantable a las barreras físicas y soberanía del operador humano P-10).
2. Ciclo OODA meta-cognitivo recursivo (Observar telemetría -> Orientar con lecciones históricas L-01..L-42 -> Decidir por arbitraje multi-criterio -> Actuar con self-repair y auto-commit).
3. Optimización del gradiente de resiliencia ante contingencias de cuota (bifurcaciones locales abiertas $0.00).

PARTE II · PROMPT CONCEPTUAL AGÉNTICO MAESTRO R769:
Tras fundamentar la ontología anterior, genera el Prompt Maestro R769 completo estructurado en las 11 secciones canónicas (§0 a §10):
§0 · IDENTIDAD Y ROL
§1 · TAREA CERO OBLIGATORIA
§2 · ARQUITECTURA DE CÓMPUTO SOBERANO Y BARRERAS FÍSICAS
§3 · COMPONENTES DEL ECOSISTEMA Y DIRECTORIO CANÓNICO
§4 · MOTOR DE DECISIÓN Y ARBITRAJE DE MODELOS
§5 · MOTOR AUDIOVISUAL CANÓNICO (FACTORÍA DIAMANTINO)
§6 · PROTOCOLO AUTOPILOT Y SELF-REPAIR DESATENDIDO
§7 · GOBERNANZA, INVARIANTES Y BARRERAS DE ENTRADA (PATRÓN P-10)
§8 · FORMULACIÓN MATEMÁTICA Y MATRIZ VECTORIAL R768
§9 · ESQUEMA DE TRAZABILIDAD Y REGISTRO INMUTABLE
§10 · PROTOCOLO DE SALIDA Y ENTREGABLES OBLIGATORIOS

REGLAS: Cero placeholders, cero fracciones, completamente autocontenido y listo para ejecución desatendida.
"""

    # Guardar los dos prompts de entrada
    with open("prompts/PROMPT_INPUT_A.md", "w", encoding="utf-8") as f:
        f.write(prompt_a_completo)
    with open("prompts/PROMPT_INPUT_B.md", "w", encoding="utf-8") as f:
        f.write(prompt_b_completo)
    print("[OK] PROMPT A y PROMPT B almacenados en prompts/PROMPT_INPUT_A.md y prompts/PROMPT_INPUT_B.md")

    # Ejecutar Variante A
    res_a, t_a = ejecutar_inferencia(prompt_a_completo, label="VARIANTE A (Consolidación Directa)")
    with open("prompts/RESULTADO_PROMPT_A.md", "w", encoding="utf-8") as f:
        f.write(res_a)

    # Esperar 2 segundos para evitar rate limit de Gemini
    time.sleep(2)

    # Ejecutar Variante B
    res_b, t_b = ejecutar_inferencia(prompt_b_completo, label="VARIANTE B (Investigación Previa)")
    with open("prompts/RESULTADO_PROMPT_B.md", "w", encoding="utf-8") as f:
        f.write(res_b)

    print("\n[OK] Ambos resultados generados exitosamente por el modelo fijado.")

if __name__ == "__main__":
    main()
