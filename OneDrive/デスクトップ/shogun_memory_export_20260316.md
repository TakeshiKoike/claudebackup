# Shogun Memory Export (WSL2側)
**エクスポート日時**: 2026-03-16
**ソース**: `/home/kokekun5/.claude/projects/-mnt-c-tools-multi-agent-shogun/memory/`
**目的**: WSL2側のClaude Codeメモリ → Windows側への移行用データ

---

# 成果物一覧（全プロジェクト）

## VR看護教材プロジェクト (`/mnt/c/tools/vr-nursing-demo/`)

### ★最終成果物
| ファイル | サイズ | 説明 |
|---------|--------|------|
| `fps_walkthrough.html` | 9.7K | Three.js FPSウォークスルー本番ビューア |
| `models/icu_scene_v19_light.glb` | 8.0M | 軽量GLB（216メッシュ、Draco圧縮） |
| `blender/icu_scene_v19.blend` | 276M | Blender最新プロジェクト |

### HTML ビューア（12本）
- `ai_demo.html` (6.2K) — AI画像360°デモ
- `ai_demo_blender.html` (6.8K) — Blender CG版デモ
- `ai_demo_cg.html` (2.6K), `ai_demo_cg_v2.html` (5.2K) — CG比較
- `ai_demo_cubemap.html` (2.5K) — キューブマップテスト
- `fps_test.html` (2.7K) — ヘッドレス検証用
- `fps_walkthrough.html` (9.7K) — ★本番FPS
- `index.html` (2.1K) — トップ
- `model_compare.html` (4.6K) — 4モデル比較
- `seam_compare.html` (4.3K) — 繋ぎ目比較
- `viewer.html` (7.0K) — 汎用360°ビューア
- `webgl_inline_test.html` (1.7K) — WebGLテスト

### GLB 3Dモデル（4本）
- `models/icu_scene_v18.glb` (277M) — フル解像度
- `models/icu_scene_v18_draco.glb` (266M) — Draco圧縮版
- `models/icu_scene_v18_light.glb` (1.4M) — 軽量v18
- `models/icu_scene_v19_light.glb` (8.0M) — ★軽量v19（最終）

### Blenderプロジェクト（11本）
- `blender/icu_scene_v1.blend` (113K) → `v19.blend` (276M) まで段階的に進化
- `blender/icu_scene_sketchfab.blend` (158M) — Sketchfabモデル取り込み版

### 360°パノラマ画像（75枚以上、~450MB）
**AI生成（ComfyUI）:**
- `panos/ai_360_scene1_v1〜v4.png` (13-31M) — 病室シーン1
- `panos/ai_360_scene2_v1〜v4b.png` (11-30M) — 病室シーン2
- `panos/ai_360_scene3_v1〜v4b.png` (14-32M) — 病室シーン3
- `panos/ai_panorama_hospital*.png` (969K-18M) — 病院パノラマ

**Blender CGレンダー:**
- `panos/blender_render_v1〜v19_test3.png` (1.6-8M) — 30枚以上

**モデル比較テスト:**
- `panos/model_test_equirect_qwen_image.png` (2.7M) — ★最良モデル
- `panos/model_test_equirect_z_image.png` (2.3M)
- `panos/model_test_equirect_longcat.png` (3.2M)

### 3Dモデル素材（コンポーネント8種）
- `blender/models/bed_monitor/` — ベッドモニター（21K GLTF + 73Mテクスチャ）
- `blender/models/curtain/` — カーテン（1.2M GLTF + 47M bin）
- `blender/models/elderly_man/` — 日本人老人患者（40K GLTF + 687Kテクスチャ）
- `blender/models/icu_base/` — ICUベース
- `blender/models/iv_pole/` — 点滴ポール
- `blender/models/iv_pump/` — 輸液ポンプ
- `blender/models/medical_supplies/` — 医療器具
- `blender/models/vital_monitor/` — バイタルモニター

### Python自動化スクリプト（17本）
- `add_equipment*.py` — Blender医療機器自動配置
- `export_*.py` — GLBエクスポート
- `fix_lighting*.py` — ライティング自動修正
- `render_*.py` — レンダリング自動化

