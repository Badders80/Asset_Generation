#!/bin/bash

SOURCE_MODELS="/mnt/scratch/models"
COMFY_MODELS="/mnt/scratch/projects/ComfyUI/models"

echo "🐎 Evolution Stables: Model Consolidation"

# Ensure ComfyUI model directories exist
mkdir -p "$COMFY_MODELS/checkpoints"
mkdir -p "$COMFY_MODELS/clip"
mkdir -p "$COMFY_MODELS/vae"
mkdir -p "$COMFY_MODELS/diffusion_models"
mkdir -p "$COMFY_MODELS/loras"
mkdir -p "$COMFY_MODELS/controlnet"
mkdir -p "$COMFY_MODELS/upscale_models"

echo "🧹 Pruning unusable legacy assets..."
# Remove SD 1.5 if it exists in project checkpoints
rm -f "$COMFY_MODELS/checkpoints/v1-5-pruned-emaonly-fp16.safetensors"
# Remove broken Flux Klein
rm -f "$COMFY_MODELS/unet/flux-2-klein-4b-fp8.safetensors"

echo "🔗 Establishing single source of truth for models..."

function link_model() {
    SRC=$1
    DEST_DIR=$2
    if [ -e "$SRC" ]; then
        FILENAME=$(basename "$SRC")
        ln -sf "$SRC" "$DEST_DIR/$FILENAME"
        echo "✅ Linked $FILENAME"
    fi
}

# Main Checkpoints
link_model "$SOURCE_MODELS/Checkpoints/sd_xl_base_1.0.safetensors" "$COMFY_MODELS/checkpoints"

# Flux Models (using UNETLoader)
mkdir -p "$COMFY_MODELS/unet"
link_model "$SOURCE_MODELS/Checkpoints/flux1-schnell-fp8.safetensors" "$COMFY_MODELS/unet"

# Video Models
# Wan uses CheckpointLoaderSimple
link_model "$SOURCE_MODELS/diffusion_models/wan2.1_t2v_1.3B_fp16.safetensors" "$COMFY_MODELS/checkpoints"
link_model "$SOURCE_MODELS/Checkpoints/svd.safetensors" "$COMFY_MODELS/checkpoints"

# Components
for te in "$SOURCE_MODELS/text_encoders"/*; do [ -e "$te" ] && link_model "$te" "$COMFY_MODELS/clip"; done
for v in "$SOURCE_MODELS/VAE"/*; do [ -e "$v" ] && link_model "$v" "$COMFY_MODELS/vae"; done
for l in "$SOURCE_MODELS/LoRAs"/*; do [ -e "$l" ] && link_model "$l" "$COMFY_MODELS/loras"; done
for cn in "$SOURCE_MODELS/ControlNet"/*; do [ -e "$cn" ] && link_model "$cn" "$COMFY_MODELS/controlnet"; done

echo "✅ Consolidation complete!"
