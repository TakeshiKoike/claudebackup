#!/usr/bin/env python3
"""
WakuFact - エピソード動画制作スクリプト
VOICEVOX音声生成 → 画像生成(プレースホルダー) → ffmpegで動画合成
"""

import json
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

VOICEVOX_URL = "http://localhost:50021"


def voicevox_synthesize(text: str, speaker_id: int, output_path: Path,
                        speed_scale: float = 1.0, pitch_scale: float = 0.0,
                        intonation_scale: float = 1.0) -> Path:
    """VOICEVOXで音声合成"""
    # audio_query
    params = urllib.parse.urlencode({"text": text, "speaker": speaker_id})
    req = urllib.request.Request(
        f"{VOICEVOX_URL}/audio_query?{params}", method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        query = json.loads(resp.read())

    # パラメータ調整
    query["speedScale"] = speed_scale
    query["pitchScale"] = pitch_scale
    query["intonationScale"] = intonation_scale

    # synthesis
    params = urllib.parse.urlencode({"speaker": speaker_id})
    req = urllib.request.Request(
        f"{VOICEVOX_URL}/synthesis?{params}",
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        wav_data = resp.read()

    output_path.write_bytes(wav_data)
    return output_path


def get_audio_duration(path: Path) -> float:
    """ffprobeで音声の長さを取得"""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def generate_placeholder_image(output_path: Path, width: int, height: int,
                                text: str, bg_color: str, text_color: str = "white"):
    """ffmpegでテキスト付きプレースホルダー画像を生成"""
    # テキストをエスケープ
    escaped = text.replace("'", "'\\''").replace(":", "\\:")
    # 長いテキストは改行
    if len(text) > 15:
        mid = len(text) // 2
        # 日本語の句読点付近で区切る
        for i in range(mid, min(mid + 10, len(text))):
            if text[i] in "、。のはがをにで":
                escaped = text[:i+1].replace(":", "\\:") + "\\n" + text[i+1:].replace(":", "\\:")
                break

    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c={bg_color}:s={width}x{height}:d=1",
        "-vf", (
            f"drawtext=text='{escaped}'"
            f":fontsize=60:fontcolor={text_color}"
            f":x=(w-text_w)/2:y=(h-text_h)/2"
            f":font=Hiragino Sans"
        ),
        "-frames:v", "1",
        str(output_path)
    ], capture_output=True, check=True)


def create_video_from_sections(sections: list, images_dir: Path,
                               output_path: Path):
    """セクション音声と画像から動画を合成"""
    # 1. 全音声を結合
    concat_list = images_dir.parent / "audio" / "concat.txt"
    audio_files = []

    for sec in sections:
        audio_path = sec["audio_path"]
        duration = sec["duration"]
        audio_files.append(f"file '{audio_path}'")
        # セクション間にポーズを追加
        pause_ms = sec.get("pause_after_ms", 0)
        if pause_ms > 0:
            pause_path = images_dir.parent / "audio" / f"pause_{sec['section']}.wav"
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"anullsrc=r=24000:cl=mono",
                "-t", str(pause_ms / 1000),
                str(pause_path)
            ], capture_output=True, check=True)
            audio_files.append(f"file '{pause_path}'")

    concat_list.write_text("\n".join(audio_files))

    combined_audio = images_dir.parent / "audio" / "combined.wav"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy", str(combined_audio)
    ], capture_output=True, check=True)

    total_duration = get_audio_duration(combined_audio)
    print(f"  Total audio duration: {total_duration:.1f}s")

    # 2. 画像スライドショー + 音声で動画生成
    # 各画像の表示時間を計算
    image_files = sorted(images_dir.glob("*.png"))
    if not image_files:
        print("Error: No images found")
        return

    num_images = len(image_files)
    duration_per_image = total_duration / num_images

    # 画像リストファイル作成
    img_concat = images_dir.parent / "images" / "imglist.txt"
    img_lines = []
    for img in image_files:
        img_lines.append(f"file '{img}'")
        img_lines.append(f"duration {duration_per_image:.3f}")
    # 最後の画像をもう一度追加（ffmpeg concat demuxer の仕様）
    img_lines.append(f"file '{image_files[-1]}'")
    img_concat.write_text("\n".join(img_lines))

    # 3. 動画合成（スライドショー + 音声）
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(img_concat),
        "-i", str(combined_audio),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path)
    ], capture_output=True, check=True)

    final_duration = get_audio_duration(output_path)
    file_size = output_path.stat().st_size / (1024 * 1024)
    print(f"  Output: {output_path}")
    print(f"  Duration: {final_duration:.1f}s, Size: {file_size:.1f}MB")


