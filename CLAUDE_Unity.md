# デジタル模擬患者プロジェクト - Unity + CC + uLipSync

## 最終目標
LLM リアルタイムリップシンク AI 患者会話システム

```
ユーザー音声 → 音声認識 → LLM (ELYZA) → VOICEVOX (TTS) → 音声 → uLipSync → キャラクター発話
```

---

## 担当: 2番さん（Claude Code）

---

## 現在のプロジェクト

### Unity プロジェクト ★現在使用
| 項目 | 値 |
|------|-----|
| プロジェクト名 | My project |
| パス | `C:\zzz\My project` |
| エンジン | Unity 6 (6000.0.23f1) |
| キャラクター | **koike2**（Character Creator） |
| リップシンク | uLipSync |
| MCP | MCP For Unity |

---

## 進捗状況（2026-01-29 15:50 更新）

### 完了
- [x] Unity 6 プロジェクト作成
- [x] CC キャラクター (koike2) インポート
- [x] uLipSync パッケージインポート
- [x] uLipSync 設定完了
- [x] VOICEVOX 連携完了
- [x] LLM (ELYZA) 連携完了
- [x] WebGL ビルド（Web プロファイル）
- [x] WebGL 圧縮設定を Disabled に変更
- [x] 正しいシーン（koike2）をビルドに含める
- [x] WebGL ブラウザ表示確認
- [x] ChatUI.cs スクリプト作成

### 次にやること
- [ ] **UI作成（Canvas, InputField, Button）+ ChatUIアタッチ** ← 今ここ
- [ ] 音声認識連携
- [ ] 全体統合テスト

---

## koike2 コンポーネント設定（現在）

### U Lip Sync Blend Shape (Script)
| 項目 | 値 |
|------|-----|
| Skinned Mesh Renderer | CC_Base_Body |
| Phoneme A | Mouth_Open |
| Phoneme I | Mouth_Widen |
| Phoneme U | Mouth_Pucker |
| Phoneme E | Mouth_Widen |
| Phoneme O | Mouth_Open |

### U Lip Sync (Script)
| 項目 | 値 |
|------|-----|
| Profile | JapaneseProfile または uLipSync-Profile-UnityChan |
| On Lip Sync Update | → uLipSyncBlendShape.OnLipSyncUpdate (koike2) |
| Audio Source Proxy | uLipSyncAudioSource (koike2) |

### VoicevoxSpeaker (Script)
| 項目 | 値 |
|------|-----|
| Voicevox Url | http://localhost:50021 |
| Speaker Id | 11（玄野武宏・男性） |
| Audio Source | koike2 の Audio Source |

### PatientAI (Script)
| 項目 | 値 |
|------|-----|
| Ollama Url | http://localhost:11434/api/generate |
| Model Name | hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF:latest |
| Voicevox Speaker | koike2 の VoicevoxSpeaker |

---

## 重要：Character Creator エクスポート設定

CC からエクスポートする際、以下の設定が必要：

1. Target Tool Preset: **Unity 3D**
2. 歯車アイコンをクリック → Export FBX Advanced Setting
3. **「Mouth Open as Morph」にチェック** ← これがないと口が開かない！

---

## Unity MCP 設定状況

| 項目 | 状態 |
|------|------|
| Unity 側 | Session Active（緑）|
| Claude Code 側 | Not Configured（UE5 MCP 使用中） |
| Claude CLI パス | `C:\Users\kokek\AppData\Roaming\npm\claude.cmd` |
| Socket Port | 6400 |

---

## 既存リソース

| 項目 | 値 |
|------|-----|
| LLM | Ollama + ELYZA-JP-8B |
| TTS | VOICEVOX（localhost:50021） |
| GPU | NVIDIA RTX 4090 |
| 患者画像 | `C:\Users\kokek\Downloads\ComfyUI_00238_.png` |

---

## システム構成図

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 音声認識    │ →  │ LLM         │ →  │ VOICEVOX    │
│ (未実装)    │    │ ELYZA-JP-8B │    │ TTS         │
│             │    │ PatientAI   │    │ Speaker:11  │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────┐
│ Unity                                               │
│  ┌──────────────┐    ┌──────────────────────────┐  │
│  │ Audio Source │ →  │ uLipSync → BlendShape    │  │
│  │ VoicevoxSpkr │    │ (Mouth_Open etc.)        │  │
│  └──────────────┘    └──────────────────────────┘  │
│                              ↓                      │
│                      ┌──────────────┐              │
│                      │ koike2 (CC)  │              │
│                      │ リップシンク  │              │
│                      └──────────────┘              │
└─────────────────────────────────────────────────────┘
```

## スクリプトファイル

| ファイル | 説明 |
|----------|------|
| `Assets/Scripts/VoicevoxSpeaker.cs` | VOICEVOX API 連携 |
| `Assets/Scripts/PatientAI.cs` | LLM (Ollama/ELYZA) 連携 |
| `Assets/Scripts/ChatUI.cs` | ブラウザ用テキスト入力UI |

---

## WebGL ビルド

### ビルド場所
```
C:\zzz\
├── index.html
├── Build/
└── TemplateData/
```

### ローカル実行方法
```bash
cd C:\zzz
python -m http.server 8080
# ブラウザで http://localhost:8080 を開く
```

### 注意：Brotli 圧縮問題
デフォルトの Brotli 圧縮は Python の http.server で動作しない。

**解決策**: Edit → Project Settings → Player → Web → Publishing Settings → **Compression Format を Disabled** に変更してリビルド

### Web 版の制限事項
- VOICEVOX/Ollama への localhost 接続はブラウザから直接不可（CORS）
- 本番運用には中継サーバーが必要

### CORS 対応起動方法（ローカルテスト用）

**VOICEVOX（CORS有効）:**
```
"C:\Users\kokek\AppData\Local\Programs\VOICEVOX\VOICEVOX.exe" --cors_policy_mode all
```

**Ollama（CORS有効）:**
```powershell
$env:OLLAMA_ORIGINS="*"
ollama serve
```
または Windows スタートメニューから Ollama を起動

---

## 移植情報

### コピー対象
```
C:\zzz\My project
```

### 除外フォルダ
- `Library/`
- `Temp/`
- `Logs/`
- `.vs/`
- `obj/`

### 移植先で必要なもの
- Unity 6 (6000.0.23f1)
- CC/iC Importer URP 2.2.1
- uLipSync（Package Manager）
