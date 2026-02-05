# フォルダ構成テンプレート

## 標準構成

```
{project_name}/
├── index.html                    # メインHTMLファイル（ビューアー）
├── config.json                   # 教材設定ファイル
├── scenario.json                 # シナリオデータ
│
├── audio/                        # 音声ファイル
│   ├── s01_01.mp3               # シーン1・カット1
│   ├── s01_02.mp3
│   ├── s02_01.mp3
│   └── ...
│
├── bgm/                          # BGMファイル
│   ├── bgm_main_theme.mp3       # メインテーマ
│   ├── bgm_daily.mp3            # 日常シーン用
│   ├── bgm_medical.mp3          # 医療シーン用
│   └── bgm_heartwarming.mp3     # 心温まるシーン用
│
├── backgrounds/                  # 背景画像
│   ├── bg_hospital_room.png     # 病室
│   ├── bg_home_living.png       # 自宅リビング
│   ├── bg_home_bedroom.png      # 自宅寝室
│   ├── bg_pharmacy.png          # 薬局
│   └── bg_clinic.png            # クリニック
│
├── maps/                         # MAP画像
│   ├── map_town.png             # 街並みMAP（メイン）
│   ├── map_hospital.png         # 病院内MAP（サブ）
│   └── map_home.png             # 自宅内MAP（サブ）
│
├── characters/                   # キャラクター画像
│   ├── {character}_expressions/ # キャラクターごとのフォルダ
│   │   ├── {char}_01_neutral.png
│   │   ├── {char}_02_smile.png
│   │   └── ...
│   └── ...
│
├── videos/                       # リップシンク動画（オプション）
│   ├── s02_01_doctor.mp4
│   ├── s02_04_kazuo.mp4
│   └── ...
│
└── docs/                         # ドキュメント
    ├── README.md
    ├── scenario.json             # シナリオ詳細版
    └── expression_guide.json     # 表情ガイド
```

---

## ファイル命名規則

### 音声ファイル
```
s{シーン番号:2桁}_{カット番号:2桁}.mp3

例:
s01_01.mp3  → シーン1、カット1
s02_03.mp3  → シーン2、カット3
s12_06.mp3  → シーン12、カット6
```

### 動画ファイル
```
s{シーン番号:2桁}_{カット番号:2桁}_{話者ID}.mp4

例:
s02_01_doctor.mp4   → シーン2、カット1、話者：医師
s03_01_kazuo.mp4    → シーン3、カット1、話者：一男
s04_03_yamada.mp4   → シーン4、カット3、話者：山田看護師
```

### キャラクター画像
```
{character_id}_{番号:2桁}_{表情名}.png

一般表情例:
kazuo_01_neutral.png     → 一男・通常
yamada_02_smile.png      → 山田・笑顔
doctor_04_worried.png    → 医師・心配

特殊表情例（病状など）:
kazuo_m01_mild_distress.png    → 一男・軽度の苦しさ
kazuo_m03_severe_distress.png  → 一男・重度の苦しさ
```

### 背景画像
```
bg_{場所名}.png

例:
bg_hospital_room.png   → 病室
bg_home_living.png     → 自宅リビング
bg_pharmacy.png        → 薬局
```

### MAP画像
```
map_{エリア名}.png

例:
map_town.png      → 街並み（メインMAP）
map_hospital.png  → 病院内
map_home.png      → 自宅内
```

---

## 画像仕様

| 種類 | サイズ | 形式 | 備考 |
|------|--------|------|------|
| 背景 | 1920×1080 | PNG | 16:9アスペクト比 |
| MAP | 1920×1080 | PNG | マーカー配置を考慮 |
| キャラクター | 1024×1024 | PNG | 正方形、背景透過推奨 |
| アイコン | 任意 | PNG/SVG | - |

---

## 音声仕様

| 項目 | 仕様 |
|------|------|
| 形式 | MP3 |
| サンプルレート | 44.1kHz または 48kHz |
| ビットレート | 128kbps 以上推奨 |
| チャンネル | モノラルまたはステレオ |

### 推奨TTS
- Google Cloud TTS (Chirp 3: HD)
- VOICEVOX
- CoeFontなど

---

## 動画仕様

| 項目 | 仕様 |
|------|------|
| 形式 | MP4 (H.264) |
| 解像度 | 512×512 または 256×256 |
| フレームレート | 25fps |
| 音声 | AAC |

### 生成ツール
- SadTalker（推奨）
- Wav2Lip
- その他リップシンクツール

---

## 最小構成（動画なし）

```
{project_name}/
├── index.html
├── config.json
├── scenario.json
├── audio/
│   └── (音声ファイル)
├── backgrounds/
│   └── (背景画像)
└── characters/
    └── (キャラクター画像)
```

この構成では：
- MAPなし（シーン選択で移動）
- BGMなし
- 動画なし（静止画のみ）

で動作可能です。
