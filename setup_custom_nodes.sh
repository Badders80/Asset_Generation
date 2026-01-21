#!/bin/bash

# Configuration
COMFYUI_DIR="${COMFYUI_DIR:-/mnt/scratch/projects/ComfyUI}"
CUSTOM_NODES_DIR="$COMFYUI_DIR/custom_nodes"

echo "🛠️  Evolution Stables: ComfyUI Custom Node Setup"
echo "------------------------------------------------"

if [ ! -d "$CUSTOM_NODES_DIR" ]; then
    echo "❌ ComfyUI custom_nodes directory not found at $CUSTOM_NODES_DIR"
    echo "Please set COMFYUI_DIR environment variable if it's in a different location."
    exit 1
fi

cd "$CUSTOM_NODES_DIR" || exit 1

# Function to install/update a node
install_node() {
    local repo_url="$1"
    local dir_name=$(basename "$repo_url" .git)

    if [ -d "$dir_name" ]; then
        echo "✅ $dir_name already exists. Pulling latest changes..."
        cd "$dir_name" && git pull && cd ..
    else
        echo "📥 Installing $dir_name..."
        git clone "$repo_url"
    fi
}

# 1. Wan2.1 Nodes
install_node "https://github.com/Wan-Video/ComfyUI-Wan.git"

# 2. Video Helper Suite (Required for VideoCombine and high-quality encoding)
install_node "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git"

# 3. ControlNet Nodes (Optional but recommended for Paint-by-Numbers)
# install_node "https://github.com/Fannovel16/comfyui_controlnet_aux.git"

echo ""
echo "📦 Installing Python dependencies for custom nodes..."
# Try to find the venv
if [ -d "../../venv" ]; then
    source "../../venv/bin/activate"
    pip install -r ComfyUI-Wan/requirements.txt
    pip install -r ComfyUI-VideoHelperSuite/requirements.txt
elif command -v pip3 &> /dev/null; then
    pip3 install -r ComfyUI-Wan/requirements.txt
    pip3 install -r ComfyUI-VideoHelperSuite/requirements.txt
else
    echo "⚠️  Could not find pip to install requirements. Please install them manually."
fi

echo ""
echo "🎉 Setup complete! Please restart ComfyUI using ./start_comfy_fixed.sh"
echo "------------------------------------------------"
