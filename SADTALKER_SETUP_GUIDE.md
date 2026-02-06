# SadTalker セットアップ・運用ガイド

## 概要

このドキュメントは、COPDビジュアルノベルプロジェクトにおける口パク（リップシンク）動画生成のためのSadTalkerセットアップと運用方法をまとめたものです。

**作成日**: 2026年1月6日
**最終更新**: 2026年1月7日
**環境**: Mac M4 Pro (48GB RAM)
**バックアップ用途**: 引き継ぎ・継続作業用

---

## 1. 環境構成

### ディレクトリ構成

```
/Users/takeshikoike2025/Downloads/
├── SadTalker/                    # SadTalker本体
│   ├── venv/                     # Python仮想環境
│   ├── checkpoints/              # 学習済みモデル
│   ├── gfpgan/weights/           # 顔補正モデル
│   ├── results/                  # 生成された動画
│   └── inference.py              # 推論スクリプト
│
└── copd_project/copd_project/    # COPDプロジェクト
    ├── audio/                    # 音声ファイル (93個)
    ├── characters/
    │   ├── kazuo_expressions/    # 一雄キャラ画像 (18個)
    │   └── doctor_expressions/   # 医師キャラ画像 (9個)
    ├── videos/                   # 生成された口パク動画
    └── copd_visual_novel_v2.28_video.html
```

### インストール済みコンポーネント

| コンポーネント | バージョン/状態 |
|--------------|----------------|
| Python | 3.9 (venv) |
| PyTorch | 2.8.0 (MPS対応) |
| torchvision | 0.17.2 |
| numpy | 1.26.4 |
| SadTalker | v0.0.2-rc |
| GFPGAN | v1.4 |

---

## 2. 重要：リップシンクが必要なセリフの判断

### リップシンクが必要
- キャラクターが実際に声を出して話すセリフ
- 医師、患者（一雄）、看護師などの会話

### リップシンク不要
- **ナレーション**（女性の声でストーリー説明）
- **心の声**（`"type": "thought"`）- 口を動かさない内心の独白

### 話者の確認方法

HTMLファイルで確認：
```bash
grep '"speaker":' copd_visual_novel_v2.28_video.html
```

話者の種類：
- `"speaker": "narration"` → ナレーション（リップシンク不要）
- `"speaker": "kazuo"` → 一雄のセリフ
- `"speaker": "doctor"` → 医師のセリフ
- `"type": "thought"` → 心の声（リップシンク不要）

---

## 3. 一雄のセリフ一覧（リップシンク対象：30個）

```
s02_02* s02_04  s02_06
s03_01  s03_03  s03_05
s04_02  s04_06
s05_04  s05_06
s06_02  s06_05  s06_07
s07_01  s07_03  s07_06
s08_02  s08_04  s08_07
s09_05
s10_02  s10_04  s10_06  s10_08
s11_02  s11_05  s11_07
s12_02  s12_06
s13_04
```
※ s02_02は心の声のためスキップ

---

## 4. 基本的な使い方

### 動画生成コマンド

```bash
cd /Users/takeshikoike2025/Downloads/SadTalker
source venv/bin/activate

python inference.py \
  --driven_audio [音声ファイルパス] \
  --source_image [画像ファイルパス] \
  --result_dir /Users/takeshikoike2025/Downloads/copd_project/copd_project/videos \
  --still \
  --preprocess full
```

### 実行例：一雄のセリフ

```bash
python inference.py \
  --driven_audio /Users/takeshikoike2025/Downloads/copd_project/copd_project/audio/s02_04.mp3 \
  --source_image /Users/takeshikoike2025/Downloads/copd_project/copd_project/characters/kazuo_expressions/kazuo_general_05_neutral.png \
  --result_dir /Users/takeshikoike2025/Downloads/copd_project/copd_project/videos \
  --still --preprocess full
```

### 実行例：医師のセリフ

```bash
python inference.py \
  --driven_audio /Users/takeshikoike2025/Downloads/copd_project/copd_project/audio/s02_01.mp3 \
  --source_image /Users/takeshikoike2025/Downloads/copd_project/copd_project/characters/doctor_expressions/doctor_05_neutral.png \
  --result_dir /Users/takeshikoike2025/Downloads/copd_project/copd_project/videos \
  --still --preprocess full
```

### 主要オプション

| オプション | 説明 |
|-----------|------|
| `--driven_audio` | 入力音声ファイル (mp3, wav) |
| `--source_image` | 入力画像ファイル (png, jpg) |
| `--result_dir` | 出力先ディレクトリ |
| `--still` | 頭の動きを抑制（静止画風） |
| `--preprocess full` | 顔全体を処理 |
| `--enhancer gfpgan` | 顔の品質向上（オプション） |
| `--size 256` または `512` | 出力解像度 |

---

## 5. キャラクター画像一覧

### 一雄（患者）

場所: `characters/kazuo_expressions/`

| ファイル名 | 表情 |
|-----------|------|
| kazuo_general_01_smile.png | 笑顔 |
| kazuo_general_02_worried.png | 心配 |
| kazuo_general_03_surprised.png | 驚き |
| kazuo_general_04_thinking.png | 考え中 |
| kazuo_general_05_neutral.png | 普通 |
| kazuo_general_06_relieved.png | 安堵 |
| kazuo_general_07_serious.png | 真剣 |
| kazuo_general_08_confused.png | 困惑 |
| kazuo_general_09_grateful.png | 感謝 |
| kazuo_medical_01_breathless.png | 息切れ |
| kazuo_medical_02_dyspnea.png | 呼吸困難 |
| kazuo_medical_03_pursed_lip.png | 口すぼめ呼吸 |
| kazuo_medical_04_cyanosis.png | チアノーゼ |
| kazuo_medical_05_neutral.png | 医療シーン普通 |
| kazuo_medical_06_fatigue.png | 疲労 |
| kazuo_medical_07_coughing.png | 咳 |
| kazuo_medical_08_after_cough.png | 咳の後 |
| kazuo_medical_09_recovering.png | 回復中 |