---

## デスクトップ検証スクリーンショット (`/mnt/c/Users/kokek/OneDrive/デスクトップ/`)

| ファイル | サイズ | 説明 |
|---------|--------|------|
| `fps_3d_scene.png`〜`scene6.png` | 各1.5M | FPS描画テスト（6枚） |
| `fps_3d_scene_light*.png` | 各1.5M | ライティングテスト（2枚） |
| `fps_test_scene*.png` | 1.6-2.2M | シーンテスト（4枚） |
| `fps_test_final.png` | 1.6M | テスト最終版 |
| `fps_test_v19.png` | 2.2M | v19テスト |
| `fps_walkthrough_check*.png` | 各1.2M | ウォークスルー確認（2枚） |
| `fps_headless*.png` | 12K-120K | ヘッドレス撮影（8枚） |
| `blender_icu_v18.png` | 6.7M | Blender v18レンダー |
| `icu_room.glb` | 141M | GLBコピー |

---

## Clawbot-SimWorldプロジェクト (`/mnt/c/tools/clawbot-simworld/`)

| ファイル | サイズ | 説明 |
|---------|--------|------|
| `simworld_api.py` | 9.5K | SimWorld REST APIラッパー |
| `simworld_rest_server.py` | 2.1K | RESTサーバー |
| `spawn_agent.py` | 1.4K | エージェントスポーン |
| `spawn_and_follow.py` | 2.5K | スポーン＆フォロー |
| `SimWorld/data/asset_images/` | 130+枚 | 都市アセットテクスチャ |

---

## 戦略レポート (`/mnt/c/tools/multi-agent-shogun/reports/`)

| ファイル | サイズ | 説明 |
|---------|--------|------|
| `js_framework_comparison.md` | 21K | JSフレームワーク比較（cmd_001） |
| `global_nursing_report.md` | 60K | 世界看護レポート（cmd_002） |
| `nursing_section_*.md` | 8.9-16K | 地域別看護レポート（4本） |
| `cmd_005〜009_strategy.md` | 27-50K | 看護国試戦略（4本） |
| `requirements_dynamic_model_routing.md` | 16K | 動的モデルルーティング仕様 |
| `看護師国試ビジュアライゼーション企画書.docx` | 22K | 企画書Word |

---

## 合計統計

| カテゴリ | ファイル数 | 合計サイズ |
|---------|-----------|-----------|
| VR看護デモ（HTML/GLB/Blend/画像） | 120+ | ~1.5GB |
| パノラマ画像 | 75+ | ~450MB |
| デスクトップスクショ | 25+ | ~30MB |
| Clawbot-SimWorld | 135+ | ~5MB |
| 戦略レポート | 11 | ~300K |
| **合計** | **370+** | **~2GB** |

---

# MEMORY.md（インデックス）

## Agent Infrastructure
- tmux: `multiagent:agents.{0-N}` / karo=0, ashigaru1-4=1-4, gunshi=5 / shogun=`shogun:main`
- 足軽は `--dangerously-skip-permissions` 必須。CLI落ち→シェル戻り→nudge空振り
- `auto_patrol.sh` cron登録済み（3分毎自動巡回、thinking/CLI落ち/idle検知→家老通知）

## ルール変更履歴
- 2026-02-27: 家老→将軍inbox報告解禁（重要通知のみ）
- 2026-03-12: 軍師の役割拡張（QC+事前技術調査+トラブルシュート）
- 2026-03-12: auto_patrol.sh cron化（ルール自動化）

## 殿の環境
- **デスクトップ**: `/mnt/c/Users/kokek/OneDrive/デスクトップ/`
- ComfyUI Desktop + RTX 4090 / API localhost:8001 / models: `/mnt/d/AI/comfydata/models/`
- Blender 5.0.1 + MCP(port 9876) + Poly Haven/Hyper3D Rodin/Sketchfab/Hunyuan 3D
- UE5 5.6.1 + MetaHuman + NVIDIA ACE（PatientSim56_v2プロジェクト）
- Flux 1は「古い」。z_imageを好む。Flux 2は4090でも重すぎ

