import websocket
import uuid
import json
import urllib.request
import urllib.parse
import argparse
import sys
import random

import os

SERVER_ADDRESS = os.environ.get("COMFYUI_ADDRESS", "127.0.0.1:8188")
CLIENT_ID = str(uuid.uuid4())

def queue_prompt(prompt, server_address):
    p = {"prompt": prompt, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"❌ SERVER ERROR: {e.code}")
        print(f"📝 DETAILS: {e.read().decode()}")
        sys.exit(1)

def get_history(prompt_id, server_address):
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

def generate_image(user_prompt, output_filename_base, width, height, server_address):
    # Verified working model from your previous logs
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
        print(f"🚀 Seed: {seed} | Generating Asset...")
        
        result = queue_prompt(workflow, server_address)
        prompt_id = result['prompt_id']
        
        while True:
            out = ws.recv()
            if isinstance(out, str):
                msg = json.loads(out)
                if msg['type'] == 'executing' and msg['data']['node'] is None and msg['data']['prompt_id'] == prompt_id:
                    break
        
        history = get_history(prompt_id, server_address)[prompt_id]
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                filename = node_output['images'][0]['filename']
                print(f"✅ Created: {filename}")
                return filename
    except Exception as e:
        print(f"❌ SCRIPT ERROR: {e}")
    finally:
        if ws: ws.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("--name", default="evergreen", help="Prefix for the output filename")
    parser.add_argument("--width", type=int, default=512, help="Image width")
    parser.add_argument("--height", type=int, default=896, help="Image height")
    parser.add_argument("--server", default=SERVER_ADDRESS, help="ComfyUI server address (e.g. 127.0.0.1:8188)")
    args = parser.parse_args()
    generate_image(args.prompt, args.name, args.width, args.height, args.server)
