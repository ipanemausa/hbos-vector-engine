import os
import sys
import time
import base64
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

api_key = os.getenv('DASHSCOPE_API_KEY')
img_path = r"Ep04\02_Storyboard\images_wan21\plano_00_nota_referencia.png"

with open(img_path, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')
data_url = f"data:image/png;base64,{b64}"

url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable"
}
payload = {
    "model": "wan2.1-i2v-turbo",
    "input": {
        "img_url": data_url,
        "prompt": "Slow elegant camera push-in on editorial disclaimer title card with subtle glowing quantum particles and prestigious crystal refractions, cinematic 8K"
    }
}

print("[*] Enviando Plano 0 a DashScope Cloud (Wan 2.1 I2V)...")
res = requests.post(url, headers=headers, json=payload, timeout=30)
print(f"Status: {res.status_code}")
print(f"Response: {res.text}")
