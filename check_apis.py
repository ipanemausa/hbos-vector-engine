import os
from dotenv import load_dotenv
import requests

load_dotenv('.env.local')
print('OPENAI:', bool(os.getenv('OPENAI_API_KEY')))
print('GEMINI:', bool(os.getenv('GEMINI_API_KEY')))
print('DASHSCOPE:', bool(os.getenv('DASHSCOPE_API_KEY')))
print('GROQ:', bool(os.getenv('GROQ_API_KEY')))

# Test OpenAI if available
openai_key = os.getenv('OPENAI_API_KEY')
if openai_key:
    r = requests.get('https://api.openai.com/v1/models', headers={'Authorization': f'Bearer {openai_key}'})
    print('OpenAI Status:', r.status_code)

# Test Gemini if available
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    r = requests.get(f'https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}')
    print('Gemini Status:', r.status_code)
