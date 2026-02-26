# 🎨 Render 3D — Blender v4

## Workflow: Claude scrive script Python → utente esegue in Blender sul suo PC (GPU)

## Setup utente
1. Scaricare Blender da https://www.blender.org/download/
2. Aprire Blender → Edit → Preferences → verificare GPU attiva in Cycles
3. Incollare script Python in Scripting workspace → Run Script
4. Premere F12 per render

## Cosa lo script crea
- Geometria casa (muri, tetto asimmetrico, aperture, comignolo)
- Materiali PBR (sasso grigio, piode, legno scuro, vetro triplo, acciaio)
- Tetto asimmetrico con piode visibili
- Vetrata angolo 2.40×2.40 senza montante
- FV full-black sulla falda sud (non visibile da nord)
- 6 camere posizionate sulle viste commissione
- Illuminazione HDRI alpina
- Terreno con prato

## Le 6 viste
| Vista | Camera | Uso |
|-------|--------|-----|
| V1 Via Orti | Dall'alto nord | Commissione (CRITICA) |
| V2 Prato sud | Dal basso sud | Commissione |
| V3 Valle | Teleobiettivo 600m | Commissione |
| V4 Nucleo | Strada est 28mm | Commissione |
| V5 Prima/Dopo | Split render | Commissione (CRITICA) |
| V6 Interno | Grandangolo 20mm | Committente |

## Per fotoinserimenti
- Render con sfondo trasparente (film transparent in Cycles)
- Sovrapporre su foto reale in GIMP/Photoshop
- Oppure: foto reale come background plate in Blender (camera match)

## Anti-Pattern: no render irrealistici; no FV in Vista 1; no stili non locali; no interni nella relazione paesaggistica.
