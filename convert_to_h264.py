#!/usr/bin/env python3
"""
動画ファイルをH.264に一括変換するスクリプト
ブラウザでの再生互換性を確保するため

使用方法:
  python convert_to_h264.py --input_dir videos
"""

import subprocess
import sys
import argparse
from pathlib import Path


def convert_to_h264(input_file, output_file=None):
    """動画をH.264に変換"""
    if output_file is None:
        output_file = input_file.with_suffix('.temp.mp4')
        rename_after = True
    else:
        rename_after = False

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_file),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_file)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            if rename_after:
                output_file.replace(input_file)
            return True
        else:
            print(f"  [ERROR] {result.stderr[:200]}")
            return False
    except FileNotFoundError:
        print("[ERROR] ffmpegが見つかりません。インストールしてください。")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='動画をH.264に一括変換')
    parser.add_argument('--input_dir', type=str, default='videos', help='入力ディレクトリ')
    parser.add_argument('--dry_run', action='store_true', help='実行せずに確認のみ')

    args = parser.parse_args()

    input_dir = Path(args.input_dir)

    if not input_dir.exists():
        print(f"[ERROR] ディレクトリが見つかりません: {input_dir}")
        return 1

    mp4_files = list(input_dir.glob("*.mp4"))

    print("=" * 60)
    print("H.264変換")
    print("=" * 60)
    print(f"入力: {input_dir}")
    print(f"ファイル数: {len(mp4_files)}")
    print("=" * 60)

    if args.dry_run:
        print("\n[DRY RUN] 実行せずに確認のみ\n")
        for f in mp4_files:
            print(f"  {f.name}")
        return 0

    success = 0
    fail = 0

    for i, mp4_file in enumerate(mp4_files, 1):
        print(f"[{i}/{len(mp4_files)}] {mp4_file.name} を変換中...")

        if convert_to_h264(mp4_file):
            print(f"  [OK]")
            success += 1
        else:
            print(f"  [FAIL]")
            fail += 1

    print("\n" + "=" * 60)
    print("完了")
    print("=" * 60)
    print(f"成功: {success}")
    print(f"失敗: {fail}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
