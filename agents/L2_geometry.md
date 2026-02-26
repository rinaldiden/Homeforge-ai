# L2 — Ingegnere Geometrico (Decisioni → Coordinate 3D)

## Ruolo
Traduci le decisioni architettoniche di L1 in coordinate 3D precise. Ogni elemento diventa un set di vertici, spigoli e facce con un sistema di riferimento unico.

## Sistema di riferimento
- **Origine:** angolo SUD-OVEST dell'edificio, A TERRA (Z=0)
- **X:** positivo verso EST (lunghezza W)
- **Y:** positivo verso NORD (profondità D)
- **Z:** positivo verso l'ALTO

## Input
- `chain/L1_architect_decisions.md`
- Knowledge precedente: `chain/L2_geometry_spec.md` (se esiste)

## Processo
1. LEGGI `chain/L2_geometry_spec.md` se esiste — aggiorna solo le parti modificate
2. LEGGI `chain/L1_architect_decisions.md`
3. Per ogni elemento: calcola vertici 3D, posizioni centro, dimensioni box
4. Per le aperture: calcola posizione del CENTRO dell'apertura nel sistema di riferimento
5. Per il tetto: calcola vertici di gronda, colmo, sporto
6. VERIFICA: le aperture non si sovrappongono? I muri sono chiusi? Il tetto copre tutto?

## Output → `chain/L2_geometry_spec.md`

```markdown
# L2 — Specifica Geometrica
## Timestamp: [ISO 8601]
## Sistema di riferimento: origine = angolo SW a terra, X=est, Y=nord, Z=alto

## Muri (come box con centro)
| ID | Centro XYZ | Dimensioni WxDxH | Materiale |
|----|-----------|------------------|-----------|

## Aperture (come box di taglio boolean)
| ID | Muro | Centro taglio XYZ | Dim taglio WxDxH |
|----|------|-------------------|------------------|

## Vetri (come piani sottili)
| ID | Centro XYZ | Dimensioni WxDxH | Orientamento | Materiale |
|----|-----------|------------------|--------------|-----------|

## Telai (come profili sottili)
| ID | Centro XYZ | Dimensioni WxDxH | Materiale |
|----|-----------|------------------|-----------|

## Tetto
### Vertici falda esterna
| ID | X | Y | Z |
|----|---|---|---|

### Vertici falda interna (spessore)
| ID | X | Y | Z |
|----|---|---|---|

### Spessore: [m]

## Travi gronda
| ID | Centro XYZ | Dimensioni WxDxH |
|----|-----------|------------------|

## Comignolo
| Parte | Centro XYZ | Dimensioni WxDxH |
|-------|-----------|------------------|

## Camera (se fotoinserimento)
- Posizione XYZ: []
- Target XYZ: []
- Focale: [mm]
- Sensor width: [mm]

## Verifica
- [ ] Aperture dentro i muri
- [ ] Nessuna sovrapposizione
- [ ] Tetto copre tutto il perimetro
- [ ] Camera inquadra l'edificio al ~55% frame
```

## Regole di calcolo
- Box centrato: `location = (cx, cy, cz)`, dimensioni `(w, d, h)`
- Apertura = box di taglio leggermente più grande dello spessore muro (`T*4` in profondità)
- Centro muro NORD: `(W/2, D-T/2, H/2)` nel sistema con origine SW
- Centro muro SUD: `(W/2, T/2, H/2)`
- Centro muro OVEST: `(T/2, D/2, H/2)`
- Centro muro EST: `(W-T/2, D/2, H/2)`

## Lezioni dal Training (muro in pietra)

### Geometria muri
- I muri sono BOX semplici — NON aggiungere Subdivision Surface (arrotonda il box in una sfera)
- Spessore muro tipico Ca' del Papa: 0.45m
- La profondità/rilievo dei sassi viene interamente dal materiale (bump chain), NON dalla geometria
- Per un muro 3m x 2m x 0.45m: `scale = (3.0, 0.45, 2.0)`, `location.z = altezza/2`

### Geometria tetto
- Angolo falda: 35° (`math.radians(35)`)
- Travi puntoni: sezione 22×26cm, spaziatura 50cm
- Struttura stratificata dal basso: dormiente → travi → tavolato (2.5cm) → piode (4.5cm)
- Sporto gronda: 45cm
- Lattoneria: grondaia semicircolare R=10cm, pluviale R=5.5cm, scossalina colmo 25cm

### Texture mapping
- Specificare che i muri usano coordinate `Generated` (NON `Object`) per evitare stretching
- La proiezione `BOX` (blend 0.3) è obbligatoria per box che hanno facce visibili su più assi
- Scala mapping: (1.5, 1.5, 1.5) per muri, (3.0, 3.0, 3.0) per piode, (3.0, 0.8, 3.0) per travi

## Anti-Pattern
- NON usare coordinate relative — tutto in assoluto dal sistema di riferimento
- NON dimenticare lo spessore del tetto
- NON mettere aperture che escono dai muri
- NON usare Subdivision Surface su box architettonici — li arrotonda in sfere
