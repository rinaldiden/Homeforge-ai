# Elemento 1: Muro in Pietra — Note Training

## Texture scelta: `rock_wall_08` (Poly Haven CC0)
- Pietre scistose piatte, orizzontali — tipiche muratura alpina/valtellinese
- Alternativa testata: `stone_wall` — pietre più grandi e irregolari, meno adatta

## Parametri finali (v5)
- Scale: 1.2 (pietre leggermente più grandi del default)
- Projection: BOX 0.3, Coordinates: Generated
- AO: multiply con diffuse, factor 1.0
- HSV: Sat 0.85, Val 1.15
- Brightness/Contrast: +0.05 / +0.15 (più contrasto tra pietre e giunti)
- Normal Map: strength 2.0
- Bump macro (displacement): strength 0.9, distance 0.05
- Bump micro (noise 300): strength 0.06, distance 0.002
- Sporco alla base: gradient Z → multiply con color ramp (0-25% altezza)

## Geometria
- CUBO 3.0 x 0.45 x 2.0m (NON plane — serve spessore reale)
- Bordo superiore: subdivide 12 cuts → displace random vertici top (seed 42)
- Base appoggiata a z=0 sul terreno

## Iterazioni
| # | Modifica | Risultato |
|---|---------|-----------|
| 1 | Confronto A (rock_wall_08) vs B (stone_wall) | A vince per autenticità alpina |
| 2 | Scale 1.2, moss variation, camera 50mm | Pietre più grandi, ma camera troppo vicina |
| 3 | CUBO con spessore 0.45m, vista 3/4 | Profondità reale ma camera troppo stretta |
| 4 | Camera 35mm a 6m, HDRI visibile | Vista completa ma bordo perfetto |
| 5 | Bordo irregolare, sporco base, contrasto | **FINALE** |

## Lezioni apprese
1. **Mai usare PLANE per muri** — serve CUBO con spessore reale per vista 3/4
2. **BOX projection è essenziale** — copre tutte le facce senza UV unwrap
3. **AO map + Brightness/Contrast** danno profondità ai giunti più del solo bump
4. **Sporco alla base** con gradient Z aggiunge realismo enorme
5. **Bordo superiore irregolare** via vertex displacement è più credibile
6. **Camera 35mm a 5-6m** è il setup ideale per foto architettoniche di dettaglio
7. **HDRI strength 1.8** con sole laterale (50-70° rotation) dà il miglior contrasto
