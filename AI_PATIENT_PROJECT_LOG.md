# AI患者プロジェクト - セッション共有ログ

## プロジェクト目標
LLM + リアルタイムリップシンク による看護教育用AI患者の制作

---

## 並行アプローチ

### アプローチA: UE5.6 + NVIDIA ACE（セッション1）
- 担当: Claude Code セッション1
- 状態: NVIDIA ACE導入開始
- ツール: https://developer.nvidia.com/ace-for-games
- 特徴: LLM + TTS + リップシンク（Audio2Face）統合ソリューション
- 要件: UE5.4以上

### アプローチB: Unity + CC5（セッション2）
- 担当: Claude Code セッション2
- 状態: 環境確認中
- 詳細: 下記参照

---

## セッション2（Unity + CC5）ログ

### 2026-01-27 進捗

#### 完了済み
- [x] Unity 6 (6000.0.23f1) プロジェクト作成
- [x] CCiC-Unity-Tools インポート済み
- [x] koike1.Fbx（CC3キャラクター）インポート済み
- [x] Build Materials 完了
- [x] uLipSync インポート済み
- [x] uLipSync / uLipSyncBlendShape コンポーネント追加済み
- [x] Skinned Mesh Renderer を CC_Base_Body に設定
- [x] MCP For Unity v9.0.8 インストール済み・Session Active

#### 次にやること
- [ ] Claude Code 再起動（MCP設定反映のため）
- [ ] Unity MCP 接続確認
- [ ] Phoneme - BlendShape マッピング設定
- [ ] リップシンクテスト
- [ ] LLM (Ollama) + TTS (VOICEVOX) 連携

#### キャラクター情報
- モデル: koike1（自分をモデルに）
- 場所: Assets/Characters/koike1.Fbx
- BlendShapes: CC3形式（Open, Tight-O, Wide, Explosive など）

#### MCP設定
- 設定ファイル: C:\Users\kokek\.claude\settings.local.json
- Unity MCP: mcp-unity（uvx経由）追加済み

---

## 共有リソース
- **LLM**: Ollama + ELYZA-JP-8B
- **TTS**: VOICEVOX（localhost:50021）
- **GPU**: RTX 4090
- **患者画像**: `C:\Users\kokek\Downloads\ComfyUI_00238_.png`

---

## 更新履歴
- 2026-01-27: ログファイル作成、Unity+CC5アプローチ開始
