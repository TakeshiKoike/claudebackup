"""エピソード制作パイプライン"""

import subprocess
from pathlib import Path

from . import audio, image, video


def produce_episode(
    ep_num: int,
    title: str,
    sections: list[dict],
    image_prompts: list[dict],
    base_dir: Path | None = None,
    version: int = 1,
) -> Path:
    """
    1エピソード分の動画を制作する。

    sections: [{"key": "hook", "text": "...", "subtitle": "...", "pause_ms": 800}, ...]
    image_prompts: [{"label": "01_hook", "prompt": "..."}, ...]
      画像数 == セクション数 (1:1対応)
    """
    if base_dir is None:
        base_dir = Path.cwd()

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
        out_path = images_dir / f"{label}.png"
        seed = ep_num * 10000 + i * 777
        print(f"  [{i+1}/{len(image_prompts)}] {label}")
        image.generate(img["prompt"], seed, out_path)

    # === STEP 2: 音声生成 ===
    print("\n[2/4] Generating audio...")
    timings = []
    audio_files: list[Path] = []
    t = 0.0

    for i, sec in enumerate(sections):
        fname = f"{i+1:02d}_{sec['key']}"
        audio_path = audio_dir / f"{fname}.wav"
        d = audio.synthesize(sec["text"], audio_path)
        print(f"  {sec['key']}: {d:.2f}s")
        timings.append((sec["key"], t, t + d))
        audio_files.append(audio_path)
        t += d

        pause_ms = sec.get("pause_ms", 0)
        if pause_ms > 0:
            pause_path = audio_dir / f"pause_{sec['key']}.wav"
            audio.make_silence(pause_path, pause_ms)
            audio_files.append(pause_path)
            t += pause_ms / 1000

    combined = audio_dir / "combined.wav"
    total = audio.concat_audio(audio_files, combined)
    print(f"  Total: {total:.2f}s")

    # === STEP 3: タイミング同期 + 字幕 ===
    print("\n[3/4] Syncing timing...")
    image_labels = [img["label"] for img in image_prompts]
    imglist = video.generate_imglist(image_labels, timings, sections, total, images_dir)
    sub_path = output_dir / "subtitles.ass"
    video.generate_ass(ep_num, title, sections, timings, total, sub_path)

    # === STEP 4: 動画合成 ===
    print("\n[4/4] Compositing video...")
    output_path = output_dir / f"wakufact_ep{ep_num:02d}_jp_sub_v{version}.mp4"
    video.composite(imglist, combined, sub_path, output_path)

    final_dur = audio.get_duration(output_path)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n  Output: {output_path}")
    print(f"  Duration: {final_dur:.1f}s, Size: {size_mb:.1f}MB")
    print(f"  DONE!")
    return output_path
