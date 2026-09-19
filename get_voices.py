import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')
k = os.getenv('ELEVENLABS_API_KEY')
r = requests.get('https://api.elevenlabs.io/v1/voices', headers={'xi-api-key': k})
print('Voices Status:', r.status_code)
if r.status_code == 200:
    voices = r.json().get('voices', [])
    print(f'Total voces encontradas: {len(voices)}')
    targets = ['adam', 'brian', 'daniel', 'bella', 'liam', 'callum', 'sarah']
    mapping = {}
    for v in voices:
        vname = v['name']
        vid = v['voice_id']
        for t in targets:
            if t in vname.lower():
                mapping[t] = vid
                print(f"Target {t.upper()} -> Name: '{vname}', ID: '{vid}'")
    print("\nMapping completo:")
    print(mapping)
else:
    print('Error:', r.text[:200])
