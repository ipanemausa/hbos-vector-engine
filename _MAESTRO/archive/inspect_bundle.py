import re

js_path = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app\resources\client-dist\assets\index-B8n16Tcf.js"
with open(js_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

fetch_matches = [m.start() for m in re.finditer(r"fetch\(", text)]
print(f"\nTotal llamadas a 'fetch(': {len(fetch_matches)}")
for idx in fetch_matches[:10]:
    snippet = text[idx:min(len(text), idx+80)]
    print(f"  fetch: {snippet.strip()}")

# Buscar referencias a compression
compression_matches = [m.start() for m in re.finditer(r"compression", text, re.IGNORECASE)]
print(f"\nReferencias a 'compression': {len(compression_matches)}")
for idx in compression_matches[:5]:
    snippet = text[max(0, idx-50):min(len(text), idx+100)]
    print(f"  snippet: {snippet.strip()}")

# Buscar referencias a TTS o audio
tts_matches = [m.start() for m in re.finditer(r"tts", text, re.IGNORECASE)]
print(f"\nReferencias a 'tts': {len(tts_matches)}")
for idx in tts_matches[:5]:
    snippet = text[max(0, idx-50):min(len(text), idx+100)]
    print(f"  snippet: {snippet.strip()}")
