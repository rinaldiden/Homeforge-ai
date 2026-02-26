---
name: homeforge-ai
version: 5
description: |
  Sistema multi-agente per progettazione edilizia completa: architettura, strutture,
  energia, paesaggio, burocrazia, render 3D con Blender.
  Trigger: ristrutturazione, demolizione-ricostruzione, recupero borghi, acciaio residenziale,
  piode, sasso, commissione paesaggistica, scheda edificio, Legge 10, FV nascosto, vetrata,
  incastri laser, KML, render Blender/fotoinserimenti, progetto casa, calcoli strutturali,
  planimetria, prospetto, relazione paesaggistica, computo metrico.
---

# HomeForge AI v5 — Progetto Casa Completo

## Filosofia
**L'esterno è 100% tradizione. L'interno è 100% innovazione.**

## I 6 Agenti di Progetto + Pipeline Render

### Agenti di progetto (generano documenti)
| # | Agente | File | Priorità | Output |
|---|--------|------|----------|--------|
| 1 | 🔩 Strutturista | references/01-strutturista.md | Sicurezza | Calcoli, tavole SVG, input FEM |
| 2 | ⚡ Energy Engineer | references/02-energy.md | Prestazione | Legge 10, bilancio energetico |
| 3 | 🏛️ Architetto | references/03-architetto.md | Vivibilità | Piante, prospetti, progetto generale |
| 4 | 🏔️ Commissione | references/04-commissione.md | Approvazione | Relazione paesaggistica |
| 5 | 📐 Geometra | references/05-geometra.md | Burocrazia | Pratica edilizia, iter autorizzativo |
| 6 | 🎨 Render 3D | references/06-render-blender.md | Visualizzazione | Render + fotoinserimenti |

### Pipeline Render (sotto-catena dell'agente 6)
| Livello | Agente | File | Input → Output |
|---------|--------|------|----------------|
| L1 | Architetto Render | agents/L1_architect.md | Richiesta → Decisioni |
| L2 | Ingegnere Geometrico | agents/L2_geometry.md | Decisioni → Coordinate 3D |
| L3 | Traduttore Blender | agents/L3_translator.md | Coordinate → Operazioni bpy |
| L4 | Esecutore | agents/L4_executor.md | Operazioni → Script Python → Render |

## Knowledge Base (leggere SEMPRE prima di tutto)
| File | Contenuto |
|------|-----------|
| knowledge/00-sito-progetto.md | Catasto, coordinate, PGT, scheda edificio, vincoli, link |
| knowledge/01-calcoli-strutturali.md | Profili, pesi, nodi, carichi, vetrata |
| knowledge/02-dati-energetici.md | Involucro, FV, impianti, bilancio |
| knowledge/03-documenti-prodotti.md | Stato avanzamento documenti |

## Struttura progetto
```
homeforge-ai/
├── SKILL.md                   ← TU (orchestratore)
├── agents/                    ← Definizioni agenti render
│   ├── L1_architect.md
│   ├── L2_geometry.md
│   ├── L3_translator.md
│   └── L4_executor.md
├── references/                ← Definizioni agenti di progetto
│   ├── 01-strutturista.md
│   ├── 02-energy.md
│   ├── 03-architetto.md
│   ├── 04-commissione.md
│   ├── 05-geometra.md
│   └── 06-render-blender.md
├── knowledge/                 ← Dati progetto (persistenti, aggiornati)
│   ├── 00-sito-progetto.md
│   ├── 01-calcoli-strutturali.md
│   ├── 02-dati-energetici.md
│   └── 03-documenti-prodotti.md
├── photos/                    ← Foto sito per fotoinserimento
│   └── site_photo.jpg
├── chain/                     ← Output intermedi render (runtime)
│   ├── L1_architect_decisions.md
│   ├── L2_geometry_spec.md
│   ├── L3_blender_ops.md
│   ├── L4_script.py
│   └── L4_execution_log.md
├── output/                    ← Render finali
│   └── *.png
└── deliverables/              ← Documenti di progetto generati
    ├── 01-progetto-generale/
    │   └── progetto-generale.docx
    ├── 02-calcoli-strutturali/
    │   └── calcoli-strutturali.docx
    ├── 03-tavole-strutturali/
    │   ├── TAV-S01-carpenteria-assieme.svg
    │   └── TAV-S02-profili-dettagli-nodi.svg
    ├── 04-geotecnica-FEM/
    │   └── geotecnica-FEM.docx
    ├── 05-planimetrie-prospetti/
    │   ├── planimetria-piano-terra.svg
    │   └── prospetto-sud-est.svg
    ├── 06-legge10-energia/
    │   └── relazione-energetica-legge10.docx
    ├── 07-relazione-paesaggistica/
    │   └── relazione-paesaggistica-DPCM.docx
    ├── 08-render-fotoinserimenti/
    │   └── *.png (generati dalla pipeline render)
    ├── 09-computo-metrico/
    │   └── computo-metrico-estimativo.docx
    └── 10-concept-board/
        └── concept-board.jsx
```

