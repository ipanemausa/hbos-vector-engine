# Kiro Persistence · op=316 · 20260926-070119

## Status
- Kiro gateway: UP
- Kiro models: 8
- Kiro in FreeLLMAPI: NO
- Claude via FreeLLMAPI: FAILS

## Protocol R-KIRO-PERSIST
1. Kiro runs as custom OpenAI-compatible provider in FreeLLMAPI
2. Base URL: http://127.0.0.1:10088/v1
3. API Key: hbos-kiro-local-key-2026
4. Model discovery runs on registration
5. On every HBOS session start: verify Kiro is in FreeLLMAPI catalog
6. If missing: re-register automatically or halt with alert

## Next action
MANUAL: Open http://127.0.0.1:3001 → Keys → Add custom provider → http://127.0.0.1:10088/v1