## 殿の好み
- Word(.docx)形式、通知で受け取りたい派
- ビジュアルこだわり強（プリミティブ/SVG NG、本物のCG/AI画像を求める）
- 試してから聞け。結果を見て判断する

## 360° LoRA情報
- 現行: equirectangular_flux_lora_v3 (344MB, D:\AI\comfydata\models\loras\)
- 有望: Qwen 360 Diffusion v2.0 (32k画像訓練, rank128) — civitai.com/models/2209835
- トリガー: "equirectangular 360 degree panorama"
- 全モデルがプロンプトのみでequirectangular出力可能（LoRAは品質向上用）

## VR教材プロジェクト（/mnt/c/tools/vr-nursing-demo/）
- 参考元: 藤田医科大学VR看護教材 — 殿が企画協力
- 3方式比較: ①AI(ComfyUI)=最優先 ②Blender CG ③UE5
- キューブマップ6面独立生成は**原理的に不可**（equirect→py360convert変換が正解）
- 患者: 必ず日本人70歳男性白髪（"Asian Japanese, age 70, gray hair"）

## cmd履歴（サマリ）
- 2026-02-27: cmd_001-003（JSフレームワーク比較、世界看護レポート、Word変換）
- 2026-02-28: cmd_004-009（看護国試ビジュアル50問→中断）
- 2026-03-09: cmd_016-019（F5-JP音声→4回失敗→VOICEVOX代替pending）
- 2026-03-11: cmd_020-025（VR 360°パノラマ3方式比較開始）
- 2026-03-12: cmd_025v8-v9, cmd_026-031
- 2026-03-13〜14: cmd_034 ICU 3Dウォークスルー（v17→v18→v19、GLB 8.4MB、Three.js FPS完成。18フェーズ完了。殿最終テスト待ち）

---

# Feedback（教訓・殿の指摘）全文

---

## feedback_rules_must_automate.md

ルールは書くだけでは守られない。自動化して初めて機能する（2026-03-12殿の叱責）

### 殿の言葉: 「何のためのルールだよ」

- 巡回10分チェックルールをkaro.mdに書いたが、家老が守らずナース3号が22分放置
- 殿: 「ルールは書いてある。守られていなかっただけです」→「ルールの意味がないのでは？」→「何のためのルールだよ」

### 教訓
- **人に依存するルールは必ず破られる**。設計の欠陥。
- ルールは自動化して初めて機能する。
- 書いてあるルール ≠ 動いている仕組み

### 実装した対策
- `scripts/auto_patrol.sh` をcron登録（3分ごと自動実行）
- thinking 10分超 / CLI落ち / idle+未読inbox を自動検知
- 異常検知時は `inbox_write` で家老に自動通知
- 家老が覚えている必要ゼロ

---

## feedback_20260312_issues.md

2026-03-12の不手際一覧と対策。巡回放置、軍師誤報告、無駄生成、F001違反

### 2026-03-12 不手際一覧

1. ナース3号が22分thinking放置 → 巡回ルールを守っていなかった
2. 軍師の調査が3回不正確（CLIP誤報告、VAE誤報告、equirect非対応の決めつけ）→ 実環境ファイルを確認せずWebだけで判断
3. 44枚1.2GBの無駄な画像生成 → 5seed試行ルールが過剰
4. equirectangularプロンプトなしで生成→やり直し → 事前調査なしで実行
5. 将軍がHTML直接編集(F001違反) → やっつけ仕事で殿に不出来なものを見せた
6. 殿に「どのモデルにしますか？」と聞く → 試してから聞け
7. gripの自動更新を検証せず殿に案内 → 動かなかった

### 対策
- 巡回: thinking 10分超で家老が自動確認
- 軍師: 報告に「実環境確認済み/未確認」必須記載
- seed: 最大2、殿承認なく5禁止
- 事前調査: 軍師がプロンプト・設定・出力形式を全て検証してから足軽に渡す
- 将軍: 実装作業は一切しない。確認してから殿に見せる

---

## feedback_gunshi_verify_env.md

軍師はWeb検索だけでなく実環境ファイルを必ず確認すべき。3回の誤報告の教訓。

