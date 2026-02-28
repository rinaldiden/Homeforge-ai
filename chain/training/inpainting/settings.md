# Inpainting Settings — Flux via ComfyUI (CPU)

## Hardware
- CPU only (NVIDIA GTX 1050 driver troppo vecchio per CUDA)
- 32 GB RAM
- pytorch 2.10.0+cpu
- ComfyUI v0.15.1

## Modelli
| Modello | File | Dimensione |
|---------|------|------------|
| UNet | `flux1-dev-Q4_K_S.gguf` | 6.4 GB (Q4_K quantizzato) |
| CLIP L | `clip_l.safetensors` | ~250 MB |
| T5-XXL | `t5xxl_fp8_e4m3fn.safetensors` | ~4.5 GB (FP8) |
| VAE | `ae.safetensors` | ~320 MB |

**Nota**: Non è disponibile un modello Flux Fill/Inpainting dedicato.
L'inpainting è realizzato con `SetLatentNoiseMask` sul modello standard flux1-dev.

## Workflow ComfyUI (14 nodi)
```
LoadImage(photo) → ImageScale → VAEEncode ──┐
LoadImage(mask) → ImageScale → ImageToMask ──┤
                                              ├→ SetLatentNoiseMask → KSampler → VAEDecode → SaveImage
UnetLoaderGGUF ──────────────────────────────┤
DualCLIPLoader → CLIPTextEncode ─────────────┘
VAELoader ───────────────────────────────────┘
```

## Parametri Ottimali
| Parametro | Valore | Note |
|-----------|--------|------|
| Risoluzione | 512x384 | Aspect ratio 4:3, bilancio qualità/tempo su CPU |
| Steps | 12 | 8 = troppo pochi, 12 = buon compromesso, 20+ = troppo lento su CPU |
| CFG | 3.0-4.0 | Flux lavora meglio con CFG basso (non 7-8 come SD) |
| Denoise | 0.70-0.80 | <0.65 = troppo simile all'originale, >0.85 = perde contesto |
| Sampler | euler | Stabile e veloce |
| Scheduler | simple | Funziona bene con Flux |

## Tempi di Esecuzione (CPU)
| Steps | Risoluzione | Tempo/step | Tempo totale |
|-------|-------------|------------|--------------|
| 8 | 512x384 | ~4.6 min | ~38 min |
| 12 | 512x384 | ~4.7 min | ~56 min |
| 20 | 512x384 | ~4.7 min | ~94 min (stimato) |

## Prompt Text
```
Restored single-story alpine stone house, walls made of round grey river stones
identical to the adjacent traditional buildings, asymmetric stone slab roof (piode)
with long gentle south slope and short steep north slope, ridge offset toward the back,
light-colored natural wood beams protruding 40cm from the eaves,
full-height corner glazing on the right corner wrapping around with no vertical mullion
and thin black aluminum frame, dark glass reflecting the landscape,
one french door with black frame on the front facade,
one small window with light wood frame on the left side,
solid light wood entrance door, stone chimney on the back roof slope,
copper rain gutter along the eaves,
winter overcast natural lighting, photorealistic architectural photography,
8k, shot on Canon EOS R5 with 35mm lens
```

## Varianti Testate
| Variante | Seed | Steps | CFG | Denoise | Note |
|----------|------|-------|-----|---------|------|
| test | 42 | 8 | 3.5 | 0.75 | Primo test, risultato promettente |
| v1 | 42 | 12 | 3.5 | 0.78 | Stesso seed, più steps → più dettaglio |
| v2 | 1337 | 12 | 3.5 | 0.78 | Seed diverso |
| v3 | 2024 | 12 | 3.5 | 0.72 | Denoise più basso → più fedele all'originale |
| v4 | 7777 | 12 | 4.0 | 0.80 | CFG più alto, denoise più alto → più creativo |
| v5 | 31415 | 12 | 3.0 | 0.70 | CFG più basso, denoise più basso → più conservativo |

## Maschera
- Formato: PNG bianco (area da sostituire) su nero (area da preservare)
- File sorgente: `photos/site_photo.jpg` (2040x1530)
- Poligono rudere: x 520-1410, y 195-930
- Feathering: GaussianBlur(radius=12) + threshold ramp (30-200)
- Canale usato per conversione: rosso (`ImageToMask` channel=red)
