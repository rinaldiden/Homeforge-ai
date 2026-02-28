# MASTERLOG — Training PBR Fotorealistico

## Regole generali scoperte

### Texture
- SEMPRE PBR reale da polyhaven.com (CC0), MAI procedurale da solo
- Set minimo 5 maps: diffuse, normal_gl, roughness, displacement, AO
- Projection: BOX 0.3, Coordinates: Generated (no UV unwrap su geometria semplice)
- Procedurale solo come micro-variazione (noise bump < 0.1 strength)

### Displacement
- **TRUE DISPLACEMENT obbligatorio** per muri in pietra (non solo bump!)
- `mat.displacement_method = 'BOTH'` → displacement reale + bump per micro-dettaglio
- Subdivision Surface: SIMPLE, render_levels 6 (NO catmull-clark che arrotonda)
- ShaderNodeDisplacement → Material Output "Displacement"
- Scale 0.04-0.045m per pietre alpinee, mai > 0.05 (deforma troppo)
- Bump aggiuntivo per dettaglio superficiale fine (str 0.6-0.7, dist 0.02)

### Giunti malta scuri
- AO con Gamma < 0.5 (crush dei darks) + Multiply sulla diffuse
- Mortar darkening: displacement invertito → ColorRamp stretto (0-0.25) → mix con quasi-nero
- Contrasto +0.22-0.25 per enfatizzare separazione pietre/giunti

### Illuminazione
- HDRI obbligatorio per render finali
- Strength: 2.0-2.5 per outdoor
- Rotazione HDRI: 30-40° per luce laterale che enfatizza ombre nei giunti
- Mai usare sky gradient per risultati finali

### Camera
- 35mm per contesto architettonico, 45-50mm per dettaglio materiale
- Vista 3/4 sempre migliore di frontale pura
- Distanza 3-4m per singolo elemento close-up, 5-6m per contesto

### Geometria
- CUBO con spessore reale, mai PLANE per muri/elementi visibili da angolo
- Bordi irregolari tramite vertex displacement (subdivide + random)
- Appoggiare sempre gli oggetti al suolo (z=0)

### Color management
- AgX view transform + Medium Contrast
- HSV per adattare texture al contesto locale
- Noise texture per variazione cromatica warm/cool su patch grandi
- Brightness/Contrast per enfatizzare profondità giunti/texture

---

## Elemento 1: Muro Misto Alpi ✅

### Riferimento: pietraeco.it "Misto Alpi"
### Texture: `castle_wall_slates` (Poly Haven CC0)
- Pietre scistose orizzontali — migliore tra 4 candidate testate
- TRUE DISPLACEMENT (0.045m scale) per rilievo 3D reale
- Scartate: broken_wall, stacked_stone_wall, rock_wall_08

### Parametri chiave
- Scale 0.75, Hue 0.505, Sat 0.92, Val 1.15, Contrast +0.25
- AO: Gamma 0.35 → Multiply (giunti molto scuri)
- Normal 2.8, Bump 0.7/0.025, Displacement 0.045/0.5
- Mortar darkening: disp invertito → ramp(0, 0.25) → nero (0.025)
- Color variation: Noise(scale 1.0) → warm HSV shift → patchy mix

### Lezioni specifiche
1. TRUE DISPLACEMENT obbligatorio — bump da solo non basta per pietre alpine
2. AO con Gamma < 0.5 per giunti neri profondi
3. Mortar darkening via displacement invertito + ColorRamp stretto
4. Noise per variazione warm/cool su patch grandi
5. Composizione 3/4 con sfondo chiaro per "foto prodotto"
6. Mai displacement > 5cm (deforma geometria)
7. 8 iterazioni necessarie per raggiungere il target

---

## Elemento 2: Tetto Piode ✅

### Texture: `castle_wall_slates` (Poly Haven)
- Pietre irregolari di dimensioni diverse — autentiche per piode
- Scartate: roof_slates_02/03 (troppo regolari, tipo tegole industriali)

### Parametri chiave
- Scale 0.8 (basso = piode grandi), Sat 0.60, Val 1.0, Contrast +0.18
- Normal 2.0, Bump 1.0/0.06
- Geometria: cubo 5.5x4x0.05m, pitch 30°

### Lezioni specifiche
1. Camera DALL'ALTO per tetti — dal basso si vede solo il muro
2. Piode = irregolari, NON usare texture regolari
3. Scale basso = pietre grandi (inverso intuitivo)
4. Saturation 0.6 per piode (grigio argento quasi monocromatico)
5. Fascia legno al bordo gronda aggiunge realismo
6. Rotazione + posizione tetto: calcolare in base alla camera

---

## Elemento 3: Struttura Tetto in Legno ✅
(Completato in sessione precedente, 3 iterazioni)

---

## Archviz Workflow Completo ✅

### Data: 2026-02-28
### Obiettivo: Casa moderna completa con workflow archviz professionale
### Risultato: 5 iterazioni, da CG a semi-fotorealistico

### Workflow eseguito:
1. **Download textures**: 4 set PBR (concrete_wall_008, wood_planks_grey, grass_path_2, concrete_floor_02) + HDRI (kloofendal_48d_partly_cloudy)
2. **Geometria**: Casa moderna 12x8m, flat roof con overhang 1m, grande vetrata frontale, cladding legno su est
3. **Materiali PBR**: concrete con weathering gradient, wood cladding, glass (IOR 1.52), paving
4. **Vegetazione procedurale**: Multi-lobe trees (5-7 icosphere), bushes con displacement clouds, 4 shade di verde
5. **HDRI + Sun**: Golden hour (elevation 35°, warm color), fill light cool, HDRI strength 1.0
6. **Camera**: 30mm, f/5.6, eye-level 3/4 view
7. **Render**: Cycles CPU 512 samples, AgX Medium Contrast, 1920x1080
8. **Post-processing PIL**: Warm grade, contrast +8%, saturation +10%, vignette, sharpening

### Lezioni nuove scoperte:
1. **grass_path_2 = MARRONE** → Serve overlay verde (RGB 0.12, 0.28, 0.08) al 65% + HSV sat 1.3
2. **Multi-lobe trees** >> singola sfera → 5-7 icosphere sovrapposte con noise displacement
3. **Micro noise bump** (scale 50-60, str 0.04) su ogni materiale PBR → rompe la perfezione CG
4. **Weathering gradient** via SeparateXYZ.Z → ColorRamp → Multiply = base scura + top sporco
5. **Window recess** (10cm) = profondità essenziale
6. **Soffit** sotto l'overhang = dettaglio cruciale per credibilità
7. **PIL post-processing** come alternativa a compositor Blender 5.0 (scene.node_tree rimosso)
8. **Fill light cool** dal lato opposto al sole → recupera dettagli nelle ombre
9. **Cono rastremato** per tronchi alberi >> cilindro dritto
10. **Subsurface Color** rimosso in Blender 5.0 → usare solo Subsurface Weight

### File prodotti:
- `chain/training/archviz_workflow/render_iter[1-5].py` — 5 script iterativi
- `chain/training/archviz_workflow/postprocess.py` — post-processing PIL
- `chain/training/archviz_workflow/iterazione_[1-5].png` — render iterativi
- `chain/training/archviz_workflow/final_render.png` — render finale post-processato
- `chain/training/archviz_workflow/LEARNED.md` — lezioni apprese
- `chain/training/archviz_workflow/materials_used.md` — materiali usati
- `chain/training/archviz_workflow/render_settings.md` — impostazioni render
