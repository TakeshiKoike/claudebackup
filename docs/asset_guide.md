# アセット作成ガイド

## キャラクター画像

### 仕様

| 項目 | 値 |
|------|-----|
| サイズ | 1024×1024 px |
| 形式 | PNG（透過推奨） |
| 背景 | 透過 or 単色（ベージュ等） |
| 構図 | バストアップ（胸から上） |

### 必要表情（1キャラクターあたり）

#### 一般表情（9種類）

| 番号 | 表情名 | ファイル名 | 用途 |
|------|--------|-----------|------|
| 01 | neutral | {char}_01_neutral.png | 通常・デフォルト |
| 02 | smile | {char}_02_smile.png | 笑顔・喜び |
| 03 | thinking | {char}_03_thinking.png | 考え中・熟考 |
| 04 | worried | {char}_04_worried.png | 心配・不安 |
| 05 | tired | {char}_05_tired.png | 疲れ・困憊 |
| 06 | surprised | {char}_06_surprised.png | 驚き |
| 07 | relieved | {char}_07_relieved.png | 安心・ほっとする |
| 08 | grateful | {char}_08_grateful.png | 感謝 |
| 09 | determined | {char}_09_determined.png | 決意・意思 |

#### 特殊表情（患者キャラクター用）

| 番号 | 表情名 | ファイル名 | 用途 |
|------|--------|-----------|------|
| m01 | mild_distress | {char}_m01_mild_distress.png | 軽度の苦痛 |
| m02 | moderate_distress | {char}_m02_moderate_distress.png | 中程度の苦痛 |
| m03 | severe_distress | {char}_m03_severe_distress.png | 重度の苦痛 |
| m04 | coughing | {char}_m04_coughing.png | 咳き込み |
| m05 | using_oxygen | {char}_m05_using_oxygen.png | 酸素吸入中 |
| m06 | resting | {char}_m06_resting.png | 休息中 |
| m07 | recovering | {char}_m07_recovering.png | 回復中 |
| m08 | breathing_exercise | {char}_m08_breathing_exercise.png | 呼吸練習 |
| m09 | post_exertion | {char}_m09_post_exertion.png | 労作後 |

### 生成プロンプト例（Stable Diffusion）

```
portrait of a 78 year old Japanese man, kind face,
wearing patient gown, {expression},
bust shot, looking at viewer,
simple beige background, anime style,
high quality, detailed face
```

### フォルダ構成

```
characters/
├── kazuo_expressions/
│   ├── kazuo_01_neutral.png
│   ├── kazuo_02_smile.png
│   ├── ...
│   ├── kazuo_m01_mild_distress.png
│   └── kazuo_m09_post_exertion.png
├── ichiko_expressions/
│   ├── ichiko_01_neutral.png
│   └── ...
└── yamada_expressions/
    ├── yamada_01_neutral.png
    └── ...
```

---

## 背景画像

### 仕様

| 項目 | 値 |
|------|-----|
| サイズ | 1920×1080 px |
| 形式 | PNG or JPG |
| アスペクト比 | 16:9 |

### 必要背景の例

| ID | 説明 | 備考 |
|----|------|------|
| bg_hospital_room | 病室 | ベッド、医療機器 |
| bg_home_living | 自宅リビング | ソファ、テーブル |
| bg_home_bedroom | 自宅寝室 | ベッド、サイドテーブル |
| bg_pharmacy | 薬局 | カウンター、薬棚 |
| bg_clinic | クリニック診察室 | 診察台、医師デスク |

### 生成プロンプト例

```
interior of a Japanese hospital room,
single bed, medical equipment,
window with curtains, warm lighting,
anime background style, detailed, high quality
```

---

## MAP画像

### 仕様

| 項目 | 値 |
|------|-----|
| サイズ | 1920×1080 px |
| 形式 | PNG |
| スタイル | イラストマップ風 |

### マーカー配置の考慮

MAP画像上にJavaScriptでマーカーを配置するため、各施設の位置を明確に。

```
map_town.png:
  - 病院: 左上エリア
  - 自宅: 中央
  - 薬局: 右側
  - クリニック: 下部

map_hospital.png:
  - 病室: 中央上
  - ナースステーション: 左
  - 受付: 下部

map_home.png:
  - リビング: 中央
  - 寝室: 右
  - 浴室: 左上
```

---

## 音声ファイル

### 仕様

| 項目 | 値 |
|------|-----|
| 形式 | MP3 |
| サンプルレート | 44.1kHz / 48kHz |
| ビットレート | 128kbps以上 |
| チャンネル | モノラル推奨 |

### Google Cloud TTS設定

