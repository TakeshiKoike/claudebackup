# デジタル模擬患者プロジェクト

## 最終目標
看護教育用のリップシンク付きデジタル模擬患者を製作する

---

## 並行作業中のアプローチ

| 担当 | アプローチ | ファイル |
|------|-----------|----------|
| 1番さん | UE5.6 + MetaHuman + Audio2Face | [CLAUDE_UE5.md](CLAUDE_UE5.md) |
| 2番さん | Unity + CC + uLipSync | [CLAUDE_Unity.md](CLAUDE_Unity.md) |

**注意**: 各担当は自分のファイルのみ編集してください。

---

## 共通リソース

| 項目 | 値 |
|------|-----|
| LLM | Ollama + ELYZA-JP-8B |
| TTS | VOICEVOX（localhost:50021） |
| GPU | NVIDIA RTX 4090 |
| 患者画像 | `C:\Users\kokek\Downloads\ComfyUI_00238_.png` |
| MCP設定 | `C:\Users\kokek\.claude\settings.local.json` |

---

## Blender MCP 設定状況（確認済み・再確認不要）

**Blender側の設定は完了済み。ユーザーに確認を求めるな。**

- Blenderアドオン: インストール・有効化済み
- 「Connect to Claude」: 実行済み
- Claude Code側: `claude mcp add blender uvx blender-mcp` 実行済み

MCPが認識されない場合は、Claude Codeセッションの再起動のみが必要。
