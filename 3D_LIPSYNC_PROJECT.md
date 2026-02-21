# 3D LipSync Patient Simulation Project

## プロジェクト概要
看護教育研究用の3Dリップシンク患者シミュレーションシステム

### 患者設定
- **名前**: 田中一男
- **年齢**: 72歳男性
- **疾患**: COPD（慢性閉塞性肺疾患）
- **性格**: 穏やかで協力的、息が切れやすいので短い文で話す

### 技術スタック
- **3D Rendering**: Three.js (r128)
- **TTS**: VOICEVOX (Speaker ID: 11 - 玄野武宏)
- **LLM**: Ollama + schroneko/llama-3.1-swallow-8b-instruct-v0.1 (日本語特化)
- **3D Modeling**: Blender + Blender MCP
- **Model Format**: GLB (glTF Binary)

---

## 経過記録 (2026年1月〜2月)

### Phase 1: 基本システム構築
- Three.jsベースの3Dビューワー作成
- VOICEVOXとの連携（音素タイミング取得）
- Ollamaとの連携（患者役AIレスポンス）
- リップシンクの基本実装（あいうえお5母音）

### Phase 2: 3Dモデル試行錯誤

#### 試行1: Blenderで手作りモデル (simple_face.glb)
- 頭部、目、眉毛、鼻、口、耳、髪を作成
- シェイプキー: mouth_a, mouth_i, mouth_u, mouth_e, mouth_o
- **結果**: 機能するが見た目がシンプルすぎる

#### 試行2: Hyper3D Rodin (AI生成モデル)
- リアルな3Dモデルを生成
- **問題**: 口が閉じた/微笑んだ状態で固定されており、リップシンク用のトポロジーがない
- 手動でシェイプキーを追加しようとしたが、間違った頂点を選択
- ユーザーフィードバック: 「ひたいがリップシンクしています」「鼻のあたりのリップシンク」
- **結論**: Hyper3Dモデルはリップシンクに不向き

#### 試行3: VRoid Studio
- アニメスタイルのみ対応
- 研究用途には不適切と判断

#### 試行4: Ready Player Me
- サービス終了済み

#### 試行5: Hunyuan3D
- オンライン版: 無料（20生成/日制限）
- ローカル版: pymeshlabの依存関係でMacインストール失敗
- 4090 GPUのPCで後日テスト予定

#### 試行6: Sketchfab API連携
- API接続成功（ユーザー: kokekun5）
- ブレンドシェイプ付きモデルを検索
- **問題**: FBXダウンロード時にシェイプキーが失われる

#### 試行7: Facial Animation Model (Sketchfab)
- モデル: "Facial animation of a sexy girl" (UID: 51c1d536d7b24f8e910e81fb50198193)
- **成功**: 149個のシェイプキーが保持された
- シェイプキー名は汎用的（target_0, target_1, ...）
- **問題**: 裸のモデルで看護教育には不適切

---

## 技術的発見

### シェイプキー分析手法

Sketchfabモデルのシェイプキーは汎用名（target_X）のため、手動で機能を特定する必要がある。

#### 分析コード例
```python
import bpy
from mathutils import Vector

obj = bpy.data.objects.get('1')
basis = obj.data.shape_keys.key_blocks['Basis']

# 口エリアの変位を分析
for kb in obj.data.shape_keys.key_blocks[1:]:
    mouth_disp = 0
    for i in range(len(basis.data)):
        b_co = basis.data[i].co
        t_co = kb.data[i].co
        # 下顔面（Z < -4）、前面（Y < -160）の頂点をチェック
        if b_co.z < -4 and b_co.y < -160:
            disp = (t_co - b_co).length
            if disp > 0.05:
                mouth_disp += disp
```

### 母音シェイプキーマッピング

Sketchfabモデルで発見した対応関係：

| 母音 | 動き | 対応シェイプキー |
|------|------|------------------|
| あ (a) | 顎を大きく開く | target_3 (0.8) + target_64/65 (0.3) |
| い (i) | 口を横に広げる（笑顔） | target_66/67 (0.8) |
| う (u) | 口をすぼめる（前に突き出す） | target_108/109 (0.7) |
| え (e) | 中程度に開く＋少し横 | target_64/65 (0.5) + target_66/67 (0.3) |
| お (o) | 丸く突き出す | target_123 (0.8) + target_3 (0.2) |

