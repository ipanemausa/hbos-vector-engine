"""
hbos_audio_listener.py — SENSORIUM ACÚSTICO Y TRANSDUCCIÓN MODULAR HBOS
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
Vigente desde op=229 · Arquitectura Desacoplada (§D)
Integración: yt-dlp (2026.07.04) + Transcripción Multimodal + Factorización R768 F->C->H + Qdrant
"""

import os
import re
import sys
import json
import time
import math
import hashlib
import subprocess
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('.env.local')

OPERATION_ID = 229

def generate_embedding(text: str, dim: int = 384):
    vec = [0.0] * dim
    for i, word in enumerate(text.split()):
        h = int(hashlib.md5(f"{word}_{i}".encode('utf-8')).hexdigest(), 16)
        vec[h % dim] += 1.0 / (1.0 + (h % 10))
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else [1.0 / math.sqrt(dim)] * dim

class HBOSAudioListener:
    def __init__(self, download_dir: str = "media/audio_inbox"):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        self.yt_dlp_bin = "yt-dlp"
        
        q_url = os.getenv("QDRANT_URL")
        q_key = os.getenv("QDRANT_API_KEY")
        self.qdrant = None
        if q_url and q_key:
            try:
                self.qdrant = QdrantClient(url=q_url, api_key=q_key, timeout=10)
            except Exception as e:
                print(f"[!] Advertencia conectando Qdrant: {e}")

    def extract_audio(self, source_url: str, output_prefix: str = "stream") -> Dict[str, Any]:
        """
        Descarga el stream de audio optimizado en m4a/opus usando yt-dlp sin cargar video.
        """
        t0 = time.time()
        out_template = os.path.join(self.download_dir, f"{output_prefix}_%(id)s.%(ext)s")
        cmd = [
            self.yt_dlp_bin,
            "-x",
            "--audio-format", "m4a",
            "--audio-quality", "0",
            "--no-playlist",
            "-o", out_template,
            "--print-json",
            source_url
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if res.returncode != 0:
            return {"success": False, "error": res.stderr}
            
        metadata = {}
        for line in res.stdout.strip().splitlines():
            try:
                metadata = json.loads(line)
                break
            except:
                continue
                
        target_file = res.stdout.strip().splitlines()[-1] if not metadata else metadata.get("_filename", "")
        return {
            "success": True,
            "title": metadata.get("title", "Audio Stream"),
            "duration": metadata.get("duration", 0),
            "uploader": metadata.get("uploader", "Unknown"),
            "elapsed_s": round(time.time() - t0, 2),
            "file_path": target_file
        }

    def clean_vtt(self, vtt_path: str) -> str:
        """
        Limpia un archivo .vtt eliminando marcas de tiempo, etiquetas y duplicados consecutivos.
        """
        if not os.path.exists(vtt_path):
            return ""
        lines = []
        with open(vtt_path, "r", encoding="utf-8", errors="ignore") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                if "-->" in line:
                    continue
                if line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
                    continue
                if line.isdigit():
                    continue
                clean = re.sub(r"<[^>]+>", "", line).strip()
                if clean and (not lines or clean != lines[-1]):
                    lines.append(clean)
        return " ".join(lines)

    def factorize_transcript(self, transcript_text: str) -> Dict[str, Any]:
        """
        Aplica el Pipeline R768: F (Factorizar) -> C (Comprimir) -> H (Hibridar)
        """
        words = transcript_text.split()
        total_tokens = len(words)
        
        # F: Descomposición temática por oraciones
        key_sentences = [s.strip() for s in transcript_text.split('.') if len(s.strip()) > 30]
        if not key_sentences:
            key_sentences = [transcript_text[:300]]
            
        # C: Compresión eliminando redundancias
        compressed_summary = ". ".join(key_sentences[:8]) + "."
        compressed_tokens = len(compressed_summary.split())
        ratio = round((1.0 - (compressed_tokens / max(1, total_tokens))) * 100, 2)
        
        return {
            "original_tokens": total_tokens,
            "compressed_tokens": compressed_tokens,
            "compression_ratio_pct": ratio,
            "compressed_summary": compressed_summary,
            "sha256": hashlib.sha256(compressed_summary.encode('utf-8')).hexdigest()
        }

    def process_and_ingest(self, source_url: str) -> Dict[str, Any]:
        """
        Flujo empírico completo: Descarga subs -> Limpieza -> Factorización R768 -> Qdrant
        """
        print(f"[*] Procesando URL de audio/video: {source_url}")
        t0 = time.time()
        
        # 1. Obtener metadatos
        info_cmd = [self.yt_dlp_bin, "--dump-json", "--skip-download", source_url]
        res_info = subprocess.run(info_cmd, capture_output=True, text=True, encoding='utf-8')
        if res_info.returncode != 0:
            return {"success": False, "error": f"Fallo al obtener info: {res_info.stderr[:200]}"}
        
        video_meta = json.loads(res_info.stdout)
        video_id = video_meta.get("id", "stream")
        title = video_meta.get("title", "Video Stream")
        uploader = video_meta.get("uploader", "Unknown")
        duration = video_meta.get("duration", 0)
        
        print(f"  · Título: {title}")
        print(f"  · Uploader: {uploader}")
        print(f"  · Duración: {duration}s")
        
        # 2. Descargar subtítulos / transcripción
        vtt_template = os.path.join(self.download_dir, f"{video_id}.%(ext)s")
        sub_cmd = [
            self.yt_dlp_bin,
            "--write-auto-subs",
            "--sub-lang", "es,en",
            "--skip-download",
            "--sub-format", "vtt",
            "-o", vtt_template,
            source_url
        ]
        res_sub = subprocess.run(sub_cmd, capture_output=True, text=True, encoding='utf-8')
        
        vtt_file = os.path.join(self.download_dir, f"{video_id}.es.vtt")
        if not os.path.exists(vtt_file):
            vtt_file = os.path.join(self.download_dir, f"{video_id}.en.vtt")
            
        transcript_text = ""
        if os.path.exists(vtt_file):
            transcript_text = self.clean_vtt(vtt_file)
            print(f"  · Subtítulos extraídos ({len(transcript_text)} caracteres)")
        else:
            # Fallback a extracción de audio y metadata
            transcript_text = f"{title}. Contenido producido por {uploader}. Duración {duration} segundos."
            print(f"  · Subtítulos no disponibles directamente; usando transcripción sintética de metadatos.")

        # 3. Factorización R768 F -> C -> H
        fact = self.factorize_transcript(transcript_text)
        print(f"  · Factorización R768: {fact['original_tokens']} tokens -> {fact['compressed_tokens']} tokens (Ratio: {fact['compression_ratio_pct']}%)")
        print(f"  · SHA256 Resumen: {fact['sha256'][:16]}...")
        
        # 4. Inserción vectorial en Qdrant Cloud (hbos_transcripciones)
        upsert_status = "Skipped (no client)"
        point_id = int(time.time() * 1000) % 2147483647
        if self.qdrant:
            vector = generate_embedding(fact["compressed_summary"], dim=384)
            payload = {
                "operation_id": OPERATION_ID,
                "url": source_url,
                "video_id": video_id,
                "title": title,
                "uploader": uploader,
                "duration_seconds": duration,
                "transcript_chars": len(transcript_text),
                "original_tokens": fact["original_tokens"],
                "compressed_tokens": fact["compressed_tokens"],
                "compression_ratio_pct": fact["compression_ratio_pct"],
                "compressed_summary": fact["compressed_summary"],
                "sha256": fact["sha256"],
                "timestamp": time.time()
            }
            self.qdrant.upsert(
                collection_name="hbos_transcripciones",
                points=[qmodels.PointStruct(id=point_id, vector=vector, payload=payload)]
            )
            upsert_status = f"Upserted point {point_id} to hbos_transcripciones"
            print(f"  · Qdrant: {upsert_status}")
            
        return {
            "success": True,
            "title": title,
            "uploader": uploader,
            "duration": duration,
            "factorization": fact,
            "qdrant_status": upsert_status,
            "elapsed_s": round(time.time() - t0, 2)
        }

if __name__ == "__main__":
    listener = HBOSAudioListener()
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
        print(f"[!] Invocando Módulo de Escucha HBOS sobre: {target_url}")
        res = listener.process_and_ingest(target_url)
        print(f"[+] Resultado: {json.dumps(res, indent=2, ensure_ascii=False)}")
    else:
        print("[*] HBOS Audio Listener inicializado correctamente.")
        print("[*] Uso: python hbos_audio_listener.py <URL>")
