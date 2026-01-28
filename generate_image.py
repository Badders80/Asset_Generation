import websocket
import uuid
import json
import urllib.request
import urllib.parse
import argparse
import sys
import random
import os
import logging
import error_handler
import workflows

# Initialize logging
logger = error_handler.setup_logging()

SERVER_ADDRESS = os.environ.get("COMFYUI_ADDRESS", "127.0.0.1:8188")
CLIENT_ID = str(uuid.uuid4())

def validate_args(args):
    """Performs domain-specific validation on arguments."""
    if args.task in ["image-to-video", "paint-by-numbers"] and not args.image:
        raise ValueError(f"Task '{args.task}' requires an input image path via --image")

    if args.task != "image-to-video" and (not args.prompt or args.prompt.strip() == ""):
        raise ValueError("Prompt cannot be empty for this task.")

    if args.width <= 0 or args.height <= 0:
        raise ValueError("Width and height must be positive integers.")

    if args.width > 2048 or args.height > 2048:
        logger.warning(f"Large dimensions requested ({args.width}x{args.height}). This may fail on some systems.")

def suggest_model(args):
    """Suggests the best model based on the task and preference."""
    if args.task == "text-to-video":
        return "wan-video"

    if args.task == "image-to-video":
        return "wan-video"

    if args.task == "paint-by-numbers":
        return "sdxl"

    if args.task == "text-to-image":
        if args.quality == "high":
            return "flux-schnell"
        else:
            return "sdxl"

    return "sdxl"

