# COPD教材 リップシンク動画生成 - RTX 4090引き継ぎ資料

**作成日**: 2026年1月8日
**対象環境**: Windows PC + RTX 4090
**目的**: 残り66個のリップシンク動画を生成する

---

## 1. 概要

### プロジェクト状況

| 項目 | 数量 |
|-----|------|
| 総セリフ数 | 81個 |
| リップシンク対象 | 71個 |
| 完了済み | 5個（シーン2） |
| **未処理** | **66個** |
| スキップ | 10個（ナレーション・心の声） |

### 処理時間見積もり

| 環境 | 1ファイル | 全66ファイル |
|-----|----------|-------------|
| Mac M4 Pro | 約10分 | 約11時間 |
| **RTX 4090** | **約1分** | **約1時間** |

---

## 2. パッケージ内容

```
copd_video_package/
├── README_RTX4090.md          # この資料
├── TASK_LIST.md               # 詳細タスクリスト
├── generate_all.sh            # Linux/Mac用バッチスクリプト
├── generate_all.bat           # Windows用バッチスクリプト
├── generate_all.py            # Python版バッチスクリプト（推奨）
├── audio/                     # 音声ファイル（必要なもののみ）
├── characters/                # キャラクター画像
│   ├── kazuo_expressions/
│   ├── ichiko_expressions/
│   ├── yamada_expressions/
│   ├── doctor_expressions/
│   ├── pharmacist_expressions/
│   └── sato_expressions/
└── videos/                    # 生成済み動画（5個）+ 出力先
```

---

## 3. セットアップ手順（RTX 4090 Windows）

### 3.1 前提条件

- Windows 10/11
- NVIDIA RTX 4090
- CUDA 11.8以上
- Python 3.9〜3.11
- Git

### 3.2 SadTalkerインストール

```powershell
# 1. SadTalkerをクローン
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker

# 2. Python仮想環境作成
python -m venv venv
.\venv\Scripts\activate

# 3. PyTorch (CUDA版) インストール
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 4. 依存パッケージインストール
pip install -r requirements.txt
pip install "numpy<2"

# 5. ffmpeg インストール（chocolateyの場合）
choco install ffmpeg
```

### 3.3 モデルダウンロード

```powershell
# checkpointsフォルダ作成
mkdir checkpoints
mkdir gfpgan\weights

# SadTalkerモデル（約1.5GB）
# 以下のURLから手動でダウンロードしてcheckpoints/に配置
# https://github.com/OpenTalker/SadTalker/releases/tag/v0.0.2-rc
# - mapping_00109-model.pth.tar
# - mapping_00229-model.pth.tar
# - SadTalker_V0.0.2_256.safetensors
# - SadTalker_V0.0.2_512.safetensors

# GFPGANモデル
# https://github.com/xinntao/facexlib/releases から
# - alignment_WFLW_4HG.pth → gfpgan/weights/
# - detection_Resnet50_Final.pth → gfpgan/weights/
# - parsing_parsenet.pth → gfpgan/weights/

# https://github.com/TencentARC/GFPGAN/releases から
# - GFPGANv1.4.pth → gfpgan/weights/
```

### 3.4 データ配置

```powershell
# copd_video_packageの中身をSadTalkerと同じ場所に配置
# 例：
# C:\Users\username\SadTalker\
# C:\Users\username\copd_video_package\audio\
# C:\Users\username\copd_video_package\characters\
# C:\Users\username\copd_video_package\videos\
```

---

## 4. 動画生成の実行

### 4.1 推奨：Python版スクリプト

```powershell
cd C:\Users\username\SadTalker
.\venv\Scripts\activate

# copd_video_packageのパスを指定して実行
python ..\copd_video_package\generate_all.py --sadtalker_dir . --data_dir ..\copd_video_package
```

### 4.2 個別実行（テスト用）

```powershell
python inference.py ^
  --driven_audio ..\copd_video_package\audio\s03_01.mp3 ^
  --source_image ..\copd_video_package\characters\kazuo_expressions\kazuo_general_05_neutral.png ^
  --result_dir ..\copd_video_package\videos ^
  --still --preprocess full
```

### 4.3 高品質オプション（時間に余裕がある場合）

```powershell
python inference.py ^
  --driven_audio [音声] ^
  --source_image [画像] ^
  --result_dir [出力先] ^
  --still --preprocess full ^
  --enhancer gfpgan ^
  --size 512
```

---

## 5. キャラクター別画像マッピング

| キャラクター | 画像パス |
|------------|---------|
| 一男（kazuo） | `characters/kazuo_expressions/kazuo_general_05_neutral.png` |
| 市子（ichiko） | `characters/ichiko_expressions/ichiko_05_neutral.png` |
| 山田看護師（yamada） | `characters/yamada_expressions/yamada_05_neutral.png` |
| 主治医（doctor） | `characters/doctor_expressions/doctor_05_neutral.png` |
| 薬剤師（pharmacist） | `characters/pharmacist_expressions/pharmacist_05_neutral.png` |
| 佐藤ケアマネ（sato） | `characters/sato_expressions/sato_05_neutral.png` |

---

## 6. 出力ファイル命名規則

生成される動画ファイル名：
```
{カットID}_{キャラクター名}.mp4

例：
s03_01_kazuo.mp4
s03_02_ichiko.mp4
s04_01_yamada.mp4
```

---

## 7. H.264変換（重要）

SadTalkerの出力はmpeg4コーデックのため、ブラウザで再生できない場合があります。
生成後、以下のコマンドでH.264に変換してください：

```powershell
# 単一ファイル
ffmpeg -y -i input.mp4 -c:v libx264 -c:a aac -movflags +faststart output.mp4

# 一括変換（PowerShell）
Get-ChildItem *.mp4 | ForEach-Object {
    $output = $_.BaseName + "_h264.mp4"
    ffmpeg -y -i $_.FullName -c:v libx264 -c:a aac -movflags +faststart $output
    Move-Item $output $_.FullName -Force
}
```

---

## 8. トラブルシューティング

### CUDA関連エラー

```powershell
# CUDAバージョン確認
nvidia-smi

# PyTorchのCUDA確認
python -c "import torch; print(torch.cuda.is_available())"
```

### メモリ不足

`--size 256` オプションを使用して解像度を下げる

### NumPy互換性エラー

```powershell
pip install "numpy<2"
```

### torchvision API変更エラー

`venv\Lib\site-packages\basicsr\data\degradations.py` を編集：

```python
# 修正前
from torchvision.transforms.functional_tensor import rgb_to_grayscale

# 修正後
try:
    from torchvision.transforms.functional_tensor import rgb_to_grayscale
except ImportError:
    from torchvision.transforms.functional import rgb_to_grayscale
```

---

## 9. 完了後の作業

1. 生成された動画（66個）をH.264に変換
2. `videos/` フォルダをZIP圧縮
3. 元のMacに転送
4. `copd_project/videos/` に配置
5. HTMLファイルで動作確認

---

## 10. 連絡先・参考

- **SadTalker公式**: https://github.com/OpenTalker/SadTalker
- **GFPGAN**: https://github.com/TencentARC/GFPGAN
- **プロジェクト詳細**: `docs/README.md` を参照

---

## 更新履歴

| 日付 | 内容 |
|-----|------|
| 2026/01/08 | RTX 4090用引き継ぎ資料作成 |
