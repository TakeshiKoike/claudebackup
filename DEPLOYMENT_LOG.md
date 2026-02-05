# COPD Visual Novel デプロイメントログ

## プロジェクト概要
- **プロジェクト名**: COPD Visual Novel（在宅療養を支える訪問看護）
- **公開URL**: https://copd-visual-novel.web.app
- **Firebase Console**: https://console.firebase.google.com/project/copd-visual-novel/overview

## デプロイ日時
- **初回デプロイ**: 2025年2月5日

## 使用技術
- **ホスティング**: Firebase Hosting
- **コンテンツ**: 静的HTML/CSS/JavaScript
- **メディア**: MP3音声、MP4動画、PNG画像

## コンテンツ構成
- メインビジュアルノベル: `copd_visual_novel_v2.32_video_complete.html`
- 音声ファイル: 92個（audio/）
- 動画ファイル: 81個（videos/）
- 背景画像: 5個（backgrounds/）
- キャラクター表情: 6キャラクター分（characters/）
- BGM: 4曲（bgm/）
- マップ: 3個（maps/）

## 変更履歴

### 2025-02-05: 初回デプロイ
- Firebase Hostingにデプロイ
- プロジェクトID: `copd-visual-novel`

### 2025-02-05: UIボタン位置修正
- **問題**: スマホ閲覧時に「BGM ON」「音声 ON」ボタンが登場人物の顔写真と重なる
- **解決**: ボタンを右下から右上に移動
- **変更箇所**:
  - `#audioControls` の `bottom: 220px` → `top: 70px`
  - メディアクエリ内の `bottom: 190px` → `top: 60px`

## 今後の更新方法
```bash
cd "/Users/takeshikoike2025/Downloads/copd_video_package 2/copd_video_package/copd_video_package"
firebase deploy --only hosting
```

## キャラクター一覧
1. **聖隷一男（Kazuo）** - 主人公（COPD患者、78歳）
2. **一子（Ichiko）** - 家族
3. **医師（Doctor）** - 担当医
4. **薬剤師（Pharmacist）**
5. **佐藤（Sato）**
6. **山田（Yamada）** - 訪問看護師

## シーン構成
- 全12シーン
- 77カット
- 10問のクイズ
