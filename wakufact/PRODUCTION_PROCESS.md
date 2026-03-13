# WakuFact 制作過程

## 概要
AI雑学ショート動画（縦型 1080x1920、40〜50秒）の自動生成パイプライン。

## 技術スタック

| 工程 | ツール | 備考 |
|------|--------|------|
| 台本生成 | Claude | 50本×日英、7カテゴリ均等 |
| 画像生成 | ComfyUI + Flux Dev | 512x896生成 → 1080x1920アップスケール |
| 音声合成 | VOICEVOX | 話者3人ローテーション（ずんだもん/四国めたん/春日部つむぎ） |
| 字幕 | ASS (Advanced SubStation Alpha) | Hiragino Sans, Title 100px / Default 56px |
| 動画合成 | ffmpeg (2パス) | libx264, AAC 192kbps, 30fps |
| SNS投稿データ | Claude | 4プラットフォーム×2言語×50ep = 400件 |

## パイプライン

```
batch_001_trivia_50.json（台本50本）
    │
    ├─→ generate_image_prompts.py → batch_001_image_prompts.json（350枚分）
    ├─→ generate_voicevox_scripts.py → batch_001_voicevox_scripts.json（50ep分）
    └─→ generate_post_metadata.py → batch_001_post_metadata.json（400件）

エピソードごと:
    ├─ ComfyUI Flux → ep{N}/images/*.png（7枚、1080x1920）
    ├─ VOICEVOX → ep{N}/audio/*.wav + combined.wav（6セクション+ポーズ）
    ├─ タイミング計算 → ep{N}/images/imglist.txt
    ├─ ASS字幕生成 → ep{N}/output/subtitles.ass
    └─ ffmpeg 2パス合成 → ep{N}/output/wakufact_ep{N}_jp_sub_v{ver}.mp4
```

## 1. 台本生成（Claude）

`batch_001_trivia_50.json` に50エピソード分を一括生成。

各エピソードの構成:
- ep番号、カテゴリ、日英タイトル
- 日英台本（hook → develop_1〜3 → climax → cta）
- 映像指示、BGMスタイル、CTA

7カテゴリ: 食べ物 / 人体 / 宇宙 / 動物 / 歴史 / テクノロジー / 自然

## 2. 画像生成（ComfyUI + Flux Dev）

`batch_001_image_prompts.json` → 1エピソード7枚。

### Flux設定
- 生成解像度: 512x896（メモリ効率）
- アップスケール: ffmpeg Lanczosフィルタで 1080x1920
- steps: 30, cfg_scale: 3.5, sampler: euler, scheduler: normal

### プロンプト構成
```
{シーン描写}, {カテゴリスタイル}, cinematic composition, 9:16 vertical format, high detail, 4k quality
```

カテゴリ別スタイル例:
- 食べ物: "vibrant food photography style, macro details, warm lighting"
- 宇宙: "cinematic space art, NASA photography style, deep cosmic colors"

### 画像ラベル（7枚/ep）
01_hook, 02_intro, 03_develop_1, 04_develop_2, 05_develop_3, 06_climax, 07_cta

## 3. 音声合成（VOICEVOX）

`batch_001_voicevox_scripts.json` → VOICEVOX API（localhost:50021）で合成。

### 話者ローテーション
| Speaker ID | 名前 | 担当EP |
|-----------|------|--------|
| 3 | ずんだもん | 1, 4, 7, ... |
| 2 | 四国めたん | 2, 5, 8, ... |
| 8 | 春日部つむぎ | 3, 6, 9, ... |

### セクション設定
| セクション | 話速 | ピッチ | 抑揚 | ポーズ(ms) |
|-----------|------|--------|------|-----------|
| hook | 1.1 | +0.02 | 1.3 | 800 |
| develop_1 | 1.0 | 0 | 1.1 | 500 |
| develop_2 | 0.95 | 0 | 1.2 | 600 |
| develop_3 | 1.0 | 0 | 1.1 | 500 |
| climax | 0.9 | +0.02 | 1.4 | 1000 |
| cta | 1.05 | 0 | 1.2 | 0 |

