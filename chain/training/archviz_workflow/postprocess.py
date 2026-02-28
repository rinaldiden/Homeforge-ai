"""
ARCHVIZ POST-PROCESSING
Applies final color grading and vignette to the render.
Since Blender 5.0 removed scene.node_tree compositor, we use PIL.
"""
import sys
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageEnhance, ImageFilter

import math


def add_vignette(img, strength=0.4):
    """Add a subtle vignette effect."""
    w, h = img.size
    cx, cy = w / 2, h / 2
    max_dist = math.sqrt(cx**2 + cy**2)

    pixels = img.load()
    for y in range(h):
        for x in range(w):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            factor = 1.0 - strength * (dist / max_dist) ** 2
            r, g, b = pixels[x, y][:3]
            pixels[x, y] = (
                max(0, int(r * factor)),
                max(0, int(g * factor)),
                max(0, int(b * factor)),
            )
    return img


def postprocess(input_path, output_path):
    """Apply archviz post-processing."""
    print(f"[PP] Loading: {input_path}")
    img = Image.open(input_path).convert("RGB")

    # 1. Slight warmth (increase red channel slightly)
    r, g, b = img.split()
    from PIL import ImageMath
    # Warm up: boost reds slightly, reduce blues slightly
    # Use point transform for simplicity
    r = r.point(lambda x: min(255, int(x * 1.03)))
    b = b.point(lambda x: int(x * 0.97))
    img = Image.merge("RGB", (r, g, b))

    # 2. Contrast boost
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.08)

    # 3. Saturation boost
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.10)

    # 4. Slight sharpening
    img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=30, threshold=3))

    # 5. Vignette
    add_vignette(img, strength=0.25)

    # Save
    img.save(output_path, quality=95)
    print(f"[PP] Saved: {output_path}")
    print(f"[PP] Size: {Path(output_path).stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    base = Path(__file__).parent
    input_file = base / "iterazione_5.png"
    output_file = base / "final_render.png"

    if not input_file.exists():
        print(f"[PP] Input not found: {input_file}")
        sys.exit(1)

    postprocess(str(input_file), str(output_file))
