# L3 — Operazioni Blender (bpy)
## Timestamp: 2026-02-26T10:02:00+01:00
## Input: chain/L2_geometry_spec.md
## Target: Blender 5.0 Python API

## Ordine esecuzione

### OP-001: Clear scene
- Tipo: utility
- Funzione: `clear_scene()` — elimina tutti gli oggetti, materiali, mesh
- Codice:
```python
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in bpy.data.meshes: bpy.data.meshes.remove(m)
for m in bpy.data.materials: bpy.data.materials.remove(m)
```

### OP-002: Crea materiale Pietra
- Tipo: material
- Nome: "Pietra"
- Node tree:
  1. TexCoord → Mapping (scale 1.0, 1.0, 1.3)
  2. Mapping → Voronoi Texture (feature: DISTANCE_TO_EDGE, scale: 5.0) → Math (LESS_THAN, threshold: 0.06) = bordi_malta
  3. Mapping → Voronoi Texture (feature: F1, scale: 5.0) → ColorRamp (4 stop: #7A7A6E @0.0, #8C8C7A @0.33, #6B6B5E @0.66, #A0998A @1.0) = colore_sassi
  4. Mapping → Noise Texture (scale: 18, detail: 14) → MixRGB (OVERLAY, fac: 0.12, input1: colore_sassi) = colore_variato
  5. MixRGB (fac: bordi_malta, input1: colore_variato, input2: #B0ADA5 malta) = base_color
  6. base_color → Principled BSDF .Base Color
  7. Mapping → Voronoi (DISTANCE_TO_EDGE, scale: 5.0) → Bump (strength: 0.20, distance: 0.02) → Normal chain
  8. Mapping → Noise (scale: 22, detail: 12) → Bump (strength: 0.08) → chain con bump precedente
  9. Principled BSDF: Roughness = 0.80, Specular IOR Level = 0.3

### OP-003: Crea materiale Vetro
- Tipo: material
- Nome: "Vetro"
- Node tree:
  1. Fresnel (IOR: 1.5) → fac per MixShader
  2. Glass BSDF (color: #E8F0E8, roughness: 0.005, IOR: 1.5)
  3. Principled BSDF (color: #1A2A1A, metallic: 0.8, roughness: 0.05)
  4. MixShader (fac: Fresnel, shader1: Glass, shader2: Principled)

### OP-004: Crea materiale Piode
- Tipo: material
- Nome: "Piode"
- Node tree:
  1. TexCoord → Mapping (scale: 1, 4, 1)
  2. Mapping → Voronoi (DISTANCE_TO_EDGE, scale: 25) → Math (LESS_THAN, 0.04) = bordi_fuga
  3. Mapping → Voronoi (F1, scale: 25) → ColorRamp (3 stop: #4A4A42 @0.0, #5E5E52 @0.5, #3A3A32 @1.0) = colore_piode
  4. MixRGB (fac: bordi_fuga, input1: colore_piode, input2: #3A3A3A fughe) → Principled.Base Color
  5. Mapping → Voronoi (DISTANCE_TO_EDGE, scale: 25) → Bump (strength: 0.5)
  6. Roughness: 0.70

### OP-005: Crea materiale Legno Scuro
- Tipo: material
- Nome: "LegnoScuro"
- Principled BSDF: Base Color #3A2A1A, Roughness 0.50, Specular IOR Level 0.3

### OP-006: Crea materiale Porta
- Tipo: material
- Nome: "Porta"
- Principled BSDF: Base Color #2A1A0A, Roughness 0.45, Specular IOR Level 0.25

### OP-010: Crea Muro Sud (M1)
- Tipo: box
- Funzione: `make_box("MuroSud", 11.0, 0.45, 3.0)`
- Location: (5.50, 0.225, 1.50)
- Materiale: "Pietra"
- Modifier: Subdivision Surface, render_levels=2, viewport_levels=1

### OP-011: Crea Muro Nord (M2)
- Tipo: box
- Funzione: `make_box("MuroNord", 11.0, 0.45, 3.0)`
- Location: (5.50, 7.775, 1.50)
- Materiale: "Pietra"
- Modifier: Subdivision Surface, render_levels=2, viewport_levels=1

### OP-012: Crea Muro Ovest (M3)
- Tipo: box
- Funzione: `make_box("MuroOvest", 0.45, 8.0, 3.0)`
- Location: (0.225, 4.0, 1.50)
- Materiale: "Pietra"
- Modifier: Subdivision Surface, render_levels=2, viewport_levels=1

### OP-013: Crea Muro Est (M4)
- Tipo: box
- Funzione: `make_box("MuroEst", 0.45, 8.0, 3.0)`
- Location: (10.775, 4.0, 1.50)
- Materiale: "Pietra"
- Modifier: Subdivision Surface, render_levels=2, viewport_levels=1

### OP-020: Boolean — Vetrata SW lato sud (A1)
- Tipo: boolean_cut
- Target: "MuroSud"
- Cutter: `make_box("cut_A1", 2.40, 1.80, 2.40)`
- Cutter location: (1.20, 0.225, 1.60)
- Operation: DIFFERENCE

### OP-021: Boolean — Vetrata SW lato ovest (A2)
- Tipo: boolean_cut
- Target: "MuroOvest"
- Cutter: `make_box("cut_A2", 1.80, 2.40, 2.40)`
- Cutter location: (0.225, 1.20, 1.60)
- Operation: DIFFERENCE

### OP-022: Boolean — Finestra sud centrale (A3)
- Tipo: boolean_cut
- Target: "MuroSud"
- Cutter: `make_box("cut_A3", 1.20, 1.80, 1.40)`
- Cutter location: (7.00, 0.225, 1.60)
- Operation: DIFFERENCE

### OP-023: Boolean — Porta ingresso (A4)
- Tipo: boolean_cut
- Target: "MuroSud"
- Cutter: `make_box("cut_A4", 1.00, 1.80, 2.20)`
- Cutter location: (4.50, 0.225, 1.10)
- Operation: DIFFERENCE

### OP-024: Boolean — Finestra ovest (A5)
- Tipo: boolean_cut
- Target: "MuroOvest"
- Cutter: `make_box("cut_A5", 1.80, 1.00, 1.20)`
- Cutter location: (0.225, 5.50, 1.50)
- Operation: DIFFERENCE

### OP-025: Boolean — Finestra est 1 (A6)
- Tipo: boolean_cut
- Target: "MuroEst"
- Cutter: `make_box("cut_A6", 1.80, 1.00, 1.20)`
- Cutter location: (10.775, 3.00, 1.50)
- Operation: DIFFERENCE

### OP-026: Boolean — Finestra est 2 (A7)
- Tipo: boolean_cut
- Target: "MuroEst"
- Cutter: `make_box("cut_A7", 1.80, 1.00, 1.20)`
- Cutter location: (10.775, 7.00, 1.50)
- Operation: DIFFERENCE

### OP-027: Boolean — Finestra nord 1 (A8)
- Tipo: boolean_cut
- Target: "MuroNord"
- Cutter: `make_box("cut_A8", 0.80, 1.80, 1.00)`
- Cutter location: (3.50, 7.775, 1.70)
- Operation: DIFFERENCE

### OP-028: Boolean — Finestra nord 2 (A9)
- Tipo: boolean_cut
- Target: "MuroNord"
- Cutter: `make_box("cut_A9", 0.80, 1.80, 1.00)`
- Cutter location: (7.50, 7.775, 1.70)
- Operation: DIFFERENCE

### OP-029: Applica tutti i modifier (subdiv + boolean)
- Per ogni muro: applica subdivision, poi applica tutti i boolean in ordine
- Fallback: se apply fallisce, rimuovi modifier senza applicare

### OP-030: Crea Vetro SW sud (V1)
- Tipo: box
- Funzione: `make_box("VetroSWsud", 2.40, 0.03, 2.40)`
- Location: (1.20, 0.02, 1.60)
- Materiale: "Vetro"

### OP-031: Crea Vetro SW ovest (V2)
- Tipo: box
- Funzione: `make_box("VetroSWovest", 0.03, 2.40, 2.40)`
- Location: (0.02, 1.20, 1.60)
- Materiale: "Vetro"

### OP-032: Crea Vetro finestra sud (V3)
- Tipo: box
- Funzione: `make_box("VetroFinSud", 1.20, 0.03, 1.40)`
- Location: (7.00, 0.02, 1.60)
- Materiale: "Vetro"

### OP-033: Crea Vetro finestra ovest (V4)
- Tipo: box
- Funzione: `make_box("VetroFinOvest", 0.03, 1.00, 1.20)`
- Location: (0.02, 5.50, 1.50)
- Materiale: "Vetro"

### OP-034-037: Vetri finestre est e nord
- V5 (est 1): `make_box("VetroEst1", 0.03, 1.00, 1.20)` @ (10.98, 3.0, 1.5)
- V6 (est 2): `make_box("VetroEst2", 0.03, 1.00, 1.20)` @ (10.98, 7.0, 1.5)
- V7 (nord 1): `make_box("VetroNord1", 0.80, 0.03, 1.00)` @ (3.5, 7.98, 1.7)
- V8 (nord 2): `make_box("VetroNord2", 0.80, 0.03, 1.00)` @ (7.5, 7.98, 1.7)

### OP-040: Crea Porta (pannello solido)
- Tipo: box
- Funzione: `make_box("Porta", 1.00, 0.08, 2.20)`
- Location: (4.50, 0.04, 1.10)
- Materiale: "Porta"

### OP-041-047: Crea telai finestre (solo finestre normali, NO vetrata angolo)
- Per ogni finestra: 4 profili (top, bot, sx, dx) in LegnoScuro, sezione 0.06 × 0.06

### OP-050: Crea tetto (mesh custom)
- Tipo: mesh_custom
- Vertici esterni: RE1(-0.40,-0.40,3.00), RE2(11.40,-0.40,3.00), RE3(11.40,5.50,4.80), RE4(-0.40,5.50,4.80), RE5(-0.40,8.40,3.00), RE6(11.40,8.40,3.00)
- Vertici interni: RI1(-0.40,-0.40,2.82), RI2(11.40,-0.40,2.82), RI3(11.40,5.50,4.62), RI4(-0.40,5.50,4.62), RI5(-0.40,8.40,2.82), RI6(11.40,8.40,2.82)
- Facce: 10 facce (2 falde ext + 2 falde int + 4 bordi laterali + 2 bordi gronda)
- Materiale: "Piode"
- Smooth shading: NO (facce piatte)

### OP-051: Crea Timpano Ovest
- Tipo: mesh_custom (prisma triangolare)
- Vertici: (0.225, 0, 3.0), (0.225, 8.0, 3.0), (0.225, 5.5, 4.8), (0.45, 0, 3.0), (0.45, 8.0, 3.0), (0.45, 5.5, 4.8)
- Nota: spessore T/2 = 0.225, sovrapposto al muro ovest in alto
- Materiale: "Pietra"

### OP-052: Crea Timpano Est
- Tipo: mesh_custom
- Come OP-051 ma specchiato: X = 10.55 e 10.775
- Materiale: "Pietra"

### OP-060: Crea Travi gronda SUD
- Tipo: loop di box
- Per i da 0 a 17:
  - x = 0.30 + i * 0.60
  - `make_box(f"TraveSud_{i}", 0.15, 0.80, 0.20)`
  - Location: (x, -0.20, 2.90)
  - Materiale: "LegnoScuro"

### OP-061: Crea Travi gronda NORD
- Tipo: loop di box
- Per i da 0 a 17:
  - x = 0.30 + i * 0.60
  - `make_box(f"TraveNord_{i}", 0.15, 0.80, 0.20)`
  - Location: (x, 8.20, 2.90)
  - Materiale: "LegnoScuro"

### OP-070: Crea Comignolo base
- Tipo: box
- Funzione: `make_box("ComignoloBase", 0.60, 0.60, 1.00)`
- Location: (5.50, 5.50, 5.30)
- Materiale: "Pietra"

### OP-071: Crea Comignolo cappello
- Tipo: box
- Funzione: `make_box("ComignoloCapp", 0.80, 0.80, 0.10)`
- Location: (5.50, 5.50, 5.90)
- Materiale: "Pietra"

### OP-080: Setup Camera
- Tipo: camera_setup
- Posizione: (5.50, -16.00, 1.60)
- Target: (5.50, 4.00, 2.00)
- Focale: 35 mm
- Sensor: 36 mm
- Clip end: 100
- Metodo: `camera.location = ...`, poi `constraint TRACK_TO` su Empty al target

### OP-081: Setup World + Lighting
- Tipo: world_setup
- Sky: ShaderNodeTexSky, sky_type='HOSEK_WILKIE', turbidity=3.0, sun_direction=(0.5, 0.6, 0.7)
- Background strength: 1.5
- Sun lamp: energy=3.0, angle=0.02, direction=(-0.3, 0.4, -0.8)
- Area light (fill): energy=50, size=5, position=(0, -8, 6)

### OP-082: Setup Render
- Tipo: render_setup
- Engine: CYCLES
- Device: GPU (CUDA fallback CPU)
- Samples: 256
- Denoising: True
- Resolution: 1920 × 1080
- Film transparent: True
- Output format: PNG RGBA
- Output path: `PROJECT_DIR / "output" / "render_model.png"`

### OP-090: Render
- Tipo: render
- `bpy.ops.render.render(write_still=True)`
- Salva in: output/render_model.png

### OP-091: Compositing pixel-based
- Tipo: composite
- Funzione: `composite_on_photo(render_model_path, foto_path, output_path)`
- Input foto: photos/site_photo.jpg (oppure foto sorgente specificata)
- Input modello: output/render_model.png
- Output: output/1_render.png
- Metodo: pixel-level alpha over (bpy.data.images, NO scene.node_tree)
