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

## Elemento 3-7: SOSPESI
Training interrotto — focus su muro Misto Alpi da riferimento pietraeco.it
