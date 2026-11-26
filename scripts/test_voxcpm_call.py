import os
import time
from gradio_client import Client, handle_file

print("Connecting to openbmb/VoxCPM-Demo...")
client = Client("openbmb/VoxCPM-Demo")

ref_path = os.path.abspath("ref-video08-15s-16k.wav")
prompt_guide = "y lo publica todo sola, en todas tus redes sociales, sin programar, empezando gratis..."

test_text = "Soy Guillermo Alonso Hoyos. Les hablo desde mi mesa de trabajo en Rionegro, Antioquia."

print(f"Calling predict with test text: '{test_text}'")
t0 = time.time()
result = client.predict(
    text_input=test_text,
    control_instruction="",
    reference_wav_path_input=handle_file(ref_path),
    use_prompt_text=True,
    prompt_text_input=prompt_guide,
    cfg_value_input=2.0,
    do_normalize=False,
    denoise=False,
    api_name="/generate"
)
t1 = time.time()
print(f"Done in {t1-t0:.2f}s! Result: {result}")
