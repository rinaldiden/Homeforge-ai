# Stone Wall Material — Parametri finali

## Tipo: PBR texture-based (Poly Haven CC0)
## Texture set: `rock_wall_08` da polyhaven.com
## Preview: `stone_wall_preview.png`

## Texture files (2K)
| Map | File | Colorspace |
|-----|------|------------|
| Diffuse | `textures/rock_wall_08_diff_2k.jpg` | sRGB |
| Normal (OpenGL) | `textures/rock_wall_08_nor_gl_2k.jpg` | Non-Color |
| Roughness | `textures/rock_wall_08_rough_2k.jpg` | Non-Color |
| Displacement | `textures/rock_wall_08_disp_2k.png` | Non-Color |

## Node tree

```
TexCoord (Generated) → Mapping (Scale 1.5, 1.5, 1.5)
    ├── Image Texture (Diffuse, BOX proj 0.3) → Hue/Sat (Sat 0.85, Val 0.95) → Base Color
    ├── Image Texture (Roughness, BOX proj 0.3) → Roughness
    ├── Image Texture (Normal, BOX proj 0.3) → Normal Map (Strength 2.0) ─┐
    ├── Image Texture (Displacement, BOX proj 0.3) → Bump (Str 0.8, Dist 0.04) ← Normal Map
    │                                                       ↓
    └── Noise Texture (Scale 150, Detail 16) → Bump (Str 0.05, Dist 0.002) → Normal output
```

## Parametri chiave

### Projection
- Tipo: **BOX** (evita stretching su facce laterali)
- Blend: **0.3** (transizione morbida tra le facce)
- Coordinate: **Generated** (funziona senza UV unwrap)

### Color correction
- Hue/Saturation/Value: Sat 0.85, Val 0.95
- Scopo: desatura leggermente e scurisce per match con sasso alpino reale

### Normal Map
- Strength: **2.0** (doppio del default per profondità visibile)

### Bump chain (2 livelli)
1. Displacement map → Bump: Strength **0.8**, Distance **0.04** (profondità giunti e sassi)
2. Noise micro → Bump: Strength **0.05**, Distance **0.002** (rugosità superficie singolo sasso)

### Displacement method
- `BUMP` (non BOTH — feature_set EXPERIMENTAL non disponibile in Blender 5.0)

## Lezioni apprese durante il training

### Iterazione 1
- **Errore:** Subdivision Surface livello 3 su un box → lo arrotonda in una palla
- **Fix:** NON usare subdiv sul box del muro

### Iterazione 2
- **Errore:** Procedurale puro con Voronoi → risultato piatto, malta troppo larga, colori uniformi
- **Conclusione:** Voronoi DISTANCE_TO_EDGE da solo non basta per fotorealismo

### Iterazione 3
- **Errore:** TexCoord Object su un box → stretching verticale (righe)
- **Fix:** Usare `Generated` coordinates + `BOX` projection su ogni Image Texture

### Iterazione 4 (v4 — broken_wall)
- **Buono:** Sassi visibili, giunti realistici
- **Problema:** Pietre troppo piatte (slate), non rotonde come sassi di fiume

### Iterazione 5 (v5 — rock_wall_08)
- **Risultato:** Fotorealistico. Sassi irregolari con profondità, malta visibile, ombre naturali.
- **Note:** Leggermente scuro/uniforme, potrebbe beneficiare di +10% luminosità

## API Blender 5.0 — Fix scoperti durante training
- `mat.cycles.displacement_method` → `mat.displacement_method`
- `scene.cycles.feature_set = 'EXPERIMENTAL'` → RIMOSSO in 5.0
- `AgX - Medium Contrast` → `AgX - Base Contrast` (nomi look cambiati)
- `obj.cycles.use_adaptive_subdivision` → non disponibile senza EXPERIMENTAL

## Fonti texture
- Poly Haven: https://polyhaven.com/a/rock_wall_08
- Licenza: CC0 (public domain, uso libero)
- Alternativa testata: `broken_wall` (buono per pietre piatte/slate)
