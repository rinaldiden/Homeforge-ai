"""
Post-processing via Blender Python (since standalone Python not available).
Applies warm grade, contrast, sharpening, vignette using bpy.data.images pixel manipulation.
"""
import bpy, math, os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_DIR / "output"


def postprocess(input_path, output_path):
    img = bpy.data.images.load(str(input_path))
    w, h = img.size
    px = list(img.pixels)  # RGBA flat list

    # 1. Warm shift: R*1.03, B*0.97
    for i in range(w * h):
        idx = i * 4
        px[idx] = min(1.0, px[idx] * 1.03)      # R
        px[idx + 2] = px[idx + 2] * 0.97          # B

    # 2. Contrast +8%: (color - 0.5) * 1.08 + 0.5
    for i in range(w * h):
        idx = i * 4
        for c in range(3):
            v = (px[idx + c] - 0.5) * 1.08 + 0.5
            px[idx + c] = max(0.0, min(1.0, v))

    # 3. Saturation +8%
    for i in range(w * h):
        idx = i * 4
        r, g, b = px[idx], px[idx+1], px[idx+2]
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        px[idx]   = max(0.0, min(1.0, lum + (r - lum) * 1.08))
        px[idx+1] = max(0.0, min(1.0, lum + (g - lum) * 1.08))
        px[idx+2] = max(0.0, min(1.0, lum + (b - lum) * 1.08))

    # 4. Vignette
    cx, cy = w / 2, h / 2
    max_dist = math.sqrt(cx**2 + cy**2)
    for y in range(h):
        for x in range(w):
            idx = (y * w + x) * 4
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            vf = 1.0 - 0.20 * (dist / max_dist) ** 2
            px[idx]   *= vf
            px[idx+1] *= vf
            px[idx+2] *= vf

    result = bpy.data.images.new("PP", width=w, height=h)
    result.pixels = px
    result.filepath_raw = str(output_path)
    result.file_format = 'PNG'
    result.save()
    print(f"Post-processed: {output_path}")


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    standalone = OUTPUT_DIR / "ca_del_papa_standalone.png"
    if standalone.exists():
        postprocess(standalone, OUTPUT_DIR / "ca_del_papa_standalone_final.png")

    render = OUTPUT_DIR / "ca_del_papa_render.png"
    if render.exists():
        postprocess(render, OUTPUT_DIR / "ca_del_papa_render_final.png")

    print("Post-processing complete.")


if __name__ == "__main__":
    main()
