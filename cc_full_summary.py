#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RTX 4090 PC Claude Code 全会話ログ統合サマリー
Windows + WSL の全610セッション・61,629メッセージ・505MB を統合分析
"""

import json
import sys
import os
import re
import glob
from collections import defaultdict, Counter
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT = "C:/Users/kokek/OneDrive/デスクトップ/Claude_Code_全ログ統合サマリー.md"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# データ読み込み
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("=== データ読み込み ===")

def load_jsonl_files(file_list, source_label):
    """JSOLNファイルリストからメッセージを抽出"""
    sessions = defaultdict(lambda: {'messages': [], 'first_ts': None, 'last_ts': None, 'file': '', 'size': 0})

    for fp in file_list:
        fname = os.path.basename(fp)
        fsize = os.path.getsize(fp)
        with open(fp, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except:
                    continue

                if obj.get('type') not in ('user', 'assistant'):
                    continue

                sender = 'human' if obj['type'] == 'user' else 'assistant'
                ts_str = obj.get('timestamp', '')
                sid = obj.get('sessionId', fname.replace('.jsonl', ''))
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
                            if isinstance(c, dict):
                                if c.get('type') == 'text':
                                    parts.append(c.get('text', ''))
                                elif c.get('type') == 'tool_use':
                                    parts.append(f"[tool:{c.get('name','')}]")
                                elif c.get('type') == 'tool_result':
                                    pass  # skip tool results for text analysis
                            elif isinstance(c, str):
                                parts.append(c)
                        text = '\n'.join(parts)
                elif isinstance(msg_obj, str):
                    text = msg_obj

                try:
                    dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                except:
                    continue

                # モデル情報
                model = ''
                if isinstance(msg_obj, dict) and sender == 'assistant':
                    model = msg_obj.get('model', '')

                # ツール使用
                tool_names = []
                if isinstance(msg_obj, dict):
                    content = msg_obj.get('content', '')
                    if isinstance(content, list):
                        for c in content:
                            if isinstance(c, dict) and c.get('type') == 'tool_use':
                                tool_names.append(c.get('name', ''))

                sessions[sid]['messages'].append({
                    'sender': sender,
                    'text': text,
                    'dt': dt,
                    'model': model,
                    'tools': tool_names,
                    'text_len': len(text),
                    'source': source_label,
                })
                sessions[sid]['file'] = fname
                sessions[sid]['size'] = fsize

                if not sessions[sid]['first_ts'] or dt < sessions[sid]['first_ts']:
                    sessions[sid]['first_ts'] = dt
                if not sessions[sid]['last_ts'] or dt > sessions[sid]['last_ts']:
                    sessions[sid]['last_ts'] = dt

    return dict(sessions)

# 1. Windows main sessions
win_main_dir = os.path.expanduser('~/.claude/projects/C--Users-kokek/')
win_main_files = sorted(glob.glob(os.path.join(win_main_dir, '*.jsonl')))
win_main = load_jsonl_files(win_main_files, 'Windows主セッション')
print(f"  Windows主セッション: {len(win_main)} sessions, {sum(len(s['messages']) for s in win_main.values())} msgs")

# 2. Windows multi-agent
win_ma_dir = os.path.expanduser('~/.claude/projects/C--tools-multi-agent-shogun/')
win_ma_files = sorted(glob.glob(os.path.join(win_ma_dir, '*.jsonl')))
win_ma = load_jsonl_files(win_ma_files, 'Windowsマルチエージェント')
print(f"  Windowsマルチエージェント: {len(win_ma)} sessions, {sum(len(s['messages']) for s in win_ma.values())} msgs")

# 3. WSL shogun
wsl_shogun_dir = 'C:/Users/kokek/OneDrive/デスクトップ/Claude全やり取り_RTX4090/wsl_multi-agent-shogun'
wsl_shogun_files = sorted(glob.glob(os.path.join(wsl_shogun_dir, '*.jsonl')))
wsl_shogun = load_jsonl_files(wsl_shogun_files, 'WSLマルチエージェントShogun')
print(f"  WSL Shogun: {len(wsl_shogun)} sessions, {sum(len(s['messages']) for s in wsl_shogun.values())} msgs")

# 4. WSL subagents
wsl_sub_dir = 'C:/Users/kokek/OneDrive/デスクトップ/Claude全やり取り_RTX4090/wsl_subagents'
wsl_sub_files = sorted(glob.glob(os.path.join(wsl_sub_dir, '*.jsonl')))
wsl_sub = load_jsonl_files(wsl_sub_files, 'WSLサブエージェント')
print(f"  WSL Subagents: {len(wsl_sub)} sessions, {sum(len(s['messages']) for s in wsl_sub.values())} msgs")

# 5. History files
print("  Loading history files...")
history_entries = []

hist_win = os.path.expanduser('~/.claude/history.jsonl')
with open(hist_win, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            obj = json.loads(line)
            ts = obj.get('timestamp', 0)
            dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc) if ts > 1e12 else datetime.fromtimestamp(ts, tz=timezone.utc)
            history_entries.append({
                'text': obj.get('display', ''),
                'dt': dt,
                'source': 'Windows history',
                'project': obj.get('project', ''),
            })
        except:
            continue

wsl_hist = 'C:/Users/kokek/OneDrive/デスクトップ/Claude全やり取り_RTX4090/wsl_history.jsonl'
if os.path.exists(wsl_hist):
    with open(wsl_hist, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line)
                ts = obj.get('timestamp', 0)
                dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc) if ts > 1e12 else datetime.fromtimestamp(ts, tz=timezone.utc)
                history_entries.append({
                    'text': obj.get('display', ''),
                    'dt': dt,
                    'source': 'WSL history',
                    'project': obj.get('project', ''),
                })
            except:
                continue

print(f"  History entries: {len(history_entries)}")

# 全セッション統合
all_sessions = {}
for label, data in [('win_main', win_main), ('win_ma', win_ma), ('wsl_shogun', wsl_shogun), ('wsl_sub', wsl_sub)]:
    for sid, sdata in data.items():
        all_sessions[f"{label}_{sid}"] = sdata

print(f"\n=== 統合結果 ===")
total_msgs = sum(len(s['messages']) for s in all_sessions.values())
total_human = sum(sum(1 for m in s['messages'] if m['sender'] == 'human') for s in all_sessions.values())
total_asst = sum(sum(1 for m in s['messages'] if m['sender'] == 'assistant') for s in all_sessions.values())
total_size = sum(s['size'] for s in all_sessions.values()) / 1024 / 1024
print(f"  セッション数: {len(all_sessions)}")
print(f"  総メッセージ: {total_msgs} (human: {total_human}, assistant: {total_asst})")
print(f"  データサイズ: {total_size:.1f} MB")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 分析
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 分析中 ===")

# --- セッション別統計 ---
session_stats = []
for sid, sdata in all_sessions.items():
    msgs = sdata['messages']
    h_msgs = [m for m in msgs if m['sender'] == 'human']
    a_msgs = [m for m in msgs if m['sender'] == 'assistant']

    # 総テキスト量
    h_chars = sum(m['text_len'] for m in h_msgs)
    a_chars = sum(m['text_len'] for m in a_msgs)

    # ツール使用
    all_tools = []
    for m in a_msgs:
        all_tools.extend(m['tools'])
    tool_counter = Counter(all_tools)

    # モデル
    models = Counter(m['model'] for m in a_msgs if m['model'])

    # 所要時間
    duration_min = 0
    if sdata['first_ts'] and sdata['last_ts']:
        duration_min = (sdata['last_ts'] - sdata['first_ts']).total_seconds() / 60

    source = msgs[0]['source'] if msgs else ''

    session_stats.append({
        'sid': sid,
        'source': source,
        'human_count': len(h_msgs),
        'assistant_count': len(a_msgs),
        'total_count': len(msgs),
        'h_chars': h_chars,
        'a_chars': a_chars,
        'total_chars': h_chars + a_chars,
        'tools': tool_counter,
        'total_tool_calls': len(all_tools),
        'models': models,
        'first_ts': sdata['first_ts'],
        'last_ts': sdata['last_ts'],
        'duration_min': duration_min,
        'size_mb': sdata['size'] / 1024 / 1024,
        'file': sdata['file'],
    })

# --- 月別集計 ---
monthly = defaultdict(lambda: {
    'sessions': set(), 'human': 0, 'assistant': 0, 'h_chars': 0, 'a_chars': 0,
    'tools': Counter(), 'models': Counter(), 'sources': Counter(),
})

for sid, sdata in all_sessions.items():
    for m in sdata['messages']:
        ym = m['dt'].strftime('%Y-%m')
        monthly[ym]['sessions'].add(sid)
        if m['sender'] == 'human':
            monthly[ym]['human'] += 1
            monthly[ym]['h_chars'] += m['text_len']
        else:
            monthly[ym]['assistant'] += 1
            monthly[ym]['a_chars'] += m['text_len']
            for t in m['tools']:
                monthly[ym]['tools'][t] += 1
            if m['model']:
                monthly[ym]['models'][m['model']] += 1
        monthly[ym]['sources'][m['source']] += 1

all_months = sorted(monthly.keys())

# --- ツール使用集計 ---
total_tools = Counter()
for s in session_stats:
    total_tools += s['tools']

# --- モデル使用集計 ---
total_models = Counter()
for s in session_stats:
    total_models += s['models']

# --- history分析 ---
history_monthly = defaultdict(int)
history_projects = Counter()
for h in history_entries:
    ym = h['dt'].strftime('%Y-%m')
    history_monthly[ym] += 1
    if h['project']:
        history_projects[h['project']] += 1

hist_months = sorted(history_monthly.keys())

# --- 日別アクティビティ ---
daily_msgs = defaultdict(int)
for sid, sdata in all_sessions.items():
    for m in sdata['messages']:
        day = m['dt'].strftime('%Y-%m-%d')
        daily_msgs[day] += 1

sorted_days = sorted(daily_msgs.items(), key=lambda x: -x[1])

# --- 時間帯分布 ---
hourly = defaultdict(int)
for sid, sdata in all_sessions.items():
    for m in sdata['messages']:
        # UTC+9 (JST)
        jst = m['dt'] + timedelta(hours=9)
        hourly[jst.hour] += 1

# --- ソース別統計 ---
source_stats = defaultdict(lambda: {'sessions': 0, 'msgs': 0, 'h_chars': 0, 'a_chars': 0, 'size_mb': 0})
for s in session_stats:
    src = s['source']
    source_stats[src]['sessions'] += 1
    source_stats[src]['msgs'] += s['total_count']
    source_stats[src]['h_chars'] += s['h_chars']
    source_stats[src]['a_chars'] += s['a_chars']
    source_stats[src]['size_mb'] += s['size_mb']

# --- セッション長分布 ---
session_lengths = [s['total_count'] for s in session_stats]
session_durations = [s['duration_min'] for s in session_stats if s['duration_min'] > 0]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# レポート出力
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== レポート出力 ===")

r = []
r.append("# RTX 4090 PC Claude Code 全会話ログ統合サマリー")
r.append(f"\n**作成日**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
r.append(f"**対象PC**: DESKTOP-U1U0FB6 (RTX 4090, Windows 11)")
r.append("")

# --- 総括 ---
r.append("## 1. 総括")
r.append("")
r.append("| 項目 | 値 |")
r.append("|---|---|")
r.append(f"| 総セッション数 | {len(all_sessions):,} |")
r.append(f"| 総メッセージ数 | {total_msgs:,} |")
r.append(f"| うちHuman | {total_human:,} |")
r.append(f"| うちAssistant | {total_asst:,} |")
r.append(f"| Human総文字数 | {sum(s['h_chars'] for s in session_stats):,} |")
r.append(f"| Assistant総文字数 | {sum(s['a_chars'] for s in session_stats):,} |")
r.append(f"| 全文字数合計 | {sum(s['total_chars'] for s in session_stats):,} |")
r.append(f"| データサイズ | {total_size:.1f} MB |")
r.append(f"| History入力記録 | {len(history_entries):,}件 |")
r.append(f"| 期間 | {all_months[0]} 〜 {all_months[-1]} |")
r.append(f"| ツール呼び出し総数 | {sum(s['total_tool_calls'] for s in session_stats):,} |")

# --- ソース別 ---
r.append("\n## 2. データソース別内訳")
r.append("")
r.append("| ソース | セッション | メッセージ | Human文字数 | Assistant文字数 | サイズ |")
r.append("|---|---|---|---|---|---|")
for src in ['Windows主セッション', 'Windowsマルチエージェント', 'WSLマルチエージェントShogun', 'WSLサブエージェント']:
    d = source_stats[src]
    r.append(f"| {src} | {d['sessions']} | {d['msgs']:,} | {d['h_chars']:,} | {d['a_chars']:,} | {d['size_mb']:.1f}MB |")
total_h_chars = sum(s['h_chars'] for s in session_stats)
total_a_chars = sum(s['a_chars'] for s in session_stats)
r.append(f"| **合計** | **{len(all_sessions)}** | **{total_msgs:,}** | **{total_h_chars:,}** | **{total_a_chars:,}** | **{total_size:.1f}MB** |")

# --- 月別推移 ---
r.append("\n## 3. 月別推移")
r.append("")
r.append("| 月 | セッション | Human | Assistant | 合計 | Human文字 | Asst文字 | ツール呼出 |")
r.append("|---|---|---|---|---|---|---|---|")
for ym in all_months:
    d = monthly[ym]
    total_m = d['human'] + d['assistant']
    tool_total = sum(d['tools'].values())
    r.append(f"| {ym} | {len(d['sessions'])} | {d['human']:,} | {d['assistant']:,} | {total_m:,} | {d['h_chars']:,} | {d['a_chars']:,} | {tool_total:,} |")

# 合計行
r.append(f"| **合計** | **{len(all_sessions)}** | **{total_human:,}** | **{total_asst:,}** | **{total_msgs:,}** | **{total_h_chars:,}** | **{total_a_chars:,}** | **{sum(total_tools.values()):,}** |")

# --- 日別アクティビティ TOP20 ---
r.append("\n## 4. 最もアクティブだった日 TOP20")
r.append("")
r.append("| 日付 | メッセージ数 |")
r.append("|---|---|")
for day, count in sorted_days[:20]:
    r.append(f"| {day} | {count:,} |")

# --- 時間帯分布 ---
r.append("\n## 5. 時間帯別メッセージ分布（JST）")
r.append("")
r.append("| 時間帯 | メッセージ数 | 比率 | バー |")
r.append("|---|---|---|---|")
max_h = max(hourly.values()) if hourly else 1
for h in range(24):
    n = hourly.get(h, 0)
    pct = n / total_msgs * 100
    bar_len = int(n / max_h * 30)
    bar = '█' * bar_len
    r.append(f"| {h:02d}:00-{h:02d}:59 | {n:,} | {pct:.1f}% | {bar} |")

# --- セッション長分布 ---
r.append("\n## 6. セッション長分布")
r.append("")
r.append("### メッセージ数")
r.append("| 区間 | セッション数 | 比率 |")
r.append("|---|---|---|")
len_bins = [(1,5), (6,10), (11,20), (21,50), (51,100), (101,200), (201,500), (501,9999)]
for lo, hi in len_bins:
    label = f"{lo}-{hi}" if hi < 9999 else f"{lo}+"
    n = sum(1 for l in session_lengths if lo <= l <= hi)
    pct = n / len(session_lengths) * 100
    r.append(f"| {label}メッセージ | {n} | {pct:.1f}% |")

r.append("")
r.append("### セッション時間（分）")
r.append("| 区間 | セッション数 | 比率 |")
r.append("|---|---|---|")
dur_bins = [(0,5), (5,15), (15,30), (30,60), (60,120), (120,240), (240,480), (480,99999)]
for lo, hi in dur_bins:
    label = f"{lo}-{hi}分" if hi < 99999 else f"{lo}分+"
    n = sum(1 for d in session_durations if lo <= d < hi)
    pct = n / len(session_durations) * 100 if session_durations else 0
    r.append(f"| {label} | {n} | {pct:.1f}% |")

# --- ツール使用ランキング ---
r.append("\n## 7. ツール使用ランキング TOP30")
r.append("")
r.append("| ツール名 | 呼び出し回数 | 比率 |")
r.append("|---|---|---|")
total_tool_sum = sum(total_tools.values())
for tool, count in total_tools.most_common(30):
    pct = count / total_tool_sum * 100 if total_tool_sum else 0
    r.append(f"| {tool} | {count:,} | {pct:.1f}% |")

# --- モデル使用 ---
r.append("\n## 8. 使用モデル")
r.append("")
r.append("| モデル | 使用回数 | 比率 |")
r.append("|---|---|---|")
total_model_sum = sum(total_models.values())
for model, count in total_models.most_common(20):
    pct = count / total_model_sum * 100 if total_model_sum else 0
    short = model if len(model) < 60 else model[:57] + '...'
    r.append(f"| {short} | {count:,} | {pct:.1f}% |")

# --- TOP20セッション ---
r.append("\n## 9. 大規模セッション TOP20（メッセージ数順）")
r.append("")
r.append("| # | ソース | 日付 | Human | Asst | 合計 | H文字 | A文字 | ツール | サイズ |")
r.append("|---|---|---|---|---|---|---|---|---|---|")
session_stats.sort(key=lambda x: -x['total_count'])
for i, s in enumerate(session_stats[:20], 1):
    date = s['first_ts'].strftime('%Y-%m-%d') if s['first_ts'] else '?'
    r.append(f"| {i} | {s['source'][:10]} | {date} | {s['human_count']} | {s['assistant_count']} | {s['total_count']} | {s['h_chars']:,} | {s['a_chars']:,} | {s['total_tool_calls']} | {s['size_mb']:.1f}MB |")

# --- History分析 ---
r.append("\n## 10. History入力記録")
r.append("")
r.append("History.jsonlはユーザーがClaude Codeに入力した全テキストの記録（assistant応答は含まない）．")
r.append("")

r.append("### 月別入力数")
r.append("| 月 | Windows | WSL | 合計 |")
r.append("|---|---|---|---|")
# Re-count per source
hist_win_monthly = defaultdict(int)
hist_wsl_monthly = defaultdict(int)
for h in history_entries:
    ym = h['dt'].strftime('%Y-%m')
    if h['source'] == 'Windows history':
        hist_win_monthly[ym] += 1
    else:
        hist_wsl_monthly[ym] += 1
for ym in sorted(set(list(hist_win_monthly.keys()) + list(hist_wsl_monthly.keys()))):
    w = hist_win_monthly.get(ym, 0)
    l = hist_wsl_monthly.get(ym, 0)
    r.append(f"| {ym} | {w} | {l} | {w+l} |")

r.append(f"\n**History期間**: {hist_months[0]} 〜 {hist_months[-1]}")
r.append(f"**総入力数**: Windows {sum(hist_win_monthly.values())} + WSL {sum(hist_wsl_monthly.values())} = {len(history_entries)}")

# --- 総稼働時間推定 ---
r.append("\n## 11. 稼働時間の推定")
r.append("")
total_duration = sum(s['duration_min'] for s in session_stats if s['duration_min'] > 0)
active_days = len(set(s['first_ts'].strftime('%Y-%m-%d') for s in session_stats if s['first_ts']))
r.append(f"- **セッション総時間**: {total_duration:.0f}分（{total_duration/60:.1f}時間）")
r.append(f"- **アクティブ日数**: {active_days}日")
r.append(f"- **1日あたり平均メッセージ**: {total_msgs/active_days:.0f}")
r.append(f"- **1日あたり平均セッション時間**: {total_duration/active_days:.0f}分")
r.append(f"- **1セッションあたり平均メッセージ**: {total_msgs/len(all_sessions):.1f}")
r.append(f"- **1セッションあたり平均時間**: {total_duration/len(session_durations):.1f}分" if session_durations else "")

# 文字数を原稿用紙換算
total_chars = total_h_chars + total_a_chars
r.append(f"\n### テキスト量の参考換算")
r.append(f"- **全文字数**: {total_chars:,}文字")
r.append(f"- **原稿用紙換算**: 約{total_chars//400:,}枚（400字詰め）")
r.append(f"- **新書換算**: 約{total_chars//100000:.0f}冊（1冊10万字）")
r.append(f"- **Human文字数**: {total_h_chars:,}文字（原稿用紙{total_h_chars//400:,}枚）")
r.append(f"- **Assistant文字数**: {total_a_chars:,}文字（原稿用紙{total_a_chars//400:,}枚）")

# --- 月別ツールTOP3 ---
r.append("\n## 12. 月別 主要ツール TOP3")
r.append("")
r.append("| 月 | 1位 | 2位 | 3位 |")
r.append("|---|---|---|---|")
for ym in all_months:
    d = monthly[ym]
    top3 = d['tools'].most_common(3)
    cols = []
    for t, c in top3:
        cols.append(f"{t}({c})")
    while len(cols) < 3:
        cols.append('-')
    r.append(f"| {ym} | {cols[0]} | {cols[1]} | {cols[2]} |")

# --- 全セッション一覧 ---
r.append("\n## 13. 全セッション一覧（日付・メッセージ数順）")
r.append("")
r.append("| # | 日付 | ソース | Human | Asst | 合計 | 時間(分) | ツール | サイズ |")
r.append("|---|---|---|---|---|---|---|---|---|")
session_stats.sort(key=lambda x: x['first_ts'] if x['first_ts'] else datetime.min.replace(tzinfo=timezone.utc))
for i, s in enumerate(session_stats, 1):
    date = s['first_ts'].strftime('%Y-%m-%d %H:%M') if s['first_ts'] else '?'
    dur = f"{s['duration_min']:.0f}" if s['duration_min'] > 0 else '-'
    r.append(f"| {i} | {date} | {s['source'][:12]} | {s['human_count']} | {s['assistant_count']} | {s['total_count']} | {dur} | {s['total_tool_calls']} | {s['size_mb']:.1f}MB |")

r.append(f"\n---\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by cc_full_summary.py*")

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(r))

print(f"\nレポート出力完了: {OUTPUT}")
print(f"行数: {len(r)}")
