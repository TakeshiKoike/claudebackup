# SadTalker クイックリファレンス

**最終更新**: 2026年1月7日

## 基本コマンド

```bash
cd /Users/takeshikoike2025/Downloads/SadTalker
source venv/bin/activate
python inference.py \
  --driven_audio [音声.mp3] \
  --source_image [画像.png] \
  --result_dir /Users/takeshikoike2025/Downloads/copd_project/copd_project/videos \
  --still --preprocess full
```

## リップシンクの判断

| 話者タイプ | リップシンク |
|-----------|-------------|
| narration（ナレーション） | 不要 |
| kazuo, doctor等（会話） | 必要 |
| thought（心の声） | 不要 |

## よく使うパス

| 項目 | パス |
|-----|------|
| SadTalker | `/Users/takeshikoike2025/Downloads/SadTalker` |
| 音声 | `.../copd_project/copd_project/audio/` |
| 一雄画像 | `.../characters/kazuo_expressions/` |
| 医師画像 | `.../characters/doctor_expressions/` |
| 出力 | `.../copd_project/copd_project/videos/` |

## キャラクター画像

### 一雄（普通の表情）
`kazuo_general_05_neutral.png`

### 医師（普通の表情）
`doctor_05_neutral.png`

## 処理済み（シーン2）

- s02_01.mp4（医師）
- s02_03.mp4（医師）
- s02_04.mp4（一雄）
- s02_05.mp4（医師）
- s02_06.mp4（一雄）

## 未処理

シーン3〜13の会話セリフ（約25ファイル）

## 処理時間目安

- Mac M4 Pro: 約10分/ファイル
- RTX 4090: 約1分/ファイル

## 詳細

`SADTALKER_SETUP_GUIDE.md` を参照
