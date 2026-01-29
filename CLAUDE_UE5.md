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

## 進捗状況（2026-01-29 更新）

- [x] UE5.6 プロジェクト作成
- [x] MCP 接続確認（runreal/unreal-mcp）
- [x] Python Remote Execution 有効化
- [x] MetaHuman Keiji インポート済み
- [x] レベルに Patient_Keiji 配置
- [x] **NVIDIA Audio2Face/ACE プラグイン導入** ✓
- [x] **Audio2Face と MetaHuman 連携（Face_AnimBP設定）** ✓
- [x] **Audio2Face-3D モデル（LocalA2F-Mark）インストール** ✓
- [x] **カメラ設定（顔アップ）** ✓
- [x] **ACE API 調査完了** ✓
- [x] **Audio2Face-3D SDK ビルド成功** ✓
- [x] **a2f_to_json ツール作成** ✓（音声→JSONブレンドシェイプ変換）
- [x] **lipsync_pipeline.py 作成** ✓（テキスト→JSON完全パイプライン）
- [x] **UE5 Remote Execution 接続確認** ✓
- [x] **MetaHuman Face 構造調査** ✓
- [x] **JSON→モーフターゲット直接適用実験** ❌ 失敗（詳細は下記「実験記録」参照）
- [x] **Sound Wave リップシンク動作** ✅ 成功（BP_takeshi77）
- [ ] **リアルタイムリップシンク** ← 次の目標（下記「リアルタイム方式」参照）
- [ ] 会話システム最適化

---

## リアルタイムリップシンク方式（2026-01-29 調査）

### 公式サポート方式

| 方式 | Blueprint | C++ | 説明 |
|------|-----------|-----|------|
| **Sound Wave** | ✅ | ✅ | インポート済みSound Waveから（現在使用中） |
| **WAV File** | ✅ | ✅ | ディスク上のWAVファイルから直接 |
| **Audio Samples** | ❌ | ✅ | 生のオーディオサンプルをストリーミング |
| **Animation Stream** | ✅ | ✅ | Animgraphサービスからのストリーム購読 |

### プロジェクト設定（Edit → Project Settings → NVIDIA ACE）

| 設定項目 | 説明 | 推奨値 |
|---------|------|--------|
| Inference Burst Mode | Default / ForceBurstMode / **ForceRealTimeMode** | ForceRealTimeMode |
| Max Initial Audio Chunk Size | リアルタイムモード時の初期チャンク（秒） | 0.5 |

**注意**: Burst modeは同一システムでレンダリングと推論を行う場合は非推奨

### Blueprint API 一覧

| ノード | 説明 |
|--------|------|
| `Animate Character From Sound Wave Async` | Sound Waveからリップシンク（現在使用中） |
| `Animate Character From Wav File Async` | WAVファイルパスからリップシンク |
| `Override A2F-3D Inference Burst Mode` | ランタイムでモード切替 |
| `Override A2F-3D Realtime Initial Chunk Size` | ランタイムでチャンクサイズ変更 |
| `Allocate A2F-3D Resources` | GPUリソース事前確保（初回遅延削減） |
| `Free A2F-3D Resources` | GPUリソース解放 |
| `Stop Character` | アニメーション停止 |

### 実用的リアルタイムワークフロー

**推奨パイプライン（現時点で最も実用的）:**

```
[ユーザー入力] → [LLM応答 2.3秒] → [VOICEVOX GPU 0.14秒] → [WAV保存] → [Animate From Wav File Async]
```

**合計遅延**: 約2.5秒（LLM応答完了後、リップシンク開始）

### 真のストリーミング方式（将来の改善）

C++ `AnimateFromAudioSamples()` API を使用すれば、音声生成中にリップシンクを開始可能。
ただし、UE5 C++プラグイン開発が必要。

