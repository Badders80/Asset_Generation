def get_sd15_t2i_workflow(prompt, name, width, height, seed, steps=None, cfg=None, upscale=False):
    actual_steps = steps if steps is not None else 20
    actual_cfg = cfg if cfg is not None else 8.0
    workflow = {
        "3": {"class_type": "KSampler", "inputs": {"cfg": actual_cfg, "denoise": 1, "latent_image": ["5", 0], "model": ["4", 0], "negative": ["7", 0], "positive": ["6", 0], "sampler_name": "euler", "scheduler": "normal", "seed": seed, "steps": actual_steps}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "v1-5-pruned-emaonly-fp16.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": height, "width": width}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": prompt}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "text, watermark, blurry, low quality"}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
    }

    if upscale:
        workflow["10"] = {"class_type": "UpscaleModelLoader", "inputs": {"model_name": "4x-UltraSharp.pth"}}
        workflow["11"] = {"class_type": "ImageUpscaleWithModel", "inputs": {"image": ["8", 0], "upscale_model": ["10", 0]}}
        workflow["9"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": name, "images": ["11", 0]}}
    else:
        workflow["9"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": name, "images": ["8", 0]}}

    return workflow

def get_flux_klein_t2i_workflow(prompt, name, width, height, seed, steps=None, cfg=None, upscale=False):
    """
    Flux Klein 4B workflow optimized for FP8 on RTX 3060.
    Uses specific loaders to avoid memory issues and 'Params' AttributeErrors.
    """
    actual_steps = steps if steps is not None else 4
    actual_cfg = cfg if cfg is not None else 1.0 # Flux usually uses 1.0 CFG with Guidance

    workflow = {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "flux-2-klein-4b-fp8.safetensors",
                "weight_dtype": "fp8_e4m3fn"
            }
        },
        "2": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "flux"
            }
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "ae.safetensors"
            }
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["2", 0],
                "text": prompt
            }
        },
        "5": {
            "class_type": "FluxGuidance",
            "inputs": {
                "guidance": 3.5,
                "conditioning": ["4", 0]
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["2", 0],
                "text": ""
            }
        },
        "7": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            }
        },
        "8": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": actual_steps,
                "cfg": actual_cfg,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["5", 0],
                "negative": ["6", 0],
                "latent_image": ["7", 0]
            }
        },
        "9": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["8", 0],
                "vae": ["3", 0]
            }
        }
    }

    if upscale:
        workflow["11"] = {"class_type": "UpscaleModelLoader", "inputs": {"model_name": "4x-UltraSharp.pth"}}
        workflow["12"] = {"class_type": "ImageUpscaleWithModel", "inputs": {"image": ["9", 0], "upscale_model": ["11", 0]}}
        workflow["10"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": name, "images": ["12", 0]}}
    else:
        workflow["10"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": name, "images": ["9", 0]}}

    return workflow

def get_sdxl_t2i_workflow(prompt, name, width, height, seed, steps=None, cfg=None, upscale=False):
    """
    Plan B: SDXL Turbo/Base workflow for high-quality alternatives.
    """
    actual_steps = steps if steps is not None else 30
    actual_cfg = cfg if cfg is not None else 7.0

    workflow = {
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": height, "width": width}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": prompt}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "extra limbs, blurry, low quality, distorted"}},
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": actual_cfg,
                "denoise": 1.0,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "seed": seed,
                "steps": actual_steps
            }
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": name, "images": ["8", 0]}}
    }

    if upscale:
        workflow["10"] = {"class_type": "UpscaleModelLoader", "inputs": {"model_name": "4x-UltraSharp.pth"}}
        workflow["11"] = {"class_type": "ImageUpscaleWithModel", "inputs": {"image": ["8", 0], "upscale_model": ["10", 0]}}
        workflow["12"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": name + "_upscaled", "images": ["11", 0]}}

    return workflow

def get_paint_by_numbers_workflow(prompt, reference_image, name, seed, steps=None, cfg=None):
    # This uses ControlNet Scribble for "Paint by Numbers" style guidance
    actual_steps = steps if steps is not None else 25
    actual_cfg = cfg if cfg is not None else 7.0
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": reference_image}},
        "2": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "control_v11p_sd15_scribble.pth"}},
        "3": {"class_type": "ControlNetApply", "inputs": {"strength": 1.0, "conditioning": ["6", 0], "control_net": ["2", 0], "image": ["1", 0]}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "v1-5-pruned-emaonly-fp16.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": 512, "width": 512}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": prompt}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "blurry, low quality"}},
        "8": {"class_type": "KSampler", "inputs": {"cfg": actual_cfg, "denoise": 1.0, "latent_image": ["5", 0], "model": ["4", 0], "negative": ["7", 0], "positive": ["3", 0], "sampler_name": "euler", "scheduler": "normal", "seed": seed, "steps": actual_steps}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["4", 2]}},
        "10": {"class_type": "SaveImage", "inputs": {"filename_prefix": name, "images": ["9", 0]}}
    }

def get_text_to_video_workflow(prompt, name, seed, steps=None, cfg=None):
    # Simple SVD-based video generation (requires SVD checkpoint)
    actual_steps = steps if steps is not None else 20
    actual_cfg = cfg if cfg is not None else 2.5
    return {
        "1": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": prompt}},
        "2": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "svd.safetensors"}},
        "3": {"class_type": "SVD_img2vid_Conditioning", "inputs": {"clip_vision": ["2", 1], "init_image": ["4", 0], "width": 512, "height": 512, "video_frames": 14, "motion_bucket_id": 127, "fps": 6, "augmentation_level": 0.0}},
        "4": {"class_type": "EmptyImage", "inputs": {"width": 512, "height": 512, "color": 0}},
        "5": {"class_type": "KSampler", "inputs": {"cfg": actual_cfg, "denoise": 1.0, "latent_image": ["3", 2], "model": ["2", 0], "negative": ["1", 0], "positive": ["3", 0], "sampler_name": "euler", "scheduler": "karras", "seed": seed, "steps": actual_steps}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["2", 2]}},
        "7": {"class_type": "VideoCombine", "inputs": {"images": ["6", 0], "frame_rate": 6, "loop_count": 0, "filename_prefix": name, "format": "video/h264-mp4"}}
    }

def get_image_to_video_workflow(image_path, name, seed, steps=None, cfg=None):
    actual_steps = steps if steps is not None else 20
    actual_cfg = cfg if cfg is not None else 2.5
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_path}},
        "2": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "svd.safetensors"}},
        "3": {"class_type": "SVD_img2vid_Conditioning", "inputs": {"clip_vision": ["2", 1], "init_image": ["1", 0], "width": 512, "height": 512, "video_frames": 14, "motion_bucket_id": 127, "fps": 6, "augmentation_level": 0.0}},
        "4": {"class_type": "KSampler", "inputs": {"cfg": actual_cfg, "denoise": 1.0, "latent_image": ["3", 2], "model": ["2", 0], "negative": ["5", 0], "positive": ["3", 0], "sampler_name": "euler", "scheduler": "karras", "seed": seed, "steps": actual_steps}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": "low quality, blurry"}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["4", 0], "vae": ["2", 2]}},
        "7": {"class_type": "VideoCombine", "inputs": {"images": ["6", 0], "frame_rate": 6, "loop_count": 0, "filename_prefix": name, "format": "video/h264-mp4"}}
    }
