#!/usr/bin/env python3
"""
タイムスタンプ付きファイルをH.264変換＋正式名に変更
"""
import subprocess
from pathlib import Path

# タスクリスト（generate_all.pyと同じ順序）
TASKS = [
    ("s03_01", "kazuo"),
    ("s03_02", "ichiko"),
    ("s03_03", "kazuo"),
    ("s03_04", "ichiko"),
    ("s03_05", "kazuo"),
    ("s03_06", "ichiko"),
    ("s04_01", "yamada"),
    ("s04_02", "kazuo"),
    ("s04_03", "yamada"),
    ("s04_04", "yamada"),
    ("s04_05", "yamada"),
    ("s04_06", "kazuo"),
    ("s04_07", "yamada"),
    ("s05_01", "yamada"),
    ("s05_02", "ichiko"),
    ("s05_03", "yamada"),
    ("s05_04", "kazuo"),
    ("s05_05", "yamada"),
    ("s05_06", "kazuo"),
    ("s05_07", "yamada"),
    ("s06_01", "yamada"),
    ("s06_02", "kazuo"),
    ("s06_03", "yamada"),
    ("s06_04", "yamada"),
    ("s06_05", "kazuo"),
    ("s06_06", "yamada"),
    ("s06_07", "kazuo"),
    ("s06_08", "yamada"),
    ("s07_01", "kazuo"),
    ("s07_02", "pharmacist"),
    ("s07_03", "kazuo"),
    ("s07_04", "pharmacist"),
    ("s07_05", "pharmacist"),
    ("s07_06", "kazuo"),
    ("s08_01", "doctor"),
    ("s08_02", "kazuo"),
    ("s08_03", "doctor"),
    ("s08_04", "kazuo"),
    ("s08_05", "doctor"),
    ("s08_06", "doctor"),
    ("s08_07", "kazuo"),
    ("s08_08", "doctor"),
    ("s09_01", "sato"),
    ("s09_02", "ichiko"),
    ("s09_03", "sato"),
    ("s09_04", "kazuo"),
    ("s09_05", "sato"),
    ("s09_06", "ichiko"),
    ("s09_07", "sato"),
    ("s10_01", "ichiko"),
    ("s10_02", "kazuo"),
    ("s10_03", "ichiko"),
    ("s10_04", "kazuo"),
    ("s10_05", "ichiko"),
    ("s10_06", "kazuo"),
    ("s10_07", "ichiko"),
    ("s10_08", "kazuo"),
    ("s11_01", "yamada"),
    ("s11_02", "kazuo"),
    ("s11_03", "yamada"),
    ("s11_04", "yamada"),
    ("s11_05", "kazuo"),
    ("s11_06", "yamada"),
    ("s11_07", "ichiko"),
    ("s11_08", "yamada"),
    ("s11_09", "ichiko"),
]

videos_dir = Path(r"C:\Users\kokek\Downloads\copd_video_package\copd_video_package\videos")

# タイムスタンプファイルを時系列順に取得（テストファイル除く）
timestamp_files = sorted([f for f in videos_dir.glob("2026_*.mp4") if "23.41.58" not in f.name])

print(f"タイムスタンプファイル: {len(timestamp_files)}個")
print(f"タスク: {len(TASKS)}個")

if len(timestamp_files) != len(TASKS):
    print("警告: ファイル数とタスク数が一致しません")
    exit(1)

success = 0
for i, ((cut_id, character), timestamp_file) in enumerate(zip(TASKS, timestamp_files), 1):
    target_name = f"{cut_id}_{character}.mp4"
    target_path = videos_dir / target_name

    # 既に存在する場合はスキップ
    if target_path.exists():
        print(f"[{i:2d}/66] {target_name} - スキップ（既存）")
        success += 1
        continue

    print(f"[{i:2d}/66] {timestamp_file.name} → {target_name}")

    # H.264変換
    cmd = [
        "ffmpeg", "-y", "-i", str(timestamp_file),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(target_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            # 元ファイル削除
            timestamp_file.unlink()
            success += 1
            print(f"  → OK")
        else:
            print(f"  → 失敗: {result.stderr[:200]}")
    except Exception as e:
        print(f"  → エラー: {e}")

print(f"\n完了: {success}/{len(TASKS)}")
