"""
HomeForge AI — ComfyUI Flux Client
Genera render fotorealistici via ComfyUI + Flux GGUF + ControlNet.
"""

import json
import time
import uuid
import urllib.request
import urllib.parse
import subprocess
import sys
import os
from pathlib import Path

COMFYUI_DIR = Path(__file__).parent.parent / "Homeforge-ComfyUI"
COMFYUI_URL = "http://127.0.0.1:8188"
PYTHON_EXE = "C:/Python312/python.exe"


class ComfyFluxClient:
    """Client per generare immagini fotorealistiche via ComfyUI + Flux."""

    def __init__(self, server_url=COMFYUI_URL):
        self.server_url = server_url.rstrip("/")
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ── Server Management ────────────────────────────────────────────

    def _server_is_running(self):
        try:
            req = urllib.request.urlopen(f"{self.server_url}/system_stats", timeout=3)
            return req.status == 200
        except Exception:
            return False

    def start_server(self, wait_timeout=120):
        """Avvia ComfyUI server se non attivo."""
        if self._server_is_running():
            print("[ComfyFlux] Server già attivo")
            return True

        print("[ComfyFlux] Avvio ComfyUI server...")
        main_py = COMFYUI_DIR / "main.py"
        if not main_py.exists():
            raise FileNotFoundError(f"ComfyUI non trovato: {main_py}")

        # Avvia in background
        cmd = [PYTHON_EXE, str(main_py), "--listen", "127.0.0.1",
               "--port", "8188", "--cpu"]
        self._server_proc = subprocess.Popen(
            cmd, cwd=str(COMFYUI_DIR),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

        # Attendi avvio
        start = time.time()
        while time.time() - start < wait_timeout:
            if self._server_is_running():
                print(f"[ComfyFlux] Server avviato in {time.time()-start:.0f}s")
                return True
            time.sleep(2)

        raise TimeoutError(f"ComfyUI non avviato entro {wait_timeout}s")

    # ── API Calls ────────────────────────────────────────────────────

    def _api_post(self, endpoint, data):
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            f"{self.server_url}/{endpoint}",
            data=body,
            headers={"Content-Type": "application/json"}
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

    def _wait_for_completion(self, prompt_id, timeout=3600):
        """Poll history fino a completamento."""
        start = time.time()
        while time.time() - start < timeout:
            history = self._api_get(f"history/{prompt_id}")
            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                status = history[prompt_id].get("status", {})
                if status.get("completed", False) or outputs:
                    return outputs
                status_str = status.get("status_str", "")
                if "error" in status_str.lower():
                    raise RuntimeError(f"ComfyUI error: {status}")
            time.sleep(3)
        raise TimeoutError(f"Generazione non completata entro {timeout}s")

    def _download_image(self, filename, subfolder="", folder_type="output"):
        params = urllib.parse.urlencode({
            "filename": filename, "subfolder": subfolder, "type": folder_type
        })
        url = f"{self.server_url}/view?{params}"
        resp = urllib.request.urlopen(url, timeout=30)
        return resp.read()

    # ── Workflow Builder ─────────────────────────────────────────────

    def _build_workflow(self, prompt, negative_prompt="",
                        depth_map_path=None, canny_map_path=None,
                        width=1024, height=768, steps=20, cfg=1.0,
                        denoise=1.0, seed=None):
        """Costruisce workflow Flux GGUF dinamicamente."""
        if seed is None:
            seed = int(time.time()) % (2**32)

        workflow = {}
        node_id = 0

        def nid():
            nonlocal node_id
            node_id += 1
            return str(node_id)

        # ── Load UNET (GGUF) ──
        unet_id = nid()
        workflow[unet_id] = {
            "class_type": "UnetLoaderGGUF",
            "inputs": {
                "unet_name": "flux1-dev-Q4_K_S.gguf"
            }
        }

        # ── Load CLIP (DualCLIPLoader) ──
        clip_id = nid()
        workflow[clip_id] = {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
                "type": "flux"
            }
        }

        # ── Load VAE ──
        vae_id = nid()
        workflow[vae_id] = {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "ae.safetensors"
            }
        }

        # ── CLIP Text Encode (positive) ──
        pos_id = nid()
        workflow[pos_id] = {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": [clip_id, 0]
            }
        }

        # ── Empty Latent ──
        latent_id = nid()
        workflow[latent_id] = {
            "class_type": "EmptySD3LatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            }
        }

        # ── Sampler ──
        model_input = [unet_id, 0]
        latent_input = [latent_id, 0]

        # ── ControlNet (se fornite depth/canny maps) ──
        conditioning_pos = [pos_id, 0]

        if depth_map_path and Path(depth_map_path).exists():
            # Load depth image
            depth_load_id = nid()
            workflow[depth_load_id] = {
                "class_type": "LoadImage",
                "inputs": {
                    "image": str(Path(depth_map_path).name),
                }
            }
            # Installare l'immagine nella cartella input di ComfyUI
            self._copy_to_input(depth_map_path)

            # Load ControlNet
            cn_load_id = nid()
            workflow[cn_load_id] = {
                "class_type": "ControlNetLoader",
                "inputs": {
                    "control_net_name": "flux-controlnet-union.safetensors"
                }
            }

            # Apply ControlNet
            cn_apply_id = nid()
            workflow[cn_apply_id] = {
                "class_type": "ControlNetApplyAdvanced",
                "inputs": {
                    "positive": conditioning_pos,
                    "negative": [pos_id, 0],  # Flux usa lo stesso
                    "control_net": [cn_load_id, 0],
                    "vae": [vae_id, 0],
                    "image": [depth_load_id, 0],
                    "strength": 0.65,
                    "start_percent": 0.0,
                    "end_percent": 0.85
                }
            }
            conditioning_pos = [cn_apply_id, 0]

        if canny_map_path and Path(canny_map_path).exists():
            canny_load_id = nid()
            workflow[canny_load_id] = {
                "class_type": "LoadImage",
                "inputs": {
                    "image": str(Path(canny_map_path).name),
                }
            }
            self._copy_to_input(canny_map_path)

            cn_load2_id = nid()
            workflow[cn_load2_id] = {
                "class_type": "ControlNetLoader",
                "inputs": {
                    "control_net_name": "flux-controlnet-union.safetensors"
                }
            }

            cn_apply2_id = nid()
            workflow[cn_apply2_id] = {
                "class_type": "ControlNetApplyAdvanced",
                "inputs": {
                    "positive": conditioning_pos,
                    "negative": [pos_id, 0],
                    "control_net": [cn_load2_id, 0],
                    "vae": [vae_id, 0],
                    "image": [canny_load_id, 0],
                    "strength": 0.50,
                    "start_percent": 0.0,
                    "end_percent": 0.70
                }
            }
            conditioning_pos = [cn_apply2_id, 0]

        # ── KSampler ──
        sampler_id = nid()
        workflow[sampler_id] = {
            "class_type": "KSampler",
            "inputs": {
                "model": model_input,
                "positive": conditioning_pos,
                "negative": conditioning_pos,  # Flux non usa negative
                "latent_image": latent_input,
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": denoise
            }
        }

        # ── VAE Decode ──
        decode_id = nid()
        workflow[decode_id] = {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": [sampler_id, 0],
                "vae": [vae_id, 0]
            }
        }

        # ── Save Image ──
        save_id = nid()
        workflow[save_id] = {
            "class_type": "SaveImage",
            "inputs": {
                "images": [decode_id, 0],
                "filename_prefix": "homeforge"
            }
        }

        return workflow

    def _copy_to_input(self, src_path):
        """Copia un file nella cartella input di ComfyUI."""
        src = Path(src_path)
        dst = COMFYUI_DIR / "input" / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            import shutil
            shutil.copy2(str(src), str(dst))
            print(f"[ComfyFlux] Copiato {src.name} -> input/")

    # ── Main Generate Method ─────────────────────────────────────────

    def generate_render(self, prompt, depth_map_path=None, canny_map_path=None,
                        site_photo_path=None, output_name=None,
                        width=1024, height=768, steps=20):
        """
        Genera un render fotorealistico con Flux via ComfyUI.

        Args:
            prompt: Prompt testuale per Flux
            depth_map_path: Path opzionale a depth map per ControlNet
            canny_map_path: Path opzionale a canny edge map per ControlNet
            site_photo_path: Path opzionale a foto del sito (per img2img futuro)
            output_name: Nome file output (senza estensione)
            width: Larghezza immagine
            height: Altezza immagine
            steps: Numero di sampling steps

        Returns:
            Path al file PNG generato
        """
        # Assicura server attivo
        self.start_server()

        # Build workflow
        print(f"[ComfyFlux] Generazione: {prompt[:80]}...")
        workflow = self._build_workflow(
            prompt=prompt,
            depth_map_path=depth_map_path,
            canny_map_path=canny_map_path,
            width=width,
            height=height,
            steps=steps
        )

        # Queue & wait
        prompt_id, client_id = self._queue_prompt(workflow)
        print(f"[ComfyFlux] Prompt queued: {prompt_id}")

        outputs = self._wait_for_completion(prompt_id, timeout=600)
        print(f"[ComfyFlux] Generazione completata!")

        # Trova l'immagine nell'output
        output_path = None
        for node_id, node_out in outputs.items():
            if "images" in node_out:
                for img_info in node_out["images"]:
                    filename = img_info["filename"]
                    subfolder = img_info.get("subfolder", "")
                    img_data = self._download_image(filename, subfolder)

                    # Salva in output/
                    if output_name:
                        save_name = f"{output_name}.png"
                    else:
                        save_name = filename
                    output_path = self.output_dir / save_name
                    output_path.write_bytes(img_data)
                    print(f"[ComfyFlux] Salvato: {output_path}")
                    break

        if output_path is None:
            raise RuntimeError("Nessuna immagine generata nell'output")

        return output_path


# ── CLI Test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    client = ComfyFluxClient()
    result = client.generate_render(
        prompt="photorealistic architectural photography of an alpine stone house, "
               "natural stone walls, slate roof with piode tiles, dark wood window frames, "
               "corner glazing on southwest corner, overcast natural lighting, "
               "mountains in background, 8k professional architectural photo",
        output_name="test_flux_basic",
        width=1024,
        height=768,
        steps=20
    )
    print(f"Output: {result}")
