import json
import urllib.request
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
        if elapsed % 60 == 0:
            print(f"  Waiting... {elapsed}s")
    print("TIMEOUT!")
    return None

def build_flux_prompt(text_prompt, width, height, prefix, seed=None):
    import random
    if seed is None:
        seed = random.randint(0, 2**53)
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux1-dev.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "clip_l.safetensors", "clip_name2": "t5xxl_fp16.safetensors", "type": "flux", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "CLIPTextEncodeFlux", "inputs": {"clip": ["2", 0], "clip_l": text_prompt[:77], "t5xxl": text_prompt, "guidance": 3.5}},
        "5": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["4", 0]}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "seed": seed, "steps": 25, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}}
    }

def generate_and_save(text_prompt, width, height, prefix, dest_path):
    print(f"\n=== Generating: {prefix} ({width}x{height}) ===")
    client_id = str(uuid.uuid4())
    prompt = build_flux_prompt(text_prompt, width, height, prefix)
    result = queue_prompt(prompt, client_id)
    prompt_id = result.get('prompt_id')
    print(f"Prompt ID: {prompt_id}")
    
    history = wait_for_completion(prompt_id, timeout=600)
    if history:
        outputs = history.get('outputs', {})
        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                for img in node_output['images']:
                    src = os.path.join(OUTPUT_DIR, img.get('subfolder', ''), img['filename'])
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src, dest_path)
                    print(f"SAVED: {dest_path}")
        return True
    print("FAILED")
    return False

# === 1. Patient Home Aerial View ===
patient_home_prompt = """Highly detailed aerial photograph of Japanese elderly couple's home interior, captured from approximately 30 meters height, looking down at 85 degree angle, almost top-down view. Ultra photorealistic photography style. Real architectural drone photography. Wide 16:9 aspect ratio.

Looking almost straight down into a Japanese traditional-modern home with roof removed, showing all rooms clearly visible from above. No walls blocking the view. Like a real architectural floor plan photograph. Elderly couple's modest single-story house.

KEY AREAS:
Entrance genkan with shoe cabinet inside near door, kitchen with refrigerator sink and small dining table, living room with sofa low table and TV, bedroom with hospital-style bed and HOME OXYGEN CONCENTRATOR MACHINE placed right next to bed with oxygen tubing visible, bathroom with bathtub and safety handrails, separate toilet room with handrails, washroom with washing machine.

EXTERIOR: Small Japanese garden with cherry blossom tree, parking space with one car, neighboring houses, quiet residential street, blue sky.

CRITICAL: Oxygen concentrator clearly visible next to bed, shoe cabinet inside house near genkan, handrails in corridor and bathroom, walker or wheelchair in hallway, realistic wood and fabric textures, warm natural lighting.

Real photograph quality, natural lighting, realistic shadows.
NOT anime, NOT illustration, NOT cartoon, NOT 3D render."""

generate_and_save(
    patient_home_prompt, 1344, 768, "patient_home_aerial",
    os.path.join(GAME_IMG_DIR, "backgrounds", "patient_home_aerial.png")
)

# === 2. Area Map ===
area_map_prompt = """Highly detailed aerial satellite photograph of Japanese suburban residential area, captured from approximately 500 meters height, looking straight down at 90 degree angle, true top-down view. Ultra photorealistic satellite drone photography style like Google Maps satellite imagery. Wide 16:9 aspect ratio.

Japanese suburban neighborhood showing mix of residential houses with gray and brown tile roofs, small commercial buildings, narrow streets. One prominent nursing station building with parking lot containing 3-4 cars and bicycle parking clearly visible at center-left. 15-20 traditional Japanese houses scattered around representing patient homes. Small medical clinic, one convenience store with parking area, small green park with trees and playground, one wider main road, typical narrow Japanese residential streets connecting houses, small rice fields on the edge.

Realistic details: Gray asphalt roads with white line markings, power lines visible, mix of old and newer houses, some with solar panels, vending machines at corners, small temple or shrine, river or canal on one edge.

Real satellite photograph quality, natural overhead lighting, building shadows visible.
NOT anime, NOT illustration, NOT cartoon, NOT 3D render, NOT digital art."""

generate_and_save(
    area_map_prompt, 1344, 768, "area_map",
    os.path.join(GAME_IMG_DIR, "maps", "area_map.png")
)

print("\n=== Background and map generation complete! ===")
