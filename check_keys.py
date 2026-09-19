import os
import requests

for env_f in ['.env.local', '.env.vercel']:
    if not os.path.exists(env_f): continue
    with open(env_f) as f:
        for line in f:
            if 'ELEVENLABS' in line:
                k = line.strip().split('=', 1)[1].strip('\"\'')
                print(f'{env_f} key: {k[:6]}... len={len(k)}')
                res = requests.get('https://api.elevenlabs.io/v1/user', headers={'xi-api-key': k})
                print(f'Status: {res.status_code}')
