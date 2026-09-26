# HBOS op=316 · Kiro Integration · 20260926-070542

## State Before
- FreeLLMAPI models: 268
- Claude in FreeLLMAPI: 9
- Kiro models: 8

## Kiro models inventory
- claude-opus-4-5
- claude-opus-4-5-20251101
- claude-haiku-4-5
- claude-sonnet-4-5
- claude-sonnet-4-5-20250929
- claude-sonnet-4
- claude-sonnet-4-20250514
- claude-3-7-sonnet-20250219


## State After
- FreeLLMAPI models: 268
- Delta: 0
- Claude via FreeLLMAPI: FAILS

## Registration
- API attempt: NOT AVAILABLE
- Manual UI required: YES

## If manual required
1. Open http://127.0.0.1:3001
2. Keys tab → Add custom provider
3. Name: kiro-gateway
4. Base URL: http://127.0.0.1:10088/v1
5. API Key: hbos-kiro-local-key-2026
6. Type: openai-compatible
7. Save and wait for discovery

## Protocol R-KIRO-PERSIST
- Kiro runs as custom OpenAI-compatible provider
- Verified on every session start
- If missing: re-register or halt
