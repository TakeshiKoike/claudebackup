# WakuFact 制作ハンドオフドキュメント

## 1. プロジェクト概要

### 目的
匿名SNSコンテンツで収益化（3ヶ月で月4〜15万円目標）。AI雑学ショート動画を自動生成パイプラインで量産する。

### ブランド
- **WakuFact** (@wakufact)
- ジャンル: 雑学ショート動画（縦型 1080x1920 / 横型 1920x1080）
- 尺: 約40〜50秒
- 言語: 日本語音声 + 日本語字幕（投稿メタデータは日英併記）
- 7カテゴリ: 食べ物 / 人体 / 宇宙 / 動物 / 歴史 / テクノロジー / 自然
- ブランドタグ: `#WakuFact #ワクファクト #毎日雑学`

### 技術スタック

| 工程 | ツール | 備考 |
|------|--------|------|
| 台本生成 | Claude | 50本×日英、7カテゴリ均等 |
| 画像生成 | ComfyUI + Flux Dev | 512x896 → 1080x1920 (縦) / 896x512 → 1920x1080 (横) |
| 音声合成 | VOICEVOX (localhost:50021) | 話者3人ローテーション |
| 字幕 | ASS (Advanced SubStation Alpha) | Hiragino Sans |
| 動画合成 | ffmpeg (2パス) | libx264, AAC 192kbps, 30fps |
| YouTube投稿 | YouTube Data API v3 + OAuth 2.0 | google-api-python-client |
| X投稿 | tweepy (v1.1 + v2) | OAuth 1.0 |
| SNS投稿データ | Claude | 4プラットフォーム × 2言語 × 50ep = 400件 |

---

## 2. パイプライン全体像

```
[台本50本 JSON] ─── Claude で一括生成
    │
    ├─→ generate_image_prompts.py → batch_001_image_prompts.json (350枚分)
    ├─→ generate_voicevox_scripts.py → batch_001_voicevox_scripts.json (50ep分)
    └─→ generate_post_metadata.py → batch_001_post_metadata.json (400件)

[エピソードごとの制作] ─── batch_produce.py で一括実行
    │
    ├─ ComfyUI Flux API → ep{N}/images/*.png (7枚)
    ├─ VOICEVOX API → ep{N}/audio/*.wav (6セクション + ポーズ + combined.wav)
    ├─ タイミング計算 → ep{N}/images/imglist.txt
    ├─ ASS字幕生成 → ep{N}/output/subtitles.ass
    └─ ffmpeg 2パス合成 → ep{N}/output/wakufact_ep{N}_jp_sub_v{ver}.mp4

[投稿]
    ├─ post_youtube.py → YouTube Shorts アップロード
    └─ post_x.py → X (Twitter) 動画ツイート
```

---

## 3. 台本構成

`batch_001_trivia_50.json` に50エピソード分を格納。

各エピソードの構成:
- ep番号、カテゴリ、日英タイトル
- 日英台本: `hook` → `develop_1` → `develop_2` → `develop_3` → `climax` → `cta` (6セクション)
- 映像指示、BGMスタイル、CTA

画像ラベル (7枚/ep): `01_hook`, `02_intro`, `03_develop_1`, `04_develop_2`, `05_develop_3`, `06_climax`, `07_cta`

---

## 4. ComfyUI Flux 画像生成設定

### 縦型 (デフォルト)
- 生成解像度: **512x896** (メモリ効率)
- アップスケール: ffmpeg Lanczos フィルタで **1080x1920**
- steps: 30, cfg_scale: 3.5, sampler: euler, scheduler: normal

### 横型
- 生成解像度: **896x512**
- アップスケール: ffmpeg Lanczos フィルタで **1920x1080**
- プロンプト修正: `9:16 vertical format` → `16:9 horizontal/landscape format` に変更

### プロンプト構成
```
{シーン描写}, {カテゴリスタイル}, cinematic composition, {aspect_format}, high detail, 4k quality
```

カテゴリ別スタイル例:
- 食べ物: `vibrant food photography style, macro details, warm lighting`
- 宇宙: `cinematic space art, NASA photography style, deep cosmic colors`

### API
- ComfyUI URL: `http://127.0.0.1:8000`
- ワークフロー JSON をPOSTし、`/history/{prompt_id}` でポーリング

