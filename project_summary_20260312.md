# デジタル模擬患者プロジェクト 総合まとめ
**作成日: 2026年3月12日**

---

## 1. プロジェクト概要

| 項目 | 内容 |
|------|------|
| **目標** | 看護教育用リップシンク付きデジタル模擬患者の製作 |
| **担当** | Takeshi Koike（聖隷クリストファー大学・看護教育関連） |
| **環境** | Windows 11 Pro / NVIDIA RTX 4090 / DESKTOP-U1U0FB6 |
| **期間** | 2025年10月〜現在（2026年3月） |
| **Claude Code利用** | 2025/10/1〜 延べ611時間・15,439メッセージ（4PC合計、2/12時点） |

---

## 2. 3つのアプローチと到達点

### アプローチ1: UE5 + MetaHuman + NVIDIA ACE（1番さん）★メイン

| 項目 | 状態 |
|------|------|
| **到達点** | **リアルタイム会話パイプライン完成** |
| **エンジン** | Unreal Engine 5.6.1 |
| **プロジェクト** | `C:\UE_Projects\PatientSim56_v2` |
| **キャラクター** | MetaHuman BP_Keiji（高齢男性）、BP_takeshi77 |
| **リップシンク** | NVIDIA ACE Audio2Face-3D（LocalA2F-Mark） |
| **LLM** | Ollama + ELYZA-JP-8B（2.6〜4.5秒応答） |
| **TTS** | VOICEVOX GPU（0.1〜0.2秒） |
| **UI** | UE5内チャットUI（WBP_PatientChat） |
| **合計遅延** | **約3〜5秒**（入力→患者発話開始） |

**完成した機能:**
- テキスト入力 → LLM応答 → VOICEVOX音声生成 → ACEリップシンク → MetaHuman発話
- UE5内チャットUI（テキスト入力、Enter送信、送信ボタン）
- 看護師音声（VOICEVOX）でLLM待ち時間をマスク
- 映画風字幕表示（看護師・患者両方）
- MetaHumanテンプレート化（PatientTemplate.json v2.0、患者切り替え対応）
- Blueprint Async API（PendingWavPath方式）で連続リップシンク対応

**最適化の経緯:**
| 指標 | 初期（1/31） | 最適化後（2/1） | 改善率 |
|------|-------------|----------------|--------|
| LLM応答 | 8.05秒 | 2.40秒 | 70%↓ |
| リップシンク | 5.64秒 | 0.97秒 | 83%↓ |
| **合計** | **約14秒** | **約3.8秒** | **73%↓** |

**主要スクリプト:**
| ファイル | 説明 |
|---------|------|
| `patient_ue5_monitor.py` | LLM+TTS+リップシンク統合スクリプト（メイン） |
| `patient_gui.py` | AI模擬患者GUIアプリ |
| `patient_conversation.py` | コマンドライン版会話システム |
| `setup_metahuman_patient.py` | MetaHumanセットアップツール |
| `MetaHuman_LipSync_Manual.md` | 完全マニュアル |

---

### アプローチ2: Unity + Character Creator + uLipSync（2番さん）

| 項目 | 状態 |
|------|------|
| **到達点** | WebGL版ブラウザ表示・テキスト入力動作確認 |
| **エンジン** | Unity 6 (6000.0.23f1) |
| **プロジェクト** | `C:\zzz\My project` |
| **キャラクター** | koike2（Character Creator） |
| **リップシンク** | uLipSync（あいうえお5母音BlendShape） |
| **既知の制限** | WebGLで長文リップシンクが途中停止する |

**完成した機能:**
- CC キャラクター インポート + uLipSync設定
- VOICEVOX連携（Speaker ID: 11）
- LLM連携（ELYZA-JP-8B）
- WebGLビルド + HTML入力欄（JavaScript→Unity連携）
- 日本語フォント対応（Noto Sans JP）

---

### アプローチ3: Three.js + Blender + VOICEVOX（3番さん）

| 項目 | 状態 |
|------|------|
| **到達点** | リップシンク基本実装完了、適切な3Dモデル未確保 |
| **技術** | Three.js (r128) + Blender MCP |
| **患者設定** | 田中一男（72歳男性、COPD） |
| **課題** | リアルな服付き男性患者モデルが見つからない |

**試行した3Dモデル:**
1. Blender手作り（simple_face.glb）→ シンプルすぎる
2. Hyper3D Rodin（AI生成）→ リップシンク用トポロジーなし
3. VRoid Studio → アニメスタイルのみ、不適切
4. Ready Player Me → サービス終了
5. Hunyuan3D → Mac依存関係失敗
6. Sketchfab API → シェイプキーが失われる
7. Sketchfab facial model → 149シェイプキー保持成功、ただし看護教育に不適切なモデル

---

## 3. 共通インフラ

