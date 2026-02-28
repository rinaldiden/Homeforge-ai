"""
Run multiple inpainting variants with different seeds and parameters.
Each variant ~35-45 min on CPU at 512x384.
"""
import json
import time
import uuid
import urllib.request
import urllib.parse
from pathlib import Path

SERVER = "http://127.0.0.1:8188"
OUTPUT_DIR = Path("C:/Users/Stramba/casa/homeforge-ai/output")

PROMPT_TEXT = (
    "Restored single-story alpine stone house, walls made of round grey river stones "
    "identical to the adjacent traditional buildings, asymmetric stone slab roof (piode) "
    "with long gentle south slope and short steep north slope, ridge offset toward the back, "
    "light-colored natural wood beams protruding 40cm from the eaves, "
    "full-height corner glazing on the right corner wrapping around with no vertical mullion "
    "and thin black aluminum frame, dark glass reflecting the landscape, "
    "one french door with black frame on the front facade, "
    "one small window with light wood frame on the left side, "
    "solid light wood entrance door, stone chimney on the back roof slope, "
    "copper rain gutter along the eaves, "
    "winter overcast natural lighting, photorealistic architectural photography, "
    "8k, shot on Canon EOS R5 with 35mm lens"
)


def build_workflow(width, height, steps, cfg, denoise, seed, prefix):
    return {
        "1": {"class_type": "UnetLoaderGGUF",
              "inputs": {"unet_name": "flux1-dev-Q4_K_S.gguf"}},
        "2": {"class_type": "DualCLIPLoader",
              "inputs": {"clip_name1": "clip_l.safetensors",
                         "clip_name2": "t5xxl_fp8_e4m3fn.safetensors", "type": "flux"}},
        "3": {"class_type": "VAELoader",
              "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode",
              "inputs": {"text": PROMPT_TEXT, "clip": ["2", 0]}},
        "5": {"class_type": "LoadImage",
              "inputs": {"image": "site_photo.jpg"}},
        "6": {"class_type": "ImageScale",
              "inputs": {"image": ["5", 0], "upscale_method": "lanczos",
                         "width": width, "height": height, "crop": "center"}},
        "7": {"class_type": "VAEEncode",
              "inputs": {"pixels": ["6", 0], "vae": ["3", 0]}},
        "8": {"class_type": "LoadImage",
              "inputs": {"image": "mask_rudere.png"}},
        "9": {"class_type": "ImageScale",
              "inputs": {"image": ["8", 0], "upscale_method": "lanczos",
                         "width": width, "height": height, "crop": "center"}},
        "10": {"class_type": "ImageToMask",
               "inputs": {"image": ["9", 0], "channel": "red"}},
        "11": {"class_type": "SetLatentNoiseMask",
               "inputs": {"samples": ["7", 0], "mask": ["10", 0]}},
        "12": {"class_type": "KSampler",
               "inputs": {"model": ["1", 0], "positive": ["4", 0],
                          "negative": ["4", 0], "latent_image": ["11", 0],
                          "seed": seed, "steps": steps, "cfg": cfg,
                          "sampler_name": "euler", "scheduler": "simple",
                          "denoise": denoise}},
        "13": {"class_type": "VAEDecode",
               "inputs": {"samples": ["12", 0], "vae": ["3", 0]}},
        "14": {"class_type": "SaveImage",
               "inputs": {"images": ["13", 0], "filename_prefix": prefix}}
    }


def queue_prompt(workflow):
    client_id = str(uuid.uuid4())
    data = json.dumps({"prompt": workflow, "client_id": client_id}).encode()
    req = urllib.request.Request(f"{SERVER}/prompt", data=data,
                                headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    return result["prompt_id"]


def wait_for_all(prompt_ids, timeout=36000):
    """Wait for all prompts to complete. Timeout 10 hours."""
    start = time.time()
    completed = set()
    results = {}
    last_print = 0

    while time.time() - start < timeout and len(completed) < len(prompt_ids):
        for pid in prompt_ids:
            if pid in completed:
                continue
            try:
                resp = urllib.request.urlopen(f"{SERVER}/history/{pid}", timeout=10)
                history = json.loads(resp.read())
                if pid in history:
                    status = history[pid].get("status", {})
                    outputs = history[pid].get("outputs", {})
                    if status.get("completed", False) or outputs:
                        completed.add(pid)
                        results[pid] = outputs
                        print(f"  [DONE] {pid[:8]}... ({len(completed)}/{len(prompt_ids)})")
                    elif "error" in str(status.get("status_str", "")).lower():
                        completed.add(pid)
                        results[pid] = None
                        print(f"  [ERROR] {pid[:8]}...")
            except Exception:
                pass

        elapsed = time.time() - start
        if elapsed - last_print > 60:
            print(f"  Elapsed: {elapsed/60:.0f} min, Completed: {len(completed)}/{len(prompt_ids)}")
            last_print = elapsed
        time.sleep(10)

    return results


def download_image(filename, subfolder=""):
    params = urllib.parse.urlencode({
        "filename": filename, "subfolder": subfolder, "type": "output"
    })
    resp = urllib.request.urlopen(f"{SERVER}/view?{params}", timeout=60)
    return resp.read()


# === VARIANTS ===
variants = [
    # (name, width, height, steps, cfg, denoise, seed)
    ("inpaint_v1", 512, 384, 12, 3.5, 0.78, 42),
    ("inpaint_v2", 512, 384, 12, 3.5, 0.78, 1337),
    ("inpaint_v3", 512, 384, 12, 3.5, 0.72, 2024),
    ("inpaint_v4", 512, 384, 12, 4.0, 0.80, 7777),
    ("inpaint_v5", 512, 384, 12, 3.0, 0.70, 31415),
]

print("=" * 60)
print(f"INPAINTING — {len(variants)} variants")
print("=" * 60)

prompt_ids = []
variant_map = {}

for name, w, h, steps, cfg, denoise, seed in variants:
    workflow = build_workflow(w, h, steps, cfg, denoise, seed, name)
    pid = queue_prompt(workflow)
    prompt_ids.append(pid)
    variant_map[pid] = name
    print(f"Queued {name}: seed={seed}, denoise={denoise}, cfg={cfg} -> {pid[:8]}...")

print(f"\nAll {len(variants)} variants queued. Waiting for completion...")
print(f"Estimated time: {len(variants) * 45} min ({len(variants) * 45 / 60:.1f} hours)")

start_time = time.time()
results = wait_for_all(prompt_ids)
total_time = time.time() - start_time

print(f"\n{'=' * 60}")
print(f"ALL DONE in {total_time/60:.0f} min ({total_time/3600:.1f} hours)")
print(f"{'=' * 60}")

# Download and save
for pid, outputs in results.items():
    name = variant_map.get(pid, "unknown")
    if outputs is None:
        print(f"  {name}: FAILED")
        continue
    for node_id, node_out in outputs.items():
        if "images" in node_out:
            for img_info in node_out["images"]:
                img_data = download_image(img_info["filename"], img_info.get("subfolder", ""))
                out_path = OUTPUT_DIR / f"{name}.png"
                out_path.write_bytes(img_data)
                print(f"  {name}: saved ({len(img_data)} bytes)")

print("\nDone!")
