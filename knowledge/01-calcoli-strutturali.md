# 🔩 Knowledge Base — Calcoli Strutturali

## Struttura portante v3
- **Tipologia:** telai trasversali in acciaio S355 JR
- **Schema:** portali trasversali (luce ~7-8m) + travi longitudinali + controventi
- **Filosofia:** incastri laser BLM Group (tab-and-slot) > bulloni > saldatura
- **Saldatura:** SOLO in officina per nodi a momento

## Profili ottimizzati (v2→v3)
| Elemento | Profilo v1 | Profilo v3 | Risparmio |
|----------|-----------|-----------|-----------|
| Colonne | HEB 200 | HEB 160 | -33% peso |
| Travi portale | IPE 270 | IPE 270 (invariato) | 0% (89% util.) |
| Travi secondarie | IPE 200 | IPE 160 | -29% |
| Travi tetto | IPE 220 | IPE 200 | -15% |
| Arcarecci | IPE 160 | IPE 140 | -16% |
| Controventi | TUB 100²×5 | TUB 80²×4 | -38% |

## Peso totale
| | v1 | v3 |
|--|----|----|
| Profili | 7,426 kg | ~5,875 kg |
| Hardware (bulloni/piastre) | 1,120 kg | ~350 kg |
| **TOTALE** | **8,550 kg** | **~6,220 kg (-27%)** |
| Bulloni | 640 pz | ~180 pz (-72%) |
| Costo stima | €39-50k | €27.5-36k |
| Montaggio | 5-6 gg | 3-4 gg |

## Carichi di progetto
- **Neve:** qs = 2.0-2.5 kN/m² (zona III, as = 580m, Ce=1.0, Ct=1.0)
- **Piode:** 150 kg/m² = 1.5 kN/m² (NON sottovalutare)
- **FV full-black 575W:** ~15 kg/m² = 0.15 kN/m²
- **Vento:** qb ≈ 0.39 kN/m² (zona 1), ce = 1.7-2.0
- **Sisma:** zona 3-4, ag = 0.05-0.10g, suolo B/C

## Nodi laser-cut
| Nodo | Tipo | Bulloni |
|------|------|---------|
| N1 Base colonna | Piastra + tirafondi | 4×M24 |
| N2 Trave-Colonna (momento) | Tab-slot + 2 bull. | 2×M20 |
| N3 Secondaria (taglio) | Incastro puro | 0-1×M16 |
| N4 Controvento | Incastro + 2 bull. | 2×M16 |
| N5 Vetrata | Telaio saldato officina | 4×M20 |
| N6 Arcarecci | Tab-slot puro | 0 |
| N7 Soppalco | Incastro + 1 bull. | 1×M16 |

## Vetrata angolo (v3)
- **Dimensione ottimale:** 2.40 × 2.40 m per lato
- **Telaio portante:** HEB 180 nascosto in controsoffitto + UPN nei muri
- **Vetro:** triplo standard a catalogo (2 lastre 1.20×2.40 per lato)
- **Angolo:** guarnizione silicone strutturale 10-15mm (no montante)
- **Risparmio vs structural glazing:** €10,000-15,000

## Sasso dalla demolizione
- Facciate totali: ~140 m², spessore 80-120mm → ~14-17 m³ necessari
- Recuperabile dal rudere: ~10-12 m³ (40-50% muri esistenti)
- Da acquistare: ~4-6 m³ (risparmio €3-5k)

## Fondazioni (da verificare con geotecnico)
- Tipo: plinti collegati o platea alleggerita
- Profondità: minimo 80cm (gelo)
- Terreno presunto: ghiaie e sabbie di conoide (buona portata)
