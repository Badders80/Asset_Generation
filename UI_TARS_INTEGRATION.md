# Evolution Stables: UI-TARS Desktop Integration Plan

This guide outlines the integration of ByteDance's **UI-TARS** (Multimodal AI Agent) as an orchestration layer for the Evolution Stables AI content generation pipeline.

---

## 1. Architecture Analysis

### How UI-TARS Works
UI-TARS (User Interface Task Automation with Retrieval and Synthesis) is a next-generation end-to-end GUI agent. It differs from traditional agents by using a **Vision-Language Model (VLM)** to directly perceive the desktop screen and execute actions (mouse/keyboard) like a human.

**Key Components:**
*   **VLM Kernel:** Seed-1.5-VL or UI-TARS-1.5-7B/32B. These models can "see" screenshots and output structured actions (e.g., `click(x, y)`, `type("prompt")`).
*   **Local Operator:** A system-level driver that executes the VLM's planned actions on the OS.
*   **MCP Support:** Full integration with the Model Context Protocol (MCP), allowing the agent to call programmatic tools (Python scripts, APIs) instead of relying solely on visual clicks.

### Integration with ComfyUI System
We will utilize a **Hybrid Integration Strategy**:
1.  **Logical Orchestration (via MCP):** UI-TARS calls our optimized `generate_image.py` script via an MCP bridge. This ensures 100% reliability for production tasks.
2.  **Visual Interaction:** UI-TARS can be used to troubleshoot or modify ComfyUI workflows visually when manual intervention is needed.

### System Requirements (RTX 3060 12GB Focus)
*   **VRAM Management:** Running a 7B VLM locally alongside Flux Schnell (which uses ~11GB) will cause OOM (Out of Memory) errors.
*   **Recommendation:** Use **VolcEngine Ark** or **Hugging Face Endpoints** for the UI-TARS VLM "brain" to save all 12GB of VRAM for ComfyUI generation.
*   **OS:** Ubuntu 24.04 or WSL2 with `wslg` support.
*   **Node.js:** v22.x (required for the UI-TARS CLI/Agent stack).

---

## 2. Integration Design

### Orchestration Workflow
1.  **User Input:** "Generate 10 high-quality racehorse portraits for the weekly newsletter."
2.  **UI-TARS Interpretation:** The agent identifies the task requires "Flux" for quality and a "Batch" operation.
3.  **Tool Call (MCP):** UI-TARS calls the `generate_asset` tool (wrapper for `generate_image.py`).
4.  **Backend Execution:** `generate_image.py` sends the prompt to the ComfyUI API.
5.  **Harvesting:** Assets are saved to `/mnt/scratch/projects/Asset_Generation/output`.
6.  **Reporting:** UI-TARS monitors the output folder and reports "Generation complete. 10 assets are ready in the output folder."

### File System Integration
*   **Project Root:** `/mnt/scratch/projects/Asset_Generation`
*   **Model Storage:** `/mnt/scratch/models` (Symlinked to ComfyUI)
*   **UI-TARS Config:** Should be stored in `~/.config/ui-tars` (Safe-Path principle for OS drive).

---

## 3. Implementation Plan

### Step 1: Environment Setup (WSL2 / Ubuntu 24.04)
1.  **Prerequisites for WSL2:**
    - Ensure you are using **WSL2** with `wsl --version` (kernel 5.10+ recommended).
    - Install GWSL or rely on native **WSLg** for GUI support.
    - Install necessary libraries for screen capture in Linux:
      ```bash
      sudo apt-get update
      sudo apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libcomposite1 libasound2 libgbm1
      ```
2.  **Install Python Dependencies:**
    ```bash
    # Install MCP framework
    pip install mcp
    ```
3.  **Install Node.js 22:**
    ```bash
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt-get install -y nodejs
    ```
4.  **Install UI-TARS CLI & Agent:**
    ```bash
    npm install @agent-tars/cli@latest -g
    ```

### Step 2: Create the MCP Bridge
Create a file named `mcp_server.py` in the project root to expose our generation scripts. This leverages the **FastMCP** framework for Python.

