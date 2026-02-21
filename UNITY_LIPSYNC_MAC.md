# Unity LipSync プロジェクト (Mac版)

## 概要
看護教育用デジタル患者シミュレーション - Unity + UMA + VOICEVOX + uLipSync

## 環境
| 項目 | 値 |
|------|-----|
| パス | `/Users/takeshikoike2025/My project (1)/` |
| エンジン | Unity (Mac) |
| キャラクター | UMA 2 (602アセット) |
| リップシンク | uLipSync + JawBone + BlendShape |
| TTS | VOICEVOX (localhost:50021) |

---

## スクリプト一覧 (Assets/Scripts/)

| ファイル | 機能 | 状態 |
|---------|------|------|
| VoicevoxSpeaker.cs | VOICEVOX API連携、テキスト→音声→AudioClip | 完了 |
| VoicevoxTester.cs | VOICEVOX動作テスト (5秒間隔) | 完了 |
| PatientLipSyncController.cs | 統合オーケストレーター (VOICEVOX→uLipSync→JawBone) | 完了 |
| BlendShapeLipSync.cs | uLipSync → BlendShape (mouth_a/i/u/e/o) | 完了 |
| JawBoneLipSync.cs | uLipSync → Jaw_M ボーン回転 (対数スケール) | 完了 |
| DirectLipSync.cs | 音量→顎ボーン回転 (シンプル版) | 完了 |
| WebSocketLipSync.cs | WebSocket(8765)で外部から音素受信 | 完了 |
| LipSyncController.cs | 汎用BlendShape制御 + テストスライダー | 完了 |
| UmaLipSync.cs | UMA ExpressionPlayer 音量駆動 | 開発中 |
| UMAClothingApplier.cs | UMA 服装適用 (MaleShirt1等) | 完了 |
| Editor/AvatarGeneratorHelper.cs | Itseez3D 写真→アバター (スカフォールド) | 未完了 |

---

## アーキテクチャ

```
テキスト入力
    ↓
VoicevoxSpeaker (HTTP → VOICEVOX API → WAV)
    ↓
AudioSource (再生)
    ↓
uLipSync (音素解析: a, i, u, e, o)
    ↓
┌─────────────┬──────────────┬───────────────┐
JawBoneLipSync BlendShapeLipSync WebSocketLipSync
(Jaw_M回転)   (mouth_a等)     (ブラウザ連携)
```

## シーン
| シーン | 用途 |
|--------|------|
| SampleScene | デフォルト |
| VoicevoxTest | VOICEVOX動作確認 |
| PatientLipSync | 患者リップシンク統合テスト |

## 外部依存
- uLipSync (音素解析プラグイン)
- UMA 2 (アバターシステム)
- Itseez3D AvatarMaker (写真→3Dアバター、未完成)
- polyperfect キャラクターモデル (Jaw_Mボーン)

## 関連MD
- `~/Downloads/uma_handover.md` - UMAキャラクター作成引き継ぎ

## 次のステップ
1. UmaLipSync のデバッグコード整理
2. AvatarGeneratorHelper 実装完了
3. VOICEVOX speaker ID の設定可能化
