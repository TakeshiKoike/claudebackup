# COPD訪問看護教材 - Claude Code 申し送り資料

## 📋 プロジェクト概要

**タイトル**: 在宅療養を支える訪問看護 - COPD事例  
**対象**: 看護学生・訪問看護師  
**形式**: インタラクティブHTML教材（音声・画像・クイズ付き）  
**作成日**: 2026年1月3日

---

## 📁 フォルダ構成

```
copd_project/
├── audio/                    # 音声ファイル（77個）
│   ├── s01_01.mp3 〜 s01_03.mp3   # シーン1（イントロ）
│   ├── s02_01.mp3 〜 s02_06.mp3   # シーン2（退院前カンファ）
│   ├── s03_01.mp3 〜 s03_06.mp3   # シーン3（退院・帰宅）
│   ├── s04_01.mp3 〜 s04_07.mp3   # シーン4（訪問看護初回）
│   ├── s05_01.mp3 〜 s05_07.mp3   # シーン5（入浴介助）
│   ├── s06_01.mp3 〜 s06_08.mp3   # シーン6（呼吸リハビリ）
│   ├── s07_01.mp3 〜 s07_06.mp3   # シーン7（薬局）
│   ├── s08_01.mp3 〜 s08_08.mp3   # シーン8（かかりつけ医受診）
│   ├── s09_01.mp3 〜 s09_07.mp3   # シーン9（ケアマネ訪問）
│   ├── s10_01.mp3 〜 s10_08.mp3   # シーン10（妻との会話）
│   ├── s11_01.mp3 〜 s11_09.mp3   # シーン11（急変時の対応）
│   └── s12_01.mp3 〜 s12_06.mp3   # シーン12（エンディング）
│
├── bgm/                      # BGM（4曲）
│   ├── bgm_main_theme.mp3    # タイトル・エンディング用
│   ├── bgm_daily.mp3         # 日常シーン用
│   ├── bgm_medical.mp3       # 医療・緊張シーン用
│   └── bgm_heartwarming.mp3  # 心温まるシーン用
│
├── backgrounds/              # 背景画像（5枚）
│   ├── bg_hospital_room.png  # 病室（シーン2）
│   ├── bg_home_living.png    # 自宅リビング（シーン3,9,10）
│   ├── bg_home_bedroom.png   # 自宅寝室（シーン4,5,6,11）
│   ├── bg_pharmacy.png       # 薬局（シーン7）
│   └── bg_clinic.png         # クリニック診察室（シーン8）
│
├── maps/                     # MAP画像（3枚）
│   ├── map_town.png          # 街並みMAP（施設ラベル付き）
│   ├── map_hospital.png      # 病院内MAP
│   └── map_home.png          # 自宅内MAP
│
├── characters/               # キャラクター表情画像（63枚）
│   ├── kazuo_expressions/    # 一男（18枚：一般9＋病状9）
│   ├── ichiko_expressions/   # 市子（9枚）
│   ├── yamada_expressions/   # 山田看護師（9枚）
│   ├── doctor_expressions/   # 主治医（9枚）
│   ├── pharmacist_expressions/ # 薬剤師（9枚）
│   └── sato_expressions/     # 佐藤ケアマネ（9枚）
│
└── docs/                     # ドキュメント
    ├── scenario.json         # シナリオ・構成データ
    └── README.md             # この申し送り資料
```

---

## 🎭 キャラクター情報

### 表情ファイル命名規則
- 一般表情: `{character}_01_neutral.png` 〜 `{character}_09_determined.png`
- 病状表情（一男のみ）: `kazuo_m01_mild_distress.png` 〜 `kazuo_m09_post_exertion.png`

### 表情一覧

| # | 一般表情 | ファイル名 |
|---|----------|-----------|
| 1 | neutral（通常） | `*_01_neutral.png` |
| 2 | smile（笑顔） | `*_02_smile.png` |
| 3 | thinking（考え中） | `*_03_thinking.png` |
| 4 | worried（心配） | `*_04_worried.png` |
| 5 | tired（疲れ） | `*_05_tired.png` |
| 6 | surprised（驚き） | `*_06_surprised.png` |
| 7 | relieved（安心） | `*_07_relieved.png` |
| 8 | grateful（感謝） | `*_08_grateful.png` |
| 9 | determined（決意） | `*_09_determined.png` |

| # | 病状表情（一男のみ） | ファイル名 |
|---|----------------------|-----------|
| 1 | mild_distress（軽度の苦しさ） | `kazuo_m01_mild_distress.png` |
| 2 | moderate_distress（中程度の苦しさ） | `kazuo_m02_moderate_distress.png` |
| 3 | severe_distress（重度の苦しさ） | `kazuo_m03_severe_distress.png` |
| 4 | coughing（咳き込み） | `kazuo_m04_coughing.png` |
| 5 | using_oxygen（酸素吸入中） | `kazuo_m05_using_oxygen.png` |
| 6 | resting（休息中） | `kazuo_m06_resting.png` |
| 7 | recovering（回復中） | `kazuo_m07_recovering.png` |
| 8 | breathing_exercise（呼吸練習） | `kazuo_m08_breathing_exercise.png` |
| 9 | post_exertion（労作後） | `kazuo_m09_post_exertion.png` |