---

## 5. VOICEVOX 音声合成設定

### API
- URL: `http://localhost:50021`
- フロー: `/audio_query` → パラメータ調整 → `/synthesis`

### 話者ローテーション

| Speaker ID | 名前 | 担当EP |
|-----------|------|--------|
| 3 | ずんだもん | 1, 4, 7, 10, ... (ep % 3 == 1) |
| 2 | 四国めたん | 2, 5, 8, 11, ... (ep % 3 == 2) |
| 8 | 春日部つむぎ | 3, 6, 9, 12, ... (ep % 3 == 0) |

### セクション別音声パラメータ

| セクション | 話速 | ピッチ | 抑揚 | ポーズ(ms) |
|-----------|------|--------|------|-----------|
| hook | 1.1 | +0.02 | 1.3 | 800 |
| develop_1 | 1.0 | 0 | 1.1 | 500 |
| develop_2 | 0.95 | 0 | 1.2 | 600 |
| develop_3 | 1.0 | 0 | 1.1 | 500 |
| climax | 0.9 | +0.02 | 1.4 | 1000 |
| cta | 1.05 | 0 | 1.2 | 0 |

### 生成ファイル (ep01例)
```
ep01/audio/
├── 01_hook.wav
├── pause_hook.wav (800ms無音)
├── 02_develop_1.wav
├── pause_develop_1.wav (500ms)
├── ...
├── 06_cta.wav
└── combined.wav (全セクション+ポーズ結合)
```

---

## 6. ffmpeg 動画合成設定

### 2パス方式の理由
ffmpegの `concat` デマルチプレクサと ASS フィルタを1パスで使うと、タイムスタンプ不整合で約16秒以降の字幕がレンダリングされない。

### Pass 1: 画像+音声 → 中間動画
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
  wakufact_ep{N}_jp_sub_v{ver}.mp4
```

### 出力仕様
| 項目 | 縦型 | 横型 |
|------|------|------|
| 解像度 | 1080x1920 (9:16) | 1920x1080 (16:9) |
| コーデック | H.264 | H.264 |
| フレームレート | 30fps | 30fps |
| 音声 | AAC 192kbps | AAC 192kbps |
| 尺 | 約40〜48秒 | 同左 |
| サイズ | 約2〜2.5MB | 同等 |

---

## 7. ASS字幕設定

### 縦型スタイル (1080x1920)
```
PlayResX: 1080
PlayResY: 1920

Style: Title  - Hiragino Sans 100px, シアン(&H0000FFFF), Bold, Outline 4, Shadow 2, Alignment 8 (上部中央)
Style: Default - Hiragino Sans 56px, 白(&H00FFFFFF), Bold, Outline 3, Shadow 1, Alignment 2 (下部中央)
```

### 横型スタイル (1920x1080)
```
PlayResX: 1920
PlayResY: 1080

Style: Title  - Hiragino Sans 120px, シアン(&H0000FFFF), Bold, Outline 6, Shadow 3, Alignment 8 (上部中央), MarginV 50
Style: Default - Hiragino Sans 80px, 白(&H00FFFFFF), Bold, Outline 4, Shadow 2, Alignment 2 (下部中央), MarginV 30
```

### 折り返しルール
- 最大文字数: Title 10文字/行、Default 17文字/行
- 優先順位:
  1. 句読点（。、！？）の直後で切る（句読点を行頭に残さない）
  2. 句読点がなければ助詞（で、に、を、が、は、の、も、て、と）の後で切る
  3. どちらもなければ max_chars で強制切断

### タイミング
- タイトル: 0:00:00.00 〜 0:00:03.00
- 各セクション: 音声開始〜音声終了に完全同期
- CTA: climax開始+1秒 〜 動画終了

---

## 8. 横画面版の作成方法

縦型を横型に変換する手順:

1. **画像生成**: プロンプトの `9:16 vertical format` を `16:9 horizontal/landscape format` に変更。生成解像度 896x512 → アップスケール 1920x1080。
2. **字幕**: `subtitles_horizontal.ass` を作成。PlayResX/Y を 1920x1080 に変更。Title 120px Alignment 8 (上部)、Default 80px Alignment 2 (下部)。
3. **imglist.txt**: 横画像パスに差し替え（または同じ画像を使う場合はスケーリング指定）。
4. **ffmpeg 2パス合成**: 通常と同じ手順。出力ファイル名を `wakufact_ep{N}_horizontal_v{ver}.mp4` とする。

---

## 9. YouTube API 投稿設定

### OAuth セットアップ
1. Google Cloud Console でプロジェクト作成
2. YouTube Data API v3 を有効化
3. OAuth 2.0 クライアントID作成 (デスクトップアプリ)
4. JSONダウンロード → `wakufact/client_secret.json` に配置
5. OAuth同意画面 → テストユーザーに自分のGoogleアカウント追加
6. `python3 post_youtube.py --auth` (ブラウザ認証 → `youtube_token.json` 生成)

### スコープ
```python
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
```

### カテゴリマッピング
| 台本カテゴリ | YouTube categoryId |
|------------|-------------------|
| 動物 | 15 (Pets & Animals) |
| 人体/歴史/食べ物/自然 | 27 (Education) |
| テクノロジー/宇宙 | 28 (Science & Technology) |

### 投稿仕様
- タイトル: 最大100文字、末尾に `#Shorts` 自動付加
- 説明: 最大5000文字、末尾に `#Shorts` 自動付加
- `selfDeclaredMadeForKids: False`
- `privacyStatus: public`
- チャンク式アップロード (256KB/chunk)
- 複数EP投稿時は10秒間隔でレート制限対策

