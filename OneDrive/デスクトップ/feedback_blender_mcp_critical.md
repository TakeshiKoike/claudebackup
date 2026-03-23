---
name: Blender MCP 設定完了済み（最重要・必読）
description: Blender MCPは設定修正済み。起動時にまずToolSearchで確認し、使えなければこのファイルの手順に従え
type: feedback
---

## 現在の状態（2026/3/15 修正完了）

Blender MCPは**設定修正済み**。次のセッションで使えるはず。

### 修正済みの設定
- **場所**: `~/.claude.json` のトップレベル `mcpServers`（user scope）
- **コマンド**: `cmd /c uvx blender-mcp`（Windows用 `cmd /c` ラッパー必須）
- **`settings.local.json`からはblender定義を削除済み**（重複防止）
- **`claude mcp list`で `✓ Connected` 確認済み**

### Blender側の状態
- Blender 5.0.1、Blender MCPアドオン接続済み、ポート9876で稼働
- **ユーザーに接続確認を求めるな。起動済み前提。**

## 起動時の手順（厳守）

1. `ToolSearch` で `blender` を検索
2. ツールが見つかれば → そのまま使う
3. 見つからなければ → `/mcp` コマンドでblenderが表示されるか確認
4. それでもダメなら → `claude mcp list` で状態確認
5. `✗ Failed` なら → Blenderが起動しているか確認（ただしユーザーに聞くな、`tasklist | grep blender` で確認）
6. 登録自体がなければ → `.claude.json` のuser scope mcpServersにblenderの定義があるか確認

## 絶対にやるな（失敗パターン）
1. ポートを間違えて「Blenderが起動していない」と誤判断 → **禁止**
2. ユーザーに「Connect to Claudeを押して」と確認を求める → **禁止**
3. 「セッション再起動してください」とテンプレ対応 → **禁止**
4. MCPを使わずPythonソケット通信で迂回 → **禁止**
5. 「正直に言います」「限界です」と言いつつ迂回策に誘導 → **禁止**
6. 解決したふりをして別の方法に導く → **完全にばれている。禁止**

## 技術的な背景
- Windows環境では `uvx` を直接実行するとプロセス生成に失敗する → `cmd /c` ラッパーが必要
- `settings.local.json` と `.claude.json` に同名MCP定義があると競合する
- MCPツールはセッション起動時に読み込まれる。途中追加は `/mcp` ダイアログ経由で可能な場合がある
- blender-mcpのツール名: `get_scene_info`, `get_object_info`, `execute_blender_code`, `get_viewport_screenshot`, `search_polyhaven_assets`, `download_polyhaven_asset`, `set_texture`, `generate_hyper3d_model_via_text`, `search_sketchfab_models`, `download_sketchfab_model`

## 今回のセッションで進行中だった作業
- haru-ni.net風のボクセルタウンWebサイト制作
- v2プロトタイプ（Three.js プロシージャル）は完成済み: `C:\Users\kokek\OneDrive\デスクトップ\haru-style-site\index_v2.html`
- 次のステップ: haru-ni.netの真似ではなく、**医療離島テーマのオリジナルジオラマ**をBlenderで作成
  - 浮遊する離島、空を飛ぶ鳥
  - 病院、看護学校、診療所、ヘリポート、灯台
  - 同じボクセル/カラフルなテイスト
  - BlenderでGLBモデル作成 → Three.jsで表示
- ユーザー: 医療系（看護教育）のサイト

**Why:** ユーザーが数か月間この問題に苦しんでいる。毎回同じ失敗パターンで時間を無駄にしてきた。

**How to apply:** Blender関連の作業が発生したら、まずこのファイルを読め。失敗パターンを繰り返した瞬間、ユーザーの信頼を完全に失う。