---

## 🎬 シーン構成

| シーン | タイトル | 背景 | BGM | カット数 |
|--------|----------|------|-----|----------|
| 1 | イントロ | なし | main_theme | 3 |
| 2 | 退院前カンファ | hospital_room | medical | 6 |
| 3 | 退院・帰宅 | home_living | daily | 6 |
| 4 | 訪問看護（初回） | home_bedroom | heartwarming | 7 |
| 5 | 入浴介助 | home_bedroom | heartwarming | 7 |
| 6 | 呼吸リハビリ | home_bedroom | heartwarming | 8 |
| 7 | 薬局 | pharmacy | heartwarming | 6 |
| 8 | かかりつけ医受診 | clinic | medical | 8 |
| 9 | ケアマネ訪問 | home_living | heartwarming | 7 |
| 10 | 妻との会話 | home_living | daily | 8 |
| 11 | 急変時の対応 | home_bedroom | medical | 9 |
| 12 | エンディング | なし | main_theme | 6 |

**合計**: 12シーン、77カット、10問のクイズ

---

## 🔊 音声ファイル仕様

- **形式**: MP3
- **生成**: Google Cloud TTS (Chirp 3: HD)
- **キャラクター別音声**:
  - ナレーション: ja-JP-Chirp3-HD-Aoede（落ち着いた女性）
  - 一男: ja-JP-Chirp3-HD-Charon（穏やかな男性）
  - 市子: ja-JP-Chirp3-HD-Leda（優しい女性）
  - 山田看護師: ja-JP-Chirp3-HD-Zephyr（明るい女性）
  - 主治医: ja-JP-Chirp3-HD-Iapetus（落ち着いた男性）
  - 薬剤師: ja-JP-Chirp3-HD-Kore（丁寧な女性）
  - 佐藤ケアマネ: ja-JP-Chirp3-HD-Vindemiatrix（親しみやすい女性）

---

## 🎯 実装要件

### 基本機能
1. **シーン選択画面**: 12シーンのサムネイル付きリスト
2. **メインビジュアル**: 16:9の背景＋キャラクター表示
3. **セリフ表示**: 話者名＋テキスト（自動進行 or 手動）
4. **音声再生**: セリフに合わせた自動再生
5. **BGM**: シーンに応じたループ再生（音量調整可）

### インタラクティブ機能
1. **知識解説パネル**: 各シーン終了後に表示
2. **クイズ機能**: 選択式（単一/複数回答対応）
3. **進捗管理**: 学習済みシーンの記録
4. **MAP表示**: シーン移動時に街並みMAPを表示

### 表情制御
- セリフの内容に応じて適切な表情を選択
- 例: 心配な内容 → worried、感謝 → grateful

---

## 📝 開発時の注意点

### 画像サイズ
- 背景: 1920×1080（16:9）
- キャラクター: 1024×1024（正方形、ベージュ背景）
- MAP: 1920×1080または可変

### キャラクター表示
- 背景の上にキャラクターを重ねて表示
- ベージュ背景部分は透過処理が必要な場合あり
- 2人以上の会話時は左右に配置

### 音声同期
- 音声ファイル名とシナリオJSONのcut.idが対応
- 例: `s02_03` → `audio/s02_03.mp3`

### 心の声の表現
- `type: "thought"` の場合は特別な表示
- 例: 吹き出しを変える、フォントを斜体に

---

## ✅ 動作確認チェックリスト

- [ ] 全12シーンが正しく表示される
- [ ] 77個の音声ファイルがすべて再生される
- [ ] BGMがシーンに応じて切り替わる
- [ ] キャラクターの表情が適切に表示される
- [ ] クイズが正しく動作する（正誤判定）
- [ ] 知識解説パネルが表示される
- [ ] レスポンシブ対応（PC/タブレット/スマホ）

---

## 📞 補足情報

### 患者情報
- **氏名**: 聖隷一男（せいれい かずお）
- **年齢**: 78歳
- **疾患**: COPD（慢性閉塞性肺疾患）
- **介護度**: 要介護2
- **治療**: 在宅酸素療法（安静時2L、労作時4L）

### シナリオの医学的監修ポイント
- NPPV拒否は患者の自己決定として尊重
- 酸素流量の設定は医師の指示に基づく
- 急性増悪の徴候は正確に記載
- 介護保険制度の説明は正確（要介護者は居宅介護支援事業所が担当）

---

## 🔄 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-01-03 | 初版作成 |

---

**作成者**: Claude AI  
**依頼者**: 武嗣（たけし）先生 - 聖隷クリストファー大学
