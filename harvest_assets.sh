#!/bin/bash
SOURCE_DIR="/mnt/scratch/projects/ComfyUI/output"
TARGET_DIR="/mnt/scratch/projects/Asset_Generation/outputs"
mkdir -p "$TARGET_DIR"

# Find the latest png created by our script
LATEST_FILE=$(ls -t "$SOURCE_DIR"/evergreen*.png 2>/dev/null | head -n 1)

if [ -z "$LATEST_FILE" ]; then
    echo "❌ No new evergreen files found."
    exit 1
fi

# Determine next sequence number
COUNT=$(ls "$TARGET_DIR"/evergreen_*.png 2>/dev/null | wc -l)
NEXT_NUM=$((COUNT + 1))
TARGET_NAME="evergreen_${NEXT_NUM}.png"

mv "$LATEST_FILE" "$TARGET_DIR/$TARGET_NAME"
echo "✅ Harvested: $TARGET_NAME -> $TARGET_DIR/"
