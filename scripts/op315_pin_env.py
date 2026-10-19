import os, re, shutil, subprocess, datetime
root = r"C:\Users\ipane\hbos-deploy\hbos-vector-engine"
key = open(os.path.join(root, "config", "freellmapi-key.txt"), encoding="utf-8").read().strip()
assert key.startswith("freellmapi-") and len(key) > 20

# .gitignore: explicit secret entries (append only if missing)
gi = os.path.join(root, ".gitignore")
txt = open(gi, encoding="utf-8").read()
need = ["config/freellmapi-key.txt", "config/freellmapi-inventory.json", "config/op315-pending.json", ".env", ".env.local"]
add = [n for n in need if not re.search(r"^" + re.escape(n) + r"\s*$", txt, re.M)]
if add:
    open(gi, "a", encoding="utf-8", newline="").write(("" if txt.endswith("\n") else "\r\n") + "\r\n# HBOS secretos explicitos (op=315)\r\n" + "\r\n".join(add) + "\r\n")
print("gitignore added:", add)

# .env: backup then set the 3 canonical vars (replace or add)
env = os.path.join(root, ".env")
bak = f"{env}.bak_{datetime.datetime.now():%Y%m%d%H%M%S}"
shutil.copyfile(env, bak)
t = open(env, encoding="utf-8").read()
for name, val in (("FREELLMAPI_KEY", f'"{key}"'), ("QDRANT_URL", "http://127.0.0.1:6333"), ("FREELLMAPI_URL", "http://127.0.0.1:3001")):
    line = f"{name}={val}"
    if re.search(rf"^{name}=.*$", t, re.M): t = re.sub(rf"^{name}=.*$", lambda m: line, t, flags=re.M)
    else: t = t.rstrip("\r\n") + "\n" + line + "\n"
open(env, "w", encoding="utf-8", newline="").write(t)
print(".env updated (backup:", os.path.basename(bak), ")")

# restrict read permissions to current user
user = os.environ["USERNAME"]
for p in (os.path.join(root, "config", "freellmapi-key.txt"), env):
    r = subprocess.run(["icacls", p, "/inheritance:r", "/grant:r", f"{user}:(R,W)"], capture_output=True, text=True)
    print("icacls", os.path.basename(p), "->", "OK" if r.returncode == 0 else r.stderr.strip()[:80])

# git must ignore all of them
for p in ("config/freellmapi-key.txt", "config/freellmapi-inventory.json", ".env"):
    r = subprocess.run(["git", "-C", root, "check-ignore", "-q", p]); print("git-ignored", p, "->", r.returncode == 0)
