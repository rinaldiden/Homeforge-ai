# L2 — Specifica Geometrica
## Timestamp: 2026-02-26T10:01:00+01:00
## Sistema di riferimento: origine = angolo SW a terra (Z=0), X=est, Y=nord, Z=alto

## Parametri globali
- W = 11.0 m (est-ovest)
- D = 8.0 m (nord-sud)
- HG = 3.0 m (altezza gronda)
- HC = 4.8 m (altezza colmo)
- T = 0.45 m (spessore muri)
- CO = 1.5 m (offset colmo verso nord dal centro)
- SP = 0.40 m (sporto gronda)
- RT = 0.18 m (spessore tetto/piode)

## Muri (come box con centro)
| ID | Nome | Centro XYZ | Dimensioni WxDxH | Materiale |
|----|------|-----------|------------------|-----------|
| M1 | Muro Sud | (5.50, 0.225, 1.50) | 11.00 × 0.45 × 3.00 | Pietra |
| M2 | Muro Nord | (5.50, 7.775, 1.50) | 11.00 × 0.45 × 3.00 | Pietra |
| M3 | Muro Ovest | (0.225, 4.00, 1.50) | 0.45 × 8.00 × 3.00 | Pietra |
| M4 | Muro Est | (10.775, 4.00, 1.50) | 0.45 × 8.00 × 3.00 | Pietra |

## Aperture (come box di taglio boolean)
Profondità taglio = T × 4 = 1.80 m (per penetrare completamente il muro)

| ID | Nome | Muro | Centro taglio XYZ | Dim taglio WxDxH |
|----|------|------|-------------------|------------------|
| A1 | Vetrata SW - lato sud | M1 | (1.20, 0.225, 1.60) | 2.40 × 1.80 × 2.40 |
| A2 | Vetrata SW - lato ovest | M3 | (0.225, 1.20, 1.60) | 1.80 × 2.40 × 2.40 |
| A3 | Finestra sud centrale | M1 | (7.00, 0.225, 1.60) | 1.20 × 1.80 × 1.40 |
| A4 | Porta ingresso | M1 | (4.50, 0.225, 1.10) | 1.00 × 1.80 × 2.20 |
| A5 | Finestra ovest | M3 | (0.225, 5.50, 1.50) | 1.80 × 1.00 × 1.20 |
| A6 | Finestra est 1 | M4 | (10.775, 3.00, 1.50) | 1.80 × 1.00 × 1.20 |
| A7 | Finestra est 2 | M4 | (10.775, 7.00, 1.50) | 1.80 × 1.00 × 1.20 |
| A8 | Finestra nord 1 | M2 | (3.50, 7.775, 1.70) | 0.80 × 1.80 × 1.00 |
| A9 | Finestra nord 2 | M2 | (7.50, 7.775, 1.70) | 0.80 × 1.80 × 1.00 |

### Note aperture vetrata angolo SW
- A1 parte dal bordo ovest: centro_x = 0 + 2.40/2 = 1.20
- A2 parte dal bordo sud: centro_y = 0 + 2.40/2 = 1.20
- Davanzale a 0.40 m: centro_z = 0.40 + 2.40/2 = 1.60
- L'angolo del muro tra M1 e M3 viene rimosso dalla combinazione di A1 e A2

## Vetri (come piani sottili)
| ID | Nome | Centro XYZ | Dimensioni WxDxH | Materiale |
|----|------|-----------|------------------|-----------|
| V1 | Vetro SW sud | (1.20, 0.02, 1.60) | 2.40 × 0.03 × 2.40 | Vetro |
| V2 | Vetro SW ovest | (0.02, 1.20, 1.60) | 0.03 × 2.40 × 2.40 | Vetro |
| V3 | Vetro finestra sud | (7.00, 0.02, 1.60) | 1.20 × 0.03 × 1.40 | Vetro |
| V4 | Vetro finestra ovest | (0.02, 5.50, 1.50) | 0.03 × 1.00 × 1.20 | Vetro |
| V5 | Vetro finestra est 1 | (10.98, 3.00, 1.50) | 0.03 × 1.00 × 1.20 | Vetro |
| V6 | Vetro finestra est 2 | (10.98, 7.00, 1.50) | 0.03 × 1.00 × 1.20 | Vetro |
| V7 | Vetro finestra nord 1 | (3.50, 7.98, 1.70) | 0.80 × 0.03 × 1.00 | Vetro |
| V8 | Vetro finestra nord 2 | (7.50, 7.98, 1.70) | 0.80 × 0.03 × 1.00 | Vetro |

