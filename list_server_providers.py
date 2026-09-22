# -*- coding: utf-8 -*-
import os
import re

appExtracted = r"C:\Users\ipane\AppData\Local\Programs\FreeLLMAPI\resources\app_extracted\build"
server_file = os.path.join(appExtracted, "server.mjs")

with open(server_file, 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# Find all register(new ...Provider(...))
matches = re.findall(r'register\(new\s+([A-Za-z0-9_]+)\s*\(([\s\S]*?)\)\);', code)
print(f"Total provider registrations found: {len(matches)}")

for cls_name, args in matches:
    # extract platform and name and baseUrl and validateUrl
    platform = re.search(r'platform:\s*["\']([^"\']+)["\']', args)
    p_name = platform.group(1) if platform else "unknown"
    name = re.search(r'name:\s*["\']([^"\']+)["\']', args)
    disp_name = name.group(1) if name else ""
    base_url = re.search(r'baseUrl:\s*["\']([^"\']+)["\']', args)
    url = base_url.group(1) if base_url else ""
    validate_url = re.search(r'validateUrl:\s*["\']([^"\']+)["\']', args)
    val_url = validate_url.group(1) if validate_url else ""
    print(f"Provider: {p_name:15} | Class: {cls_name:22} | Name: {disp_name:20} | BaseUrl: {url}")
