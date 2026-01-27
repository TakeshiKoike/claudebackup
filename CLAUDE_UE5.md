# デジタル模擬患者プロジェクト - UE5 + MetaHuman

## 最終目標
看護教育用のリップシンク付きデジタル模擬患者を製作する

---

## 担当: 1番さん（Claude Code）

---

## 現在のプロジェクト

### UE5.6 プロジェクト ★現在使用
| 項目 | 値 |
|------|-----|
| パス | `C:\UE_Projects\PatientSim56` |
| エンジン | UE 5.6.1 |
| MCP | runreal/unreal-mcp |
| 有効プラグイン | PythonScriptPlugin, LiveLink, LiveLinkControlRig, **NV_ACE_Reference v2.5.0** |
| 現在のマップ | Lvl_ThirdPerson |
| MetaHuman | Keiji（Patient_Keiji として配置済み） |

---

## 進捗状況（2026-01-27）

- [x] UE5.6 プロジェクト作成
- [x] MCP 接続確認（runreal/unreal-mcp）
- [x] Python Remote Execution 有効化
- [x] MetaHuman Keiji インポート済み
- [x] レベルに Patient_Keiji 配置
- [x] **NVIDIA Audio2Face/ACE プラグイン導入** ✓
- [x] **Audio2Face と MetaHuman 連携（Face_AnimBP設定）** ✓
- [ ] **リアルタイムリップシンクテスト** ← 今ここ
- [ ] VOICEVOX → ACE パイプライン構築

---

## NVIDIA ACE プラグイン詳細

| 項目 | 値 |
|------|-----|
| プラグイン名 | NV_ACE_Reference |
| バージョン | 2.5.0-20250614-2282 |
| 場所 | `C:\UE_Projects\PatientSim56\Plugins\NV_ACE_Reference` |
| ドキュメント | https://docs.nvidia.com/ace/ace-unreal-plugin/latest/ |

### 含まれるモジュール
| モジュール | 説明 |
|-----------|------|
| **A2FLocal** | ローカルAudio2Face (RTX 4090で実行) |
| **A2FRemote** | リモートAudio2Face (クラウド) |
| **GPTLocal** | ローカルLLM (Minitron SLM) |
| **AnimStream** | アニメーションストリーミング |
| **OmniverseLiveLink** | Omniverse連携 |

### 含まれるアセット
- `mh_arkit_mapping_pose_A2F` - MetaHuman用ポーズアセット
- `mh_arkit_mapping_anim_A2F` - MetaHuman用アニメーション

---

## 次回やること

1. **Audio2Face-3D モデルをダウンロード＆インストール** ← 今ここ
   - https://developer.nvidia.com/ace-for-games にアクセス
   - 「Download Audio2Face 3.0 Unreal Engine Models」をダウンロード
   - 解凍して `C:\UE_Projects\PatientSim56\Plugins\` に配置
   - UEエディタ再起動
2. **リアルタイムリップシンクテスト**
   - VOICEVOX（玄野武宏 ID:11）で音声生成
   - `AnimateCharacterFromWavFileAsync` でリップシンク実行
3. **VOICEVOX → ACE パイプライン構築**
   - リアルタイム連携テスト

### 完了済み
- [x] ACEAudioCurveSource コンポーネント追加済み（Patient_Keiji）
- [x] Face_AnimBP 設定完了
  - Apply ACE Face Animations ノード追加
  - Pose Asset → mh_arkit_mapping_pose_A2F に変更
  - Modify Curve (MouthClose) 無効化（Alpha=0）
- [x] VOICEVOX テスト音声生成済み（`C:\UE_Projects\PatientSim56\Saved\test_voice.wav`）

### ブロッカー
- **A2FLocal モデル未インストール**: NV_ACE_Reference プラグインはあるが、リップシンク用AIモデルが別途必要

---

## MCP 設定

### runreal/unreal-mcp
| 項目 | 値 |
|------|-----|
| プロトコル | UDP マルチキャスト + Python Remote Execution |
| アドレス | 239.0.0.1:6766 |
| 設定 | `npx -y @runreal/unreal-mcp` |
| 必要設定 | UE5 で Python Remote Execution を有効化 |

---

## 旧プロジェクト（参考用）

### UE5.7 プロジェクト
| 項目 | 値 |
|------|-----|
| パス | `C:\Users\kokek\OneDrive\ドキュメント\Unreal Projects\MyProject3` |
| エンジン | UE 5.7 |
| MCP | UnrealClaude (HTTP Port 3000) |

### UE5.3 プロジェクト
| 項目 | 値 |
|------|-----|
| パス | `C:\UE_Projects\PatientSim53` |
| エンジン | UE 5.3 |

---

## 断念したアプローチ

### Audio2Face スタンドアロン
- **理由**: NV_ACE_Referenceプラグインで直接UE5内処理が可能。外部アプリ不要。

### MuseTalk（Tencent）
- **理由**: 「リアルタイム」が実際にはバッチ処理、リップシンク品質も不十分

### OVRLipSync（Meta）
- **理由**: UE5.3/5.6/5.7 との互換性問題

---

## 既存リソース

| 項目 | 値 |
|------|-----|
| LLM | Ollama + ELYZA-JP-8B |
| TTS | VOICEVOX（localhost:50021） |
| GPU | NVIDIA RTX 4090 |
| 患者画像 | `C:\Users\kokek\Downloads\ComfyUI_00238_.png` |

---

## 参考リンク
- [runreal/unreal-mcp](https://github.com/runreal/unreal-mcp)
- [NVIDIA ACE](https://developer.nvidia.com/ace)