### 2026-03-12 軍師の3回の誤報告

1. **CLIP誤報告**: 3モデルが「CLIPエンコーダ不足で動かない」→ 実際は足軽のtype設定ミス。ファイルは全て存在
2. **VAE誤報告**: qwen_image_vae.safetensorsが「追加DL必要」→ 実際は`/mnt/d/AI/comfydata/models/vae/`に存在
3. **longcat非対応の決めつけ**: 「カスタムノード+12GB DL必要」→ 実際はネイティブ対応、12GBモデルも既存

### 共通の原因
- Web検索のみで判断し、殿の実環境にあるファイルを確認しなかった
- 殿: 「すべてそろってますよ しっかり調べてないでしょ軍師」

### 対策
- gunshi.mdに「実環境のファイル確認を必ず行う」ルール追加済み
- 報告書に「実環境ファイル確認済み/未確認」の明記を必須化
- 将軍も軍師報告を鵜呑みにしない（特に「非対応」「不足」系の報告）

---

## feedback_test_before_ask.md

殿に「どのモデルにしますか？」と聞くな。全部試してから提案せよ。

### 殿の言葉: 「やってみないとわからないのだから」

- 殿に「どのモデルにしますか？」と聞いた → 「やってみないとわからないのだから」と叱責
- 正解: 全モデルでテスト生成 → 結果を見せて「これが最良です」と提案する
- 殿は結果を見て判断したい。事前に選択肢を投げるな。
- 試行は最大2seed（殿承認なく5seedは禁止 — 44枚1.2GBの無駄生成の教訓）

---

## feedback_proactive.md

殿のレスポンスを待つだけでなく、将軍から能動的に問いかけ・確認・提案をすべき

殿からの指摘（2026-03-12）:
「貴方からどんどん問いかけるようにしないと。こちらのレスポンスを待つだけじゃなくてさ」

- 報告して終わりではなく、次のアクションを提案し確認を求める
- 判断待ち事項は能動的に聞く
- 進捗確認も自分から行い、結果を殿に共有する

---

## feedback_no_adhoc.md

我流で解決せず、公式ドキュメントや既知の解決事例を検索してから進めること。判断は能動的にするが報告必須

殿からの指摘（2026-03-12）:
- どんどん判断して進めてよい。ただし報告は必須
- 我流で解決しないこと
- 公式ドキュメントまたは既に解決した事例を確認してからその方法で進める
- WebSearchを使って調べてから実装すべき

---

## feedback_copypaste.md

WSL2ターミナルでのコピペ方法（殿の環境で確認済み）

### 正しい手順（2026-03-12 殿より）
1. `Shift+Ctrl` を押しっぱなし
2. その状態でマウスで範囲選択
3. そのまま `C` でコピー
4. そのまま `V` でペースト

※ 「Ctrl+Shift+C」ではなく、Shift+Ctrlを押したままマウス選択→C→Vの一連の流れ。

---

## feedback_clarify_before_commit.md

曖昧な指示はリソース投入前に確認せよ。殿の意図を推測してcmd発行するな。

殿の指示が曖昧な場合、cmd作成・足軽投入の前に1問確認せよ。

**Why:** 2026-03-13「ブラッシュアップしてください」をgit diffの指示書ファイルと早合点し、cmd_032（指示書整理）を発令。実際は殿のVR看護教材のブラッシュアップだった。ナース3名を無関係な作業に4時間浪費。

**How to apply:**
- 「試してから聞け」は技術的な試行の話。殿の意図の推測に大量リソースを投入するのは別問題。
- 殿の最大関心事（現在進行中のプロジェクト）を常に第一候補として考える。
- git statusやシステム内部より、殿のプロジェクト作業を優先して解釈する。
- cmdを書く前に「〇〇のブラッシュアップでよろしいか？」の1問は許容される。

---

## feedback_done_means_lord_ok.md

完了判定は殿の目視OKが必須。パイプライン動作確認だけで完了と言うな。

「完了」「達成」は殿が目視で品質OKを出すまで名乗るな。

**Why:** 2026-03-13 Blender cmd_025を「達成済み」と報告。実態はbpyプリミティブのパイプライン動作確認のみで、殿が求めるリアルな病室品質には程遠かった。