```python
# mcp_server.py
from mcp.server.fastmcp import FastMCP
import subprocess
import os

mcp = FastMCP("EvolutionStables")

PROJECT_DIR = "/mnt/scratch/projects/Asset_Generation"

@mcp.tool()
def generate_image_asset(prompt: str, name: str = "asset", model: str = "sdxl"):
    """
    Generate an image using the local pipeline.
    Models: 'sdxl' (fast), 'flux' (high quality).
    """
    # Map model names to existing generate_image.py logic
    # Note: Using existing scripts to ensure consistency with current setup
    cmd = ["python3", os.path.join(PROJECT_DIR, "generate_image.py"), prompt, "--name", name]

    # Logic to handle Flux vs SDXL if generate_image.py supports --auto-model
    if model == "flux":
        cmd.append("--auto-model")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_DIR)
    return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"

@mcp.tool()
def list_available_workflows():
    """Reads workflows.py to list available generation templates."""
    # Logic to parse workflows.py and return available function names or templates
    try:
        import workflows
        return [func for func in dir(workflows) if func.startswith("get_")]
    except ImportError:
        return "workflows.py not found in path."

@mcp.tool()
def harvest_outputs():
    """Run the harvest script to organize generated assets."""
    script_path = os.path.join(PROJECT_DIR, "harvest_assets.sh")
    result = subprocess.run(["bash", script_path], capture_output=True, text=True, cwd=PROJECT_DIR)
    return result.stdout

if __name__ == "__main__":
    mcp.run()
```

### Step 3: Configure UI-TARS
1.  Launch UI-TARS Desktop or CLI.
2.  In Settings, select **VLM Provider: VolcEngine Ark** (to save VRAM).
3.  Add the MCP server in the settings by pointing to the `mcp_server.py` location.

---

## 4. Testing Strategy

To ensure a stable integration, follow this three-tier testing approach:

### Tier 1: Unit Testing (Programmatic)
1.  **Script Isolation:** Run `python3 generate_image.py "test prompt"` manually to verify ComfyUI connectivity.
2.  **MCP Tool Verification:** Use the `mcp inspect` tool (if available) or run `python3 mcp_server.py` and verify it starts without errors.

### Tier 2: Agent Orchestration Test
1.  **Prompt:** "UI-TARS, call the Evolution Stables generate_image_asset tool with prompt 'a red horse' and name it 'test_red'."
2.  **Verify:** Check `/mnt/scratch/projects/Asset_Generation/output` for `test_red.png`.
3.  **VRAM Check:** Monitor `nvidia-smi` during generation. Ensure UI-TARS (the agent) is not consuming significant VRAM (it should be offloaded to the API).

### Tier 3: End-to-End Visual Test
1.  **Prompt:** "Open the output folder, find the latest horse image, and show it to me."
2.  **Verify:** UI-TARS should use the OS file explorer and an image viewer to display the result.

---

## 5. Use Cases for Evolution Stables

### Case A: "Generate 10 racehorse portraits and post to Instagram"
1.  **UI-TARS** calls `generate_asset(prompt="portrait of a racehorse", model="sdxl", count=10)`.
2.  UI-TARS waits for files in the output directory.
3.  UI-TARS opens the browser, navigates to Instagram, and uploads the generated images from `/mnt/scratch/projects/Asset_Generation/output`.

### Case B: "Create hero image for website from latest race results"
1.  **User** provides a text file of race results.
2.  **UI-TARS** reads the results, synthesizes a prompt (e.g., "Cinematic photo of the winning horse [Name] crossing the finish line").
3.  **UI-TARS** calls `generate_asset(prompt=..., model="flux")`.
4.  UI-TARS moves the final image to the website's asset folder.

### Case C: "Build weekly social media content package"
1.  **UI-TARS** generates a mix of 5 images (Flux) and 2 videos (Wan2.1).
2.  UI-TARS organizes them into a folder named `Weekly_Package_[Date]`.
3.  UI-TARS sends a summary notification via the terminal or browser.

---

## 6. Safety & Performance
*   **VRAM Safety:** Never run UI-TARS local VLM (7B) and ComfyUI (Flux) at the same time on the 12GB card. Always use API-based VLM for the agent.
*   **Data Integrity:** All heavy assets remain on `/mnt/scratch` to avoid filling up the OS drive.
*   **Modularity:** The MCP bridge allows adding new models (like Wan2.1) without changing the UI-TARS configuration.
