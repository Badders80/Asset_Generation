#!/bin/bash

# Configuration
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
COMFYUI_DIR="${COMFYUI_DIR:-/mnt/scratch/projects/ComfyUI}"
LOG_FILE="$PROJECT_DIR/comfyui_server.log"

# Optional: Clean restart
if [[ "$1" == "--clean" ]]; then
    echo "🧹 Killing existing ComfyUI processes..."
    pkill -f "main.py --listen 0.0.0.0" || true
    sleep 2
fi

# Check if ComfyUI is already running
if pgrep -f "python3 main.py --listen 0.0.0.0" > /dev/null; then
    echo "⚠️ ComfyUI is already running."
    exit 0
fi

# Ensure we are in the project root
cd "$PROJECT_DIR" || exit 1

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Navigate to ComfyUI
if [ ! -d "$COMFYUI_DIR" ]; then
    echo "❌ ComfyUI directory not found at $COMFYUI_DIR"
    exit 1
fi
cd "$COMFYUI_DIR" || exit 1

# Start ComfyUI with optimized flags for RTX 3060 12GB
echo "🚀 Starting ComfyUI (Optimized for RTX 3060 12GB)..."
# --force-fp16: Speed up on RTX 30 series
# --disable-smart-memory: Prevent overhead on 12GB cards
# No --highvram (as requested)
python3 main.py --listen 0.0.0.0 --force-fp16 --disable-smart-memory > "$LOG_FILE" 2>&1 &

# Store PID
echo $! > "$PROJECT_DIR/comfyui.pid"

echo "✅ ComfyUI started in background (PID: $!)."
echo "📝 Log: $LOG_FILE"
