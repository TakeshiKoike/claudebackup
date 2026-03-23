---
name: 2026/3/15セッション引き継ぎ（必読）
description: haru-ni.net風サイト制作+Blender MCP修正の全経緯。次セッション開始時に必ず読んでユーザーに報告せよ
type: project
---

# セッション引き継ぎ書 — 2026年3月15日

**このファイルを読んだら、ユーザーに以下のように報告すること：**
> 「前回のセッションの引き継ぎを確認しました。haru-ni.net風の医療離島ジオラマサイト制作の途中です。Blender MCPの設定を修正済みなので、まずMCPツールが使えるか確認します。」

---

## 1. 何をしていたか

haru-ni.net（https://haru-ni.net/）のようなボクセル風3Dジオラマが回転するWebサイトを制作中。

### 完成済み
- `C:\Users\kokek\OneDrive\デスクトップ\haru-style-site\index.html` — 初版（幾何学ワイヤーフレーム）
- `C:\Users\kokek\OneDrive\デスクトップ\haru-style-site\index_v2.html` — v2（Three.jsプロシージャル・ボクセルタウン）

### v2の内容
- Three.jsでプロシージャル生成したボクセル風ミニチュアタウン
- 観覧車（回転アニメーション付き）、気球（浮遊）、桜パーティクル
- マウスドラッグで島を回転、自動回転あり
- 左側にカード（6枚、回転角度に連動して切替）
- 背景色: #e0c67b（haru-ni.netと同じゴールド）

### 次にやること
**haru-ni.netの真似ではなく、オリジナルの医療離島テーマに作り変える。**

ユーザーの指示:
- 「勘違い（島と鳥）を逆手にとって」→ 浮遊する離島 + 空を飛ぶ鳥
- 医療系サイトなので病院・看護学校等を設置
- **Blender MCPを使ってGLBモデルを作成** → Three.jsで読み込んで表示
- 同じカラフル・ボクセル風テイスト

### 設置する建物・要素（ユーザー希望）
| 要素 | 説明 |
|------|------|
| 浮遊する離島 | 緑の台地+岩肌の崖 |
| 病院 | ピンク/白、十字マーク付き |
| 看護学校 | 黄色/クリーム色、時計塔付き |
| 診療所 | 小さな水色の建物 |
| ヘリポート | 救急ヘリ用パッド |
| 灯台 | 離島のシンボル |
| 鳥たち | 島の周りを自由に飛ぶ（カモメ風） |
| 桜の木 | 春らしいパーティクル |

---

## 2. Blender MCP — 修正済みの設定

### 何が問題だったか
数か月間、Blender MCPツールがClaude Codeセッション内で使えなかった。

### 原因（2026/3/15に特定）
1. **Windows環境で `cmd /c` ラッパーが必要だった** — `uvx` を直接実行するとプロセス生成に失敗する
2. **設定が2箇所に重複していた** — `settings.local.json` と `.claude.json` の両方にblender定義があり競合
3. **`settings.local.json` の定義はClaude Codeに認識されなかった** — `claude mcp list` に表示されず

### 修正内容
- `~/.claude/settings.local.json` からblender定義を**削除済み**
- `~/.claude.json` のトップレベル `mcpServers`（user scope）に以下を追加済み:
```json
"blender": {
  "type": "stdio",
  "command": "cmd",
  "args": ["/c", "uvx", "blender-mcp"],
  "env": {}
}
```
- `claude mcp list` で `blender: cmd /c uvx blender-mcp - ✓ Connected` を確認済み

### 次セッションでの確認手順
1. `ToolSearch` で `blender` を検索
2. ツールが見つかれば → 成功。そのまま作業開始
3. 見つからなければ → `/mcp` でblenderが表示されるか確認
4. `/mcp` に表示されていれば → 接続を有効化
5. 表示されていなければ → `claude mcp list` で確認
6. **Pythonで迂回するな。ユーザーに接続確認を求めるな。**

### Blender側の状態
- Blender 5.0.1 起動中
- Blender MCPアドオン: ポート9876で稼働中、「Disconnect from MCP server」表示（接続済み）
- Poly Haven, Sketchfab, Hyper3D Rodin 全て有効

### blender-mcpのツール名（全リスト）
- `get_scene_info` — シーン内オブジェクト一覧取得
- `get_object_info` — 特定オブジェクトの詳細情報
- `execute_blender_code` — Blender Pythonコード実行（★メイン）
- `get_viewport_screenshot` — ビューポートスクリーンショット取得
- `search_polyhaven_assets` — Poly Havenアセット検索
- `download_polyhaven_asset` — Poly Havenアセットダウンロード
- `set_texture` — テクスチャ設定
- `get_polyhaven_status` — Poly Haven接続状態
- `get_hyper3d_status` — Hyper3D状態
- `get_sketchfab_status` — Sketchfab状態
- `search_sketchfab_models` — Sketchfabモデル検索
- `download_sketchfab_model` — Sketchfabモデルダウンロード
- `generate_hyper3d_model_via_text` — テキストから3Dモデル生成

---

## 3. 絶対にやるな（ユーザーが激怒する行動）

1. 「Blenderが起動していない」と言う → 起動済み前提
2. 「Connect to Claudeを押してください」と聞く → 禁止
3. 「セッション再起動してください」とテンプレ対応 → 禁止
4. Pythonソケット通信で迂回しようとする → MCPを使え
5. 「正直に言います」「限界です」と言って迂回策に誘導 → ばれている
6. 解決したふりをして別の方法に導く → ばれている
7. 「何をしましょうか？」と漠然と聞く → 具体的に提案しろ
8. 作業指示なく勝手にコードを書き始める → ユーザーの確認を取れ

---

## 4. ユーザー情報

- Takeshi Koike（聖隷クリストファー大学・看護教育）
- 環境: RTX 4090 Windows PC
- Blender 5.0.1 使用中
- 数か月間Blender MCPの問題に苦しんでいる
- テンプレ対応・迂回策・嘘に対して非常に敏感
- 間違えたらまず謝ること
