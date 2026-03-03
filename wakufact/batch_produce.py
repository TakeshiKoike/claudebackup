#!/usr/bin/env python3
"""
WakuFact - バッチ制作スクリプト
エピソード番号を指定して、画像生成→音声生成→動画合成を一括実行
"""

import json
import subprocess
import sys
import time
import uuid
import urllib.request
import urllib.parse
from pathlib import Path

COMFYUI_URL = "http://127.0.0.1:8000"
VOICEVOX_URL = "http://localhost:50021"
VOICEVOX_SPEAKER = 3

def dur(p):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(p)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def comfyui_generate(prompt, seed, images_dir, label, idx):
    """ComfyUI Flux画像生成 → 1080x1920リサイズ"""
    workflow = {
        "3": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 15, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
        "4": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux1-dev.safetensors", "weight_dtype": "default"}},
        "5": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 512, "height": 896, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["10", 0]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["10", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["9", 0]}},
        "9": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "10": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "t5xxl_fp16.safetensors", "clip_name2": "clip_l.safetensors", "type": "flux"}},
        "11": {"class_type": "SaveImage", "inputs": {"filename_prefix": f"wakufact_ep{idx:02d}", "images": ["8", 0]}},
    }

    client_id = str(uuid.uuid4())
    data = json.dumps({"prompt": workflow, "client_id": client_id}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt", data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    prompt_id = result["prompt_id"]

    start = time.time()
    while time.time() - start < 600:
        try:
            req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
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
                        params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": "output"})
                        req2 = urllib.request.Request(f"{COMFYUI_URL}/view?{params}")
                        with urllib.request.urlopen(req2) as resp2:
                            raw = images_dir / f"{label}_raw.png"
                            raw.write_bytes(resp2.read())
                        out = images_dir / f"{label}.png"
                        subprocess.run(
                            ["ffmpeg", "-y", "-i", str(raw),
                             "-vf", "scale=1080:1920:flags=lanczos,unsharp=3:3:0.5",
                             str(out)],
                            capture_output=True, check=True,
                        )
                        raw.unlink()
                        elapsed = time.time() - start
                        print(f"    Done {elapsed:.0f}s -> {out.name}")
                        return out
                break
        except Exception:
            pass
        time.sleep(3)
    return None


def voicevox_synth(text, output_path, speed=1.0):
    """VOICEVOX音声合成"""
    params = urllib.parse.urlencode({"text": text, "speaker": VOICEVOX_SPEAKER})
    req = urllib.request.Request(f"{VOICEVOX_URL}/audio_query?{params}", method="POST")
    with urllib.request.urlopen(req) as resp:
        query = json.loads(resp.read())
    query["speedScale"] = speed

    params = urllib.parse.urlencode({"speaker": VOICEVOX_SPEAKER})
    req = urllib.request.Request(
        f"{VOICEVOX_URL}/synthesis?{params}",
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        output_path.write_bytes(resp.read())
    return dur(output_path)


def make_pause(output_path, duration_ms):
    """無音WAV生成"""
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anullsrc=r=24000:cl=mono",
        "-t", str(duration_ms / 1000),
        str(output_path),
    ], capture_output=True, check=True)