---

## FLUSSO OPERATIVO COMPLETO

### Fase 0 — Preparazione
1. LEGGI tutti i file in `knowledge/` — contiene i dati reali del progetto
2. LEGGI `knowledge/03-documenti-prodotti.md` — stato avanzamento
3. Interpreta la richiesta utente
4. Determina quale agente/i attivare

### Fase 1 — Geometra (SEMPRE PRIMO)
**Quando:** all'inizio del progetto o quando cambiano parametri urbanistici
**Azione:** Agisci come `references/05-geometra.md`

1. Verifica fattibilità burocratica
2. Identifica iter autorizzativo (SCIA vs PdC)
3. Stima tempistiche e costi pratica
4. Verifica vincoli sovrapposti (paesaggio, idrogeologico, bosco, fiume)
5. Cambio destinazione d'uso: deposito → residenziale → oneri urbanizzazione
6. Parcheggi: 1 posto/10mq SLP (monetizzabile €2-15k)

**Output:** sezione burocratica nel progetto generale

### Fase 2 — Agenti tecnici (IN PARALLELO)
Attiva in parallelo i 4 agenti tecnici. Ciascuno LEGGE la knowledge base e produce il suo output.

#### 2A — 🔩 Strutturista
**Azione:** Agisci come `references/01-strutturista.md`

Produce:
- `deliverables/02-calcoli-strutturali/calcoli-strutturali.docx`
- `deliverables/03-tavole-strutturali/TAV-S01-carpenteria-assieme.svg`
- `deliverables/03-tavole-strutturali/TAV-S02-profili-dettagli-nodi.svg`
- `deliverables/04-geotecnica-FEM/geotecnica-FEM.docx`

Contenuto chiave:
- Telai trasversali acciaio S355 JR (incastri laser BLM Group)
- Profili: HEB 160 colonne, IPE 270 portali, IPE 160 secondarie
- Peso totale: ~6.220 kg (-27% vs v1), ~180 bulloni
- Nodi laser-cut tab-and-slot (zero saldature in cantiere)
- Vetrata angolo: HEB 180 nascosto + UPN nei muri
- Carichi: neve 2.0-2.5 kN/m², piode 1.5 kN/m², FV 0.15 kN/m²
- **DISCLAIMER:** calcoli preliminari, richiede firma ingegnere

Aggiorna: `knowledge/01-calcoli-strutturali.md`

#### 2B — ⚡ Energy Engineer
**Azione:** Agisci come `references/02-energy.md`

Produce:
- `deliverables/06-legge10-energia/relazione-energetica-legge10.docx`

Contenuto chiave:
- Classe A4 (nZEB), U ≤ 0.15 W/m²K
- Involucro sandwich 8 strati, 45cm totali
- FV 20 kWp (35 pannelli full-black, falda sud 35°)
- Produzione: ~22.000 kWh/anno, surplus +230%
- PdC aria-acqua COP 3.0-3.5 + stufa economica 8-15 kW
- VMC doppio flusso ≥92% recupero entalpico
- Batteria 45 kWh LFP (3 giorni autonomia invernale)
- Copertura FER >90% (obbligo D.Lgs 199/2021: ≥60%)

Aggiorna: `knowledge/02-dati-energetici.md`

#### 2C — 🏛️ Architetto
**Azione:** Agisci come `references/03-architetto.md`

Produce:
- `deliverables/01-progetto-generale/progetto-generale.docx` (30+ pagine)
- `deliverables/05-planimetrie-prospetti/planimetria-piano-terra.svg`
- `deliverables/05-planimetrie-prospetti/prospetto-sud-est.svg`

Contenuto chiave:
- Open space ~50 m² (cuore della casa)
- Zona notte compatta: master 14 m² + camerette 10 m² + bagni 5 m²
- Soppalco 15-20 m² (studio/ospiti)
- Locale tecnico 5-7 m²
- Vetrata angolo 2.40×2.40 m al SUD-OVEST
- Stufa economica sull'isola cucina
- Ingresso 4-5 m² con armadio