### 医師

場所: `characters/doctor_expressions/`

| ファイル名 | 表情 |
|-----------|------|
| doctor_01_smile.png | 笑顔 |
| doctor_02_worried.png | 心配 |
| doctor_03_surprised.png | 驚き |
| doctor_04_thinking.png | 考え中 |
| doctor_05_neutral.png | 普通 |
| doctor_06_relieved.png | 安堵 |
| doctor_07_serious.png | 真剣 |
| doctor_08_confused.png | 困惑 |
| doctor_09_grateful.png | 感謝 |

---

## 6. 処理進捗

### 完了済み

| シーン | ファイル | 話者 | 状態 |
|-------|---------|------|------|
| シーン2 | s02_01.mp4 | 医師 | 完了 |
| シーン2 | s02_02 | 一雄（心の声） | スキップ |
| シーン2 | s02_03.mp4 | 医師 | 完了 |
| シーン2 | s02_04.mp4 | 一雄 | 完了 |
| シーン2 | s02_05.mp4 | 医師 | 完了 |
| シーン2 | s02_06.mp4 | 一雄 | 完了 |

### 未処理

- シーン3〜13の会話セリフ（約25ファイル）

---

## 7. 処理性能

### Mac M4 Pro での実測値

| 項目 | 値 |
|-----|-----|
| 5秒音声の処理時間 | 約8〜10分 |
| 出力解像度 | 256x256 |
| フレームレート | 25 fps |

### 処理時間見積もり

| 環境 | 1ファイル | 全30ファイル |
|-----|----------|-------------|
| Mac M4 Pro | 約10分 | 約5時間 |
| RTX 4090 | 約1分 | 約30分 |

---

## 8. セットアップ時に解決した問題

### 問題1: NumPy 2.0 互換性

**症状**: `np.VisibleDeprecationWarning` が存在しないエラー

**解決**: NumPyをダウングレード
```bash
pip install "numpy<2"
```

### 問題2: torchvision API変更

**症状**: `torchvision.transforms.functional_tensor` インポートエラー

**解決**: ファイル修正
```
ファイル: venv/lib/python3.9/site-packages/basicsr/data/degradations.py
```
```python
# 修正前
from torchvision.transforms.functional_tensor import rgb_to_grayscale

# 修正後
try:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale
except ImportError:
    from torchvision.transforms.functional import rgb_to_grayscale
```

### 問題3: np.float 廃止

**症状**: `np.float` は NumPy 1.20 以降で廃止

**解決**: ファイル修正
```
ファイル: src/face3d/util/my_awing_arch.py (18行目)
```
```python
# 修正前
preds = preds.astype(np.float, copy=False)

# 修正後
preds = preds.astype(np.float64, copy=False)
```

### 問題4: NumPy配列の形状問題

**症状**: inhomogeneous shape エラー

**解決**: ファイル修正
```
ファイル: src/face3d/util/preprocess.py (101行目)
```
```python
# 修正前
trans_params = np.array([w0, h0, s, t[0], t[1]])

# 修正後
trans_params = np.array([w0, h0, s, float(t[0]), float(t[1])])
```

---

## 9. 新規環境での再セットアップ手順

別のマシンで環境を構築する場合の手順：

```bash
# 1. SadTalkerをクローン
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker

# 2. Python仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 3. 依存パッケージインストール
pip install torch torchvision torchaudio
pip install -r requirements.txt
pip install "numpy<2"

# 4. モデルダウンロード
mkdir -p checkpoints gfpgan/weights

# SadTalkerモデル
curl -L -o checkpoints/mapping_00109-model.pth.tar \
  https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar
curl -L -o checkpoints/mapping_00229-model.pth.tar \
  https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar
curl -L -o checkpoints/SadTalker_V0.0.2_256.safetensors \
  https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors
curl -L -o checkpoints/SadTalker_V0.0.2_512.safetensors \
  https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors

# GFPGANモデル
curl -L -o gfpgan/weights/alignment_WFLW_4HG.pth \
  https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth
curl -L -o gfpgan/weights/detection_Resnet50_Final.pth \
  https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth
curl -L -o gfpgan/weights/GFPGANv1.4.pth \
  https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth
curl -L -o gfpgan/weights/parsing_parsenet.pth \
  https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth

# 5. 互換性修正（上記「解決した問題」参照）を適用
```

---

## 10. トラブルシューティング

### 仮想環境が見つからない場合

```bash
cd /Users/takeshikoike2025/Downloads/SadTalker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### CUDA/MPS関連エラー

Mac では MPS (Metal Performance Shaders) を使用。エラーが出た場合：
```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

### メモリ不足エラー

`--size 256` オプションで解像度を下げる

---

## 11. 連絡先・参考リンク

- **SadTalker公式**: https://github.com/OpenTalker/SadTalker
- **GFPGAN**: https://github.com/TencentARC/GFPGAN

---

## 12. 更新履歴

| 日付 | 内容 |
|-----|------|
| 2026/01/06 | 初版作成。Mac M4 Proでの環境構築完了。テスト動画生成成功。 |
| 2026/01/07 | シーン2（医師と患者）のリップシンク動画生成完了。ナレーション・心の声はスキップすることを明記。キャラクター画像一覧を正確なファイル名に修正。 |
