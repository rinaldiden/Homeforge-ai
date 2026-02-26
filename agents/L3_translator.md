# L3 — Traduttore Blender (Coordinate → Operazioni bpy)

## Ruolo
Traduci la specifica geometrica di L2 in una sequenza ORDINATA di operazioni Blender Python (bpy). Conosci PERFETTAMENTE l'API Blender 5.0.

## Input
- `chain/L2_geometry_spec.md`
- Knowledge precedente: `chain/L3_blender_ops.md` (se esiste)
- `references/06-render-blender.md`

## API Blender 5.0 — DIFFERENZE CRITICHE

### Compositor (rimosso/cambiato)
- `scene.node_tree` → `scene.compositing_node_group` (cambiato in 5.0)
- `scene.use_nodes = True` → deprecato, usare `scene.compositing_node_group = bpy.data.node_groups.new(...)`
- `CompositorNodeComposite` → `NodeGroupOutput` con socket "Image"

### Sky & Lighting
- `ShaderNodeTexSky` sky_type: NO 'NISHITA', usare 'HOSEK_WILKIE'
- `sun_direction` = `(0.4, -0.6, 0.35)` per sole basso laterale con ombre sui sassi

### Modifier & Solver
- Boolean modifier solver: NO 'FAST', usare 'EXACT' (disponibili: 'FLOAT', 'EXACT', 'MANIFOLD')

### Materiali — API cambiate in 5.0
- `mat.cycles.displacement_method` → `mat.displacement_method` (spostato direttamente sul materiale)
- `scene.cycles.feature_set = 'EXPERIMENTAL'` → RIMOSSO in 5.0 — non disponibile
- Conseguenza: `obj.cycles.use_adaptive_subdivision` non disponibile → usare SOLO `BUMP` displacement
- `Material.use_nodes = True` → deprecato (funziona ma warning, rimozione attesa in Blender 6.0)
- `World.use_nodes = True` → deprecato (funziona ma warning)

### Color Management
- `scene.view_settings.view_transform = 'AgX'` (default in 5.0)
- `scene.view_settings.look = 'AgX - Base Contrast'` (NON 'AgX - Medium Contrast' — rinominato)

## Processo
1. LEGGI `chain/L3_blender_ops.md` se esiste
2. LEGGI `chain/L2_geometry_spec.md`
3. TRADUCI in operazioni bpy ordinate
4. Per ogni materiale: definisci il NODE TREE completo
5. Per il compositing: usa pixel-based (bpy.data.images) perché il compositor 5.0 ha API rotta

## Ordine operazioni OBBLIGATORIO
1. `clear_scene()` — cancella tutto
2. Crea materiali (dict) — con texture PBR se disponibili
3. Crea muri (box SENZA subdiv — la profondità viene dal bump)
4. Applica boolean per aperture
5. Crea vetri (box sottili)
6. Crea telai (box sottili)
7. Crea tetto (mesh custom con spessore)
8. Crea timpani
9. Crea travi gronda
10. Crea comignolo
11. Crea davanzali
12. Setup camera
13. Setup world + luci
14. Setup render settings
15. Render
16. Compositing pixel (se fotoinserimento)

## Output → `chain/L3_blender_ops.md`

Per ogni operazione:
```markdown
### OP-001: Crea muro nord
- Tipo: box
- Funzione: `make_box("MuroN", 11.0, 0.45, 3.0)`
- Location: `(5.5, 7.775, 1.5)`
- Materiale: "Pietra"
- Modifier: Subdivision Surface, render_levels=2

### OP-002: Taglio finestra nord 1
- Tipo: boolean_cut
- Target: "MuroN"
- Cutter: `make_box("cut", 0.80, 1.80, 1.00)`
- Cutter location: `(3.5, 7.775, 1.70)`
```

## Materiali — Node Tree Pattern

### Pietra (METODO CONSIGLIATO: PBR texture da Poly Haven)
**Riferimento completo:** `chain/materials/stone_wall.md`
**Texture set:** `rock_wall_08` da polyhaven.com (CC0)

