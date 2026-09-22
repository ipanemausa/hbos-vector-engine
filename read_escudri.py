# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('_ESCUDRI_20260922_185301.md', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

sections = text.split('## ')
for s in sections:
    lines = s.strip().split('\n')
    title = lines[0]
    print(f"\n=======================================================")
    print(f"=== SECTION: {title} ({len(lines)} lines)")
    print(f"=======================================================")
    print('\n'.join(lines[1:30]))
