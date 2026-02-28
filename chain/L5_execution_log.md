# L5 — Flux Render Log

## Status: PIPELINE VERIFIED (CPU-limited)

## Timestamp: 2026-02-28T02:35:00

## Setup
- ComfyUI v0.15.1 installed at C:/Users/Stramba/casa/Homeforge-ComfyUI
- Models: flux1-dev-Q4_K_S.gguf, clip_l, t5xxl_fp8, ae.safetensors, flux-controlnet-union
- Custom nodes: ComfyUI-GGUF, ComfyUI-Advanced-ControlNet, comfyui_controlnet_aux, was-node-suite-comfyui
- Mode: CPU-only (GTX 1050 driver too old for CUDA)

## Pipeline Test Results
- Workflow accepted by ComfyUI API: YES
- Models loaded successfully: YES (UNET GGUF, DualCLIP, VAE, ControlNet Union)
- ControlNet with VAE input: YES (fixed)
- Sampling started: YES (euler, simple scheduler, cfg=1.0)
- CPU performance: ~3-5 min/step at 512x384, ~10-15 min/step at 1024x768
- Full 20-step render at 1024x768: estimated 3-5 hours on CPU

## Known Issues (resolved in code)
1. ComfyUI-Manager stderr wrapper crash on Windows cp1252 -> patched logger.py
2. ControlNetApplyAdvanced requires VAE input for Flux -> added vae connection
3. Unicode arrow in print -> replaced with ASCII

## Hardware Note
GPU upgrade or NVIDIA driver update needed for practical usage.
With a modern GPU (RTX 3060+), generation would take 30-60 seconds.

## Input Files
- Grezzo: output/test_L4_grezzo.png (635 KB)
- Depth: output/test_L4_depth.png (178 KB)
- Canny: output/test_L4_canny.png (408 KB)