### 組み合わせシェイプキー作成コード

```python
import bpy
import numpy as np

vowel_combos = {
    'mouth_a': [('target_3', 0.8), ('target_64', 0.3), ('target_65', 0.3)],
    'mouth_i': [('target_66', 0.8), ('target_67', 0.8)],
    'mouth_u': [('target_108', 0.7), ('target_109', 0.7)],
    'mouth_e': [('target_64', 0.5), ('target_65', 0.5), ('target_66', 0.3), ('target_67', 0.3)],
    'mouth_o': [('target_123', 0.8), ('target_3', 0.2)]
}

for vowel_name, combo in vowel_combos.items():
    new_key = obj.shape_key_add(name=vowel_name, from_mix=False)
    basis_coords = np.array([v.co[:] for v in basis.data])
    combined = basis_coords.copy()

    for src_name, weight in combo:
        src_key = obj.data.shape_keys.key_blocks.get(src_name)
        if src_key:
            src_coords = np.array([v.co[:] for v in src_key.data])
            delta = src_coords - basis_coords
            combined += delta * weight

    for i, co in enumerate(combined):
        new_key.data[i].co = co
```

---

## HTMLビューワーコード

### リップシンク同期の核心部分

```javascript
function vowelFromPhoneme(p) {
    p = p.toLowerCase();
    if (p === 'a' || p.endsWith('a')) return 'a';
    if (p === 'i' || p.endsWith('i')) return 'i';
    if (p === 'u' || p.endsWith('u')) return 'u';
    if (p === 'e' || p.endsWith('e')) return 'e';
    if (p === 'o' || p.endsWith('o')) return 'o';
    return null;
}

async function playWithLipSync(audioBuffer, phonemes) {
    const decoded = await audioCtx.decodeAudioData(audioBuffer.slice(0));
    const src = audioCtx.createBufferSource();
    src.buffer = decoded;
    src.connect(audioCtx.destination);

    const start = audioCtx.currentTime;
    src.start();

    let idx = 0;
    function update() {
        const elapsed = audioCtx.currentTime - start;
        while (idx < phonemes.length) {
            const ph = phonemes[idx];
            if (elapsed < ph.s) { setMouth(null); break; }
            if (elapsed < ph.s + ph.d) { setMouth(vowelFromPhoneme(ph.p)); break; }
            idx++;
        }
        if (idx >= phonemes.length) setMouth(null);
        if (elapsed < decoded.duration) requestAnimationFrame(update);
    }
    update();
}
```

---

## 今後の課題

1. **適切な3Dモデルの確保**
   - 服を着た男性患者モデルが必要
   - リップシンク対応（シェイプキー/ブレンドシェイプ付き）
   - リアルな見た目（研究用途）

2. **検討中のオプション**
   - Hunyuan3Dをローカルで実行（4090 GPUのPC）
   - 別のSketchfabモデルを探す（服を着た男性）
   - simple_face.glbをベースに改良

3. **ユーザーの要件**
   - 「リップシンク優先、リアルさは二の次」
   - 「妥協はしない（研究なので）」
   - 「譲歩するような提案はするな」

---

## ファイル一覧

| ファイル | 説明 |
|----------|------|
| `test_patient_lipsync.html` | シェイプキーテスト用HTML |
| `lipsync_3d_v7.html` | リップシンクv7（simple_face.glb用） |
| `lipsync_3d_v8.html` | リップシンクv8（患者情報追加） |
| `simple_face.glb` | Blender作成シンプル顔モデル |
| `patient_tanaka_lipsync.glb` | 各種エクスポート試行 |

---

## 更新履歴

- **2026-01-21**: プロジェクト開始
- **2026-01-25**: バックアップ作成 (3d_lipsync_project_backup_20260125_164603)
- **2026-01-30**: v7, v8 HTML作成
- **2026-02-05**: Sketchfabモデル分析、シェイプキーマッピング完了
