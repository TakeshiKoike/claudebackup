# Claude Code スキル導入ガイド

**作成日**: 2026年2月22日
**環境**: Windows 11 / RTX 4090 PC (DESKTOP-U1U0FB6)
**参考**: https://zenn.dev/imohuke/articles/claude-code-mcp-skills-summary

---

## 概要

Claude Code の **Skills** は、タスク実行手順やベストプラクティスをまとめた拡張モジュール。
`~/.claude/skills/` にインストールすることで、Claude Code が自動的に認識し、関連するタスク時に適用する。

---

## インストール済みスキル一覧（9個）

| # | スキル名 | 分類 | ソース |
|---|---------|------|--------|
| 1 | find-skills | メタ | vercel-labs/skills |
| 2 | skill-creator | メタ | anthropics/skills |
| 3 | ui-ux-pro-max | デザイン | nextlevelbuilder/ui-ux-pro-max-skill |
| 4 | vercel-react-best-practices | フロントエンド | vercel-labs/agent-skills |
| 5 | supabase-postgres-best-practices | バックエンド | supabase/agent-skills |
| 6 | stripe-best-practices | 決済 | anthropics/claude-plugins-official |
| 7 | browser-use | 自動化 | browser-use/browser-use |
| 8 | remote-browser | 自動化 | browser-use/browser-use |
| 9 | remotion-best-practices | 動画 | （既存） |

---

## 各スキル詳細

### 1. find-skills（スキル検索）

| 項目 | 内容 |
|------|------|
| 用途 | 既存スキルの検索・発見・インストール |
| トリガー | 「Xはどうやるの？」「Xのスキルはある？」等 |
| 手動呼び出し | `/find-skills` |

**主要コマンド**:
```bash
npx skills find [query]     # スキルを検索
npx skills add <package>    # スキルをインストール
npx skills check            # 更新確認
npx skills update           # 全スキル更新
npx skills ls               # インストール済み一覧
```

**使用例**:
```bash
npx skills find "react performance"
npx skills add vercel-labs/agent-skills@vercel-react-best-practices -g -y
```

---

### 2. skill-creator（スキル作成ガイド）

| 項目 | 内容 |
|------|------|
| 用途 | 新しいスキルの設計・作成・パッケージング |
| トリガー | 「新しいスキルを作りたい」「スキルを更新したい」 |
| 手動呼び出し | `/skill-creator` |

**スキルのディレクトリ構造**:
```
skill-name/
├── SKILL.md              # 必須: frontmatter + 指示
├── scripts/              # 任意: 実行スクリプト
├── references/           # 任意: 参考ドキュメント
└── assets/               # 任意: テンプレート・画像等
```

**作成の6ステップ**:
1. 具体例でスキルの用途を理解
2. 再利用可能なリソースを計画
3. `scripts/init_skill.py` で初期化
4. SKILL.md とリソースを編集
5. `scripts/package_skill.py` でパッケージング
6. 実使用に基づいて反復改善

---

### 3. ui-ux-pro-max（UI/UXデザイン）

| 項目 | 内容 |
|------|------|
| 用途 | UI/UXデザインシステムの自動生成 |
| トリガー | UIの設計・構築・レビュー・改善時 |
| 手動呼び出し | `/ui-ux-pro-max` |

**収録データ**:
- 50+ UIスタイル（glassmorphism, brutalism, neumorphism 等）
- 97 カラーパレット（業界別）
- 57 フォントペアリング
- 25 チャートタイプ
- 99 UXガイドライン
- 9 技術スタック対応（React, Next.js, Vue, Svelte, SwiftUI, React Native, Flutter, Tailwind, shadcn/ui）

**使用例**:
```bash
# デザインシステム自動生成（最初に必ず実行）
python3 skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness" --design-system -p "Serenity Spa"

# ドメイン別詳細検索
python3 skills/ui-ux-pro-max/scripts/search.py "animation accessibility" --domain ux

# スタック別ベストプラクティス
python3 skills/ui-ux-pro-max/scripts/search.py "layout responsive" --stack html-tailwind
```