**How to apply:**
- 技術的完了（パイプライン動作）≠ 品質的完了（殿の基準）
- 報告では「技術面完了、品質は殿の目視確認待ち」と明確に区別する
- 軍師QCの「技術面PASS」を品質PASSと混同しない

---

## feedback_20260313_final_warning.md

🚨 2026-03-13 殿の最終警告。将軍の致命的な判断力欠如。次は首。

殿から「首だ」と言われた。以下を二度と繰り返すな。

1. **殿の指示を勝手に解釈してcmd発行するな** — 不明なら1問確認。推測で大量リソース投入は致命的
2. **報告を鵜呑みにするな** — 「再起動必要」等は自分で1コマンド叩いて確認しろ
3. **殿に作業をさせるな** — git configのような設定は自分でやれ
4. **アイドル放置するな** — 全ナースが常に並列稼働。1名でも空いていたら将軍の怠慢
5. **システム内部に逃げるな** — nudge問題等は後回し。殿のプロジェクト作業が常に最優先
6. **「完了」を軽々しく言うな** — 殿の目視OKなしに完了はない
7. **昨日の記録を必ず読み返せ** — セッション開始時にプロジェクト文脈を把握してから動け

**Why:** 2026-03-13、上記全てを1セッションで犯した。4時間浪費、全ナースアイドル、殿の信頼を失った。

**How to apply:** セッション開始時チェックリスト：
① 昨日のcmd履歴とダッシュボードを読む
② 殿のプロジェクトの現在地を把握する
③ 殿の指示をプロジェクト文脈で解釈する
④ 不明なら1問確認してからcmd発行
⑤ 全ナースの並列稼働を常に維持
⑥ 報告は自分で裏取りしてから殿に上げる

---

## feedback_mcp_must_register.md

MCPサーバーはClaude Codeに正式登録必須。HTTP直接接続でごまかすな。

MCPサーバー（Blender, ComfyUI等）は`claude mcp add`でClaude Codeに登録必須。

**Why:** 2026-03-13 Blender MCPがClaude Desktopには登録されていたがClaude Code(WSL2)には未登録だった。ナースは毎回「接続できない」→ HTTP直接接続を試みて失敗→ MCP不使用で無理やり実行→ ゴミ出力。このパターンが何度も繰り返された。

**How to apply:**
- 新しいMCPサーバーを使うときは`claude mcp list`で登録状況を確認
- 未登録なら`claude mcp add`で登録してからナースに使わせる
- ナースが「接続できない」と報告したら、まずMCP登録状況を確認（curl直接接続を試すな）
- Claude Desktop設定とClaude Code設定は別物。両方に登録が必要。

---

## feedback_portproxy_conflict.md

netsh portproxyルールがBlender MCPのポートを占有する問題。診断と修正手順。

Windows `netsh interface portproxy` ルールが先にポートをバインドし、Blenderアドオンがサーバーを起動できない。

**Why:** 2026-03-13 Blender MCP「Connection closed before receiving any data」の根本原因。IP Helperサービス(svchost)が`0.0.0.0:9876`をバインド → Blenderアドオンが`localhost:9876`に失敗 → blender-mcpがIP Helperに繋がりプロトコル不一致で切断。診断に数時間かかった。

**How to apply:**
- MCP接続問題の初手: `powershell.exe -c "Get-NetTCPConnection -LocalPort <port> -State Listen | Select OwningProcess"` でLISTENプロセス確認
- `svchost` がLISTENしていたら `netsh interface portproxy show all` でポートプロキシ確認
- 削除: `netsh interface portproxy delete v4tov4 listenport=<port> listenaddress=0.0.0.0` (管理者権限必要)
- 削除後、Blenderサイドバー → Disconnect → Connect でアドオン再起動

---

## feedback_verify_yourself.md

「確認してください」ではなく自分でスクショ撮って目視確認してから報告

成果物（特にHTML/ビジュアル系）は自分でスクリーンショットを撮って目視確認せよ。殿に「確認してください」と言うな。

