# COPD模擬患者 リアルタイムリップシンクシステム

## 概要

SadTalkerで生成されたリップシンク動画から口形状を抽出し、LLM対話型の模擬患者システムにリアルタイムリップシンクを実装した。

---

## 完成したシステム

### アーキテクチャ
```
看護学生の質問（テキスト入力）
        ↓
Ollama + ELYZA-JP-8B（患者応答生成）
        ↓
VOICEVOX（男性音声合成）
        ↓
Web Audio API（音量解析）
        ↓
口スプライト切替（リアルタイムリップシンク）
        ↓
患者キャラクター（Kazuo）が発話
```

### アクセスURL
- **対話型模擬患者**: http://localhost:8888/interactive_patient.html
- **単体リップシンクテスト**: http://localhost:8888/patient_lipsync.html

---

## 作業プロセス

### 1. SadTalker動画の分析

**元データ**: `copd_video_package.zip`（約42MB）
- 13シーン分の音声ファイル（mp3）
- SadTalkerで生成済みのリップシンク動画（約70本）
- キャラクター表情画像（doctor, ichiko, kazuo, pharmacist, sato, yamada）
- 背景、BGM、マップ画像

**展開先**: `C:\Users\kokek\copd_lipsync_work\`

### 2. 口形状の抽出

#### 手法
1. FFmpegでkazuo動画からフレーム抽出（10fps）
2. 173フレームを取得
3. MediaPipeでの顔ランドマーク検出を試みるも、AI生成画像では精度不足
4. 画像解析（暗さ・エッジ密度）による口開閉度の推定に切り替え
5. 開閉度でソートし、AIUEO + 閉口の6パターンを選定

#### 生成されたスプライト
```
C:\Users\kokek\copd_lipsync_work\mouth_sprites\final\
├── base.png                 # ベース画像（Kazuo）
├── mouth_spritesheet.png    # 6パターンスプライトシート（135x68px × 6）
├── mouth_a.png              # 個別：あ
├── mouth_i.png              # 個別：い
├── mouth_u.png              # 個別：う
├── mouth_e.png              # 個別：え
├── mouth_o.png              # 個別：お
├── mouth_closed.png         # 個別：閉口
└── mouth_preview.png        # プレビュー画像
```

**スプライト順序**: `[閉, あ, い, う, え, お]`（インデックス 0-5）

### 3. リアルタイムリップシンクの実装

#### 音量→口形状マッピング
```javascript
if (volume < 0.05) mouthIndex = 0;      // 閉口
else if (volume < 0.15) mouthIndex = 3; // う
else if (volume < 0.25) mouthIndex = 4; // え
else if (volume < 0.35) mouthIndex = 2; // い
else if (volume < 0.5) mouthIndex = 5;  // お
else mouthIndex = 1;                     // あ
```

#### 技術スタック
- **音声解析**: Web Audio API (AnalyserNode)
- **描画**: Canvas 2D
- **音声合成**: VOICEVOX API (localhost:50021)
- **LLM**: Ollama API (localhost:11434)

### 4. 対話システムの実装

#### 患者プロンプト設定
```
【基本情報】
- 名前: 山田一男（やまだ かずお）
- 年齢: 72歳 男性
- 職業: 元会社員（定年退職）

【病状】
- 診断: COPD（慢性閉塞性肺疾患）ステージII
- 主な症状: 労作時の息切れ、慢性的な咳と痰
- 喫煙歴: 50年間、1日20本（現在は禁煙中）

【性格・話し方】
- 穏やかで協力的だが、病気についてはやや不安
- 敬語は使わず親しみやすい話し方
- 回答は1〜2文で簡潔に
```

#### VOICEVOX男性話者
| 話者 | ID | 推奨用途 |
|------|-----|----------|
| 青山龍星 | 13 | 低め落ち着き（デフォルト） |
| 玄野武宏 | 11 | ノーマル |
| 白上虎太郎 | 12 | 中年風 |
| 雀松朱司 | 52 | 渋め |

---

## 生成ファイル一覧

### スクリプト
| ファイル | 説明 |
|---------|------|
| `extract_aiueo.py` | MediaPipeによる口形状分類（精度不足） |
| `extract_aiueo_v2.py` | 画像解析による口開閉度推定 |
| `create_mouth_sprites.py` | スプライトシート生成 |
| `list_speakers.py` | VOICEVOX話者一覧取得 |

### HTMLデモ
| ファイル | 説明 |
|---------|------|
| `interactive_patient.html` | **対話型模擬患者（メイン）** |
| `patient_lipsync.html` | VOICEVOX単体リップシンクテスト |
| `lipsync_demo.html` | マイク入力リップシンクテスト |

---

## 起動方法

### 必要サービス
1. **VOICEVOX** - 音声合成エンジン（localhost:50021）
2. **Ollama** - LLMサーバー（localhost:11434）
3. **HTTPサーバー** - CORS対策

### 起動手順
```bash
# 1. VOICEVOXを起動（GUIアプリ）

# 2. Ollamaを起動（通常は自動起動）
ollama serve

# 3. HTTPサーバー起動
cd C:\Users\kokek\copd_lipsync_work\mouth_sprites\final
python -m http.server 8888

# 4. ブラウザでアクセス
# http://localhost:8888/interactive_patient.html
```

---

## 技術的知見

### SadTalkerの口の動きの特徴
- 自然な微妙な動き（誇張されていない）
- フレーム間の差が小さい（variance: 53.5〜55.1）
- AIUEO分類には十分な差異がある

### CORSの問題
- ローカルHTMLファイルから`localhost:50021`へのfetchはブロックされる
- HTTPサーバー経由（`http://localhost:8888`）でアクセスすることで解決

### LLM出力のクリーンアップ
ELYZA/Llama3形式のトークンが出力に混入する場合がある：
```javascript
patientResponse = patientResponse
    .replace(/<\|start_header_id\|>/g, '')
    .replace(/<\|end_header_id\|>/g, '')
    .replace(/<\|eot_id\|>/g, '')
    .trim();
```

---

## 今後の課題・拡張案

1. **音素解析の高度化**: 音量だけでなく、フォルマント解析で母音を判定
2. **表情変化**: 感情に応じた表情切り替え（kazuoには9種類の表情画像あり）
3. **音声認識**: 看護学生の音声入力対応（Web Speech API）
4. **3D化**: Unity/UE5への移植（uLipSync/Audio2Face連携）
5. **シナリオモード**: 固定シナリオとLLM自由対話のハイブリッド

---

## 関連ファイル

- **プロジェクトルート**: `C:\Users\kokek\CLAUDE.md`
- **UE5アプローチ**: `C:\Users\kokek\CLAUDE_UE5.md`
- **Unityアプローチ**: `C:\Users\kokek\CLAUDE_Unity.md`
- **本ドキュメント**: `C:\Users\kokek\COPDLLM.md`

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-01-31 | 初版作成。SadTalker動画からの口形状抽出、リアルタイムリップシンク、LLM対話システム完成 |