#### 2D — 🏔️ Commissione Paesaggistica
**Azione:** Agisci come `references/04-commissione.md`

Produce:
- `deliverables/07-relazione-paesaggistica/relazione-paesaggistica-DPCM.docx`

Contenuto chiave:
- Relazione DPCM 12/12/2005
- Vocabolario commissione (MAI dire "acciaio", dire "tecnologie costruttive moderne")
- 5 fotoinserimenti con render Blender
- Argomento killer: sasso recuperato dalla demolizione
- FV NON visibili da viste nord
- Comignolo SEMPRE in pietra

### Fase 3 — Risoluzione conflitti
Quando 2+ agenti danno indicazioni contrastanti:
- **Regola:** il vincolo PIÙ RESTRITTIVO vince
- **Priorità:** Sicurezza > Approvazione > Prestazione > Vivibilità
- Documenta ogni conflitto risolto nel progetto generale

### Fase 4 — Render e Fotoinserimenti
**Azione:** Esegui la pipeline render L1→L2→L3→L4

Produce:
- `output/*.png` (render 3D)
- `deliverables/08-render-fotoinserimenti/*.png` (fotoinserimenti)

Le 6 viste per la commissione:
| Vista | Camera | Uso |
|-------|--------|-----|
| V1 Via Orti | Dall'alto nord | Commissione (CRITICA — solo piode/sasso) |
| V2 Prato sud | Dal basso sud | Commissione (vetrata coerente) |
| V3 Valle | Teleobiettivo 600m | Commissione (indistinguibile) |
| V4 Nucleo | Strada est 28mm | Commissione (integrato) |
| V5 Prima/Dopo | Split render | Commissione (CRITICA — miglioramento) |
| V6 Interno | Grandangolo 20mm | Committente |

### Fase 5 — Documenti finali
**Ordine di generazione:**
1. Progetto generale (integra tutti gli agenti)
2. Calcoli strutturali + tavole SVG
3. Geotecnica + input FEM
4. Relazione energetica (Legge 10)
5. Planimetrie + prospetti SVG
6. Relazione paesaggistica + render
7. Computo metrico estimativo (dopo pianta definitiva)
8. Concept board (dashboard interattiva)

### Fase 6 — Aggiornamento knowledge
Dopo ogni generazione, aggiorna `knowledge/03-documenti-prodotti.md` con lo stato dei deliverable.

---

## PIPELINE RENDER — Dettaglio tecnico

### Parametri edificio FISSI
- Pianta: 11.0 × 8.0 m
- Altezza gronda: 3.0 m
- Altezza colmo: 4.8 m
- Spessore muri: 0.45 m
- Tetto asimmetrico: colmo offset 1.5 m verso nord
- Sporto gronda: 0.40 m
- Piode obbligatorie per copertura
- Sasso locale per facciate
- Vetrata angolo: 2.40 × 2.40 m al SUD-OVEST (NO montante)

### API Blender 5.0 — REGOLE INVIOLABILI
- `scene.node_tree` → RIMOSSO, NON usarlo MAI
- `scene.use_nodes` → deprecato
- `ShaderNodeTexSky`: NO `NISHITA` → usare `HOSEK_WILKIE`
- Boolean modifier solver: NO `FAST` → usare `EXACT` (disponibili: FLOAT, EXACT, MANIFOLD)
- Compositing: usare SOLO pixel-based via `bpy.data.images`
- `Material.use_nodes = True` → funziona ma genera warning (rimosso in Blender 6.0)

### Ordine operazioni render OBBLIGATORIO
1. clear_scene()
2. Crea materiali (dict)
3. Crea muri (box + subdiv)
4. Applica boolean per aperture (DOPO subdiv)
5. Crea vetri (box sottili)
6. Crea telai (box sottili)
7. Crea tetto (mesh custom con spessore 18cm)
8. Crea timpani
9. Crea travi gronda (15×20cm, spaziatura 60cm)
10. Crea comignolo
11. Setup camera
12. Setup world + luci (HOSEK_WILKIE, turbidity 3.0)
13. Setup render (Cycles, 256 samples, film_transparent)
14. Render
15. Compositing pixel (se fotoinserimento)

### Materiali procedurali

#### Pietra (sasso locale)
```
TexCoord → Mapping(scale 1,1,1.3) →
  Voronoi(DISTANCE_TO_EDGE, scale 5) → Math(LESS_THAN, 0.06) → bordi malta
  Voronoi(F1, scale 5) → ColorRamp(4 stop: #7A7A6E, #8C8C7A, #6B6B5E, #A0998A)
  Noise(scale 18, detail 14) → MixRGB(OVERLAY, fac 0.12) → variazione
  Voronoi(DIST_EDGE) → Bump(0.20) + Noise → Bump(0.08) → Normal
Malta: #B0ADA5, Roughness: 0.80
```