---

## 10. 説明文の日英併記フォーマット

YouTube投稿時の説明文は日英併記。フォーマット例:

```
バナナはベリー、イチゴはベリーじゃない！植物学的な分類の驚きの事実。

Bananas are berries, but strawberries aren't! Surprising facts about botanical classification.

#WakuFact #ワクファクト #毎日雑学 #雑学 #豆知識 #Shorts
```

---

## 11. ハッシュタグ一覧

### ブランドタグ (常時使用)
`#WakuFact` `#ワクファクト` `#毎日雑学`

### プラットフォーム別タグ (メタデータ内)
各エピソードの `batch_001_post_metadata.json` に格納。

### 追加タグ (27個、YouTube投稿時に自動追加)
```
fyp, foryou, foryoupage, viral, tiktok, trending, duet,
funny, comedy, trend, humor, greenscreen, anime, love,
stitch, meme, pov, football, explore, like, dance, bts,
learnontiktok, food, memes, greenscreenvideo, video
```

---

## 12. 現在の進捗状況

### 完成済み
| 項目 | 状況 |
|------|------|
| 台本 (日英) | 50本完了 |
| 画像プロンプト | 350枚分完了 |
| VOICEVOX台本 | 50本完了 |
| 投稿メタデータ | 400件完了 |
| 動画制作 (縦型) | EP01〜EP24 完成 |
| 横画面版 | EP01 デモ完成 (v7) |
| YouTube投稿 | 15本アップ済み (説明文日英併記) |
| ブランドアセット | アイコン + バナー生成済み |

### EP01〜EP24 の動画バージョン
- EP01: v10 (最多イテレーション、字幕・タイミング調整)
- EP02〜EP04: v5
- EP05〜EP24: batch_produce.py で一括生成

---

## 13. EP25〜EP50 の残作業

1. **VOICEVOX起動**: `localhost:50021` で待機確認
2. **ComfyUI起動**: `http://127.0.0.1:8000` で待機確認
3. **バッチ実行**:
   ```bash
   python3 batch_produce.py 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50
   ```
4. **品質チェック**: 各エピソードの動画を再生確認
5. **YouTube投稿**:
   ```bash
   python3 post_youtube.py 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50
   ```
6. **X投稿** (オプション):
   ```bash
   python3 post_x.py <ep_num> jp
   ```

---

## 14. スクリプト一覧

### データ生成 (前処理、1回実行)

| スクリプト | 役割 |
|-----------|------|
| `generate_image_prompts.py` | 台本JSON → Flux用画像プロンプトJSON (350枚分) |
| `generate_voicevox_scripts.py` | 台本JSON → VOICEVOX API用台本JSON (50ep分) |
| `generate_post_metadata.py` | 台本JSON → 4SNS × 2言語の投稿メタデータJSON |
| `generate_brand_assets.py` | ComfyUIでブランドアイコン + バナー画像生成 |

### 動画制作 (エピソードごと)

