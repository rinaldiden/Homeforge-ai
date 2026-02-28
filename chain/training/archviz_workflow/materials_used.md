# Materials Used — Archviz Workflow Training

## PBR Texture Sets (Poly Haven CC0, 2K JPG)

### 1. concrete_wall_008
- Source: https://polyhaven.com/a/concrete_wall_008
- Maps: diff, nor_gl, rough, disp
- Usage: Main walls (concrete), with weathering gradient
- Settings: scale 1.5, sat 0.72, val 0.83, normal 3.0, bump 0.55

### 2. wood_planks_grey
- Source: https://polyhaven.com/a/wood_planks_grey
- Maps: diff, nor_gl, rough, disp
- Usage: Wood cladding on east wall and front-right segment
- Settings: scale (2, 0.6, 2), sat 0.78, val 0.72, normal 2.5, bump 0.5

### 3. grass_path_2
- Source: https://polyhaven.com/a/grass_path_2
- Maps: diff, nor_gl, rough, disp
- Usage: Ground plane (with green overlay fix)
- Settings: scale 7, green tint overlay at 0.65, sat 1.3
- NOTE: Renders brown without green overlay! Must apply color correction.

### 4. concrete_floor_02
- Source: https://polyhaven.com/a/concrete_floor_02
- Maps: diff, nor_gl, rough, disp
- Usage: Paving area, entry steps
- Settings: scale 2.5, sat 0.68, val 0.80, normal 2.0, bump 0.35

## HDRI
- kloofendal_48d_partly_cloudy_2k.hdr
- Source: https://polyhaven.com/a/kloofendal_48d_partly_cloudy
- Strength: 1.0, Rotation Z: 155°

## Procedural Materials (no textures)
- RoofDark: (0.04, 0.04, 0.04), rough 0.60
- DarkFrame: (0.02, 0.02, 0.02), rough 0.28, metallic 0.92
- ConcreteSlab: (0.52, 0.50, 0.47), rough 0.75
- Soffit: (0.80, 0.78, 0.76), rough 0.85
- Gravel: (0.45, 0.42, 0.38), rough 0.95
- Glass: transmission 1.0, IOR 1.52, rough 0.003, slight green tint
- Foliage (4 shades): dark/mid/light/hedge greens, subsurface 0.12
- Bark: (0.08, 0.05, 0.02), rough 0.95
