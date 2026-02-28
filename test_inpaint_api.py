"""
Test diretto inpainting via API ComfyUI (server già attivo).
Bassa risoluzione (512x384, 8 steps) per test veloce.
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

def build_workflow(width, height, steps, cfg, denoise, seed):
    return {
        "1": {
            "class_type": "UnetLoaderGGUF",
            "inputs": {"unet_name": "flux1-dev-Q4_K_S.gguf"}
        },
        "2": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
                "type": "flux"
            }
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "ae.safetensors"}
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": PROMPT_TEXT,
                "clip": ["2", 0]
            }
        },
        # Load photo
        "5": {
            "class_type": "LoadImage",
            "inputs": {"image": "site_photo.jpg"}
        },
        # Resize photo
        "6": {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["5", 0],
                "upscale_method": "lanczos",
                "width": width,
                "height": height,
                "crop": "center"
            }
        },
        # VAE encode photo
        "7": {
            "class_type": "VAEEncode",
            "inputs": {
                "pixels": ["6", 0],
                "vae": ["3", 0]
            }
        },
        # Load mask
        "8": {
            "class_type": "LoadImage",
            "inputs": {"image": "mask_rudere.png"}
        },
        # Resize mask
        "9": {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["8", 0],
                "upscale_method": "lanczos",
                "width": width,
                "height": height,
                "crop": "center"
            }
        },
        # Convert image to mask
        "10": {
            "class_type": "ImageToMask",
            "inputs": {
                "image": ["9", 0],
                "channel": "red"
            }
        },
        # Set latent noise mask
        "11": {
            "class_type": "SetLatentNoiseMask",
            "inputs": {
                "samples": ["7", 0],
                "mask": ["10", 0]
            }
        },
        # KSampler
        "12": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["4", 0],
                "latent_image": ["11", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": denoise
            }
        },
        # VAE Decode
        "13": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["12", 0],
                "vae": ["3", 0]
            }
        },
        # Save
        "14": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["13", 0],
                "filename_prefix": "inpaint_test"
            }
        }
    }


def queue_and_wait(workflow, timeout=18000):
    client_id = str(uuid.uuid4())
    data = json.dumps({"prompt": workflow, "client_id": client_id}).encode()
    req = urllib.request.Request(
        f"{SERVER}/prompt", data=data,
        headers={"Content-Type": "application/json"}
    )
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    prompt_id = result["prompt_id"]
    print(f"Queued: {prompt_id}")

    start = time.time()
    last_print = 0
    while time.time() - start < timeout:
        try:
            resp = urllib.request.urlopen(f"{SERVER}/history/{prompt_id}", timeout=10)
            history = json.loads(resp.read())
            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                status = history[prompt_id].get("status", {})
                if status.get("completed", False) or outputs:
                    return outputs, prompt_id
                status_str = str(status)
                if "error" in status_str.lower():
                    raise RuntimeError(f"Error: {status}")
        except (urllib.error.URLError, ConnectionResetError):
            pass
        elapsed = time.time() - start
        if elapsed - last_print > 30:
            print(f"  Waiting... {elapsed/60:.1f} min")
            last_print = elapsed
        time.sleep(5)
    raise TimeoutError("Timeout")


def download_image(filename, subfolder=""):
    params = urllib.parse.urlencode({
        "filename": filename, "subfolder": subfolder, "type": "output"
    })
    resp = urllib.request.urlopen(f"{SERVER}/view?{params}", timeout=60)
    return resp.read()


# === MAIN ===
print("=" * 60)
print("INPAINTING TEST — 512x384, 8 steps")
print("=" * 60)

workflow = build_workflow(
    width=512, height=384,
    steps=8, cfg=3.5, denoise=0.75, seed=42
)

start_time = time.time()
outputs, pid = queue_and_wait(workflow)
elapsed = time.time() - start_time
print(f"Completed in {elapsed/60:.1f} min")

for node_id, node_out in outputs.items():
    if "images" in node_out:
        for img_info in node_out["images"]:
            img_data = download_image(img_info["filename"], img_info.get("subfolder", ""))
            out_path = OUTPUT_DIR / "inpaint_test.png"
            out_path.write_bytes(img_data)
            print(f"Saved: {out_path} ({len(img_data)} bytes)")

print("DONE")
