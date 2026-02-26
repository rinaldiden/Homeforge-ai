# L4 — Esecutore Blender (Operazioni → Script Python)

## Ruolo
Scrivi script Python COMPLETO e FUNZIONANTE per Blender. Gestisci errori, edge cases, ordine di esecuzione. Lo script deve produrre un render PNG di qualità architettonica.

## Input
- `chain/L3_blender_ops.md`
- Knowledge precedente: `chain/L4_script.py` e `chain/L4_execution_log.md`
- Foto per compositing: `photos/site_photo.jpg`

## Due modalità

### A) SCRIPT (default)
Genera `chain/L4_script.py` eseguibile con:
```bash
blender --background --python chain/L4_script.py
```

### B) MCP LIVE
Se Blender MCP è connesso, esegui via tool calls:
- `execute_blender_code`: esegui blocchi di codice Python
- `get_scene_info`: verifica stato scena
- `screenshot`: feedback visivo

## Struttura script OBBLIGATORIA

```python
"""
HomeForge AI — Render Script
Generated: [timestamp]
Project: [nome progetto]
"""
import bpy, bmesh, math, os
from pathlib import Path
from mathutils import Vector

# === CONFIG ===
PROJECT_DIR = Path(__file__).parent.parent
PHOTOS_DIR = PROJECT_DIR / "photos"
OUTPUT_DIR = PROJECT_DIR / "output"
# ... paths

# === UTILITY ===
def clear_scene(): ...
def make_box(name, w, d, h): ...
def boolean_cut(obj, name, w, d, h, x, y, z): ...
def subdiv(obj, levels=2): ...

# === MATERIALI ===
def mat_pietra(): ...
def mat_piode(): ...
def mat_vetro(): ...
# ...

# === GEOMETRIA ===
def build_exterior(materials): ...

# === SETUP ===
def setup_camera(): ...
def setup_lighting(): ...
def setup_render(): ...

# === COMPOSITING ===
def composite_on_photo(model_png, photo_path, output_path): ...

# === MAIN ===
def main():
    print("HomeForge AI — Render")
    clear_scene()
    mats = create_materials()
    build_exterior(mats)
    setup_camera()
    setup_lighting()
    setup_render()
    render()
    composite()
    print("Done!")

if __name__ == "__main__":
    main()
```

## Checklist pre-generazione
- [ ] Tutti i box hanno dimensioni > 0
- [ ] Boolean cutter più grande dello spessore muro (T*4)
- [ ] Boolean solver = 'EXACT' (NON 'FAST')
- [ ] Nessun Subdivision Surface su box architettonici
- [ ] Camera clip_end > distanza camera-edificio
- [ ] Film transparent = True per compositing
- [ ] Output path esistente
- [ ] Nessun `scene.node_tree` (Blender 5.0)
- [ ] Nessun `NISHITA` sky type
- [ ] Nessun `mat.cycles.displacement_method` → usare `mat.displacement_method`
- [ ] Nessun `scene.cycles.feature_set` → rimosso in 5.0
- [ ] Color management: `AgX` + `AgX - Base Contrast` (NON Medium Contrast)
- [ ] Texture PBR: `Generated` coords + `BOX` projection su ogni Image Texture

## Gestione errori
```python
try:
    bpy.ops.object.modifier_apply(modifier=mod.name)
except RuntimeError as e:
    print(f"  WARN: modifier apply failed: {e}")
    # Fallback: rimuovi modifier senza applicare
    obj.modifiers.remove(mod)
```

## Compositing pixel-based (Blender 5.0 safe)
```python
def composite_on_photo(model_path, photo_path, output_path):
    """Alpha over: modello RGBA su foto RGB."""
    foto = bpy.data.images.load(str(photo_path))
    model = bpy.data.images.load(model_path)
    fw, fh = foto.size
    # Scale se necessario...
    foto_px = list(foto.pixels)
    mod_px = list(model.pixels)
    res = [0.0] * (fw * fh * 4)
    for i in range(fw * fh):
        idx = i * 4
        a = mod_px[idx+3]
        res[idx]   = mod_px[idx]  *a + foto_px[idx]  *(1-a)
        res[idx+1] = mod_px[idx+1]*a + foto_px[idx+1]*(1-a)
        res[idx+2] = mod_px[idx+2]*a + foto_px[idx+2]*(1-a)
        res[idx+3] = 1.0
    result = bpy.data.images.new("Comp", width=fw, height=fh)
    result.pixels = res
    result.filepath_raw = output_path
    result.file_format = 'PNG'
    result.save()
```

## Execution Log → `chain/L4_execution_log.md`
```markdown
# L4 — Execution Log
## Timestamp: [ISO 8601]
## Script: chain/L4_script.py
## Command: blender --background --python chain/L4_script.py

## Result
- Status: [SUCCESS/FAILED]
- Render time: [seconds]
- Output: [path]
- Warnings: [list]
- Errors: [list]

## Changes from previous
- [cosa è cambiato e perché]
```

## Pattern PBR Texture (da training muro in pietra)

### Caricamento texture Poly Haven
```python
TEX_DIR = Path(__file__).parent / "materials" / "textures"

# Ogni Image Texture deve usare BOX projection + Generated coords
tex = ns.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(str(TEX_DIR / "rock_wall_08_diff_2k.jpg"))
tex.image.colorspace_settings.name = 'sRGB'   # 'Non-Color' per rough/normal/disp
tex.projection = 'BOX'
tex.projection_blend = 0.3
```