### 参考リンク
- [NVIDIA ACE Unreal Plugin Docs](https://docs.nvidia.com/ace/ace-unreal-plugin/2.5/)
- [Audio2Face-3D Docs](https://docs.nvidia.com/ace/ace-unreal-plugin/2.5/ace-unreal-plugin-audio2face.html)

### 最新の進捗（2026-01-29 夜）

#### Sound Wave リップシンク成功！
**BP_takeshi77 でリップシンク動作確認済み**

| 項目 | 設定 |
|------|------|
| キャラクター | BP_takeshi77（MetaHuman） |
| コンポーネント | ACEAudioCurveSourceComponent（Auto Activate: True） |
| Blueprint | Event BeginPlay → Animate Character From Sound Wave Async |
| **重要**: Character ピン | **Self を接続**（これが必須！） |
| Sound Wave | /Game/Audio/LipsyncAudio（2.99秒）、/Game/Audio/LongMaleVoice（10.05秒） |
| A2F Provider | LocalA2F-Mark |

**修正ポイント**:
- 「AnimateCharacterFromSoundWave called with no Character input」エラー
- 解決: Animate Character From Sound Wave Async ノードの Character ピンに「Get a reference to Self」を接続

**バックアップ**: `C:\UE_Projects\PatientSim56\Backup_ACE_Lipsync_20260129\`

---

#### 成功（SDK関連）
1. **TensorRT 10.14.1** インストール完了（`C:\TensorRT`）
2. **Audio2Face-3D SDK** ビルド成功（147/147ターゲット）
3. **モデルデータ** ダウンロード完了（mark, claire, james）
4. **a2f_to_json ツール** 作成・動作確認
   - 16kHz WAV → JSON ブレンドシェイプ変換
   - 68個のウェイト × 60fps で出力
   - 4秒音声 → 240フレーム生成成功
5. **lipsync_pipeline.py** テキスト→JSON完全パイプライン完成
   - 処理時間: 7.63秒
6. **UE5 Remote Execution** 接続成功
   - Python API でモーフターゲット読み書き可能

#### 失敗
- **JSON → MetaHuman 直接適用**: Face_AnimBP がモーフを上書きするため不可
- **Playモード**: 3回クラッシュ

#### 重要な発見
- MetaHuman Face は `Face_AnimBP_C` で制御されている
- Python API での `set_morph_target()` は値を設定できるが、視覚的変化なし
- ACEプラグインの専用API使用が必要

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

## Audio2Face-3D SDK 統合（2026-01-29 完了）

### インストール済みコンポーネント
| コンポーネント | バージョン | パス |
|---------------|-----------|------|
| CUDA | 12.8 | `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8` |
| TensorRT | 10.14.1 | `C:\TensorRT` |
| Audio2Face-3D SDK | 最新 | `C:\UE_Projects\Audio2Face-3D-SDK` |

### a2f_to_json ツール
| 項目 | 値 |
|------|-----|
| 実行ファイル | `C:\UE_Projects\Audio2Face-3D-SDK\tools\a2f_to_json\build\Release\a2f_to_json.exe` |
| 入力 | 16kHz WAV音声ファイル |
| 出力 | JSONブレンドシェイプデータ（68ウェイト × 60fps） |
| モデル | mark（デフォルト） |

### 使用方法

#### 単体使用
```powershell
# 環境設定スクリプトで実行
C:\UE_Projects\Audio2Face-3D-SDK\tools\a2f_to_json\run_test.ps1

# または手動
$env:Path = "C:\TensorRT\lib;C:\TensorRT\bin;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin;" + $env:Path
$env:Path += ";C:\UE_Projects\Audio2Face-3D-SDK\_build\release\audio2x-sdk\bin"

.\a2f_to_json.exe input.wav output.json [model.json]
```

#### 完全パイプライン（テキスト→リップシンク）
```powershell
python C:\Users\kokek\lipsync_pipeline.py "こんにちは、今日はどうされましたか"
```

**パイプライン性能（2026-01-29テスト）**:
| ステップ | 時間 |
|---------|------|
| VOICEVOX音声生成 | 6.15秒 |
| A2F SDKリップシンク | 1.48秒 |
| **合計** | **7.63秒** |

出力: `C:\UE_Projects\PatientSim56\Saved\Lipsync\` に WAV + JSON

### 出力JSON形式
```json
{
  "fps": 60,
  "frameCount": 240,
  "blendshapeCount": 68,
  "frames": [
    [0.0225, 0.0000, ...],  // フレーム0: 68個のブレンドシェイプウェイト
    [0.0246, 0.0000, ...],  // フレーム1
    ...
  ]
}
```

---

## 次回やること

### UE5 統合の選択肢

#### A: JSONファイル経由 ← **現在のアプローチ（実装済み）**

**パイプライン完成！**
1. ✅ VOICEVOXで音声生成 → WAVファイル保存
2. ✅ a2f_to_json でブレンドシェイプJSON生成
3. 🔄 UE5でJSONを読み込み → MetaHuman FaceにMorph Target適用
4. 🔄 音声再生と同期してアニメーション再生

**利点**: シンプル、デバッグしやすい
**欠点**: ファイルI/O遅延

**UE5での使用方法**:
```python
# UE5 Python Remote Executionで実行
exec(open(r"C:\Users\kokek\ue_json_lipsync.py").read())
load_lipsync(r"C:\UE_Projects\PatientSim56\Saved\Lipsync\lipsync_XXXX.json")
setup_metahuman("Patient_Keiji")
apply_frame(0)  # テストフレーム適用
```

#### B: LiveLink経由（リアルタイム）
1. カスタムLiveLinkソースを作成
2. a2f_to_json をリアルタイムストリーミング対応に拡張
3. LiveLink → MetaHuman Face

**利点**: 低遅延リアルタイム
**欠点**: 実装が複雑

#### C: ACEプラグインに戻る
- Blueprint非同期APIを活用
- 既存のLocalA2F-Markモデル利用

---

### 旧選択肢（参考）

~~### 選択肢A: UE5 ACE プラグインで実用的な会話システム（推奨）~~
~~### 選択肢B: Audio2Face-3D SDK で真のリアルタイム~~
→ **選択肢B完了！SDK動作確認済み**

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

## 実験記録：JSON → MetaHuman直接適用（2026-01-29）失敗

### 目標
Audio2Face-3D SDKで生成したJSONブレンドシェイプデータを、UE5のMetaHumanに直接適用してリップシンクを実現する。

### 実験内容

#### 成功した部分
1. **Audio2Face-3D SDK ビルド** ✅
   - TensorRT 10.14.1 インストール
   - SDK 147/147 ターゲットビルド成功

2. **a2f_to_json ツール作成** ✅
   - 16kHz WAV → JSON変換
   - 68ブレンドシェイプ × 60fps 出力
   - 処理時間: 1.48秒（4秒音声）

3. **完全パイプライン** ✅
   - テキスト → VOICEVOX → WAV → JSON
   - 合計処理時間: 7.63秒

4. **UE5 Python Remote Execution 接続** ✅
   - `remote_execution.py` で UE5 と通信成功
   - MetaHuman (BP_Keiji) 発見
   - Face コンポーネント特定
   - モーフターゲット値の読み書き確認

#### 失敗した部分
1. **モーフターゲット視覚反映** ❌
   - `set_morph_target("CTRL_expressions_jawOpen", 1.0)` 実行
   - 値は設定される（0.0 → 0.9 確認済み）
   - **しかし画面上で顔が動かない**

2. **AnimBP無効化試行** ❌
   - `animation_mode = ANIMATION_CUSTOM_MODE` 設定
   - `comp.stop()` 実行
   - `anim_class = None` 設定
   - `mark_render_state_dirty()` 実行
   - **いずれも視覚的変化なし**

3. **Playモード** ❌
   - Playボタンを押すとUE5がクラッシュ（3回発生）

### 原因分析

#### 確認できた事実
- Face コンポーネントには `Face_AnimBP_C` が設定されている
- モーフターゲット名 `CTRL_expressions_jawOpen` は存在する
- Python API での値の読み書きは正常に動作する

#### 推定される原因
1. **Face_AnimBP が毎フレーム上書き**
   - AnimBPがモーフターゲットを常に制御している
   - Python での設定が次フレームで上書きされる可能性

2. **MetaHuman 特有の制御方式**
   - 通常の SkeletalMesh と異なる制御パスを使用している可能性
   - ACE プラグインは専用の連携方法を持っている

3. **Claude Code の限界**
   - 画面を見ることができない
   - 視覚的なデバッグが不可能
   - 試行錯誤に時間がかかる

### 試行したスクリプト一覧
| スクリプト | 目的 | 結果 |
|-----------|------|------|
| `ue_json_lipsync.py` | JSON読込→モーフ適用 | UE5クラッシュ |
| `ue_json_lipsync_safe.py` | 安全な構造確認 | 成功 |
| `ue5_remote.py` | Remote Execution接続 | 成功 |
| `ue5_find_morphs.py` | モーフターゲット探索 | 成功 |
| `ue5_apply_lipsync.py` | フレーム適用 | 値設定成功、視覚変化なし |
| `ue5_test_jaw.py` | 単純なjawOpen設定 | 値設定成功、視覚変化なし |
| `ue5_animate_lipsync.py` | 連続アニメーション | 完走、視覚変化なし |
| `ue5_pakupaku.py` | 口パクパク | 完走、視覚変化なし |
| `ue5_pakupaku2.py` | AnimBP無効化+パクパク | 完走、視覚変化なし |
| `ue5_open_mouth.py` | 口を開けたまま固定 | 完走、視覚変化なし |
| `ue5_force_jaw.py` | 強制更新試行 | 完走、視覚変化なし |

### 結論
**JSON → MetaHuman 直接適用アプローチは現状では失敗。**

MetaHuman の Face は通常の SkeletalMesh モーフターゲット制御では動かせない。
ACE プラグインの専用 API（`animate_character_from_wav_file`）を使用すべき。

### 今後の選択肢
1. **ACEプラグインに戻る**（推奨）
   - 既に動作確認済み
   - `animate_character_from_wav_file()` を使用

2. **LiveLink 経由**
   - ACE プラグインと同様の方式
   - 実装が複雑

3. **AnimBP の改造**
   - Face_AnimBP に外部入力を受け付ける機能を追加
   - Blueprint の深い知識が必要

---

## 断念したアプローチ

### JSON → MetaHuman 直接モーフ適用（2026-01-29）
- **理由**: Face_AnimBP がモーフターゲットを上書きするため、Python API での直接制御では視覚的変化が得られない。詳細は上記「実験記録」参照。

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
| `C:\Users\kokek\lipsync_pipeline.py` | **テキスト→リップシンクJSON完全パイプライン** |
| `C:\Users\kokek\ue_json_lipsync.py` | **UE5用JSONリップシンク適用スクリプト** |

---

## 参考リンク
- [runreal/unreal-mcp](https://github.com/runreal/unreal-mcp)
- [NVIDIA ACE](https://developer.nvidia.com/ace)
- [Audio2Face-3D SDK](https://github.com/NVIDIA/Audio2Face-3D-SDK)
