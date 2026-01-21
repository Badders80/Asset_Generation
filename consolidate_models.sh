#!/bin/bash

# Define paths
SOURCE_DIR="/mnt/scratch/models"
COMFY_DIR="/mnt/scratch/projects/ComfyUI/models"

echo "🐎 Evolution Stables: Advanced Model Consolidation"

# Function to create directories and link
safe_link() {
    local src="$1"
    local dest_dir="$2"
    local name=$(basename "$src")

    if [ ! -e "$src" ]; then
        echo "⚠️ Source missing: $src"
        return
    fi

    mkdir -p "$dest_dir"
    ln -sf "$src" "$dest_dir/$name"
    echo "✅ Linked: $name"
}

echo "🧹 Pruning legacy/broken files..."
rm -f "$COMFY_DIR/checkpoints/v1-5-pruned-emaonly-fp16.safetensors"
rm -f "$COMFY_DIR/unet/flux-2-klein-4b-fp8.safetensors"

echo "🔗 Linking Core Models..."
# Flux Schnell (17GB)
safe_link "$SOURCE_DIR/Checkpoints/flux1-schnell-fp8.safetensors" "$COMFY_DIR/unet"

# SDXL Base
# Already at $COMFY_DIR/checkpoints/sd_xl_base_1.0.safetensors - no action needed

# Wan 2.1 Video
safe_link "$SOURCE_DIR/diffusion_models/wan2.1_t2v_1.3B_fp16.safetensors" "$COMFY_DIR/unet"
safe_link "$SOURCE_DIR/VAE/wan_2.1_vae.safetensors" "$COMFY_DIR/vae"

# Motion Module (AnimateDiff)
safe_link "$SOURCE_DIR/Checkpoints/mm_sdxl_v10_beta.ckpt" "$COMFY_DIR/checkpoints"

echo "🔗 Linking Supporting Encoders..."
# Flux Encoders
safe_link "$SOURCE_DIR/clip/umt5_xxl_fp8_e4m3fn_scaled.safetensors" "$COMFY_DIR/clip"
# Others are likely already in $COMFY_DIR/clip based on audit

echo "✅ Consolidation complete!"
