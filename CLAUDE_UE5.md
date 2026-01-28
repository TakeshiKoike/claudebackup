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

## 進捗状況（2026-01-28）

- [x] UE5.6 プロジェクト作成
- [x] MCP 接続確認（runreal/unreal-mcp）
- [x] Python Remote Execution 有効化
- [x] MetaHuman Keiji インポート済み
- [x] レベルに Patient_Keiji 配置
- [x] **NVIDIA Audio2Face/ACE プラグイン導入** ✓
- [x] **Audio2Face と MetaHuman 連携（Face_AnimBP設定）** ✓
- [x] **Audio2Face-3D モデル（LocalA2F-Mark）インストール** ✓
- [x] **バッチ処理リップシンク動作確認** ✓
- [x] **カメラ設定（顔アップ）** ✓
- [x] **ACE API 調査完了** ✓
- [x] **リアルタイムストリーミングパイプライン構築** ✓
- [x] **VOICEVOX → ACE リアルタイム連携** ✓
- [ ] 会話システム最適化（応答時間短縮）

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

### 選択肢A: UE5 ACE プラグインで実用的な会話システム（推奨）
1. **Blueprint で非同期 API を使用**
   - `AnimateCharacterFromWavFileAsync` は Blueprint 専用
   - Python からは同期版のみ利用可能（25秒の遅延あり）
2. **短い音声クリップで運用**
   - 長い文章を分割して順次再生
   - 各クリップの処理遅延を許容

### 選択肢B: Audio2Face-3D SDK で真のリアルタイム
1. **TensorRT スタンドアロン SDK インストール**
   - https://developer.nvidia.com/tensorrt からZIPダウンロード
   - pip版はDLLのみでヘッダファイルなし（ビルド不可）
   - バージョン 10.13+ が必要
2. **Audio2Face-3D SDK ビルド**
   - `C:\UE_Projects\Audio2Face-3D-SDK` にクローン済み
   - CUDA 12.8 ✅、TensorRT ❌（スタンドアロン版が必要）
3. **カスタム統合**
   - SDK から生成したブレンドシェイプを UE5 へ送信

### 完了済み
- [x] ACEAudioCurveSource コンポーネント追加済み（BP_Keiji）
- [x] Face_AnimBP 設定完了
- [x] VOICEVOX テスト音声生成済み（`C:\UE_Projects\PatientSim56\Saved\test_voice.wav`）
- [x] **Audio2Face-3D モデル インストール**
  - NvAudio2FaceMark-UE5.6-v2.4.0（LocalA2F-Mark）
  - `C:\UE_Projects\PatientSim56\Plugins\` に配置済み
- [x] **バッチ処理リップシンク動作確認**
  - `ACEBlueprintLibrary.animate_character_from_wav_file()` で動作OK
  - `a2f_provider_name="LocalA2F-Mark"` 指定
- [x] **カメラ・PlayerStart設定**
  - Keijiの顔正面にカメラ配置
  - PlayerStartも同位置に配置

### 課題と調査結果

#### ACE プラグイン API 調査（2026-01-28）
| API | 説明 | Python公開 |
|-----|------|-----------|
| `animate_character_from_wav_file` | 同期版、約25秒遅延 | ✓ |
| `AnimateCharacterFromWavFileAsync` | 非同期版 | ✗（Blueprint専用）|
| `override_a2f3d_inference_mode` | バースト/リアルタイムモード切替 | ✓ |
| `override_a2f3d_realtime_initial_chunk_size` | チャンクサイズ設定 | ✓ |
| `allocate_a2f3d_resources` | リソース事前確保 | ✓ |

#### 発見事項
- **リアルタイムモード**: `force_burst_mode=False` で有効だが、入力は完全なWAVファイル必須
- **真のオーディオストリーミング**: UE5プラグインでは未対応、SDK直接利用が必要
- **pip版TensorRT**: DLLのみでヘッダなし、SDKビルドには不十分

#### パイプライン性能テスト結果（2026-01-28）
| ステップ | CPU版 | GPU版 |
|---------|-------|-------|
| LLM応答 (ELYZA-8B) | 2.3秒 | 2.3秒 |
| 音声生成 (VOICEVOX) | 6秒 | **0.14秒** |
| リップシンク (LocalA2F-Mark) | - | 音声長と同等 |

**VOICEVOX GPU モード**: `--use_gpu` オプションで約50倍高速化

**結論**: 会話システム実用レベル達成。

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
| TTS | VOICEVOX（localhost:50021、GPU モード） |
| GPU | NVIDIA RTX 4090 |
| 患者画像 | `C:\Users\kokek\Downloads\ComfyUI_00238_.png` |

---

## VOICEVOX GPU モード起動

```powershell
# エンジン停止
Stop-Process -Name 'run' -Force -ErrorAction SilentlyContinue

# GPU モードで起動
Start-Process -FilePath 'C:\Users\kokek\AppData\Local\Programs\VOICEVOX\vv-engine\run.exe' -ArgumentList '--use_gpu','--port','50021'
```

---

## 作成済みスクリプト

| スクリプト | 説明 |
|-----------|------|
| `C:\Users\kokek\ue_lipsync_test.py` | 基本リップシンクテスト |
| `C:\Users\kokek\ue_realtime_lipsync2.py` | リアルタイムモード設定+テスト |
| `C:\Users\kokek\generate_voice.py` | VOICEVOX音声生成 |
| `C:\Users\kokek\ue_check_ace_api.py` | ACE API 一覧表示 |
| `C:\Users\kokek\ue_check_realtime_api.py` | リアルタイムAPI詳細 |
| `C:\Users\kokek\ue_observe_test.py` | リップシンク観察テスト |
| `C:\Users\kokek\patient_test.py` | パイプライン自動テスト |
| `C:\Users\kokek\patient_conversation.py` | 対話式会話システム |

---

## 参考リンク
- [runreal/unreal-mcp](https://github.com/runreal/unreal-mcp)
- [NVIDIA ACE](https://developer.nvidia.com/ace)
- [Audio2Face-3D SDK](https://github.com/NVIDIA/Audio2Face-3D-SDK)
