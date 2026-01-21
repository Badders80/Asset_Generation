#!/bin/bash

SOURCE_MODELS="/mnt/scratch/models"
COMFY_MODELS="/mnt/scratch/projects/ComfyUI/models"

echo "🧹 Removing broken/outdated models..."
rm -f "$COMFY_MODELS/checkpoints/v1-5-pruned-emaonly-fp16.safetensors"
rm -f "$COMFY_MODELS/unet/flux-2-klein-4b-fp8.safetensors"

echo "🔗 Symlinking Flux Schnell..."
mkdir -p "$COMFY_MODELS/checkpoints"
ln -sf "$SOURCE_MODELS/Checkpoints/flux1-schnell-fp8.safetensors" "$COMFY_MODELS/checkpoints/flux1-schnell-fp8.safetensors"

echo "🔗 Symlinking Wan2.1 video model..."
mkdir -p "$COMFY_MODELS/diffusion_models"
ln -sf "$SOURCE_MODELS/diffusion_models/wan2.1_t2v_1.3B_fp16.safetensors" "$COMFY_MODELS/diffusion_models/wan2.1_t2v_1.3B_fp16.safetensors"

echo "🔗 Symlinking other components..."
for te in "$SOURCE_MODELS/text_encoders"/*; do [ -e "$te" ] && ln -sf "$te" "$COMFY_MODELS/clip/"; done
for vae in "$SOURCE_MODELS/VAE"/*; do [ -e "$vae" ] && ln -sf "$vae" "$COMFY_MODELS/vae/"; done
for lora in "$SOURCE_MODELS/LoRAs"/*; do [ -e "$lora" ] && ln -sf "$lora" "$COMFY_MODELS/loras/"; done
for cn in "$SOURCE_MODELS/ControlNet"/*; do [ -e "$cn" ] && ln -sf "$cn" "$COMFY_MODELS/controlnet/"; done

echo "✅ Consolidation complete!"
ls -lh "$COMFY_MODELS/checkpoints/"
