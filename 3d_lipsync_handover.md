# 3Dリップシンク患者シミュレーション - 引き継ぎ資料

**作成日**: 2026年1月24日
**目的**: 看護教育用デジタル患者シミュレーション（3Dアバター版）

---

## 1. プロジェクト概要

### 最終目標
- 3Dアバター患者がLLMで応答を生成し、音声合成でリップシンクしながら話す
- Webブラウザで動作

### 技術スタック（予定）
```
Qwen2.5 14B (LLM) → VOICEVOX (音声合成) → VRMモデル (3Dアバター) → three-vrm (Webリップシンク)
```

---

## 2. 完了済みの作業

### 2D版（バックアップ済み・動作確認OK）

| ファイル | 場所 | 内容 |
|---------|------|------|
| `llm_lipsync_demo.html` | `/Users/takeshikoike2025/Downloads/lipsync_2d_backup/` | Qwen + VOICEVOX + 2Dリップシンク |
| `voicevox_lipsync_demo.html` | 同上 | VOICEVOX + 2Dリップシンク |
| `realtime_lipsync_demo.html` | 同上 | 基本リップシンクデモ |

**動作確認方法**:
```bash
cd "/Users/takeshikoike2025/Downloads/copd_video_package 2/copd_video_package/copd_video_package"
python3 -m http.server 8080
# ブラウザで http://localhost:8080/llm_lipsync_demo.html
```

**必要なサービス**:
- Ollama (qwen2.5:14b) - ポート11434
- VOICEVOX - ポート50021

---

### 3D版の進捗

#### ステップ1: ComfyUI + Tripoでメッシュ生成 ✅ 完了

生成済みモデル:
```
/Users/takeshikoike2025/comfyUI/output/tripo_model_e182db97-4832-4d94-9bde-4f276e6745d6.glb (27MB)
```

プロジェクトフォルダにもコピー済み:
```
/Users/takeshikoike2025/Downloads/copd_video_package 2/copd_video_package/copd_video_package/model.glb
```

#### ステップ2: Blenderで調整 🔄 進行中

**Blenderインストール済み**: バージョン 5.0.1
```
/Applications/Blender.app
```

**Blender MCPインストール済み**:
- アドオンファイル: `/tmp/blender-mcp/addon.py`
- Claude Code MCP設定: `~/.mcp.json`

```json
{
  "mcpServers": {
    "blender": {
      "type": "stdio",
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

**注意**: Blender MCPを使うには、Claude Codeの再起動が必要

#### ステップ3: VRM化と口パク接続 ⏳ 未着手

---

## 3. 次のステップ（3D版）

### 3.1 Blenderでの作業

1. **glbをインポート**
   - File → Import → glTF 2.0
   - `/Users/takeshikoike2025/comfyUI/output/tripo_model_e182db97-4832-4d94-9bde-4f276e6745d6.glb`

2. **メッシュのクリーンアップ**
   - 不要なジオメトリ削除
   - Decimateで軽量化（必要に応じて）

3. **Shape Key（ブレンドシェイプ）追加**
   - 口の形を5〜6パターン作成:
     - `mouth_a` (あ)
     - `mouth_i` (い)
     - `mouth_u` (う)
     - `mouth_e` (え)
     - `mouth_o` (お)
     - `mouth_closed` (閉)

4. **リギング（オプション）**
   - Mixamo または Rigify でスケルトン追加

### 3.2 VRM化

1. **VRM Exporter導入**
   - UniVRM for Blender をインストール

2. **BlendShapeGroupに割り当て**
   - 口のShape KeyをVRMの標準Visemeにマッピング

3. **VRMとしてエクスポート**

### 3.3 Webでリップシンク

1. **three-vrm でVRMを読み込み**
2. **音声解析でViseme制御**
3. **既存の2D版デモをベースに3D版を作成**

---

## 4. ファイル一覧

```
/Users/takeshikoike2025/Downloads/
├── lipsync_2d_backup/              # 2D版バックアップ
│   ├── llm_lipsync_demo.html
│   ├── voicevox_lipsync_demo.html
│   └── realtime_lipsync_demo.html
├── 3d_lipsync_handover.md          # この資料
└── copd_video_package 2/.../
    ├── model.glb                   # Tripoで生成した3Dモデル
    ├── 3d_lipsync_demo.html        # 3Dビューア（モーフなしで動作制限あり）
    ├── characters/                 # 2D用キャラクター画像
    ├── audio/                      # VOICEVOX音声
    └── backup_2d/                  # バックアップコピー

/Users/takeshikoike2025/comfyUI/output/
└── tripo_model_e182db97-4832-4d94-9bde-4f276e6745d6.glb  # 元の3Dモデル

/tmp/blender-mcp/
└── addon.py                        # Blender MCPアドオン
```

---

## 5. 技術メモ

### ブレンドシェイプ（モーフターゲット）とは
3Dモデルの「表情の変形パターン」を事前に登録しておく仕組み。
- 基本の顔（口閉じ）に対して
- 「あ」の口形を100%適用すると口が開く
- 0〜100%で滑らかに変形可能

### Tripoモデルの制限
- Tripoで生成した3Dモデルはブレンドシェイプを持っていない
- リップシンクには手動でShape Keyを追加する必要がある

### 代替案
- VRMモデル（VRoid Studio等で作成）は最初からリップシンク対応
- Ready Player Me（2026/1/31終了予定）

---

## 6. 環境情報

| 項目 | バージョン/状態 |
|------|----------------|
| macOS | Darwin 25.2.0 |
| Blender | 5.0.1 |
| Ollama | インストール済み (qwen2.5:14b) |
| VOICEVOX | インストール済み (ポート50021) |
| ComfyUI | `/Users/takeshikoike2025/comfyUI/` |
| Python | 3.x |

---

## 7. 参考リンク

- Blender MCP: https://github.com/ahujasid/blender-mcp
- three-vrm: https://github.com/pixiv/three-vrm
- VRM仕様: https://vrm.dev/
- Tripo: https://www.tripo3d.ai/

---

## 8. 更新履歴

| 日付 | 内容 |
|------|------|
| 2026/01/24 | 2D版完成、3D版ステップ1完了、Blender/MCP設定完了 |
