#!/usr/bin/env python3
"""
シーン11の一男の動画を正しい医療表情で再生成
"""
import subprocess
import sys
from pathlib import Path

# シーン11の一男のセリフと正しい表情
TASKS = [
    ("s11_02", "kazuo", "kazuo_expressions/kazuo_medical_02_dyspnea.png"),
    ("s11_05", "kazuo", "kazuo_expressions/kazuo_medical_02_dyspnea.png"),
]

sadtalker_dir = Path(r"C:\Users\kokek\Downloads\SadTalker")
data_dir = Path(r"C:\Users\kokek\Downloads\copd_video_package\copd_video_package")

print("シーン11の一男の動画を医療表情で再生成")
print("=" * 60)

for i, (cut_id, character, image_path) in enumerate(TASKS, 1):
    print(f"\n[{i}/{len(TASKS)}] {cut_id}_{character} を再生成...")

    audio_file = data_dir / "audio" / f"{cut_id}.mp3"
    image_file = data_dir / "characters" / image_path
    output_dir = data_dir / "videos"

    # SadTalkerで生成
    cmd = [
        sys.executable, "inference.py",
        "--driven_audio", str(audio_file),
        "--source_image", str(image_file),
        "--result_dir", str(output_dir),
        "--still",
        "--preprocess", "full"
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(sadtalker_dir / "venv" / "Scripts" / "activate" if False else sadtalker_dir),
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print(f"  生成成功")

            # 最新の出力ファイルを探してH.264変換
            import time
            time.sleep(1)

            # タイムスタンプファイルを探す
            latest_mp4 = max(output_dir.glob("2026_*.mp4"), key=lambda p: p.stat().st_mtime, default=None)

            if latest_mp4:
                target_path = output_dir / f"{cut_id}_{character}.mp4"

                # H.264変換
                print(f"  H.264変換中...")
                ffmpeg_cmd = [
                    "ffmpeg", "-y", "-i", str(latest_mp4),
                    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                    "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart",
                    str(target_path)
                ]

                ffmpeg_result = subprocess.run(ffmpeg_cmd, capture_output=True)

                if ffmpeg_result.returncode == 0:
                    latest_mp4.unlink()  # 元ファイル削除
                    print(f"  → OK: {target_path.name}")
                else:
                    print(f"  → H.264変換失敗")
            else:
                print(f"  → 出力ファイルが見つかりません")
        else:
            print(f"  生成失敗: {result.stderr[:200]}")
    except Exception as e:
        print(f"  エラー: {e}")

print("\n" + "=" * 60)
print("完了")
