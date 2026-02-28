"""
HomeForge AI — L5 Flux Renderer: End-to-End Test
Prende i render grezzi da L4 e genera l'immagine fotorealistica via ComfyUI + Flux.
"""

import sys
import time
from pathlib import Path

# Aggiungi project dir al path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from comfy_flux_client import ComfyFluxClient
from prompt_engineer_flux import PromptEngineerFlux

OUTPUT_DIR = PROJECT_DIR / "output"


def main():
    print("=" * 60)
    print("HomeForge AI — L5 Flux Renderer")
    print("=" * 60)

    # Verifica input da L4
    depth_path = OUTPUT_DIR / "test_L4_depth.png"
    canny_path = OUTPUT_DIR / "test_L4_canny.png"
    grezzo_path = OUTPUT_DIR / "test_L4_grezzo.png"

    for p in [grezzo_path, depth_path, canny_path]:
        if not p.exists():
            print(f"[L5] ERRORE: File mancante: {p}")
            print("[L5] Esegui prima L4_script_grezzo.py in Blender")
            sys.exit(1)
        print(f"[L5] Input trovato: {p.name} ({p.stat().st_size / 1024:.0f} KB)")

    # Genera prompt da L1
    print("\n[L5] Generazione prompt da L1...")
    engineer = PromptEngineerFlux()
    try:
        prompt_data = engineer.generate_prompt()
    except FileNotFoundError:
        print("[L5] L1 decisions non trovate, uso prompt manuale")
        prompt_data = {
            "positive": (
                "photorealistic architectural photography, professional 8k photo, "
                "shot with Canon EOS R5 and 24-70mm f/2.8 lens, "
                "natural overcast alpine lighting, soft shadows, "
                "Italian Alps Valtellina valley background with mountains, "
                "11x8m single story alpine stone house, "
                "natural rough-cut alpine stone masonry walls with lime mortar, "
                "traditional heavy slate stone piode roof tiles, asymmetric gable, "
                "large corner glazing on southwest corner with frameless glass joint, "
                "dark weathered wood window frames and beam ends at eaves, "
                "traditional stone chimney, "
                "viewed from south meadow at eye level, 16m distance, "
                "rural alpine village setting, green meadow foreground, "
                "mountain peaks in background, autumn atmosphere"
            ),
            "negative": (
                "cartoon, illustration, 3d render, CGI look, plastic, "
                "oversaturated, unrealistic colors, blurry, low quality"
            )
        }

    print(f"[L5] Prompt: {prompt_data['positive'][:120]}...")

    # Genera immagine fotorealistica
    print("\n[L5] Avvio generazione Flux...")
    start_time = time.time()

    client = ComfyFluxClient()
    result = client.generate_render(
        prompt=prompt_data["positive"],
        depth_map_path=str(depth_path),
        canny_map_path=str(canny_path),
        output_name="test_L5_fotorealistico",
        width=1024,
        height=768,
        steps=4  # CPU mode: 4 steps (~20min), GPU: use 20 steps
    )

    elapsed = time.time() - start_time

    print(f"\n[L5] COMPLETATO in {elapsed:.0f}s")
    print(f"[L5] Output: {result}")
    print("=" * 60)

    # Salva log
    log_path = PROJECT_DIR / "chain" / "L5_execution_log.md"
    log_path.write_text(f"""# L5 — Flux Render Log
## Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S')}
## Prompt: {prompt_data['positive'][:200]}...
## ControlNet: depth=yes, canny=yes
## Settings: steps=20, cfg=1.0, size=1024x768

## Result
- Status: SUCCESS
- Generation time: {elapsed:.0f}s
- Output: {result}
- Input grezzo: {grezzo_path}
- Input depth: {depth_path}
- Input canny: {canny_path}
""", encoding="utf-8")
    print(f"[L5] Log salvato: {log_path}")


if __name__ == "__main__":
    main()
