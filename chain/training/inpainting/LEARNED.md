# Inpainting con Flux — Lezioni Apprese

## 1. SetLatentNoiseMask è sufficiente per inpainting
Senza un modello Flux Fill dedicato, il metodo `SetLatentNoiseMask` funziona bene:
- VAEEncode della foto originale → latent
- Maschera applicata al latent via SetLatentNoiseMask
- KSampler con denoise < 1.0 rigenera solo l'area mascherata
- I pixel fuori maschera restano intatti nel latent space

**Risultato**: integrazione convincente senza bordi visibili.

## 2. CFG basso per Flux
Flux funziona meglio con CFG 3.0-4.0, non con i valori 7-8 tipici di Stable Diffusion.
CFG troppo alto produce artefatti e colori innaturali.

## 3. Denoise è il parametro più critico
- **0.70**: conservativo, mantiene molto della struttura originale (buono se la foto ha già forme simili)
- **0.75-0.78**: bilanciato, buon compromesso tra fedeltà e creatività
- **0.80+**: più creativo, può generare strutture più diverse dall'originale
- **<0.65**: quasi nessun cambiamento, inutile
- **>0.85**: perde troppo contesto, risultato disconnesso dall'ambiente

## 4. La maschera richiede feathering
Bordi netti nella maschera → bordi visibili nel risultato.
Feathering con GaussianBlur(12) + ramp graduale elimina il problema.
La maschera deve coprire TUTTO l'oggetto da sostituire con un margine di ~20px.

## 5. CPU è lento ma funziona
- ~4.6 min per step a 512x384
- 12 steps = 56 min per variante
- 5 varianti = ~4.5 ore totali
- Il modello GGUF Q4_K quantizzato gira bene su CPU con 32 GB RAM
- Memoria totale usata: ~12 GB (UNet 6.6 GB + CLIP 4.8 GB + VAE 0.3 GB)

## 6. Risoluzione 512x384 è il minimo pratico
- Sotto 512x384 il modello non genera dettagli sufficienti
- 768x576 migliorerebbe la qualità ma raddoppia i tempi
- Per risultati finali, considerare upscaling post-generazione

## 7. Il prompt architettonico funziona meglio se specifico
Elementi che funzionano bene nel prompt:
- Materiali specifici ("round grey river stones", "stone slab roof")
- Riferimenti al contesto ("identical to adjacent traditional buildings")
- Dettagli costruttivi ("beams protruding 40cm from eaves")
- Stile fotografico ("Canon EOS R5 with 35mm lens", "photorealistic")
- Condizioni di luce ("winter overcast natural lighting")

Elementi meno efficaci:
- Negative prompt: Flux non usa veramente il negative, usato lo stesso positive per entrambi
- Risoluzioni specifiche nel prompt ("8k"): effetto minimo a 512x384

## 8. Seed diversi → risultati diversi ma coerenti
Ogni seed genera una variante diversa della stessa interpretazione del prompt.
Questo è utile per:
- Esplorare diverse configurazioni architettoniche
- Trovare la migliore integrazione con il contesto
- Offrire scelta al committente

## 9. ComfyUI API workflow
- Queue multiple prompts in una volta sola = ComfyUI le esegue in sequenza
- Polling su `/history/{prompt_id}` per monitorare completamento
- Download immagini via `/view?filename=...&type=output`
- Il server mantiene il modello in memoria → dalla seconda generazione in poi non c'è tempo di caricamento

## 10. Errori comuni e soluzioni
| Problema | Causa | Soluzione |
|----------|-------|-----------|
| `tqdm stderr flush error` | Background process senza terminale | Redirect stderr: `2>logfile.txt` |
| `Port 8188 already in use` | Istanza precedente attiva | `taskkill //F //PID <pid>` |
| Timeout client 180s | Server già attivo, client tenta restart | Usare API dirette se server è già up |
| Maschera troppo larga | Copre alberi/cielo | Iterare poligono con overlay di verifica |

## 11. Pipeline completa
```
1. Preparare foto sorgente (site_photo.jpg nel input di ComfyUI)
2. Creare maschera con PIL (poligono + feathering)
3. Copiare maschera in ComfyUI input
4. Avviare ComfyUI (--cpu --port 8188)
5. Queue workflow via API con parametri
6. Polling /history fino a completamento
7. Download risultato via /view API
8. Valutare e iterare se necessario
```

## 12. Risultati Batch — Valutazione Comparativa (2026-02-28)

5 varianti generate a 512x384, 12 steps, sampler euler/simple:

| Variante | Seed | CFG | Denoise | Punteggio | Note |
|----------|------|-----|---------|-----------|------|
| v1 | 42 | 3.5 | 0.78 | 23/30 | Buona base, travi visibili, vetrata ok |
| v2 | 1337 | 3.5 | 0.78 | 21/30 | Troppo legno, meno pietra tradizionale |
| v3 | 2024 | 3.5 | 0.72 | 19/30 | Denoise basso → 2 piani, non single-story |
| v4 | 7777 | 4.0 | 0.80 | **24/30** | **BEST** — pietra round, vetrata nera, proporzioni giuste |
| v5 | 31415 | 3.0 | 0.70 | 23/30 | Buon tetto piode, vetrata angolare |

**Vincitore: V4** (seed=7777, cfg=4.0, denoise=0.80)
- Muri in pietra rotonda grigia coerenti con edifici adiacenti
- Vetrata grande con telaio nero e frame sottile
- Travi in legno chiaro visibili lungo la gronda
- Proporzioni single-story corrette
- Ottima integrazione fotografica con il contesto

**Insight chiave**: CFG 4.0 + denoise 0.80 produce il miglior risultato per architettura.
Il denoise più alto (0.80) permette al modello più libertà compositiva,
mentre il CFG più alto (4.0) mantiene aderenza al prompt.

## Prossimi passi per migliorare
- [ ] Provare risoluzione 768x576 (qualità superiore, ~2x tempo)
- [ ] Aggiungere ControlNet (Canny/Depth) per guidare la struttura
- [ ] Upscaling post-generazione (Real-ESRGAN o simile)
- [ ] Provare modello Flux Fill quando disponibile in GGUF
- [ ] GPU upgrade per tempi ragionevoli (<5 min per variante)
