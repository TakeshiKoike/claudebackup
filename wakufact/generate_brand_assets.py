#!/usr/bin/env python3
"""WakuFact ブランドアセット生成（アイコン + バナー）"""

import json
import subprocess
import time
import uuid
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

COMFYUI_URL = "http://127.0.0.1:8000"
BRAND_DIR = Path(__file__).parent / "brand"
BRAND_DIR.mkdir(exist_ok=True)


def build_workflow(prompt: str, width: int, height: int, seed: int,
                   steps: int = 20, cfg: float = 1.0) -> dict:
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            }
        },
        "4": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "flux1-dev.safetensors",
                "weight_dtype": "default"
            }
        },
        "5": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1,
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["10", 0],
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "",
                "clip": ["10", 0],
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["9", 0],
            }
        },
        "9": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "ae.safetensors",
            }
        },
        "10": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": "t5xxl_fp16.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "flux",
            }
        },
        "11": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "wakufact_brand",
                "images": ["8", 0],
            }
        },
    }


def queue_prompt(workflow: dict, client_id: str) -> str:
    data = json.dumps({"prompt": workflow, "client_id": client_id}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["prompt_id"]


def poll_completion(prompt_id: str, timeout: int = 600) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
            with urllib.request.urlopen(req) as resp:
                history = json.loads(resp.read())
            if prompt_id in history:
                return history[prompt_id]
        except urllib.error.URLError:
            pass
        time.sleep(2)
    raise TimeoutError(f"Generation timed out after {timeout}s")


def download_image(filename: str, subfolder: str, output_path: Path):
    params = urllib.parse.urlencode({
        "filename": filename,
        "subfolder": subfolder,
        "type": "output",
    })
    req = urllib.request.Request(f"{COMFYUI_URL}/view?{params}")
    with urllib.request.urlopen(req) as resp:
        output_path.write_bytes(resp.read())


def upscale_image(input_path: Path, output_path: Path, width: int, height: int):
    subprocess.run([
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", f"scale={width}:{height}:flags=lanczos",
        str(output_path)
    ], capture_output=True, check=True)


def generate_image(name: str, prompt: str, gen_w: int, gen_h: int,
                   final_w: int, final_h: int, seed: int):
    """1枚の画像を生成してリサイズ"""
    client_id = str(uuid.uuid4())
    print(f"\n--- {name} ---")
    print(f"  Generate: {gen_w}x{gen_h} → Upscale: {final_w}x{final_h}")
    print(f"  Prompt: {prompt[:100]}...")

    workflow = build_workflow(prompt, gen_w, gen_h, seed, steps=20, cfg=1.0)
    prompt_id = queue_prompt(workflow, client_id)
    print(f"  Queued: {prompt_id[:12]}...")

    result = poll_completion(prompt_id)
    outputs = result.get("outputs", {})
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            for img in node_output["images"]:
                raw_path = BRAND_DIR / f"{name}_raw.png"
                out_path = BRAND_DIR / f"{name}.png"
                download_image(img["filename"], img.get("subfolder", ""), raw_path)
                upscale_image(raw_path, out_path, final_w, final_h)
                raw_path.unlink()
                print(f"  Saved: {out_path}")
                return out_path
    return None


# ===== アセット定義 =====

ICON_PROMPT = (
    "A cute and friendly owl mascot character for a trivia facts channel called WakuFact, "
    "the owl has big curious sparkling eyes, wearing round glasses, holding a glowing light bulb, "
    "warm golden and teal color palette, clean flat illustration style with subtle gradients, "
    "circular composition perfect for profile icon, solid dark navy background, "
    "kawaii Japanese mascot style, highly detailed, professional logo quality, centered composition"
)

YOUTUBE_BANNER_PROMPT = (
    "Wide horizontal banner for a trivia facts YouTube channel called WakuFact, "
    "a cute owl mascot with glasses on the left side, "
    "scattered floating icons of science symbols, planets, DNA, light bulbs, question marks, "
    "warm golden and teal gradient background with subtle geometric patterns, "
    "clean modern design, professional channel art, "
    "plenty of negative space in center and right for text overlay, "
    "illustration style with flat design elements"
)

X_HEADER_PROMPT = (
    "Ultra-wide horizontal header banner for a trivia facts social media account, "
    "a cute owl mascot with glasses peeking from the left edge, "
    "floating knowledge icons: light bulbs, stars, atoms, question marks scattered across, "
    "warm golden and teal gradient background, clean minimal design, "
    "panoramic composition, professional social media header, illustration style"
)

ASSETS = [
    {
        "name": "icon_wakufact",
        "prompt": ICON_PROMPT,
        "gen_w": 512, "gen_h": 512,
        "final_w": 800, "final_h": 800,
        "seed": 77042,
    },
    {
        "name": "banner_youtube",
        "prompt": YOUTUBE_BANNER_PROMPT,
        "gen_w": 768, "gen_h": 432,
        "final_w": 2560, "final_h": 1440,
        "seed": 77142,
    },
    {
        "name": "header_x",
        "prompt": X_HEADER_PROMPT,
        "gen_w": 768, "gen_h": 256,
        "final_w": 1500, "final_h": 500,
        "seed": 77242,
    },
]


if __name__ == "__main__":
    print("=== WakuFact ブランドアセット生成 ===")
    results = {}
    for asset in ASSETS:
        try:
            path = generate_image(**asset)
            results[asset["name"]] = path
        except Exception as e:
            print(f"  ERROR: {e}")
            results[asset["name"]] = None

    print("\n\n=== 結果 ===")
    for name, path in results.items():
        status = f"OK: {path}" if path else "FAILED"
        print(f"  {name}: {status}")