## Telai (come profili sottili — solo per finestre, non per vetrata angolo)
Sezione telaio: 0.06 × 0.06 m, materiale legno scuro

| ID | Nome | Centro XYZ | Dimensioni WxDxH | Note |
|----|------|-----------|------------------|------|
| T3-top | Telaio fin sud top | (7.00, 0.03, 2.33) | 1.32 × 0.06 × 0.06 | sopra V3 |
| T3-bot | Telaio fin sud bot | (7.00, 0.03, 0.87) | 1.32 × 0.06 × 0.06 | sotto V3 |
| T3-sx  | Telaio fin sud sx  | (6.37, 0.03, 1.60) | 0.06 × 0.06 × 1.52 | sx V3 |
| T3-dx  | Telaio fin sud dx  | (7.63, 0.03, 1.60) | 0.06 × 0.06 × 1.52 | dx V3 |
| TP-top | Telaio porta top | (4.50, 0.03, 2.23) | 1.12 × 0.06 × 0.06 | sopra porta |
| TP-sx  | Telaio porta sx  | (3.97, 0.03, 1.10) | 0.06 × 0.06 × 2.32 | sx porta |
| TP-dx  | Telaio porta dx  | (5.03, 0.03, 1.10) | 0.06 × 0.06 × 2.32 | dx porta |

## Tetto (mesh custom con spessore)

### Calcolo posizioni
- Centro pianta: (W/2, D/2) = (5.50, 4.00)
- Colmo Y = D/2 + CO = 4.00 + 1.50 = 5.50
- Colmo Z = HC = 4.80
- Gronda Z = HG = 3.00

### Vertici falda esterna (vista dall'alto: gronda sud → colmo → gronda nord)
| ID | X | Y | Z | Nota |
|----|---|---|---|------|
| RE1 | -SP | -SP | HG | Gronda SW esterna (-0.40, -0.40, 3.00) |
| RE2 | W+SP | -SP | HG | Gronda SE esterna (11.40, -0.40, 3.00) |
| RE3 | W+SP | 5.50 | HC | Colmo EST (11.40, 5.50, 4.80) |
| RE4 | -SP | 5.50 | HC | Colmo OVEST (-0.40, 5.50, 4.80) |
| RE5 | -SP | D+SP | HG | Gronda NW esterna (-0.40, 8.40, 3.00) |
| RE6 | W+SP | D+SP | HG | Gronda NE esterna (11.40, 8.40, 3.00) |

### Vertici falda interna (offset verso l'interno di RT=0.18m)
| ID | X | Y | Z | Nota |
|----|---|---|---|------|
| RI1 | -SP | -SP | HG-RT | (-0.40, -0.40, 2.82) |
| RI2 | W+SP | -SP | HG-RT | (11.40, -0.40, 2.82) |
| RI3 | W+SP | 5.50 | HC-RT | (11.40, 5.50, 4.62) |
| RI4 | -SP | 5.50 | HC-RT | (-0.40, 5.50, 4.62) |
| RI5 | -SP | D+SP | HG-RT | (-0.40, 8.40, 2.82) |
| RI6 | W+SP | D+SP | HG-RT | (11.40, 8.40, 2.82) |

### Facce tetto
- Falda SUD esterna: RE1, RE2, RE3, RE4
- Falda NORD esterna: RE4, RE3, RE6, RE5
- Falda SUD interna: RI1, RI2, RI3, RI4
- Falda NORD interna: RI4, RI3, RI6, RI5
- Bordo gronda sud: RE1, RE2, RI2, RI1
- Bordo gronda nord: RE5, RE6, RI6, RI5
- Bordo laterale ovest sud: RE1, RE4, RI4, RI1
- Bordo laterale est sud: RE2, RE3, RI3, RI2
- Bordo laterale ovest nord: RE4, RE5, RI5, RI4
- Bordo laterale est nord: RE3, RE6, RI6, RI3

