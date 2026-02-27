# Elemento 2: Tetto Piode — Note Training

## Texture scelta: `castle_wall_slates` (Poly Haven CC0)
- Pietre irregolari di dimensioni diverse — autentico per piode tradizionali
- Alternative testate e scartate:
  - `roof_slates_02`: troppo regolare, sembra tegole industriali
  - `roof_slates_03`: ordinato, buono per ardesia moderna ma non per piode

## Parametri finali
- Scale: 0.8 (piode grandi, scale BASSO = pietre PIÙ GRANDI)
- Projection: BOX 0.3, Coordinates: Generated
- AO: multiply, factor 1.0
- Contrast: +0.18 (buon rilievo tra lastre)
- HSV: Sat 0.60, Val 1.0 (piode molto grigie/desaturate)
- Normal Map: strength 2.0
- Bump: strength 1.0, distance 0.06

## Geometria
- CUBO 5.5 x 4.0 x 0.05m (spessore 5cm visibile al bordo)
- Rotazione 30° intorno a X (pitch tetto verso la camera)
- Posizione: centrato sopra muro a z=3.5
- Fascia legno sotto bordo gronda: cubo sottile con wood texture

## Iterazioni
| # | Modifica | Risultato |
|---|---------|-----------|
| 1 | Confronto A/B/C, camera dal basso | Tetto fuori inquadratura |
| 2 | Geometria rivista, muro supporto | Camera vedeva solo il muro |
| 3 | Camera dall'alto | Finalmente tetto visibile! C vince |
| 4 | Scena completa: muro + fascia + tetto | Buono ma camera troppo bassa |
| 5-6 | Camera centrata più alta | **FINALE** |

## Lezioni apprese
1. **Per tetti inclinati, camera DALL'ALTO** — dal basso si vede solo il sottotetto/muro
2. **Piode = irregolari** — NON usare texture regolari tipo tegole
3. **Scale basso = pietre grandi** — per piode tradizionali serve scale 0.8-1.0
4. **Saturation molto bassa (0.6)** per piode — sono grigio-argento quasi monocromatiche
5. **Fascia legno** aggiunge realismo al bordo gronda
6. **La geometria del tetto è critica** — rotazione + posizione devono essere calcolate per la visibilità dalla camera scelta
