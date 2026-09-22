import os, sys, hashlib, subprocess, datetime, json

def get_sha256(filepath, max_mb=500):
    try:
        # If file is on G: and > 100MB, skip full sha256 to avoid downloading multi-hundred MB stream unless local
        size_mb = os.path.getsize(filepath) / (1024*1024)
        if filepath.startswith("G:") and size_mb > 50:
            return "DRIVE_STREAM_SKIPPED_FOR_SPEED"
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192 * 1024):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def get_ffprobe_info(filepath):
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration,size,bit_rate:stream=width,height,codec_name,r_frame_rate',
            '-of', 'json', str(filepath)
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=12)
        data = json.loads(res.stdout)
        fmt = data.get('format', {})
        dur = float(fmt.get('duration', 0.0))
        streams = data.get('streams', [])
        v_stream = next((s for s in streams if s.get('codec_name') in ['h264', 'hevc', 'vp9', 'av1']), streams[0] if streams else {})
        return {
            'duration_s': round(dur, 3),
            'width': v_stream.get('width'),
            'height': v_stream.get('height'),
            'fps': v_stream.get('r_frame_rate'),
            'vcodec': v_stream.get('codec_name')
        }
    except Exception as e:
        return {'err': str(e)}

target_files = [
    # Demis Hassabis Videos
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\assets\videos\demis_hassabis_final.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\assets\videos\demis_hassabis_v2\video_final.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\assets\videos\demis_hassabis_v2\video_final_v2.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\assets\videos\demis_hassabis_v2\escenas\ep04_plano_00_wan21.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\assets\videos\demis_hassabis_v2\escenas\ep04_plano_01_wan21.mp4",
    
    # Avatar Presentaciones
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\assets\avatar\alex_avatar_presentation.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\assets\avatar\diamantino_avatar_presentation.mp4",
    r"c:\Users\ipane\backup_hbos\assets\avatar\alex_avatar_presentation.mp4",
    r"G:\My Drive\HBOS-Diamantino\assets\avatar\alex_avatar_presentation.mp4",

    # Ep02 Masters Local
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\_backup_ep02_master_v3.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_master_v3.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_master_v4.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_master_v5.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_plano_07b_wan21.mp4",

    # Ep02 Masters Backup
    r"c:\Users\ipane\backup_hbos\Ep02\ep02_master_v4.mp4",
    r"c:\Users\ipane\backup_hbos\Ep02\ep02_master_v5.mp4",
    r"c:\Users\ipane\backup_hbos\_BACKUP_EPISODIOS\Ep02_2026-09-18\ep02_master_v3.mp4",
    r"c:\Users\ipane\backup_hbos\_BACKUP_EPISODIOS\Ep02_2026-09-18\ep02_master_v4.mp4",

    # Ep02 Masters Drive
    r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips\05_Master\ep02_master_v5.mp4",
    r"G:\My Drive\HBOS-Diamantino\_BACKUP_EPISODIOS\Ep02_2026-09-18\ep02_master_v1.mp4",
    r"G:\My Drive\HBOS-Diamantino\_BACKUP_EPISODIOS\Ep02_2026-09-18\ep02_master_v1_backup.mp4",
    r"G:\My Drive\HBOS-Diamantino\_BACKUP_EPISODIOS\Ep02_2026-09-18\ep02_master_v2.mp4",
    r"G:\My Drive\HBOS-Diamantino\_BACKUP_EPISODIOS\Ep02_2026-09-18\ep02_master_v3.mp4",

    # Ep03 Masters
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\Ep03\ep03_master_v1.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\Ep03\ep03_master_v2.mp4",
    r"c:\Users\ipane\backup_hbos\Ep03\ep03_master_v2.mp4",
    r"c:\Users\ipane\backup_hbos\_BACKUP_EPISODIOS\Ep03_2026-09-18\ep03_master_v1.mp4",
    r"c:\Users\ipane\backup_hbos\_BACKUP_EPISODIOS\Ep03_2026-09-18\ep03_master_v2.mp4",
    r"G:\My Drive\HBOS-Diamantino\Ep03-RedesFotonicasCuanticas\05_Master\ep03_master_v1.mp4",
    r"G:\My Drive\HBOS-Diamantino\Ep03-RedesFotonicasCuanticas\05_Master\ep03_master_v2.mp4",

    # Ep01
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\media\diamantino\ep01.mp4",
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\public\media\diamantino\ep01.mp4"
]

report = []
for p in target_files:
    exists = os.path.exists(p)
    item = {
        'path': p,
        'exists': exists
    }
    print(f"Checking: {os.path.basename(p)} exists={exists}", flush=True)
    if exists:
        try:
            stat = os.stat(p)
            item['size_bytes'] = stat.st_size
            item['size_mb'] = round(stat.st_size / (1024*1024), 2)
            item['mtime'] = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
            item['sha256'] = get_sha256(p)
            item['ffprobe'] = get_ffprobe_info(p)
        except Exception as e:
            item['error'] = str(e)
    report.append(item)
    # save progress incrementally
    with open('forense_report_detallado.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

print(f"[OK] Reporte detallado finalizado: {len(report)} archivos examinados.", flush=True)
