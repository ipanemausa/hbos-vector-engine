import os, sys, glob, hashlib, subprocess, json, datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('.env.local')

def get_sha256(filepath):
    try:
        h = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192 * 1024):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"

def get_ffprobe_duration(filepath):
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', str(filepath)
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        dur = res.stdout.strip()
        if dur:
            return round(float(dur), 3)
        return None
    except Exception as e:
        return f"ERR: {e}"

def scan_videos():
    roots = [
        r"c:\Users\ipane\hbos-deploy\hbos-vector-engine",
        r"c:\Users\ipane\backup_hbos",
        r"G:\My Drive\HBOS-Diamantino",
        r"G:\My Drive\HBOS_DRIVE"
    ]
    exts = {'.mp4', '.mov', '.mkv', '.webm'}
    findings = []

    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(days=14) # extend to 14 days to be certain

    for root in roots:
        if not os.path.exists(root):
            print(f"[WARN] Path does not exist: {root}")
            continue
        print(f"[*] Scanning {root}...")
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip .git, node_modules
            if '.git' in dirpath or 'node_modules' in dirpath:
                continue
            for f in filenames:
                ext = os.path.splitext(f)[1].lower()
                if ext in exts:
                    full_p = os.path.join(dirpath, f)
                    try:
                        stat = os.stat(full_p)
                        mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
                        size_b = stat.st_size
                        findings.append({
                            'path': full_p,
                            'name': f,
                            'size_bytes': size_b,
                            'size_mb': round(size_b / (1024*1024), 2),
                            'mtime': mtime.isoformat(),
                            'is_recent_14d': mtime >= seven_days_ago
                        })
                    except Exception as e:
                        print(f"Error reading {full_p}: {e}")

    print(f"Total video files found: {len(findings)}")
    # compute hash and ffprobe for matched or notable files
    for item in findings:
        p = item['path']
        print(f"Probing: {item['name']} ({item['size_mb']} MB)")
        item['sha256'] = get_sha256(p)
        item['duration_s'] = get_ffprobe_duration(p)

    with open('forense_video_scan.json', 'w', encoding='utf-8') as out:
        json.dump(findings, out, indent=2)
    print("[OK] Saved forense_video_scan.json")

if __name__ == '__main__':
    scan_videos()
