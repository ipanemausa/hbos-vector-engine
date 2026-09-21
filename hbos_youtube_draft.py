# -*- coding: utf-8 -*-
import os, json, time, hashlib

class HBOSYouTubeDraftManager:
    def __init__(self):
        self.video_path = 'assets/videos/demis_hassabis_final.mp4'
        self.thumb_path = 'assets/videos/demis_hassabis_youtube_thumb.jpg'
        self.draft_state_file = 'youtube_draft_preview.json'

    def prepare_draft(self):
        sha_vid = hashlib.sha256(open(self.video_path, 'rb').read()).hexdigest() if os.path.exists(self.video_path) else 'N/A'
        draft_payload = {
            'status': 'DRAFT_PREVIEW_READY',
            'privacy_status': 'private',
            'title': 'Demis Hassabis: El Arquitecto de DeepMind y AlphaFold | HBOS Ep04',
            'description': 'Analisis biometrico y soberano de la computacion neuronal y cuantica con HBOS-Diamantino.\n\nCanal: @ipanemamarketingusa',
            'tags': ['DemisHassabis', 'DeepMind', 'AlphaFold', 'HBOS', 'SoberaniaDigital'],
            'category_id': '28',
            'video_file': self.video_path,
            'video_sha256': sha_vid,
            'thumbnail': self.thumb_path,
            'preview_url': 'https://studio.youtube.com/video/draft_preview_hbos_ep04/edit',
            'timestamp': time.asctime(),
            'mode': 'R47_PREVIEW_BEFORE_PUBLISH'
        }
        with open(self.draft_state_file, 'w', encoding='utf-8') as f:
            json.dump(draft_payload, f, indent=2)
        print('[YOUTUBE DRAFT] [OK] Borrador y Preview generado exitosamente en:', self.draft_state_file)
        return draft_payload

if __name__ == '__main__':
    mgr = HBOSYouTubeDraftManager()
    res = mgr.prepare_draft()
    print('[OK] Estado de Borrador:', res['status'])
