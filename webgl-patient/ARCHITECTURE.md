# WebGL リアルタイム会話＋リップシンクアバター アーキテクチャ

## 概要

構成をきちんと切り分ければ、全部つなげてリアルタイム会話＋リップシンクWebGLアバターは実現可能です。

## 全体アーキテクチャ

### 1. 3Dモデル生成

- 画像生成AI＋Tripoなどでメッシュを自動生成、またはAIキャラ生成サービスでベースモデル作成
- Blenderでメッシュ調整、ボーン設定、口用BlendShape（A/I/U/E/Oなど）を作成
- Web向けならglTF/glbまたはVRM形式へエクスポート（Blender→glTFのワークフローは多数事例あり）

### 2. Blender → WebGL（Three.jsなど）

- BlenderからglTF/glbで書き出し
- Web側はThree.js＋GLTFLoaderで読み込み、WebGLとしてブラウザに表示
- VRMを使う場合はthree-vrmを使ってVRMモデルとBlendShapeを操作

### 3. Webでのリップシンク処理

仕組みの典型例：

1. 音声の再生時間や波形をWeb Audio APIで取得
2. JSONなどの「時間→口形（Viseme）」テーブルを参照
3. three-vrm経由でVRMのBlendShapeを更新

これでブラウザ上でリアルタイムリップシンクが可能です。

Azure/AWSなどのTTS APIのviseme情報をThree.jsモデルにマッピングする例も公開されています。

### 4. LLM＋TTSで会話を生成

構成例（ブラウザ→サーバ）：

1. ユーザ発話（テキスト or 音声認識結果）をサーバに送る
2. サーバ側でLLMに投げて返答テキストを生成
3. 返答テキストをTTS（ElevenLabs/Azure/OpenAI TTSなど）に渡し、音声＋viseme情報を取得
4. 音声をブラウザにストリーミング再生しつつ、viseme列をWebGL側に渡してBlendShapeを更新

## 参考事例

- **ChatdollKit** - 「3Dモデル＋音声付きチャットボット」を作るWebGL SDK（Unityベース、WebGLデモあり）
- **three-vrm** - VRMモデルをThree.jsで扱うライブラリ
- **VRoid Hub** - 無料VRMモデル多数

## 本プロジェクトの実装

| コンポーネント | 技術 |
|---------------|------|
| 3Dモデル | VRM (VRoid Hub) |
| Web表示 | Three.js + three-vrm |
| リップシンク | Visemeベース (AIUEO) |
| TTS | VOICEVOX (localhost:50021) |
| LLM | Ollama + ELYZA-JP-8B |
| バックエンド | Python Flask |