**対応ドメイン**: product, style, typography, color, landing, chart, ux, react, web, prompt

---

### 4. vercel-react-best-practices（React/Next.js最適化）

| 項目 | 内容 |
|------|------|
| 用途 | React/Next.js パフォーマンス最適化 |
| トリガー | React コンポーネントの作成・レビュー・リファクタリング時 |
| 自動適用 | React/Next.js コードを扱うときに自動トリガー |

**8カテゴリ57ルール（優先度順）**:

| 優先度 | カテゴリ | 影響度 | ルール例 |
|--------|---------|--------|---------|
| 1 | ウォーターフォール排除 | CRITICAL | Promise.all()、Suspense境界 |
| 2 | バンドルサイズ最適化 | CRITICAL | バレルインポート回避、動的インポート |
| 3 | サーバーサイド性能 | HIGH | React.cache()、LRUキャッシュ |
| 4 | クライアントデータ取得 | MEDIUM-HIGH | SWR、パッシブイベント |
| 5 | 再レンダリング最適化 | MEDIUM | useMemo、derived state |
| 6 | レンダリング性能 | MEDIUM | content-visibility、SVG最適化 |
| 7 | JavaScript性能 | LOW-MEDIUM | Set/Map活用、早期return |
| 8 | 高度なパターン | LOW | useLatest、初期化パターン |

---

### 5. supabase-postgres-best-practices（PostgreSQL最適化）

| 項目 | 内容 |
|------|------|
| 用途 | PostgreSQL クエリ・スキーマ最適化 |
| トリガー | SQL作成、インデックス設計、RLS設定時 |
| 自動適用 | PostgreSQL/Supabase のコードを扱うときに自動トリガー |

**8カテゴリ（優先度順）**:

| 優先度 | カテゴリ | 影響度 |
|--------|---------|--------|
| 1 | クエリパフォーマンス | CRITICAL |
| 2 | コネクション管理 | CRITICAL |
| 3 | セキュリティ & RLS | CRITICAL |
| 4 | スキーマ設計 | HIGH |
| 5 | 並行制御・ロック | MEDIUM-HIGH |
| 6 | データアクセスパターン | MEDIUM |
| 7 | 監視・診断 | LOW-MEDIUM |
| 8 | 高度な機能 | LOW |

---

### 6. stripe-best-practices（Stripe決済）

| 項目 | 内容 |
|------|------|
| 用途 | Stripe API 統合のベストプラクティス |
| トリガー | 決済処理、チェックアウト、サブスクリプション実装時 |
| 自動適用 | Stripe 関連コードを扱うときに自動トリガー |

**主な指針**:
- Checkout Sessions API を最優先で使用
- PaymentIntents / SetupIntents の適切な使い分け
- 非推奨API（Charges API, Sources API, legacy Card Element）の回避
- Billing/Subscription API を活用した SaaS 設計
- Stripe Connect（direct/destination charges）のプラットフォーム設計

---

### 7. browser-use（ブラウザ自動化）

| 項目 | 内容 |
|------|------|
| 用途 | ブラウザ操作の自動化（ローカル環境向け） |
| トリガー | Webサイト操作、フォーム入力、スクリーンショット取得時 |
| 手動呼び出し | `/browser-use` |

**3つのモード**:
- `chromium` — 自動管理されたChromium
- `real` — 既存のChromeプロファイルを使用
- `remote` — クラウドブラウザ

**主な機能**:
- ページナビゲーション・要素クリック・テキスト入力
- スクリーンショット取得
- Cookie管理（get/set/clear/export/import）
- JavaScript実行
- AIエージェントモード（`browser-use run "task"` で自律的タスク実行）
- Cloudflareトンネルでローカルサーバーを公開

---