```python
from google.cloud import texttospeech

voice_settings = {
    "narrator": "ja-JP-Chirp3-HD-Aoede",      # 落ち着いた女性
    "kazuo": "ja-JP-Chirp3-HD-Charon",        # 穏やかな男性
    "ichiko": "ja-JP-Chirp3-HD-Leda",         # 優しい女性
    "yamada": "ja-JP-Chirp3-HD-Zephyr",       # 明るい女性
    "doctor": "ja-JP-Chirp3-HD-Iapetus",      # 落ち着いた男性
    "pharmacist": "ja-JP-Chirp3-HD-Kore",     # 丁寧な女性
    "sato": "ja-JP-Chirp3-HD-Vindemiatrix"   # 親しみやすい女性
}
```

### 一括生成スクリプト例

```python
import json
from google.cloud import texttospeech

def generate_audio(text, speaker, output_path):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP",
        name=voice_settings[speaker]
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open(output_path, "wb") as out:
        out.write(response.audio_content)

# シナリオから音声生成
with open("scenario.json") as f:
    data = json.load(f)

for scene in data["scenes"]:
    for cut in scene["cuts"]:
        if cut["speaker"] != "narration":
            generate_audio(
                cut["text"],
                cut["speaker"],
                f"audio/{cut['id']}.mp3"
            )
```

---

## BGMファイル

### 仕様

| 項目 | 値 |
|------|-----|
| 形式 | MP3 |
| 長さ | 2-5分（ループ再生される） |
| 音量 | 適度に控えめ（BGMとして） |

### 推奨BGM

| ID | 用途 | 雰囲気 |
|----|------|--------|
| main_theme | タイトル・エンディング | 落ち着いた、感動的 |
| daily | 日常シーン | 穏やか、明るい |
| medical | 医療シーン | 緊張感、真剣 |
| heartwarming | 心温まるシーン | 優しい、温かい |

### フリー素材サイト

- DOVA-SYNDROME
- 甘茶の音楽工房
- 魔王魂
- MusMus

---

## リップシンク動画

### 仕様

| 項目 | 値 |
|------|-----|
| 形式 | MP4 (H.264) |
| 解像度 | 512×512 px |
| フレームレート | 25fps |
| 音声 | AAC |

### SadTalker生成コマンド

```bash
cd SadTalker
source venv/bin/activate

python inference.py \
  --driven_audio ../project/audio/s02_01.mp3 \
  --source_image ../project/characters/doctor_expressions/doctor_01_smile.png \
  --result_dir ../project/videos \
  --still \
  --preprocess full
```

### 一括生成スクリプト

```python
import subprocess
import json

with open("scenario.json") as f:
    data = json.load(f)

for task in data["lipsync_tasks"]:
    audio_file = f"audio/{task['audio_file']}"
    image_file = f"characters/{task['characters'][0]}.png"
    output_name = f"s{task['scene']:02d}_{task['cut']:02d}_{task['speaker']}"

    subprocess.run([
        "python", "inference.py",
        "--driven_audio", audio_file,
        "--source_image", image_file,
        "--result_dir", "videos",
        "--still",
        "--preprocess", "full"
    ])
```

### H.264変換

SadTalkerの出力は一部ブラウザで再生できない場合があるため、変換が必要：

```bash
# 単一ファイル
ffmpeg -i input.mp4 -c:v libx264 -c:a aac -movflags +faststart output.mp4

# 一括変換
for f in videos/*.mp4; do
  ffmpeg -i "$f" -c:v libx264 -c:a aac -movflags +faststart "${f%.mp4}_h264.mp4"
done
```

---

## チェックリスト

### キャラクター画像
- [ ] 全キャラクターの9表情が揃っている
- [ ] サイズが1024×1024である
- [ ] ファイル名が規則に従っている
- [ ] 背景が統一されている

### 背景画像
- [ ] 必要な背景がすべて揃っている
- [ ] サイズが1920×1080である
- [ ] スタイルが統一されている

### 音声ファイル
- [ ] 全カットの音声がある
- [ ] ファイル名がカットIDと一致している
- [ ] 音量が統一されている

### 動画ファイル
- [ ] リップシンク対象カットの動画がある
- [ ] H.264形式で保存されている
- [ ] 音声と口の動きが同期している

---

## トラブルシューティング

### 画像が表示されない
1. ファイルパスを確認
2. ファイル名の大文字・小文字を確認
3. 画像形式（PNG/JPG）を確認

### 音声が再生されない
1. ファイル形式（MP3）を確認
2. ブラウザの自動再生ポリシーを確認
3. 音量設定を確認

### 動画が再生されない
1. H.264形式であることを確認
2. ブラウザの対応状況を確認
3. ファイルサイズが大きすぎないか確認