def queue_prompt(prompt, server_address):
    p = {"prompt": prompt, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    url = f"http://{server_address}/prompt"
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode()
        raise error_handler.APIError("Server returned an error", code=e.code, details=err_msg)
    except urllib.error.URLError as e:
        raise error_handler.ConnectionError(f"Failed to connect to server at {url}: {e.reason}")
    except Exception as e:
        raise error_handler.ComfyUIError(f"Unexpected error queuing prompt: {e}")

def get_history(prompt_id, server_address):
    url = f"http://{server_address}/history/{prompt_id}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())
    except Exception as e:
        raise error_handler.ComfyUIError(f"Failed to retrieve history for {prompt_id}: {e}")

def upload_image(image_path, server_address):
    """Uploads a local image to the ComfyUI server's input directory."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Local image not found: {image_path}")

    url = f"http://{server_address}/upload/image"
    filename = os.path.basename(image_path)

    with open(image_path, "rb") as f:
        image_data = f.read()

    # Construct multipart/form-data manually
    boundary = "---WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"image\"; filename=\"{filename}\"\r\n"
        f"Content-Type: image/png\r\n\r\n"
    ).encode('utf-8') + image_data + f"\r\n--{boundary}--\r\n".encode('utf-8')

    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            logger.info(f"📤 Uploaded: {filename} to ComfyUI")
            return result['name']
    except Exception as e:
        raise error_handler.ComfyUIError(f"Failed to upload image {image_path}: {e}")

def get_workflow(args, seed):
    """Returns the appropriate workflow JSON based on task and model."""
    upscale = (args.quality == "high")

    if args.task == "text-to-image":
        if args.model == "flux-schnell":
            return workflows.get_flux_workflow(args.prompt, args.name, args.width, args.height, seed, args.steps, args.cfg, upscale, is_schnell=True)
        elif args.model == "flux-klein-4b":
            return workflows.get_flux_workflow(args.prompt, args.name, args.width, args.height, seed, args.steps, args.cfg, upscale, is_schnell=False)
        else: # sdxl
            return workflows.get_sdxl_workflow(args.prompt, args.name, args.width, args.height, seed, args.steps, args.cfg, upscale)

    elif args.task == "paint-by-numbers":
        server_filename = upload_image(args.image, args.server)
        return workflows.get_controlnet_workflow(args.prompt, server_filename, args.name, seed, args.steps, args.cfg)

    elif args.task == "text-to-video":
        return workflows.get_wan_workflow(args.prompt, args.name, seed, args.steps)

    elif args.task == "image-to-video":
        server_filename = upload_image(args.image, args.server)
        if args.model == "wan-video":
            return workflows.get_wan_i2v_workflow(args.prompt, server_filename, args.name, seed, args.steps)
        else:
            return workflows.get_svd_workflow(args.prompt, server_filename, args.name, seed, args.steps, args.cfg)

    return None

def generate_asset(args, iteration=0):
    # Use provided seed or generate random one
    seed = args.seed if hasattr(args, 'seed') and args.seed is not None else random.randint(0, 18446744073709551615)
    ws = None
    try:
        workflow = get_workflow(args, seed)
        if not workflow:
            raise ValueError(f"Unsupported task/model combination: {args.task}/{args.model}")

        ws = websocket.WebSocket()
        ws.connect(f"ws://{args.server}/ws?clientId={CLIENT_ID}")
        logger.info(f"🚀 [Iter {iteration+1}/{args.count}] Seed: {seed} | Task: {args.task} | Model: {args.model}")
        
        result = queue_prompt(workflow, args.server)
        prompt_id = result['prompt_id']
        
        while True:
            out = ws.recv()
            if isinstance(out, str):
                msg = json.loads(out)
                if msg['type'] == 'executing' and msg['data']['node'] is None and msg['data']['prompt_id'] == prompt_id:
                    break
        
        history_data = get_history(prompt_id, args.server)
        if prompt_id not in history_data:
            raise error_handler.ComfyUIError(f"Prompt ID {prompt_id} not found in history.")

        history = history_data[prompt_id]
        output_found = False
        for node_id in history.get('outputs', {}):
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                filename = node_output['images'][0]['filename']
                logger.info(f"✅ Created Image: {filename}")
                output_found = True
            if 'gifs' in node_output:
                filename = node_output['gifs'][0]['filename']
                logger.info(f"✅ Created Video: {filename}")
                output_found = True

        if not output_found:
            raise error_handler.ComfyUIError("No outputs found in history.")

    except error_handler.APIError as e:
        logger.error(f"❌ API Error: {e}")
        if e.details:
            logger.error(f"📝 Details: {e.details}")
    except (error_handler.ComfyUIError, websocket.WebSocketException) as e:
        logger.error(f"❌ Generation failed: {e}")
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred: {e}")
    finally:
        if ws:
            ws.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate assets via ComfyUI API")
    parser.add_argument("prompt", nargs='?', default="", help="Text prompt for image generation")
    parser.add_argument("--task", default="text-to-image", choices=["text-to-image", "text-to-video", "image-to-video", "paint-by-numbers"], help="Task to perform")
    parser.add_argument("--name", default="evergreen", help="Prefix for the output filename")
    parser.add_argument("--width", type=int, default=1024, help="Image width")
    parser.add_argument("--height", type=int, default=1024, help="Image height")
    parser.add_argument("--server", default=SERVER_ADDRESS, help="ComfyUI server address")
    parser.add_argument("--model", choices=["sdxl", "flux-schnell", "flux-klein-4b", "svd", "wan-video"], help="Model architecture to use")
    parser.add_argument("--auto-model", action="store_true", help="Automatically select the best model")
    parser.add_argument("--quality", default="balanced", choices=["speed", "balanced", "high"], help="Quality preference")
    parser.add_argument("--steps", type=int, help="Sampling steps override")
    parser.add_argument("--cfg", type=float, help="CFG scale override")
    parser.add_argument("--image", help="Input image path")
    parser.add_argument("--count", type=int, default=1, help="Number of assets to generate")
    parser.add_argument("--seed", type=int, help="Manual seed for generation")

    args = parser.parse_args()

    if args.auto_model:
        args.model = suggest_model(args)
        logger.info(f"💡 Auto-model: {args.model}")
    elif not args.model:
        args.model = "sdxl" # Default
        logger.info(f"🔧 Defaulting to: {args.model}")

    try:
        validate_args(args)
        for i in range(args.count):
            generate_asset(args, i)
    except ValueError as e:
        logger.error(f"❌ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        error_handler.handle_fatal_error(e)