def fmt_time(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def produce_episode(ep_num, title, sections_data, image_prompts):
    """
    sections_data: [{"key": "hook", "text": "...", "pause_ms": 800}, ...]
    image_prompts: [{"label": "01_hook", "prompt": "..."}, ...] (7枚)
    """
    base_dir = Path(__file__).parent
    ep_dir = base_dir / f"ep{ep_num:02d}"
    audio_dir = ep_dir / "audio"
    images_dir = ep_dir / "images"
    output_dir = ep_dir / "output"
    for d in [audio_dir, images_dir, output_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"EP{ep_num:02d}: {title}")
    print(f"{'='*50}")

    # === STEP 1: 画像生成 ===
    print("\n[1/4] Generating images...")
    for i, img in enumerate(image_prompts):
        label = img["label"]
        prompt = img["prompt"]
        seed = ep_num * 10000 + i * 777
        print(f"  [{i+1}/{len(image_prompts)}] {label}")
        comfyui_generate(prompt, seed, images_dir, label, ep_num)

    # === STEP 2: 音声生成 ===
    print("\n[2/4] Generating audio...")
    timings = []
    audio_files = []
    t = 0.0

    for i, sec in enumerate(sections_data):
        fname = f"{i+1:02d}_{sec['key']}"
        audio_path = audio_dir / f"{fname}.wav"
        d = voicevox_synth(sec["text"], audio_path)
        print(f"  {sec['key']}: {d:.2f}s")
        timings.append((sec["key"], t, t + d))
        audio_files.append(f"file '{audio_path.resolve()}'")
        t += d

        pause_ms = sec.get("pause_ms", 0)
        if pause_ms > 0:
            pause_path = audio_dir / f"pause_{sec['key']}.wav"
            make_pause(pause_path, pause_ms)
            audio_files.append(f"file '{pause_path.resolve()}'")
            t += pause_ms / 1000

    # 音声結合
    concat_list = audio_dir / "concat.txt"
    concat_list.write_text("\n".join(audio_files))
    combined = audio_dir / "combined.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list), "-c", "copy", str(combined),
    ], capture_output=True, check=True)
    total = dur(combined)
    print(f"  Total: {total:.2f}s")

    # === STEP 3: タイミング同期 ===
    print("\n[3/4] Syncing timing...")
    n_sections = len(sections_data)
    n_images = len(image_prompts)

    # 画像タイミング: hook音声中にhook+introを表示、残り1:1
    img_timings = []
    if n_images == n_sections + 1:
        # 7画像6音声パターン
        hook_end = timings[0][2] + (sections_data[0].get("pause_ms", 0) / 1000)
        hook_mid = timings[0][1] + (hook_end - timings[0][1]) / 2
        img_timings.append((image_prompts[0]["label"] + ".png", timings[0][1], hook_mid))
        img_timings.append((image_prompts[1]["label"] + ".png", hook_mid, hook_end))
        for j in range(1, n_sections):
            sec_end = timings[j][2] + (sections_data[j].get("pause_ms", 0) / 1000)
            img_timings.append((image_prompts[j + 1]["label"] + ".png", img_timings[-1][2], sec_end))
        # 最後の画像の終了をtotalに合わせる
        last = img_timings[-1]
        img_timings[-1] = (last[0], last[1], total)
    else:
        # 画像数=音声数の場合は1:1
        for j in range(n_sections):
            sec_end = timings[j][2] + (sections_data[j].get("pause_ms", 0) / 1000)
            start = img_timings[-1][2] if img_timings else 0.0
            img_timings.append((image_prompts[j]["label"] + ".png", start, sec_end))
        last = img_timings[-1]
        img_timings[-1] = (last[0], last[1], total)

    # imglist.txt
    img_lines = []
    for img_name, start, end in img_timings:
        img_path = (images_dir / img_name).resolve()
        img_lines.append(f"file '{img_path}'")
        img_lines.append(f"duration {end - start:.3f}")
    last_img = (images_dir / img_timings[-1][0]).resolve()
    img_lines.append(f"file '{last_img}'")
    (images_dir / "imglist.txt").write_text("\n".join(img_lines))

    for img_name, start, end in img_timings:
        print(f"  {img_name}: {start:.2f}s - {end:.2f}s")

    # === STEP 4: 字幕 + 動画合成 ===
    print("\n[4/4] Compositing video...")

    # ASS字幕
    ass = f"""[Script Info]
Title: WakuFact EP{ep_num:02d}
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Hiragino Sans,56,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,8,40,40,600,1
Style: Title,Hiragino Sans,100,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,3,8,40,40,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    # タイトル
    ass += f"Dialogue: 1,{fmt_time(0.0)},{fmt_time(3.0)},Title,,0,0,0,,{title}\n"

    # 字幕
    for sec_data, timing in zip(sections_data, timings):
        sub_text = sec_data.get("subtitle", sec_data["text"])
        ass += f"Dialogue: 0,{fmt_time(timing[1])},{fmt_time(timing[2])},Default,,0,0,0,,{sub_text}\n"

    # CTA
    cta_start = timings[-1][1] + 1.0
    ass += f"Dialogue: 1,{fmt_time(cta_start)},{fmt_time(total)},Title,,0,0,0,,フォローして次の雑学も見てね！\n"

    sub_path = output_dir / "subtitles.ass"
    sub_path.write_text(ass)

    # 動画合成
    output_path = output_dir / f"wakufact_ep{ep_num:02d}_jp_sub_v1.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str((images_dir / "imglist.txt").resolve()),
        "-i", str(combined.resolve()),
        "-vf", f"ass={sub_path.resolve()}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(output_path),
    ], capture_output=True, check=True)

    final_dur = dur(output_path)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n  Output: {output_path}")
    print(f"  Duration: {final_dur:.1f}s, Size: {size_mb:.1f}MB")
    print(f"  DONE!")
    return output_path
