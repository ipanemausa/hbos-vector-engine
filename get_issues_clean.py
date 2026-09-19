import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

r = requests.get('https://api.github.com/repos/tashfeenahmed/freellmapi/issues?state=open&per_page=15', headers={'User-Agent': 'Mozilla/5.0'}).json()
issues = [i for i in r if 'pull_request' not in i][:5]
for i in issues:
    num = i.get('number')
    title = i.get('title')
    labels = [l.get('name') for l in i.get('labels', [])]
    print(f"#{num}: {title} | Labels: {labels}")
