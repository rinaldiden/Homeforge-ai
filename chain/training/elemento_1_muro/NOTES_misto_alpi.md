# Muro Misto Alpi — Note Training

## Riferimento: pietraeco.it "Misto Alpi"
- Muratura alpina con pietre miste scistose
- Giunti malta molto scuri (quasi neri) e profondamente incassati
- Variazione cromatica: grigio scuro, argento, marrone-grigio nello stesso muro
- Rilievo 3D forte: pietre sporgono 3-5cm dal piano malta
- Pietre miste: lastre piatte orizzontali + blocchi più spessi

## Texture scelta: `castle_wall_slates` (Poly Haven CC0)
- Migliore tra 4 candidate testate (iter1)
- Alternative testate:
  - `broken_wall`: pietre troppo chiare/irregolari
  - `stacked_stone_wall`: troppo scuro/rossastro
  - `rock_wall_08`: troppo piatto e uniforme

## Tecnica chiave: TRUE DISPLACEMENT
- Differenza fondamentale rispetto agli iter precedenti (solo bump)
- `mat.displacement_method = 'BOTH'` (displacement + bump per micro-detail)
- Subdivision Surface modifier: SIMPLE, render_levels = 6
- ShaderNodeDisplacement: Scale 0.045, Midlevel 0.5
- Bump aggiuntivo: Strength 0.7, Distance 0.025 (micro-dettaglio superficie)

## Parametri materiale finali
- Scale: (0.75, 0.75, 0.75) — pietre medio-grandi
- Projection: BOX 0.3, Coordinates: Generated
- AO: Gamma 0.35 → Multiply (giunti molto scuri)
- Contrast: +0.25, Bright: 0.0
- HSV: Hue 0.505, Sat 0.92, Val 1.15
- Normal Map: strength 2.8
- Displacement: 4.5cm scale, midlevel 0.5
- Mortar darkening: inverted displacement → ColorRamp(0, 0.25) → mix with near-black (0.025)

## Variazione cromatica
- Noise texture scale 1.0, detail 4.0, roughness 0.6
- ColorRamp con cutoff 0.30-0.70 per patch definite
- Warm HSV shift: Hue 0.55, Sat 1.35, Val 1.05
- Mix tra versione cool (grigia) e warm (marrone) guidata dal noise

## Composizione
- Camera 3/4 mostra fronte + lato (come foto prodotto pietraeco.it)
- Wall rotato -20° su Z
- Cap scuro in alto (come bordo superiore finito)
- Sfondo grigio chiaro (0.88)
- Lens 45mm, HDRI Strength 2.2, rotazione 35°

## Iterazioni
| # | Modifica | Risultato |
|---|---------|-----------|
| 1 | Confronto 4 texture con displacement | castle_wall_slates vince, troppo scuro |
| 2 | 3 varianti bright/warm/deep | V3_deep migliore, ancora troppo chiaro |
| 3 | AO doppia + disp 5.5cm | Troppo aggressivo, sembra corteccia |
| 4 | Ritorno bilanciato, noise warm/cool | Buon rilievo, giunti non abbastanza scuri |
| 5 | Gamma AO + mortar darkening via disp | Giunti più scuri, buona direzione |
| 6 | Composizione prodotto 3/4 con sfondo | Muro troppo piccolo nel frame |
| 7 | Camera più vicina, bordo irregolare | Buona composizione, giunti da migliorare |
| 8 | Gamma 0.35, mortar nero, toni caldi | **FINALE** |

## Lezioni apprese
1. **TRUE DISPLACEMENT è obbligatorio** per muri in pietra — il solo bump non basta
2. **AO con Gamma < 0.5** per giunti molto scuri (power curve sulle ombre)
3. **Mortar darkening via displacement map** inverted → ramp → mix con colore scuro
4. **Noise texture per variazione cromatica** warm/cool su patch grandi (scale 1.0)
5. **Composizione 3/4** mostra sia la faccia frontale che lo spessore laterale
6. **Non esagerare col displacement** — 4-4.5cm è il giusto, 5.5cm deforma troppo
7. **ColorRamp stretto** (0-0.25) per targetizzare solo i giunti profondi
