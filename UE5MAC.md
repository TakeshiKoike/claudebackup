# デジタル模擬患者プロジェクト - UE5 + MetaHuman (Mac版)

## 最終目標
看護教育用のリップシンク付きデジタル模擬患者を製作する

---

## 担当: 1番さん（Claude Code）

---

## Mac 環境情報

| 項目 | 値 |
|------|-----|
| プラットフォーム | macOS (Darwin 25.2.0) |
| チップ | Apple M4 Pro |
| メモリ | 48 GB |
| GPU | Apple Silicon (NVIDIA非対応) |
| UE インストール | `/Users/Shared/Epic Games/UE_5.6`, `/Users/Shared/Epic Games/UE_5.7` |

---

## 現在のプロジェクト

### MyProject3 ★現在使用
| 項目 | 値 |
|------|-----|
| パス | `/Users/takeshikoike2025/Documents/Unreal Projects/MyProject3` |
| エンジン | UE 5.6 |
| MCP | runreal/unreal-mcp |
| 有効プラグイン | LiveLink, LiveLinkControlRig, AppleARKitFaceSupport |
| MetaHuman | ✅ インポート済み (Keiji, takeshi77) |

---

## Mac版 進捗状況（2026-02-06）

### 環境構築
- [x] UE 5.6 インストール済み
- [x] UE 5.7 インストール済み
- [x] MyProject3 作成済み（UE 5.6）
- [x] LiveLink プラグイン有効化
- [x] LiveLinkControlRig プラグイン有効化
- [x] AppleARKitFaceSupport プラグイン有効化
- [x] Ollama v0.13.5 インストール済み（llama-3.1-swallow-8b, gemma2:9b, qwen2.5:14b）
- [x] VOICEVOX v0.25.1 起動確認済み (localhost:50021)
- [x] MCP 設定変更: flopperam版 → @runreal/unreal-mcp（プラグイン不要）
- [x] MCP 接続確認済み（UE 5.6.1 接続成功）
- [x] Python Remote Execution 有効化確認済み
- [x] MetaHuman インポート済み (Keiji, takeshi77)

### リップシンク
- [x] Mac対応リップシンク方式の選定 → **PyLiveLinkFace + VOICEVOX 音素解析**
- [x] MetaHuman ブレンドシェイプ調査 (ARKit 66ポーズ、CTRL_expressions_* カーブ)
- [x] PyLiveLinkFace インストール済み (UDP 11111 → UE5 LiveLink)
- [x] リップシンクスクリプト作成済み (`Scripts/lipsync_livelink.py`)
- [x] VOICEVOX 音素タイミング抽出動作確認済み
- [x] 日本語音素 → ARKit ブレンドシェイプ マッピング定義済み
- [ ] UE5 LiveLink パネルでソース検出確認
- [ ] MetaHuman (BP_Keiji) の LiveLink 接続設定
- [ ] リップシンク動作テスト（UE5上で口が動くことを確認）

---

## Mac版 リップシンク方式 ★決定

### ⚠️ NVIDIA ACE は Mac 非対応
PC版で使用していた NVIDIA ACE (Audio2Face) は CUDA/RTX GPU が必要なため Mac では使用不可。

### ★採用: PyLiveLinkFace + VOICEVOX 音素解析
- **方式**: VOICEVOX音素タイミング → ARKitブレンドシェイプ → PyLiveLinkFace(UDP) → UE5 LiveLink → MetaHuman Face_AnimBP
- **ライブラリ**: PyLiveLinkFace 0.1 (pip install pylivelinkface)
- **プロトコル**: UDP 11111 (Live Link Face バイナリ形式)
- **iOSデバイス不要**: Python から直接 ARKit 互換データを送信
- **スクリプト**: `Scripts/lipsync_livelink.py`

### パイプライン
```
テキスト → VOICEVOX (音声合成 + 音素タイミング)
  → Python 音素→ビゼーム変換 (日本語5母音+子音マッピング)
    → PyLiveLinkFace (ARKit 61ブレンドシェイプ バイナリエンコード)
      → UDP 11111 → UE5 LiveLink
        → Face_AnimBP → mh_arkit_mapping_pose → CTRL_expressions → MetaHuman 顔ボーン
```