def produce_episode(ep_num: int):
    """エピソード制作メイン"""
    base_dir = Path(__file__).parent
    ep_dir = base_dir / f"ep{ep_num:02d}"
    audio_dir = ep_dir / "audio"
    images_dir = ep_dir / "images"
    output_dir = ep_dir / "output"

    for d in [audio_dir, images_dir, output_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # エピソードデータ読み込み
    with open(base_dir / "batch_001_trivia_50.json", "r", encoding="utf-8") as f:
        trivia_data = json.load(f)

    with open(base_dir / "batch_001_voicevox_scripts.json", "r", encoding="utf-8") as f:
        voicevox_data = json.load(f)

    with open(base_dir / "batch_001_image_prompts.json", "r", encoding="utf-8") as f:
        image_data = json.load(f)

    ep_trivia = trivia_data["episodes"][ep_num - 1]
    ep_voice = voicevox_data["episodes"][ep_num - 1]
    ep_images = image_data["episodes"][ep_num - 1]

    print(f"=== EP.{ep_num:02d}: {ep_trivia['title_jp']} ===")
    print(f"Speaker ID: {ep_voice['speaker_id']}")

    # --- STEP 1: VOICEVOX音声生成 ---
    print("\n[1/3] Generating VOICEVOX audio...")
    sections_with_audio = []
    for i, section in enumerate(ep_voice["sections"]):
        audio_path = audio_dir / f"{i+1:02d}_{section['section']}.wav"
        print(f"  Section {i+1}/{len(ep_voice['sections'])}: {section['label']} ({len(section['text'])} chars)")

        voicevox_synthesize(
            text=section["text"],
            speaker_id=ep_voice["speaker_id"],
            output_path=audio_path,
            speed_scale=section.get("speed_scale", 1.0),
            pitch_scale=section.get("pitch_scale", 0.0),
            intonation_scale=section.get("intonation_scale", 1.0),
        )

        duration = get_audio_duration(audio_path)
        print(f"    -> {duration:.2f}s")

        sections_with_audio.append({
            **section,
            "audio_path": str(audio_path),
            "duration": duration,
        })

    # --- STEP 2: プレースホルダー画像生成 ---
    print("\n[2/3] Generating placeholder images...")
    # カテゴリ別カラー
    category_colors = {
        "食べ物": ["0xFF6B35", "0xFFA07A", "0xFF4500", "0xFFD700", "0xFF6347", "0xE8751A", "0xFF8C00"],
        "人体": ["0x4A90D9", "0x5BA3E6", "0x3D7BC7", "0x6BB3F0", "0x2E6CB5", "0x7EC8E3", "0x4A90D9"],
        "宇宙": ["0x1B0533", "0x2D1B69", "0x0D0221", "0x3C1F7B", "0x150B3D", "0x4B2D8E", "0x1B0533"],
        "動物": ["0x2D5016", "0x3A6B1E", "0x1F3B0F", "0x4C8228", "0x2D5016", "0x5A9A32", "0x3A6B1E"],
        "歴史": ["0x8B6914", "0x9E7B1C", "0x705312", "0xB08D24", "0x8B6914", "0xC4A02E", "0x9E7B1C"],
        "テクノロジー": ["0x1A1A2E", "0x2D2D4A", "0x0F0F1E", "0x3F3F66", "0x1A1A2E", "0x525282", "0x2D2D4A"],
        "自然": ["0x0B6623", "0x148F32", "0x084D1A", "0x1DB843", "0x0B6623", "0x26D94E", "0x148F32"],
    }
    colors = category_colors.get(ep_trivia["category"], ["0x333333"] * 7)

    section_labels = ["HOOK", "INTRO", "展開1", "展開2", "展開3", "CLIMAX", "CTA"]
    for i, img_info in enumerate(ep_images["images"]):
        img_path = images_dir / f"{i+1:02d}_{img_info['label']}.png"
        label = section_labels[i] if i < len(section_labels) else f"SCENE {i+1}"
        color = colors[i] if i < len(colors) else "0x333333"

        generate_placeholder_image(
            output_path=img_path,
            width=1080, height=1920,
            text=f"EP.{ep_num:02d} {label}",
            bg_color=color,
        )
        print(f"  Image {i+1}/{len(ep_images['images'])}: {img_path.name}")

    # --- STEP 3: 動画合成 ---
    print("\n[3/3] Compositing video...")
    output_path = output_dir / f"wakufact_ep{ep_num:02d}_jp.mp4"
    create_video_from_sections(sections_with_audio, images_dir, output_path)

    print(f"\n=== DONE ===")
    return output_path


if __name__ == "__main__":
    ep = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    produce_episode(ep)
