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

## 進捗状況（2026-02-05 15:45 更新）

### セッション履歴

#### 2026-02-05 セッション開始
- Mac環境（macOS Darwin 25.2.0）でClaude Code起動
- Unity MCP接続確認中
- 前回の進捗を確認し、作業再開

#### 2026-01-27 セッション
- uLipSync設定完了
- BlendShapeマッピング設定完了

---

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
- [x] Unity UI作成（Canvas, InputField, Button）+ ChatUIアタッチ
- [x] 日本語フォント設定（Noto Sans JP）
- [x] HTML側の入力欄追加（WebGL用）
- [x] JavaScript → Unity連携（SendChatFromWeb）
- [x] WebGL版テキスト入力動作確認

### 既知の問題・制限
- **WebGLでのリップシンク制限**: 長文（複数の「。」を含む）では途中でリップシンクが止まる
  - Unity Editorでは正常動作
  - 対策: LLMの応答を1文に制限するプロンプト設定
- **ビルド時のindex.html上書き**: Unity再ビルドのたびにカスタムindex.htmlが上書きされる
  - 対策: ビルド後に手動でindex.htmlを修正、またはカスタムテンプレート作成

### 次にやること
- [ ] カスタムWebGLテンプレート作成（index.html上書き問題解決）
- [ ] カメラ位置・背景の調整
- [ ] 音声認識連携（オプション）
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
| `Assets/Scripts/ChatUI.cs` | ブラウザ用テキスト入力UI + SendChatFromWeb() |

### ChatUI.cs の重要メソッド
- `SendChatFromWeb(string message)`: JavaScriptから呼び出されるpublicメソッド

### index.html カスタマイズ内容
- HTMLの入力欄（`#chat-input`）を追加
- JavaScript で `gameInstance.SendMessage('chatmanager', 'SendChatFromWeb', message)` を呼び出し
- Unity内のInputFieldは WebGL で動作しないため、HTML側で入力を受け付ける

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
python -m http.server 8000
# ブラウザで http://localhost:8000 を開く
```

### 一括起動バッチファイル
`C:\zzz\start.bat` をダブルクリックで以下が起動：
- VOICEVOX（CORS有効）
- Ollama（CORS有効）
- Python HTTPサーバー
- ブラウザ自動オープン

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
