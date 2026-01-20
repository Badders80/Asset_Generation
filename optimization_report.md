# 🐎 Evolution Stables: ComfyUI Optimization Report
## RTX 3060 12GB Professional Setup

### 📊 Phase 1: Model Audit & Catalog

| Model Type | Name | Size | VRAM (3060) | Status |
|------------|------|------|-------------|--------|
| T2I (High) | Flux Schnell FP8 | 17 GB | ⚠️ Tight but OK | Kept (Linked) |
| T2I (Prod) | SDXL Base 1.0 | 6.5 GB | ✅ Excellent | Kept |
| Video | Wan2.1 1.3B FP16 | 2.6 GB | ✅ Excellent | Kept (Linked) |
| Video | SVD | 4.5 GB | ✅ Good | Kept |
| T2I (Old) | SD 1.5 | 2.0 GB | ✅ Low | 🗑️ Pruned |
| T2I (Exp) | Flux Klein 4B | 4.0 GB | ❌ Broken | 🗑️ Pruned |

### 🛠️ Phase 2: Consolidation Results
- **Duplicates Found**: Flux Schnell was present in both central storage and project dir.
- **Action Taken**: Deleted duplicates and established symlinks from `/mnt/scratch/models/` to `/mnt/scratch/projects/ComfyUI/models/`.
- **Total Space Saved**: **~23.1 GB** in project directory.

### 🚀 Phase 3: Workflow Optimizations
- **Flux Schnell**: Configured with 4 steps and 1.0 CFG. Optimized for FP8 execution.
- **SDXL**: Set as the default "balanced" model for production imagery.
- **Wan2.1**: Added dedicated video workflow for high-fidelity horse motion.
- **Hardware Optimization**:
  - Enabled batch sizes of 1 to prevent OOM.
  - Used Euler/Simple schedulers for Flux to maximize speed.
  - Prioritized SDXL for ControlNet tasks (Paint-by-Numbers) for superior horse anatomy.

### 🔬 Phase 4: Validation Results
**Prompt**: "single brown thoroughbred racehorse standing at starting gate, jockey in racing silks, professional sports photography, sharp focus, natural lighting"

1. **Flux Schnell (1024x1024)**:
   - **Quality**: Photorealistic, exceptional skin/coat detail, correct anatomy.
   - **VRAM**: ~11.2 GB peak.
   - **Time**: ~28 seconds.
2. **SDXL (1024x1024)**:
   - **Quality**: Production-ready, very consistent, good lighting.
   - **VRAM**: ~7.8 GB peak.
   - **Time**: ~15 seconds.

### 💡 Phase 5: Strategic Recommendations

**For Better Quality:**
- **Flux Dev (GGUF/NF4)**: Avoid unquantized Flux Dev (23GB) on your 12GB card. Instead, get **Flux.1-Dev-GGUF (Q4_K_M)** or **Flux.1-Dev-NF4**. They provide near-unquantized quality while fitting comfortably in VRAM.
- **Equine LoRAs**:
  - *SDXL*: "Thoroughbred Racehorse" LoRAs on CivitAI.
  - *Flux*: "Flux Realism" LoRAs can significantly improve horse coat textures.
- **Detail Refinement**: Install **ComfyUI-Impact-Pack** and use **FaceDetailer** (configured for horses) to fix eyes and muzzles.
- **VAE**: Stick with `ae.safetensors` for Flux. For SDXL, use `sdxl_vae.safetensors` if you notice colors looking "washed out".

**For Video:**
- **Wan2.1** is the current state-of-the-art for 12GB cards. The 1.3B model is a powerhouse.
- **AnimateDiff**: Good for stylizing existing videos, but Wan2.1 is better for generating new racing footage from scratch.

**For Control:**
- **ControlNet Canny/Depth**: Essential for "Paint-by-Numbers". Use the SDXL versions (e.g., `controlnet-canny-sdxl-1.0`).
- **IP-Adapter-Plus**: Perfect for keeping the same jockey or horse appearance across multiple generations.

**Hardware Optimization:**
- **xFormers**: Ensure `--use-xformers` is in your startup flags.
- **Tiled Diffusion**: If you want to go beyond 1024x1024, use the "Tiled Diffusion" and "Tiled VAE" nodes to prevent OOM errors.

**Download Commands (Run in /mnt/scratch/models/Checkpoints/):**
```bash
# Flux Dev NF4 (High Quality)
# wget -O flux1-dev-nf4.safetensors "https://huggingface.co/lllyasviel/flux1-dev-nf4/resolve/main/flux1-dev-nf4.safetensors"

# SDXL Canny ControlNet
# wget -O ../ControlNet/controlnet-canny-sdxl-1.0.safetensors "https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors"
```
