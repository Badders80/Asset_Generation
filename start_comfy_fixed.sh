#!/bin/bash

# Use environment variables or defaults
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
COMFYUI_DIR="${COMFYUI_DIR:-/mnt/scratch/projects/ComfyUI}"
LOG_FILE="$PROJECT_DIR/comfyui_server.log"

# Optional: Clean restart
if [[ "$1" == "--clean" ]]; then
    echo "🧹 Killing existing ComfyUI processes..."
    pkill -f "python main.py --listen 0.0.0.0" || true
    sleep 2
fi

# Check if ComfyUI is already running
if pgrep -f "python main.py --listen 0.0.0.0" > /dev/null; then
    echo "⚠️ ComfyUI is already running. Use --clean for a fresh start."
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

# Start ComfyUI with optimized flags for RTX 3060 12GB
echo "🚀 Starting ComfyUI with RTX 3060 optimizations..."
# Optimizations: force-fp16 for speed, disable-smart-memory to prevent overhead
# We explicitly avoid --highvram as recommended for this specific card
python main.py --listen 0.0.0.0 --force-fp16 --disable-smart-memory > "$LOG_FILE" 2>&1 &

# Store PID
echo $! > "$PROJECT_DIR/comfyui.pid"

echo "✅ ComfyUI server started in the background (PID: $!)."
echo "📝 Log: $LOG_FILE"
