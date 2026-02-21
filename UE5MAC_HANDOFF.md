# 引き継ぎ合い言葉

**「UE5MAC.md を読んで作業を継続して」**

---

## 現在の状態（2026-02-06）

### 完了
- UE5.6 インストール済み
- Ollama v0.13.5 + VOICEVOX v0.25.1 動作確認
- MCP設定を @runreal/unreal-mcp に変更済み（プラグイン不要版）

### 待機中
- **UE5 再起動**（不要なプラグイン削除済み）
- **Claude Code 再起動**（新MCP設定読み込み）
- MCP接続確認 → MetaHumanインポートへ

### 断念した方法
- flopperam/unreal-engine-mcp: C++プラグインのBuildId不一致でコンパイル失敗

---

## 重要ファイル
| ファイル | 内容 |
|---------|------|
| `/Users/takeshikoike2025/UE5MAC.md` | プロジェクト詳細・進捗 |
| `~/Library/Application Support/Claude/claude_desktop_config.json` | MCP設定 |
| `~/Documents/Unreal Projects/MyProject3/` | UE5プロジェクト |

---

## 次のアクション
1. UE5 + Claude Code 再起動後
2. `mcp__unrealMCP__get_actors_in_level` で接続確認
3. 成功したら MetaHuman インポートへ進む