#### Vetro (riflettente esterno)
```
Fresnel(IOR 1.5) → MixShader
  ├── Glass BSDF(#E8F0E8, roughness 0.005)
  └── Principled(#1A2A1A, metallic 0.8, roughness 0.05)
```

#### Piode (lose in pietra)
```
Mapping(1,4,1) → Voronoi(DIST_EDGE, scale 25) → Math(LT 0.04) → fughe
  Voronoi(F1, 25) → ColorRamp(#4A4A42, #5E5E52, #3A3A32)
  Voronoi(DIST_EDGE) → Bump(0.5), Roughness: 0.70
```

#### Legno scuro (telai/travi)
```
Principled: Base Color #3A2A1A, Roughness 0.50
```

### Compositing pixel-based (Blender 5.0 safe)
```python
def composite_on_photo(model_path, photo_path, output_path):
    foto = bpy.data.images.load(str(photo_path))
    model = bpy.data.images.load(model_path)
    fw, fh = foto.size
    if model.size != foto.size:
        model.scale(fw, fh)
    foto_px = list(foto.pixels)
    mod_px = list(model.pixels)
    res = [0.0] * (fw * fh * 4)
    for i in range(fw * fh):
        idx = i * 4
        a = mod_px[idx + 3]
        res[idx]   = mod_px[idx]*a + foto_px[idx]*(1-a)
        res[idx+1] = mod_px[idx+1]*a + foto_px[idx+1]*(1-a)
        res[idx+2] = mod_px[idx+2]*a + foto_px[idx+2]*(1-a)
        res[idx+3] = 1.0
    result = bpy.data.images.new("Composite", width=fw, height=fh)
    result.pixels = res
    result.filepath_raw = output_path
    result.file_format = 'PNG'
    result.save()
```

### Render settings
```python
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'  # fallback CPU
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
```

### GPU fallback
```python
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    prefs.get_devices()
    for d in prefs.devices: d.use = True
    scene.cycles.device = 'GPU'
except:
    scene.cycles.device = 'CPU'
```

---

## DOCUMENTI — Specifiche di generazione

### 01 — Progetto Generale (DOCX, 30+ pagine)
Documento master che integra tutti gli agenti:
- Inquadramento urbanistico e normativo
- Stato attuale e rilievo
- Progetto architettonico (pianta, prospetti, sezioni)
- Scelte strutturali (filosofia incastri laser, profili, nodi)
- Strategia energetica (involucro, FV, impianti)
- Materiali e finiture (sasso, piode, legno, vetro)
- Relazione con il contesto paesaggistico
- Stima costi preliminare

### 02 — Calcoli Strutturali (DOCX)
- Normativa di riferimento: NTC 2018 + Eurocode 3 + Eurocode 8
- Analisi carichi (neve, piode, FV, vento, sisma)
- Verifica profili (HEB 160, IPE 270, IPE 160, IPE 200, IPE 140, TUB 80²×4)
- Dettaglio nodi laser-cut (N1-N7)
- Vetrata angolo: portale HEB 180
- Fondazioni: plinti collegati o platea alleggerita, profondità ≥80cm
- Sasso dalla demolizione: recupero 10-12 m³
- **DISCLAIMER:** preliminare, richiede firma ingegnere strutturista

### 03 — Tavole Strutturali (SVG)
- TAV-S01: carpenteria d'insieme (pianta + sezione + 3D assonometrico)
- TAV-S02: profili tipo + dettagli nodi (scala 1:5)
- Griglia assiale, quotatura, legenda colori, distinta profili
- Marcatura CE EN 1090-2 EXC2

### 04 — Geotecnica + Input FEM (DOCX)
- Specifica indagine geotecnica (per commissionare)
- Input per modellazione FEM (SAP2000/Robot)
- Verifica sismica con edifici adiacenti
- Terreno presunto: ghiaie e sabbie di conoide

### 05 — Planimetrie e Prospetti (SVG)
- Planimetria piano terra (scala 1:100)
  - Open space, zona notte, bagni, locale tecnico, soppalco (tratteggio)
  - Quote, superfici, arredi schematici
  - Legenda colori per zone funzionali
- Prospetto sud-est (scala 1:100)
  - Materiali annotati (sasso, piode, legno, vetro)
  - Quote altezze (gronda, colmo)
  - Contesto (prato, montagne)

