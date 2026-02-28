# Archviz Workflow — Lessons Learned

## Date: 2026-02-28

## Overview
Full archviz training exercise: modern house with PBR materials, HDRI lighting,
procedural vegetation, and post-processing. 5 iterations to reach acceptable quality.

## Key Workflow Steps

### 1. Geometry
- Start with simple cubes, NO subdivision on architectural boxes
- Use `transform_apply(scale=True)` immediately after sizing
- Window recess (10cm deep) adds critical depth perception
- Soffit under roof overhang is essential for realism
- Plinth/foundation slab grounds the building

### 2. PBR Materials
- **ALWAYS** use PBR textures: diff + nor_gl + rough + disp (4 maps minimum)
- Use `BOX` projection (blend 0.3) on all Image Texture nodes
- Use `Generated` coordinates, NOT `Object` (avoids stretching)
- Normal map strength 2.0-3.0 for visible depth
- Bump chain: displacement texture → Bump (str 0.5) → micro noise → Bump (str 0.04)
- Micro noise (scale 50-60, detail 7) adds grain/imperfection that prevents CG look
- Weathering via vertical gradient (SeparateXYZ → Z → ColorRamp) darkens bottom/top

### 3. Grass Ground Fix
- `grass_path_2` from Poly Haven renders brown/tan by default → looks like dirt
- **FIX**: Overlay green tint (RGB 0.12, 0.28, 0.08) at factor 0.65
- Add noise-driven color variation between two green shades
- Final HSV boost: saturation 1.3, value 1.05
- This was the single biggest improvement (iter 4→5)

### 4. Vegetation
- Icosphere bushes: subdivisions=3, flatten Z to 0.45-0.55
- CRITICAL: Displace modifier with CLOUDS texture (scale 0.2, depth 5, strength 0.2*radius)
- Use 3-4 different green materials (dark/mid/light/hedge) for natural variety
- Multi-lobe trees: 5-7 overlapping icospheres at random offsets
- Cone trunk (tapered cylinder) looks better than straight cylinder
- Trees need noise displacement on crown lobes too

### 5. HDRI & Lighting
- HDRI strength 1.0-1.2 (not too bright, let sun dominate)
- Sun light energy 3.5-4.0, angle 0.8° for sharp shadows
- Golden hour: rotation ~35° elevation, warm color (1.0, 0.92, 0.78)
- Fill light (cool sun, energy 0.5) from opposite side to lift shadows
- HDRI rotation matters: position sky features for best background

### 6. Camera
- Eye-level (1.55-1.65m), 3/4 view from front-left
- Focal length 28-32mm (archviz standard)
- Slight DOF: f/5.6, focus at building center
- Frame with foreground trees for depth (but not blocking building)

### 7. Render Settings
- Cycles CPU, 512 samples, OpenImageDenoise ON
- Resolution: 1920x1080
- AgX color management, Medium Contrast look
- Render time: ~18-22 min on CPU (no GPU)

### 8. Post-Processing (PIL)
- Since Blender 5.0 removed `scene.node_tree`, use PIL/Pillow
- Warm grade: R×1.03, B×0.97
- Contrast +8%, Saturation +10%
- UnsharpMask (radius 1.5, percent 30) for subtle sharpening
- Vignette (strength 0.25, quadratic falloff)

## What Didn't Work
- `grass_path_2` texture as-is → brown dirt, NOT green grass
- Single-sphere tree crowns → obviously CG
- Flat icosphere bushes without displacement → green blobs
- Blender 5.0 compositor (`scene.node_tree`) → REMOVED, can't use
- `Subsurface Color` input → removed in Blender 5.0, use only `Subsurface Weight`
- Low sample counts (<256) → noisy, even with denoiser

## Iteration Summary
| Iter | Time | Samples | Key Change | Quality |
|------|------|---------|------------|---------|
| 1 | 13min | 256 | Basic scene, all PBR | 3/10 — flat, CG |
| 2 | 17min | 300 | Micro noise, displaced bushes | 4/10 — better textures |
| 3 | 17min | 512 | Golden hour, weathered concrete | 5/10 — good light |
| 4 | 22min | 512 | Multi-lobe trees, garden detail | 6/10 — organic trees |
| 5 | 18min | 512 | Green grass fix, post-processing | 7/10 — best result |
