# generate_image.py

## Purpose
A production-grade CLI tool for high-quality visual asset generation on the RTX 3060 12GB. Optimized for photorealistic equine imagery and automated batch processing.

## Core Tasks (`--task`)

| Task | Description | Models | Requirement |
|------|-------------|--------|-------------|
| `text-to-image` | High-res imagery | `flux-schnell`, `sdxl` | Prompt |
| `paint-by-numbers` | Guided generation | `sdxl` | Image + Prompt |
| `text-to-video` | AI Cinematics | `wan-video` | Prompt |
| `image-to-video` | Reference animation | `svd` | Image + Prompt |

## Usage
```bash
python3 generate_image.py [prompt] [options]
```

### Key Options
- `--auto-model`: Recommends the best model for the task/quality.
- `--count [N]`: Queues N sequential generations (perfect for overnight runs).
- `--quality {speed, balanced, high}`: Adjusts parameters and enables upscaling.
- `--width / --height`: Target dimensions (defaults to 1024x1024).

## Examples

### Professional Horse Racing Batch
```bash
python3 generate_image.py "majestic thoroughbred racehorse galloping on race track, golden hour" --task text-to-image --quality high --auto-model --count 10
```

### Video Generation (Wan2.1)
```bash
python3 generate_image.py "thoroughbred horse in full sprint, dynamic camera motion" --task text-to-video --model wan-video
```

## Infrastructure Setup

1. **Consolidate Models**: Run `./consolidate_models.sh` to link your 17GB Flux model and others.
2. **Start Server**: Run `./start_comfy_fixed.sh --clean` to start with RTX 3060 optimizations.
3. **Monitor**: Watch `asset_gen.log` for detailed progress.
