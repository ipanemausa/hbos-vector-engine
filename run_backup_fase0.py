import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

base = r"G:\My Drive\HBOS-Diamantino\Ep02-Los7Chips"

# 1. Backup Master
src_master = os.path.join(base, r"05_Master\ep02_master_v1.mp4")
dst_master = os.path.join(base, r"05_Master\_backup_ep02_master_v1.mp4")
print(f"[*] 1. Copiando Master v1 -> {dst_master}...")
shutil.copyfile(src_master, dst_master)
t1 = os.path.exists(dst_master)
s1 = os.path.getsize(dst_master)
print(f"    [OK] Master backup existe: {t1} ({s1} bytes)")

# 2. Backup Clips
src_clips = os.path.join(base, r"04_Clips_Wan21")
dst_clips = os.path.join(base, r"04_Clips_Wan21_v1_backup")
print(f"[*] 2. Copiando Clips Wan 2.1 -> {dst_clips}...")
if os.path.exists(dst_clips):
    shutil.rmtree(dst_clips)
shutil.copytree(src_clips, dst_clips)
t2 = os.path.exists(dst_clips)
num_clips = len(os.listdir(dst_clips))
print(f"    [OK] Clips backup existe: {t2} ({num_clips} archivos)")

# 3. Backup Voces
src_voces = os.path.join(base, r"03_Assets\Voces")
dst_voces = os.path.join(base, r"03_Assets\Voces_v1_backup")
print(f"[*] 3. Copiando Voces -> {dst_voces}...")
if os.path.exists(dst_voces):
    shutil.rmtree(dst_voces)
shutil.copytree(src_voces, dst_voces)
t3 = os.path.exists(dst_voces)
num_voces = len(os.listdir(dst_voces))
print(f"    [OK] Voces backup existe: {t3} ({num_voces} archivos)")

print("\n=======================================================")
print("VERIFICACION DE BACKUPS (Test-Path):")
print(f"- 05_Master\\_backup_ep02_master_v1.mp4: {t1}")
print(f"- 04_Clips_Wan21_v1_backup: {t2}")
print(f"- 03_Assets\\Voces_v1_backup: {t3}")
print("=======================================================")
if t1 and t2 and t3:
    print("[EXITO] FASE 0 — BACKUP TOTAL COMPLETADO AL 100%")
else:
    print("[ERROR] Falla en alguno de los backups")