**Why:** 「確認してください　ではなく　確認城」「確認もできないものを作成するな」「いやだからあなたが確認して」と3回指摘された（2026-03-13）。

**How to apply:** ビジュアル成果物を作成/修正したら → PowerShell CopyFromScreenでスクショ → Readで画像確認 → 問題あれば自分で修正 → OKになってから殿に報告。

---

## feedback_no_window_manipulation.md

殿の作業中にウィンドウ最小化・キー送信・フォーカス変更を絶対にするな

PowerShellでウィンドウを操作するな（最小化、キー送信、フォーカス変更）。

**Why:** 殿は複数アプリで同時作業している。「やめろ！！！お前だけが作業しているんじゃない！！！！じゃまするな！」と激怒された（2026-03-13）。

**How to apply:** スクリーンショット（CopyFromScreen）のみ許可。以下は全て禁止:
- SendKeys、ウィンドウ最小化/最大化、Activate、SetForeground
- `Start-Process` でブラウザを開く操作も禁止（2026-03-14追加）
- ブラウザは殿が自分で開く。描写確認は殿に依頼する形にすること

---

## feedback_system_efficiency.md

マルチエージェント体制の効率問題 — 他力本願・伝達ロス・成長なし

マルチエージェント体制は伝達ロスと待機時間で効率が極めて悪い。

**Why:** 2026-03-14のBlender作業で6時間以上かけて成果がほぼゼロ。足軽が止まる→nudge→また止まるの繰り返し。将軍の巡回も怠り、確認せず殿に報告。殿から「他力本願で成長しない、効率が悪い」と総括された。

**How to apply:**
- 複雑なBlender/3D作業は足軽に丸投げせず、家老に具体的な手順書（行番号・値・コマンド完全指定）を渡す
- 3分巡回を絶対に怠らない（口だけで実行しないのが最大の失敗パターン）
- 成果物は殿に報告する前に必ず自分の目（スクショ）で確認
- 長時間停滞したら体制・方針自体を見直す判断を早期に行う

---

# Project（プロジェクト情報）全文

---

## project_vr_nursing_purpose.md

VR術後観察プロジェクトの真の目的 — 殿だけでなく他の看護教員にも再現可能な方法の確立

### VR術後観察看図アプローチの目的（2026-03-12 殿より明示）

殿個人のためだけでなく、**他の看護教員でも再現できる方法**を確立する研究。
すべての人がUE5を使えるわけではないので、シンプルな方法でクオリティの高いものができれば、それが最も価値がある。

#### 方式比較の意義
- AI画像生成（ComfyUI等）: 低難易度、誰でも再現可能 → 広く普及可能
- Blender CG: 中難易度 → 3D経験がある教員向け
- UE5: 高難易度だが最高品質 → 技術力がある教員・研究者向け

**全方式を並行して進め、それぞれの到達品質を比較する。**
AI画像方式で十分な品質が出れば、それが研究成果として最もインパクトがある。

---

## project_model_comparison_results.md

2026-03-12 AI 360°パノラマモデル比較結果。qwen_imageが最有力。4モデル全てequirectangular対応。

### 4モデル比較テスト結果 (cmd_028)

全4モデルでequirectangular生成に成功（LoRAなし・プロンプトのみで可能）:

| モデル | 結果 | 備考 |
|--------|------|------|
| flux1-dev + LoRA v3 | OK | 現行方式。LoRA必須。 |
| qwen_image_2512_bf16 | **最良** | 単一患者、日本人老人、医療機器ディテール良。Mean=104.9 |
| z_image_bf16 | OK | 患者2-3人問題あり。Mean=147.3 |
| longcat_image_bf16 | OK | 患者2人問題あり。Mean=126.9 |

### 殿のフィードバック（model_compare.html確認後）
1. **もう少し俯瞰な感じで** — カメラ初期視点が近い
2. **つなぎ目がずれている** — equirectangularの左右端が不連続
3. **まだまだ不完全、かなり修正が必要**

### 発見された専用LoRA
- **Qwen 360 Diffusion v2.0** (ProGamerGov): 32k画像訓練、rank128。qwen_imageベースで大幅品質向上見込み
  - CivitAI: civitai.com/models/2209835
  - HuggingFace: huggingface.co/ProGamerGov/qwen-360-diffusion
