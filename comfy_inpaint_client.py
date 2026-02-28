"""
HomeForge AI — ComfyUI Flux Inpainting Client
Inpainting del rudere con Flux GGUF via ComfyUI.
Usa SetLatentNoiseMask per inpainting con modello standard.
"""
import json
import time
import uuid
import urllib.request
import urllib.parse
import subprocess
import sys
import shutil
from pathlib import Path

COMFYUI_DIR = Path(__file__).parent.parent / "Homeforge-ComfyUI"
COMFYUI_URL = "http://127.0.0.1:8188"
PYTHON_EXE = "C:/Python312/python.exe"

PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ComfyInpaintClient:
    def __init__(self, server_url=COMFYUI_URL):
        self.server_url = server_url.rstrip("/")

    # ── Server ──
    def _server_is_running(self):
        try:
            req = urllib.request.urlopen(f"{self.server_url}/system_stats", timeout=3)
            return req.status == 200
        except Exception:
            return False

    def start_server(self, wait_timeout=180):
        if self._server_is_running():
            print("[Inpaint] Server already running")
            return True
        print("[Inpaint] Starting ComfyUI server...")
        main_py = COMFYUI_DIR / "main.py"
        cmd = [PYTHON_EXE, str(main_py), "--listen", "127.0.0.1",
               "--port", "8188", "--cpu"]
        self._proc = subprocess.Popen(
            cmd, cwd=str(COMFYUI_DIR),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        start = time.time()
        while time.time() - start < wait_timeout:
            if self._server_is_running():
                print(f"[Inpaint] Server started in {time.time()-start:.0f}s")
                return True
            time.sleep(3)
        raise TimeoutError(f"ComfyUI didn't start within {wait_timeout}s")

    # ── API ──
    def _api_post(self, endpoint, data):
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            f"{self.server_url}/{endpoint}",
            data=body, headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read().decode("utf-8"))

    def _api_get(self, endpoint):
        req = urllib.request.urlopen(f"{self.server_url}/{endpoint}", timeout=30)
        return json.loads(req.read().decode("utf-8"))

    def _queue_prompt(self, workflow):
        client_id = str(uuid.uuid4())
        data = {"prompt": workflow, "client_id": client_id}
        result = self._api_post("prompt", data)
        return result["prompt_id"], client_id

    def _wait_for_completion(self, prompt_id, timeout=18000):
        """Poll until done. Timeout 5 hours for CPU rendering."""
        start = time.time()
        last_print = 0
        while time.time() - start < timeout:
            try:
                history = self._api_get(f"history/{prompt_id}")
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    status = history[prompt_id].get("status", {})
                    if status.get("completed", False) or outputs:
                        return outputs
                    status_str = status.get("status_str", "")
                    if "error" in status_str.lower():
                        raise RuntimeError(f"ComfyUI error: {status}")
            except (urllib.error.URLError, ConnectionResetError):
                pass  # Server busy
            elapsed = time.time() - start
            if elapsed - last_print > 60:
                print(f"[Inpaint] Waiting... {elapsed/60:.0f} min elapsed")
                last_print = elapsed
            time.sleep(5)
        raise TimeoutError(f"Not completed within {timeout}s")

    def _download_image(self, filename, subfolder="", folder_type="output"):
        params = urllib.parse.urlencode({
            "filename": filename, "subfolder": subfolder, "type": folder_type
        })
        url = f"{self.server_url}/view?{params}"
        resp = urllib.request.urlopen(url, timeout=60)
        return resp.read()

    def _copy_to_input(self, src_path):
        src = Path(src_path)
        dst = COMFYUI_DIR / "input" / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            shutil.copy2(str(src), str(dst))
            print(f"[Inpaint] Copied {src.name} -> ComfyUI input/")

    # ── Inpainting Workflow ──
    def _build_inpaint_workflow(self, photo_filename, mask_filename,
                                 prompt, width, height,
                                 steps=20, cfg=3.5, denoise=0.75, seed=None):
        """
        Inpainting workflow using SetLatentNoiseMask.
        1. LoadImage (photo) → VAEEncode → latent
        2. LoadImage (mask) → SetLatentNoiseMask
        3. KSampler (denoise < 1.0) regenerates only masked area
        4. VAEDecode → SaveImage
        """
        if seed is None:
            seed = int(time.time()) % (2**32)

        workflow = {}
        nid_counter = [0]
        def nid():
            nid_counter[0] += 1
            return str(nid_counter[0])

        # Load UNET (GGUF)
        unet_id = nid()
        workflow[unet_id] = {
            "class_type": "UnetLoaderGGUF",
            "inputs": {"unet_name": "flux1-dev-Q4_K_S.gguf"}
        }

        # Load CLIP
        clip_id = nid()
        workflow[clip_id] = {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
                "type": "flux"
            }
        }

        # Load VAE
        vae_id = nid()
        workflow[vae_id] = {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "ae.safetensors"}
        }

        # CLIP Text Encode (prompt)
        pos_id = nid()
        workflow[pos_id] = {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": [clip_id, 0]
            }
        }

        # Load Photo
        photo_load_id = nid()
        workflow[photo_load_id] = {
            "class_type": "LoadImage",
            "inputs": {"image": photo_filename}
        }

        # Resize photo to target resolution for processing
        resize_photo_id = nid()
        workflow[resize_photo_id] = {
            "class_type": "ImageScale",
            "inputs": {
                "image": [photo_load_id, 0],
                "upscale_method": "lanczos",
                "width": width,
                "height": height,
                "crop": "center"
            }
        }

        # VAE Encode photo → latent
        vae_enc_id = nid()
        workflow[vae_enc_id] = {
            "class_type": "VAEEncode",
            "inputs": {
                "pixels": [resize_photo_id, 0],
                "vae": [vae_id, 0]
            }
        }

        # Load Mask
        mask_load_id = nid()
        workflow[mask_load_id] = {
            "class_type": "LoadImage",
            "inputs": {"image": mask_filename}
        }

        # Resize mask to match
        resize_mask_id = nid()
        workflow[resize_mask_id] = {
            "class_type": "ImageScale",
            "inputs": {
                "image": [mask_load_id, 0],
                "upscale_method": "lanczos",
                "width": width,
                "height": height,
                "crop": "center"
            }
        }

        # Convert mask image to mask (take red channel)
        # Use WAS node: Image to Mask
        img_to_mask_id = nid()
        workflow[img_to_mask_id] = {
            "class_type": "ImageToMask",
            "inputs": {
                "image": [resize_mask_id, 0],
                "channel": "red"
            }
        }

        # SetLatentNoiseMask — this is the key for inpainting!
        set_mask_id = nid()
        workflow[set_mask_id] = {
            "class_type": "SetLatentNoiseMask",
            "inputs": {
                "samples": [vae_enc_id, 0],
                "mask": [img_to_mask_id, 0]
            }
        }

        # KSampler with denoise < 1.0
        sampler_id = nid()
        workflow[sampler_id] = {
            "class_type": "KSampler",
            "inputs": {
                "model": [unet_id, 0],
                "positive": [pos_id, 0],
                "negative": [pos_id, 0],  # Flux doesn't use negative
                "latent_image": [set_mask_id, 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": denoise
            }
        }

        # VAE Decode
        decode_id = nid()
        workflow[decode_id] = {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": [sampler_id, 0],
                "vae": [vae_id, 0]
            }
        }

        # Save Image
        save_id = nid()
        workflow[save_id] = {
            "class_type": "SaveImage",
            "inputs": {
                "images": [decode_id, 0],
                "filename_prefix": "inpaint"
            }
        }

        return workflow, seed

    # ── Main Inpaint Method ──
    def inpaint(self, photo_path, mask_path, prompt,
                output_name="inpaint", width=1024, height=768,
                steps=20, cfg=3.5, denoise=0.75, seed=None):
        """Run inpainting. Returns (output_path, seed_used)."""
        self.start_server()

        # Copy files to ComfyUI input
        self._copy_to_input(photo_path)
        self._copy_to_input(mask_path)

        photo_filename = Path(photo_path).name
        mask_filename = Path(mask_path).name

        print(f"[Inpaint] Running: denoise={denoise}, steps={steps}, cfg={cfg}")
        print(f"[Inpaint] Resolution: {width}x{height}")
        print(f"[Inpaint] Prompt: {prompt[:100]}...")

        workflow, seed_used = self._build_inpaint_workflow(
            photo_filename, mask_filename, prompt,
            width, height, steps, cfg, denoise, seed
        )
        print(f"[Inpaint] Seed: {seed_used}")

        prompt_id, client_id = self._queue_prompt(workflow)
        print(f"[Inpaint] Queued: {prompt_id}")

        outputs = self._wait_for_completion(prompt_id)
        print(f"[Inpaint] Completed!")

        output_path = None
        for node_id_str, node_out in outputs.items():
            if "images" in node_out:
                for img_info in node_out["images"]:
                    filename = img_info["filename"]
                    subfolder = img_info.get("subfolder", "")
                    img_data = self._download_image(filename, subfolder)
                    save_name = f"{output_name}.png"
                    output_path = OUTPUT_DIR / save_name
                    output_path.write_bytes(img_data)
                    print(f"[Inpaint] Saved: {output_path}")
                    break

        if output_path is None:
            raise RuntimeError("No image generated")

        return output_path, seed_used


