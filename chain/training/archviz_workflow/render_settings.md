# Render Settings — Archviz Workflow

## Cycles Settings
- Engine: CYCLES
- Device: CPU (GTX 1050 driver too old for CUDA/OptiX)
- Samples: 512
- Denoiser: OpenImageDenoise (built-in)
- Resolution: 1920 x 1080 (16:9)
- Color depth: 16-bit PNG

## Color Management
- View Transform: AgX
- Look: AgX - Medium Contrast (fallback: AgX - Base Contrast)
- Exposure: 0 (default)
- Gamma: 1.0

## Camera
- Focal Length: 30mm
- DOF: enabled, f/5.6, focus distance 16m
- Position: (-10, -14, 1.55) — eye level, SW 3/4 view
- Target: (0.5, 0, 1.6) — center of building, mid-height
- Clip End: 600m

## Lighting
### Sun (Key Light)
- Energy: 4.0
- Angle: 0.8° (sharp shadows)
- Rotation: elevation 35°, azimuth -55° (SW golden hour)
- Color: (1.0, 0.92, 0.78) — warm

### Fill Light
- Energy: 0.5
- Angle: 15° (soft)
- Rotation: elevation 60°, azimuth 30° (NE)
- Color: (0.85, 0.90, 1.0) — slightly cool

### HDRI
- Strength: 1.0
- Rotation Z: 155°

## Post-Processing (PIL)
- Warm color shift: R×1.03, B×0.97
- Contrast: +8%
- Saturation: +10%
- Sharpening: UnsharpMask(radius=1.5, percent=30, threshold=3)
- Vignette: strength 0.25, quadratic falloff

## Performance
- Render time: 18-22 min per frame on CPU
- Scene complexity: ~100 objects, 4 PBR materials, 1 HDRI
- With GPU (RTX 3060+): estimated 30-60 seconds
