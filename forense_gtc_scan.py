import os, sys, glob, json, hashlib, subprocess, datetime

def get_sha256(filepath):
    try:
        if filepath.startswith("G:") and os.path.getsize(filepath) > 50*1024*1024:
            return "DRIVE_STREAM_LARGE"
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192 * 1024):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def get_ffprobe(filepath):
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration,size:stream=width,height,codec_name,r_frame_rate',
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

keywords = [
    'gtc', 'jensen', 'taiwan', 'video2', 'video_2', 'video3', 'video_3',
    'v2', 'v3', 'anchor', 'demo_v2', 'demo_v3', 'master_v2', 'master_v3',
    'master_v4', 'master_v5', 'final_v2', 'final_v3', 'final2', 'final3',
    'huang', 'ep02'
]

scan_roots = [
    r"c:\Users\ipane\hbos-deploy\hbos-vector-engine",
    r"c:\Users\ipane\backup_hbos",
    r"G:\My Drive\HBOS-Diamantino",
    r"G:\My Drive\HBOS_DRIVE"
]

exts = {'.mp4', '.mov', '.mkv', '.webm', '.avi'}

results = []

for root in scan_roots:
    if not os.path.exists(root):
        continue
    print(f"Scanning {root}...")
    for dirpath, dirnames, filenames in os.walk(root):
        if '.git' in dirpath or 'node_modules' in dirpath:
            continue
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in exts:
                f_lower = f.lower()
                dir_lower = dirpath.lower()
                # Check if matches any keyword
                if any(k in f_lower or k in dir_lower for k in keywords):
                    full_p = os.path.join(dirpath, f)
                    try:
                        stat = os.stat(full_p)
                        results.append({
                            'path': full_p,
                            'filename': f,
                            'dir': dirpath,
                            'size_bytes': stat.st_size,
                            'size_mb': round(stat.st_size / (1024*1024), 2),
                            'mtime': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except Exception as e:
                        pass

print(f"Found {len(results)} candidate video files.")

# Probe each
for r in results:
    p = r['path']
    print(f"Probing {r['filename']} ({r['size_mb']} MB)...")
    r['sha256'] = get_sha256(p)
    r['ffprobe'] = get_ffprobe(p)

with open('forense_gtc_jensen_videos.json', 'w', encoding='utf-8') as out:
    json.dump(results, out, indent=2)

print("[OK] Saved forense_gtc_jensen_videos.json")
