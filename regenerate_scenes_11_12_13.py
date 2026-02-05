#!/usr/bin/env python3
"""
シーン11-13の動画を正しい設定で生成/再生成するスクリプト

修正内容:
- シーン11: 話者と画像の修正（チアノーゼ画像使用）
- シーン12: 全動画を新規生成
- シーン13: s13_04のみ生成

使用方法:
  cd C:/Users/kokek/Downloads/SadTalker
  python ../copd_video_package/copd_video_package/regenerate_scenes_11_12_13.py
"""

import subprocess
import sys
import time
from pathlib import Path

# SadTalkerとデータのパス
SADTALKER_DIR = Path("C:/Users/kokek/Downloads/SadTalker")
DATA_DIR = Path("C:/Users/kokek/Downloads/copd_video_package/copd_video_package")

# 生成タスクリスト: (カットID, キャラクター名, 画像パス, 説明)
TASKS = [
    # シーン11: 急変時の対応（修正が必要なカットのみ）
    ("s11_01", "ichiko", "ichiko_expressions/ichiko_02_worried.png", "いち子「お父さん、大丈夫？」"),
    ("s11_02", "kazuo", "kazuo_expressions/kazuo_medical_04_cyanosis.png", "一男「昨日から調子が悪くて」"),
    ("s11_05", "kazuo", "kazuo_expressions/kazuo_medical_04_cyanosis.png", "一男「37度5分くらいあります」"),
    ("s11_07", "kazuo", "kazuo_expressions/kazuo_medical_04_cyanosis.png", "一男「少し黄色っぽいかも」"),

    # シーン12: 回復期（全て新規生成）
    ("s12_01", "yamada", "yamada_expressions/yamada_01_smile.png", "山田「調子はいかがですか？」"),
    ("s12_02", "kazuo", "kazuo_expressions/kazuo_general_06_relieved.png", "一男「だいぶ楽になりました」"),
    ("s12_03", "yamada", "yamada_expressions/yamada_01_smile.png", "山田「SpO2を測りますね」"),
    ("s12_04", "ichiko", "ichiko_expressions/ichiko_09_grateful.png", "いち子「本当に助かりました」"),
    ("s12_05", "yamada", "yamada_expressions/yamada_01_smile.png", "山田「早めに対応できました」"),
    ("s12_06", "kazuo", "kazuo_expressions/kazuo_general_01_smile.png", "一男「孫が来るんだ」"),
    ("s12_07", "yamada", "yamada_expressions/yamada_01_smile.png", "山田「リハビリも続けましょう」"),

    # シーン13: エピローグ（s13_04のみ、他はナレーション）
    ("s13_04", "kazuo", "kazuo_expressions/kazuo_general_09_grateful.png", "一男「みなさんのおかげだな」"),
]


def generate_video(cut_id, character, image_path, description):
    """SadTalkerで1つの動画を生成"""
    audio_file = DATA_DIR / "audio" / f"{cut_id}.mp3"
    image_file = DATA_DIR / "characters" / image_path
    output_dir = DATA_DIR / "videos"
    target_file = output_dir / f"{cut_id}_{character}.mp4"

    # ファイル確認
    if not audio_file.exists():
        print(f"  [ERROR] 音声ファイルなし: {audio_file}")
        return False
    if not image_file.exists():
        print(f"  [ERROR] 画像ファイルなし: {image_file}")
        return False

    # 既存ファイルを削除（再生成のため）
    if target_file.exists():
        target_file.unlink()
        print(f"  既存ファイル削除: {target_file.name}")

    # SadTalkerコマンド
    cmd = [
        sys.executable, "inference.py",
        "--driven_audio", str(audio_file),
        "--source_image", str(image_file),
        "--result_dir", str(output_dir),
        "--still",
        "--preprocess", "full"
    ]

    print(f"  SadTalker実行中...")

    try:
        result = subprocess.run(
            cmd,
            cwd=str(SADTALKER_DIR),
            capture_output=True,
            text=True,
            timeout=180
        )

        if result.returncode != 0:
            print(f"  [ERROR] SadTalker失敗")
            print(f"  stderr: {result.stderr[:300]}")
            return False

        # 出力ファイルを探してリネーム＆H.264変換
        time.sleep(1)

        # タイムスタンプ形式のファイルを探す
        timestamp_files = list(output_dir.glob("202*_*.mp4"))
        if timestamp_files:
            latest = max(timestamp_files, key=lambda p: p.stat().st_mtime)

            # H.264変換
            print(f"  H.264変換中...")
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", str(latest),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart",
                str(target_file)
            ]

            ffmpeg_result = subprocess.run(ffmpeg_cmd, capture_output=True)

            if ffmpeg_result.returncode == 0:
                latest.unlink()  # 元ファイル削除
                print(f"  [OK] {target_file.name}")
                return True
            else:
                # 変換失敗時はリネームのみ
                latest.rename(target_file)
                print(f"  [OK] {target_file.name} (H.264変換スキップ)")
                return True
        else:
            print(f"  [ERROR] 出力ファイルが見つかりません")
            return False

    except subprocess.TimeoutExpired:
        print(f"  [ERROR] タイムアウト")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    print("=" * 70)
    print("シーン11-13 動画再生成スクリプト")
    print("=" * 70)
    print(f"SadTalker: {SADTALKER_DIR}")
    print(f"データ: {DATA_DIR}")
    print(f"タスク数: {len(TASKS)}")
    print("=" * 70)

    # パス確認
    if not SADTALKER_DIR.exists():
        print(f"[ERROR] SadTalkerが見つかりません: {SADTALKER_DIR}")
        return 1

    if not (SADTALKER_DIR / "inference.py").exists():
        print(f"[ERROR] inference.pyが見つかりません")
        return 1

    # 出力ディレクトリ確認
    output_dir = DATA_DIR / "videos"
    output_dir.mkdir(exist_ok=True)

    # 処理開始
    success = 0
    fail = 0
    start_time = time.time()

    for i, (cut_id, character, image_path, description) in enumerate(TASKS, 1):
        print(f"\n[{i}/{len(TASKS)}] {cut_id}_{character}")
        print(f"  {description}")

        if generate_video(cut_id, character, image_path, description):
            success += 1
        else:
            fail += 1

    # 結果
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("完了")
    print("=" * 70)
    print(f"成功: {success}")
    print(f"失敗: {fail}")
    print(f"時間: {elapsed/60:.1f}分")
    print(f"出力: {output_dir}")

    if fail > 0:
        print("\n[WARNING] 失敗した動画があります。再実行してください。")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