### Bump chain a 2 livelli (profondità realistica)
```python
# Livello 1: displacement texture → Bump (profondità giunti e sassi)
bump = ns.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.8
bump.inputs["Distance"].default_value = 0.04  # 4cm
lk.new(tex_disp.outputs["Color"], bump.inputs["Height"])
lk.new(normal_map.outputs["Normal"], bump.inputs["Normal"])

# Livello 2: noise micro → Bump (rugosità singolo sasso)
bump2 = ns.new("ShaderNodeBump")
bump2.inputs["Strength"].default_value = 0.05
bump2.inputs["Distance"].default_value = 0.002
lk.new(noise_micro.outputs["Fac"], bump2.inputs["Height"])
lk.new(bump.outputs["Normal"], bump2.inputs["Normal"])

lk.new(bump2.outputs["Normal"], bsdf.inputs["Normal"])
```

### Setup render Cycles (Blender 5.0 safe)
```python
scene.render.engine = 'CYCLES'
scene.cycles.samples = 512
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Base Contrast'

# GPU con fallback CPU
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    prefs.get_devices()
    for d in prefs.devices: d.use = True
    scene.cycles.device = 'GPU'
except:
    scene.cycles.device = 'CPU'
```

### Texture disponibili (già scaricate)

**Muro pietra (rock_wall_08):**
- `chain/materials/textures/rock_wall_08_diff_2k.jpg` — diffuse/color (sRGB)
- `chain/materials/textures/rock_wall_08_nor_gl_2k.jpg` — normal map OpenGL (Non-Color)
- `chain/materials/textures/rock_wall_08_rough_2k.jpg` — roughness (Non-Color)
- `chain/materials/textures/rock_wall_08_disp_2k.png` — displacement (Non-Color)
- Parametri completi: `chain/materials/stone_wall.md`

**Piode tetto (patterned_slate_tiles):**
- `chain/materials/textures/patterned_slate_tiles_diff_2k.jpg` — diffuse (sRGB)
- `chain/materials/textures/patterned_slate_tiles_nor_gl_2k.jpg` — normal (Non-Color)
- `chain/materials/textures/patterned_slate_tiles_rough_2k.jpg` — roughness (Non-Color)
- `chain/materials/textures/patterned_slate_tiles_disp_2k.png` — displacement (Non-Color)

**Legno travi (weathered_brown_planks):**
- `chain/materials/textures/weathered_brown_planks_diff_2k.jpg` — diffuse (sRGB)
- `chain/materials/textures/weathered_brown_planks_nor_gl_2k.jpg` — normal (Non-Color)
- `chain/materials/textures/weathered_brown_planks_rough_2k.jpg` — roughness (Non-Color)
- `chain/materials/textures/weathered_brown_planks_disp_2k.png` — displacement (Non-Color)

**Rame brunito:** procedurale (no texture esterne)

- Parametri tetto completi: `chain/materials/roof_piode.md`

## Lezioni dal Training (muro in pietra — 5 iterazioni)

| Iterazione | Problema | Soluzione |
|------------|----------|-----------|
| 1 | Subdiv livello 3 su box → sfera | NON usare Subdivision Surface su box |
| 1 | `mat.cycles.displacement_method` → errore | Usare `mat.displacement_method` |
| 1 | `feature_set = 'EXPERIMENTAL'` → errore | Rimosso in 5.0, usare BUMP only |
| 1 | `AgX - Medium Contrast` → errore | Usare `AgX - Base Contrast` |
| 2 | Voronoi procedurale → piatto | Texture PBR molto superiori |
| 3 | TexCoord Object su box → stretching | Usare `Generated` coords |
| 4 | broken_wall texture → pietre piatte | Usare `rock_wall_08` per sassi fiume |
| 5 | Risultato fotorealistico | Parametri finali in stone_wall.md |

**Training tetto (6 iterazioni):**

| Iterazione | Problema | Soluzione |
|------------|----------|-----------|
| 1 | slab_tiles = crazy paving | Usare `patterned_slate_tiles` per piode |
| 2 | Travi troppo piccole, texture piode enorme | Sezione 22×26cm, scala texture 3.0 |
| 3 | Rame verde turchese brillante | Colori più scuri nel ramp (parziale) |
| 4-5 | Rame ancora verde anche con colori scurissimi | AgX + metallic alto amplifica riflessi cielo |
| 6 | Rame brunito (SOLUZIONE) | Toni bruni, metallic 0.95, NO verde-rame |

## Anti-Pattern
- NON generare script parziali — deve essere COMPLETO e autonomo
- NON usare path relativi — usa Path(__file__) o path assoluti
- NON dimenticare `OUTPUT_DIR.mkdir(parents=True, exist_ok=True)`
- NON lasciare print() senza informazione utile
- NON usare `mat.cycles.displacement_method` → `mat.displacement_method`
- NON usare `scene.cycles.feature_set` → rimosso in Blender 5.0
- NON usare Subdivision Surface su box architettonici
- NON usare TexCoord `Object` su box → usare `Generated` + `BOX` projection
- NON usare materiale procedurale puro per sassi — usare texture PBR da Poly Haven
