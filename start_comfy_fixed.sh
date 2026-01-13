#!/bin/bash

# Ensure we are in the correct directory for the venv activation
cd /mnt/scratch/projects/Asset_Generation

# Activate the virtual environment
source venv/bin/activate

# Navigate to the ComfyUI directory
cd /mnt/scratch/projects/ComfyUI

# Start ComfyUI with the listen flag in the background
# Redirect output to a log file for debugging
python main.py --listen 0.0.0.0 > ../Asset_Generation/comfyui_server.log 2>&1 &

# Deactivate the virtual environment in this shell after launching the background process
deactivate

echo "ComfyUI server started in the background. Check /mnt/scratch/projects/Asset_Generation/comfyui_server.log for output."
