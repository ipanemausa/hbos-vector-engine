# -*- coding: utf-8 -*-
with open(r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build\main.mjs", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

print("Length of main.mjs:", len(code))
# Buscar app.whenReady o app.on('window-all-closed')
for term in ["window-all-closed", "whenReady", "app.quit", "ready-to-show"]:
    idx = 0
    while True:
        idx = code.find(term, idx)
        if idx == -1:
            break
        print(f"--- MATCH {term} AT {idx} ---")
        print(code[idx-50:idx+250])
        idx += len(term)
