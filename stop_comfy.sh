#!/bin/bash

# Directory where PID file is stored
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
PID_FILE="$PROJECT_DIR/comfyui.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "🛑 Stopping ComfyUI (PID: $PID)..."
    kill "$PID" 2>/dev/null || pkill -f "python3 main.py --listen 0.0.0.0"
    rm "$PID_FILE"
    echo "✅ ComfyUI stopped."
else
    echo "⚠️ No PID file found. Attempting pkill..."
    pkill -f "python3 main.py --listen 0.0.0.0"
    echo "✅ Done."
fi
