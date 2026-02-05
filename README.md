# ビジュアルノベル教材テンプレート

医療・看護教育用インタラクティブビジュアルノベル教材を作成するための汎用テンプレートです。

## 概要

このテンプレートを使用することで、以下のような教材を効率的に作成できます：

- **COPD訪問看護教材** - 在宅療養を支える訪問看護
- **助産教材** - 妊娠初期の経験
- **その他医療シミュレーション** - 様々な症例・シナリオに対応

## 特徴

- インタラクティブなビジュアルノベル形式
- キャラクターの表情変化・リップシンク動画対応
- MAP移動による没入感
- 知識解説パネル
- クイズ機能
- BGM・音声対応
- レスポンシブデザイン

---

## クイックスタート

### 方法1: Webエディターを使用（推奨）

```bash
# ローカルサーバーを起動
cd visual_novel_template
python3 -m http.server 8080

# ブラウザで開く
# エディター: http://localhost:8080/editor.html
# ビューアー: http://localhost:8080/viewer.html
```

1. **editor.html** でシナリオを作成
   - プロジェクト設定（タイトル、患者情報、テーマカラー）
   - シーン・カットの追加・編集
   - 知識パネル・クイズの設定
   - JSONとしてエクスポート

2. **viewer.html** で再生
   - エディタで作成したJSONファイルを読み込み
   - または「デモデータ」ボタンでCOPDサンプルを体験

### 方法2: JSONを直接編集

### 1. テンプレートをコピー

```bash
cp -r visual_novel_template my_new_project
cd my_new_project
```

### 2. 設定ファイルを編集

`config.json` を開いて教材情報を設定：

```json
{
  "meta": {
    "title": "あなたの教材タイトル",
    "subtitle": "サブタイトル",
    ...
  }
}
```

### 3. シナリオを作成

`scenario.json` にシーンとカットを定義：

```json
{
  "scenes": [
    {
      "id": 1,
      "title": "シーン1",
      "cuts": [
        {"id": "s01_01", "speaker": "narration", "text": "..."}
      ]
    }
  ]
}
```

### 4. アセットを配置

- `audio/` - 音声ファイル
- `backgrounds/` - 背景画像
- `characters/` - キャラクター画像
- `videos/` - リップシンク動画（オプション）

### 5. ブラウザで確認

```bash
# ローカルサーバーを起動
python3 -m http.server 8080

# ビューアーで開く
open http://localhost:8080/viewer.html
```

---

## ファイル構成

```
visual_novel_template/
├── README.md                    # このファイル
├── editor.html                  # Webベースシナリオエディター
├── viewer.html                  # Webベースシナリオビューアー
├── config_template.json         # 設定テンプレート
├── scenario_template.json       # シナリオテンプレート
│
├── demo_assets/                 # デモ用アセット（COPD教材）
│   ├── backgrounds/             # 背景画像（5枚）
│   └── characters/              # キャラクター画像（63枚）
│
├── examples/                    # サンプルファイル
│   ├── copd_config.json         # COPD設定サンプル
│   ├── copd_scenario.json       # COPDシナリオサンプル
│   └── copd_asset_list.md       # アセットリスト
│
└── docs/
    ├── folder_structure.md      # フォルダ構成詳細
    ├── scenario_guide.md        # シナリオ作成ガイド
    └── asset_guide.md           # アセット作成ガイド
```

---

## 設定ファイル（config.json）

### 基本情報

```json
{
  "meta": {
    "title": "教材タイトル",
    "subtitle": "サブタイトル",
    "version": "1.0.0",
    "author": "作成者",
    "institution": "所属機関",
    "targetAudience": "対象者"
  }
}
```

### テーマカラー

```json
{
  "theme": {
    "primaryColor": "#2d5a27",
    "secondaryColor": "#4a7c43",
    "accentColor": "#8bc34a"
  }
}
```

### キャラクター定義

```json
{
  "characters": {
    "protagonist": {
      "id": "hanako",
      "name": "せいれい花子",
      "role": "patient",
      "folder": "hanako_expressions",
      "voice": "ja-JP-Chirp3-HD-Leda"
    }
  }
}
```

### 機能の有効/無効

```json
{
  "features": {
    "enableMaps": true,
    "enableBgm": true,
    "enableVideo": true,
    "enableQuiz": true,
    "enableKnowledge": true
  }
}
```

---

## シナリオファイル（scenario.json）

### シーン定義

```json
{
  "scenes": [
    {
      "id": 1,
      "title": "イントロ",
      "background": null,
      "bgm": "main_theme",
      "cuts": [...],
      "knowledge": {...},
      "quiz": {...}
    }
  ]
}
```

### カット定義

```json
{
  "id": "s02_01",
  "speaker": "doctor",
  "text": "セリフテキスト",
  "characters": ["patient", "doctor"],
  "type": "dialogue"
}
```

### タイプ

| type | 説明 |
|------|------|
| narration | ナレーション |
| dialogue | セリフ |
| thought | 心の声 |

---

## 新規教材の作成手順

### Step 1: 企画

1. 教材のテーマ・学習目標を決定
2. 主人公と登場人物を設計
3. シーン構成を作成（12シーン程度推奨）
4. 各シーンのカット割りを作成

### Step 2: シナリオ作成

1. `scenario_template.json` をコピー
2. シーンとカットを記述
3. 知識解説とクイズを追加

### Step 3: アセット準備

1. **キャラクター画像** - 各キャラクター9表情
2. **背景画像** - シーンごとの背景
3. **音声ファイル** - Google Cloud TTS等で生成
4. **BGM** - 著作権フリー素材を使用

### Step 4: 動画生成（オプション）

1. SadTalkerをセットアップ
2. 音声とキャラクター画像からリップシンク動画を生成
3. `videos/` フォルダに配置

### Step 5: 統合・テスト

1. HTMLファイルを生成/更新
2. ローカルサーバーで動作確認
3. 全シーン・全カットをテスト

---

## ツール

### 音声生成
- Google Cloud TTS (Chirp 3: HD)
- VOICEVOX
- CoeFont

### 画像生成
- Stable Diffusion
- DALL-E
- Midjourney

### リップシンク動画生成
- SadTalker（推奨）
- Wav2Lip

### 動画変換
```bash
# H.264に変換
ffmpeg -i input.mp4 -c:v libx264 -c:a aac -movflags +faststart output.mp4
```

---

## 既存教材からの移行

### COPD教材の構造

```
copd_video_package/
├── copd_visual_novel_v2.32_video_complete.html
├── audio/
├── bgm/
├── backgrounds/
├── maps/
├── characters/
└── videos/
```

### 助産教材の構造

```
midwifery_video_package/
├── scene_data.json
├── audio/
├── characters/
└── videos/
```

---

## ライセンス

教育目的での使用を想定しています。

---

## 問い合わせ

質問やフィードバックは、作成者までご連絡ください。
