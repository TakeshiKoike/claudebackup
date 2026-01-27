# デジタル模擬患者プロジェクト - Unity + CC + uLipSync

## 最終目標
看護教育用のリップシンク付きデジタル模擬患者を製作する

---

## 担当: 2番さん（Claude Code）

---

## 現在のプロジェクト

### Unity プロジェクト ★現在使用
| 項目 | 値 |
|------|-----|
| プロジェクト名 | My project |
| エンジン | Unity 6 (6000.0.23f1) |
| キャラクター | koike1（Character Creator） |
| リップシンク | uLipSync |
| MCP | MCP For Unity（設定中） |

---

## 進捗状況（2026-01-27）

- [x] Unity 6 プロジェクト作成
- [x] CC キャラクター (koike1) インポート
- [x] uLipSync パッケージインポート
- [x] uLipSync コンポーネント追加
- [x] uLipSyncBlendShape コンポーネント追加
- [x] Skinned Mesh Renderer: CC_Base_Body 設定
- [ ] **Phoneme - BlendShape マッピング設定** ← 今ここ
- [ ] uLipSync Profile 設定
- [ ] リアルタイムテスト

---

## Unity MCP 設定状況

| 項目 | 状態 |
|------|------|
| Unity 側 | Session Active（緑）|
| Claude Code 側 | Not Configured |
| Claude CLI パス | `C:\Users\kokek\AppData\Roaming\npm\claude.cmd` |
| Socket Port | 6400 |

---

## 次のマッピング設定

| Phoneme | BlendShape |
|---------|------------|
| A | Open |
| I | Wide |
| U | Tight-O |
| E | Wide |
| O | Tight-O |

---

## 既存リソース

| 項目 | 値 |
|------|-----|
| LLM | Ollama + ELYZA-JP-8B |
| TTS | VOICEVOX（localhost:50021） |
| GPU | NVIDIA RTX 4090 |
| 患者画像 | `C:\Users\kokek\Downloads\ComfyUI_00238_.png` |
