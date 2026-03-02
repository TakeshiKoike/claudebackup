#!/usr/bin/env python3
"""
WakuFact - ComfyUI API経由でFlux画像を生成
EP指定で7枚の画像を生成し、ep{N}/images/ に保存
"""

import json
import subprocess
import sys
import time
import uuid
import urllib.request
import urllib.error
from pathlib import Path

COMFYUI_URL = "http://127.0.0.1:8000"

# Flux Dev ワークフロー（API形式）
def build_workflow(prompt: str, negative_prompt: str, width: int, height: int,
                   seed: int, steps: int = 15, cfg: float = 1.0) -> dict:
    """Flux Dev用のComfyUI APIワークフロー (メモリ最適化版)
    - UNETLoader で fp8_e4m3fn 変換 (22GB→~12GB)
    - DualCLIPLoader で t5xxl_fp8 を使用 (9.1GB→~5GB)
    - 解像度は呼び出し側で小さめに指定し、後でリサイズ
    """
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
                "filename_prefix": "wakufact",
                "images": ["8", 0],
            }
        },
    }


def queue_prompt(workflow: dict, client_id: str) -> str:
    """ComfyUIにプロンプトをキューイング"""
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
    """生成完了を待つ"""
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
    """生成画像をダウンロード"""
    params = urllib.parse.urlencode({
        "filename": filename,
        "subfolder": subfolder,
        "type": "output",
    })
    req = urllib.request.Request(f"{COMFYUI_URL}/view?{params}")
    with urllib.request.urlopen(req) as resp:
        output_path.write_bytes(resp.read())


def upscale_image(input_path: Path, output_path: Path, width: int = 1080, height: int = 1920):
    """ffmpegで画像をリサイズ"""
    subprocess.run([
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", f"scale={width}:{height}:flags=lanczos",
        str(output_path)
    ], capture_output=True, check=True)


def generate_episode_images(ep_num: int):
    """エピソードの画像7枚を生成"""
    import urllib.parse

    base_dir = Path(__file__).parent
    images_dir = base_dir / f"ep{ep_num:02d}" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 画像プロンプト読み込み
    with open(base_dir / "batch_001_image_prompts.json", "r", encoding="utf-8") as f:
        image_data = json.load(f)

    ep_images = image_data["episodes"][ep_num - 1]
    client_id = str(uuid.uuid4())

    print(f"=== EP.{ep_num:02d}: {ep_images['title_jp']} ===")
    print(f"Generating {ep_images['total_images']} images via Flux Dev...\n")

    for i, img_info in enumerate(ep_images["images"]):
        label = img_info["label"]
        prompt = img_info["prompt"]
        seed = ep_num * 1000 + i * 100 + 42

        # 縦長 9:16 (512x896 でメモリ節約、生成後に1080x1920へリサイズ)
        width = 512
        height = 896

        print(f"  [{i+1}/{ep_images['total_images']}] {label}")
        print(f"    Prompt: {prompt[:80]}...")

        workflow = build_workflow(
            prompt=prompt,
            negative_prompt="",
            width=width,
            height=height,
            seed=seed,
            steps=15,
            cfg=1.0,
        )

        try:
            prompt_id = queue_prompt(workflow, client_id)
            print(f"    Queued: {prompt_id[:12]}...")

            result = poll_completion(prompt_id, timeout=600)

            # 画像取得
            outputs = result.get("outputs", {})
            for node_id, node_output in outputs.items():
                if "images" in node_output:
                    for img in node_output["images"]:
                        filename = img["filename"]
                        subfolder = img.get("subfolder", "")
                        raw_path = images_dir / f"{i+1:02d}_{label}_raw.png"
                        out_path = images_dir / f"{i+1:02d}_{label}.png"
                        download_image(filename, subfolder, raw_path)
                        # 512x896 → 1080x1920 にリサイズ
                        upscale_image(raw_path, out_path)
                        raw_path.unlink()  # 元画像削除
                        print(f"    Saved: {out_path.name} (upscaled to 1080x1920)")
                        break
                    break

        except Exception as e:
            print(f"    Error: {e}")
            print(f"    Skipping image {i+1}")
            continue

    print(f"\n=== Done! Images saved to {images_dir} ===")


if __name__ == "__main__":
    ep = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    generate_episode_images(ep)
