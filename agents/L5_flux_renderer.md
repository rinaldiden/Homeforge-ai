# L5 — Flux Renderer (Render Grezzo → Immagine Fotorealistica)

## Ruolo
Prendi il render grezzo di Blender (geometria corretta con materiali base) e trasformalo in un'immagine fotorealistica utilizzando ComfyUI + Flux con ControlNet (depth + canny).

## Input
- `output/test_L4_grezzo.png` — Render Blender con geometria e materiali base grigi
- `output/test_L4_depth.png` — Depth map dalla camera Blender
- `output/test_L4_canny.png` — Canny edge map (bordi netti della geometria)
- `chain/L1_architect_decisions.md` — Decisioni architettoniche (per generare il prompt)

## Output
- `output/test_L5_fotorealistico.png` — Immagine fotorealistica generata da Flux

## Workflow

### 1. Genera Prompt
Usa `prompt_engineer_flux.py` per leggere L1 e generare il prompt Flux ottimizzato:
- Materiali reali (sasso, piode, legno scuro)
- Stile fotografico professionale
- Contesto alpino Valtellina
- Vista corretta (sud, nord, etc.)

### 2. Genera Immagine
Usa `comfy_flux_client.py` per inviare a ComfyUI:
```python
from comfy_flux_client import ComfyFluxClient
from prompt_engineer_flux import PromptEngineerFlux

engineer = PromptEngineerFlux()
prompt_data = engineer.generate_prompt()

client = ComfyFluxClient()
result = client.generate_render(
    prompt=prompt_data["positive"],
    depth_map_path="output/test_L4_depth.png",
    canny_map_path="output/test_L4_canny.png",
    output_name="test_L5_fotorealistico",
    width=1024,
    height=768,
    steps=20
)
```

### 3. Parametri ControlNet
- **Depth**: strength 0.65, end_percent 0.85 — guida la struttura 3D
- **Canny**: strength 0.50, end_percent 0.70 — preserva bordi architettonici
- Se la geometria è troppo "soft", aumentare canny strength a 0.60
- Se troppo rigida/artificiale, ridurre depth strength a 0.50

### 4. Qualità
- Steps: 20 (default), 30 per qualità alta
- CFG: 1.0 (Flux funziona meglio con CFG basso)
- Dimensioni: 1024×768 (landscape architettonico)
- Sampler: euler + simple scheduler

## ControlNet Mode Union
Il modello `flux-controlnet-union.safetensors` supporta più modalità:
- mode 0: canny
- mode 1: tile
- mode 2: depth
- mode 3: blur
- mode 4: pose
- mode 5: gray
- mode 6: low quality

Per archviz usiamo depth (mode 2) + canny (mode 0).

## Hardware Note
Con GTX 1050 4GB + Flux GGUF Q4_K_S:
- Il modello viene eseguito su CPU (RAM ~16GB richiesti)
- Tempo stimato: 5-15 minuti per immagine
- T5XXL fp8 su CPU: ~2 min per encoding
- Ridurre steps a 15 se troppo lento

## Anti-Pattern
- NON usare CFG alto (>3.0) con Flux — produce artefatti
- NON generare a risoluzione >1280 — CPU troppo lento
- NON ignorare le ControlNet maps — senza, Flux genera geometria casuale
- NON cambiare il sampler da euler — è il più stabile per Flux
- NON usare negative prompt lungo — Flux non li gestisce bene

## Execution Log → `chain/L5_execution_log.md`
```markdown
# L5 — Flux Render Log
## Timestamp: [ISO 8601]
## Prompt: [testo usato]
## ControlNet: depth=[sì/no], canny=[sì/no]
## Settings: steps=[n], cfg=[n], size=[WxH]

## Result
- Status: [SUCCESS/FAILED]
- Generation time: [seconds]
- Output: [path]
- Quality assessment: [note sulla qualità]
```