### 8. remote-browser（リモートブラウザ）

| 項目 | 内容 |
|------|------|
| 用途 | サンドボックス環境でのクラウドブラウザ操作 |
| トリガー | GUI無し環境でのWebブラウザ操作が必要な時 |
| 備考 | browser-use のリモート専用版 |

---

### 9. remotion-best-practices（動画制作）

| 項目 | 内容 |
|------|------|
| 用途 | Remotion（React動画制作）のベストプラクティス |
| トリガー | Remotion コードを扱うとき |
| 自動適用 | Remotion プロジェクトで自動トリガー |

**主な機能**:
- アニメーション・タイミング（interpolation, spring, easing）
- メディア操作（動画/音声の埋め込み・トリミング）
- キャプション・字幕（SRT、TikTokスタイル）
- 3Dコンテンツ（Three.js / React Three Fiber）
- テキストアニメーション、トランジション

---

## ファイル配置

```
C:\Users\kokek\
├── .agents\skills\              # スキル本体（全エージェント共通）
│   ├── find-skills\
│   ├── skill-creator\
│   ├── ui-ux-pro-max\
│   ├── vercel-react-best-practices\
│   ├── supabase-postgres-best-practices\
│   ├── stripe-best-practices\
│   ├── browser-use\
│   ├── remote-browser\
│   └── remotion-best-practices\
│
└── .claude\skills\              # Claude Code 用シンボリックリンク
    ├── find-skills -> .agents/skills/find-skills
    ├── skill-creator -> .agents/skills/skill-creator
    ├── ui-ux-pro-max -> .agents/skills/ui-ux-pro-max
    ├── vercel-react-best-practices -> .agents/skills/vercel-react-best-practices
    ├── supabase-postgres-best-practices -> .agents/skills/supabase-postgres-best-practices
    ├── stripe-best-practices -> .agents/skills/stripe-best-practices
    ├── browser-use -> .agents/skills/browser-use
    ├── remote-browser -> .agents/skills/remote-browser
    └── remotion-best-practices -> .agents/skills/remotion-best-practices
```

---

## 管理コマンド

```bash
# 一覧表示
npx skills ls

# スキル検索
npx skills find [キーワード]

# スキル追加（グローバル、確認スキップ）
npx skills add <owner/repo> -g -y

# 特定スキルのみ追加
npx skills add <owner/repo> -g -s <skill-name> -y

# 更新確認
npx skills check

# 全スキル更新
npx skills update

# スキル削除
npx skills remove <skill-name>

# 新規スキル初期化
npx skills init <skill-name>
```

---

## インストール履歴

| スキル | インストールコマンド |
|--------|---------------------|
| find-skills | `npx skills add vercel-labs/skills -g -s find-skills -y` |
| skill-creator | `npx skills add anthropics/skills -g -s skill-creator -y` |
| ui-ux-pro-max | `npx skills add nextlevelbuilder/ui-ux-pro-max-skill -g -y` |
| vercel-react-best-practices | `npx skills add vercel-labs/agent-skills -g -s vercel-react-best-practices -y` |
| supabase-postgres-best-practices | `npx skills add supabase/agent-skills -g -s supabase-postgres-best-practices -y` |
| stripe-best-practices | `npx skills add anthropics/claude-plugins-official -g -s stripe-best-practices -y --full-depth` |
| browser-use + remote-browser | `npx skills add browser-use/browser-use -g -y --full-depth` |

---

## 注意事項

- スキルは **次回のClaude Codeセッションから自動認識** される（現セッションでは再起動が必要）
- スキルはClaude Code以外にも **Cursor, Codex, Gemini CLI, Kiro CLI, Windsurf** 等のエージェントにも同時インストールされている
- スキルの更新は `npx skills update` で一括実行可能
- カスタムスキルを作りたい場合は `/skill-creator` を使用
- スキル検索は `/find-skills` または https://skills.sh/ から
