# Roof Piode + Legno + Rame — Parametri finali

## Tipo: Tetto alpino con piode, travi legno scuro, lattoneria rame brunito
## Preview: `roof_piode_preview.png`

## Componenti

### 1. Piode (copertura in lastre di pietra)
- **Texture set:** `patterned_slate_tiles` da polyhaven.com (CC0)
- **Aspetto:** Lastre grigio scuro irregolari con giunti, superficie ruvida

| Map | File | Colorspace |
|-----|------|------------|
| Diffuse | `textures/patterned_slate_tiles_diff_2k.jpg` | sRGB |
| Normal (GL) | `textures/patterned_slate_tiles_nor_gl_2k.jpg` | Non-Color |
| Roughness | `textures/patterned_slate_tiles_rough_2k.jpg` | Non-Color |
| Displacement | `textures/patterned_slate_tiles_disp_2k.png` | Non-Color |

**Node tree:**
```
TexCoord (Generated) → Mapping (Scale 3,3,3 — Rot Z 90°)
    ├── Image Texture (Diffuse, BOX 0.3) → Hue/Sat (Sat 0.55, Val 0.70) → Base Color
    ├── Image Texture (Roughness, BOX 0.3) → Roughness
    ├── Image Texture (Normal, BOX 0.3) → Normal Map (Str 2.5) ─┐
    ├── Image Texture (Displacement, BOX 0.3) → Bump (Str 1.0, Dist 0.05) ← Normal
    │                                                    ↓
    └── Noise (Scale 100, Detail 12) → Bump (Str 0.04, Dist 0.001) → Normal output
```

**Parametri chiave:**
- Displacement method: `BUMP`
- Proiezione: `BOX` (blend 0.3) su ogni Image Texture
- Coordinate: `Generated`
- Rotazione mapping Z: 90° per allineare le lastre orizzontalmente
- Hue/Sat: Sat 0.55, Val 0.70 (molto desaturato e scuro per piode alpine)
- Normal Map strength: 2.5 (molto forte per profondità lastre)
- Bump chain: displacement (Str 1.0, Dist 0.05) + noise micro (Str 0.04, Dist 0.001)

---

### 2. Legno Travi (struttura portante)
- **Texture set:** `weathered_brown_planks` da polyhaven.com (CC0)
- **Aspetto:** Legno marrone scuro invecchiato con venature

| Map | File | Colorspace |
|-----|------|------------|
| Diffuse | `textures/weathered_brown_planks_diff_2k.jpg` | sRGB |
| Normal (GL) | `textures/weathered_brown_planks_nor_gl_2k.jpg` | Non-Color |
| Roughness | `textures/weathered_brown_planks_rough_2k.jpg` | Non-Color |
| Displacement | `textures/weathered_brown_planks_disp_2k.png` | Non-Color |

**Node tree:**
```
TexCoord (Generated) → Mapping (Scale 3.0, 0.8, 3.0)
    ├── Image Texture (Diffuse, BOX 0.3) → Hue/Sat (Sat 0.65, Val 0.55) → Base Color
    ├── Image Texture (Roughness, BOX 0.3) → Roughness
    ├── Image Texture (Normal, BOX 0.3) → Normal Map (Str 2.0) ─┐
    └── Image Texture (Displacement, BOX 0.3) → Bump (Str 0.7, Dist 0.015) ← Normal → output
```

**Parametri chiave:**
- Mapping Y scale: 0.8 (venature allungate lungo la trave)
- Hue/Sat: Sat 0.65, Val 0.55 (scuro alpino invecchiato)
- Bump: Str 0.7, Dist 0.015

---

### 3. Rame Brunito (lattoneria)
- **Tipo:** Procedurale (no texture esterne)
- **Aspetto:** Rame semi-ossidato, marrone scuro metallico con variazioni

**Node tree:**
```
TexCoord (Generated) → Mapping (Scale 10,10,10)
    └── Noise (Scale 6, Detail 10, Rough 0.6)
        ├── ColorRamp → Base Color
        │   0.20: (0.55, 0.30, 0.15) — rame caldo
        │   0.50: (0.35, 0.18, 0.08) — bruno medio
        │   0.75: (0.22, 0.12, 0.06) — scuro
        │   0.92: (0.15, 0.08, 0.04) — molto scuro
        ├── ColorRamp → Roughness
        │   0.25: 0.20 (lucido)
        │   0.70: 0.50 (opaco)
        └── Noise (Scale 100, Detail 14) → Bump (Str 0.15, Dist 0.003) → Normal
```

