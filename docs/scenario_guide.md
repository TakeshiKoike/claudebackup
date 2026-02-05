# シナリオ作成ガイド

## シナリオ構成の基本

### 推奨構成

| シーン数 | カット数/シーン | 総カット数 | クイズ数 |
|----------|----------------|------------|----------|
| 10-15 | 5-10 | 60-100 | 8-12 |

### シーンタイプ

1. **イントロ** - 主人公・背景紹介（1シーン）
2. **本編** - メインストーリー（8-12シーン）
3. **エンディング** - まとめ・振り返り（1シーン）

---

## シーン定義

### 基本構造

```json
{
  "id": 2,
  "title": "退院前カンファレンス",
  "background": "hospital_room",
  "bgm": "medical",
  "location": "hospital",
  "subLocation": "hospital_room",
  "cuts": [...],
  "knowledge": {...},
  "quiz": {...}
}
```

### フィールド説明

| フィールド | 必須 | 説明 |
|-----------|------|------|
| id | ○ | シーン番号（1から連番） |
| title | ○ | シーンタイトル |
| background | △ | 背景ID（nullも可） |
| bgm | △ | BGM ID |
| location | △ | MAP上の場所ID |
| subLocation | △ | サブMAP上の場所ID |
| cuts | ○ | カットの配列 |
| knowledge | △ | 知識解説（シーン終了時に表示） |
| quiz | △ | クイズ（knowledge表示後に表示） |

---

## カット定義

### 基本構造

```json
{
  "id": "s02_01",
  "speaker": "doctor",
  "text": "聖隷さん、入院中の治療で症状は改善しました。",
  "characters": ["kazuo", "doctor"],
  "type": "dialogue"
}
```

### フィールド説明

| フィールド | 必須 | 説明 |
|-----------|------|------|
| id | ○ | カットID（s{シーン}_{カット}形式） |
| speaker | ○ | 話者ID |
| text | ○ | セリフ・ナレーションテキスト |
| characters | △ | 表示するキャラクターの配列 |
| type | △ | narration / dialogue / thought |

### タイプ別の表示

```
narration: ナレーション用スタイル（緑バッジ）
dialogue:  通常のセリフ
thought:   心の声（斜体、青バッジ）
```

---

## 表情ガイド（expressionGuide）

### 構造

```json
{
  "expressionGuide": {
    "s02_01": [
      {"id": "kazuo", "expression": "kazuo_04_worried", "position": "left"},
      {"id": "doctor", "expression": "doctor_05_neutral", "position": "right"}
    ]
  }
}
```

### ポジション

```
left:   画面左側（25%位置）
center: 画面中央（50%位置）
right:  画面右側（75%位置）
```

### 表情選択のガイドライン

| セリフの内容 | 推奨表情 |
|-------------|---------|
| 挨拶・通常 | neutral (05) |
| 喜び・感謝 | smile (02), grateful (08) |
| 考え中 | thinking (03) |
| 心配・不安 | worried (04) |
| 疲れ・辛さ | tired (05) |
| 驚き | surprised (06) |
| 安心・ほっとする | relieved (07) |
| 決意・意思表明 | determined (09) |

---

## 知識解説（knowledge）

### 構造

```json
{
  "knowledge": {
    "title": "COPDとは",
    "text": "COPD（Chronic Obstructive Pulmonary Disease）は...\n\n【ポイント1】\n・項目1\n・項目2\n\n【ポイント2】\n・項目3"
  }
}
```

### 書き方のコツ

1. **タイトル** - 簡潔に（10文字以内）
2. **本文** - 箇条書きを活用
3. **構造化** - 【】で小見出しを付ける
4. **分量** - 200-400文字程度

### 例

```json
{
  "title": "在宅酸素療法（HOT）とは",
  "text": "Home Oxygen Therapyの略で、自宅で酸素吸入を行う治療法です。\n\n【機器の種類】\n・酸素濃縮器（主に自宅用）\n・液体酸素\n・携帯用ボンベ（外出用）\n\n【重要な注意点】\n・火気厳禁（2m以内）\n・酸素流量は医師の指示を守る\n・月1回の外来受診が必要"
}
```

