# MetaHuman リップシンクシステム 完全マニュアル

## 目次
1. [システム概要](#1-システム概要)
2. [システム構成図](#2-システム構成図)
3. [データフロー](#3-データフロー)
4. [必要なソフトウェア・プラグイン](#4-必要なソフトウェアプラグイン)
5. [新規MetaHumanセットアップ手順（1から作成）](#5-新規metahumanセットアップ手順1から作成)
6. [MetaHuman入れ替え手順](#6-metahuman入れ替え手順)
7. [共通部分と個別設定部分](#7-共通部分と個別設定部分)
8. [設定ファイル詳細](#8-設定ファイル詳細)
9. [トラブルシューティング](#9-トラブルシューティング)
10. [今回の作業記録（2026-02-04）](#10-今回の作業記録2026-02-04)

---

## 1. システム概要

### 目的
看護教育用のリップシンク付きデジタル模擬患者システム。
ユーザーの入力に対してLLMが患者として応答し、音声とリップシンクを伴ってMetaHumanが発話する。

### 処理フロー
```
[ユーザー入力] → [LLM応答生成] → [音声合成] → [リップシンク] → [MetaHuman発話]
     ↓              ↓              ↓              ↓
   テキスト      ELYZA-8B       VOICEVOX      NVIDIA ACE
                (Ollama)        (GPU)       Audio2Face
```

### 処理時間（実測値）
| ステップ | 処理時間 |
|---------|---------|
| LLM応答生成 | 2〜5秒 |
| 音声合成 | 0.1〜0.2秒 |
| リップシンク開始 | 即時 |
| **合計** | **約3〜7秒** |

---

## 2. システム構成図

```
┌─────────────────────────────────────────────────────────────────┐
│                         UE5 Editor                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Lvl_ThirdPerson                       │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │              BP_keiji (MetaHuman)                │    │   │
│  │  │  ┌─────────────────────────────────────────┐    │    │   │
│  │  │  │  Components:                            │    │    │   │
│  │  │  │  - Face (SkeletalMeshComponent)         │    │    │   │
│  │  │  │  - Body (SkeletalMeshComponent)         │    │    │   │
│  │  │  │  - ACEAudioCurveSource ← リップシンク用 │    │    │   │
│  │  │  └─────────────────────────────────────────┘    │    │   │
│  │  │  ┌─────────────────────────────────────────┐    │    │   │
│  │  │  │  Variables (Instance Editable):         │    │    │   │
│  │  │  │  - PendingWavPath (String)              │    │    │   │
│  │  │  │  - IsReady (Boolean)                    │    │    │   │
│  │  │  │  - PendingMessage (String)              │    │    │   │
│  │  │  │  - CurrentSubtitle (String)             │    │    │   │
│  │  │  └─────────────────────────────────────────┘    │    │   │
│  │  │  ┌─────────────────────────────────────────┐    │    │   │
│  │  │  │  Event Graph:                           │    │    │   │
│  │  │  │  - Event Tick → PendingWavPath監視      │    │    │   │
│  │  │  │  - AnimateFromWavFileAsync実行          │    │    │   │
│  │  │  │  - On Animation Ended → IsReady=True    │    │    │   │
│  │  │  └─────────────────────────────────────────┘    │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↑                                  │
│                    Python Remote Execution                      │
│                         (UDP 239.0.0.1:6766)                   │
└─────────────────────────────────────────────────────────────────┘
                               ↑
┌─────────────────────────────────────────────────────────────────┐
│                    Python Scripts                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  patient_conversation.py                                 │   │
│  │  - UE5接続 (remote_execution)                           │   │
│  │  - LLM呼び出し (Ollama API)                             │   │
│  │  - 音声生成 (VOICEVOX API)                              │   │
│  │  - PendingWavPath設定 → リップシンクトリガー            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                      ↓                    ↓                     │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │   Ollama (LLM)       │    │   VOICEVOX (TTS)     │          │
│  │   localhost:11434    │    │   localhost:50021    │          │
│  │   ELYZA-JP-8B        │    │   GPU Mode           │          │
│  └──────────────────────┘    └──────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. データフロー

### 3.1 リップシンク実行フロー

```
┌────────────────┐
│ Python Script  │
│ (外部から実行)  │
└───────┬────────┘
        │ 1. WAVファイル生成
        ↓
┌────────────────┐
│ VOICEVOX       │
│ 音声合成       │
└───────┬────────┘
        │ 2. WAVファイル保存
        ↓
┌────────────────────────────────────────────────┐
│ C:/UE_Projects/PatientSim56/Saved/             │
│ patient_response.wav                           │
└───────┬────────────────────────────────────────┘
        │ 3. PendingWavPath変数に設定
        ↓
┌────────────────────────────────────────────────┐
│ BP_keiji.PendingWavPath =                      │
│ "C:/UE_Projects/PatientSim56/Saved/..."        │
└───────┬────────────────────────────────────────┘
        │ 4. Event Tickで検知
        ↓
┌────────────────────────────────────────────────┐
│ Event Graph (Event Tick)                       │
│ if IsReady && PendingWavPath != "":            │
│   IsReady = False                              │
│   AnimateCharacterFromWavFileAsync()           │
│   PendingWavPath = ""                          │
└───────┬────────────────────────────────────────┘
        │ 5. NVIDIA ACE処理
        ↓
┌────────────────────────────────────────────────┐
│ ACEAudioCurveSourceComponent                   │
│ - WAVファイル読み込み                          │
│ - Audio2Face-3D推論 (LocalA2F-Mark)            │
│ - ブレンドシェイプ生成                         │
│ - Faceメッシュに適用                           │
└───────┬────────────────────────────────────────┘
        │ 6. アニメーション完了
        ↓
┌────────────────────────────────────────────────┐
│ On Animation Ended イベント                    │
│ IsReady = True                                 │
│ (次のリップシンク受付可能)                     │
└────────────────────────────────────────────────┘
```

### 3.2 変数の役割

| 変数名 | 型 | 役割 | 設定元 |
|--------|-----|------|--------|
| PendingWavPath | String | 再生するWAVファイルパス | Python |
| IsReady | Boolean | リップシンク受付可能フラグ | Blueprint |
| PendingMessage | String | UI入力メッセージ（WBP用） | WBP_PatientChat |
| CurrentSubtitle | String | 字幕表示テキスト | Python |

---

## 4. 必要なソフトウェア・プラグイン

### 4.1 UE5プラグイン

| プラグイン | 用途 | 入手先 |
|-----------|------|--------|
| **NV_ACE_Reference** | NVIDIA ACEリップシンク | [NVIDIA Developer](https://developer.nvidia.com/ace-for-games) |
| **NvAudio2FaceMark** | Audio2Face-3Dモデル | 同上 |
| **Python Script Plugin** | Python連携 | UE5標準 |
| **Live Link** | リアルタイムデータ連携 | UE5標準 |

### 4.2 外部ソフトウェア

| ソフトウェア | 用途 | ポート |
|-------------|------|--------|
| **Ollama** | LLM推論 | localhost:11434 |
| **VOICEVOX** | 音声合成 | localhost:50021 |

### 4.3 UE5プロジェクト設定

| 設定項目 | 場所 | 値 |
|---------|------|-----|
| Python Remote Execution | Edit → Project Settings → Python | Enable Remote Execution: ON |
| Multicast Group | 同上 | 239.0.0.1:6766 |
| NVIDIA ACE Provider | Edit → Project Settings → NVIDIA ACE | LocalA2F-Mark |

---

## 5. 新規MetaHumanセットアップ手順（1から作成）

### 5.1 前提条件
- UE5.6プロジェクトが作成済み
- NV_ACE_Referenceプラグインがインストール済み
- NvAudio2FaceMarkプラグインがインストール済み
- Python Remote Executionが有効化済み

### 5.2 手順

#### Step 1: MetaHumanのインポート
1. Quixel Bridgeを開く（UE5内）
2. 使用したいMetaHumanを選択
3. 「Add to Project」でインポート
4. `/Game/MetaHumans/[名前]/BP_[名前]` が作成される

#### Step 2: ACEAudioCurveSourceComponentの追加
1. Content Browserで `BP_[名前]` をダブルクリック
2. Blueprintエディタが開く
3. 左の「Components」パネルで「+ Add」をクリック
4. 「ACEAudioCurveSource」を検索して追加
5. 右の「Details」パネルで設定：
   - **Auto Activate**: ✓ チェックON
   - **A2F Provider Name**: LocalA2F-Mark

#### Step 3: Blueprint変数の追加
1. 左の「My Blueprint」パネルで「Variables」の「+」をクリック
2. 以下の4つの変数を追加：

| 変数名 | 型 | デフォルト値 | Instance Editable |
|--------|-----|-------------|-------------------|
| PendingWavPath | String | (空) | ✓ ON |
| IsReady | Boolean | True | ✓ ON |
| PendingMessage | String | (空) | ✓ ON |
| CurrentSubtitle | String | (空) | ✓ ON |

**重要**: 各変数を選択し、Detailsパネルで「Instance Editable」にチェックを入れること。

#### Step 4: Event Graphの作成

**Event Tick部分:**
```
Event Tick
    ↓
Branch (Condition: IsReady)
    ├─ True →
    │     Branch (Condition: PendingWavPath == "")
    │         ├─ True → (何もしない)
    │         └─ False →
    │               Set IsReady = False
    │                   ↓
    │               Animate Character From Wav File Async
    │                   - Character: Self
    │                   - Path to Wav: PendingWavPath
    │                   - A2F Provider Name: "LocalA2F-Mark"
    │                   ↓ (Audio Send Completed)
    │               Set PendingWavPath = ""
    │
    └─ False → (何もしない)
```

**On Animation Ended部分:**
1. 左のComponentsパネルで「ACEAudioCurveSource」を選択
2. 右クリック → 「Add Event」 → 「On Animation Ended」
3. 以下のように接続：
```
On Animation Ended (ACEAudioCurveSource)
    ↓
Set IsReady = True
```

#### Step 5: コンパイルと保存
1. 「Compile」ボタンをクリック
2. 「Save」ボタンをクリック

#### Step 6: レベルへの配置
1. Content Browserから `BP_[名前]` をレベルにドラッグ
2. 位置を調整（例: X=10, Y=0, Z=210）
3. カメラを顔が見える位置に配置

#### Step 7: 設定ファイルの更新
`C:\UE_Projects\PatientSim56_v2\Config\PatientTemplate.json` を編集：

```json
{
    "active_patient": "[新しい患者ID]",
    "metahumans": {
        "[新しい患者ID]": {
            "blueprint_name": "BP_[名前]",
            "display_name": "[表示名]",
            "profile_id": "[プロファイルID]"
        }
    },
    "patient_profiles": [
        {
            "id": "[プロファイルID]",
            "name": "[患者名]",
            "age": [年齢],
            "gender": "[male/female]",
            "condition": "[症状]",
            "personality": "[性格]",
            "voice_speaker_id": [VOICEVOXのスピーカーID],
            "llm_prompt": "[LLMプロンプト]"
        }
    ]
}
```

#### Step 8: 動作確認
1. UE5で「Play」ボタン
2. 別ターミナルで `python C:\Users\kokek\patient_conversation.py`
3. テキストを入力してリップシンクを確認

---

## 6. MetaHuman入れ替え手順

### 6.1 既存のMetaHumanがセットアップ済みの場合

既にBP_takeshi77などがセットアップ済みで、別のMetaHumanに入れ替える場合。

#### 最小作業パターン（推奨）

| 手順 | 作業内容 | 所要時間 |
|------|---------|---------|
| 1 | 新MetaHumanをQuixel Bridgeからインポート | 5分 |
| 2 | ACEAudioCurveSourceComponent追加 | 2分 |
| 3 | 変数4つ追加（Instance Editable ON） | 5分 |
| 4 | Event Graphを既存BPからコピペ | 3分 |
| 5 | On Animation Endedイベントを再紐づけ | 2分 |
| 6 | PatientTemplate.json更新 | 2分 |
| 7 | レベルに配置 | 1分 |
| **合計** | | **約20分** |

#### 詳細手順

**Step 1: 新MetaHumanのインポート**
- Quixel Bridgeから新しいMetaHumanをインポート

**Step 2: ACEコンポーネント追加**
- BP_[新名前]を開く
- Add Component → ACEAudioCurveSource
- Auto Activate = ON

**Step 3: 変数追加**
以下の4変数を追加（全てInstance Editable ON）：
- PendingWavPath (String)
- IsReady (Boolean, default=True)
- PendingMessage (String)
- CurrentSubtitle (String)

**Step 4: Event Graphコピー**
1. 既存のBP_takeshi77を開く
2. Event Graph → Ctrl+A → Ctrl+C
3. 新しいBP_[新名前]を開く
4. Event Graph → Ctrl+A → Delete → Ctrl+V

**Step 5: On Animation Ended再紐づけ（重要！）**
コピペしたEvent Graphの「On Animation Ended」は、古いBPのACEコンポーネントを参照しています。
1. On Animation Endedノードを**削除**
2. 左のComponentsで**ACEAudioCurveSource**を右クリック
3. Add Event → On Animation Ended
4. 新しいノードから「Set IsReady = True」に接続

**Step 6: 設定ファイル更新**
PatientTemplate.jsonのactive_patientとmetahumansを更新

**Step 7: レベル配置**
- 古いMetaHumanをレベルから削除
- 新しいMetaHumanをドラッグ&ドロップ

---

## 7. 共通部分と個別設定部分

### 7.1 共通部分（変更不要）

以下は全MetaHumanで共通。一度設定すれば変更不要。

| 項目 | 場所 | 説明 |
|------|------|------|
| NV_ACE_Referenceプラグイン | Plugins/ | プロジェクト共通 |
| NvAudio2FaceMarkプラグイン | Plugins/ | プロジェクト共通 |
| Python Remote Execution設定 | Project Settings | プロジェクト共通 |
| patient_conversation.py | C:\Users\kokek\ | スクリプト共通 |
| patient_config.py | C:\Users\kokek\ | 設定読み込み共通 |
| WAV出力パス | PatientTemplate.json | 共通パス |
| Ollama/VOICEVOX設定 | PatientTemplate.json | 共通 |

### 7.2 個別設定部分（MetaHumanごとに必要）

| 項目 | 設定場所 | 説明 |
|------|---------|------|
| ACEAudioCurveSourceComponent | Blueprint | 各BPに追加 |
| 4つのBlueprint変数 | Blueprint | 各BPに追加、Instance Editable必須 |
| Event Graph | Blueprint | コピペ後、On Animation Ended再紐づけ |
| PatientTemplate.json登録 | 設定ファイル | metahumans, patient_profiles |
| active_patient | 設定ファイル | 使用するMetaHumanのID |
| レベル配置 | Level | 使用するBPをレベルに配置 |

### 7.3 チェックリスト

新しいMetaHumanを追加する際のチェックリスト：

```
□ MetaHumanインポート完了
□ ACEAudioCurveSourceComponent追加
  □ Auto Activate = ON
□ 変数追加
  □ PendingWavPath (String, Instance Editable ON)
  □ IsReady (Boolean, default=True, Instance Editable ON)
  □ PendingMessage (String, Instance Editable ON)
  □ CurrentSubtitle (String, Instance Editable ON)
□ Event Graphコピペ
□ On Animation Endedイベント再紐づけ
□ Compile成功
□ Save完了
□ PatientTemplate.json更新
  □ metahumansに追加
  □ patient_profilesに追加
  □ active_patient変更
□ レベルに配置
□ 動作確認（Playモードでリップシンク）
```

---

## 8. 設定ファイル詳細

### 8.1 PatientTemplate.json

**場所**: `C:\UE_Projects\PatientSim56_v2\Config\PatientTemplate.json`

```json
{
    "template_version": "2.0",
    "description": "AI模擬患者システム - MetaHumanテンプレート設定",
    "last_updated": "2026-02-04",

    // 現在アクティブな患者ID
    "active_patient": "keiji",

    // 登録済みMetaHuman一覧
    "metahumans": {
        "keiji": {
            "blueprint_name": "BP_keiji",    // Blueprint名（大文字小文字注意）
            "display_name": "啓二（男性60歳・高齢者）",
            "profile_id": "keiji_default"     // 使用するプロファイルID
        },
        "takeshi": {
            "blueprint_name": "BP_takeshi77",
            "display_name": "タケシ（男性）",
            "profile_id": "takeshi_default"
        }
    },

    // 患者プロファイル（LLMプロンプト、音声設定など）
    "patient_profiles": [
        {
            "id": "keiji_default",
            "name": "啓二",
            "age": 60,
            "gender": "male",
            "condition": "軽い腰痛",
            "personality": "穏やか",
            "voice_speaker_id": 11,          // VOICEVOXスピーカーID
            "llm_prompt": "あなたは入院中の60歳男性患者です..."
        }
    ],

    // システム共通設定
    "system_config": {
        "voicevox_url": "http://localhost:50021",
        "ollama_url": "http://localhost:11434",
        "llm_model": "hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF:latest",
        "wav_output_path": "C:/UE_Projects/PatientSim56/Saved/patient_response.wav",
        "a2f_provider": "LocalA2F-Mark"
    }
}
```

### 8.2 Blueprint名の注意点

**重要**: Blueprint名は大文字小文字を区別します。

- `BP_Keiji` と `BP_keiji` は**別物**として扱われる
- PatientTemplate.jsonの`blueprint_name`と、実際のBlueprint名が完全一致している必要がある
- UE5でリネームした場合は、設定ファイルも更新すること

---

## 9. トラブルシューティング

### 9.1 よくある問題と解決策

| 問題 | 原因 | 解決策 |
|------|------|--------|
| リップシンクが動かない | ACEコンポーネントのAuto Activate=OFF | ONに変更 |
| リップシンクが動かない | 変数のInstance Editable=OFF | 4変数全てONに変更 |
| リップシンクが動かない | On Animation Endedが紐づいていない | 再紐づけ（Step 5参照） |
| リップシンクが動かない | PendingWavPathが空のまま | Blueprint名の大文字小文字確認 |
| 「cannot be edited on instances」エラー | Instance Editable=OFF | 変数のInstance EditableをONに |
| MetaHumanが見つからない | Blueprint名の不一致 | PatientTemplate.jsonを確認 |
| UE5に接続できない | Python Remote Execution無効 | Project Settingsで有効化 |
| ACEコンポーネントが「TRASH_...」 | コンポーネント作成失敗 | 手動で削除→再追加 |

### 9.2 デバッグ方法

**Python経由で状態確認:**
```python
import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.6\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python')
import remote_execution as re
import time

remote = re.RemoteExecution()
remote.start()
time.sleep(2)
remote.open_command_connection(remote.remote_nodes[0]['node_id'])

result = remote.run_command('''
import unreal
editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
game_world = editor_subsystem.get_game_world()
actors = unreal.GameplayStatics.get_all_actors_of_class(game_world, unreal.Actor)
for a in actors:
    if "keiji" in a.get_name().lower():
        print(f"Actor: {a.get_name()}")
        print(f"IsReady: {a.get_editor_property('IsReady')}")
        print(f"PendingWavPath: {a.get_editor_property('PendingWavPath')}")
        comps = a.get_components_by_class(unreal.ACEAudioCurveSourceComponent)
        for c in comps:
            print(f"ACE: {c.get_name()}, auto_activate={c.auto_activate}, is_active={c.is_active()}")
''', unattended=True)
print(result)
remote.stop()
```

---

## 10. 今回の作業記録（2026-02-04）

### 10.1 実施した作業

#### 目標
BP_Keiji（高齢者MetaHuman）にリップシンク機能を追加

#### 作業内容

| 順序 | 作業 | 方法 | 結果 |
|------|------|------|------|
| 1 | ACEAudioCurveSourceComponent追加 | MCP Python API | △ 追加されたがTRASH_状態 |
| 2 | Blueprint変数4つ追加 | MCP Python API | △ 追加されたがInstance Editable=OFF |
| 3 | Event Graphコピー | 手動（BP_takeshi77からコピペ） | ○ 成功 |
| 4 | On Animation Ended再紐づけ | 手動 | ○ 成功 |
| 5 | ACEコンポーネント再作成 | 手動 | ○ 成功 |
| 6 | Instance Editable有効化 | 手動 | ○ 成功 |
| 7 | Blueprint名修正 | 設定ファイル編集 | ○ 成功 |

#### 発生した問題と教訓

| 問題 | 原因 | 教訓 |
|------|------|------|
| ACEコンポーネントが「TRASH_」状態 | MCP Python APIでの作成が不完全 | **手動で作成すべき** |
| auto_activate=FALSE | MCP Python APIで設定漏れ | **手動で確認・設定すべき** |
| Instance Editable=OFF | MCP Python APIで設定不可 | **手動で設定必須** |
| Blueprint名の大文字小文字不一致 | リネーム時の確認漏れ | **設定ファイルと実際の名前を照合** |
| On Animation Endedが機能しない | コピペ元のコンポーネント参照のまま | **コピペ後に必ず再紐づけ** |

### 10.2 結論

**MCP Python APIでできること:**
- 変数の追加（ただしInstance Editableは手動設定必要）
- 簡単なプロパティ変更

**手動で行うべきこと:**
- ACEAudioCurveSourceComponentの追加
- Auto Activateの設定
- Instance Editableの設定
- Event Graphの作成/コピー
- On Animation Endedの紐づけ

**推奨ワークフロー:**
1. MetaHumanインポート（Quixel Bridge）
2. 全てのBlueprint設定を**UE5エディタで手動実施**
3. 設定ファイルのみスクリプトで管理

---

## 付録: VOICEVOXスピーカーID一覧（参考）

| ID | キャラクター | 性別 | 推奨用途 |
|----|------------|------|---------|
| 0 | 四国めたん（あまあま） | 女性 | - |
| 2 | 四国めたん（ノーマル） | 女性 | - |
| 8 | 春日部つむぎ | 女性 | 看護師 |
| 11 | 玄野武宏（ノーマル） | 男性 | 男性患者 |
| 13 | 青山龍星 | 男性 | - |

---

*最終更新: 2026-02-04*
*作成者: Claude AI (Opus 4.5)*
