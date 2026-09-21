# -*- coding: utf-8 -*-
"""
hbos_youtube_studio_preview.py — REGLA R51: PREVIEW YOUTUBE STUDIO + PANTALLA 3
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from hbos_auth_ui import HBOSAuthUI

class HBOSYouTubeStudioPreview:
    def __init__(self):
        self.video_path = os.path.abspath('assets/videos/demis_hassabis_final.mp4')
        self.thumb_path = os.path.abspath('assets/videos/demis_hassabis_youtube_thumb.jpg')
        self.log_file = 'youtube_studio_preview_log.json'
        self.auth = HBOSAuthUI(timeout_minutes=60)

    def verify_assets(self):
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"Video master no encontrado en {self.video_path}")
        if not os.path.exists(self.thumb_path):
            raise FileNotFoundError(f"Thumbnail no encontrado en {self.thumb_path}")
        
        sha_vid = hashlib.sha256(open(self.video_path, 'rb').read()).hexdigest()
        sha_thumb = hashlib.sha256(open(self.thumb_path, 'rb').read()).hexdigest()
        size_mb = os.path.getsize(self.video_path) / (1024 * 1024)
        
        return {
            'video_sha256': sha_vid,
            'thumbnail_sha256': sha_thumb,
            'size_mb': round(size_mb, 2)
        }

    def launch_screen3_preview(self):
        """Lanza ffplay en la Pantalla 3 (-1920, 0, 1280x720) para inspeccion humana in-situ."""
        print('[PANTALLA 3] Proyectando video master en Monitor 3 (x=-1920, y=0, 1280x720)...')
        cmd = [
            'ffplay',
            '-x', '1280',
            '-y', '720',
            '-left', '-1920',
            '-top', '0',
            '-window_title', 'HBOS Studio Preview - Pantalla 3 (Demis Hassabis)',
            self.video_path
        ]
        # Iniciar en background independiente
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc.pid

    def execute_preview_protocol(self):
        assets = self.verify_assets()
        
        # 1. Chequeo OAuth
        has_oauth = os.path.exists('client_secret.json') or os.path.exists('youtube_oauth.json')
        studio_target_url = 'https://studio.youtube.com' if not has_oauth else 'https://studio.youtube.com/video/draft_ep04/edit'
        
        metadata = {
            'title': 'Demis Hassabis: El Arquitecto de DeepMind y AlphaFold | HBOS Ep04',
            'description': (
                "Episodio 04 de HBOS-Diamantino.\n"
                "La revolucion de AlphaFold y la creacion de la AGI soberana explicada por Demis Hassabis.\n\n"
                "Canal Soberano: @ipanemamarketingusa\n"
                "Hash Criptografico SHA-256: " + assets['video_sha256']
            ),
            'tags': ['DemisHassabis', 'DeepMind', 'AlphaFold', 'HBOS', 'Diamantino', 'AGI', 'InteligenciaArtificial'],
            'privacy': 'private',
            'category_id': '28',
            'video_file': self.video_path,
            'thumbnail_file': self.thumb_path,
            'size_mb': assets['size_mb'],
            'sha256': assets['video_sha256'],
            'oauth_status': 'OAUTH_PENDING' if not has_oauth else 'OAUTH_ACTIVE',
            'studio_preview_url': studio_target_url
        }
        
        # 2. Abrir reproductor en Pantalla 3
        player_pid = self.launch_screen3_preview()
        
        # 3. Validacion Biometrica con Windows Hello (scope op244_preview)
        approved = self.auth.authorize(
            scope='op244_preview',
            message='HBOS R51: Aprobar preview y publicacion en YouTube Studio'
        )
        
        audit_entry = {
            'operation_id': 244,
            'timestamp': time.asctime(),
            'rule': 'R51',
            'status': 'PREVIEW_APPROVED' if approved else 'PREVIEW_REJECTED',
            'player_pid': player_pid,
            'metadata': metadata,
            'biometric_authorized': approved
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(audit_entry, f, indent=2)
            
        print('[YOUTUBE STUDIO PREVIEW] [OK] Auditoria y estado guardado en:', self.log_file)
        return audit_entry

if __name__ == '__main__':
    preview_mgr = HBOSYouTubeStudioPreview()
    res = preview_mgr.execute_preview_protocol()
    print('[OK] Protocolo R51 Completado:', res['status'])
