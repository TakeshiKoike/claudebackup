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
| キャラクター | koike1（Character Creator） |
| リップシンク | uLipSync |
| MCP | MCP For Unity（UE5 が使用中のため手動操作） |

---

## 進捗状況（2026-01-27 22:50 更新）

### セッション終了時点

### 完了
- [x] Unity 6 プロジェクト作成
- [x] CC キャラクター (koike1) インポート
- [x] uLipSync パッケージインポート
- [x] uLipSync コンポーネント追加
- [x] uLipSyncBlendShape コンポーネント追加
- [x] Skinned Mesh Renderer: CC_Base_Body 設定
- [x] Phoneme - BlendShape マッピング設定
- [x] uLipSync Profile 設定（uLipSync-Profile-Sample 使用）
- [x] イベント接続（uLipSync → uLipSyncBlendShape）

### 次にやること
- [ ] **Audio Source を koike1 に追加** ← 今ここ
- [ ] Audio Source Proxy に Audio Source を設定
- [ ] VOICEVOX 連携テスト
- [ ] LLM (ELYZA) 連携
- [ ] 音声認識連携
- [ ] 全体統合テスト

---

## koike1 コンポーネント設定（現在）

### U Lip Sync Blend Shape (Script)
| 項目 | 値 |
|------|-----|
| Skinned Mesh Renderer | CC_Base_Body |
| Phoneme A | Open |
| Phoneme I | Wide |
| Phoneme U | Tight-O |
| Phoneme E | Wide |
| Phoneme O | Tight-O |

### U Lip Sync (Script)
| 項目 | 値 |
|------|-----|
| Profile | uLipSync-Profile-Sample |
| On Lip Sync Update | → uLipSyncBlendShape.OnLipSyncUpdate (koike1) |
| Audio Source Proxy | 未設定（次のステップ） |

---

## 次のステップ詳細

### Audio Source 設定
1. koike1 に **Add Component** → **Audio Source**
2. U Lip Sync (Script) の **Audio Source Proxy** に Audio Source を設定

### VOICEVOX 連携
1. VOICEVOX API (localhost:50021) から音声取得
2. AudioClip に変換
3. Audio Source で再生 → uLipSync がリップシンク

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
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────┐
│ Unity                                               │
│  ┌──────────────┐    ┌──────────────────────────┐  │
│  │ Audio Source │ →  │ uLipSync → BlendShape    │  │
│  └──────────────┘    └──────────────────────────┘  │
│                              ↓                      │
│                      ┌──────────────┐              │
│                      │ koike1 (CC)  │              │
│                      │ リップシンク  │              │
│                      └──────────────┘              │
└─────────────────────────────────────────────────────┘
```

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
