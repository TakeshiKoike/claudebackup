# kangodx.com 作業メモ

## プロジェクト情報
| 項目 | 値 |
|------|-----|
| サイトURL | https://kangodx.com |
| Firebase URL | https://kango-dx-news.web.app |
| 管理画面 | https://kango-dx-news.web.app/admin/ |
| ソースコード | `/Users/takeshikoike2025/Downloads/プロジェクト/kango-dx-news-full/` |
| Firebase Project | kango-dx-news |
| 技術 | Firebase Hosting + Firestore + Auth (Google) |

## 残作業 (上から順に)

### 1. オリジナル記事の表示修正
**状態**: 未着手（コード確認完了、修正直前）

**問題**: 管理画面でオリジナル記事を投稿すると、Quill.js のリッチテキスト HTML が `description` フィールドに保存される。一覧ページ（カード表示）で `d.description` をそのまま innerHTML に挿入しているため、HTML タグ（`<h2>`, `<strong>`, `<ul>` 等）がカード内にそのまま描画されて表示が崩れる。

**修正方針**: 各カテゴリの一覧ページ (`index.html`) に `stripHtml()` 関数を追加し、カードの excerpt 部分では HTML タグを除去してプレーンテキストで表示する。

**修正対象ファイル** (全5ファイル):
- `public/blog/index.html` 行175
- `public/digital/index.html` 行175
- `public/nursing/index.html` 行175
- `public/deluxe/index.html` 行175
- `public/dx/index.html` 行197

**修正不要（確認済み）**:
- `public/index.html` (トップページ) — description を表示していない
- 全カテゴリの `article.html` (詳細ページ) — `article.url` の条件分岐済み、description は innerHTML として正しく表示される

### 2. ドメイン設定の確認
- kangodx.com のカスタムドメイン設定が Firebase Hosting で正しいか確認

### 3. デプロイ状況の確認
- 最終デプロイ日時、ローカルとの差分を確認
- `firebase deploy` で最新をデプロイ

## 現状のオリジナル記事機能まとめ

### 管理画面 (admin/index.html) — 実装済み
- 「外部記事（URLあり）」と「オリジナル記事」のラジオボタン切替
- オリジナル記事: URL欄非表示、Quill.js リッチテキストエディタ表示
- 保存時: `isOriginal: true`, `url: ''`, Quill HTML を `description` に保存
- 編集モーダル: `isOriginal || !url` でオリジナル判定、Quill エディタ表示

### 記事詳細 (各カテゴリの article.html) — OK
- `article.url` がある場合のみ「元記事を読む」ボタン表示
- `description` を innerHTML に挿入 → Quill HTML がリッチに表示される

### Firestore スキーマ (news コレクション)
```
title, description, url, image, category, comment, views, isHero, isOriginal, addedAt, addedBy, publishedAt, updatedAt
```
※ README.md にはまだ `isOriginal` フィールドが未記載

## ファイル構成
```
public/
├── index.html          # トップページ
├── admin/index.html    # 管理画面（Quill.js エディタ付き）
├── digital/            # デジタル系ニュース
│   ├── index.html      # 一覧 ← 要修正
│   └── article.html    # 詳細 ← OK
├── nursing/            # 看護系ニュース
│   ├── index.html      # ← 要修正
│   └── article.html    # ← OK
├── deluxe/             # デラックスニュース
│   ├── index.html      # ← 要修正
│   └── article.html    # ← OK
├── dx/                 # 看護教育トピックス
│   ├── index.html      # ← 要修正
│   └── article.html    # ← OK
├── blog/               # KOKEKUNブログ
│   ├── index.html      # ← 要修正
│   └── article.html    # ← OK
└── column/             # 旧コラム（3カテゴリ版、現在未使用？）
```
