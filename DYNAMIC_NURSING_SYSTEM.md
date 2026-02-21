# DynamicNursingSystem - Unity + MLX LLM 患者会話

## 概要
Unity上でローカルLLM (MLX Qwen2.5) を使った患者会話シミュレーション

## 環境
| 項目 | 値 |
|------|-----|
| パス | `/Users/takeshikoike2025/Documents/DynamicNursingSystem/` |
| エンジン | Unity |
| LLM | MLX Qwen2.5-7B-Instruct-4bit (localhost:8080) |
| API | OpenAI互換 chat/completions |

---

## スクリプト一覧 (Assets/Scripts/)

| ファイル | 機能 | 状態 |
|---------|------|------|
| LLMClient.cs | MLX LLMサーバーとHTTP通信 | 完了 |
| ConversationUI.cs | TextMeshProベースのチャットUI (色分け表示) | 完了 |
| ChatLogger.cs | 会話ログJSON保存 + LoRA訓練データ出力 | 完了 |

---

## 患者ペルソナ (デフォルト)
- **名前**: 山田花子
- **年齢**: 68歳女性
- **主訴**: 階段昇降時の胸部圧迫感 (3日前から)
- **既往歴**: 高血圧、糖尿病
- **性格**: 不安が強い、曖昧な返答をする

## アーキテクチャ

```
看護師(ユーザー)入力
    ↓
ConversationUI → LLMClient (HTTP POST)
    ↓
MLX Server (localhost:8080) → Qwen2.5-7B応答
    ↓
ConversationUI表示 (看護師=青, 患者=赤, システム=灰)
    ↓
ChatLogger (JSON保存 + LoRA訓練形式エクスポート)
```

## プロジェクト状態
| コンポーネント | 状態 |
|--------------|------|
| LLM通信 | ✅ |
| チャットUI | ✅ |
| データログ | ✅ |
| シーン作成 | ❌ 未作成 |
| プレファブ | ❌ 未作成 |

## 次のステップ
1. メインシーン作成 + UI配置
2. 複数患者シナリオ対応
3. LoRA訓練パイプライン構築
