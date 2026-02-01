# WebGL リアルタイムリップシンク模擬患者システム

## 概要
Three.js + Web Audio API + Blender MCP でブラウザ完結のリップシンク会話システム

## 技術スタック
| 項目 | 技術 |
|------|------|
| 3D表示 | Three.js + GLB |
| モデリング | Blender MCP |
| リップシンク | Web Audio API (音量ベース) |
| TTS | VOICEVOX (localhost:50021) |
| LLM | Ollama + ELYZA-JP-8B |
| バックエンド | Python Flask |

## 起動方法
```bash
cd C:\Users\kokek\webgl-patient
python server.py
```
ブラウザで http://localhost:8888 にアクセス

## 必要なサービス
- VOICEVOX Engine: localhost:50021
- Ollama: localhost:11434
- Blender (MCP用)

## ファイル構成
```
webgl-patient/
├── index.html              # メインページ (Three.js)
├── mblab_lipsync.html      # MB-Lab用リップシンクページ ★推奨
├── server.py               # Flask API サーバー (port 8888)
├── patient.glb             # 3Dモデル (シンプル版)
├── mblab_patient.glb       # MB-Lab患者モデル (83シェイプキー) ★推奨
├── create_patient_model.py # モデル作成スクリプト
└── audio/                  # 生成音声ファイル
```

## 進捗
- [x] プロジェクト構成決定
- [x] Three.js フロントエンド実装
- [x] Flask バックエンド実装 (port 8888)
- [x] LLM + TTS 統合テスト成功
- [x] Blender MCP設定追加
- [x] シンプル顔モデル作成済み (patient.glb, mouth_openシェイプキー付き)
- [x] MB-Lab患者モデル作成 (83シェイプキー、髪・ガウン付き)
- [x] MB-Lab用リップシンクページ実装 (mblab_lipsync.html)
- [x] リップシンク動作確認 OK
- [ ] より リアルな髪モデル作成（オプション）

## 作業ログ
### 2026-01-31
- プロジェクト開始
- Three.js + Flask 基本実装完了
- Chat API動作確認: LLM応答 + VOICEVOX音声生成 OK
- Blender MCP設定を settings.local.json に追加
- **patient.glb 作成完了** (mouth_open シェイプキー付き)

### 2026-02-01
- MB-Labアドオンでリアルな患者モデル作成（83シェイプキー）
- 髪（グレー楕円）とガウン（水色）追加
- mblab_lipsync.html 実装 - AIUEO対応リップシンク
- **リップシンク動作確認 OK**

## リップシンク仕組み
1. ユーザー入力 → Flask → Ollama (LLM応答)
2. LLM応答 → VOICEVOX → WAVファイル生成
3. WAVファイル → ブラウザ → Web Audio API で音量解析
4. 音量 → Three.js morph target → 口の開閉アニメーション

## 次のステップ
1. ~~Meshyモデルを再インポート~~ → MB-Labで解決
2. より自然な髪モデル作成（オプション）
3. 表情バリエーション追加（オプション）

## 学んだこと (2026-01-31)
- 座標を推測してシェイプキーを作るのは危険
- シェイプキーを何度も作り直すとメッシュが壊れる可能性あり
- 正しい手順: 頂点グループを先に作成 → それを基にシェイプキー作成
- VRoid (アニメ調) は選択肢外 → Meshy (リアル調) で進める

## 学んだこと (2026-02-01)
- **MB-Lab**はリップシンク用シェイプキーが最初から83個入っており最適
- MB-Labシェイプキーマッピング:
  - あ: `Expressions_mouthOpenLarge_max`
  - い: `Expressions_mouthSmile_max`
  - う/お: `Expressions_mouthOpenO_max`
  - え: `Expressions_mouthOpenHalf_max`
- 髪やガウンは別オブジェクトとして追加しGLBエクスポートで統合
- Three.jsでマテリアル名/メッシュ名で判定して色分け
