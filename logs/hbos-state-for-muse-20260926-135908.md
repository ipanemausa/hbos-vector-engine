# 

# HBOS · State Snapshot for Muse · 20260926-135908

# Complete system state as of op=319 close.

# Read-only reference for external surface (Muse).

═══════════════════════════════════════════════════════════════════
0 · SYSTEM SNAPSHOT
═══════════════════════════════════════════════════════════════════

* Git: c1719a0 HBOS op=319: persist 10 FreeLLMAPI providers in hbos\_providers (13 total)
* Working tree: CLEAN
* Qdrant collections: 33

═══════════════════════════════════════════════════════════════════
1 · RULES (hbos\_rules · complete)
═══════════════════════════════════════════════════════════════════

### 31401

{"rule\_id":"R20","texto":"Servicios criticos arrancan automaticos en login","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31402

{"rule\_id":"R21","texto":"Health-check cada 5 minutos","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31403

{"rule\_id":"R22","texto":"Auto-recuperacion sin intervencion humana","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31404

{"rule\_id":"R23","texto":"Tokens diarios se rotan automaticamente","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31405

{"rule\_id":"R24","texto":"Config FreeLLMAPI se sincroniza con Kiro al arrancar","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31406

{"rule\_id":"R25","texto":"Logs con rotacion diaria","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31407

{"rule\_id":"R26","texto":"Cero intervencion humana en arranque","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31408

{"rule\_id":"R27","texto":"TODO va a Qdrant. Si no esta en Qdrant, no existe","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31409

{"rule\_id":"R28","texto":"Anti es brazo ejecutor puro. NO usa LLM interno","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31410

{"rule\_id":"R29","texto":"Los LLMs van via FreeLLMAPI :3001","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31411

{"rule\_id":"R30","texto":"Keys NUNCA en el chat","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"operativa"}

### 31412

{"rule\_id":"R31","texto":"R31: El chat NUNCA recibe valores de secrets. Solo OK/KO, hash SHA256\[:16], y longitud. Anti gestiona .env.local. Rotacion con Windows Hello.","op":314,"fecha":"2026-09-25T20:50:30.593294","categoria":"security"}

### 31413

{"rule\_id":"R32","texto":"Antes de proponer una operacion en el chat, verificar en Qdrant si ya existe. Si existe, NO rediseñar. Solo ejecutar. El chat no reinventa. El chat consulta.","op":314,"fecha":"2026-09-25T21:04:42.177173","categoria":"operativa"}

### R40

Known errors anticipated in hbos\_anticipations before execution.

### R44

Confirmation only when critical: secrets, inviolable rules, deletion, live strategy.

### R36

Every approval recorded with chained hash sha256\[:16] in hbos\_approvals.

### R-PERSIST-RUNTIME

Every runtime config persisted in Qdrant BEFORE executing actions.

### R34

Router arbitrates between live routes by explicit policy.

### R38

Every approval ledger exports to NotebookLM in canonical format.

### R39

Four-Gate Layer Structure: PRE-DEBUG, ANTICIPATE, POST-DEBUG, FRONTIER.

### R41

Frontier debug at phase close: verify state, no leakage, checkpoint written.

### R35

Route admitted to pool only after passing canonical test.

### R43

Auto-edit by default. Every improvement applied automatically with hash.

### R37

Every phase defines checkpoint + bounded retry + resume policy.

### R45

Control exercised from console (PWSH/Antigravity). Chat reasons, console controls.

### R33

Model != provider. Provider is a route. Router selects route.

### R42

FreeLLMAPI is source of truth for arbitration. Qdrant is mirror.

### R-GUARD-REGRESSION

Do NOT break what already works. Compare before/after.

### R-QDRANT-ROOT

Qdrant is single source of truth. If Qdrant fails, everything fails.



═══════════════════════════════════════════════════════════════════
2 · PROTOCOLS (hbos\_protocols · complete)
═══════════════════════════════════════════════════════════════════

### 31460

{"protocol\_id":"P1","nombre":"AUTOSTART","descripcion":"Arranca FreeLLMAPI, Kiro Gateway, Qdrant al iniciar sesion Windows","op":314,"fecha":"2026-09-25T21:04:42.177173","estado":"definido"}

### 31461

{"protocol\_id":"P2","nombre":"HEALTH-CHECK","descripcion":"Verifica cada 5 min que los servicios responden","op":314,"fecha":"2026-09-25T21:04:42.177173","estado":"definido"}

### 31462

{"protocol\_id":"P3","nombre":"AUTORECOVER","descripcion":"Si algo cae, lo levanta solo","op":314,"fecha":"2026-09-25T21:04:42.177173","estado":"definido"}

### 31463

{"protocol\_id":"P4","nombre":"KEY-ROTATE","descripcion":"Rota tokens de Kiro cuando caducan (24h)","op":314,"fecha":"2026-09-25T21:04:42.177173","estado":"definido"}

### 31464

{"protocol\_id":"P5","nombre":"PROMPT-EXEC","descripcion":"Envia prompt factorizado a FreeLLMAPI con auto:smartest","op":314,"fecha":"2026-09-25T21:04:42.177173","estado":"definido"}

### 31465

{"protocol\_id":"P6","nombre":"PERSIST","descripcion":"Persiste estado, decisiones y contexto en Qdrant","op":314,"fecha":"2026-09-25T21:04:42.177173","estado":"definido"}

### 31466

{"protocol\_id":"P7","nombre":"LOAD-CONTEXT","descripcion":"Lee Qdrant y genera encabezado vivo para chat nuevo","op":314,"fecha":"2026-09-25T21:04:42.177173","estado":"definido"}

### P9

KNOWLEDGE-INGEST: ingest sources (video, docs) into Qdrant.

### P11

MUSE-BRIDGE: Muse external surface connection to HBOS.

### P12

APPROVAL-LEDGER: hash chain + NotebookLM export.

### P8

MODEL-ROUTING: arbitrate between routes to same model.

### P10

VIDEO-PIPELINE: video production pipeline (script, assets, render).

### P13

FOUR-GATE-LAYER: PRE-DEBUG, ANTICIPATE, POST-DEBUG, FRONTIER per layer.



═══════════════════════════════════════════════════════════════════
3 · PROVIDERS (hbos\_providers · 13 total)
═══════════════════════════════════════════════════════════════════

* **huggingface** · HuggingFace Router · status: rate\_limited · type: freellmapi-provider
* **kilo** · Kilo Gateway · status: healthy · type: freellmapi-provider
* **llm7** · LLM7 · status: healthy · type: freellmapi-provider
* **qdrant** · qdrant-cloud · status: up · type: provider
* **kiro** · kiro · status: healthy · type: freellmapi-provider
* **kiro** · kiro-gateway · status: down · type: provider
* **google** · Google AI Studio · status: healthy · type: freellmapi-provider
* **ovh** · OVH AI Endpoints · status: healthy · type: freellmapi-provider
* **groq** · Groq · status: healthy · type: freellmapi-provider
* **github** · GitHub Models · status: healthy · type: freellmapi-provider
* **router** · freellmapi · status: up · 268 models · type: provider
* **ollama** · Ollama Cloud · status: healthy · type: freellmapi-provider
* **openrouter** · OpenRouter · status: healthy · type: freellmapi-provider

═══════════════════════════════════════════════════════════════════
4 · ANTICIPATIONS (hbos\_anticipations · 9)
═══════════════════════════════════════════════════════════════════

* Layer 0.5: freellmapi call without Authorization → always load config/freellmapi-key.txt
* Layer 1.1: qdrant unreachable → halt immediately (root rule)
* Layer 0.6: kiro call without Authorization → always send Bearer hbos-kiro-local-key-2026
* Layer 0.6: kiro gateway down (connection refused) → soft-fail, arbitrage via other providers, do not halt
* Layer 2.1: duplicate rules in Qdrant → check hbos\_rules first (R32)
* Layer 0.6: kiro key expires daily → auto-refresh task must run OR register as custom provider once
* Layer 3.1: gemini 3.8 not available (geo block) → use gemini-3.7-flash or gpt-oss-120b
* Layer 0.7: invariant source unclear → read expected from config/op315-invariant.txt, do not hardcode
* Layer 5.1: backup disk full → verify 500MB free before compress

═══════════════════════════════════════════════════════════════════
5 · CHAINS (hbos\_chains · 6)
═══════════════════════════════════════════════════════════════════

* **auto:default**: Default balanced routing
* **auto:vision**: Vision tasks
* **auto:long-context**: Long context tasks
* **auto:code**: Code generation
* **auto:reasoning**: Reasoning-heavy tasks
* **auto:video**: Video production pipeline

═══════════════════════════════════════════════════════════════════
6 · INVENTORY (hbos\_inventory · 8 mascotas + video)
═══════════════════════════════════════════════════════════════════

* {"tipo":"mascota","op":314,"fecha":"2026-09-25T21:04:42.177173","nombre":"Diamantino","gema":"diamante","genero":"M"}
* {"tipo":"mascota","op":314,"fecha":"2026-09-25T21:04:42.177173","nombre":"Rubín","gema":"rubi","genero":"M"}
* {"tipo":"mascota","op":314,"fecha":"2026-09-25T21:04:42.177173","nombre":"Zafir","gema":"zafiro","genero":"M"}
* {"tipo":"mascota","op":314,"fecha":"2026-09-25T21:04:42.177173","nombre":"Topaz","gema":"topacio","genero":"M"}
* {"tipo":"mascota","op":314,"fecha":"2026-09-25T21:04:42.177173","nombre":"Emerald","gema":"esmeralda","genero":"F"}
* {"tipo":"mascota","op":314,"fecha":"2026-09-25T21:04:42.177173","nombre":"Amatista","gema":"amatista","genero":"F"}
* {"tipo":"mascota","op":314,"fecha":"2026-09-25T21:04:42.177173","nombre":"Opalina","gema":"opalo","genero":"F"}
* {"tipo":"video","op":314,"fecha":"2026-09-25T21:04:42.177173","nombre":"video-6-mascotas-demis-hassabis","estado":"storyboard borrador","duracion":"4:00"}

═══════════════════════════════════════════════════════════════════
7 · MASCOTAS (diamantino\_assets · 70)
═══════════════════════════════════════════════════════════════════

### Amatista (10 assets)

* gema: Amatista
* estilo: cinematografico 8K GTC keynote
* episodio: Ep02 - Los 7 Chips
* ruta\_drive ejemplo: G:\\My Drive\\Diamantini\\Amatista\\amatista\_frontal\_neutro\_v1.png

### Citrilo (10 assets)

* gema: Citrino
* estilo: cinematografico 8K GTC keynote
* episodio: Ep02 - Los 7 Chips
* ruta\_drive ejemplo: G:\\My Drive\\Diamantini\\Citrilo\\citrilo\_frontal\_neutro\_v1.png

### Diamantino (10 assets)

* gema: Diamante
* estilo: cinematografico 8K GTC keynote
* episodio: Ep02 - Los 7 Chips
* ruta\_drive ejemplo: G:\\My Drive\\Diamantini\\Diamantino\\diamantino\_frontal\_neutro\_v1.png

### Esmeralda (10 assets)

* gema: Esmeralda
* estilo: cinematografico 8K GTC keynote
* episodio: Ep02 - Los 7 Chips
* ruta\_drive ejemplo: G:\\My Drive\\Diamantini\\Esmeralda\\esmeralda\_frontal\_neutro\_v1.png

### Grafito (10 assets)

* gema: Grafito
* estilo: cinematografico 8K GTC keynote
* episodio: Ep02 - Los 7 Chips
* ruta\_drive ejemplo: G:\\My Drive\\Diamantini\\Grafito\\grafito\_frontal\_neutro\_v1.png

### Rubin (10 assets)

* gema: Rubí
* estilo: cinematografico 8K GTC keynote
* episodio: Ep02 - Los 7 Chips
* ruta\_drive ejemplo: G:\\My Drive\\Diamantini\\Rubin\\rubin\_frontal\_neutro\_v1.png

### Zafir (10 assets)

* gema: Zafiro
* estilo: cinematografico 8K GTC keynote
* episodio: Ep02 - Los 7 Chips
* ruta\_drive ejemplo: G:\\My Drive\\Diamantini\\Zafir\\zafir\_frontal\_neutro\_v1.png



═══════════════════════════════════════════════════════════════════
8 · MOVIMIENTOS (diamantino\_movimientos · 321)
═══════════════════════════════════════════════════════════════════

Sample of first 30 movements:

* **cabeza\_girar\_izq\_45** · cabeza · girar · izquierda · 45\_grados · 2.5s
* **cabeza\_asentir\_arriba\_30** · cabeza · asentir · arriba · 30\_grados · 2s
* **ojos\_parpadear\_normal** · ojos · parpadear · frente · normal · 1.5s
* **brazos\_saludar\_der** · brazos · saludar · lateral\_der · 45\_grados · 3s
* **piernas\_caminar\_adelante** · piernas · caminar · adelante · paso\_firme · 4.5s
* **cabeza\_girar\_izquierda\_15\_grados** · cabeza · girar · izquierda · 15\_grados · 2.5s
* **cabeza\_girar\_izquierda\_30\_grados** · cabeza · girar · izquierda · 30\_grados · 2.5s
* **cabeza\_girar\_izquierda\_45\_grados** · cabeza · girar · izquierda · 45\_grados · 2.5s
* **cabeza\_girar\_derecha\_15\_grados** · cabeza · girar · derecha · 15\_grados · 2.5s
* **cabeza\_girar\_derecha\_30\_grados** · cabeza · girar · derecha · 30\_grados · 2.5s
* **cabeza\_girar\_derecha\_45\_grados** · cabeza · girar · derecha · 45\_grados · 2.5s
* **cabeza\_girar\_arriba\_15\_grados** · cabeza · girar · arriba · 15\_grados · 2.5s
* **cabeza\_girar\_arriba\_30\_grados** · cabeza · girar · arriba · 30\_grados · 2.5s
* **cabeza\_girar\_arriba\_45\_grados** · cabeza · girar · arriba · 45\_grados · 2.5s
* **cabeza\_girar\_abajo\_15\_grados** · cabeza · girar · abajo · 15\_grados · 2.5s
* **cabeza\_girar\_abajo\_30\_grados** · cabeza · girar · abajo · 30\_grados · 2.5s
* **cabeza\_girar\_abajo\_45\_grados** · cabeza · girar · abajo · 45\_grados · 2.5s
* **cabeza\_inclinar\_izquierda\_15\_grados** · cabeza · inclinar · izquierda · 15\_grados · 2.5s
* **cabeza\_inclinar\_izquierda\_30\_grados** · cabeza · inclinar · izquierda · 30\_grados · 2.5s
* **cabeza\_inclinar\_izquierda\_45\_grados** · cabeza · inclinar · izquierda · 45\_grados · 2.5s
* **cabeza\_inclinar\_derecha\_15\_grados** · cabeza · inclinar · derecha · 15\_grados · 2.5s
* **cabeza\_inclinar\_derecha\_30\_grados** · cabeza · inclinar · derecha · 30\_grados · 2.5s
* **cabeza\_inclinar\_derecha\_45\_grados** · cabeza · inclinar · derecha · 45\_grados · 2.5s
* **cabeza\_inclinar\_arriba\_15\_grados** · cabeza · inclinar · arriba · 15\_grados · 2.5s
* **cabeza\_inclinar\_arriba\_30\_grados** · cabeza · inclinar · arriba · 30\_grados · 2.5s
* **cabeza\_inclinar\_arriba\_45\_grados** · cabeza · inclinar · arriba · 45\_grados · 2.5s
* **cabeza\_inclinar\_abajo\_15\_grados** · cabeza · inclinar · abajo · 15\_grados · 2.5s
* **cabeza\_inclinar\_abajo\_30\_grados** · cabeza · inclinar · abajo · 30\_grados · 2.5s
* **cabeza\_inclinar\_abajo\_45\_grados** · cabeza · inclinar · abajo · 45\_grados · 2.5s
* **cabeza\_ladear\_izquierda\_15\_grados** · cabeza · ladear · izquierda · 15\_grados · 2.5s

(Total: 321 movements. Full list available on request.)

═══════════════════════════════════════════════════════════════════
9 · CANON (hbos\_canon · 85)
═══════════════════════════════════════════════════════════════════

(hbos\_canon preserved in Qdrant. Available on request.)

═══════════════════════════════════════════════════════════════════
10 · DECISIONS (hbos\_decisions · 14)
═══════════════════════════════════════════════════════════════════

* \[]  ·
* \[]  ·
* \[]  ·
* \[]  ·
* \[]  ·
* \[]  ·
* \[]  ·
* \[]  ·
* \[]  ·
* \[]  ·
* \[]  ·
* \[20260926-070542] kiro integration attempt ·
* \[20260926-123850] search mascotas+muse+video ·
* \[20260926-064941] kiro integration verification ·

═══════════════════════════════════════════════════════════════════
END · HBOS STATE SNAPSHOT
═══════════════════════════════════════════════════════════════════