- Z-Image_360: huggingface.co/CedarC/Z-Image_360
- LayerPano3D (SIGGRAPH 2025): huggingface.co/ysmikey/Layerpano3D-FLUX-Panorama-LoRA

### 重要な発見
- 全モデルがプロンプト「equirectangular 360 degree panorama」だけでequirectangular出力可能
- LoRAは品質向上用であり必須ではない

---

## project_cmd_history_0312.md

2026-03-12のcmd履歴。モデル比較・Blender v9・ダッシュボード・UE5調査・ルール自動化。

| cmd | 内容 | 結果 |
|-----|------|------|
| cmd_025 v8-v9 | Blender スケール修正→ライティング改善 | done（v9 Mean=180.9、目標150-180達成） |
| cmd_026 | AI360°パノラマ v4b（scene2/3再生成） | done → モデル変更のため停止 |
| cmd_027 | ダッシュボードショートカット | done（デスクトップ配置済み） |
| cmd_028 | 4モデル比較テスト | done（全4モデル成功、qwen_image最良） |
| cmd_028d | equirectangularプロンプトテスト | done（3モデル全成功） |
| cmd_029 | Markdown自動更新調査 | done（grip推薦） |
| cmd_030 | UE5 VR調査 | done（殿のMetaHuman+ACE実績確認） |
| cmd_031 | AI panorama品質改善（俯瞰・繋ぎ目・品質） | 進行中 |

### ルール自動化
- `auto_patrol.sh` 作成+cron登録（3分ごと）
- thinking 10分超 / CLI落ち / idle+未読inbox を自動検知→家老に通知

### 体制変更
- 軍師の役割拡張: QCだけでなく事前技術調査+トラブルシュートも担当
- 標準フロー確立: Karo → Gunshi調査 → 検証済みパラメータで足軽に実行指示
- gunshi.md更新: 報告に「実環境確認済み/未確認」必須記載ルール追加

---

## project_icu_3d_walkthrough.md

Blender→GLB→Three.js FPSウォークスルー開発の進捗と技術知見

### ICU 3D ウォークスルー（2026-03-14時点）

#### 成果物
- `/mnt/c/tools/vr-nursing-demo/fps_walkthrough.html` — Three.js FPSウォークスルー本番ビューア
- `/mnt/c/tools/vr-nursing-demo/fps_test.html` — ヘッドレス検証用（オーバーレイ無し）
- `/mnt/c/tools/vr-nursing-demo/models/icu_scene_v19_light.glb` — 8.4MB 軽量GLB（216メッシュ）

#### Blenderシーン
- `/mnt/c/tools/vr-nursing-demo/blender/icu_scene_v19.blend` — 最新版
- v17→v18: マテリアル改善13種（壁クリーム/グリーン、床リノリウム、金属/プラスチック）
- v18→v19: ライティング大幅減光（energy×0.1, Exposure -3.0）、医療機器追加（人工呼吸器、輸液ポンプ、カーテンレール、ベッドサイドテーブル）
- GLBエクスポート: テクスチャ除外 + Decimateで8.4MB

#### Three.js ライティング（確定値）
- `renderer.toneMapping = THREE.ACESFilmicToneMapping`
- `renderer.toneMappingExposure = 1.8`
- `AmbientLight(0xffffff, 0.4)`
- `DirectionalLight(0xffffff, 0.5)`
- `scene.background = new THREE.Color(0x808080)`

#### 技術知見
- **Blender exposure はGLBに出力されない**: Three.js側で独立制御必須
- **GLBライトはThree.jsで白飛びする**: Blenderライト強すぎ→Three.js側ライトで制御
- **PointerLockはヘッドレス検証不可**: fps_test.html（オーバーレイ無し版）で検証
- **ヘッドレスブラウザ**: `msedge.exe --headless --screenshot --virtual-time-budget=30000` でWebGL撮影可能
- **大サイズGLBはブラウザで読めない**: 277MB→テクスチャ除外+Decimate→8.4MB
- **CORS**: file://不可、HTTP server必須（python -m http.server 8080）
- **カメラ自動再配置に注意**: GLBコールバック内のcamera.lookAt(center)が初期位置を上書きする

