import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

out_dir = r"Ep04\02_Storyboard\images_wan21"
os.makedirs(out_dir, exist_ok=True)

bg_path = r"Ep04\02_Storyboard\backgrounds\bg_ep04_biocuantico_1080p.png"
bg_master = Image.open(bg_path).convert("RGBA")

# 1. Plano 0: Nota de Referencia P-17
p0_img = bg_master.copy()
overlay = Image.new("RGBA", p0_img.size, (5, 12, 30, 235))
p0_img = Image.alpha_composite(p0_img, overlay)
draw0 = ImageDraw.Draw(p0_img)
w, h = p0_img.size

# Frame cristalino y dorado
draw0.rectangle([(50, 50), (w - 50, h - 50)], outline=(212, 175, 55, 240), width=3)
draw0.rectangle([(65, 65), (w - 65, h - 65)], outline=(0, 200, 255, 140), width=1)

# Textos
try:
    font_title = ImageFont.truetype("arial.ttf", 44)
    font_sub = ImageFont.truetype("arial.ttf", 32)
    font_body = ImageFont.truetype("arial.ttf", 26)
    font_tag = ImageFont.truetype("arial.ttf", 22)
except Exception:
    font_title = font_sub = font_body = font_tag = ImageFont.load_default()

draw0.text((w/2, 120), "HBOS-DIAMANTINO · AGENCIA DE DIVULGACIÓN CIENTÍFICA", fill=(0, 220, 255), font=font_tag, anchor="mm")
draw0.text((w/2, 180), "NOTA DE REFERENCIA CANÓNICA (PATRÓN P-17)", fill=(255, 215, 0), font=font_title, anchor="mm")

cuerpo_p0 = [
    "Los descubrimientos científicos presentados en esta serie audiovisual (AlphaFold, AlphaMissense, AlphaProteo)",
    "son propiedad intelectual de Google DeepMind y de los galardonados con el Premio Nobel de Química 2024:",
    "Demis Hassabis, John Jumper y David Baker.",
    "",
    "HBOS-Diamantino actúa exclusivamente como HOST y agencia de divulgación científica soberana.",
    "Nuestros anfitriones y avatares cristalinos EXPLICAN y DIFUNDEN la ciencia; no se apropian de ella.",
    "",
    "El sello visual, los personajes minerales, la arquitectura agéntica y el sistema de producción",
    "son propiedad y autoría de Guillermo Hoyos / HBOS-Diamantino."
]

y_text = 280
for line in cuerpo_p0:
    draw0.text((w/2, y_text), line, fill=(240, 245, 255), font=font_body, anchor="mm")
    y_text += 45

draw0.text((w/2, 980), "FUENTES OFICIALES: NobelPrize.org · Google DeepMind · Nature · Science · Isomorphic Labs", fill=(120, 180, 230), font=font_tag, anchor="mm")

p0_final = os.path.join(out_dir, "plano_00_nota_referencia.png")
p0_img.convert("RGB").save(p0_final)
print(f"[OK] Plano 0 guardado: {p0_final}")

# Mapping de hosts para planos 1 al 9
host_files = {
    1: (r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard\diamantino_v1_keynote.png", "plano_01_diamantino_intro.png"),
    2: (r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard\rubin_v3_articulado.png", "plano_02_rubin.png"),
    3: (r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard\zafir_v1_articulado.png", "plano_03_zafir.png"),
    4: (r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard\esmeralda_v1_articulado.png", "plano_04_esmeralda.png"),
    5: (r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard\citrilo_v1_articulado.png", "plano_05_citrilo.png"),
    6: (r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard\grafito_v1_articulado.png", "plano_06_grafito.png"),
    7: (r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard\amatista_v1_articulado.png", "plano_07_amatista.png"),
    8: (r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard\diamantino_v1_keynote.png", "plano_08_diamantino_recap.png"),
    9: (r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\02_Storyboard\escena_ensemble_gtc_keynote.png", "plano_09_ensemble_cierre.png")
}

for plano_id, (src_host, out_name) in host_files.items():
    comp = bg_master.copy()
    if os.path.exists(src_host):
        h_img = Image.open(src_host).convert("RGBA")
        # Resize to fit nicely on 1920x1080 stage
        h_scaled = h_img.resize((1920, 1080), Image.Resampling.LANCZOS)
        comp = Image.alpha_composite(comp, h_scaled)
    else:
        print(f"[!] Warning: {src_host} no encontrado")
        
    out_p = os.path.join(out_dir, out_name)
    comp.convert("RGB").save(out_p)
    print(f"[OK] Plano {plano_id} guardado: {out_p}")

print("\n[ÉXITO] 10 Planos de Storyboard compuestos listos para Wan 2.1 I2V.")
