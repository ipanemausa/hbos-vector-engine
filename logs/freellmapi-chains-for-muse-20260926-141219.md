# HBOS · FreeLLMAPI Chains · Smart Fallback Documentation
# For Muse · 20260926-141219
# Source: FreeLLMAPI documentation + live API

═══════════════════════════════════════════════════════════════════
1 · WHAT ARE FALLBACK CHAINS?
═══════════════════════════════════════════════════════════════════

FreeLLMAPI treats the catalog of free tiers as a POOLED FALLBACK CHAIN.
The router scores every model with live measurements and picks the best
one that is under all its rate limits. When a provider returns 429/5xx
or times out, the router:

  1. Puts that key on short cooldown
  2. Retries on the NEXT model in the chain
  3. Up to 20 attempts, bounded by wall-clock retry budget

Context handoff: when the chain switches model mid-conversation, a compact
system message tells the new model it is taking over, so it doesn't restart.

═══════════════════════════════════════════════════════════════════
2 · ROUTING STRATEGIES (6 options)
═══════════════════════════════════════════════════════════════════

| Strategy    | What it does |
|-------------|--------------|
| priority    | Your manual order (drag to reorder) |
| balanced    | Weighted mix (default: reliability 50%, speed 25%, intelligence 25%) |
| smartest    | Prefers highest capability |
| fastest     | Prefers lowest latency |
| reliable    | Prefers lowest error rate |
| custom      | Your own weight mix |

Scoring uses a Thompson-sampling bandit with live per-model measurements:
speed, capability, rate-limit headroom, recent errors.

═══════════════════════════════════════════════════════════════════
3 · NAMED PROFILES (auto:<name>)
═══════════════════════════════════════════════════════════════════

You can save NAMED FALLBACK CHAIN PROFILES (e.g. a coding chain, a
vision chain, a long-context chain) and switch the active one from the
dashboard. Call by name with auto:<profile>:

  model: "auto:video"         → video production pipeline
  model: "auto:reasoning"     → reasoning-heavy tasks
  model: "auto:long-context"  → long context
  model: "auto:vision"        → vision tasks
  model: "auto:code"          → code generation
  model: "auto"               → default chain (balanced)

═══════════════════════════════════════════════════════════════════
4 · DIAGNOSTIC HEADERS
═══════════════════════════════════════════════════════════════════

Every response carries:

  X-Routed-Via:        <platform>/<model>   (who served the request)
  X-Fallback-Attempts: N                    (how many failed before success)

If fallover occurred, also:

  X-Fallback-Trail:    groq/llama key1=rate_limited; google/gemini key2=timeout
  X-Fallback-Detail:   timings + error text per hop (OFF by default)

Enable detail with FALLBACK_DETAIL_HEADER=1 or expose_fallback_detail_header
setting. Max 10 hops listed, then "; +N more".

═══════════════════════════════════════════════════════════════════
5 · EMBEDDINGS ROUTING (different rules)
═══════════════════════════════════════════════════════════════════

Embeddings NEVER cross models. Vectors from different models live in
incompatible spaces. So embeddings route by FAMILY (one model identity +
dimension), and failover only walks providers serving that same family.

Available families:
- gemini-embedding-001 (default, 3072 dims)
- text-embedding-3-large (3072 dims, GitHub Models)
- text-embedding-3-small (1536 dims, GitHub Models)
- bge-m3 (1024 dims, Cloudflare → Hugging Face)
- qwen3-embedding-0.6b (1024 dims, Cloudflare)
- nv-embedqa-e5-v5 (1024 dims, NVIDIA)
- llama-nemotron-embed-1b-v2 (2048 dims, NVIDIA)
- embeddinggemma-300m (768 dims, Cloudflare)

═══════════════════════════════════════════════════════════════════
6 · CURRENT CHAINS IN HBOS (hbos_chains)
═══════════════════════════════════════════════════════════════════

- auto:default        → Default balanced routing
- auto:video          → Video production pipeline
- auto:reasoning      → Reasoning-heavy tasks
- auto:long-context   → Long context tasks
- auto:vision         → Vision tasks
- auto:code           → Code generation

═══════════════════════════════════════════════════════════════════
7 · HOW TO CONFIGURE (dashboard)
═══════════════════════════════════════════════════════════════════

1. Open http://127.0.0.1:3001
2. Go to Models page
3. Fallback Chains section (bottom)
4. Drag to reorder providers by priority
5. Or create named profiles under the chain list
6. Select routing strategy at top (Balanced, Smartest, Fastest, etc.)

═══════════════════════════════════════════════════════════════════
8 · WHAT THIS MEANS FOR MUSE
═══════════════════════════════════════════════════════════════════

When Muse needs to call an LLM for reasoning, video, or long-context:

1. Use the appropriate chain: auto:reasoning, auto:video, auto:long-context
2. FreeLLMAPI picks the best available route automatically
3. If one provider fails, it falls to the next
4. Muse sees which route served via X-Routed-Via
5. Muse does NOT need to know about individual providers

Muse asks for a capability, the router finds the route.

═══════════════════════════════════════════════════════════════════
END · FreeLLMAPI Chains for Muse
═══════════════════════════════════════════════════════════════════
