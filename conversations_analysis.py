#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
conversations.json テキスト分析スクリプト
5つの分析を実施:
(1) 月別メッセージ長推移
(2) 肯定的表現と否定的表現の頻度比較
(3) 教育・臨床関連語彙の出現頻度
(4) 依頼文の構造パターン分類
(5) フェーズ別の語彙特徴
"""

import json
import sys
import re
from collections import defaultdict, Counter
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

INPUT = "C:/Users/kokek/Downloads/data-2026-03-15-15-02-07-batch-0000/conversations.json"
OUTPUT = "C:/Users/kokek/OneDrive/デスクトップ/conversations_analysis_result.md"

print("Loading conversations.json...")
with open(INPUT, 'r', encoding='utf-8') as f:
    data = json.load(f)

# ── メッセージ抽出 ──
messages = []  # (year_month, sender, text, created_at)
for conv in data:
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
        messages.append((ym, sender, text, dt))

messages.sort(key=lambda x: x[3])
print(f"Total messages with text: {len(messages)}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# (1) 月別メッセージ長推移
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== (1) 月別メッセージ長推移 ===")
monthly_human = defaultdict(list)
monthly_assistant = defaultdict(list)
monthly_count = defaultdict(lambda: {'human': 0, 'assistant': 0})

for ym, sender, text, dt in messages:
    length = len(text)
    if sender == 'human':
        monthly_human[ym].append(length)
        monthly_count[ym]['human'] += 1
    elif sender == 'assistant':
        monthly_assistant[ym].append(length)
        monthly_count[ym]['assistant'] += 1

all_months = sorted(set(list(monthly_human.keys()) + list(monthly_assistant.keys())))

result_1 = []
result_1.append("| 月 | Human件数 | Human平均文字数 | Human中央値 | Assistant件数 | Assistant平均文字数 | Assistant中央値 |")
result_1.append("|---|---|---|---|---|---|---|")
for ym in all_months:
    h = monthly_human.get(ym, [])
    a = monthly_assistant.get(ym, [])
    h_avg = int(sum(h)/len(h)) if h else 0
    h_med = sorted(h)[len(h)//2] if h else 0
    a_avg = int(sum(a)/len(a)) if a else 0
    a_med = sorted(a)[len(a)//2] if a else 0
    result_1.append(f"| {ym} | {len(h)} | {h_avg} | {h_med} | {len(a)} | {a_avg} | {a_med} |")
    print(f"  {ym}: Human {len(h)}件(avg {h_avg}字) / Assistant {len(a)}件(avg {a_avg}字)")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# (2) 肯定的表現と否定的表現の頻度比較
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== (2) 肯定的表現と否定的表現の頻度比較 ===")

positive_words = {
    # ユーザー側の肯定
    'ありがとう': 0, 'すごい': 0, 'いいね': 0, '素晴らしい': 0, '完璧': 0,
    'うまくいった': 0, '成功': 0, 'OK': 0, 'いい感じ': 0, '助かる': 0,
    'できた': 0, 'よかった': 0, 'うれしい': 0, '嬉しい': 0, 'さすが': 0,
    'ナイス': 0, '最高': 0, 'いいですね': 0, '了解': 0, 'おお': 0,
    'perfect': 0, 'great': 0, 'thanks': 0, 'good': 0, 'nice': 0,
    'awesome': 0, 'excellent': 0, 'amazing': 0, 'wonderful': 0, 'love': 0,
}

negative_words = {
    # ユーザー側の否定・不満
    'エラー': 0, 'error': 0, '違う': 0, 'ダメ': 0, 'だめ': 0,
    '失敗': 0, 'うまくいかない': 0, '動かない': 0, '無理': 0, 'バグ': 0,
    'おかしい': 0, '間違い': 0, '間違って': 0, '壊れ': 0, 'やり直し': 0,
    '困った': 0, 'できない': 0, '問題': 0, 'なんで': 0, 'しない': 0,
    'wrong': 0, 'fail': 0, 'broken': 0, 'not working': 0, 'bug': 0,
    'issue': 0, 'crash': 0, 'fix': 0,
}

# 月別集計
monthly_positive = defaultdict(int)
monthly_negative = defaultdict(int)
positive_by_sender = defaultdict(lambda: defaultdict(int))
negative_by_sender = defaultdict(lambda: defaultdict(int))

for ym, sender, text, dt in messages:
    text_lower = text.lower()
    for word in positive_words:
        count = text_lower.count(word.lower())
        if count > 0:
            positive_words[word] += count
            monthly_positive[ym] += count
            positive_by_sender[sender][word] += count
    for word in negative_words:
        count = text_lower.count(word.lower())
        if count > 0:
            negative_words[word] += count
            monthly_negative[ym] += count
            negative_by_sender[sender][word] += count

total_pos = sum(positive_words.values())
total_neg = sum(negative_words.values())
print(f"  肯定的表現 合計: {total_pos}")
print(f"  否定的表現 合計: {total_neg}")
print(f"  肯定/否定比: {total_pos/total_neg:.2f}" if total_neg > 0 else "  否定0")

result_2_words = []
result_2_words.append("\n### 肯定的表現 TOP20")
result_2_words.append("| 表現 | 合計 | Human | Assistant |")
result_2_words.append("|---|---|---|---|")
for w, c in sorted(positive_words.items(), key=lambda x: -x[1])[:20]:
    h = positive_by_sender['human'].get(w, 0)
    a = positive_by_sender['assistant'].get(w, 0)
    result_2_words.append(f"| {w} | {c} | {h} | {a} |")

result_2_words.append("\n### 否定的表現 TOP20")
result_2_words.append("| 表現 | 合計 | Human | Assistant |")
result_2_words.append("|---|---|---|---|")
for w, c in sorted(negative_words.items(), key=lambda x: -x[1])[:20]:
    h = negative_by_sender['human'].get(w, 0)
    a = negative_by_sender['assistant'].get(w, 0)
    result_2_words.append(f"| {w} | {c} | {h} | {a} |")

result_2_monthly = []
result_2_monthly.append("\n### 月別 肯定vs否定")
result_2_monthly.append("| 月 | 肯定 | 否定 | 比率(肯定/否定) |")
result_2_monthly.append("|---|---|---|---|")
for ym in all_months:
    p = monthly_positive.get(ym, 0)
    n = monthly_negative.get(ym, 0)
    ratio = f"{p/n:.2f}" if n > 0 else "∞"
    result_2_monthly.append(f"| {ym} | {p} | {n} | {ratio} |")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# (3) 教育・臨床関連語彙の出現頻度
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== (3) 教育・臨床関連語彙の出現頻度 ===")

edu_clinical_terms = {
    # 看護教育
    '看護': 0, '模擬患者': 0, '患者': 0, '臨床': 0, '実習': 0,
    '教育': 0, '学生': 0, '国家試験': 0, '国試': 0, '看護師': 0,
    'シミュレーション': 0, '演習': 0, '授業': 0, '教材': 0, 'カリキュラム': 0,
    'アセスメント': 0, 'フィジカルアセスメント': 0, '問診': 0, 'バイタル': 0,
    # 臨床・医療
    '訪問看護': 0, '在宅': 0, '病棟': 0, '病室': 0, '病院': 0,
    '診療': 0, '治療': 0, '手術': 0, '投薬': 0, '処方': 0,
    '症状': 0, '疾患': 0, '疾病': 0, '診断': 0, 'ケア': 0,
    'リハビリ': 0, '介護': 0, '褥瘡': 0, '感染': 0,
    # ICT・DX
    'ICT': 0, 'DX': 0, 'デジタル': 0, 'AI': 0, 'VR': 0,
    'リップシンク': 0, 'MetaHuman': 0, 'VOICEVOX': 0,
    # 技術用語
    'UE5': 0, 'Unity': 0, 'Blender': 0, 'Three.js': 0, 'Python': 0,
    'ComfyUI': 0, 'ffmpeg': 0, 'HTML': 0, 'CSS': 0, 'JavaScript': 0,
}

monthly_edu = defaultdict(lambda: defaultdict(int))

for ym, sender, text, dt in messages:
    for term in edu_clinical_terms:
        # case-sensitive for acronyms, case-insensitive for Japanese
        if term.isascii() and term[0].isupper():
            count = text.count(term)
        else:
            count = text.lower().count(term.lower())
        if count > 0:
            edu_clinical_terms[term] += count
            monthly_edu[ym][term] += count

result_3 = []
result_3.append("| 語彙 | 出現回数 |")
result_3.append("|---|---|")
for term, count in sorted(edu_clinical_terms.items(), key=lambda x: -x[1]):
    if count > 0:
        result_3.append(f"| {term} | {count} |")
        if count >= 50:
            print(f"  {term}: {count}")

# 月別の教育臨床語彙密度（上位10語彙の月別推移）
top10_terms = [t for t, c in sorted(edu_clinical_terms.items(), key=lambda x: -x[1])[:10]]
result_3_monthly = []
result_3_monthly.append("\n### 上位10語彙の月別推移")
header = "| 月 | " + " | ".join(top10_terms) + " |"
sep = "|---|" + "|".join(["---"] * len(top10_terms)) + "|"
result_3_monthly.append(header)
result_3_monthly.append(sep)
for ym in all_months:
    vals = [str(monthly_edu[ym].get(t, 0)) for t in top10_terms]
    result_3_monthly.append(f"| {ym} | " + " | ".join(vals) + " |")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# (4) 依頼文の構造パターン分類
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== (4) 依頼文の構造パターン分類 ===")

patterns = {
    '～して/～してください（直接依頼）': re.compile(r'して(ください|くれ|ほしい|下さい)?|してみて'),
    '～お願い（丁寧依頼）': re.compile(r'お願い(します|いたします|できます)?'),
    '～できますか？（可能確認型）': re.compile(r'できます(か|？)|可能(です)?か'),
    '～教えて（情報要求型）': re.compile(r'教えて(ください|くれ|ほしい)?'),
    '～作って/作成して（生成依頼型）': re.compile(r'(作って|作成して|生成して|書いて|作り)(ください|くれ|ほしい)?'),
    '～確認して（検証依頼型）': re.compile(r'(確認して|チェックして|見て|調べて)(ください|くれ|ほしい)?'),
    '～修正して/直して（修正依頼型）': re.compile(r'(修正して|直して|変更して|変えて|更新して)(ください|くれ|ほしい)?'),
    '～説明して（説明要求型）': re.compile(r'(説明して|解説して|教えて)(ください|くれ|ほしい)?'),
    '～ですか？/～ますか？（質問型）': re.compile(r'(です|ます)(か|？)\s*[？?]?$', re.MULTILINE),
    '～しよう/～しましょう（提案・協働型）': re.compile(r'(しよう|しましょう|やろう|やりましょう|いこう|いきましょう)'),
    '～とは？/～って何？（定義質問型）': re.compile(r'(とは[？?]|って何|って(なに|なん)|ってどう)'),
}

pattern_counts = defaultdict(int)
pattern_monthly = defaultdict(lambda: defaultdict(int))
pattern_examples = defaultdict(list)

for ym, sender, text, dt in messages:
    if sender != 'human':
        continue
    for name, regex in patterns.items():
        matches = regex.findall(text)
        if matches:
            pattern_counts[name] += len(matches)
            pattern_monthly[ym][name] += len(matches)
            if len(pattern_examples[name]) < 3 and len(text) < 200:
                pattern_examples[name].append(text.strip()[:100])

result_4 = []
result_4.append("| 依頼パターン | 出現回数 | 例 |")
result_4.append("|---|---|---|")
for name, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
    examples = " / ".join(pattern_examples[name][:2]).replace("|", "｜").replace("\n", " ")[:100]
    result_4.append(f"| {name} | {count} | {examples} |")
    print(f"  {name}: {count}")

# 月別推移
top_patterns = [p for p, _ in sorted(pattern_counts.items(), key=lambda x: -x[1])[:6]]
result_4_monthly = []
result_4_monthly.append("\n### 主要依頼パターンの月別推移")
header = "| 月 | " + " | ".join([p.split('（')[0] for p in top_patterns]) + " |"
sep = "|---|" + "|".join(["---"] * len(top_patterns)) + "|"
result_4_monthly.append(header)
result_4_monthly.append(sep)
for ym in all_months:
    vals = [str(pattern_monthly[ym].get(p, 0)) for p in top_patterns]
    result_4_monthly.append(f"| {ym} | " + " | ".join(vals) + " |")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# (5) フェーズ別の語彙特徴
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== (5) フェーズ別の語彙特徴 ===")

# フェーズ定義（月ベース）
phases = {
    '導入期 (2025-01〜03)': ('2025-01', '2025-03'),
    '拡張期 (2025-04〜06)': ('2025-04', '2025-06'),
    '発展期 (2025-07〜09)': ('2025-07', '2025-09'),
    '深化期 (2025-10〜12)': ('2025-10', '2025-12'),
    '統合期 (2026-01〜03)': ('2026-01', '2026-03'),
}

# 各フェーズの語彙を収集
phase_words = defaultdict(Counter)
phase_msg_count = defaultdict(int)
phase_char_count = defaultdict(int)

# 日本語のトークン化（簡易: 2-4文字のn-gram + 既知語彙）
important_vocab = [
    'UE5', 'Unity', 'Blender', 'MetaHuman', 'VOICEVOX', 'ComfyUI', 'ffmpeg',
    'Python', 'JavaScript', 'HTML', 'CSS', 'Three.js', 'React',
    '看護', '患者', '模擬患者', '教育', '臨床', '実習', '学生', '国試',
    'リップシンク', 'AI', 'VR', 'DX', 'ICT', 'デジタル',
    '訪問看護', '動画', '音声', '画像', 'API', 'MCP', 'Ollama',
    'ELYZA', 'Nemotron', 'flux', 'TTS', 'GPU', 'VRAM',
    'エラー', 'バグ', '修正', '完成', '成功', '失敗',
    'シミュレーション', 'アセスメント', 'ケア', '処方', '症状',
    'GitHub', 'WSL', 'Docker', 'npm', 'pip',
    '漫画', 'ナレーション', 'スクリプト', 'パイプライン', '自動化',
    '経営', '診療所', '離島', 'ジオラマ', 'WebGL',
]

for ym, sender, text, dt in messages:
    for phase_name, (start, end) in phases.items():
        if start <= ym <= end:
            phase_msg_count[phase_name] += 1
            phase_char_count[phase_name] += len(text)
            for vocab in important_vocab:
                if vocab.isascii() and vocab[0].isupper():
                    count = text.count(vocab)
                else:
                    count = text.lower().count(vocab.lower())
                if count > 0:
                    phase_words[phase_name][vocab] += count
            break

result_5 = []
for phase_name in phases:
    mc = phase_msg_count.get(phase_name, 0)
    cc = phase_char_count.get(phase_name, 0)
    result_5.append(f"\n### {phase_name}")
    result_5.append(f"- メッセージ数: {mc}")
    result_5.append(f"- 総文字数: {cc:,}")
    result_5.append(f"- 平均文字数/メッセージ: {cc//mc if mc else 0}")
    result_5.append("")
    top_words = phase_words[phase_name].most_common(25)
    result_5.append("| 語彙 | 出現回数 |")
    result_5.append("|---|---|")
    for word, count in top_words:
        result_5.append(f"| {word} | {count} |")
    print(f"  {phase_name}: {mc}件, top3={[w for w,c in top_words[:3]]}")

# フェーズ間の特徴語（そのフェーズで特に多い語）
result_5_unique = []
result_5_unique.append("\n### フェーズ別 特徴語（他フェーズと比較して突出している語彙）")
for phase_name in phases:
    if not phase_words[phase_name]:
        continue
    total_in_phase = sum(phase_words[phase_name].values())
    if total_in_phase == 0:
        continue
    # 各語のそのフェーズでの比率 vs 全体での比率
    all_total = sum(sum(pw.values()) for pw in phase_words.values())
    unique_scores = []
    for word, count in phase_words[phase_name].items():
        phase_ratio = count / total_in_phase
        all_count = sum(pw.get(word, 0) for pw in phase_words.values())
        all_ratio = all_count / all_total if all_total else 0
        if all_ratio > 0:
            score = phase_ratio / all_ratio
            unique_scores.append((word, score, count))
    unique_scores.sort(key=lambda x: -x[1])
    top5 = unique_scores[:5]
    result_5_unique.append(f"\n**{phase_name}**: " + ", ".join([f"{w}(x{s:.1f}, {c}回)" for w, s, c in top5]))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# レポート出力
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== レポート出力 ===")

report = []
report.append("# conversations.json テキスト分析レポート")
report.append(f"**分析日**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
report.append(f"**対象**: {len(data)}会話 / {len(messages)}メッセージ（テキスト有り）")
report.append(f"**期間**: {all_months[0]} 〜 {all_months[-1]}")
report.append("")

report.append("---")
report.append("## (1) 月別メッセージ長推移")
report.append("")
report.extend(result_1)

report.append("")
report.append("---")
report.append("## (2) 肯定的表現と否定的表現の頻度比較")
report.append(f"\n**合計**: 肯定 {total_pos} / 否定 {total_neg} / 比率 {total_pos/total_neg:.2f}" if total_neg else "")
report.extend(result_2_words)
report.extend(result_2_monthly)

report.append("")
report.append("---")
report.append("## (3) 教育・臨床関連語彙の出現頻度")
report.append("")
report.extend(result_3)
report.extend(result_3_monthly)

report.append("")
report.append("---")
report.append("## (4) 依頼文の構造パターン分類（Human発話のみ）")
report.append("")
report.extend(result_4)
report.extend(result_4_monthly)

report.append("")
report.append("---")
report.append("## (5) フェーズ別の語彙特徴")
report.extend(result_5)
report.extend(result_5_unique)

report.append("\n---\n*Generated by conversations_analysis.py*")

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"\nレポート出力完了: {OUTPUT}")
print(f"合計 {len(report)} 行")