**Parametri chiave:**
- Metallic: 0.95 (rame è sempre metallico anche brunito)
- Roughness base: 0.35 (semi-lucido)
- Bump: Str 0.15, Dist 0.003 (micro-imperfezioni)
- NO verde-rame/patina: per rame tipico alpino usare solo toni bruni

---

## Geometria tetto

### Parametri strutturali
| Parametro | Valore |
|-----------|--------|
| Angolo falda | 35° |
| Lunghezza falda | 5.0 m |
| Larghezza tetto | 4.5 m |
| Sporto gronda | 0.45 m |
| Spessore piode | 4.5 cm |
| Sezione travi | 22 × 26 cm |
| Spaziatura travi | 50 cm |
| Spessore tavolato | 2.5 cm |
| Raggio grondaia | 10 cm |
| Diametro pluviale | 11 cm |

### Struttura stratificata (dal basso)
1. Dormiente (trave orizzontale in cima al muro): 0.18 × 0.14 m
2. Travi puntoni (inclinati a 35°): 0.22 × 0.26 m ogni 50 cm
3. Tavolato: 2.5 cm continuo
4. Piode: 4.5 cm

### Lattoneria rame
- Grondaia semicircolare: R = 10 cm, lungo tutto il bordo inferiore
- Staffette ogni ~80 cm (6 su 4.5 m)
- Pluviale verticale: R = 5.5 cm, angolo destro
- Gomito di raccordo grondaia→pluviale
- Scossalina colmo: striscia 25 cm in cima alla falda
- Bordo rame gronda: striscia 12 cm sotto le piode al bordo

---

## Lezioni apprese durante il training (6 iterazioni)

### v1 — Texture sbagliata
- **Errore:** `slab_tiles` → pietre irregolari tipo "crazy paving", non piode rettangolari
- **Fix:** Usare `patterned_slate_tiles` (lastre più regolari/rettangolari)

### v2 — Travi e scala
- **Errore:** Travi troppo piccole, scala texture piode troppo grande
- **Fix:** Sezione travi 22×26cm, scala texture 5.0→3.0, camera 3/4

### v3 — Rame verde brillante
- **Errore:** Rame ossidato con patina verde → sembra turchese/verde chiaro
- **Fix parziale:** Colori più scuri nel ColorRamp

### v4 — Rame ancora verde
- **Errore:** Anche con colori scurissimi, AgX li rende più chiari
- **Conclusione:** Il metallic alto amplifica la riflessione di luce del cielo → appare verde

### v5 — Metallic variabile
- **Tentativo:** Metallic variabile (alto dove rame, basso dove patina)
- **Risultato:** Leggermente meglio ma ancora verde

### v6 — Rame brunito (SOLUZIONE)
- **Fix definitivo:** Abbandonare la patina verde, usare rame BRUNITO
- **Risultato:** Rame marrone scuro metallico, realistico per lattoneria alpina
- **Lezione chiave:** In Blender con AgX, i verdi metallici escono troppo chiari.
  Per lattoneria alpina, usare toni BRUNI (marrone/arancio scuro) con metallic 0.95

---

## Note tecniche

### Perché rame brunito e non verderame
- Il rame completamente ossidato (verde) richiede decenni di esposizione
- La maggior parte della lattoneria alpina è rame brunito (5-20 anni)
- In Blender con AgX + HDRI sky, il verde metallico riflette il cielo → appare turchese
- Il rame brunito (marrone scuro metallico) è più realistico e renderizza meglio

### Mapping piode
- Rotazione Z = 90° necessaria per allineare le lastre orizzontalmente sulla falda
- Scala 3.0 per lastre di ~30cm
- Molto desaturate (Sat 0.55) e scure (Val 0.70) per match con piode alpine

### Mapping legno travi
- Scala Y = 0.8 (bassa) per allungare le venature lungo l'asse della trave
- Scala X/Z = 3.0 (alta) per dettaglio sulla sezione trasversale

## Fonti texture
- Poly Haven: https://polyhaven.com/a/patterned_slate_tiles (piode)
- Poly Haven: https://polyhaven.com/a/weathered_brown_planks (legno)
- Licenza: CC0 (public domain)