| コンポーネント | 詳細 |
|---------------|------|
| **LLM** | Ollama + ELYZA-JP-8B |
| **TTS** | VOICEVOX（localhost:50021、GPUモード利用可） |
| **GPU** | NVIDIA RTX 4090（24GB VRAM） |
| **Nemotron-Nano-9B** | llama.cpp b8119で80+ tok/s（Ollama未対応） |
| **Blender MCP** | 設定済み（`claude mcp add blender uvx blender-mcp`） |

---

## 4. 実験・調査済みツール一覧

### 音声対話（Full-Duplex）

| ツール | 言語 | 環境 | 状態 |
|--------|------|------|------|
| **llm-jp-moshi-v1** | 日本語 | WSL2 Ubuntu-22.04 | 起動確認済み（試作段階、19.7GB VRAM） |
| **PersonaPlex-7B** | 英語 | WSL2 Ubuntu-22.04 | 起動確認済み（約16GB） |

### 画像・動画

| ツール | 用途 | 状態 |
|--------|------|------|
| **flux-stream-editor** | リアルタイム動画スタイル変換 | 動作確認済み（FPS 5.10） |
| **Voicebox (Qwen3-TTS)** | ボイスクローニング | GPU対応起動手順確立 |
| **Osmo Pocket 3** | カメラキャプチャ | OpenCV直接キャプチャ確認済み |

### マルチエージェント

| ツール | 用途 | 状態 |
|--------|------|------|
| **multi-agent-shogun** | tmux+Claude Code複数体制 | WSL2で正常稼働確認（MSYS2は実用不可） |
| カスタマイズ版 | 3人看護教育体制 | コミット済み（GitHub: TakeshiKoike/multi-agent-nursing） |

### 動画制作

| ツール | 用途 | 状態 |
|--------|------|------|
| **WakuFact v2** | AI雑学ショート動画自動制作 | EP01 v5完成、EP02〜50未制作 |
| **PPTX→MP4変換** | プレゼン動画化 | 手順確立済み（PowerPoint COM + ffmpeg） |

---

## 5. NVIDIA ACE 技術詳細

### インストール済みコンポーネント

| コンポーネント | バージョン |
|---------------|-----------|
| ACE Unreal Plugin | NV_ACE_Reference v2.5.0 |
| Audio2Face-3D モデル | LocalA2F-Mark（v3.0 diffusion、4.4+ GiB VRAM） |
| Audio2Face-3D SDK | ビルド済み（147/147ターゲット） |
| TensorRT | 10.14.1 |
| CUDA | 12.8 |

### Blueprint構成（BP_Keiji / BP_takeshi77）

| 変数 | 型 | 用途 |
|------|-----|------|
| PendingMessage | String | UIからのメッセージ受け取り |
| PendingWavPath | String | WAVファイルパス（リップシンクトリガー） |
| IsReady | Boolean | リップシンク可能状態フラグ |
| CurrentSubtitle | String | 字幕テキスト |

### 断念したアプローチ
- JSON→MetaHuman直接モーフ適用（Face_AnimBPが上書き）
- Audio2Faceスタンドアロン（ACEプラグインで十分）
- MuseTalk（バッチ処理、品質不十分）
- OVRLipSync（UE5互換性問題）

---

## 6. 未完了タスク（2026/3/4 最終更新）

| # | タスク | 詳細 | 優先度 |
|---|--------|------|--------|
| 1 | **病室環境構築** | 病棟アセット（所持済み）でUE5病室背景作成 | 高 |
| 2 | **IME入力問題対応** | 変換候補が入力欄を隠す → 入力欄上部移動 or 外部GUI | 高 |
| 3 | **WakuFact v2 EP01最終確認** | Meiryo 100pt v5完成、フィードバック待ち | 中 |
| 4 | **WakuFact v2 EP02〜04制作** | EP01完了後に着手 | 中 |
| 5 | **WakuFact v2 全50EP発音スキャン** | VOICEVOX読み間違い検出 | 低 |

---

## 7. 開発ロードマップ

### Phase 1: スタンドアロン完成 ✅
- [x] LLMリアルタイムリップシンク
- [x] GUIアプリ
- [x] MetaHumanテンプレート化
- [x] UE5内チャットUI
- [x] 看護師音声（待ち時間マスク）
- [x] 字幕表示

### Phase 1.5: 演出強化 ← 現在
- [x] MetaHuman交換テンプレート化
- [x] BP_Keiji ACE設定
- [ ] **病室背景（病棟アセット配置）** ← 次のタスク
- [ ] アイドリングアニメーション（呼吸、まばたき）
- [ ] 2体同時リップシンク（患者+看護師）

### Phase 2: Pixel Streaming対応
- [ ] Pixel Streaming設定
- [ ] Webクライアント作成
- [ ] サーバー構築

### Phase 3: 配布・運用
- [ ] パッケージ化
- [ ] マニュアル作成
- [ ] 複数患者対応

---

## 8. 環境・ツール一覧

### ソフトウェア