### 生成ファイル（ep01例）
```
ep01/audio/
├── 01_hook.wav
├── pause_hook.wav (800ms)
├── 02_develop_1.wav
├── pause_develop_1.wav (500ms)
├── ...
├── 06_cta.wav
└── combined.wav（全結合）
```

## 4. 字幕生成（ASS）

音声の実時間から字幕タイミングを計算。

### スタイル
- **Title**: Hiragino Sans 100px, シアン, 最大10文字/行
- **Default**: Hiragino Sans 56px, 白, 最大17文字/行

### 折り返しルール
1. 句読点（。、！？）の直後で切る（句読点を行頭に残さない）
2. 句読点がなければ助詞（で、に、を、が、は、の、も、て、と）の後で切る
3. どちらもなければ max_chars で強制切断

### タイミング
- タイトル: 0〜3秒
- 各セクション: 音声開始〜音声終了に完全同期
- CTA: climax開始+1秒 〜 動画終了

## 5. 動画合成（ffmpeg 2パス）

### なぜ2パスか
ffmpegの `concat` デマルチプレクサとASSフィルタを1パスで使うと、タイムスタンプ不整合で約16秒以降の字幕がレンダリングされない。

### Pass 1: 画像+音声→中間動画
```bash
ffmpeg -y \
  -f concat -safe 0 -i imglist.txt \
  -i combined.wav \
  -c:v libx264 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k \
  -shortest -movflags +faststart \
  output.tmp.mp4
```

### Pass 2: 字幕焼き込み
```bash
ffmpeg -y \
  -i output.tmp.mp4 \
  -vf "ass=subtitles.ass" \
  -c:v libx264 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart \
  wakufact_ep01_jp_sub_v10.mp4
```

### 出力仕様
- 解像度: 1080x1920（9:16縦型）
- コーデック: H.264
- フレームレート: 30fps
- 音声: AAC 192kbps
- 尺: 約40〜48秒
- サイズ: 約2〜2.5MB

## 6. SNS投稿メタデータ

`batch_001_post_metadata.json` に4プラットフォーム×2言語で生成。

- YouTube Shorts: タイトル、説明、タグ
- TikTok: キャプション、ハッシュタグ、サウンド提案
- Instagram Reels: キャプション、カバーテキスト
- X/Twitter: 280文字制限対応ツイート

ブランドタグ: #WakuFact #ワクファクト #毎日雑学

## 7. 完了状況

### 完成済み（4エピソード）
| EP | タイトル | 最終版 |
|----|---------|--------|
| 01 | バナナはベリー、イチゴはベリーじゃない | v10 |
| 02 | あなたの脳は小さな電球1個分の電力で動いている | v5 |
| 03 | 宇宙はステーキとラム酒の匂いがする | v5 |
| 04 | ハチミツは3000年経っても腐らない | v5 |

### データ生成済み（50エピソード分）
- 台本50本（日英）
- 画像プロンプト350枚
- VOICEVOX台本50本
- 投稿メタデータ400件

### 残作業
- EP05〜EP50: 画像生成 + 音声合成 + 動画合成
- `batch_produce.py` または `wakufact-produce` CLIで自動化可能

## ディレクトリ構成

```
wakufact/
├── pyproject.toml
├── batch_001_trivia_50.json
├── batch_001_image_prompts.json
├── batch_001_voicevox_scripts.json
├── batch_001_post_metadata.json
├── src/wakufact/
│   ├── __init__.py
│   ├── producer.py          # パイプライン統合
│   ├── audio.py             # VOICEVOX + ffmpeg音声
│   ├── image.py             # ComfyUI Flux画像生成
│   ├── video.py             # ffmpeg動画合成 + ASS字幕
│   └── cli.py               # CLIエントリポイント
├── generate_image_prompts.py
├── generate_voicevox_scripts.py
├── generate_post_metadata.py
├── generate_comfyui_images.py
├── batch_produce.py
├── rebuild_all.py
└── ep01〜ep04/
    ├── audio/*.wav
    ├── images/*.png + imglist.txt
    └── output/*.mp4 + subtitles.ass
```
