# Blender MCP Usage Guide

## 概要
Blender MCPを使用してClaude Codeから直接Blenderを操作する方法

## 基本的な使い方

### シーン情報の取得
```python
# mcp__blender__get_scene_info を使用
```

### スクリーンショット取得
```python
# mcp__blender__get_viewport_screenshot を使用
```

### コード実行
```python
# mcp__blender__execute_blender_code を使用
```

---

## シェイプキー操作の実用例

### 1. オブジェクトのシェイプキー確認
```python
import bpy

for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.data.shape_keys:
        print(f"{obj.name}: {len(obj.data.shape_keys.key_blocks)} shape keys")
        for kb in obj.data.shape_keys.key_blocks:
            print(f"  - {kb.name}")
```

### 2. シェイプキーの値を設定
```python
import bpy

obj = bpy.data.objects.get('MyMesh')
if obj and obj.data.shape_keys:
    kb = obj.data.shape_keys.key_blocks.get('mouth_a')
    if kb:
        kb.value = 1.0  # 0.0 ~ 1.0
```

### 3. シェイプキーの変位量を分析
```python
import bpy

obj = bpy.data.objects.get('MyMesh')
basis = obj.data.shape_keys.key_blocks['Basis']

for kb in obj.data.shape_keys.key_blocks[1:]:
    total_disp = 0
    for i in range(len(basis.data)):
        disp = (basis.data[i].co - kb.data[i].co).length
        total_disp += disp
    print(f"{kb.name}: total displacement = {total_disp:.2f}")
```

### 4. 特定エリアの頂点のみ分析
```python
import bpy

obj = bpy.data.objects.get('MyMesh')
basis = obj.data.shape_keys.key_blocks['Basis']

# 口エリア（下顔面）の頂点のみチェック
for kb in obj.data.shape_keys.key_blocks[1:]:
    mouth_disp = 0
    for i in range(len(basis.data)):
        b_co = basis.data[i].co
        t_co = kb.data[i].co

        # Z座標で下顔面をフィルタ
        if b_co.z < -4:
            disp = (t_co - b_co).length
            mouth_disp += disp

    if mouth_disp > 1:
        print(f"{kb.name}: mouth area = {mouth_disp:.2f}")
```

### 5. 新しいシェイプキーを作成（複数の組み合わせ）
```python
import bpy
import numpy as np

obj = bpy.data.objects.get('MyMesh')
basis = obj.data.shape_keys.key_blocks['Basis']

# 組み合わせ定義
combo = [('target_3', 0.8), ('target_64', 0.3)]

# 新しいシェイプキー作成
new_key = obj.shape_key_add(name='mouth_a', from_mix=False)

# ベースの座標を取得
basis_coords = np.array([v.co[:] for v in basis.data])
combined = basis_coords.copy()

# 各ソースシェイプキーの変位を加算
for src_name, weight in combo:
    src_key = obj.data.shape_keys.key_blocks.get(src_name)
    if src_key:
        src_coords = np.array([v.co[:] for v in src_key.data])
        delta = src_coords - basis_coords
        combined += delta * weight

# 新しいシェイプキーに適用
for i, co in enumerate(combined):
    new_key.data[i].co = co
```

---

## GLBエクスポート

### シェイプキー付きでエクスポート
```python
import bpy

# エクスポート対象を選択
bpy.ops.object.select_all(action='DESELECT')
for obj_name in ['Face', 'Eyes', 'Mouth']:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        obj.select_set(True)

# GLBエクスポート
bpy.ops.export_scene.gltf(
    filepath='/path/to/output.glb',
    export_format='GLB',
    use_selection=True,
    export_apply=False,  # シェイプキー保持のため
    export_morph=True,   # シェイプキーをエクスポート
    export_morph_normal=True
)
```

---

## トラブルシューティング

### シェイプキーがエクスポートされない
- `export_apply=False` を確認
- `export_morph=True` を確認
- メッシュにモディファイアがある場合は適用が必要な場合あり

### シェイプキー名が変わる
- FBX形式では名前が失われることがある
- GLB/glTF形式を推奨

### 変位が見えない
- シェイプキーの値が0になっていないか確認
- 正しいメッシュオブジェクトを操作しているか確認
- ビューポートの更新が必要な場合は `bpy.context.view_layer.update()` を実行

---

## 座標系の確認

モデルによって座標系が異なるため、最初に確認が必要：

```python
import bpy

obj = bpy.data.objects.get('MyMesh')
basis = obj.data.shape_keys.key_blocks['Basis']

# 頂点の範囲を確認
all_verts = [(v.co.x, v.co.y, v.co.z) for v in basis.data]
print(f"X: {min(v[0] for v in all_verts):.2f} to {max(v[0] for v in all_verts):.2f}")
print(f"Y: {min(v[1] for v in all_verts):.2f} to {max(v[1] for v in all_verts):.2f}")
print(f"Z: {min(v[2] for v in all_verts):.2f} to {max(v[2] for v in all_verts):.2f}")
```

一般的な座標系：
- **Blender標準**: Z=上、Y=前
- **インポートモデル**: 変換されていることが多いので確認必要
