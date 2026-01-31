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
├── server.py               # Flask API サーバー (port 8888)
├── patient.glb             # 3Dモデル
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
- [ ] リップシンク動作確認
- [ ] より リアルな顔モデル作成（オプション）

## 作業ログ
### 2026-01-31
- プロジェクト開始
- Three.js + Flask 基本実装完了
- Chat API動作確認: LLM応答 + VOICEVOX音声生成 OK
- Blender MCP設定を settings.local.json に追加
- **patient.glb 作成完了** (mouth_open シェイプキー付き)
- 次: ブラウザでリップシンク動作確認

## リップシンク仕組み
1. ユーザー入力 → Flask → Ollama (LLM応答)
2. LLM応答 → VOICEVOX → WAVファイル生成
3. WAVファイル → ブラウザ → Web Audio API で音量解析
4. 音量 → Three.js morph target → 口の開閉アニメーション

## 次のステップ
1. サーバー起動: `python server.py` (webgl-patient フォルダ)
2. ブラウザで http://localhost:8888 にアクセス
3. チャットでリップシンク動作確認
4. (オプション) よりリアルなモデルに改善
