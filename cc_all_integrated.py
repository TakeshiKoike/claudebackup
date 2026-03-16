#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全Claude Code会話データ統合サマリー
- RTX 4090 Windows主セッション (66 JSONL)
- RTX 4090 Windowsマルチエージェント (6 JSONL)
- RTX 4090 WSL Shogun (496 JSONL)
- RTX 4090 WSL サブエージェント (42 JSONL)
- MacBook (claude_code_all_logs_20260316.zip) — 全プロジェクト+サブエージェント
- 診断ログ (claude-code-logs.zip) — session-current, session-prev-subagent, history
- History: RTX Windows + RTX WSL + MacBook
"""

import json
import sys
import os
import re
import glob
from collections import defaultdict, Counter
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT = "C:/Users/kokek/OneDrive/デスクトップ/Claude_Code_全データ統合サマリー.md"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ヘルパー
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_text(msg_obj):
    """メッセージオブジェクトからテキストを抽出"""
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
                elif isinstance(c, str):
                    parts.append(c)
            text = '\n'.join(parts)
    elif isinstance(msg_obj, str):
        text = msg_obj
    return text

def extract_tools(msg_obj):
    """ツール使用を抽出"""
    tools = []
    if isinstance(msg_obj, dict):
        content = msg_obj.get('content', '')
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get('type') == 'tool_use':
                    tools.append(c.get('name', ''))
    return tools

def load_jsonl_sessions(file_list, source_label, device_label):
    """JSOINLファイルリストからセッション辞書を構築"""
    sessions = {}
    for fp in file_list:
        fname = os.path.basename(fp)
        fsize = os.path.getsize(fp)
        msgs = []
        sid = None
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
                if not sid:
                    sid = obj.get('sessionId', fname.replace('.jsonl', ''))
                msg_obj = obj.get('message', {})
                text = extract_text(msg_obj)
                tools = extract_tools(msg_obj) if sender == 'assistant' else []
                model = ''
                if isinstance(msg_obj, dict) and sender == 'assistant':
                    model = msg_obj.get('model', '')
                try:
                    dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                except:
                    continue
                msgs.append({
                    'sender': sender, 'text': text, 'dt': dt,
                    'model': model, 'tools': tools, 'text_len': len(text),
                    'source': source_label, 'device': device_label,
                })

        if msgs:
            key = f"{device_label}_{source_label}_{sid or fname}"
            sessions[key] = {
                'messages': msgs,
                'first_ts': min(m['dt'] for m in msgs),
                'last_ts': max(m['dt'] for m in msgs),
                'file': fname,
                'size': fsize,
                'source': source_label,
                'device': device_label,
            }
    return sessions

def load_history(filepath, source_label):
    """history.jsonlを読み込み"""
    entries = []
    if not os.path.exists(filepath):
        return entries
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                obj = json.loads(line)
                ts = obj.get('timestamp', 0)
                if ts > 1e12:
                    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
                else:
                    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                entries.append({
                    'text': obj.get('display', ''),
                    'dt': dt,
                    'source': source_label,
                    'project': obj.get('project', ''),
                })
            except:
                continue
    return entries

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# データ読み込み
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("=== データ読み込み ===")

all_sessions = {}

# --- 1. RTX 4090 Windows 主セッション ---
files = sorted(glob.glob(os.path.expanduser('~/.claude/projects/C--Users-kokek/*.jsonl')))
s = load_jsonl_sessions(files, 'Windows主セッション', 'RTX4090')
all_sessions.update(s)
print(f"  RTX4090 Windows主: {len(s)} sessions")

# --- 2. RTX 4090 Windows マルチエージェント ---
files = sorted(glob.glob(os.path.expanduser('~/.claude/projects/C--tools-multi-agent-shogun/*.jsonl')))
s = load_jsonl_sessions(files, 'Windowsマルチエージェント', 'RTX4090')
all_sessions.update(s)
print(f"  RTX4090 Windowsマルチ: {len(s)} sessions")

# --- 3. RTX 4090 WSL Shogun ---
wsl_dir = 'C:/Users/kokek/OneDrive/デスクトップ/Claude全やり取り_RTX4090/wsl_multi-agent-shogun'
files = sorted(glob.glob(os.path.join(wsl_dir, '*.jsonl')))
s = load_jsonl_sessions(files, 'WSL-Shogun', 'RTX4090-WSL')
all_sessions.update(s)
print(f"  RTX4090 WSL Shogun: {len(s)} sessions")

# --- 4. RTX 4090 WSL サブエージェント ---
wsl_sub_dir = 'C:/Users/kokek/OneDrive/デスクトップ/Claude全やり取り_RTX4090/wsl_subagents'
files = sorted(glob.glob(os.path.join(wsl_sub_dir, '*.jsonl')))
s = load_jsonl_sessions(files, 'WSLサブエージェント', 'RTX4090-WSL')
all_sessions.update(s)
print(f"  RTX4090 WSL Subagents: {len(s)} sessions")

# --- 5. MacBook ログ (展開済み) ---
mac_base = 'C:/Users/kokek/Downloads/claude_code_all_logs_20260316'
# メインセッション
for proj_dir in glob.glob(os.path.join(mac_base, 'projects', '*')):
    proj_name = os.path.basename(proj_dir)
    # メインJSONL
    main_files = sorted(glob.glob(os.path.join(proj_dir, '*.jsonl')))
    if main_files:
        label = f'Mac-{proj_name}'
        s = load_jsonl_sessions(main_files, label, 'MacBook')
        all_sessions.update(s)
        print(f"  MacBook {proj_name}: {len(s)} main sessions")

    # サブエージェント
    for sess_dir in glob.glob(os.path.join(proj_dir, '*', 'subagents')):
        sub_files = sorted(glob.glob(os.path.join(sess_dir, '*.jsonl')))
        if sub_files:
            s = load_jsonl_sessions(sub_files, f'Mac-sub-{proj_name}', 'MacBook')
            all_sessions.update(s)
            if s:
                print(f"    + {len(s)} subagent sessions")

# --- 6. 診断ログ (claude-code-logs.zip 展開) ---
import zipfile
diag_zip = 'C:/Users/kokek/Downloads/claude-code-logs.zip'
diag_dir = 'C:/Users/kokek/Downloads/claude-code-logs-extracted'
if not os.path.exists(diag_dir):
    with zipfile.ZipFile(diag_zip, 'r') as z:
        z.extractall(diag_dir)
diag_jsonl = sorted(glob.glob(os.path.join(diag_dir, '**', '*.jsonl'), recursive=True))
if diag_jsonl:
    s = load_jsonl_sessions(diag_jsonl, '診断ログ', 'RTX4090-current')
    # 重複チェック: 既存セッションとsessionIdが被るか確認
    new_count = 0
    for k, v in s.items():
        # 既に同じファイルがあるか簡易チェック
        dup = False
        for ek, ev in all_sessions.items():
            if ev['file'] == v['file'] and abs(len(ev['messages']) - len(v['messages'])) < 5:
                dup = True
                break
        if not dup:
            all_sessions[k] = v
            new_count += 1
    print(f"  診断ログ: {len(s)} sessions ({new_count} new)")

# --- History ---
print("\n  Loading history files...")
all_history = []
all_history.extend(load_history(os.path.expanduser('~/.claude/history.jsonl'), 'RTX4090-Windows'))
all_history.extend(load_history('C:/Users/kokek/OneDrive/デスクトップ/Claude全やり取り_RTX4090/wsl_history.jsonl', 'RTX4090-WSL'))
all_history.extend(load_history(os.path.join(mac_base, 'history.jsonl'), 'MacBook'))
# 診断ログのhistory
diag_hist = os.path.join(diag_dir, 'claude-code-logs', 'history.jsonl')
if os.path.exists(diag_hist):
    all_history.extend(load_history(diag_hist, 'RTX4090-diag'))
print(f"  Total history: {len(all_history)} entries")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 集計
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 集計 ===")

total_msgs = sum(len(s['messages']) for s in all_sessions.values())
total_human = sum(sum(1 for m in s['messages'] if m['sender'] == 'human') for s in all_sessions.values())
total_asst = sum(sum(1 for m in s['messages'] if m['sender'] == 'assistant') for s in all_sessions.values())
total_h_chars = sum(sum(m['text_len'] for m in s['messages'] if m['sender'] == 'human') for s in all_sessions.values())
total_a_chars = sum(sum(m['text_len'] for m in s['messages'] if m['sender'] == 'assistant') for s in all_sessions.values())
total_chars = total_h_chars + total_a_chars
total_size = sum(s['size'] for s in all_sessions.values()) / 1024 / 1024
total_tools = sum(sum(len(m['tools']) for m in s['messages']) for s in all_sessions.values())

print(f"  Sessions: {len(all_sessions)}")
print(f"  Messages: {total_msgs} (H:{total_human}, A:{total_asst})")
print(f"  Chars: {total_chars:,}")
print(f"  Size: {total_size:.1f} MB")
print(f"  Tools: {total_tools}")

# デバイス別
device_stats = defaultdict(lambda: {'sessions': 0, 'msgs': 0, 'h': 0, 'a': 0, 'h_chars': 0, 'a_chars': 0, 'size': 0, 'tools': 0})
for s in all_sessions.values():
    d = s['device']
    device_stats[d]['sessions'] += 1
    device_stats[d]['msgs'] += len(s['messages'])
    device_stats[d]['size'] += s['size']
    for m in s['messages']:
        if m['sender'] == 'human':
            device_stats[d]['h'] += 1
            device_stats[d]['h_chars'] += m['text_len']
        else:
            device_stats[d]['a'] += 1
            device_stats[d]['a_chars'] += m['text_len']
            device_stats[d]['tools'] += len(m['tools'])

# ソース別
source_stats = defaultdict(lambda: {'sessions': 0, 'msgs': 0, 'h': 0, 'a': 0})
for s in all_sessions.values():
    src = s['source']
    source_stats[src]['sessions'] += 1
    source_stats[src]['msgs'] += len(s['messages'])
    for m in s['messages']:
        if m['sender'] == 'human':
            source_stats[src]['h'] += 1
        else:
            source_stats[src]['a'] += 1

# 月別
monthly = defaultdict(lambda: {'sessions': set(), 'h': 0, 'a': 0, 'h_chars': 0, 'a_chars': 0, 'tools': Counter(), 'models': Counter(), 'devices': Counter()})
for sid, sdata in all_sessions.items():
    for m in sdata['messages']:
        ym = m['dt'].strftime('%Y-%m')
        monthly[ym]['sessions'].add(sid)
        if m['sender'] == 'human':
            monthly[ym]['h'] += 1
            monthly[ym]['h_chars'] += m['text_len']
        else:
            monthly[ym]['a'] += 1
            monthly[ym]['a_chars'] += m['text_len']
            for t in m['tools']:
                monthly[ym]['tools'][t] += 1
            if m['model']:
                monthly[ym]['models'][m['model']] += 1
        monthly[ym]['devices'][m['device']] += 1
all_months = sorted(monthly.keys())

# ツール全体
all_tool_counter = Counter()
for sid, sdata in all_sessions.items():
    for m in sdata['messages']:
        for t in m['tools']:
            all_tool_counter[t] += 1

# モデル全体
all_model_counter = Counter()
for sid, sdata in all_sessions.items():
    for m in sdata['messages']:
        if m['model']:
            all_model_counter[m['model']] += 1

# 時間帯
hourly = defaultdict(int)
for sid, sdata in all_sessions.items():
    for m in sdata['messages']:
        jst = m['dt'] + timedelta(hours=9)
        hourly[jst.hour] += 1

# 日別
daily = defaultdict(int)
for sid, sdata in all_sessions.items():
    for m in sdata['messages']:
        jst = m['dt'] + timedelta(hours=9)
        daily[jst.strftime('%Y-%m-%d')] += 1

# セッション別
session_list = []
for sid, sdata in all_sessions.items():
    msgs = sdata['messages']
    h_msgs = [m for m in msgs if m['sender'] == 'human']
    a_msgs = [m for m in msgs if m['sender'] == 'assistant']
    tools_total = sum(len(m['tools']) for m in a_msgs)
    duration = (sdata['last_ts'] - sdata['first_ts']).total_seconds() / 60 if sdata['first_ts'] and sdata['last_ts'] else 0
    session_list.append({
        'sid': sid, 'device': sdata['device'], 'source': sdata['source'],
        'h': len(h_msgs), 'a': len(a_msgs), 'total': len(msgs),
        'h_chars': sum(m['text_len'] for m in h_msgs),
        'a_chars': sum(m['text_len'] for m in a_msgs),
        'tools': tools_total, 'duration': duration,
        'first_ts': sdata['first_ts'], 'last_ts': sdata['last_ts'],
        'size': sdata['size'] / 1024 / 1024,
    })

# History集計
hist_monthly = defaultdict(lambda: Counter())
for h in all_history:
    ym = h['dt'].strftime('%Y-%m')
    hist_monthly[ym][h['source']] += 1

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# レポート
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== レポート出力 ===")
r = []

r.append("# Claude Code 全データ統合サマリー")
r.append(f"\n**作成日**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
r.append("")

# 総括
r.append("## 1. 総括")
r.append("")
r.append("| 項目 | 値 |")
r.append("|---|---|")
r.append(f"| 総セッション数 | {len(all_sessions):,} |")
r.append(f"| 総メッセージ数 | {total_msgs:,} |")
r.append(f"| うちHuman | {total_human:,} |")
r.append(f"| うちAssistant | {total_asst:,} |")
r.append(f"| Human総文字数 | {total_h_chars:,} |")
r.append(f"| Assistant総文字数 | {total_a_chars:,} |")
r.append(f"| **全文字数合計** | **{total_chars:,}** |")
r.append(f"| データサイズ（JSONL） | {total_size:.1f} MB |")
r.append(f"| ツール呼び出し総数 | {total_tools:,} |")
r.append(f"| History入力記録 | {len(all_history):,}件 |")
r.append(f"| 期間 | {all_months[0]} 〜 {all_months[-1]} |")
r.append(f"| 原稿用紙換算 | {total_chars//400:,}枚（400字詰め） |")
r.append(f"| 新書換算 | 約{total_chars//100000}冊 |")

# デバイス別
r.append("\n## 2. デバイス別内訳")
r.append("")
r.append("| デバイス | セッション | メッセージ | Human文字 | Asst文字 | ツール | サイズ |")
r.append("|---|---|---|---|---|---|---|")
for dev in sorted(device_stats.keys()):
    d = device_stats[dev]
    r.append(f"| {dev} | {d['sessions']} | {d['msgs']:,} | {d['h_chars']:,} | {d['a_chars']:,} | {d['tools']:,} | {d['size']/1024/1024:.1f}MB |")
r.append(f"| **合計** | **{len(all_sessions)}** | **{total_msgs:,}** | **{total_h_chars:,}** | **{total_a_chars:,}** | **{total_tools:,}** | **{total_size:.1f}MB** |")

# ソース別
r.append("\n## 3. ソース別内訳")
r.append("")
r.append("| ソース | セッション | Human | Assistant | 合計 |")
r.append("|---|---|---|---|---|")
for src, d in sorted(source_stats.items(), key=lambda x: -x[1]['msgs']):
    r.append(f"| {src} | {d['sessions']} | {d['h']:,} | {d['a']:,} | {d['msgs']:,} |")

# 月別推移
r.append("\n## 4. 月別推移")
r.append("")
r.append("| 月 | セッション | Human | Asst | 合計 | H文字 | A文字 | ツール | デバイス内訳 |")
r.append("|---|---|---|---|---|---|---|---|---|")
for ym in all_months:
    d = monthly[ym]
    total_m = d['h'] + d['a']
    tool_t = sum(d['tools'].values())
    dev_str = ', '.join(f"{k}:{v}" for k, v in d['devices'].most_common(3))
    r.append(f"| {ym} | {len(d['sessions'])} | {d['h']:,} | {d['a']:,} | {total_m:,} | {d['h_chars']:,} | {d['a_chars']:,} | {tool_t:,} | {dev_str} |")

# 日別TOP20
r.append("\n## 5. 最もアクティブだった日 TOP20")
r.append("")
r.append("| 日付 | メッセージ数 |")
r.append("|---|---|")
for day, count in sorted(daily.items(), key=lambda x: -x[1])[:20]:
    r.append(f"| {day} | {count:,} |")

# 時間帯
r.append("\n## 6. 時間帯別分布（JST）")
r.append("")
r.append("| 時間帯 | メッセージ数 | 比率 | バー |")
r.append("|---|---|---|---|")
max_h = max(hourly.values()) if hourly else 1
for h in range(24):
    n = hourly.get(h, 0)
    pct = n / total_msgs * 100
    bar = '█' * int(n / max_h * 30)
    r.append(f"| {h:02d}:00 | {n:,} | {pct:.1f}% | {bar} |")

# ツールTOP30
r.append("\n## 7. ツール使用ランキング TOP30")
r.append("")
r.append("| ツール | 回数 | 比率 |")
r.append("|---|---|---|")
tool_sum = sum(all_tool_counter.values())
for tool, count in all_tool_counter.most_common(30):
    pct = count / tool_sum * 100 if tool_sum else 0
    r.append(f"| {tool} | {count:,} | {pct:.1f}% |")

# モデル
r.append("\n## 8. 使用モデル")
r.append("")
r.append("| モデル | 回数 | 比率 |")
r.append("|---|---|---|")
model_sum = sum(all_model_counter.values())
for model, count in all_model_counter.most_common(20):
    pct = count / model_sum * 100 if model_sum else 0
    short = model if len(model) < 60 else model[:57] + '...'
    r.append(f"| {short} | {count:,} | {pct:.1f}% |")

# 大規模セッションTOP20
r.append("\n## 9. 大規模セッション TOP20")
r.append("")
r.append("| # | デバイス | ソース | 日付 | H | A | 合計 | H文字 | A文字 | ツール | サイズ |")
r.append("|---|---|---|---|---|---|---|---|---|---|---|")
session_list.sort(key=lambda x: -x['total'])
for i, s in enumerate(session_list[:20], 1):
    date = s['first_ts'].strftime('%Y-%m-%d') if s['first_ts'] else '?'
    r.append(f"| {i} | {s['device']} | {s['source'][:15]} | {date} | {s['h']} | {s['a']} | {s['total']} | {s['h_chars']:,} | {s['a_chars']:,} | {s['tools']} | {s['size']:.1f}MB |")

# History
r.append("\n## 10. History入力記録")
r.append("")
r.append("| 月 | RTX-Win | RTX-WSL | MacBook | 合計 |")
r.append("|---|---|---|---|---|")
hist_all_months = sorted(hist_monthly.keys())
for ym in hist_all_months:
    d = hist_monthly[ym]
    w = d.get('RTX4090-Windows', 0) + d.get('RTX4090-diag', 0)
    l = d.get('RTX4090-WSL', 0)
    m = d.get('MacBook', 0)
    r.append(f"| {ym} | {w} | {l} | {m} | {w+l+m} |")

# 稼働時間
total_duration = sum(s['duration'] for s in session_list if s['duration'] > 0)
active_days = len(set(
    s['first_ts'].strftime('%Y-%m-%d')
    for s in session_list if s['first_ts']
))
r.append("\n## 11. 稼働統計")
r.append("")
r.append(f"- **セッション総時間**: {total_duration:.0f}分（**{total_duration/60:.1f}時間**）")
r.append(f"- **アクティブ日数**: {active_days}日")
r.append(f"- **1日あたり平均メッセージ**: {total_msgs/max(active_days,1):.0f}")
r.append(f"- **1セッションあたり平均メッセージ**: {total_msgs/len(all_sessions):.1f}")
r.append(f"- **全文字数**: {total_chars:,}文字")
r.append(f"- **原稿用紙換算**: {total_chars//400:,}枚")
r.append(f"- **新書換算**: 約{total_chars//100000}冊（1冊10万字）")

# セッション長分布
r.append("\n## 12. セッション長分布")
r.append("")
r.append("| 区間 | 件数 | 比率 |")
r.append("|---|---|---|")
bins = [(1,5), (6,10), (11,20), (21,50), (51,100), (101,200), (201,500), (501,9999)]
for lo, hi in bins:
    label = f"{lo}-{hi}" if hi < 9999 else f"{lo}+"
    n = sum(1 for s in session_list if lo <= s['total'] <= hi)
    pct = n / len(session_list) * 100
    r.append(f"| {label}メッセージ | {n} | {pct:.1f}% |")

# 月別ツールTOP3
r.append("\n## 13. 月別主要ツールTOP3")
r.append("")
r.append("| 月 | 1位 | 2位 | 3位 |")
r.append("|---|---|---|---|")
for ym in all_months:
    top3 = monthly[ym]['tools'].most_common(3)
    cols = [f"{t}({c})" for t, c in top3]
    while len(cols) < 3:
        cols.append('-')
    r.append(f"| {ym} | {cols[0]} | {cols[1]} | {cols[2]} |")

# 月別モデルTOP3
r.append("\n## 14. 月別主要モデルTOP3")
r.append("")
r.append("| 月 | 1位 | 2位 | 3位 |")
r.append("|---|---|---|---|")
for ym in all_months:
    top3 = monthly[ym]['models'].most_common(3)
    cols = [f"{t.split('/')[-1] if '/' in t else t}({c})" for t, c in top3]
    while len(cols) < 3:
        cols.append('-')
    r.append(f"| {ym} | {cols[0]} | {cols[1]} | {cols[2]} |")

r.append(f"\n---\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by cc_all_integrated.py*")

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(r))

print(f"\nレポート出力完了: {OUTPUT}")
print(f"行数: {len(r)}")