---

## クイズ（quiz）

### 単一回答

```json
{
  "quiz": {
    "question": "COPD急性増悪時に最初に選択される治療は？",
    "options": [
      {"text": "気管挿管による人工呼吸", "correct": false},
      {"text": "NPPV（非侵襲的陽圧換気療法）", "correct": true},
      {"text": "高流量鼻カニュラ酸素療法", "correct": false},
      {"text": "ネブライザー吸入", "correct": false}
    ],
    "multipleAnswer": false,
    "explanation": "COPD急性増悪時はNPPVが第一選択です。"
  }
}
```

### 複数回答

```json
{
  "quiz": {
    "question": "COPD急性増悪の徴候として正しいのはどれか？（2つ選べ）",
    "options": [
      {"text": "膿性痰の増加", "correct": true},
      {"text": "呼吸困難の軽減", "correct": false},
      {"text": "食欲の増進", "correct": false},
      {"text": "発熱", "correct": true}
    ],
    "multipleAnswer": true
  }
}
```

### 問題作成のコツ

1. **国家試験形式** - 4択を基本とする
2. **明確な正解** - 曖昧な選択肢は避ける
3. **学習目標に沿う** - シーンの内容に関連した問題
4. **適度な難易度** - 基本事項を確認する

---

## シーンフロー（sceneFlow）

MAP移動を制御するための設定。

```json
{
  "sceneFlow": [
    {
      "sceneId": 1,
      "location": null,
      "nextLocation": "hospital",
      "showMap": false
    },
    {
      "sceneId": 2,
      "location": "hospital",
      "subLocation": "hospital_room",
      "nextLocation": "home",
      "showMap": true
    },
    {
      "sceneId": 3,
      "location": "home",
      "subLocation": "home_living",
      "nextLocation": "home",
      "showMap": true
    }
  ]
}
```

---

## テンプレートの使用例

### COPD教材のシーン構成

| シーン | タイトル | 場所 | BGM |
|--------|----------|------|-----|
| 1 | イントロ | - | main_theme |
| 2 | 退院前カンファ | 病院 | medical |
| 3 | 退院・帰宅 | 自宅 | daily |
| 4 | 訪問看護（初回） | 自宅 | heartwarming |
| 5 | 入浴介助 | 自宅 | heartwarming |
| 6 | 呼吸リハビリ | 自宅 | heartwarming |
| 7 | 薬局 | 薬局 | heartwarming |
| 8 | かかりつけ医受診 | クリニック | medical |
| 9 | ケアマネ訪問 | 自宅 | heartwarming |
| 10 | 妻との会話 | 自宅 | daily |
| 11 | 急変時の対応 | 自宅 | medical |
| 12 | エンディング | - | main_theme |

### 助産教材のシーン構成

| シーン | タイトル | 場所 | BGM |
|--------|----------|------|-----|
| 1 | イントロ | - | main_theme |
| 2 | 異変に気づく | 自宅 | daily |
| 3 | パートナーへの相談 | 自宅 | daily |
| 4 | 友人への相談 | カフェ | daily |
| 5 | 薬局で検査薬購入 | 薬局 | daily |
| 6 | 妊娠について調べる | 自宅 | thinking |
| 7 | クリニック受付 | クリニック | medical |
| 8 | 診察・検査 | クリニック | medical |
| 9 | パートナーへ報告 | 自宅 | heartwarming |
| 10 | 出産の意思決定 | クリニック | heartwarming |
| 11 | 母子手帳の交付 | 支援センター | heartwarming |
| 12 | エンディング | - | main_theme |

---

## チェックリスト

### シナリオ完成時

- [ ] 全シーンにIDとタイトルがある
- [ ] 全カットにIDとspeakerとtextがある
- [ ] カットIDが連番になっている（s01_01, s01_02...）
- [ ] 知識解説が各シーンに含まれている
- [ ] クイズの正解が1つ以上設定されている
- [ ] 表情ガイドが全カットに設定されている

### JSON検証

```bash
# JSONの構文チェック
python3 -m json.tool scenario.json > /dev/null
```
