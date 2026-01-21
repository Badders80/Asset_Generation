def get_flux_workflow(prompt, name, width, height, seed, steps=None, cfg=None, upscale=False, is_schnell=True):
    """
    Flux workflow optimized for FP8 on RTX 3060.
    """
    actual_steps = steps if steps is not None else 4
    actual_cfg = cfg if cfg is not None else 1.0
    # Use the 17GB schnell model by default as linked in consolidate_models.sh
    ckpt_name = "flux1-schnell-fp8.safetensors"

    workflow = {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": ckpt_name,
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

def get_sdxl_workflow(prompt, name, width, height, seed, steps=None, cfg=None, upscale=False):
    """
    SDXL workflow optimized for equine imagery.
    """
    actual_steps = steps if steps is not None else 30
    actual_cfg = cfg if cfg is not None else 7.0

    workflow = {
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": height, "width": width}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": prompt}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "extra limbs, blurry, low quality, distorted, watermark, signature"}},
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
        workflow["11"] = {"class_type": "UpscaleModelLoader", "inputs": {"model_name": "4x-UltraSharp.pth"}}
        workflow["12"] = {"class_type": "ImageUpscaleWithModel", "inputs": {"image": ["8", 0], "upscale_model": ["11", 0]}}
        workflow["13"] = {"class_type": "SaveImage", "inputs": {"filename_prefix": name + "_upscaled", "images": ["12", 0]}}

    return workflow

def get_wan_workflow(prompt, name, seed, steps=None):
    """
    Wan2.1 Video generation workflow using WanImageToVideo conditioning.
    """
    actual_steps = steps if steps is not None else 20

    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "wan2.1_t2v_1.3B_fp16.safetensors",
                "weight_dtype": "default"
            }
        },
        "2": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "wan"
            }
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "wan_2.1_vae.safetensors"
            }
        },
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": "low quality, blurry, distorted, watermark"}},
        "6": {
            "class_type": "WanImageToVideo",
            "inputs": {
                "positive": ["4", 0],
                "negative": ["5", 0],
                "vae": ["3", 0],
                "width": 832,
                "height": 480,
                "length": 81,
                "batch_size": 1
            }
        },
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 6.0,
                "denoise": 1.0,
                "latent_image": ["6", 2],
                "model": ["1", 0],
                "negative": ["6", 1],
                "positive": ["6", 0],
                "sampler_name": "uni_pc",
                "scheduler": "wan",
                "seed": seed,
                "steps": actual_steps
            }
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["8", 0],
                "frame_rate": 16,
                "loop_count": 0,
                "filename_prefix": name,
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 19,
                "save_output": True,
                "pingpong": False,
                "bitrate": 100,
                "megabit": True
            }
        }
    }

def get_wan_i2v_workflow(prompt, image_path, name, seed, steps=None):
    """
    Wan2.1 Image-to-Video generation workflow.
    """
    actual_steps = steps if steps is not None else 20

    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "wan2.1_i2v_1.3B_fp16.safetensors",
                "weight_dtype": "default"
            }
        },
        "2": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "wan"
            }
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "wan_2.1_vae.safetensors"
            }
        },
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": "low quality, blurry, static, distorted"}},
        "10": {"class_type": "LoadImage", "inputs": {"image": image_path}},
        "6": {
            "class_type": "WanImageToVideo",
            "inputs": {
                "positive": ["4", 0],
                "negative": ["5", 0],
                "vae": ["3", 0],
                "width": 832,
                "height": 480,
                "length": 81,
                "batch_size": 1,
                "start_image": ["10", 0]
            }
        },
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 6.0,
                "denoise": 1.0,
                "latent_image": ["6", 2],
                "model": ["1", 0],
                "negative": ["6", 1],
                "positive": ["6", 0],
                "sampler_name": "uni_pc",
                "scheduler": "wan",
                "seed": seed,
                "steps": actual_steps
            }
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["8", 0],
                "frame_rate": 16,
                "loop_count": 0,
                "filename_prefix": name,
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 19,
                "save_output": True,
                "pingpong": False,
                "bitrate": 100,
                "megabit": True
            }
        }
    }

def get_svd_workflow(prompt, image_path, name, seed, steps=None, cfg=None):
    """
    SVD workflow for image-to-video.
    """
    actual_steps = steps if steps is not None else 20
    actual_cfg = cfg if cfg is not None else 2.5

    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_path}},
        "2": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "svd.safetensors"}},
        "3": {"class_type": "SVD_img2vid_Conditioning", "inputs": {"clip_vision": ["2", 1], "init_image": ["1", 0], "width": 512, "height": 512, "video_frames": 14, "motion_bucket_id": 127, "fps": 6, "augmentation_level": 0.0}},
        "4": {"class_type": "KSampler", "inputs": {"cfg": actual_cfg, "denoise": 1.0, "latent_image": ["3", 2], "model": ["2", 0], "negative": ["5", 0], "positive": ["3", 0], "sampler_name": "euler", "scheduler": "karras", "seed": seed, "steps": actual_steps}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": "low quality, blurry"}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["4", 0], "vae": ["2", 2]}},
        "7": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["6", 0],
                "frame_rate": 6,
                "loop_count": 0,
                "filename_prefix": name,
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 19,
                "save_output": True,
                "pingpong": False,
                "bitrate": 100,
                "megabit": True
            }
        }
    }

def get_controlnet_workflow(prompt, reference_image, name, seed, steps=None, cfg=None):
    """
    ControlNet Canny with SDXL.
    """
    actual_steps = steps if steps is not None else 25
    actual_cfg = cfg if cfg is not None else 7.0
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": reference_image}},
        "2": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "controlnet-canny-sdxl-1.0.safetensors"}},
        "3": {"class_type": "ControlNetApply", "inputs": {"strength": 0.8, "conditioning": ["6", 0], "control_net": ["2", 0], "image": ["1", 0]}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": 1024, "width": 1024}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": prompt}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "blurry, low quality"}},
        "8": {"class_type": "KSampler", "inputs": {"cfg": actual_cfg, "denoise": 1.0, "latent_image": ["5", 0], "model": ["4", 0], "negative": ["7", 0], "positive": ["3", 0], "sampler_name": "dpmpp_2m", "scheduler": "karras", "seed": seed, "steps": actual_steps}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["4", 2]}},
        "10": {"class_type": "SaveImage", "inputs": {"filename_prefix": name, "images": ["9", 0]}}
    }
