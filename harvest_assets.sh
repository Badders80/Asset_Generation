#!/bin/bash
# Use environment variables or defaults
SOURCE_DIR="${COMFYUI_OUTPUT_DIR:-/mnt/scratch/projects/ComfyUI/output}"
TARGET_DIR="${ASSET_TARGET_DIR:-$(pwd)/outputs}"
PREFIX="${ASSET_PREFIX:-evergreen}"

mkdir -p "$TARGET_DIR"

# Find the latest png created by our script
LATEST_FILE=$(ls -t "$SOURCE_DIR"/${PREFIX}*.png 2>/dev/null | head -n 1)

if [ -z "$LATEST_FILE" ]; then
    echo "❌ No new ${PREFIX} files found in $SOURCE_DIR"
    exit 1
fi

# Determine next sequence number by finding the max existing number
MAX_NUM=$(ls "$TARGET_DIR"/${PREFIX}_*.png 2>/dev/null | grep -oP "${PREFIX}_\K[0-9]+" | sort -n | tail -n 1)
if [ -z "$MAX_NUM" ]; then
    NEXT_NUM=1
else
    NEXT_NUM=$((MAX_NUM + 1))
fi

TARGET_NAME="${PREFIX}_${NEXT_NUM}.png"

mv "$LATEST_FILE" "$TARGET_DIR/$TARGET_NAME"
echo "✅ Harvested: $TARGET_NAME -> $TARGET_DIR/"
