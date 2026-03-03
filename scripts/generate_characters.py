import json
import urllib.request
import time
import uuid
import os
import shutil
import random

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
                    print(f"  ERROR: {status}")
                    return None
        except:
            pass
        time.sleep(5)
        elapsed = int(time.time() - start)
        if elapsed % 60 == 0:
            print(f"  Waiting... {elapsed}s")
    print("  TIMEOUT!")
    return None

def build_flux_prompt(text_prompt, width, height, prefix, seed=None):
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
    print(f"  Generating: {prefix}...")
    client_id = str(uuid.uuid4())
    prompt = build_flux_prompt(text_prompt, width, height, prefix)
    result = queue_prompt(prompt, client_id)
    prompt_id = result.get('prompt_id')
    
    history = wait_for_completion(prompt_id, timeout=600)
    if history:
        outputs = history.get('outputs', {})
        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                for img in node_output['images']:
                    src = os.path.join(OUTPUT_DIR, img.get('subfolder', ''), img['filename'])
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src, dest_path)
                    print(f"  SAVED: {os.path.basename(dest_path)}")
        return True
    print(f"  FAILED: {prefix}")
    return False

# ============================================================
# Character definitions with base prompt and expression variants
# ============================================================

# Use consistent seed base per character to maintain face consistency
CHAR_SEED_BASE = {
    "manager": 42001,
    "nurse_01": 42010,
    "nurse_02": 42020,
    "nurse_03": 42030,
    "pt": 42040,
    "male_01": 42050,
    "female_01": 42060,
}

STAFF_CHARS = {
    "manager": {
        "base": "Professional portrait photograph of a Japanese woman in her early 50s, nursing station director. Wearing clean white medical coat over light blue blouse. Short neat black hair with subtle gray streaks. Thin-framed glasses. Light natural makeup. Small pearl earrings. Bust shot from chest up. Solid light gray studio background. High quality studio portrait photograph, professional lighting, sharp focus on face. NOT anime, NOT illustration, NOT 3D render.",
        "expressions": {
            "smile": "Warm confident smile showing competence and experience. Looking directly at camera.",
            "serious": "Thoughtful serious expression, slight frown. Looking directly at camera.",
            "thinking": "Looking slightly upward, contemplative expression.",
            "explaining": "Mouth slightly open as if speaking, engaged expression. Looking directly at camera."
        }
    },
    "nurse_01": {
        "base": "Professional portrait photograph of a Japanese female nurse in her early 30s. Wearing light pink nurse scrubs. Stethoscope around neck. Hair tied back in neat ponytail. Natural makeup. Professional and approachable appearance. Bust shot from chest up. Solid light gray studio background. High quality studio portrait photograph, professional lighting. NOT anime, NOT illustration, NOT 3D render.",
        "expressions": {
            "smile": "Friendly warm smile. Looking directly at camera.",
            "serious": "Focused professional expression. Looking directly at camera.",
            "thinking": "Thoughtful expression, looking slightly to the side.",
            "explaining": "Speaking expression, mouth slightly open. Looking directly at camera."
        }
    },
    "nurse_02": {
        "base": "Professional portrait photograph of a young Japanese female nurse in her mid-20s. Wearing light blue nurse scrubs. Short bob haircut. Youthful energetic appearance. Minimal natural makeup. Bust shot from chest up. Solid light gray studio background. High quality studio portrait photograph, professional lighting. NOT anime, NOT illustration, NOT 3D render.",
        "expressions": {
            "smile": "Cheerful bright smile. Looking directly at camera.",
            "serious": "Determined focused expression. Looking directly at camera.",
            "thinking": "Curious thoughtful expression, head tilted slightly.",
            "explaining": "Enthusiastic speaking expression. Looking directly at camera."
        }
    },
    "nurse_03": {
        "base": "Professional portrait photograph of a Japanese male nurse in his mid-30s. Wearing white nurse scrubs. Short neat black hair. Clean-shaven face. Professional competent appearance. Bust shot from chest up. Solid light gray studio background. High quality studio portrait photograph, professional lighting. NOT anime, NOT illustration, NOT 3D render.",
        "expressions": {
            "smile": "Calm reassuring smile. Looking directly at camera.",
            "serious": "Serious focused expression. Looking directly at camera.",
            "thinking": "Contemplative expression, looking slightly upward.",
            "explaining": "Speaking calmly, mouth slightly open. Looking directly at camera."
        }
    },
    "pt": {
        "base": "Professional portrait photograph of a Japanese male physical therapist in his early 30s. Wearing navy polo shirt typical of rehabilitation staff. Athletic but not muscular build. Short sporty haircut. Healthy active appearance. Bust shot from chest up. Solid light gray studio background. High quality studio portrait photograph, professional lighting. NOT anime, NOT illustration, NOT 3D render.",
        "expressions": {
            "smile": "Friendly encouraging smile. Looking directly at camera.",
            "serious": "Professional focused expression. Looking directly at camera.",
            "thinking": "Thoughtful analytical expression.",
            "explaining": "Encouraging speaking expression. Looking directly at camera."
        }
    }
}

