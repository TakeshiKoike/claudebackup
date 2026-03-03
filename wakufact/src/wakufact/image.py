"""ComfyUI Flux画像生成"""

import json
import subprocess
import time
import uuid
import urllib.request
import urllib.parse
from pathlib import Path

COMFYUI_URL = "http://127.0.0.1:8000"


def generate(prompt: str, seed: int, output_path: Path,
             width: int = 512, height: int = 896,
             final_width: int = 1080, final_height: int = 1920,
             steps: int = 15, cfg: float = 1.0,
             unet: str = "flux1-dev.safetensors",
             weight_dtype: str = "default",
             url: str = COMFYUI_URL,
             timeout: int = 600) -> Path | None:
    """ComfyUI Flux画像生成 → リサイズ"""
    workflow = {
        "3": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": steps, "cfg": cfg,
            "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
            "model": ["4", 0], "positive": ["6", 0],
            "negative": ["7", 0], "latent_image": ["5", 0],
        }},
        "4": {"class_type": "UNETLoader", "inputs": {
            "unet_name": unet, "weight_dtype": weight_dtype,
        }},
        "5": {"class_type": "EmptySD3LatentImage", "inputs": {
            "width": width, "height": height, "batch_size": 1,
        }},
        "6": {"class_type": "CLIPTextEncode", "inputs": {
            "text": prompt, "clip": ["10", 0],
        }},
        "7": {"class_type": "CLIPTextEncode", "inputs": {
            "text": "", "clip": ["10", 0],
        }},
        "8": {"class_type": "VAEDecode", "inputs": {
            "samples": ["3", 0], "vae": ["9", 0],
        }},
        "9": {"class_type": "VAELoader", "inputs": {
            "vae_name": "ae.safetensors",
        }},
        "10": {"class_type": "DualCLIPLoader", "inputs": {
            "clip_name1": "t5xxl_fp16.safetensors",
            "clip_name2": "clip_l.safetensors",
            "type": "flux",
        }},
        "11": {"class_type": "SaveImage", "inputs": {
            "filename_prefix": output_path.stem,
            "images": ["8", 0],
        }},
    }

    client_id = str(uuid.uuid4())
    data = json.dumps({"prompt": workflow, "client_id": client_id}).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/prompt", data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    prompt_id = result["prompt_id"]

    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(f"{url}/history/{prompt_id}")
            with urllib.request.urlopen(req) as resp:
                history = json.loads(resp.read())
            if prompt_id in history:
                status = history[prompt_id].get("status", {}).get("status_str", "")
                if status == "error":
                    msgs = history[prompt_id]["status"].get("messages", [])
                    for m in msgs:
                        if m[0] == "execution_error":
                            print(f"    ERROR: {m[1].get('exception_message', '')}")
                    return None
                outputs = history[prompt_id].get("outputs", {})
                for nid, nout in outputs.items():
                    if "images" in nout:
                        filename = nout["images"][0]["filename"]
                        subfolder = nout["images"][0].get("subfolder", "")
                        params = urllib.parse.urlencode({
                            "filename": filename, "subfolder": subfolder, "type": "output",
                        })
                        req2 = urllib.request.Request(f"{url}/view?{params}")
                        with urllib.request.urlopen(req2) as resp2:
                            raw = output_path.with_suffix(".raw.png")
                            raw.write_bytes(resp2.read())
                        subprocess.run([
                            "ffmpeg", "-y", "-i", str(raw),
                            "-vf", f"scale={final_width}:{final_height}:flags=lanczos,unsharp=3:3:0.5",
                            str(output_path),
                        ], capture_output=True, check=True)
                        raw.unlink()
                        return output_path
                break
        except Exception:
            pass
        time.sleep(3)
    return None
