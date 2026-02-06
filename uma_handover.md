# UMA キャラクター作成 - Claude Code 引き継ぎ資料

## 目標
UnityでUMA (Unity Multipurpose Avatar) を使ってキャラクターを作成する

## 環境
- Mac
- Unity プロジェクト: `/Users/takeshikoike2025/My project (1)/`
- UMA 2 インストール済み: `Assets/UMA/` (602アセット)

## 現在の状態

### シーン内のオブジェクト
- `Main Camera`
- `Directional Light`
- `Global Volume`
- `UMA_Context` ✅ (UMAシステム基盤、正常)
- `UMA_Character` (非アクティブ、不要)
- `UMADynamicCharacterAvatar` ✅ (キャラクター本体、コンポーネント認識済み)

### 修正済みの問題
- `Assets/UMA/Core/StandardAssets/UMA/Scripts/MeshHideAsset.cs` 23行目
- `[SerializeField]` がプロパティに付いていたコンパイルエラー → 削除して修正済み
- 現在コンパイルエラーなし

### 未完了の作業
**UMADynamicCharacterAvatar の Race 設定ができていない**

キャラクターを表示するには `activeRace` を `HumanMale` または `HumanFemale` に設定する必要がある。

## 試したが失敗したアプローチ

1. **MCP manage_components でプロパティ設定**
   - `activeRace` は `RaceSetter` 型で単純な文字列設定不可
   
2. **MCP execute_menu_item**
   - カスタムメニュー実行が不安定

3. **MCP manage_gameobject でプレファブ追加**
   - UMAプレファブは依存関係が複雑で失敗

## 推奨アプローチ

### 方法1: C#スクリプトで直接設定
```csharp
// Assets/Editor/SetUMARace.cs (作成済み、コンパイル待ち)
using UnityEngine;
using UnityEditor;
using UMA.CharacterSystem;

public class SetUMARace
{
    [MenuItem("Tools/Set UMA Race - HumanMale")]
    static void SetHumanMale()
    {
        var avatar = GameObject.Find("UMADynamicCharacterAvatar");
        if (avatar != null)
        {
            var dca = avatar.GetComponent<DynamicCharacterAvatar>();
            if (dca != null)
            {
                dca.activeRace.name = "HumanMale";
                dca.BuildCharacter();
            }
        }
    }
}
```

### 方法2: SerializedObject経由
```csharp
using UnityEditor;

var avatar = GameObject.Find("UMADynamicCharacterAvatar");
var dca = avatar.GetComponent<DynamicCharacterAvatar>();
var so = new SerializedObject(dca);
var raceProp = so.FindProperty("activeRace").FindPropertyRelative("name");
raceProp.stringValue = "HumanMale";
so.ApplyModifiedProperties();
```

## ファイル一覧

| パス | 状態 |
|------|------|
| Assets/UMA/ | UMA本体 (602アセット) |
| Assets/UMA/Getting Started/UMADynamicCharacterAvatar.prefab | キャラクタープレファブ |
| Assets/UMA/Examples/Legacy Examples/Assets/Prefabs/UMA_Demo_Context.prefab | Context プレファブ |
| Assets/Editor/SetUMARace.cs | Race設定スクリプト (作成済み) |
| Assets/Editor/UMACharacterCreator.cs | キャラクター作成スクリプト (作成済み) |

## 次のステップ

1. `Assets/Editor/SetUMARace.cs` のコンパイル完了を待つ
2. Unity メニュー `Tools/Set UMA Race - HumanMale` を実行
3. Play モードでキャラクター表示確認
4. カメラ位置調整 (キャラクターが見える位置に)

## 補足: 最終目標 (ユーザーの研究プロジェクト)

- 看護教育用デジタル患者シミュレーション
- UMAアバター + Swallow 8B LLM + VOICEVOX音声合成 + uLipSyncリップシンク
- Ready Player Me が2026/1/31で終了のため、UMAを代替として採用
