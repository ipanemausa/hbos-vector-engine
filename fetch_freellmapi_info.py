import requests
import json

headers = {'User-Agent': 'Mozilla/5.0'}

# 1. Top 5 open issues
r_issues = requests.get('https://api.github.com/repos/tashfeenahmed/freellmapi/issues?state=open&per_page=5', headers=headers).json()
print('=== TOP 5 ISSUES ===')
for i in r_issues:
    if 'pull_request' not in i:
        print(f"#{i.get('number')}: {i.get('title')}")

# 2. Contributors
r_contrib = requests.get('https://api.github.com/repos/tashfeenahmed/freellmapi/contributors?per_page=100', headers=headers)
contribs = r_contrib.json() if r_contrib.status_code == 200 else []
print(f"Contributors count (page 1): {len(contribs)}")

# 3. Readme
r_readme = requests.get('https://raw.githubusercontent.com/tashfeenahmed/freellmapi/main/README.md', headers=headers)
with open('scratch_freellmapi_readme.md', 'w', encoding='utf-8') as f:
    f.write(r_readme.text)
print('README saved, length:', len(r_readme.text))
