# L1 — Decisioni Architettoniche
## Timestamp: 2026-02-26T10:00:00+01:00
## Richiesta: Genera il render della casa vista dal prato a sud, con fotoinserimento sulla foto del rudere (1.jpeg)

## Elementi architettonici

### 1. Involucro
- Pianta: 11.0 × 8.0 m, 88 mq (sedime catastale) + 10% ampliamento = ~97 mq
- Altezza gronda: 3.0 m
- Altezza colmo: 4.8 m
- Spessore muri: 0.45 m (sandwich 8 strati)
- Materiale esterno: sasso locale recuperato dalla demolizione + integrazione
- Finitura: pietra a vista con fughe di malta grigio chiara

### 2. Copertura
- Tipo: asimmetrico, colmo offset 1.5 m verso nord
- Materiale: piode (lose in pietra locale) — OBBLIGATORIO per NAF
- Pendenza falda sud: ~70% (colmo offset verso nord = falda sud più lunga)
- Pendenza falda nord: ~30% (falda nord più corta e ripida)
- Sporto gronda: 0.40 m con teste di trave a vista
- Spessore copertura: 0.18 m (struttura + piode)

### 3. Aperture

#### 3.1 Vetrata angolo SUD-OVEST
- Nome: Vetrata angolo SW
- Facciata: SUD + OVEST (angolo)
- Tipo: vetrata fissa senza montante all'angolo
- Dimensioni: 2.40 × 2.40 m per lato (2 lastre 1.20×2.40 per lato)
- Posizione: angolo sud-ovest, davanzale a 0.40 m da terra
- Materiale telaio: alluminio nero (nascosto nei muri)
- Vetro: triplo standard, guarnizione silicone strutturale all'angolo (10-15mm)
- Struttura: HEB 180 nascosto in controsoffitto + UPN nei muri

#### 3.2 Finestra sud 1
- Nome: Finestra sud centrale
- Facciata: SUD
- Tipo: finestra
- Dimensioni: 1.20 × 1.40 m
- Posizione: centro-destra della facciata sud, davanzale a 0.90 m
- Materiale telaio: legno scuro
- Vetro: triplo

#### 3.3 Porta ingresso
- Nome: Porta ingresso
- Facciata: SUD
- Tipo: porta
- Dimensioni: 1.00 × 2.20 m
- Posizione: a destra della vetrata angolo, 3.5 m dal bordo ovest
- Materiale: legno scuro massello

#### 3.4 Finestra ovest
- Nome: Finestra ovest
- Facciata: OVEST
- Tipo: finestra
- Dimensioni: 1.00 × 1.20 m
- Posizione: centro della facciata ovest (nord della vetrata angolo), davanzale a 0.90 m
- Materiale telaio: legno scuro

#### 3.5 Finestra est 1
- Nome: Finestra est 1
- Facciata: EST
- Tipo: finestra
- Dimensioni: 1.00 × 1.20 m
- Posizione: a 3.0 m dal bordo sud, davanzale a 0.90 m
- Materiale telaio: legno scuro

#### 3.6 Finestra est 2
- Nome: Finestra est 2
- Facciata: EST
- Tipo: finestra
- Dimensioni: 1.00 × 1.20 m
- Posizione: a 7.0 m dal bordo sud, davanzale a 0.90 m
- Materiale telaio: legno scuro

#### 3.7 Finestra nord 1
- Nome: Finestra nord 1
- Facciata: NORD
- Tipo: finestra
- Dimensioni: 0.80 × 1.00 m
- Posizione: a 3.5 m dal bordo ovest, davanzale a 1.20 m
- Materiale telaio: legno scuro

#### 3.8 Finestra nord 2
- Nome: Finestra nord 2
- Facciata: NORD
- Tipo: finestra
- Dimensioni: 0.80 × 1.00 m
- Posizione: a 7.5 m dal bordo ovest, davanzale a 1.20 m
- Materiale telaio: legno scuro

### 4. Elementi speciali
- Comignolo: pietra locale, 0.60 × 0.60 m, altezza 1.0 m sopra il colmo, posizione centrata
- Travi gronda: sezione 0.15 × 0.20 m, spaziatura 0.60 m, legno scuro, teste a vista sporgenti 0.10 m oltre la facciata
- FV: 35 pannelli full-black sulla falda sud — NON visibili da questa vista (dal basso)

### 5. Vista richiesta
- Punto di vista: dal prato a sud, altezza occhi (~1.60 m), a ~16 m dall'edificio
- Fotoinserimento: SÌ, su foto 1.jpeg (vista del rudere dal prato sud)
- Elementi di contesto: tutto il prato, cielo, montagne, edifici circostanti dalla foto originale

## Decisioni e motivazioni
1. **Vetrata al SW (non SE):** il committente ha specificato angolo sud-ovest per massimizzare vista valle
2. **Altezze corrette a 3.0/4.8m:** il committente ha corretto le altezze originali della scheda (5.5/7.5 erano per 2 piani, questo è 1 piano + soppalco)
3. **Porta sul lato sud:** accessibilità dal prato, posizione tradizionale
4. **Finestre nord piccole:** tradizione alpina, minor dispersione termica, vincolo commissione
5. **Comignolo in pietra:** obbligatorio per commissione paesaggistica (anti-pattern: MAI comignolo non in pietra)

## Conflitti risolti
- Vetrata angolo vs commissione: ammessa se "integrata nel contesto" — telaio nascosto, proporzioni calibrate, non visibile da Via Orti (nord)
- FV vs paesaggio: pannelli full-black integrati in falda, non visibili dalle viste nord (commissione)
