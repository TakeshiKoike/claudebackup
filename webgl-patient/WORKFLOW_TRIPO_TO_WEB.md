# Tripoモデル → Blender → Web ワークフロー

「Tripoなどで作ったモデルをBlenderで仕上げて、Web向け形式に出す」部分を手順ベースで説明します。

## 1. TripoなどからBlenderに持ってくる

### Tripo側

1. Text to 3D でモデルを生成（患者などのプロンプト）
2. 出力形式は **GLB（glTF）** を選んでダウンロード（TripoはPBRテクスチャ入りのGLBを吐けます）

### Blenderで読み込み

1. Blender起動 → 「**File → Import → glTF 2.0（.glb/.gltf）**」を選択
2. ダウンロードしたGLBを指定すると、モデルとマテリアルがシーンに配置されます

### 読み込み後に最低限チェック

- スケール（2m前後に収まるようにUnit Scale調整）
- 原点位置（足元がワールド原点付近になるように移動）
- メッシュが1体にまとまっているか（バラバラなら結合しておくと後々楽です）

---

## 2. ボーン（リグ）を用意する

Tripoモデルは「ボーン無し」のことが多いので、ヒューマノイド用のリグを付けます。

### 人型なら：

1. Blenderの「**Add → Armature → Human（Rigify）**」などで人型リグを追加
2. 「Armature」をメッシュに合わせてスケール・位置を調整
3. モディファイアの「Armature」でメッシュにリグを指定し、ウェイトペイントや自動ウェイトでスキニング

### すでにボーン付きのGLBなら：

1. OutlinerでArmatureを確認
2. ポーズモードで腕や顎を動かして、メッシュが正しく追従するか確認

---

## 3. 口用BlendShape（シェイプキー）作成

Blenderでは「**Shape Keys**」として作ります。VRM/リップシンク用には **A/I/U/E/O** のVisemeを作るのが基本です。

### ベースキーの作成

1. メッシュを選択 → Object Data Properties（緑の三角アイコン）
2. Shape Keys セクションで「＋」を押し、**Basis** を作る（これが基準）

### Aの口（あ）

1. 再度「＋」で新しいShape Keyを作り、名前を **A** などにする
2. 値（Value）を 1.0 に上げる
3. **Edit Mode** に入り、口周りの頂点だけ選択して下方向に大きく開く形に調整
4. Edit Modeを抜けてValueを0〜1で動かすと、「あ」の口だけが動くことを確認

### I/U/E/O も同様

I, U, E, O のShape Keyを追加し、それぞれに対応する口形を彫る。

**ポイント：**
- **I**：横に広く、上下はあまり開かない
- **U**：すぼめる方向に頂点を前へ
- **E**：横広＋上の歯が少し見える程度
- **O**：縦よりも丸くすぼめる感じ

### まばたきや表情も余裕があれば

`Blink_L`, `Blink_R`, `Joy`, `Angry` などを同じ要領で追加。
VRMでは表情用BlendShapeも標準的に使えるので、後で流用可能です。

---

## 4. Web向けのエクスポート形式を決める

### パターンA：そのまま glTF / GLB

Unityや素のthree.jsだけで使うときにシンプル。

**手順：**
1. 「**File → Export → glTF 2.0（.glb）**」を選択
2. 「Include」でアニメーションやシェイプキーを含める設定をオンにする
3. glbにまとめてエクスポートすれば、Three.jsのGLTFLoaderで読み込み可能

### パターンB：VRM形式にする（おすすめ）

VRMにすると、three-vrmやUniVRMで「A/I/U/E/O」などのBlendShapeを標準的に扱えて、リップシンクとの連携が楽になります。

#### VRM Addon for Blenderを導入

1. GitHubの「**VRM Addon for Blender（saturday06版など）**」からzipダウンロード
2. Blenderで「**Edit → Preferences → Add-ons → Install**」からzipをインストールし、有効化

#### Humanoid設定

1. VRMタブから「Add VRM Humanoid」などを使い、人型ボーンをHumanoidとしてマッピング
2. 頭・首・腕・脚などを対応付ける

#### BlendShapeのVRM割り当て

1. VRMのBlendShape設定画面で、A/I/U/E/O Shape Keyをそれぞれ A, I, U, E, O のVisemeに割り当て
2. 必要ならBlinkや表情もPresetに紐づける

#### VRMとしてエクスポート

1. 「**File → Export → VRM（.vrm）**」を選択
2. Exportダイアログで
   - Export Only Selections など必要に応じてチェック
   - VRM 0.x か 1.0 を選択（Unity/three-vrmの対応バージョンに合わせる）
3. Saveボタンで書き出し

---

## 5. このあと WebGL でやること

glTF/VRMをWebへ持っていくときは：

1. **Three.js＋GLTFLoader** or **three-vrm** でモデルを読み込み
2. JavaScriptからBlendShape／シェイプキーの値を操作して、TTSのviseme/音声に合わせてリップシンクさせる

---

## 本プロジェクトの選択

| 項目 | 選択 |
|------|------|
| アバタータイプ | 上半身バストアップ |
| 出力形式 | VRM（three-vrm使用） |
| リップシンク | A/I/U/E/O Viseme |