# ── Main ──
if __name__ == "__main__":
    client = ComfyInpaintClient()

    PHOTO = str(PROJECT_DIR / "photos" / "site_photo.jpg")
    MASK = str(OUTPUT_DIR / "mask_rudere.png")

    PROMPT = (
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

    # Generate 5 variants with different seeds
    seeds = [42, 1337, 2024, 7777, 31415]
    results = []

    for i, seed in enumerate(seeds):
        print(f"\n{'='*60}")
        print(f"VARIANT {i+1}/5 — Seed {seed}")
        print(f"{'='*60}")
        try:
            path, used_seed = client.inpaint(
                photo_path=PHOTO,
                mask_path=MASK,
                prompt=PROMPT,
                output_name=f"inpaint_v{i+1}",
                width=1024,
                height=768,
                steps=20,
                cfg=3.5,
                denoise=0.75,
                seed=seed
            )
            results.append((path, used_seed))
            print(f"[OK] Variant {i+1} saved: {path}")
        except Exception as e:
            print(f"[ERROR] Variant {i+1}: {e}")
            results.append((None, seed))

    print(f"\n{'='*60}")
    print(f"COMPLETED: {len([r for r in results if r[0]])} / 5 variants")
    for i, (path, seed) in enumerate(results):
        status = "OK" if path else "FAILED"
        print(f"  v{i+1}: {status} (seed {seed})")
    print(f"{'='*60}")
