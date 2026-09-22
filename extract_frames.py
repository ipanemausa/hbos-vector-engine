import os, subprocess

videos = [
    ("ep01", r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\media\diamantino\ep01.mp4"),
    ("ep02_v1", r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_master_v1.mp4"),
    ("ep02_v2", r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_master_v2.mp4"),
    ("ep02_v3", r"c:\Users\ipane\hbos-deploy\hbos-vector-engine\ep02_master_v3.mp4")
]

os.makedirs("scratch_frames", exist_ok=True)

for name, vpath in videos:
    if not os.path.exists(vpath):
        continue
    # Extract 4 frames across duration
    for sec in [5, 25, 60, 85, 120]:
        out_img = f"scratch_frames/{name}_sec{sec}.jpg"
        cmd = [
            "ffmpeg", "-y", "-ss", str(sec), "-i", vpath,
            "-vframes", "1", "-q:v", "2", out_img
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[OK] Extracted frames for {name}")
