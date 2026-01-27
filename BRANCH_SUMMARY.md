# Repository Branch Summary

This document provides an overview of the branches in the **Evolution Stables** repository as of January 2026.

## Branch Overview

### 1. `main`
*   **Status:** The primary stable branch.
*   **Latest Commit:** `5777abc` ("Merge pull request #2 from Badders80/feature/ui-tars...")
*   **Summary:** Represents the current production state. It includes the **UI-TARS Desktop Integration Analysis** and core scripts for ComfyUI automation.

### 2. `refactor-scripts-1429442093558450114`
*   **Status:** Advanced Technical Update.
*   **Latest Commit:** `33ec535` ("Finalize ComfyUI optimization, Wan2.1 environment setup...")
*   **Summary:** A significant overhaul of the generation infrastructure. Key features include:
    *   **Wan2.1 Integration:** Support for high-quality text-to-video and image-to-video.
    *   **Hardware Optimization:** Specific tuning for RTX 3060 12GB (FP16/FP8, memory management).
    *   **Architecture:** Introduction of `workflows.py` for modular JSON templates and `error_handler.py` for structured logging.
    *   **Model Management:** Scripts for symlinking and auditing models (`consolidate_models.sh`).

### 3. `feature/ui-tars-integration-analysis-17319468473055222206`
*   **Status:** Documentation Feature Branch.
*   **Latest Commit:** `023e520` ("feat: add comprehensive UI-TARS integration guide...")
*   **Summary:** Used for developing the `UI_TARS_INTEGRATION.md` guide. Its contents are currently merged into `main`.

---

## Technical Comparison

| Feature | `main` | `refactor-scripts` |
| --- | --- | --- |
| Wan2.1 Support | Basic | Full (with conditioning fixes) |
| Workflow Templates | Hardcoded | Modular (`workflows.py`) |
| Error Handling | Standard | Centralized (`error_handler.py`) |
| GPU Optimization | Basic | RTX 3060 Specific |
| Model Symlinking | No | Yes (`consolidate_models.sh`) |
