# Claude Code Insights 統合手順

## 目的
4台のPCのClaude Code利用データを統合し、総合インサイトレポートを作成する。

## 対象PC

| # | PC | 用途 |
|---|-----|------|
| 1 | RTX 4090 (Windows) | UE5, SadTalker, GPU系処理 |
| 2 | ThinkPad (Windows) | 持ち運び用 |
| 3 | MacBook Air | 軽作業 |
| 4 | MacBook Pro (M4 Pro) | メイン開発機 ← 統合先 |

## 各PCでの作業手順

### ステップ1: /insights を実行（まだの場合）

```bash
claude
```
Claude Code起動後:
```
/insights
```
これでセッション分析データ（facetsフォルダ）が生成される。

### ステップ2: データ収集スクリプトを実行

#### 方法A: GitHubから直接実行
```bash
curl -sL https://raw.githubusercontent.com/TakeshiKoike/claudebackup/main/collect-insights.sh | bash
```

#### 方法B: 手動実行
このリポジトリの `collect-insights.sh` をダウンロードして:
```bash
bash collect-insights.sh
```

#### Windows (PowerShell) の場合
Git Bashまたは WSL で実行してください:
```bash
# Git Bash or WSL
bash collect-insights.sh
```

### ステップ3: 生成ファイルの確認

ホームディレクトリに以下が作成される:
```
~/insights-<ホスト名>-<日付>.tar.gz
```
サイズは通常 20KB〜100KB 程度。

### ステップ4: MacBook Pro に転送

以下のいずれかの方法で転送:
- AirDrop（Mac間）
- USBメモリ
- Google Drive / OneDrive
- `scp` コマンド

### ステップ5: MacBook Pro で展開

```bash
# RTX 4090 の場合
tar xzf insights-<ホスト名>-<日付>.tar.gz -C ~/claude-insights-merged/1-RTX4090/

# ThinkPad の場合
tar xzf insights-<ホスト名>-<日付>.tar.gz -C ~/claude-insights-merged/2-ThinkPad/

# MacBook Air の場合
tar xzf insights-<ホスト名>-<日付>.tar.gz -C ~/claude-insights-merged/3-MacBookAir/
```

### ステップ6: 統合レポート生成

MacBook Pro の Claude Code で:
```
統合して
```

## 収集されるデータの内容

| ファイル | 内容 | プライバシー |
|---------|------|------------|
| `facets/*.json` | セッション分析（目標、満足度、摩擦タイプ等） | 会話内容は含まない |
| `sessions/*_sessions-index.json` | セッション一覧（日時、メッセージ数、要約1行） | 要約のみ |
| `pc-info.json` | PC名、OS、アーキテクチャ | 基本情報のみ |
| `report-*.html` | 個別PCのHTMLレポート（参照用） | 分析結果 |

※ 生のチャットログ（.jsonlファイル）は**含まれない**ので安全。

## 統合先フォルダ構造（MacBook Pro上）

```
~/claude-insights-merged/
├── 1-RTX4090/
│   ├── facets/*.json
│   ├── sessions/*_sessions-index.json
│   ├── pc-info.json
│   └── report-*.html
├── 2-ThinkPad/
│   ├── ...
├── 3-MacBookAir/
│   ├── ...
└── 4-MacBookPro/        ← 済み
    ├── facets/*.json (36件)
    ├── sessions/
    ├── pc-info.json
    └── report-*.html
```

## 現在の進捗

- [x] MacBook Pro（36セッション）
- [ ] RTX 4090
- [ ] ThinkPad
- [ ] MacBook Air
