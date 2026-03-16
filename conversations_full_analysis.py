#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
conversations.json + Claude Code JSONL 全量統合分析
JSISE論文用 学術分析レポート

分析項目:
1. 全humanメッセージの6分類コーディング（月別比率推移）
2. やり取りのシーケンスパターン（協働パターン抽出）
3. 1メッセージあたりの具体性の推移（固有名詞・技術用語・数値密度）
4. 教育的専門知識の言語化の実例（フェーズ別10件抽出）
"""

import json
import sys
import os
import re
import glob
from collections import defaultdict, Counter
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT = "C:/Users/kokek/OneDrive/デスクトップ/conversations_full_analysis.md"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# データ読み込み
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("=== データ読み込み ===")

# --- conversations.json (Web/Desktop) ---
CONV_PATH = "C:/Users/kokek/Downloads/data-2026-03-15-15-02-07-batch-0000/conversations.json"
print(f"Loading {CONV_PATH}...")
with open(CONV_PATH, 'r', encoding='utf-8') as f:
    conv_data = json.load(f)

web_messages = []  # (year_month, sender, text, timestamp_str, source, conv_name)
for conv in conv_data:
    conv_name = conv.get('name', '') or ''
    for msg in conv.get('chat_messages', []):
        sender = msg.get('sender', '')
        text = msg.get('text', '') or ''
        created = msg.get('created_at', '')
        if not text.strip() or not created:
            continue
        try:
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            ym = dt.strftime('%Y-%m')
        except:
            continue
        web_messages.append((ym, sender, text, dt, 'web', conv_name))

print(f"  Web/Desktop: {len(web_messages)} messages")

# --- Claude Code JSONL ---
JSONL_DIR = os.path.expanduser('~/.claude/projects/C--Users-kokek/')
jsonl_files = glob.glob(os.path.join(JSONL_DIR, '*.jsonl'))
print(f"Loading {len(jsonl_files)} JSONL files...")

cc_messages = []  # same format
for fp in jsonl_files:
    with open(fp, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line)
            except:
                continue
            if obj.get('type') not in ('user', 'assistant'):
                continue
            sender = 'human' if obj['type'] == 'user' else 'assistant'
            ts = obj.get('timestamp', '')
            msg_obj = obj.get('message', {})

            # テキスト抽出
            text = ''
            if isinstance(msg_obj, dict):
                content = msg_obj.get('content', '')
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    parts = []
                    for c in content:
                        if isinstance(c, dict) and c.get('type') == 'text':
                            parts.append(c.get('text', ''))
                        elif isinstance(c, str):
                            parts.append(c)
                    text = '\n'.join(parts)
            elif isinstance(msg_obj, str):
                text = msg_obj

            if not text.strip() or not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                ym = dt.strftime('%Y-%m')
            except:
                continue

            session_id = obj.get('sessionId', '')
            cc_messages.append((ym, sender, text, dt, 'claude_code', session_id))

print(f"  Claude Code: {len(cc_messages)} messages")

# 統合
all_messages = sorted(web_messages + cc_messages, key=lambda x: x[3])
print(f"  統合合計: {len(all_messages)} messages")

# humanのみ
human_msgs = [(ym, text, dt, src, ctx) for ym, sender, text, dt, src, ctx in all_messages if sender == 'human']
print(f"  Human messages: {len(human_msgs)}")

all_months = sorted(set(m[0] for m in all_messages))
print(f"  期間: {all_months[0]} 〜 {all_months[-1]}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 分析1: 全humanメッセージの6分類コーディング
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 分析1: メッセージコーディング ===")

# ルールベース分類（キーワード重み付けスコアリング）
def classify_message(text):
    """
    6分類:
    A: 教育的意図の伝達
    B: 技術的指示
    C: 設計判断
    D: 品質フィードバック
    E: コンテキスト補足
    F: その他
    """
    scores = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'F': 0}
    t = text.lower()

    # A: 教育的意図の伝達
    edu_kw = [
        ('看護教育', 3), ('学習目標', 3), ('臨床', 2), ('実習', 2), ('学生', 2),
        ('教育', 2), ('患者', 1.5), ('模擬患者', 3), ('看護師', 1.5), ('国家試験', 2),
        ('国試', 2), ('アセスメント', 2), ('フィジカル', 2), ('バイタル', 2),
        ('教材', 2), ('カリキュラム', 2), ('授業', 2), ('演習', 2),
        ('シミュレーション', 1.5), ('看護', 1), ('ケア', 1.5), ('症状', 1.5),
        ('診断', 1.5), ('疾患', 1.5), ('訪問看護', 2), ('在宅', 1.5),
        ('介護', 1.5), ('リハビリ', 1.5), ('褥瘡', 2), ('感染', 1),
        ('問診', 2), ('処方', 1.5), ('病棟', 1.5), ('病院', 1),
        ('臨床判断', 3), ('看護過程', 3), ('看護計画', 3),
        ('学習者', 2), ('教員', 2), ('指導', 1.5),
    ]
    for kw, w in edu_kw:
        if kw in t:
            scores['A'] += w * t.count(kw)

    # B: 技術的指示
    tech_kw = [
        ('コード', 2), ('実装', 2), ('修正して', 3), ('直して', 2), ('変更して', 2),
        ('作って', 2), ('作成して', 2), ('書いて', 1.5), ('追加して', 2),
        ('削除して', 2), ('エラー', 1.5), ('バグ', 2), ('動かない', 2),
        ('インストール', 2), ('セットアップ', 2), ('設定', 1.5),
        ('python', 1.5), ('javascript', 1.5), ('html', 1.5), ('css', 1.5),
        ('api', 1.5), ('npm', 2), ('pip', 2), ('git', 1.5),
        ('ffmpeg', 2), ('コンパイル', 2), ('ビルド', 1.5), ('デプロイ', 2),
        ('ファイル', 1), ('フォルダ', 1), ('パス', 1), ('コマンド', 1.5),
        ('スクリプト', 1.5), ('関数', 1.5), ('クラス', 1.5),
        ('ue5', 2), ('unity', 2), ('blender', 2), ('comfyui', 2),
        ('voicevox', 2), ('ollama', 2), ('docker', 2), ('wsl', 1.5),
        ('three.js', 2), ('react', 1.5), ('metahuman', 2),
    ]
    for kw, w in tech_kw:
        if kw in t:
            scores['B'] += w * t.count(kw)

    # C: 設計判断
    design_kw = [
        ('構造', 2), ('アーキテクチャ', 3), ('設計', 2), ('テンプレート', 2),
        ('パイプライン', 2), ('ワークフロー', 2), ('方針', 2), ('戦略', 2),
        ('どっちがいい', 3), ('どちらがいい', 3), ('比較', 1.5), ('選択', 1.5),
        ('パターン', 1.5), ('フレームワーク', 2), ('モジュール', 2),
        ('分離', 1.5), ('統合', 1.5), ('自動化', 2), ('最適', 1.5),
        ('代替', 2), ('候補', 1.5), ('提案', 1.5), ('アプローチ', 2),
        ('にする', 1), ('にしよう', 1.5), ('にしましょう', 1.5),
        ('全体像', 2), ('構成', 1.5), ('レイアウト', 1.5),
    ]
    for kw, w in design_kw:
        if kw in t:
            scores['C'] += w * t.count(kw)

    # D: 品質フィードバック
    feedback_kw = [
        ('ありがとう', 2), ('すごい', 2), ('いいね', 2), ('素晴らしい', 2),
        ('完璧', 3), ('ok', 1.5), ('いい感じ', 2), ('助かる', 2),
        ('できた', 1.5), ('よかった', 1.5), ('さすが', 2), ('最高', 2),
        ('違う', 2), ('ダメ', 2), ('だめ', 2), ('間違い', 2), ('間違って', 2),
        ('やり直し', 3), ('もう一度', 1.5), ('こうじゃない', 3),
        ('そうじゃなく', 3), ('惜しい', 2), ('微妙', 2),
        ('いいけど', 1.5), ('けど', 0.5), ('ただ', 0.5),
        ('うまくいった', 2), ('成功', 1.5), ('失敗', 1.5),
        ('perfect', 2), ('great', 1.5), ('good', 1), ('nice', 1.5),
        ('wrong', 2), ('not', 0.5),
    ]
    for kw, w in feedback_kw:
        if kw in t:
            scores['D'] += w * t.count(kw)

    # E: コンテキスト補足
    context_kw = [
        ('前回', 3), ('引き継ぎ', 3), ('続き', 2), ('さっき', 2), ('先ほど', 2),
        ('ちなみに', 2), ('補足', 3), ('背景', 2), ('経緯', 2), ('状況', 1.5),
        ('現在', 1), ('今', 0.5), ('実は', 2), ('というのも', 2),
        ('参考に', 2), ('見て', 1), ('読んで', 1.5), ('確認して', 1),
        ('ところで', 1.5), ('余談', 2), ('報告', 1.5),
        ('セッション', 1.5), ('メモリ', 1.5),
    ]
    for kw, w in context_kw:
        if kw in t:
            scores['E'] += w * t.count(kw)

    # 最高スコアを取得
    max_score = max(scores.values())
    if max_score < 1.5:  # 閾値未満は「その他」
        return 'F'

    # 最高スコアのカテゴリを返す
    best = max(scores, key=scores.get)
    return best

# 分類名マッピング
cat_names = {
    'A': '教育的意図の伝達',
    'B': '技術的指示',
    'C': '設計判断',
    'D': '品質フィードバック',
    'E': 'コンテキスト補足',
    'F': 'その他',
}

# 全humanメッセージを分類
classified = []  # (ym, cat, text, dt, src, ctx)
monthly_cats = defaultdict(lambda: Counter())
total_cats = Counter()

for ym, text, dt, src, ctx in human_msgs:
    cat = classify_message(text)
    classified.append((ym, cat, text, dt, src, ctx))
    monthly_cats[ym][cat] += 1
    total_cats[cat] += 1

print("  分類結果:")
for cat in 'ABCDEF':
    n = total_cats[cat]
    pct = n / len(human_msgs) * 100
    print(f"    {cat}: {cat_names[cat]} = {n} ({pct:.1f}%)")

# 分析1結果
r1 = []
r1.append("## 分析1: Humanメッセージの発話行為コーディング")
r1.append("")
r1.append("### 1.1 コーディングスキーム")
r1.append("")
r1.append("本分析では，ユーザ（看護教育者）の全発話メッセージを以下の6カテゴリに分類した．")
r1.append("分類にはキーワード重み付けスコアリング方式を採用し，各メッセージに対して")
r1.append("カテゴリごとのスコアを算出，最高スコアのカテゴリに分類した（閾値1.5未満は「その他」）．")
r1.append("")
r1.append("| コード | カテゴリ | 定義 | 件数 | 比率 |")
r1.append("|---|---|---|---|---|")
for cat in 'ABCDEF':
    n = total_cats[cat]
    pct = n / len(human_msgs) * 100
    defs = {
        'A': '学習目標，学生の理解度，臨床的背景など教育的文脈の伝達',
        'B': '具体的な実装指示，コード修正依頼，環境構築の指示',
        'C': '構造の決定，テンプレート化，アーキテクチャ選択に関する判断',
        'D': '肯定的・否定的評価，成果物への修正要求',
        'E': '前回セッションからの引き継ぎ，状況説明，背景情報の補足',
        'F': '上記に該当しない発話（挨拶，確認応答等）',
    }
    r1.append(f"| {cat} | {cat_names[cat]} | {defs[cat]} | {n:,} | {pct:.1f}% |")

r1.append(f"\n**分析対象**: {len(human_msgs):,}メッセージ（Web/Desktop: {sum(1 for m in human_msgs if m[3])}件 + Claude Code: 統合）")

r1.append("\n### 1.2 月別コーディング比率の推移")
r1.append("")
r1.append("| 月 | 総数 | A:教育意図 | B:技術指示 | C:設計判断 | D:品質FB | E:文脈補足 | F:その他 |")
r1.append("|---|---|---|---|---|---|---|---|")
for ym in all_months:
    cats = monthly_cats[ym]
    total = sum(cats.values())
    if total == 0:
        continue
    vals = []
    for cat in 'ABCDEF':
        n = cats[cat]
        pct = n / total * 100
        vals.append(f"{n} ({pct:.0f}%)")
    r1.append(f"| {ym} | {total} | " + " | ".join(vals) + " |")

# フェーズ別集約
phases = {
    '導入期 (2025-01〜03)': ('2025-01', '2025-03'),
    '拡張期 (2025-04〜06)': ('2025-04', '2025-06'),
    '発展期 (2025-07〜09)': ('2025-07', '2025-09'),
    '深化期 (2025-10〜12)': ('2025-10', '2025-12'),
    '統合期 (2026-01〜03)': ('2026-01', '2026-03'),
}

r1.append("\n### 1.3 フェーズ別コーディング比率")
r1.append("")
r1.append("| フェーズ | 総数 | A:教育意図 | B:技術指示 | C:設計判断 | D:品質FB | E:文脈補足 | F:その他 |")
r1.append("|---|---|---|---|---|---|---|---|")
for phase_name, (start, end) in phases.items():
    phase_cats = Counter()
    for ym in all_months:
        if start <= ym <= end:
            phase_cats += monthly_cats[ym]
    total = sum(phase_cats.values())
    if total == 0:
        continue
    vals = []
    for cat in 'ABCDEF':
        n = phase_cats[cat]
        pct = n / total * 100
        vals.append(f"{n} ({pct:.0f}%)")
    r1.append(f"| {phase_name} | {total} | " + " | ".join(vals) + " |")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 分析2: シーケンスパターン
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 分析2: シーケンスパターン ===")

# 会話単位でシーケンスを構築
# conversations.json: 会話ごと
# JSONL: sessionIdごと

def analyze_sequences(conv_msgs_list):
    """会話のリスト(各会話は[(sender, text, cat)]のリスト)からパターンを抽出"""
    # 2-gram, 3-gram, 4-gramのパターン
    bigrams = Counter()
    trigrams = Counter()
    fourgrams = Counter()

    # 会話長分布
    conv_lengths = []

    # ターン間の分類遷移
    cat_transitions = Counter()

    for conv in conv_msgs_list:
        conv_lengths.append(len(conv))
        senders = [m[0] for m in conv]
        cats = [m[2] for m in conv if m[0] == 'human']

        # sender bigrams
        for i in range(len(senders) - 1):
            bigrams[(senders[i], senders[i+1])] += 1
        for i in range(len(senders) - 2):
            trigrams[(senders[i], senders[i+1], senders[i+2])] += 1
        for i in range(len(senders) - 3):
            fourgrams[(senders[i], senders[i+1], senders[i+2], senders[i+3])] += 1

        # human分類の遷移
        for i in range(len(cats) - 1):
            cat_transitions[(cats[i], cats[i+1])] += 1

    return bigrams, trigrams, fourgrams, conv_lengths, cat_transitions

# conversations.json の会話単位
web_convs = []
for conv in conv_data:
    msgs = []
    for msg in conv.get('chat_messages', []):
        sender = msg.get('sender', '')
        text = msg.get('text', '') or ''
        if not text.strip():
            continue
        cat = classify_message(text) if sender == 'human' else '-'
        msgs.append((sender, text, cat))
    if msgs:
        web_convs.append(msgs)

# JSONL のセッション単位
cc_sessions = defaultdict(list)
for fp in sorted(jsonl_files):
    with open(fp, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line)
            except:
                continue
            if obj.get('type') not in ('user', 'assistant'):
                continue
            sender = 'human' if obj['type'] == 'user' else 'assistant'
            sid = obj.get('sessionId', fp)
            msg_obj = obj.get('message', {})
            text = ''
            if isinstance(msg_obj, dict):
                content = msg_obj.get('content', '')
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    parts = []
                    for c in content:
                        if isinstance(c, dict) and c.get('type') == 'text':
                            parts.append(c.get('text', ''))
                        elif isinstance(c, str):
                            parts.append(c)
                    text = '\n'.join(parts)
            if not text.strip():
                continue
            cat = classify_message(text) if sender == 'human' else '-'
            cc_sessions[sid].append((sender, text, cat))

cc_convs = list(cc_sessions.values())

all_convs = web_convs + cc_convs
print(f"  会話数: Web {len(web_convs)}, Claude Code {len(cc_convs)}, 合計 {len(all_convs)}")

bigrams, trigrams, fourgrams, conv_lengths, cat_transitions = analyze_sequences(all_convs)

# 協働パターンの抽出
# human分類の遷移パターンから典型的なシーケンスを特定
r2 = []
r2.append("## 分析2: やり取りのシーケンスパターン")
r2.append("")
r2.append("### 2.1 会話の基本統計")
r2.append("")
r2.append(f"- 総会話数: {len(all_convs):,}（Web/Desktop: {len(web_convs)}, Claude Code: {len(cc_convs)}）")
r2.append(f"- 会話あたりのメッセージ数: 平均 {sum(conv_lengths)/len(conv_lengths):.1f}, 中央値 {sorted(conv_lengths)[len(conv_lengths)//2]}")
r2.append(f"- 最長会話: {max(conv_lengths)} メッセージ")

# 会話長の分布
len_bins = [(1,2,'1-2'), (3,5,'3-5'), (6,10,'6-10'), (11,20,'11-20'), (21,50,'21-50'), (51,100,'51-100'), (101,9999,'101+')]
r2.append("")
r2.append("| 会話長 | 件数 | 比率 |")
r2.append("|---|---|---|")
for lo, hi, label in len_bins:
    n = sum(1 for l in conv_lengths if lo <= l <= hi)
    pct = n / len(conv_lengths) * 100
    r2.append(f"| {label}メッセージ | {n} | {pct:.1f}% |")

r2.append("\n### 2.2 発話者遷移パターン")
r2.append("")
r2.append("#### 2-gramパターン（隣接ペア）")
r2.append("| パターン | 頻度 | 比率 |")
r2.append("|---|---|---|")
total_bi = sum(bigrams.values())
for (a, b), count in bigrams.most_common(10):
    pct = count / total_bi * 100
    r2.append(f"| {a} → {b} | {count:,} | {pct:.1f}% |")

r2.append("\n#### 3-gramパターン")
r2.append("| パターン | 頻度 |")
r2.append("|---|---|")
for pattern, count in trigrams.most_common(8):
    r2.append(f"| {'→'.join(pattern)} | {count:,} |")

r2.append("\n### 2.3 Human発話の分類遷移パターン")
r2.append("")
r2.append("ユーザの連続する発話がどのカテゴリからどのカテゴリへ遷移するかを分析した．")
r2.append("")
r2.append("| 遷移 | 頻度 | 解釈 |")
r2.append("|---|---|---|")

transition_interpretations = {
    ('B', 'B'): '反復的技術指示（段階的な実装の進行）',
    ('B', 'D'): '実装結果への評価（技術指示→品質確認サイクル）',
    ('D', 'B'): '評価後の追加指示（フィードバック→次の実装指示）',
    ('A', 'B'): '教育的文脈の提示後に技術的実装を依頼',
    ('B', 'A'): '技術実装後に教育的観点から評価・指示',
    ('B', 'C'): '実装から設計判断へ（具体作業から抽象思考への移行）',
    ('C', 'B'): '設計決定後の実装着手',
    ('D', 'D'): '連続的フィードバック（段階的な品質調整）',
    ('E', 'B'): '文脈共有後に作業開始',
    ('A', 'A'): '教育的議論の深化',
    ('F', 'B'): '軽い確認後の技術指示',
    ('B', 'F'): '技術指示後の簡単な確認応答',
    ('B', 'E'): '実装中の追加文脈提供',
    ('D', 'A'): '評価後に教育的視点から再指示',
    ('F', 'F'): '短い応答の連続（確認のやり取り）',
    ('C', 'C'): '設計議論の継続',
    ('A', 'C'): '教育目標から設計判断へ',
    ('C', 'A'): '設計判断に教育的根拠を追加',
}

for (a, b), count in cat_transitions.most_common(20):
    interp = transition_interpretations.get((a, b), '')
    r2.append(f"| {cat_names[a]}({a})→{cat_names[b]}({b}) | {count:,} | {interp} |")

# 典型的な協働パターン抽出
r2.append("\n### 2.4 典型的な協働パターン")
r2.append("")

# B→D→B サイクル（技術指示→評価→修正指示）
bdb_count = 0
for conv in all_convs:
    h_cats = [m[2] for m in conv if m[0] == 'human']
    for i in range(len(h_cats) - 2):
        if h_cats[i] == 'B' and h_cats[i+1] == 'D' and h_cats[i+2] == 'B':
            bdb_count += 1

# A→B→D サイクル（教育意図→技術指示→評価）
abd_count = 0
for conv in all_convs:
    h_cats = [m[2] for m in conv if m[0] == 'human']
    for i in range(len(h_cats) - 2):
        if h_cats[i] == 'A' and h_cats[i+1] == 'B' and h_cats[i+2] == 'D':
            abd_count += 1

# E→B→B (文脈→実装→実装)
ebb_count = 0
for conv in all_convs:
    h_cats = [m[2] for m in conv if m[0] == 'human']
    for i in range(len(h_cats) - 2):
        if h_cats[i] == 'E' and h_cats[i+1] == 'B' and h_cats[i+2] == 'B':
            ebb_count += 1

# C→B→D (設計→実装→評価)
cbd_count = 0
for conv in all_convs:
    h_cats = [m[2] for m in conv if m[0] == 'human']
    for i in range(len(h_cats) - 2):
        if h_cats[i] == 'C' and h_cats[i+1] == 'B' and h_cats[i+2] == 'D':
            cbd_count += 1

r2.append("| パターン | 頻度 | 解釈 |")
r2.append("|---|---|---|")
r2.append(f"| B→D→B（実装→評価→修正） | {bdb_count} | 反復的品質改善サイクル．最も基本的な協働パターン |")
r2.append(f"| A→B→D（教育意図→実装→評価） | {abd_count} | 教育者主導の開発サイクル．教育的要件の技術的実現 |")
r2.append(f"| E→B→B（文脈共有→連続実装） | {ebb_count} | セッション再開パターン．引き継ぎ後に集中作業 |")
r2.append(f"| C→B→D（設計→実装→評価） | {cbd_count} | 設計駆動開発パターン．構造決定後に実装・検証 |")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 分析3: 具体性の推移
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 分析3: 具体性の推移 ===")

# 固有名詞・技術用語リスト
proper_nouns = set([
    'UE5', 'Unity', 'Blender', 'MetaHuman', 'VOICEVOX', 'ComfyUI', 'ELYZA',
    'Nemotron', 'Ollama', 'Docker', 'WSL', 'NVIDIA', 'RTX', 'CUDA',
    'Three.js', 'React', 'Next.js', 'Python', 'JavaScript', 'TypeScript',
    'HTML', 'CSS', 'ffmpeg', 'Git', 'GitHub', 'npm', 'pip',
    'COPD', 'VR', 'AR', 'DX', 'ICT', 'AI', 'LLM', 'TTS', 'MCP',
    'VOICEVOX', 'Moshi', 'PersonaPlex', 'Qwen', 'Flux', 'Remotion',
    'WebGL', 'OpenGL', 'OpenCV', 'GGUF', 'llama.cpp', 'tmux', 'MSYS2',
    'Selenium', 'PowerPoint', 'PPTX', 'Voicebox', 'WakuFact',
    'Audio2Face', 'ACE', 'uLipSync', 'CC4', 'MetaHuman',
    'KEIJI', 'Windows', 'Linux', 'Ubuntu', 'Mac', 'Chrome',
    'API', 'REST', 'JSON', 'JSONL', 'CSV', 'MD', 'PDF', 'GLB', 'FBX',
    'PNG', 'JPG', 'MP4', 'WAV', 'MP3',
])

# 数値パターン
num_pattern = re.compile(r'\b\d+(\.\d+)?\b')
# パス・URL
path_pattern = re.compile(r'[A-Za-z]:\\[^\s]+|/[a-z][^\s]*|https?://[^\s]+|localhost:\d+')
# バージョン番号
version_pattern = re.compile(r'v?\d+\.\d+(\.\d+)?')

def calc_specificity(text):
    """具体性スコア: 固有名詞数 + 数値出現数 + パス/URL数"""
    t_lower = text.lower()

    # 固有名詞
    noun_count = sum(1 for pn in proper_nouns if pn.lower() in t_lower)

    # 数値
    num_count = len(num_pattern.findall(text))

    # パス/URL
    path_count = len(path_pattern.findall(text))

    # バージョン
    ver_count = len(version_pattern.findall(text))

    total = noun_count + num_count + path_count + ver_count

    # 文字数で正規化（100文字あたり）
    length = max(len(text), 1)
    density = total / length * 100

    return total, density, noun_count, num_count, path_count

monthly_specificity = defaultdict(lambda: {'total': [], 'density': [], 'nouns': [], 'nums': [], 'paths': [], 'lengths': []})

for ym, text, dt, src, ctx in human_msgs:
    total, density, nouns, nums, paths = calc_specificity(text)
    monthly_specificity[ym]['total'].append(total)
    monthly_specificity[ym]['density'].append(density)
    monthly_specificity[ym]['nouns'].append(nouns)
    monthly_specificity[ym]['nums'].append(nums)
    monthly_specificity[ym]['paths'].append(paths)
    monthly_specificity[ym]['lengths'].append(len(text))

r3 = []
r3.append("## 分析3: メッセージの具体性の推移")
r3.append("")
r3.append("ユーザ発話における固有名詞（ツール名・技術用語），数値，パス/URL の出現密度を")
r3.append("月別に計測し，指示の具体性の変化を定量的に評価した．")
r3.append("")
r3.append("### 3.1 月別具体性指標")
r3.append("")
r3.append("| 月 | 件数 | 平均文字数 | 固有名詞/msg | 数値/msg | パスURL/msg | 具体性密度(/100字) |")
r3.append("|---|---|---|---|---|---|---|")
for ym in all_months:
    d = monthly_specificity[ym]
    if not d['total']:
        continue
    n = len(d['total'])
    avg_len = sum(d['lengths']) / n
    avg_nouns = sum(d['nouns']) / n
    avg_nums = sum(d['nums']) / n
    avg_paths = sum(d['paths']) / n
    avg_density = sum(d['density']) / n
    r3.append(f"| {ym} | {n} | {avg_len:.0f} | {avg_nouns:.2f} | {avg_nums:.2f} | {avg_paths:.2f} | {avg_density:.2f} |")
    print(f"  {ym}: {n}件, 密度={avg_density:.2f}, 名詞={avg_nouns:.2f}, 数値={avg_nums:.2f}")

# フェーズ別
r3.append("\n### 3.2 フェーズ別具体性指標")
r3.append("")
r3.append("| フェーズ | 件数 | 平均文字数 | 固有名詞/msg | 数値/msg | パスURL/msg | 具体性密度(/100字) |")
r3.append("|---|---|---|---|---|---|---|")
for phase_name, (start, end) in phases.items():
    merged = {'total': [], 'density': [], 'nouns': [], 'nums': [], 'paths': [], 'lengths': []}
    for ym in all_months:
        if start <= ym <= end:
            for k in merged:
                merged[k].extend(monthly_specificity[ym][k])
    if not merged['total']:
        continue
    n = len(merged['total'])
    avg_len = sum(merged['lengths']) / n
    avg_nouns = sum(merged['nouns']) / n
    avg_nums = sum(merged['nums']) / n
    avg_paths = sum(merged['paths']) / n
    avg_density = sum(merged['density']) / n
    r3.append(f"| {phase_name} | {n} | {avg_len:.0f} | {avg_nouns:.2f} | {avg_nums:.2f} | {avg_paths:.2f} | {avg_density:.2f} |")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 分析4: 教育的専門知識の言語化の実例
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 分析4: 教育的専門知識の言語化の実例 ===")

# カテゴリAのメッセージをフェーズ別に抽出
# 「教育的専門知識」のスコアが高いもの上位10件
edu_keywords_weighted = [
    ('看護教育', 5), ('模擬患者', 5), ('臨床判断', 5), ('看護過程', 5),
    ('フィジカルアセスメント', 5), ('シミュレーション教育', 5),
    ('学習目標', 4), ('臨床実習', 4), ('客観的臨床能力試験', 5),
    ('OSCE', 5), ('カリキュラム', 4), ('教育効果', 4),
    ('看護計画', 4), ('看護診断', 4), ('問診', 3), ('バイタルサイン', 4),
    ('患者理解', 4), ('コミュニケーション', 3), ('共感', 3),
    ('学生', 3), ('臨床', 2), ('教育', 2), ('実習', 2),
    ('看護師', 2), ('患者', 2), ('症状', 2), ('疾患', 2),
    ('アセスメント', 3), ('ケア', 2), ('訪問看護', 3),
    ('在宅', 2), ('経営', 3), ('診療所', 3),
    ('国家試験', 3), ('看護技術', 4), ('援助', 3),
]

def edu_score(text):
    """教育的専門知識スコア"""
    t = text.lower()
    score = 0
    for kw, w in edu_keywords_weighted:
        if kw.lower() in t:
            score += w
    # 長すぎるメッセージはペナルティ（コード貼り付けなど）
    if len(text) > 1000:
        score *= 0.5
    # 短すぎるメッセージもペナルティ
    if len(text) < 20:
        score *= 0.3
    return score

r4 = []
r4.append("## 分析4: 教育的専門知識の言語化の実例")
r4.append("")
r4.append("各フェーズから，教育的専門知識スコアの高い代表的発話を10件ずつ抽出した．")
r4.append("これらは看護教育者がAIに対して教育的・臨床的文脈を言語化している実例であり，")
r4.append("ドメイン専門家とAIの協働における知識伝達の具体的様態を示す．")
r4.append("")

for phase_name, (start, end) in phases.items():
    phase_msgs = []
    for ym, cat, text, dt, src, ctx in classified:
        if start <= ym <= end:
            score = edu_score(text)
            if score >= 3:  # 最低閾値
                phase_msgs.append((score, text, ym, dt, src))

    # スコア降順、重複排除
    phase_msgs.sort(key=lambda x: -x[0])
    seen_texts = set()
    unique = []
    for score, text, ym, dt, src in phase_msgs:
        # 先頭50文字で重複チェック
        key = text[:50]
        if key not in seen_texts:
            seen_texts.add(key)
            unique.append((score, text, ym, src))

    top10 = unique[:10]

    r4.append(f"### 4.{list(phases.keys()).index(phase_name)+1} {phase_name}")
    r4.append(f"（抽出対象: {len(phase_msgs)}件 → 上位10件）")
    r4.append("")

    if not top10:
        r4.append("*該当メッセージなし*")
        r4.append("")
        continue

    for i, (score, text, ym, src) in enumerate(top10, 1):
        # テキストのクリーニング（改行→スペース、長すぎるものは省略）
        clean = text.replace('\n', ' ').replace('\r', '').strip()
        if len(clean) > 400:
            clean = clean[:400] + '…（以下略）'
        source_label = 'Web/Desktop' if src == 'web' else 'Claude Code'
        r4.append(f"**例{i}** [{ym}, {source_label}, スコア:{score:.0f}]")
        r4.append(f"> {clean}")
        r4.append("")

    print(f"  {phase_name}: {len(phase_msgs)}件から{len(top10)}件抽出")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# レポート出力
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== レポート出力 ===")

report = []
report.append("# 看護教育者とAIの協働的対話の定量分析")
report.append("")
report.append("## メタ情報")
report.append("")
report.append(f"- **分析日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
report.append(f"- **データソース1**: conversations.json（Web/Desktop版Claude, {len(conv_data)}会話）")
report.append(f"- **データソース2**: Claude Code JSONL（{len(jsonl_files)}セッション）")
report.append(f"- **総メッセージ数**: {len(all_messages):,}（うちHuman: {len(human_msgs):,}）")
report.append(f"- **分析期間**: {all_months[0]} 〜 {all_months[-1]}（{len(all_months)}か月）")
report.append(f"- **分析手法**: キーワード重み付けスコアリングによる自動分類")
report.append(f"- **分類カテゴリ**: 6分類（教育的意図/技術的指示/設計判断/品質FB/文脈補足/その他）")
report.append("")
report.append("### データソース別内訳")
report.append("")
web_h = sum(1 for m in human_msgs if m[3] is not None)  # all have dt
web_h_count = sum(1 for ym, sender, text, dt, src, ctx in all_messages if sender == 'human' and src == 'web')
cc_h_count = sum(1 for ym, sender, text, dt, src, ctx in all_messages if sender == 'human' and src == 'claude_code')
report.append(f"| ソース | Human | Assistant | 合計 |")
report.append(f"|---|---|---|---|")
web_total = sum(1 for m in all_messages if m[4] == 'web')
cc_total = sum(1 for m in all_messages if m[4] == 'claude_code')
web_a = sum(1 for ym, sender, text, dt, src, ctx in all_messages if sender == 'assistant' and src == 'web')
cc_a = sum(1 for ym, sender, text, dt, src, ctx in all_messages if sender == 'assistant' and src == 'claude_code')
report.append(f"| Web/Desktop (conversations.json) | {web_h_count:,} | {web_a:,} | {web_total:,} |")
report.append(f"| Claude Code (JSONL) | {cc_h_count:,} | {cc_a:,} | {cc_total:,} |")
report.append(f"| **合計** | **{web_h_count+cc_h_count:,}** | **{web_a+cc_a:,}** | **{len(all_messages):,}** |")

report.append("")
report.append("---")
report.append("")
report.extend(r1)
report.append("")
report.append("---")
report.append("")
report.extend(r2)
report.append("")
report.append("---")
report.append("")
report.extend(r3)
report.append("")
report.append("---")
report.append("")
report.extend(r4)

report.append("")
report.append("---")
report.append("")
report.append("## 分析手法の限界")
report.append("")
report.append("1. **分類精度**: キーワードベースの自動分類であり，文脈依存の意味的分類には限界がある．")
report.append("   特にカテゴリ間の境界が曖昧なメッセージ（例: 教育的意図を含む技術指示）では誤分類の可能性がある．")
report.append("2. **具体性指標**: 固有名詞辞書は手動構築であり，網羅性に限界がある．")
report.append("3. **シーケンス分析**: Human-Assistant間の応答関係はタイムスタンプベースの推定であり，")
report.append("   マルチターンの文脈依存関係を完全には捉えていない．")
report.append("4. **教育的専門知識の抽出**: スコアリングはキーワード頻度に基づいており，")
report.append("   暗黙的な教育的判断（例: 「それでいい」という簡潔な承認に含まれる専門的判断）は捕捉できない．")
report.append("")
report.append("---")
report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by conversations_full_analysis.py*")

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"\nレポート出力完了: {OUTPUT}")
print(f"行数: {len(report)}")