### MetaHuman フェイシャル制御の仕組み
- Face_AnimBP が LiveLink から ARKit カーブ名 (JawOpen等) を受信
- mh_arkit_mapping_pose (PoseAsset) で ARKit → CTRL_expressions に変換
- CTRL_expressions カーブがフェイスの875ボーンを駆動
- **重要**: set_morph_target() は Face_AnimBP に影響しない（AnimBPが毎フレーム上書き）

### 不採用の選択肢
| 選択肢 | 理由 |
|--------|------|
| ARKit + LiveLink (iOS) | iOSデバイス必要、リアルタイムキャプチャ用 |
| OVRLipSync (Meta) | UE5互換性問題（PC版で断念済み） |
| クラウドAPI | レイテンシ、コスト |

---

## MCP 設定

### @runreal/unreal-mcp ★採用
| 項目 | 値 |
|------|-----|
| プロトコル | UDP マルチキャスト + Python Remote Execution |
| アドレス | 239.0.0.1:6766 |
| 設定 | `npx -y @runreal/unreal-mcp` |
| 必要設定 | UE5 で Python Remote Execution を有効化 |
| プラグイン | **不要** |
| 現在の状態 | ✅ 接続確認済み (UE 5.6.1) |

### flopperam/unreal-engine-mcp ❌断念
| 項目 | 値 |
|------|-----|
| 理由 | C++プラグイン必要、UE5.6 とBuildId不一致でコンパイル失敗 |
| 接続先 | TCP port 55557 |

---

## 旧プロジェクト（参考用）

### MyProject
| 項目 | 値 |
|------|-----|
| パス | `/Users/takeshikoike2025/Documents/Unreal Projects/MyProject` |

### MyProject2
| 項目 | 値 |
|------|-----|
| パス | `/Users/takeshikoike2025/Documents/Unreal Projects/MyProject2` |

---

## 既存リソース（Mac版）

| 項目 | 値 |
|------|-----|
| LLM | Ollama v0.13.5 ✅ |
| LLMモデル | llama-3.1-swallow-8b, gemma2:9b, qwen2.5:14b |
| TTS | VOICEVOX v0.25.1 ✅ (localhost:50021) |
| GPU | Apple M4 Pro（CUDA非対応） |

---

## 次回やること

1. **UE5 で LiveLink パネルを開く** (Window → Virtual Production → Live Link)
2. **テスト送信を実行**: `python3 Scripts/lipsync_livelink.py --test`
3. **LiveLink ソースが検出されることを確認**
4. **BP_Keiji の LiveLink 設定** (ARKit Face Subject = "PythonFace")
5. **VOICEVOX リップシンクテスト**: `python3 Scripts/lipsync_livelink.py "こんにちは"`
6. **口の動きを確認・ビゼームマッピング調整**

---

## PC版との差異

| 項目 | PC版 | Mac版 |
|------|------|-------|
| GPU | NVIDIA RTX 4090 | Apple M4 Pro |
| リップシンク | NVIDIA ACE (Audio2Face) | PyLiveLinkFace + VOICEVOX 音素解析 |
| TTS | VOICEVOX --use_gpu (0.14秒) | VOICEVOX v0.25.1 CPU版 |
| CUDA | 12.8 | 非対応 |

---

## 参考リンク
- [runreal/unreal-mcp](https://github.com/runreal/unreal-mcp)
- [PyLiveLinkFace](https://github.com/JimWest/PyLiveLinkFace) ★リップシンク送信ライブラリ
- [Apple ARKit Face Tracking](https://developer.apple.com/documentation/arkit/arfaceanchor)
- [UE5 Live Link Face](https://docs.unrealengine.com/5.0/en-US/live-link-face-in-unreal-engine/)
- [Animating MetaHumans with LiveLink](https://docs.metahuman.unrealengine.com/en-US/animating-metahumans-with-livelink-in-unreal-engine/)
