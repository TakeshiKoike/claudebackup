# LLM-jp-Moshi-v1 Mac セットアップ記録

## 概要
- **モデル**: LLM-jp-Moshi-v1 (国立情報学研究所 NII)
- **公式**: https://www.nii.ac.jp/news/release/2026/0225.html
- **HuggingFace**: https://huggingface.co/llm-jp/llm-jp-moshi-v1
- **GitHub**: https://github.com/llm-jp/llm-jp-moshi
- **ライセンス**: Apache 2.0 (商用利用可)
- **日付**: 2026-02-27

## モデル仕様
- 日本語フルデュプレックス音声対話モデル (世界初の商用可能版)
- 7Bパラメータ、ベース: Kyutai Moshi
- 学習データ: J-CHAT (ポッドキャスト69,000時間) + LLM-jp-Zoom1 (Zoom対話1,000時間)
- 相槌・間合いを学習済み
- 試作段階 (応答が不自然な場合あり)

## 公式要件
- **24GB以上VRAM搭載のLinux GPUマシン**
- **MacOS非対応** (公式)

## Mac (M4 Pro/48GB) での動作方法

### 方針
公式にはMac非対応だが、PyTorch版 `moshi` パッケージに `--device mps` オプションがあり、2箇所のパッチで動作可能。

### 1. 環境構築

```bash
python3.12 -m venv ~/moshi-env
source ~/moshi-env/bin/activate
pip install -U pip
pip install "moshi<=0.2.2" "sphn==0.1.12"
```

### 2. モデルダウンロード

```bash
huggingface-cli download llm-jp/llm-jp-moshi-v1 --local-dir ~/moshi-model
```

ファイル構成 (約14GB):
```
moshi-model/
├── model.safetensors              # 14GB (メインモデル)
├── moshi_lm_kwargs.json           # モデル設定
├── tokenizer_spm_32k_3.model      # テキストトークナイザ (日本語SentencePiece)
├── tokenizer-e351c8d8-checkpoint125.safetensors  # 音声トークナイザ (Mimi)
├── README.md
└── README-en.md
```

### 3. パッチ (2箇所)

#### パッチ1: `moshi/server.py` — torch.cuda.synchronize() の条件化

```python
# 変更前 (warmup関数内):
        torch.cuda.synchronize()

# 変更後:
        if torch.cuda.is_available():
            torch.cuda.synchronize()
```

#### パッチ2: `moshi/utils/quantize.py` — bitsandbytes import の遅延化

`bitsandbytes` はCUDA専用ライブラリで Mac にインストール不可。
非量子化モデルでは実際には使わないので、import を量子化パス内に移動。

```python
# linear() 関数 — import を is_quantized ブロック内に移動
def linear(module, x, name='weight'):
    if is_quantized(module, name):
        import bitsandbytes as bnb  # ← ここに移動
        # ... bnb使用コード
    else:
        return nn.functional.linear(x, getattr(module, name))

# multi_linear() 関数 — 同様にトップレベルの import を削除し、else ブロック内に移動
def multi_linear(...):
    # トップレベルの `import bitsandbytes as bnb` を削除
    ...
    for t in range(T):
        if weight_scb is None:
            y = nn.functional.linear(x[:, t], weight[linear_index])
        else:
            import bitsandbytes as bnb  # ← ここに移動
            # ... bnb使用コード
```

### 4. 起動

```bash
source ~/moshi-env/bin/activate
PYTORCH_ENABLE_MPS_FALLBACK=1 python3 -m moshi.server \
    --hf-repo llm-jp/llm-jp-moshi-v1 \
    --device mps \
    --half
```

- `PYTORCH_ENABLE_MPS_FALLBACK=1`: MPS未実装のオペレータ (`aten::index_copy.out`) をCPUフォールバック
- `--device mps`: Apple Metal Performance Shaders 使用
- `--half`: float16 (bfloat16の代わり)

### 5. アクセス

ブラウザで http://localhost:8998

## 注意事項
- イヤホン/ヘッドホン推奨 (エコー防止)
- `aten::index_copy.out` がMPS未実装のためCPUフォールバックが発生 → 速度低下
- メモリ使用量: 約2GB〜 (推論開始で増加)
- warmup に数分かかる

## MLX版について
`moshi_mlx` パッケージ (Kyutai公式Mac対応) も試したが、LLM-jp-Moshi-v1の重み名がMLX版のモデル定義と異なり (PyTorch形式 vs MLX形式)、257パラメータが不一致でロード失敗。重みのリネーム変換が必要。

## 別アプローチ: MLX版で動かす場合 (未完)
```bash
pip install moshi_mlx
python3 -m moshi_mlx.local --hf-repo llm-jp/llm-jp-moshi-v1
# → ValueError: 257 parameters not in model (重み名不一致)
```
重み名マッピングを作成すれば動く可能性あり。今後の課題。

## モデル設定 (moshi_lm_kwargs.json)
```json
{
  "dim": 4096,
  "text_card": 32000,
  "n_q": 16,
  "dep_q": 8,
  "card": 2048,
  "num_heads": 32,
  "num_layers": 32,
  "hidden_scale": 4.125,
  "gating": "silu",
  "norm": "rms_norm_f32",
  "positional_embedding": "rope",
  "depformer_dim": 1024,
  "depformer_num_heads": 16,
  "depformer_num_layers": 6
}
```