| ツール | バージョン/詳細 |
|--------|----------------|
| Unreal Engine | 5.6.1 |
| Unity | 6 (6000.0.23f1) |
| NVIDIA ACE | v2.5.0 |
| Ollama | v0.16.2 |
| VOICEVOX | v0.25.1 |
| Docker Desktop | 29.1.5 |
| llama.cpp | b8119 + CUDA 12.4 |
| MSYS2 + tmux | 3.6a |
| Claude Code | Skills 9個インストール済み |

### 重要ファイルマップ

```
C:\Users\kokek\
├── patient_ue5_monitor.py      ★ メイン統合スクリプト
├── patient_gui.py              ★ GUIアプリ
├── patient_conversation.py       コマンドライン会話
├── patient_config.py             共通設定読み込み
├── setup_metahuman_patient.py    MetaHumanセットアップ
├── MetaHuman_LipSync_Manual.md ★ 完全マニュアル
├── CLAUDE_UE5.md                 UE5作業ログ
├── CLAUDE_Unity.md               Unity作業ログ
├── 3D_LIPSYNC_PROJECT.md         Three.js作業ログ
├── CLAUDE.md                     プロジェクト共通ルール
├── .claude/projects/.../memory/
│   ├── MEMORY.md               ★ メモリインデックス
│   ├── wakufact_v2.md            WakuFact v2手順書
│   ├── pptx_to_video.md          PPTX→MP4手順書
│   ├── tmux_multi_agent.md       マルチエージェント手順書
│   └── critical_lessons.md       教訓集
├── wakufact-v2/                  AI雑学動画パイプライン
├── flux-stream-editor/           リアルタイム動画変換
├── llama-cpp/                    Nemotron-Nano-9B
├── voicebox-src/                 Voicebox GPU版
├── multi-agent-shogun/           マルチエージェント看護教育版
└── camera-mcp/                   カメラMCPサーバー

C:\UE_Projects\
├── PatientSim56/                 ベース保管（変更禁止）
├── PatientSim56_v2/            ★ 現在の作業用プロジェクト
│   ├── Plugins/NV_ACE_Reference/
│   ├── Plugins/NvAudio2FaceMark-UE5.6-.../
│   └── Config/PatientTemplate.json
└── Audio2Face-3D-SDK/            SDK（ビルド済み）

C:\zzz\
├── My project/                   Unity 6プロジェクト
└── (WebGLビルド出力)

WSL2 (Ubuntu-22.04):
├── /home/kokekun5/llm-jp-moshi/  日本語full-duplex音声対話
├── /home/kokekun5/personaplex/   英語full-duplex音声対話
└── /mnt/c/tools/multi-agent-shogun/  マルチエージェント（オリジナル版）
```

---

## 9. 確立した教訓

1. **我流禁止** — 公式ドキュメント・作者の手順を100%忠実に守る
2. **動作確認必須** — 修正後は必ず動作確認してから報告
3. **安易にお手上げしない** — 自分のミスを原因不明と諦めない
4. **独断で方針変更しない** — 困難時もまず原因を徹底調査
5. **ミスは即修正** — 言い訳せず即座に認めて修正→動作確認→報告
6. **別名保存厳守** — 元ファイルを絶対に上書き・削除しない（`_v2`, `_v3`等）
7. **手順書は必ず保存** — 確立した手順はmemory/配下に記録

---

## 10. セッション履歴サマリー

| 日付 | 内容 |
|------|------|
| 2026/3/4 | デジタル模擬患者会話テスト、VOICEVOX音声変更、COPD疾患設定 |
| 2026/3/3 | WakuFact v2 EP01制作（v1→v5、Meiryo 100pt確定） |
| 2026/2/28 | PersonaPlex-7B 起動確認 |
| 2026/2/27 | multi-agent-shogun WSL2起動成功 |
| 2026/2/25 | llm-jp-moshi-v1導入、MSYS2+tmux導入 |
| 2026/2/22 | Claude Code Skills 9個インストール |
| 2026/2/21 | flux-stream-editor, Voicebox, Nemotron-Nano-9B セットアップ |
| 2026/2/17 | Osmo Pocket 3 カメラキャプチャ確認 |
| 2026/2/12 | 4PC統合レポート完成（Claude総合.docx） |
| 2026/2/4-5 | MetaHuman交換テンプレート化、Unity WebGL確認 |
| 2026/2/2 | UE5内チャットUI完成、看護師音声+字幕、GUIアプリ完成 |
| 2026/2/1 | リアルタイム最適化（14秒→3.8秒、73%短縮） |
| 2026/1/31 | 会話パイプライン初回動作確認 |
| 2026/1/29 | ACEリップシンク成功、JSON直接適用失敗→ACE API採用決定 |
| 2026/1/28 | NVIDIA ACE プラグイン導入、VOICEVOX GPU 50倍高速化確認 |
| 2026/1/21 | Three.jsプロジェクト開始 |
| 2025/10/1 | Claude Code利用開始 |
