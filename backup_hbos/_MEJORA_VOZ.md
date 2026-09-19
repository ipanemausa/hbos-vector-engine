# MEJORA DE VOZ Y ARQUITECTURA VOCAL EN HBOS-DIAMANTINO
**Análisis Comparativo, Parámetros Acústicos y Síntesis Soberana**  
**Documento Canónico de Ingeniería de Audio y Dirección Vocal**  
**operation_id:** 186 | **Gobernanza:** Patrones P-04 v2, P-05, P-18 | **Ecosistema:** HBOS-Diamantino

---

## 1. COMPARATIVA DE MOTORES DE SÍNTESIS VOCAL (TTS)

| Parámetro | ElevenLabs Cloud | CosyVoice2 / FreeLLMAPI | Edge TTS Neural (Local/Cloud) |
| :--- | :--- | :--- | :--- |
| **Calidad Timbre** | 9.8 / 10 (Emocional profunda) | 9.2 / 10 (Excelente articulación) | 9.0 / 10 (Claridad broadcast óptima) |
| **Latencia TTFB** | ~1.5 - 2.5 seg | ~0.8 - 1.5 seg | ~0.3 - 0.7 seg (Ultra-rápido) |
| **Restricción Cuota** | Muy estricta (~10k chars/mes free) | Sin límite en servidor local | Sin límite de caracteres |
| **Costo por 1k Chars**| $0.30 USD | **$0.00 USD** | **$0.00 USD** |
| **Soberanía** | Externa (API propietaria) | Soberana en Sandbox | Invocable sin autenticación |

---

## 2. PARÁMETROS ACÚSTICOS DE LA VOZ DIAMANTINO

Para proyectar la personalidad de un **Anchor de Civilización Tipo 5**, la voz de Diamantino se somete a los siguientes estándares de calibración:

1. **Timbre y Tono:**
   - Voz masculina barítono media-baja.
   - Resonancia de pecho con agudos cristalinos (rango 120 Hz - 4,500 Hz).
2. **Velocidad y Cadencia:**
   - **Tasa de locución:** 135 a 145 palabras por minuto.
   - **Pausas respiratorias:** 0.35s a 0.45s entre oraciones; 0.20s en comas técnicas.
3. **Modulación Emocional:**
   - **Tono Serio y Confiable:** En enunciación de datos y premios Nobel (Bloques 0, 1, 8).
   - **Tono Analítico y Descriptivo:** En desglose molecular y biomédico (Bloques 2, 3, 4, 5).
   - **Tono Humanista y Cercano:** En impacto sobre enfermedades huérfanas y salud global (Bloques 6, 7, 9).

---

## 3. PROCESAMIENTO POST-SÍNTESIS EBU R128 (PATRÓN P-04 v2)

Cada bloque de audio crudo se masteriza mediante la siguiente cadena DSP:

```bash
ffmpeg -i voz_raw.mp3 \
  -af "loudnorm=I=-14.0:TP=-1.0:LRA=11.0:measured_I=-14:measured_TP=-1.0" \
  -ar 48000 -c:a pcm_s24le voz_master.wav
```

- **Loudness Integrado:** `-14.0 LUFS` ($\pm 0.5$ LUFS de tolerancia).
- **True Peak Máximo:** `-1.0 dBTP` (garantiza cero distorsión en transcodificación MP3/AAC de plataformas como YouTube, Spotify o TikTok).
- **Frecuencia de Muestreo:** `48,000 Hz` a `24 bits` (estándar broadcast de cine y televisión).
