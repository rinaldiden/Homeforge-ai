# Strategia Materiali — PBR vs Procedurale

## Risultato del Confronto

### Muro di pietra
| Aspetto | Procedurale (Voronoi) | PBR (rock_wall_08) |
|---------|----------------------|---------------------|
| Realismo | 2/10 — pattern matematico visibile | 8/10 — pietre irregolari naturali |
| Profondità | 1/10 — completamente piatto | 8/10 — bump + normal map |
| Colore | 3/10 — uniforme, innaturale | 7/10 — variazione naturale |
| Giunti/malta | 2/10 — troppo larghi/geometrici | 8/10 — realistici, sottili |
| Verdetto | **INUTILIZZABILE** per fotorealismo | **BUONO** — usabile come base |

### Tetto piode
| Aspetto | Procedurale (Voronoi) | PBR (castle_wall_slates) |
|---------|----------------------|--------------------------|
| Realismo | 2/10 — celle Voronoi visibili | 7/10 — lastre di pietra reali |
| Profondità | 1/10 — piatto | 7/10 — bump sulle lastre |
| Colore | 3/10 — "malta" arancione innaturale | 7/10 — grigio ardesia naturale |
| Verdetto | **INUTILIZZABILE** | **BUONO** — serve iterazione fine |

### Travi legno
| Aspetto | Procedurale (Noise) | PBR (weathered_brown_planks) |
|---------|---------------------|------------------------------|
| Realismo | 4/10 — generic wood | 7/10 — venatura reale |
| Verdetto | **MEDIOCRE** | **BUONO** |

### HDRI vs Sky gradient
| Aspetto | Sky gradient (Hosek-Wilkie) | HDRI (alps_field) |
|---------|---------------------------|---------------------|
| Luce | 4/10 — uniforme, piatta | 8/10 — sole reale, ombre direzionali |
| Sfondo | 3/10 — gradiente blu generico | 9/10 — montagne, prato, villaggio |
| Verdetto | **Solo per test rapidi** | **OBBLIGATORIO per render finali** |

---

## REGOLA DEFINITIVA PER L4

### Regola 1: SEMPRE texture PBR reali
Per qualsiasi materiale fotorealistico, L4 DEVE:
1. Scaricare texture PBR 2K da polyhaven.com (API gratuita, CC0)
2. Set minimo: **diffuse + normal + roughness + displacement + AO** (5 maps)
3. Usare Image Texture con projection BOX e blend 0.3
4. Usare Generated coordinates (no UV unwrap necessario su geometria semplice)

### Regola 2: Procedurale SOLO come variazione aggiuntiva
Il procedurale NON deve mai essere il materiale base. Può essere usato SOLO per:
- Micro-bump aggiuntivo (Noise Texture → Bump, strength < 0.1)
- Variazione colore sottile (Noise → Mix con fattore < 0.1)
- Sporco/weathering (Noise → overlay molto leggero)

### Regola 3: SEMPRE HDRI per render finali
- Scaricare HDRI 2K da polyhaven.com appropriato per il contesto
- Per Ca' del Papa: `alps_field` o simili HDRI alpini
- Strength HDRI: 1.5-2.0 per luce naturale outdoor
- Mai usare sky gradient per render finali

### Regola 4: Color correction per contesto locale
- Pietra Valtellina: desaturare (sat 0.7-0.8), schiarire (val 1.2-1.4)
- Legno travi: leggera desaturazione (sat 0.85-0.95)
- Normal map strength: 1.5-2.0 (raddoppiare il default)
- Bump displacement: strength 0.5-0.8, distance 0.02-0.05

### Regola 5: Render settings
- Cycles, 512 samples (256 per test rapidi)
- Denoising: ON
- Color management: AgX
- Resolution: 1920x1080 minimo

---

## Texture Library (Poly Haven CC0)

| Materiale | Asset ID | Uso |
|-----------|----------|-----|
| Muro pietra | `rock_wall_08` | Muratura esterna/interna |
| Piode tetto | `castle_wall_slates` | Copertura tetto in piode |
| Travi legno | `weathered_brown_planks` | Travi, architrave, bonde |
| Alt. muro | `broken_wall` | Pietre piatte/slate |
| Alt. tetto | `slab_tiles` | Tegole piatte alternative |
| HDRI | `alps_field` | Ambiente alpino |

## Come scaricare da Poly Haven (per L4)

```python
# API endpoints
# Lista assets: https://api.polyhaven.com/assets?t=textures&c=wall
# File info: https://api.polyhaven.com/files/{asset_id}
# Download diretto:
#   Texture: https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/{id}/{id}_{map}_2k.jpg
#   HDRI: https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/{id}_2k.hdr
# Maps: diff, nor_gl, rough, disp (png), ao, arm
```

## Lezioni apprese

1. **Subdivision Surface su box** → lo arrotonda. NON usare per muri.
2. **TexCoord Object su box** → stretching. Usare Generated + BOX projection.
3. **EXPERIMENTAL feature_set** → rimosso in Blender 5.0, no adaptive subdivision.
4. **AgX look names** → in 5.0: `AgX - Base Contrast` (non Medium)
5. **mat.displacement_method** → non `mat.cycles.displacement_method` in 5.0
6. **AO map multiply** → usare ShaderNodeMix con RGBA/MULTIPLY, fattore 1.0
