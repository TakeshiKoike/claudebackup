#!/usr/bin/env python3
"""
COPD教材 リップシンク動画一括生成スクリプト
RTX 4090用

使用方法:
  cd SadTalker
  python ../copd_video_package/generate_all.py --sadtalker_dir . --data_dir ../copd_video_package
"""

import subprocess
import os
import sys
import argparse
from pathlib import Path
import time

# 生成タスクリスト: (カットID, キャラクター名, 画像パス)
TASKS = [
    # シーン3: 退院・帰宅
    ("s03_01", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s03_02", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
    ("s03_03", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s03_04", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
    ("s03_05", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s03_06", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),

    # シーン4: 訪問看護（初回）
    ("s04_01", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s04_02", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s04_03", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s04_04", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s04_05", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s04_06", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s04_07", "yamada", "yamada_expressions/yamada_05_neutral.png"),

    # シーン5: 入浴介助
    ("s05_01", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s05_02", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
    ("s05_03", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s05_04", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s05_05", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s05_06", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s05_07", "yamada", "yamada_expressions/yamada_05_neutral.png"),

    # シーン6: 呼吸リハビリ
    ("s06_01", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s06_02", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s06_03", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s06_04", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s06_05", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s06_06", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s06_07", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s06_08", "yamada", "yamada_expressions/yamada_05_neutral.png"),

    # シーン7: 薬局
    ("s07_01", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s07_02", "pharmacist", "pharmacist_expressions/pharmacist_05_neutral.png"),
    ("s07_03", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s07_04", "pharmacist", "pharmacist_expressions/pharmacist_05_neutral.png"),
    ("s07_05", "pharmacist", "pharmacist_expressions/pharmacist_05_neutral.png"),
    ("s07_06", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),

    # シーン8: かかりつけ医受診
    ("s08_01", "doctor", "doctor_expressions/doctor_05_neutral.png"),
    ("s08_02", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s08_03", "doctor", "doctor_expressions/doctor_05_neutral.png"),
    ("s08_04", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s08_05", "doctor", "doctor_expressions/doctor_05_neutral.png"),
    ("s08_06", "doctor", "doctor_expressions/doctor_05_neutral.png"),
    ("s08_07", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s08_08", "doctor", "doctor_expressions/doctor_05_neutral.png"),

    # シーン9: ケアマネ訪問
    ("s09_01", "sato", "sato_expressions/sato_05_neutral.png"),
    ("s09_02", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
    ("s09_03", "sato", "sato_expressions/sato_05_neutral.png"),
    ("s09_04", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s09_05", "sato", "sato_expressions/sato_05_neutral.png"),
    ("s09_06", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
    ("s09_07", "sato", "sato_expressions/sato_05_neutral.png"),

    # シーン10: 妻との会話
    ("s10_01", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
    ("s10_02", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s10_03", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
    ("s10_04", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s10_05", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
    ("s10_06", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s10_07", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
    ("s10_08", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),

    # シーン11: 急変時の対応
    ("s11_01", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s11_02", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s11_03", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s11_04", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s11_05", "kazuo", "kazuo_expressions/kazuo_general_05_neutral.png"),
    ("s11_06", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s11_07", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
    ("s11_08", "yamada", "yamada_expressions/yamada_05_neutral.png"),
    ("s11_09", "ichiko", "ichiko_expressions/ichiko_05_neutral.png"),
]


def generate_video(sadtalker_dir, data_dir, cut_id, character, image_path, high_quality=False):
    """1つの動画を生成"""
    audio_file = data_dir / "audio" / f"{cut_id}.mp3"
    image_file = data_dir / "characters" / image_path
    output_dir = data_dir / "videos"

    # ファイル存在確認
    if not audio_file.exists():
        print(f"  [ERROR] 音声ファイルが見つかりません: {audio_file}")
        return False
    if not image_file.exists():
        print(f"  [ERROR] 画像ファイルが見つかりません: {image_file}")
        return False

    # コマンド構築
    cmd = [
        sys.executable, "inference.py",
        "--driven_audio", str(audio_file),
        "--source_image", str(image_file),
        "--result_dir", str(output_dir),
        "--still",
        "--preprocess", "full"
    ]

    if high_quality:
        cmd.extend(["--enhancer", "gfpgan", "--size", "512"])

    # 実行
    try:
        result = subprocess.run(
            cmd,
            cwd=str(sadtalker_dir),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  [ERROR] 生成失敗")
            print(f"  stderr: {result.stderr[:500]}")
            return False

        return True
    except Exception as e:
        print(f"  [ERROR] 例外発生: {e}")
        return False


def rename_output(data_dir, cut_id, character):
    """SadTalkerの出力ファイルをリネーム"""
    output_dir = data_dir / "videos"
    target_name = f"{cut_id}_{character}.mp4"

    # SadTalkerは results/{タイムスタンプ}/{audio名}.mp4 形式で出力
    # 最新の出力ファイルを探す
    for mp4_file in sorted(output_dir.rglob(f"{cut_id}*.mp4"), reverse=True):
        if mp4_file.name != target_name:
            target_path = output_dir / target_name
            mp4_file.rename(target_path)
            print(f"  リネーム: {mp4_file.name} -> {target_name}")
            return True

    return False


def convert_to_h264(video_path):
    """H.264に変換"""
    temp_path = video_path.with_suffix('.temp.mp4')

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",
        str(temp_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            temp_path.replace(video_path)
            return True
    except:
        pass

    return False


def main():
    parser = argparse.ArgumentParser(description='COPD教材リップシンク動画一括生成')
    parser.add_argument('--sadtalker_dir', type=str, required=True, help='SadTalkerディレクトリ')
    parser.add_argument('--data_dir', type=str, required=True, help='データディレクトリ(copd_video_package)')
    parser.add_argument('--high_quality', action='store_true', help='高品質モード(GFPGAN + 512px)')
    parser.add_argument('--start_from', type=int, default=0, help='開始インデックス(0から)')
    parser.add_argument('--convert_h264', action='store_true', help='H.264に変換')
    parser.add_argument('--dry_run', action='store_true', help='実行せずに確認のみ')

    args = parser.parse_args()

    sadtalker_dir = Path(args.sadtalker_dir).resolve()
    data_dir = Path(args.data_dir).resolve()

    # パス確認
    print("=" * 60)
    print("COPD教材 リップシンク動画一括生成")
    print("=" * 60)
    print(f"SadTalker: {sadtalker_dir}")
    print(f"データ: {data_dir}")
    print(f"タスク数: {len(TASKS)}")
    print(f"開始位置: {args.start_from}")
    print(f"高品質モード: {args.high_quality}")
    print("=" * 60)

    if not sadtalker_dir.exists():
        print(f"[ERROR] SadTalkerディレクトリが見つかりません: {sadtalker_dir}")
        return 1

    if not data_dir.exists():
        print(f"[ERROR] データディレクトリが見つかりません: {data_dir}")
        return 1

    # 出力ディレクトリ確認
    output_dir = data_dir / "videos"
    output_dir.mkdir(exist_ok=True)

    if args.dry_run:
        print("\n[DRY RUN] 実行せずに確認のみ\n")
        for i, (cut_id, character, image_path) in enumerate(TASKS[args.start_from:], args.start_from):
            audio = data_dir / "audio" / f"{cut_id}.mp3"
            image = data_dir / "characters" / image_path
            print(f"[{i+1:2d}/{len(TASKS)}] {cut_id}_{character}")
            print(f"         音声: {'OK' if audio.exists() else 'MISSING'} - {audio}")
            print(f"         画像: {'OK' if image.exists() else 'MISSING'} - {image}")
        return 0

    # 処理開始
    success_count = 0
    fail_count = 0
    start_time = time.time()

    for i, (cut_id, character, image_path) in enumerate(TASKS[args.start_from:], args.start_from):
        print(f"\n[{i+1:2d}/{len(TASKS)}] {cut_id}_{character} を生成中...")

        task_start = time.time()

        # 既に存在する場合はスキップ
        target_file = output_dir / f"{cut_id}_{character}.mp4"
        if target_file.exists():
            print(f"  [SKIP] 既に存在します: {target_file.name}")
            success_count += 1
            continue

        # 生成
        if generate_video(sadtalker_dir, data_dir, cut_id, character, image_path, args.high_quality):
            # リネーム
            rename_output(data_dir, cut_id, character)

            # H.264変換
            if args.convert_h264 and target_file.exists():
                print(f"  H.264変換中...")
                convert_to_h264(target_file)

            task_time = time.time() - task_start
            print(f"  [OK] 完了 ({task_time:.1f}秒)")
            success_count += 1
        else:
            print(f"  [FAIL] 失敗")
            fail_count += 1

    # 結果サマリー
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("完了")
    print("=" * 60)
    print(f"成功: {success_count}")
    print(f"失敗: {fail_count}")
    print(f"合計時間: {total_time/60:.1f}分")
    print(f"出力先: {output_dir}")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