| スクリプト | 役割 |
|-----------|------|
| `batch_produce.py` | メインパイプライン: 画像生成 → 音声生成 → 字幕生成 → ffmpeg 2パス合成 |
| `generate_comfyui_images.py` | ComfyUI API経由でFlux画像を生成 (EP指定で7枚) |
| `produce_episode.py` | 単一エピソード制作 (VOICEVOX + プレースホルダー画像 + ffmpeg) |
| `produce_ep02_04.py` | EP02〜04のバッチ制作ラッパー |
| `rebuild_all.py` | 全エピソードの字幕・imglist・動画を音声から再構築 |

### SNS投稿

| スクリプト | 役割 |
|-----------|------|
| `post_youtube.py` | YouTube Shorts 自動投稿 (OAuth 2.0, チャンク式アップロード) |
| `post_x.py` | X (Twitter) 動画ツイート投稿 (tweepy v1.1 + v2) |

### src/wakufact/ モジュール (CLIツール用)

| モジュール | 役割 |
|-----------|------|
| `producer.py` | パイプライン統合 |
| `audio.py` | VOICEVOX + ffmpeg 音声処理 |
| `image.py` | ComfyUI Flux 画像生成 |
| `video.py` | ffmpeg 動画合成 + ASS 字幕 |
| `cli.py` | CLI エントリポイント (`wakufact-produce` コマンド) |

---

## 15. ディレクトリ構成

```
wakufact/
├── HANDOFF.md                          # このドキュメント
├── PRODUCTION_PROCESS.md               # 制作過程メモ (本ドキュメントに統合済み)
├── pyproject.toml                      # パッケージ設定
├── .env                                # X API キー (gitignore対象)
├── client_secret.json                  # Google OAuth (gitignore対象)
├── youtube_token.json                  # YouTube認証トークン (gitignore対象)
│
├── batch_001_trivia_50.json            # 台本50本 (日英)
├── batch_001_image_prompts.json        # 画像プロンプト350枚分
├── batch_001_voicevox_scripts.json     # VOICEVOX台本50本
├── batch_001_post_metadata.json        # 投稿メタデータ400件
│
├── batch_produce.py                    # メイン制作パイプライン
├── generate_image_prompts.py           # 画像プロンプト生成
├── generate_voicevox_scripts.py        # VOICEVOX台本生成
├── generate_post_metadata.py           # 投稿メタデータ生成
├── generate_comfyui_images.py          # ComfyUI画像生成
├── generate_brand_assets.py            # ブランドアセット生成
├── produce_episode.py                  # 単一EP制作
├── produce_ep02_04.py                  # EP02-04バッチ
├── rebuild_all.py                      # 全EP再構築
├── post_youtube.py                     # YouTube投稿
├── post_x.py                           # X投稿
│
├── brand/
│   ├── icon_wakufact.png               # チャンネルアイコン
│   ├── banner_youtube.png              # YouTubeバナー
│   └── header_x.png                    # Xヘッダー
│
├── src/wakufact/
│   ├── __init__.py
│   ├── producer.py
│   ├── audio.py
│   ├── image.py
│   ├── video.py
│   └── cli.py
│
└── ep01〜ep24/                         # 完成済みエピソード
    ├── audio/
    │   ├── 01_hook.wav
    │   ├── pause_hook.wav
    │   ├── 02_develop_1.wav ... 06_cta.wav
    │   └── combined.wav
    ├── images/
    │   ├── 01_hook.png ... 07_cta.png
    │   └── imglist.txt
    └── output/
        ├── subtitles.ass               # 縦型字幕
        ├── subtitles_horizontal.ass    # 横型字幕 (ep01のみ)
        ├── wakufact_ep{N}_jp_sub_v{ver}.mp4     # 縦型動画
        └── wakufact_ep{N}_horizontal_v{ver}.mp4 # 横型動画 (ep01のみ)
```

---

## 16. 環境要件

- macOS (Apple Silicon)
- Python 3.x
- VOICEVOX v0.25.1 (ローカル起動、ポート 50021)
- ComfyUI + Flux Dev モデル (ローカル起動、ポート 8000)
- ffmpeg / ffprobe
- pip: `google-api-python-client`, `google-auth-oauthlib`, `tweepy`, `python-dotenv`
