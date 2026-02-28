"""
Post-processing PIL per Ca' del Papa render finale.
Applica: warm grade, contrast boost, sharpening, vignette.
"""
from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
import numpy as np

PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_DIR / "output"

def postprocess(input_path, output_path):
    img = Image.open(input_path).convert("RGB")
    w, h = img.size

    # 1. Warm color shift (R+3%, B-3%)
    r, g, b = img.split()
    r = r.point(lambda x: min(255, int(x * 1.03)))
    b = b.point(lambda x: int(x * 0.97))
    img = Image.merge("RGB", (r, g, b))

    # 2. Contrast +8%
    img = ImageEnhance.Contrast(img).enhance(1.08)

    # 3. Saturation +8%
    img = ImageEnhance.Color(img).enhance(1.08)

    # 4. Sharpening
    img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=30, threshold=3))

    # 5. Vignette
    arr = np.array(img, dtype=np.float64)
    cx, cy = w / 2, h / 2
    max_dist = (cx**2 + cy**2) ** 0.5
    Y, X = np.ogrid[:h, :w]
    dist = ((X - cx)**2 + (Y - cy)**2) ** 0.5
    vignette = 1.0 - 0.25 * (dist / max_dist) ** 2
    arr *= vignette[:, :, np.newaxis]
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)

    img.save(output_path, quality=95)
    print(f"Post-processed: {output_path}")
    return output_path


if __name__ == "__main__":
    # Standalone
    standalone_in = OUTPUT_DIR / "ca_del_papa_standalone.png"
    standalone_out = OUTPUT_DIR / "ca_del_papa_standalone_final.png"
    if standalone_in.exists():
        postprocess(standalone_in, standalone_out)

    # Fotoinserimento
    render_in = OUTPUT_DIR / "ca_del_papa_render.png"
    render_out = OUTPUT_DIR / "ca_del_papa_render_final.png"
    if render_in.exists():
        postprocess(render_in, render_out)

    print("Done.")