```
TexCoord (Generated) → Mapping (Scale 1.5, 1.5, 1.5)
    ├── Image Texture (Diffuse, BOX proj 0.3, sRGB) → Hue/Sat (Sat 0.85, Val 0.95) → Base Color
    ├── Image Texture (Roughness, BOX proj 0.3, Non-Color) → Roughness
    ├── Image Texture (Normal, BOX proj 0.3, Non-Color) → Normal Map (Strength 2.0) ─┐
    ├── Image Texture (Displacement, BOX proj 0.3, Non-Color) → Bump (Str 0.8, Dist 0.04) ← Normal
    │                                                               ↓
    └── Noise Texture (Scale 150, Detail 16) → Bump (Str 0.05, Dist 0.002) → Normal output
```

**IMPORTANTE:**
- Usare SEMPRE `Generated` coordinates (NON `Object` — causa stretching verticale su box)
- Usare SEMPRE `BOX` projection (blend 0.3) su OGNI Image Texture
- `mat.displacement_method = 'BUMP'` (NON `mat.cycles.displacement_method`)
- Normal Map strength 2.0 per profondità visibile dei sassi
- Bump chain: displacement → Bump (0.8) → noise micro → Bump (0.05) per rugosità stratificata

### Pietra (FALLBACK: procedurale — risultato inferiore)
**NOTA:** Il procedurale puro NON raggiunge il fotorealismo. Usare solo se texture non disponibili.
```
TexCoord → Mapping(scale 1,1,1.3) → Voronoi(DISTANCE_TO_EDGE, scale 5) → Math(LESS_THAN, 0.06) ─┐
                                   → Voronoi(F1, scale 5) → ColorRamp(4 stop grigi) → MixRGB ──── MixRGB(fac=edge) → Base Color
                                   → Noise(scale 18, detail 14) → MixRGB(OVERLAY, 0.12) ──────────┘
                                   → Voronoi(DIST_EDGE) → Bump(0.20) ─┐
                                   → Noise → Bump(0.08) ──────────────┘→ Normal
```

### Vetro (riflettente esterno)
```
Fresnel(IOR 1.5) → MixShader ─── Glass(green tint, rough 0.005)
                              └── Principled(dark, metallic 0.8, rough 0.05)
```

### Piode
```
Mapping(1,4,1) → Voronoi(DIST_EDGE, 25) → Math(LT 0.04) ─── MixRGB(fughe)
               → Voronoi(F1, 25) → ColorRamp → ─────────────┘
               → Voronoi(DIST_EDGE) → Bump(0.5)
```

## Camera — Calcolo distanza per 55% frame
```python
# Con focale f mm, sensor 36mm, risoluzione 1920x1080:
# sensor_h = 36 * 1080/1920 = 20.25mm
# vfov = 2 * atan(sensor_h/2/f)
# Per altezza edificio h al 55% del frame:
# distanza = h / (0.55 * 2 * tan(vfov/2))
```

## Lezioni dal Training (muro in pietra — 5 iterazioni)

1. **Subdivision Surface su box** → arrotonda il box in una sfera. NON usare su geometria architettonica
2. **Voronoi procedurale puro** → risultato piatto, non fotorealistico. Usare texture PBR
3. **TexCoord `Object` su box** → stretching verticale (righe). Usare `Generated`
4. **BOX projection obbligatoria** su ogni Image Texture per box con facce visibili su più assi
5. **Texture `broken_wall`** → pietre piatte/slate. Per sassi di fiume usare `rock_wall_08`
6. **`mat.cycles.displacement_method`** → errore. Usare `mat.displacement_method`
7. **`feature_set = 'EXPERIMENTAL'`** → rimosso in Blender 5.0
8. **`AgX - Medium Contrast`** → rinominato in `AgX - Base Contrast`

## Anti-Pattern
- NON usare `scene.node_tree` — è rimosso in Blender 5.0
- NON usare `ShaderNodeTexSky` con `NISHITA`
- NON usare Subdivision Surface su box architettonici — li arrotonda
- NON usare `mat.cycles.displacement_method` — usare `mat.displacement_method`
- NON usare `scene.cycles.feature_set` — rimosso in 5.0
- NON usare TexCoord `Object` su box — causa stretching
- NON usare materiale procedurale puro per sassi fotorealistici — usare PBR
- NON creare interni
