import re

js_path = r"G:\My Drive\HBOS-Diamantino\_SANDBOX\FreeLLMAPI\app\resources\client-dist\assets\index-B8n16Tcf.js"
with open(js_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Buscar 'trpc' o endpoints
print("Buscando trpc o endpoints...")
for kw in ["trpc", "keys.add", "keys.create", "api/keys", "addKey", "saveKey"]:
    matches = [m.start() for m in re.finditer(kw, text, re.IGNORECASE)]
    print(f"Palabra '{kw}': {len(matches)} coincidencias")
    for idx in matches[:3]:
        print("   ->", text[max(0, idx-40):min(len(text), idx+60)].replace("\n", " "))
