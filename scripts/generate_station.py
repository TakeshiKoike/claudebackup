import json
import urllib.request
import urllib.error
import time
import uuid
import os
import shutil

COMFYUI_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = "/Users/takeshikoike2025/comfyUI/output"
GAME_IMG_DIR = "/Users/takeshikoike2025/訪問看護ゲーム_dev/images"

def queue_prompt(prompt, client_id):
    data = json.dumps({"prompt": prompt, "client_id": client_id}).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def get_history(prompt_id):
    req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def wait_for_completion(prompt_id, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        try:
            history = get_history(prompt_id)
            if prompt_id in history:
                status = history[prompt_id].get('status', {})
                if status.get('completed', False) or status.get('status_str') == 'success':
                    return history[prompt_id]
                if status.get('status_str') == 'error':
                    print(f"ERROR: {json.dumps(status, indent=2)}")
                    return None
        except:
            pass
        time.sleep(5)
        elapsed = int(time.time() - start)
        if elapsed % 30 == 0:
            print(f"  Waiting... {elapsed}s elapsed")
    print("TIMEOUT!")
    return None

def build_flux_prompt(text_prompt, width=1344, height=768, prefix="nursing_station", seed=None):
    """Build Flux 1 Dev API prompt"""
    if seed is None:
        import random
        seed = random.randint(0, 2**53)
    
    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "flux1-dev.safetensors",
                "weight_dtype": "default"
            }
        },
        "2": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp16.safetensors",
                "type": "flux",
                "device": "default"
            }
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "ae.safetensors"
            }
        },
        "4": {
            "class_type": "CLIPTextEncodeFlux",
            "inputs": {
                "clip": ["2", 0],
                "clip_l": text_prompt[:77],
                "t5xxl": text_prompt,
                "guidance": 3.5
            }
        },
        "5": {
            "class_type": "ConditioningZeroOut",
            "inputs": {
                "conditioning": ["4", 0]
            }
        },
        "6": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            }
        },
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["6", 0],
                "seed": seed,
                "steps": 25,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["7", 0],
                "vae": ["3", 0]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["8", 0],
                "filename_prefix": prefix
            }
        }
    }

# === Generate Station Aerial View ===
station_prompt = """Highly detailed aerial photograph of Japanese home nursing station office interior, captured from approximately 30 meters height, looking down at 85 degree angle, almost top-down view. Ultra photorealistic photography style. Real architectural drone photography. Wide 16:9 aspect ratio.

Looking almost straight down into a Japanese home nursing station office with roof removed, showing all rooms clearly visible from above. No walls blocking the view. Like a real architectural floor plan photograph.

KEY AREAS VISIBLE FROM ABOVE:
Glass door entrance with reception counter, main office with 4-6 desks each with computer monitor, large whiteboard showing weekly visit schedule, nursing bags stored near desks, conference room with large table and 6-8 chairs, medical supply storage with organized shelving, staff break room with kitchenette, barrier-free toilet and washroom.

EXTERIOR: Small parking lot with 2-3 compact cars, bicycles and scooters for home visits, neighboring buildings, quiet Japanese suburban street, blue sky.

CRITICAL: Large whiteboard with weekly schedule visible, nursing bags visible, multiple computer workstations, medical supply shelves organized, staff in pink or light blue scrubs at desks, hand sanitizer stations, AED on wall, fluorescent ceiling lights, wood laminate flooring, white walls, modern Japanese office furniture.

Real photograph quality, natural lighting from windows and fluorescent lights, realistic shadows, authentic materials and textures.
NOT anime, NOT illustration, NOT cartoon, NOT 3D render, NOT digital art."""

print("=== Generating: Station Aerial View (1344x768) ===")
client_id = str(uuid.uuid4())
prompt = build_flux_prompt(station_prompt, width=1344, height=768, prefix="station_aerial")
result = queue_prompt(prompt, client_id)
prompt_id = result.get('prompt_id')
print(f"Prompt ID: {prompt_id}")

history = wait_for_completion(prompt_id, timeout=600)
if history:
    outputs = history.get('outputs', {})
    for node_id, node_output in outputs.items():
        if 'images' in node_output:
            for img in node_output['images']:
                src = os.path.join(OUTPUT_DIR, img['subfolder'], img['filename']) if img.get('subfolder') else os.path.join(OUTPUT_DIR, img['filename'])
                dst = os.path.join(GAME_IMG_DIR, "backgrounds", "station_aerial.png")
                shutil.copy2(src, dst)
                print(f"SAVED: {dst}")
    print("Station aerial view DONE!")
else:
    print("FAILED to generate station aerial view")