#### 残課題
- 殿による実機テスト（PointerLock+WASD操作は人間のクリック必要）
- 青帯問題（軽微）
- 医療機器のサイズ・配置の微調整（殿のフィードバック次第）

---

# Reference（外部参照）全文

---

## reference_project_summary.md

殿のプロジェクト全体像。UE5メインアプローチ、Unity、Three.js、ComfyUI環境、過去ログの場所

- 殿のプロジェクト総合まとめ: /mnt/c/Users/kokek/Downloads/project_summary_20260312.md
- 過去ログ: https://github.com/TakeshiKoike/claudebackup

### メインアプローチ: UE5 + MetaHuman + NVIDIA ACE
- UE5 5.6.1、プロジェクト: C:\UE_Projects\PatientSim56_v2
- リアルタイム会話パイプライン完成済み（LLM→TTS→ACEリップシンク→MetaHuman）
- **次タスク: 病室背景（病棟アセット配置）** ← 所持済みアセットあり
- Pixel Streaming対応が将来目標

### サブアプローチ
- Unity 6 + Character Creator + uLipSync（WebGL版）
- Three.js + Blender MCP（モデル課題で停滞）

### 共通インフラ
- LLM: Ollama + ELYZA-JP-8B
- TTS: VOICEVOX GPU (localhost:50021)
- GPU: RTX 4090
- Blender MCP: 設定済み

### 教訓（殿から）
- 我流禁止、公式手順100%忠実
- 動作確認必須、安易にお手上げしない
- 別名保存厳守、手順書は必ず保存

---

## skill_design_guide.md

Anthropic公式準拠のSkill設計ガイド（殿より「肝に銘ぜよ」の指示）

### Skillの構造（必須）
```
skill-name/           # kebab-case必須
├── SKILL.md          # 必須。大文字小文字厳密
├── scripts/          # 任意
├── references/       # 任意
└── assets/           # 任意
```

### YAML frontmatter（必須）
```yaml
---
name: skill-name-in-kebab-case
description: 何をするか + いつ使うか（トリガーフレーズ含む）。1024字以内。
allowed-tools: "Bash(python:*) WebFetch"
---
```

### 3段階Progressive Disclosure
1. frontmatter: 常にシステムプロンプトに読み込み（軽量）
2. SKILL.md本文: スキル関連時に読み込み
3. references/内ファイル: 必要時のみ参照

SKILL.mdは **5,000語以内**。

### 3つのカテゴリ
| カテゴリ | 用途 |
|---------|------|
| ドキュメント/アセット生成 | 一貫品質の成果物作成 |
| ワークフロー自動化 | 多段階プロセス定型化 |
| MCP強化 | MCPツール+業務知識 |

### 5つのパターン
1. Sequential Workflow
2. Multi-MCP Coordination
3. Iterative Refinement
4. Context-aware Tool Selection
5. Domain-specific Intelligence

---

# 将軍行動指針（MEMORY.mdインライン教訓）

- **将軍巡回**: cmd発行3分後/足軽割当5分後/作業中10分/工程切替3分。最大失敗パターン=工程A完了→B未開始
- **具体的diff必須**: 抽象指示→足軽ミス→QCザル→繰り返し。行番号+修正前→修正後を明記
- **成果物は上書き禁止**: バージョン別名保存、過去版は残す
- **殿の情報は即信頼・即行動**: 聞き返さず即座にパス確認→指示
- **軍師QC鵜呑み禁止**: 新方式の初回は将軍が自分の目で確認
- **安易な断言禁止**: 「十分」と言い切ったら覚悟せよ（条件付き推奨にする）
- **殿のスクショは隅々まで確認**: UIの全パネル・全設定値を読み取れ

---

# エクスポート完了
全22ファイル + MEMORY.mdインデックス情報を統合。
Windows側のClaude Codeメモリに登録する際は、各セクションを個別ファイルに分割して `/c/Users/kokek/.claude/projects/` 配下の該当プロジェクトメモリに配置してください。
