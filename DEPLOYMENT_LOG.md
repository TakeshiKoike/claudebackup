# COPD Visual Novel デプロイメントログ

**作成日**: 2026年2月5日
**最終更新**: 2026年2月5日

---

## プロジェクト概要

| 項目 | 内容 |
|------|------|
| プロジェクト名 | COPD Visual Novel（在宅療養を支える訪問看護） |
| 公開URL | https://copd-visual-novel.web.app |
| GitHubバックアップ | https://github.com/TakeshiKoike/claudebackup/tree/copd-visual-novel |
| Firebase Console | https://console.firebase.google.com/project/copd-visual-novel/overview |

---

## 変更履歴

### 2026-02-05 初回デプロイ & UI修正

#### 実施内容
1. **Firebase Hosting 新規プロジェクト作成**
   - プロジェクトID: `copd-visual-novel`
   - 260ファイルをデプロイ

2. **UIボタン位置修正**
   - **問題**: スマホ閲覧時に「BGM ON」「音声 ON」ボタンが登場人物の顔写真と重なる
   - **解決**: ボタンを右下から右上に移動
   - **変更ファイル**: `copd_visual_novel_v2.32_video_complete.html`
   - **変更箇所**:
     ```css
     /* 変更前 */
     #audioControls { bottom: 220px; }

     /* 変更後 */
     #audioControls { top: 70px; }
     ```
     ```css
     /* メディアクエリ内 変更前 */
     #audioControls { bottom: 190px; }

     /* メディアクエリ内 変更後 */
     #audioControls { top: 60px; }
     ```

3. **GitHubバックアップ**
   - リポジトリ: `TakeshiKoike/claudebackup`
   - ブランチ: `copd-visual-novel`
   - コミット: 275ファイル

---

## 使用技術

- **ホスティング**: Firebase Hosting
- **コンテンツ**: 静的HTML/CSS/JavaScript
- **メディア**: MP3音声、MP4動画、PNG画像
- **3Dモデル**: GLB形式

---

## コンテンツ構成

| カテゴリ | ファイル数 | 場所 |
|----------|------------|------|
| メインHTML | 5 | ルート |
| 音声ファイル | 92 | audio/ |
| 動画ファイル | 81 | videos/ |
| 背景画像 | 5 | backgrounds/ |
| キャラクター表情 | 54 | characters/ |
| BGM | 4 | bgm/ |
| マップ | 3 | maps/ |
| 3Dモデル | 1 | model.glb |

---

## キャラクター一覧

| キャラクター | 役割 | 表情数 |
|--------------|------|--------|
| 聖隷一男（Kazuo） | 主人公（COPD患者、78歳） | 18 |
| 一子（Ichiko） | 家族 | 9 |
| 医師（Doctor） | 担当医 | 9 |
| 薬剤師（Pharmacist） | 薬局 | 9 |
| 佐藤（Sato） | - | 9 |
| 山田（Yamada） | 訪問看護師 | 9 |

---

## シーン構成

- 全12シーン
- 77カット
- 10問のクイズ

---

## 今後の更新方法

### Webサイト更新
```bash
cd "/Users/takeshikoike2025/Downloads/copd_video_package 2/copd_video_package/copd_video_package"
firebase deploy --only hosting
```

### GitHubバックアップ更新
```bash
cd "/Users/takeshikoike2025/Downloads/copd_video_package 2/copd_video_package/copd_video_package"
git add .
git commit -m "変更内容を記載"
git push origin copd-visual-novel
```

---

## 担当

- **デプロイ作業**: Claude Opus 4.5
- **依頼者**: Takeshi Koike