PATIENT_CHARS = {
    "male_01": {
        "base": "Portrait photograph of an elderly Japanese man in his late 70s, home care patient. Wearing comfortable home clothes, beige cardigan over simple shirt. Thin white hair, slightly receding. Gentle wrinkled face showing kindness. Thin build typical of elderly. Bust shot from chest up. Solid light warm background. Natural portrait photograph quality. NOT anime, NOT illustration, NOT 3D render.",
        "expressions": {
            "smile": "Gentle warm grandfatherly smile. Looking at camera.",
            "tired": "Slightly tired expression, eyes half-closed.",
            "worried": "Concerned worried expression, slight frown.",
            "relieved": "Relaxed relieved expression after care.",
            "sleeping": "Eyes closed, peaceful sleeping face."
        }
    },
    "female_01": {
        "base": "Portrait photograph of an elderly Japanese woman in her late 70s, home care patient. Wearing comfortable home clothes, soft purple cardigan. Short permed gray hair typical Japanese grandmother style. Warm kind face with smile wrinkles. Slightly plump grandmotherly appearance. Bust shot from chest up. Solid light warm background. Natural portrait photograph quality. NOT anime, NOT illustration, NOT 3D render.",
        "expressions": {
            "smile": "Warm grandmotherly smile. Looking at camera.",
            "tired": "Slightly tired expression, eyes drooping.",
            "worried": "Anxious worried expression.",
            "relieved": "Relieved happy expression.",
            "sleeping": "Eyes closed, peaceful sleeping face."
        }
    }
}

# Generate all characters
total = sum(len(c["expressions"]) for c in STAFF_CHARS.values()) + sum(len(c["expressions"]) for c in PATIENT_CHARS.values())
count = 0

print(f"=== Generating {total} character images ===\n")

# Staff
for char_key, char_data in STAFF_CHARS.items():
    print(f"\n--- Staff: {char_key} ---")
    base_seed = CHAR_SEED_BASE[char_key]
    for expr_name, expr_desc in char_data["expressions"].items():
        count += 1
        full_prompt = f"{char_data['base']} {expr_desc}"
        dest = os.path.join(GAME_IMG_DIR, "staff", char_key, f"{char_key}_{expr_name}.png")
        print(f"[{count}/{total}]", end="")
        generate_and_save(full_prompt, 768, 1024, f"{char_key}_{expr_name}", dest)

# Patients
for char_key, char_data in PATIENT_CHARS.items():
    print(f"\n--- Patient: {char_key} ---")
    base_seed = CHAR_SEED_BASE[char_key]
    for expr_name, expr_desc in char_data["expressions"].items():
        count += 1
        full_prompt = f"{char_data['base']} {expr_desc}"
        dest = os.path.join(GAME_IMG_DIR, "patients", char_key, f"{char_key}_{expr_name}.png")
        print(f"[{count}/{total}]", end="")
        generate_and_save(full_prompt, 768, 1024, f"{char_key}_{expr_name}", dest)

print(f"\n=== ALL {total} character images generated! ===")
