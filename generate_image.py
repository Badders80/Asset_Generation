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

# Initialize logging
logger = error_handler.setup_logging()

SERVER_ADDRESS = os.environ.get("COMFYUI_ADDRESS", "127.0.0.1:8188")
CLIENT_ID = str(uuid.uuid4())

def validate_args(args):
    """Performs domain-specific validation on arguments."""
    if not args.prompt or args.prompt.strip() == "":
        raise ValueError("Prompt cannot be empty.")

    if args.width <= 0 or args.height <= 0:
        raise ValueError("Width and height must be positive integers.")

    if args.width > 2048 or args.height > 2048:
        logger.warning(f"Large dimensions requested ({args.width}x{args.height}). This may fail on some systems.")

def queue_prompt(prompt, server_address):
    p = {"prompt": prompt, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    url = f"http://{server_address}/prompt"
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        raise error_handler.APIError("Server returned an error", code=e.code, details=e.read().decode())
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

def generate_image(user_prompt, output_filename_base, width, height, server_address):
    # Verified working model from previous logs
    ckpt = "v1-5-pruned-emaonly-fp16.safetensors"
    seed = random.randint(0, 18446744073709551615)
    ws = None
    try:
        workflow = {
            "3": {"class_type": "KSampler", "inputs": {"cfg": 8, "denoise": 1, "latent_image": ["5", 0], "model": ["4", 0], "negative": ["7", 0], "positive": ["6", 0], "sampler_name": "euler", "scheduler": "normal", "seed": seed, "steps": 20}},
            "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": height, "width": width}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": user_prompt}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": "text, watermark, blurry, low quality"}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": output_filename_base, "images": ["8", 0]}}
        }

        ws = websocket.WebSocket()
        ws.connect(f"ws://{server_address}/ws?clientId={CLIENT_ID}")
        logger.info(f"🚀 Seed: {seed} | Generating Asset...")
        
        result = queue_prompt(workflow, server_address)
        prompt_id = result['prompt_id']
        
        while True:
            out = ws.recv()
            if isinstance(out, str):
                msg = json.loads(out)
                if msg['type'] == 'executing' and msg['data']['node'] is None and msg['data']['prompt_id'] == prompt_id:
                    break
        
        history_data = get_history(prompt_id, server_address)
        if prompt_id not in history_data:
            raise error_handler.ComfyUIError(f"Prompt ID {prompt_id} not found in history.")

        history = history_data[prompt_id]
        for node_id in history.get('outputs', {}):
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                filename = node_output['images'][0]['filename']
                logger.info(f"✅ Created: {filename}")
                return filename

        raise error_handler.ComfyUIError("No images found in history outputs.")
    except (error_handler.ComfyUIError, websocket.WebSocketException) as e:
        error_handler.handle_fatal_error(e, "Generation failed")
    except Exception as e:
        error_handler.handle_fatal_error(e, "An unexpected error occurred during generation")
    finally:
        if ws:
            ws.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate images via ComfyUI API")
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("--name", default="evergreen", help="Prefix for the output filename")
    parser.add_argument("--width", type=int, default=512, help="Image width")
    parser.add_argument("--height", type=int, default=896, help="Image height")
    parser.add_argument("--server", default=SERVER_ADDRESS, help="ComfyUI server address (e.g. 127.0.0.1:8188)")

    args = parser.parse_args()

    try:
        validate_args(args)
        generate_image(args.prompt, args.name, args.width, args.height, args.server)
    except ValueError as e:
        logger.error(f"❌ Input validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        error_handler.handle_fatal_error(e)
