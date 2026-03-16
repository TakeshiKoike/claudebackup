#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全Claude Code会話ログ — 内容サマリー作成
628セッション・61,830メッセージの会話内容を読み取り、
何をやったか・成果物・時系列を人間が読めるレポートにまとめる
"""

import json
import sys
import os
import re
import glob
from collections import defaultdict, Counter
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT = "C:/Users/kokek/OneDrive/デスクトップ/Claude_Code_全会話ログまとめ.md"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# データ読み込み（前回と同じ）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def extract_text(msg_obj):
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
    return text

def load_sessions(file_list, source, device):
    sessions = {}
    for fp in file_list:
        fname = os.path.basename(fp)
        msgs = []
        sid = None
        with open(fp, 'r', encoding='utf-8') as f:
            for line in f:
                try: obj = json.loads(line)
                except: continue
                if obj.get('type') not in ('user', 'assistant'): continue
                sender = 'human' if obj['type'] == 'user' else 'assistant'
                ts_str = obj.get('timestamp', '')
                if not sid: sid = obj.get('sessionId', fname.replace('.jsonl',''))
                text = extract_text(obj.get('message', {}))
                try: dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                except: continue
                msgs.append({'sender': sender, 'text': text, 'dt': dt})
        if msgs:
            key = f"{device}_{source}_{sid or fname}"
            sessions[key] = {
                'messages': msgs, 'source': source, 'device': device,
                'first_ts': min(m['dt'] for m in msgs),
                'last_ts': max(m['dt'] for m in msgs),
                'file': fname, 'size': os.path.getsize(fp),
            }
    return sessions

print("=== データ読み込み ===")
all_sessions = {}

# RTX 4090 Windows
s = load_sessions(sorted(glob.glob(os.path.expanduser('~/.claude/projects/C--Users-kokek/*.jsonl'))), 'Win主', 'RTX4090')
all_sessions.update(s)
print(f"  RTX Win主: {len(s)}")

s = load_sessions(sorted(glob.glob(os.path.expanduser('~/.claude/projects/C--tools-multi-agent-shogun/*.jsonl'))), 'Winマルチ', 'RTX4090')
all_sessions.update(s)
print(f"  RTX Winマルチ: {len(s)}")

# RTX WSL
s = load_sessions(sorted(glob.glob('C:/Users/kokek/OneDrive/デスクトップ/Claude全やり取り_RTX4090/wsl_multi-agent-shogun/*.jsonl')), 'WSL-Shogun', 'RTX4090-WSL')
all_sessions.update(s)
print(f"  RTX WSL Shogun: {len(s)}")

s = load_sessions(sorted(glob.glob('C:/Users/kokek/OneDrive/デスクトップ/Claude全やり取り_RTX4090/wsl_subagents/*.jsonl')), 'WSLサブ', 'RTX4090-WSL')
all_sessions.update(s)
print(f"  RTX WSL Sub: {len(s)}")

# MacBook
mac_base = 'C:/Users/kokek/Downloads/claude_code_all_logs_20260316'
for proj_dir in glob.glob(os.path.join(mac_base, 'projects', '*')):
    proj_name = os.path.basename(proj_dir)
    main_files = sorted(glob.glob(os.path.join(proj_dir, '*.jsonl')))
    if main_files:
        s = load_sessions(main_files, f'Mac-{proj_name}', 'MacBook')
        all_sessions.update(s)
    for sess_dir in glob.glob(os.path.join(proj_dir, '*', 'subagents')):
        sub_files = sorted(glob.glob(os.path.join(sess_dir, '*.jsonl')))
        if sub_files:
            s = load_sessions(sub_files, f'Mac-sub', 'MacBook')
            all_sessions.update(s)

# 診断ログ
import zipfile
diag_dir = 'C:/Users/kokek/Downloads/claude-code-logs-extracted'
if not os.path.exists(diag_dir):
    with zipfile.ZipFile('C:/Users/kokek/Downloads/claude-code-logs.zip', 'r') as z:
        z.extractall(diag_dir)
diag_files = sorted(glob.glob(os.path.join(diag_dir, '**', '*.jsonl'), recursive=True))
if diag_files:
    s = load_sessions(diag_files, '診断', 'RTX4090')
    all_sessions.update(s)

print(f"  合計: {len(all_sessions)} sessions")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# セッションを日付順にソートし、各セッションの内容を要約
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== セッション内容分析 ===")

# 日付順ソート
sorted_sessions = sorted(all_sessions.items(), key=lambda x: x[1]['first_ts'])

def summarize_session(sdata):
    """セッションの内容を要約"""
    msgs = sdata['messages']
    human_msgs = [m for m in msgs if m['sender'] == 'human']
    asst_msgs = [m for m in msgs if m['sender'] == 'assistant']

    # humanの最初の5発話（セッションの目的がわかる）
    first_humans = []
    for m in human_msgs[:5]:
        t = m['text'].strip().replace('\n', ' ')[:200]
        if t:
            first_humans.append(t)

    # キーワード抽出
    all_text = ' '.join(m['text'] for m in msgs)
    all_lower = all_text.lower()

    keywords = []
    kw_list = [
        ('UE5', 'UE5'), ('MetaHuman', 'MetaHuman'), ('Unity', 'Unity'),
        ('Blender', 'Blender'), ('Three.js', 'Three.js'), ('VOICEVOX', 'VOICEVOX'),
        ('ComfyUI', 'ComfyUI'), ('Ollama', 'Ollama'), ('ffmpeg', 'ffmpeg'),
        ('リップシンク', 'リップシンク'), ('模擬患者', '模擬患者'),
        ('看護', '看護'), ('教育', '教育'), ('実習', '実習'), ('国試', '国試'),
        ('動画', '動画'), ('画像', '画像'), ('音声', '音声'), ('TTS', 'TTS'),
        ('WakuFact', 'WakuFact'), ('ICT', 'ICT'), ('DX', 'DX'),
        ('Moshi', 'Moshi'), ('PersonaPlex', 'PersonaPlex'), ('Nemotron', 'Nemotron'),
        ('tmux', 'tmux'), ('multi-agent', 'multi-agent'), ('shogun', 'shogun'),
        ('Docker', 'Docker'), ('WSL', 'WSL'), ('MCP', 'MCP'),
        ('Selenium', 'Selenium'), ('GitHub', 'GitHub'), ('git', 'git'),
        ('国家試験', '国試'), ('訪問看護', '訪問看護'), ('在宅', '在宅'),
        ('離島', '離島'), ('ジオラマ', 'ジオラマ'), ('haru', 'haru'),
        ('WebGL', 'WebGL'), ('GLB', 'GLB'), ('Sketchfab', 'Sketchfab'),
        ('Voicebox', 'Voicebox'), ('ボイスクローニング', 'ボイスクローニング'),
        ('flux', 'flux'), ('Remotion', 'Remotion'), ('React', 'React'),
        ('PPTX', 'PPTX'), ('PowerPoint', 'PowerPoint'), ('PDF', 'PDF'),
        ('経営シミュレーション', '経営シミュ'), ('看護師', '看護師'),
        ('COPD', 'COPD'), ('ビジュアルノベル', 'VN'),
        ('カンゴデラックス', 'kangodx'), ('kangodx', 'kangodx'),
        ('kango-dx', 'kango-dx'), ('論文', '論文'), ('JSISE', 'JSISE'),
        ('スクリーンショット', 'スクショ'), ('スクショ', 'スクショ'),
        ('pip', 'pip'), ('npm', 'npm'), ('Python', 'Python'),
        ('エラー', 'エラー'), ('デバッグ', 'デバッグ'),
        ('メモリ', 'メモリ'), ('CLAUDE.md', 'CLAUDE.md'),
        ('引き継ぎ', '引き継ぎ'), ('セッション', 'セッション'),
        ('レポート', 'レポート'), ('分析', '分析'),
    ]
    seen = set()
    for search, label in kw_list:
        if search.lower() in all_lower and label not in seen:
            keywords.append(label)
            seen.add(label)

    # 成果物検出（ファイル作成・出力系）
    artifacts = []
    file_patterns = re.findall(r'(?:作成|出力|保存|生成|書き込み).*?(?:\.(?:py|js|html|css|md|json|mp4|mp3|wav|png|jpg|glb|fbx|docx|pptx|bat|sh))', all_text)
    if file_patterns:
        artifacts.extend(file_patterns[:3])

    return {
        'first_humans': first_humans,
        'keywords': keywords[:15],
        'h_count': len(human_msgs),
        'a_count': len(asst_msgs),
        'total_chars': sum(len(m['text']) for m in msgs),
        'duration_min': (sdata['last_ts'] - sdata['first_ts']).total_seconds() / 60,
    }

# 日ごとにセッションをグループ化
daily_sessions = defaultdict(list)
for sid, sdata in sorted_sessions:
    jst = sdata['first_ts'] + timedelta(hours=9)
    day = jst.strftime('%Y-%m-%d')
    summary = summarize_session(sdata)
    summary['sid'] = sid
    summary['device'] = sdata['device']
    summary['source'] = sdata['source']
    summary['first_ts'] = sdata['first_ts']
    summary['size_mb'] = sdata['size'] / 1024 / 1024
    daily_sessions[day].append(summary)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Windows主セッション（ユーザー直接操作）の詳細を掘り下げ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 主セッション詳細分析 ===")

# 主セッション（WSL-Shogunやサブエージェント以外）を抽出
main_sessions = []
for sid, sdata in sorted_sessions:
    if sdata['source'] in ('Win主', 'Winマルチ') or sdata['device'] == 'MacBook':
        if 'sub' not in sdata['source']:
            summary = summarize_session(sdata)
            summary['sid'] = sid
            summary['device'] = sdata['device']
            summary['source'] = sdata['source']
            summary['first_ts'] = sdata['first_ts']
            summary['msgs'] = sdata['messages']
            main_sessions.append(summary)

print(f"  主セッション（ユーザー直接操作）: {len(main_sessions)}")

# 各主セッションから最初のhuman発話を取得してテーマを特定
session_themes = []
for s in main_sessions:
    humans = [m for m in s['msgs'] if m['sender'] == 'human']
    # 最初の3発話を結合してテーマ推定
    theme_text = ' '.join(m['text'][:300] for m in humans[:3])
    theme_lower = theme_text.lower()

    # テーマ分類
    theme = '不明'
    if any(k in theme_lower for k in ['模擬患者', 'metahuman', 'ue5', 'keiji', 'リップシンク', 'audio2face', 'ace']):
        theme = 'デジタル模擬患者（UE5/MetaHuman）'
    elif any(k in theme_lower for k in ['unity', 'ulipsync', 'cc4', 'webgl']):
        theme = 'デジタル模擬患者（Unity）'
    elif any(k in theme_lower for k in ['blender', 'three.js', 'glb', 'ジオラマ', 'haru', '離島']):
        theme = '3Dモデリング/Webサイト（Blender/Three.js）'
    elif any(k in theme_lower for k in ['wakufact', '雑学', 'ショート動画']):
        theme = 'WakuFact AI雑学動画'
    elif any(k in theme_lower for k in ['ict看護', 'ナイチンゲール', 'ふたつのict']):
        theme = 'ICT看護動画制作'
    elif any(k in theme_lower for k in ['voicebox', 'ボイスクローニング', 'qwen3-tts', 'tts audio']):
        theme = 'ボイスクローニング/TTS'
    elif any(k in theme_lower for k in ['comfyui', 'flux', '画像生成']):
        theme = 'ComfyUI/画像生成'
    elif any(k in theme_lower for k in ['moshi', 'personaplex', 'full-duplex']):
        theme = '音声対話（Moshi/PersonaPlex）'
    elif any(k in theme_lower for k in ['nemotron', 'llama', 'ollama', 'elyza', 'llm']):
        theme = 'ローカルLLM'
    elif any(k in theme_lower for k in ['multi-agent', 'shogun', 'tmux']):
        theme = 'マルチエージェント'
    elif any(k in theme_lower for k in ['skill', 'npx skills']):
        theme = 'Claude Code Skills'
    elif any(k in theme_lower for k in ['github', 'git push', 'commit', 'backup']):
        theme = 'Git/GitHub管理'
    elif any(k in theme_lower for k in ['jsise', '論文', '投稿', '学会']):
        theme = 'JSISE論文'
    elif any(k in theme_lower for k in ['国試', '国家試験', 'kokushi']):
        theme = '看護師国家試験教材'
    elif any(k in theme_lower for k in ['訪問看護', '経営', 'シミュレーション']):
        theme = '訪問看護/経営シミュレーション'
    elif any(k in theme_lower for k in ['kangodx', 'kango-dx', 'カンゴデラックス', '看護dx']):
        theme = 'カンゴデラックス'
    elif any(k in theme_lower for k in ['レポート', '分析', '統合', 'conversations']):
        theme = 'データ分析/レポート'
    elif any(k in theme_lower for k in ['selenium', 'スクショ', 'スクリーンショット']):
        theme = 'スクリーンショット/成果物整理'
    elif any(k in theme_lower for k in ['pptx', 'powerpoint', 'mp4', '動画変換']):
        theme = 'PPTX/動画変換'
    elif any(k in theme_lower for k in ['camera', 'osmo', 'カメラ']):
        theme = 'カメラ/画像認識'
    elif any(k in theme_lower for k in ['memory', 'メモリ', 'claude.md', '引き継ぎ']):
        theme = 'メモリ/セッション管理'
    elif any(k in theme_lower for k in ['セットアップ', 'install', 'setup', '環境構築']):
        theme = '環境構築'

    jst = s['first_ts'] + timedelta(hours=9)
    session_themes.append({
        'date': jst.strftime('%Y-%m-%d %H:%M'),
        'device': s['device'],
        'source': s['source'],
        'theme': theme,
        'h_count': s['h_count'],
        'a_count': s['a_count'],
        'total_chars': s['total_chars'],
        'duration': s['duration_min'],
        'first_human': s['first_humans'][0] if s['first_humans'] else '',
        'keywords': s['keywords'],
    })

# テーマ別集計
theme_counter = Counter(s['theme'] for s in session_themes)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# レポート出力
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== レポート出力 ===")
r = []

r.append("# Claude Code 全会話ログまとめ")
r.append(f"\n**作成日**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
r.append("")

# 全体概要
total_msgs = sum(len(s['messages']) for s in all_sessions.values())
total_h = sum(s['h_count'] for s in session_themes)
total_chars_all = sum(sum(len(m['text']) for m in s['messages']) for s in all_sessions.values())
r.append("## 全体概要")
r.append("")
r.append(f"RTX 4090 PC（Windows + WSL）と MacBook のClaude Code全会話ログ。")
r.append(f"**628セッション・61,830メッセージ・321万文字**（原稿用紙8,049枚 / 新書32冊相当）。")
r.append(f"期間は2026年1月〜3月16日。うちユーザー直接操作の主セッションは{len(main_sessions)}件。")
r.append(f"残りはWSL上のmulti-agent-shogun自動実行セッション（496件）とサブエージェント。")
r.append("")

# テーマ別集計
r.append("## テーマ別セッション数（ユーザー直接操作のみ）")
r.append("")
r.append("| テーマ | セッション数 |")
r.append("|---|---|")
for theme, count in theme_counter.most_common():
    r.append(f"| {theme} | {count} |")
r.append(f"| **合計** | **{len(session_themes)}** |")

# ━━ 日別の作業内容 ━━
r.append("\n## 日別作業記録")
r.append("")

for day in sorted(daily_sessions.keys()):
    sessions = daily_sessions[day]
    # 主セッション（ユーザー直接）のみ
    main = [s for s in sessions if s['source'] in ('Win主', 'Winマルチ') or (s['device'] == 'MacBook' and 'sub' not in s['source'])]
    auto = [s for s in sessions if s not in main]

    if not main and not auto:
        continue

    total_day_msgs = sum(s['h_count'] + s['a_count'] for s in sessions)
    r.append(f"### {day}（{total_day_msgs:,}メッセージ）")
    r.append("")

    if main:
        for s in main:
            jst = s['first_ts'] + timedelta(hours=9)
            time_str = jst.strftime('%H:%M')
            kw_str = ', '.join(s['keywords'][:8]) if s['keywords'] else ''
            first_h = s['first_humans'][0][:150] if s['first_humans'] else ''
            chars_k = s['total_chars'] / 1000
            dur_str = f"{s['duration_min']:.0f}分" if s['duration_min'] > 0 else ''

            r.append(f"- **[{time_str}]** [{s['device']}] {s['source']} | {s['h_count']}h/{s['a_count']}a | {chars_k:.0f}K字 | {dur_str}")
            if kw_str:
                r.append(f"  - キーワード: {kw_str}")
            if first_h:
                r.append(f"  - 最初の発話: 「{first_h}」")
            r.append("")

    if auto:
        auto_msgs = sum(s['h_count'] + s['a_count'] for s in auto)
        auto_sessions = len(auto)
        r.append(f"- *自動セッション: {auto_sessions}件, {auto_msgs:,}メッセージ*")
        r.append("")

# ━━ 主セッション全一覧（テーマ付き） ━━
r.append("\n## 主セッション全一覧")
r.append("")
r.append("| # | 日時 | デバイス | テーマ | Human | 文字数 | 時間 | 最初の発話 |")
r.append("|---|---|---|---|---|---|---|---|")
for i, s in enumerate(session_themes, 1):
    first_h = s['first_human'][:60].replace('|','｜').replace('\n',' ') if s['first_human'] else ''
    dur = f"{s['duration']:.0f}分" if s['duration'] > 0 else '-'
    chars_k = f"{s['total_chars']/1000:.0f}K"
    r.append(f"| {i} | {s['date']} | {s['device'][:6]} | {s['theme'][:20]} | {s['h_count']} | {chars_k} | {dur} | {first_h} |")

# ━━ WSL Shogun自動セッション統計 ━━
r.append("\n## WSL multi-agent-shogun 自動セッション")
r.append("")
wsl_sessions = [(sid, sdata) for sid, sdata in sorted_sessions if sdata['source'] == 'WSL-Shogun']
wsl_total_msgs = sum(len(s['messages']) for _, s in wsl_sessions)
wsl_total_chars = sum(sum(len(m['text']) for m in s['messages']) for _, s in wsl_sessions)
r.append(f"- **セッション数**: {len(wsl_sessions)}")
r.append(f"- **メッセージ数**: {wsl_total_msgs:,}")
r.append(f"- **文字数**: {wsl_total_chars:,}")
r.append(f"- **内容**: multi-agent-shogun（戦国体制→看護教育3人体制カスタマイズ版）の自動実行ログ")
r.append(f"- **特徴**: リーダー看護師+看護師2名の3ペイン構成でタスクを自動分担・実行")
r.append("")

# 日別メッセージ数
wsl_daily = defaultdict(int)
for _, sdata in wsl_sessions:
    for m in sdata['messages']:
        jst = m['dt'] + timedelta(hours=9)
        wsl_daily[jst.strftime('%Y-%m-%d')] += 1
r.append("| 日付 | メッセージ |")
r.append("|---|---|")
for day, count in sorted(wsl_daily.items(), key=lambda x: -x[1])[:10]:
    r.append(f"| {day} | {count:,} |")

# ━━ MacBookセッション詳細 ━━
r.append("\n## MacBookセッション")
r.append("")
mac_main = [s for s in session_themes if s['device'] == 'MacBook']
if mac_main:
    r.append(f"- **セッション数**: {len(mac_main)}")
    r.append(f"- **プロジェクト**: kango-deluxe, kango-dx, multi-agent-nurse, ホームディレクトリ")
    r.append("")
    r.append("| # | 日時 | テーマ | Human | 文字数 | 最初の発話 |")
    r.append("|---|---|---|---|---|---|")
    for i, s in enumerate(mac_main, 1):
        first_h = s['first_human'][:80].replace('|','｜').replace('\n',' ') if s['first_human'] else ''
        chars_k = f"{s['total_chars']/1000:.0f}K"
        r.append(f"| {i} | {s['date']} | {s['theme'][:20]} | {s['h_count']} | {chars_k} | {first_h} |")

# ━━ 時系列ナラティブ ━━
r.append("\n## 時系列ナラティブ（主要な流れ）")
r.append("")

# 週ごとにまとめ
from datetime import date as date_type

week_themes = defaultdict(list)
for s in session_themes:
    d = datetime.strptime(s['date'][:10], '%Y-%m-%d')
    # 週の月曜日を計算
    monday = d - timedelta(days=d.weekday())
    week_key = monday.strftime('%m/%d')
    week_themes[week_key].append(s['theme'])

for week, themes in sorted(week_themes.items()):
    theme_counts = Counter(themes)
    top_themes = ', '.join(f"{t}({c})" for t, c in theme_counts.most_common(3))
    r.append(f"- **{week}週**: {top_themes} — 計{len(themes)}セッション")

# ━━ 統計サマリー ━━
r.append("\n## 統計サマリー")
r.append("")
r.append("| 項目 | 値 |")
r.append("|---|---|")
r.append(f"| 全セッション | 628 |")
r.append(f"| 全メッセージ | 61,830 |")
r.append(f"| 全文字数 | 3,219,727（新書32冊分） |")
r.append(f"| ユーザー直接操作セッション | {len(main_sessions)} |")
r.append(f"| 自動実行セッション（WSL Shogun） | {len(wsl_sessions)} |")
r.append(f"| MacBookセッション | {len(mac_main)} |")
r.append(f"| データサイズ | 496.6 MB |")
r.append(f"| ツール呼び出し | 20,554回 |")
r.append(f"| History入力記録 | 8,663件 |")

r.append(f"\n---\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by cc_content_summary.py*")

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(r))

print(f"\n出力完了: {OUTPUT}")
print(f"行数: {len(r)}")
