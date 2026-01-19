#!/bin/bash

# Use environment variables or defaults
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
COMFYUI_DIR="${COMFYUI_DIR:-/mnt/scratch/projects/ComfyUI}"
LOG_FILE="$PROJECT_DIR/comfyui_server.log"

# Check if ComfyUI is already running
if pgrep -f "python main.py --listen 0.0.0.0" > /dev/null; then
    echo "⚠️ ComfyUI is already running."
    exit 0
fi

# Ensure we are in the correct directory for the venv activation
cd "$PROJECT_DIR" || exit 1

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Navigate to the ComfyUI directory
if [ ! -d "$COMFYUI_DIR" ]; then
    echo "❌ ComfyUI directory not found at $COMFYUI_DIR"
    exit 1
fi
cd "$COMFYUI_DIR" || exit 1

# Start ComfyUI with the listen flag in the background
echo "🚀 Starting ComfyUI..."
python main.py --listen 0.0.0.0 > "$LOG_FILE" 2>&1 &

# Store PID
echo $! > "$PROJECT_DIR/comfyui.pid"

echo "✅ ComfyUI server started in the background (PID: $!)."
echo "📝 Log: $LOG_FILE"
