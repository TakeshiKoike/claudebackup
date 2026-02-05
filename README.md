# カンゴ☆デラックス

「看護×DX×教育」の交差点。VR・MR・生成AI・シミュレーション教育など、最先端のデジタル技術を活用した看護教育の未来を創造するメディアサイト。

## サイトURL

- **公開サイト:** https://kango-dx-news.web.app
- **管理画面:** https://kango-dx-news.web.app/admin/

## カテゴリ構成（5カテゴリー）

| カテゴリー | パス | 説明 | カラー |
|-----------|------|------|--------|
| 💻 デジタル系のニュース | `/digital/` | AI・VR・DXなど、デジタル技術に関する最新ニュース | 青 #1565C0 |
| 🏥 看護系のニュース | `/nursing/` | 看護に関する最新ニュース | ピンク #E91E63 |
| ⭐ デラックスニュース | `/deluxe/` | KOKEKUNが気になったニュース | オレンジ #FF9800 |
| 🎓 看護教育トピックス | `/dx/` | 看護教育に関するトピックス | 緑 #2E7D32 |
| ✍️ KOKEKUNブログ | `/blog/` | KOKEKUNのブログ。日々の思いや気づき | 紫 #9C27B0 |

## ページ構成

```
public/
├── index.html          # トップページ
├── admin/
│   └── index.html      # 管理画面（記事投稿・編集）
├── digital/
│   ├── index.html      # デジタル系ニュース一覧
│   └── article.html    # 記事詳細
├── nursing/
│   ├── index.html      # 看護系ニュース一覧
│   └── article.html    # 記事詳細
├── deluxe/
│   ├── index.html      # デラックスニュース一覧
│   └── article.html    # 記事詳細
├── dx/
│   ├── index.html      # 看護教育トピックス一覧
│   └── article.html    # 記事詳細
├── blog/
│   ├── index.html      # KOKEKUNブログ一覧
│   └── article.html    # 記事詳細
└── images/
    ├── hero-dx.png     # ヒーロースライダー画像
    ├── hero-ai.png
    └── hero-vr.png
```

## 技術スタック

- **ホスティング:** Firebase Hosting
- **データベース:** Firebase Firestore
- **フロントエンド:** HTML/CSS/JavaScript (Vanilla)
- **認証:** Firebase Authentication (Google)
- **アナリティクス:** Google Analytics (G-E8K9FG83WD)

## 機能

### トップページ
- ヒーロースライダー（DX, AI, VR テーマ、自動スライド）
- 最新記事一覧（全カテゴリーから10件）
- カテゴリーカード（5カテゴリー）
- サイドバー（サイト説明、お問い合わせ、SNSリンク）

### カテゴリーページ
- 記事一覧（カテゴリー別フィルタリング）
- サイドバー（カテゴリーナビ、人気記事）
- 記事詳細ページ（閲覧数カウント機能付き）

### 管理画面
- Google認証によるログイン
- OGP自動取得機能
- 記事の投稿・編集・削除
- カテゴリー別フィルタリング
- ヒーロー表示フラグ設定

## Firestore データ構造

```javascript
// news コレクション
{
  title: "記事タイトル",
  description: "記事の説明",
  url: "元記事URL",
  image: "画像URL",
  category: "digital|nursing|deluxe|education|blog",
  comment: "KOKEKUNのひとこと",
  views: 0,
  isHero: false,
  addedAt: Timestamp,
  addedBy: "user@email.com"
}
```

## デプロイ

```bash
firebase deploy
```

## 更新履歴

### 2025-02-05
- サイト構成を3カテゴリーから5カテゴリーに変更
- 看護系ニュース（nursing）を新規追加
- KOKEKUNブログ（blog）を新規追加
- トップページのヘッダーからお問い合わせをサイドバーに移動
- 管理画面のカテゴリー選択を5つに更新
- Firestoreインデックスを設定

---

© 2025 カンゴ☆デラックス All Rights Reserved.