### 06 — Relazione Energetica Legge 10 (DOCX)
- Dati climatici zona E/F
- Trasmittanze limite (pareti, tetto, pavimento, serramenti)
- Bilancio energetico mensile
- Copertura FER (>90%)
- Conformità D.Lgs 199/2021, D.Lgs 192/2005
- Schema impianto (PdC + stufa + VMC + FV + batteria)

### 07 — Relazione Paesaggistica DPCM (DOCX)
- Formato DPCM 12/12/2005
- Analisi vincoli e contesto
- Descrizione intervento con vocabolario commissione
- Fotoinserimenti (5 viste)
- Compatibilità paesaggistica
- Sasso recuperato = argomento killer

### 08 — Render e Fotoinserimenti (PNG)
- Generati dalla pipeline render L1→L2→L3→L4
- 6 viste commissione + render interni per committente
- Fotoinserimenti su foto reali del sito

### 09 — Computo Metrico Estimativo (DOCX)
- Da generare dopo pianta definitiva
- Categorie: demolizioni, fondazioni, struttura acciaio, involucro, copertura,
  serramenti, impianti meccanici, impianti elettrici, FV, finiture

### 10 — Concept Board (JSX)
- Dashboard React interattiva
- 5 tab: Concept, Materiali, Sezioni, Energia, Render
- Dati progetto integrati: 130 m², 677 mc, 25 kW FV, U=0.15
- Palette materiali con campioni colore
- Sezione muro (8 strati)
- Grafico bilancio energetico mensile
- Prompt render AI per Midjourney/DALL-E/Grok

---

## GESTIONE ITERAZIONI

### Richiesta utente → quale agente attivare
| Tipo richiesta | Agente/i | Fase |
|----------------|----------|------|
| "fai il progetto completo" | TUTTI in sequenza | 0→1→2→3→4→5→6 |
| "calcola la struttura" | Strutturista | 2A |
| "fai la Legge 10" | Energy + Strutturista (carichi) | 2B |
| "fai la pianta" | Architetto | 2C |
| "prepara la paesaggistica" | Commissione + Render | 2D + 4 |
| "genera un render" | Pipeline Render L1→L4 | 4 |
| "verifica la pratica" | Geometra | 1 |
| "aggiorna i calcoli" | Strutturista | 2A |
| "fai il computo" | Tutti (serve progetto completo) | 5 |
| "fai il concept board" | Tutti (serve progetto completo) | 5 |

### Iterazioni render
1. NON ripartire da zero — leggi i file `chain/` esistenti
2. Identifica quale livello è impattato:
   - Cambio architettonico → riparti da L1
   - Cambio coordinate → riparti da L2
   - Cambio operazioni Blender → riparti da L3
   - Cambio script/render → riparti da L4
3. Aggiorna SOLO i livelli necessari e successivi

---

## PATH E CONFIGURAZIONE

- Blender: `C:/Program Files/Blender Foundation/Blender 5.0/blender.exe`
- Foto sorgenti: `C:/Users/Stramba/Desktop/ca del papa/foto/` (1.jpeg, 2.jpeg, 3.jpeg, 4.jpeg)
- Output render: `output/` e/o `Desktop/ca del papa/foto/`
- Deliverables: `deliverables/`
- Naming render: `{n}_render.png` — MAI sovrascrivere le foto originali
- Script render: `chain/L4_script.py` — eseguibile con `blender --background --python`
- Script DEVE usare `Path(__file__)` per path relativi

## VINCOLI ASSOLUTI

1. NON inventare dimensioni — usa SOLO quelle dalla knowledge base
2. NON ignorare vincoli della commissione paesaggistica
3. NON cambiare decisioni precedenti senza motivazione esplicita
4. NON generare interni nei render per la commissione
5. NON sovrascrivere foto originali — usare suffisso _render
6. NON usare `scene.node_tree` — Blender 5.0
7. NON usare `NISHITA` sky type — Blender 5.0
8. NON usare Boolean solver `FAST` — Blender 5.0
9. NON generare script render parziali — deve essere COMPLETO e AUTONOMO
10. Conflitti tra agenti → vincolo più restrittivo vince
11. Ogni calcolo strutturale → DISCLAIMER: richiede firma ingegnere
12. Vocabolario commissione: MAI dire "acciaio", MAI dire "casa passiva", MAI mostrare FV
13. LEGGERE knowledge/ PRIMA di qualsiasi generazione
14. AGGIORNARE knowledge/03-documenti-prodotti.md dopo ogni generazione
