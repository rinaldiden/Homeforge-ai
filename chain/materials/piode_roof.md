# Piode Roof Material — Parametri finali

## Tipo: PBR texture-based (Poly Haven CC0)
## Texture set: `castle_wall_slates` da polyhaven.com
## Preview: `piode_roof_PBR_preview.png`

## Texture files (2K)
| Map | File | Colorspace |
|-----|------|------------|
| Diffuse | `textures/castle_wall_slates_diff_2k.jpg` | sRGB |
| Normal (OpenGL) | `textures/castle_wall_slates_nor_gl_2k.jpg` | Non-Color |
| Roughness | `textures/castle_wall_slates_rough_2k.jpg` | Non-Color |
| Displacement | `textures/castle_wall_slates_disp_2k.png` | Non-Color |
| AO | `textures/castle_wall_slates_ao_2k.jpg` | Non-Color |

## Node tree

```
TexCoord (Generated) → Mapping (Scale 2.0, 2.0, 2.0)
    ├── Image Texture (Diffuse, BOX proj 0.3)  ─┐
    ├── Image Texture (AO, BOX proj 0.3)        ─┤→ Mix (MULTIPLY, Factor 1.0)
    │                                              → Hue/Sat (Sat 0.7, Val 1.15) → Base Color
    ├── Image Texture (Roughness, BOX proj 0.3) → Roughness
    ├── Image Texture (Normal, BOX proj 0.3) → Normal Map (Strength 2.0)
    └── Image Texture (Displacement, BOX proj 0.3) → Bump (Str 0.6, Dist 0.03) → Normal
```

## Parametri chiave

### Projection
- Tipo: **BOX** (evita stretching)
- Blend: **0.3**
- Coordinate: **Generated**
- Scale: **2.0** (piode più grandi della texture base)

### Color correction
- Hue/Saturation/Value: Sat 0.7, Val 1.15
- Scopo: piode grigie, leggermente desaturate

### Displacement method
- `BUMP` (no EXPERIMENTAL in Blender 5.0)

## Travi legno

### Texture: `weathered_brown_planks` (Poly Haven CC0)
- Scale: (1.0, 3.0, 1.0) — allungato lungo l'asse del trave
- Sat 0.9, Val 1.1
- Stesse impostazioni BOX/Generated

## Alternative testate
- `slab_tiles`: buono per tegole piatte regolari, meno adatto per piode irregolari
- `patterned_slate_tiles`: pattern troppo regolare per piode tradizionali

## Fonti
- Poly Haven: https://polyhaven.com/a/castle_wall_slates
- Licenza: CC0 (public domain)
