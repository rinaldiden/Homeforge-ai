"""
Monitor ComfyUI queue and collect completed variant images.
Polls every 30s, copies finished images to output/, exits when all done.
"""
import json
import time
import shutil
import urllib.request
import urllib.parse
from pathlib import Path

SERVER = "http://127.0.0.1:8188"
OUTPUT_DIR = Path("C:/Users/Stramba/casa/homeforge-ai/output")
COMFY_OUTPUT = Path("C:/Users/Stramba/casa/Homeforge-ComfyUI/output")

VARIANTS = ["inpaint_v1", "inpaint_v2", "inpaint_v3", "inpaint_v4", "inpaint_v5"]

collected = set()

# Check what's already collected
for v in VARIANTS:
    src = COMFY_OUTPUT / f"{v}_00001_.png"
    dst = OUTPUT_DIR / f"{v}.png"
    if src.exists():
        if not dst.exists():
            shutil.copy2(src, dst)
            print(f"[COPY] {v} -> {dst}")
        collected.add(v)
        print(f"[ALREADY DONE] {v}")

print(f"\nCollected so far: {len(collected)}/{len(VARIANTS)}")

while len(collected) < len(VARIANTS):
    time.sleep(30)
    for v in VARIANTS:
        if v in collected:
            continue
        src = COMFY_OUTPUT / f"{v}_00001_.png"
        if src.exists():
            dst = OUTPUT_DIR / f"{v}.png"
            shutil.copy2(src, dst)
            collected.add(v)
            print(f"[DONE] {v} copied to {dst} ({src.stat().st_size} bytes)")

    # Also check queue status
    try:
        resp = urllib.request.urlopen(f"{SERVER}/queue", timeout=10)
        q = json.loads(resp.read())
        running = len(q.get("queue_running", []))
        pending = len(q.get("queue_pending", []))
        print(f"  Queue: running={running}, pending={pending}, collected={len(collected)}/{len(VARIANTS)}")
    except Exception:
        pass

print(f"\n{'='*60}")
print(f"ALL {len(VARIANTS)} VARIANTS COLLECTED!")
print(f"{'='*60}")
for v in VARIANTS:
    p = OUTPUT_DIR / f"{v}.png"
    if p.exists():
        print(f"  {v}: {p.stat().st_size} bytes")
    else:
        print(f"  {v}: MISSING")
