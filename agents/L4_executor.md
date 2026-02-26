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
- [ ] Ordine: subdiv → boolean apply → materiale
- [ ] Camera clip_end > distanza camera-edificio
- [ ] Film transparent = True per compositing
- [ ] Output path esistente
- [ ] Nessun `scene.node_tree` (Blender 5.0)
- [ ] Nessun `NISHITA` sky type

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

## Anti-Pattern
- NON generare script parziali — deve essere COMPLETO e autonomo
- NON usare path relativi — usa Path(__file__) o path assoluti
- NON dimenticare `OUTPUT_DIR.mkdir(parents=True, exist_ok=True)`
- NON lasciare print() senza informazione utile
