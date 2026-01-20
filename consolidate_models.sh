#!/bin/bash

# Configuration
SOURCE_MODELS="/mnt/scratch/models"
COMFY_MODELS="/mnt/scratch/projects/ComfyUI/models"

echo "--- 🔍 Phase 1: Auditing Models ---"

function check_vram() {
    FILE=$1
    SIZE=$(du -bg "$FILE" | cut -f1)
    if [ "$SIZE" -gt 12 ]; then
        echo "⚠️ High VRAM (>12GB): May need quantization or 4-bit loading."
    else
        echo "✅ Compatible with 12GB VRAM."
    fi
}

# Audit Source
for dir in "Checkpoints" "text_encoders" "VAE" "diffusion_models" "LoRAs"; do
    echo "Auditing $SOURCE_MODELS/$dir..."
    if [ -d "$SOURCE_MODELS/$dir" ]; then
        ls -lh "$SOURCE_MODELS/$dir"
    else
        echo "Directory $SOURCE_MODELS/$dir not found."
    fi
done

echo -e "\n--- 🛠️ Phase 2: Optimizing & Consolidating ---"

# 1. Delete unusable models
echo "Pruning unusable models..."
SPACE_SAVED=0

# SD 1.5
SD15_PATH="$COMFY_MODELS/checkpoints/v1-5-pruned-emaonly-fp16.safetensors"
if [ -f "$SD15_PATH" ]; then
    SIZE=$(stat -c%s "$SD15_PATH")
    rm "$SD15_PATH"
    echo "Deleted SD 1.5: $SD15_PATH"
    SPACE_SAVED=$((SPACE_SAVED + SIZE))
fi

# Broken Flux Klein
FLUX_KLEIN_PATH="$COMFY_MODELS/unet/flux-2-klein-4b-fp8.safetensors"
if [ -f "$FLUX_KLEIN_PATH" ]; then
    SIZE=$(stat -c%s "$FLUX_KLEIN_PATH")
    rm "$FLUX_KLEIN_PATH"
    echo "Deleted broken Flux Klein: $FLUX_KLEIN_PATH"
    SPACE_SAVED=$((SPACE_SAVED + SIZE))
fi

# 2. Symlink models
echo "Creating symlinks to consolidate repository..."

function create_symlink() {
    SRC=$1
    DEST_DIR=$2
    if [ -f "$SRC" ]; then
        mkdir -p "$DEST_DIR"
        FILENAME=$(basename "$SRC")
        if [ -L "$DEST_DIR/$FILENAME" ]; then
            echo "Symlink already exists for $FILENAME"
        elif [ -f "$DEST_DIR/$FILENAME" ]; then
            echo "⚠️ File already exists at $DEST_DIR/$FILENAME, skipping symlink."
        else
            ln -s "$SRC" "$DEST_DIR/$FILENAME"
            echo "Linked $FILENAME -> $DEST_DIR"
        fi
    fi
}

create_symlink "$SOURCE_MODELS/Checkpoints/flux1-schnell-fp8.safetensors" "$COMFY_MODELS/checkpoints"
create_symlink "$SOURCE_MODELS/Checkpoints/sd_xl_base_1.0.safetensors" "$COMFY_MODELS/checkpoints"
create_symlink "$SOURCE_MODELS/diffusion_models/wan2.1_t2v_1.3B_fp16.safetensors" "$COMFY_MODELS/diffusion_models"

# Consolidate all secondary model types
echo "Linking secondary model components..."
for te in "$SOURCE_MODELS/text_encoders"/*; do [ -e "$te" ] && create_symlink "$te" "$COMFY_MODELS/clip"; done
for vae in "$SOURCE_MODELS/VAE"/*; do [ -e "$vae" ] && create_symlink "$vae" "$COMFY_MODELS/vae"; done
for lora in "$SOURCE_MODELS/LoRAs"/*; do [ -e "$lora" ] && create_symlink "$lora" "$COMFY_MODELS/loras"; done
for cn in "$SOURCE_MODELS/ControlNet"/*; do [ -e "$cn" ] && create_symlink "$cn" "$COMFY_MODELS/controlnet"; done

SAVED_GB=$(awk "BEGIN {print $SPACE_SAVED / 1024 / 1024 / 1024}")
echo -e "\n✅ Optimization Complete. Total space saved in project dir: ${SAVED_GB} GB"
