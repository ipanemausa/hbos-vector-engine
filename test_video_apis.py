import os, requests, base64

with open('public/media/ep02/rubin_v4_cabeza_bruto.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

env_vercel = {}
with open('.env.vercel') as f:
    for l in f:
        if '=' in l:
            p = l.strip().split('=', 1)
            env_vercel[p[0]] = p[1].strip('"\'')

key = env_vercel.get('DASHSCOPE_API_KEY')

data_url = f'data:image/png;base64,{b64}'
res = requests.post(
    'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis',
    headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'X-DashScope-Async': 'enable'},
    json={'model': 'wan2.1-i2v-turbo', 'input': {'img_url': data_url, 'prompt': 'Vera Rubin GPU compute'}}
)
print('Base64 test status:', res.status_code, res.json())
