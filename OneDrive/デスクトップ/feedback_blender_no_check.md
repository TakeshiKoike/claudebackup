---
name: Blender接続確認を求めない
description: Blender MCPの接続確認をユーザーに求めない。起動済み前提で直接作業を進める
type: feedback
---

Blender MCPの接続状態をユーザーに確認するのをやめること。毎回「Connect to Claudeを押してください」と聞くのは禁止。

**Why:** ユーザーはBlenderを常に起動・接続済みの状態で使っている。毎回同じ確認を求められることに強い不満を持っている。

**How to apply:** Blender MCPツールが見つからない場合でも、ユーザーに確認を求めず、ポート9876への直接接続やPythonスクリプト経由など代替手段で作業を進める。Blenderは起動済み・接続済みが前提。