## Timpani (triangoli laterali — muro che chiude il frontone)

### Timpano OVEST
Vertici: (0, 0, HG), (0, D, HG), (0, 5.50, HC)
- Triangolo con base su facciata ovest, vertice al colmo
- Spessore: T = 0.45 m (estrusione verso X positivo)
- Materiale: Pietra

### Timpano EST
Vertici: (W, 0, HG), (W, D, HG), (W, 5.50, HC)
- Spessore: T = 0.45 m (estrusione verso X negativo)
- Materiale: Pietra

## Travi gronda (teste a vista)
Sezione: 0.15 × 0.20 m, spaziatura 0.60 m
Sporgenza: SP = 0.40 m

### Travi gronda SUD (orientate N-S)
| ID | Centro XYZ | Dimensioni WxDxH |
|----|-----------|------------------|
| TG-S01 | (0.30, -0.20, 2.90) | 0.15 × 0.80 × 0.20 |
| TG-S02 | (0.90, -0.20, 2.90) | 0.15 × 0.80 × 0.20 |
| TG-S03 | (1.50, -0.20, 2.90) | 0.15 × 0.80 × 0.20 |
| ... | ogni 0.60 m fino a X=10.70 | |
| TG-S18 | (10.50, -0.20, 2.90) | 0.15 × 0.80 × 0.20 |

Totale: ~18 travi sulla gronda sud (da X=0.30 a X=10.50, passo 0.60)

### Travi gronda NORD (orientate N-S)
| ID | Centro XYZ | Dimensioni WxDxH |
|----|-----------|------------------|
| TG-N01 | (0.30, 8.20, 2.90) | 0.15 × 0.80 × 0.20 |
| ... | ogni 0.60 m | |
| TG-N18 | (10.50, 8.20, 2.90) | 0.15 × 0.80 × 0.20 |

## Comignolo
| Parte | Centro XYZ | Dimensioni WxDxH | Materiale |
|-------|-----------|------------------|-----------|
| Base | (5.50, 5.50, 5.30) | 0.60 × 0.60 × 1.00 | Pietra |
| Cappello | (5.50, 5.50, 5.90) | 0.80 × 0.80 × 0.10 | Pietra |

Nota: base parte dal colmo (4.80) e arriva a 5.80. Cappello a 5.85-5.95.

## Davanzali
| ID | Centro XYZ | Dimensioni WxDxH | Materiale |
|----|-----------|------------------|-----------|
| D3 | (7.00, -0.03, 0.87) | 1.35 × 0.12 × 0.05 | Pietra |
| D5 | (-0.03, 5.50, 1.47) | 0.12 × 1.10 × 0.05 | Pietra |

## Camera (fotoinserimento vista sud)
- Posizione: (5.50, -16.00, 1.60)
- Target: (5.50, 4.00, 2.00)
- Focale: 35 mm
- Sensor width: 36 mm
- Clip start: 0.1
- Clip end: 100
- Risoluzione: 1920 × 1080

### Verifica distanza camera
- sensor_h = 36 × 1080/1920 = 20.25 mm
- vfov = 2 × atan(20.25 / (2 × 35)) = 2 × atan(0.2893) = 2 × 16.14° = 32.28°
- Per HC=4.80 al 55% frame: d = 4.80 / (0.55 × 2 × tan(16.14°)) = 4.80 / (0.55 × 0.5786) = 4.80 / 0.318 ≈ 15.1 m
- Camera a 16 m → edificio al ~52% del frame ✓

## Verifica
- [x] Aperture dentro i muri (tutte le aperture hanno centro dentro il muro corrispondente)
- [x] Nessuna sovrapposizione (aperture distanziate, vetrata angolo senza conflitti)
- [x] Tetto copre tutto il perimetro (sporto 0.40 m su tutti i lati)
- [x] Camera inquadra l'edificio al ~52% frame (leggermente sotto 55%, ok)
- [x] Colmo offset 1.5m nord dal centro (Y=5.50 vs centro=4.00)
- [x] Vetrata angolo al SUD-OVEST (A1 su M1 + A2 su M3)
