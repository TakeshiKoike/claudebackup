# デジタル模擬患者プロジェクト

## 起動時ルール（最優先・厳守）

**セッション開始時・再起動時に、必ず以下を実行すること：**

1. `memory/MEMORY.md` を読む（自動読み込みされる）
2. **`memory/session_handoff_20260315.md` を必ず読む**（最新の引き継ぎ書）
3. `memory/feedback_blender_mcp_critical.md` を必ず読む（Blender MCP失敗パターン）
4. `memory/` 配下の関連メモリファイルを確認する（特に手順書テーブルに記載のファイル）
5. MEMORY.md内の「未完了タスク」セクションを確認する
6. ユーザーに「前回は○○の作業をしていました。続きをしますか？」と具体的に提案する

**絶対にやってはいけないこと：**
- 過去の作業を忘れて白紙状態から始めること
- メモリファイルを読まずに作業を開始すること
- 「何をしましょうか？」と漠然と聞くこと（具体的に提案せよ）

---

## 最終目標
看護教育用のリップシンク付きデジタル模擬患者を製作する

---

## 並行作業中のアプローチ

| 担当 | アプローチ | ファイル |
|------|-----------|----------|
| 1番さん | UE5.6 + MetaHuman + Audio2Face | [CLAUDE_UE5.md](CLAUDE_UE5.md) |
| 2番さん | Unity + CC + uLipSync | [CLAUDE_Unity.md](CLAUDE_Unity.md) |
| 3番さん | Three.js + Blender MCP + VOICEVOX | [3D_LIPSYNC_PROJECT.md](3D_LIPSYNC_PROJECT.md) |

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

---

## ファイル保存ルール（厳守）

**ファイルを修正・バージョンアップする際は、元のファイルを絶対に上書き・削除しない。**

- 修正前のデータは必ずそのまま残す
- 新しいバージョンは別名保存する（ファイル名にバージョン番号や日付を付与）
- 例: `file.mp4` → 修正後は `file_v2.mp4`、さらに修正なら `file_v3.mp4`
- 元ファイルの削除はユーザーが明示的に指示した場合のみ行う
