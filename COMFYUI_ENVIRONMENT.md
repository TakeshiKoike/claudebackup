# ComfyUI - AI画像/動画生成環境

## 概要
看護教育コンテンツ用AI画像・動画生成環境

## 環境
| 項目 | 値 |
|------|-----|
| パス | `/Users/takeshikoike2025/comfyUI/` |
| 出力数 | 575枚 (1.4GB) |
| モデル容量 | 89GB+ |
| 最終使用 | 2026年2月5日 |

---

## モデル構成

| カテゴリ | サイズ | 用途 |
|---------|-------|------|
| diffusion_models/ | 41GB | Flux 1.0, QWen Image Edit (t2i/i2i) |
| text_encoders/ | 19GB | t5xxl, CLIP, QWen-2.5-VL |
| checkpoints/ | 12GB | Stable Audio (7.2GB), ACE (4.5GB) |
| clip_vision/ | 817MB | sigclip_vision |
| loras/ | 810MB | QWen Image Edit Lightning |
| vae/ | 562MB | QWen VAE, AE |
| style_models/ | 123MB | Flux 1.0 Redux |

## ワークフロー (user/内 23 JSONファイル)

### 看護/医療系 (WAN2.6 t2v)
- 小児api_wan2_6_t2v.json - 小児シナリオ
- 病院api_wan2_6_t2v.json - 病院シナリオ
- 検診api_wan2_6_t2v.json - 検診シナリオ
- 療養部屋api_wan2_6_t2v.json - 療養室
- 訪問検診api_wan2_6_t2v.json - 訪問検診
- ゴミ屋敷api_wan2_6_t2v.json - ゴミ屋敷

### t2i / i2i
- 2026.1.7FLUX1.json - Flux t2i
- 2026.1.7STAMP1.json - STAMP t2i
- 2026.1.3. zaitaku t2i.json - 在宅ケア
- 2026.1.8. kokushi 1 i2i.json - 国試画像
- 2026.1.7image_qwen_image_edit.json - 画像編集

### その他
- 2026.1.17 audio_stable_audio_example.json - 音声生成
- ICT manga.json - マンガ生成

## 用途
- 訪問看護ゲーム画像素材生成
- 看護国試ビジュアル化の画像生成
- 教育動画素材生成
