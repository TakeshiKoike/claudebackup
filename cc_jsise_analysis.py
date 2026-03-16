#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Claude Code 全データ JSISE論文用分析
RTX4090(Win+WSL) + MacBook 628セッション・61,830メッセージ

分析1: 全humanメッセージの6分類コーディング（月別比率推移）
分析2: やり取りのシーケンスパターン（協働パターン抽出）
分析3: 1メッセージあたりの具体性の推移（固有名詞・技術用語・数値密度）
分析4: 教育的専門知識の言語化の実例（フェーズ別10件抽出）
"""

import json, sys, os, re, glob
from collections import defaultdict, Counter
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT = "C:/Users/kokek/OneDrive/デスクトップ/Claude_Code_JSISE分析.md"

# ━━━ データ読み込み ━━━
print("=== データ読み込み ===")

def extract_text(msg_obj):
    if isinstance(msg_obj, dict):
        content = msg_obj.get('content', '')
        if isinstance(content, str): return content
        if isinstance(content, list):
            return '\n'.join(
                c.get('text','') if isinstance(c,dict) and c.get('type')=='text'
                else c if isinstance(c,str) else ''
                for c in content)
    elif isinstance(msg_obj, str): return msg_obj
    return ''

def extract_tools(msg_obj):
    tools = []
    if isinstance(msg_obj, dict):
        content = msg_obj.get('content', '')
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get('type') == 'tool_use':
                    tools.append(c.get('name', ''))
    return tools

def load_jsonl(file_list, source, device):
    sessions = {}
    for fp in file_list:
        fname = os.path.basename(fp)
        msgs = []; sid = None
        with open(fp, 'r', encoding='utf-8') as f:
            for line in f:
                try: obj = json.loads(line)
                except: continue
                if obj.get('type') not in ('user','assistant'): continue
                sender = 'human' if obj['type']=='user' else 'assistant'
                ts = obj.get('timestamp','')
                if not sid: sid = obj.get('sessionId', fname.replace('.jsonl',''))
                text = extract_text(obj.get('message',{}))
                tools = extract_tools(obj.get('message',{})) if sender=='assistant' else []
                model = ''
                if isinstance(obj.get('message'), dict) and sender=='assistant':
                    model = obj['message'].get('model','')
                try: dt = datetime.fromisoformat(ts.replace('Z','+00:00'))
                except: continue
                msgs.append({'sender':sender,'text':text,'dt':dt,'model':model,'tools':tools,'text_len':len(text)})
        if msgs:
            key = f"{device}_{source}_{sid or fname}"
            sessions[key] = {'messages':msgs, 'source':source, 'device':device,
                'first_ts':min(m['dt'] for m in msgs), 'last_ts':max(m['dt'] for m in msgs)}
    return sessions

all_sessions = {}

# RTX4090 Windows
s = load_jsonl(sorted(glob.glob(os.path.expanduser('~/.claude/projects/C--Users-kokek/*.jsonl'))), 'Win主', 'RTX4090')
all_sessions.update(s); print(f"  RTX Win主: {len(s)}")
s = load_jsonl(sorted(glob.glob(os.path.expanduser('~/.claude/projects/C--tools-multi-agent-shogun/*.jsonl'))), 'Winマルチ', 'RTX4090')
all_sessions.update(s); print(f"  RTX Winマルチ: {len(s)}")

# RTX4090 WSL
s = load_jsonl(sorted(glob.glob('C:/Users/kokek/OneDrive/デスクトップ/Claude全やり取り_RTX4090/wsl_multi-agent-shogun/*.jsonl')), 'WSL-Shogun', 'RTX4090-WSL')
all_sessions.update(s); print(f"  WSL Shogun: {len(s)}")
s = load_jsonl(sorted(glob.glob('C:/Users/kokek/OneDrive/デスクトップ/Claude全やり取り_RTX4090/wsl_subagents/*.jsonl')), 'WSLサブ', 'RTX4090-WSL')
all_sessions.update(s); print(f"  WSL Sub: {len(s)}")

# MacBook
mac_base = 'C:/Users/kokek/Downloads/claude_code_all_logs_20260316'
for proj_dir in glob.glob(os.path.join(mac_base, 'projects', '*')):
    pn = os.path.basename(proj_dir)
    mf = sorted(glob.glob(os.path.join(proj_dir, '*.jsonl')))
    if mf:
        s = load_jsonl(mf, f'Mac-{pn}', 'MacBook'); all_sessions.update(s)
    for sd in glob.glob(os.path.join(proj_dir, '*', 'subagents')):
        sf = sorted(glob.glob(os.path.join(sd, '*.jsonl')))
        if sf:
            s = load_jsonl(sf, f'Mac-sub', 'MacBook'); all_sessions.update(s)

# 診断ログ
import zipfile
diag_dir = 'C:/Users/kokek/Downloads/claude-code-logs-extracted'
if not os.path.exists(diag_dir):
    with zipfile.ZipFile('C:/Users/kokek/Downloads/claude-code-logs.zip','r') as z: z.extractall(diag_dir)
df = sorted(glob.glob(os.path.join(diag_dir,'**','*.jsonl'), recursive=True))
if df:
    s = load_jsonl(df, '診断', 'RTX4090'); all_sessions.update(s)

# 全メッセージ統合
all_messages = []
for sid, sdata in all_sessions.items():
    for m in sdata['messages']:
        ym = m['dt'].strftime('%Y-%m')
        all_messages.append((ym, m['sender'], m['text'], m['dt'], sdata['source'], sdata['device'], sid))

all_messages.sort(key=lambda x: x[3])
human_msgs = [(ym,text,dt,src,dev,sid) for ym,sender,text,dt,src,dev,sid in all_messages if sender=='human']
all_months = sorted(set(m[0] for m in all_messages))

print(f"\n  統合: {len(all_sessions)} sessions, {len(all_messages)} msgs, human={len(human_msgs)}")
print(f"  期間: {all_months[0]} 〜 {all_months[-1]}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 分析1: 6分類コーディング
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 分析1: メッセージコーディング ===")

def classify(text):
    scores = {'A':0,'B':0,'C':0,'D':0,'E':0,'F':0}
    t = text.lower()
    # A: 教育的意図
    for kw,w in [('看護教育',3),('学習目標',3),('臨床',2),('実習',2),('学生',2),('教育',2),('患者',1.5),
        ('模擬患者',3),('看護師',1.5),('国家試験',2),('国試',2),('アセスメント',2),('フィジカル',2),
        ('バイタル',2),('教材',2),('カリキュラム',2),('授業',2),('演習',2),('シミュレーション',1.5),
        ('看護',1),('ケア',1.5),('症状',1.5),('診断',1.5),('疾患',1.5),('訪問看護',2),('在宅',1.5),
        ('介護',1.5),('褥瘡',2),('問診',2),('処方',1.5),('病棟',1.5),('臨床判断',3),('看護過程',3),
        ('看護計画',3),('指導',1.5),('copd',2),('糖尿病',2),('ナイチンゲール',2),('経営シミュ',2)]:
        if kw in t: scores['A'] += w * t.count(kw)
    # B: 技術的指示
    for kw,w in [('コード',2),('実装',2),('修正して',3),('直して',2),('変更して',2),('作って',2),
        ('作成して',2),('書いて',1.5),('追加して',2),('削除して',2),('エラー',1.5),('バグ',2),
        ('動かない',2),('インストール',2),('セットアップ',2),('設定',1.5),('python',1.5),
        ('javascript',1.5),('html',1.5),('css',1.5),('api',1.5),('npm',2),('pip',2),('git',1.5),
        ('ffmpeg',2),('コンパイル',2),('ビルド',1.5),('デプロイ',2),('ファイル',1),('フォルダ',1),
        ('パス',1),('コマンド',1.5),('スクリプト',1.5),('関数',1.5),('ue5',2),('unity',2),
        ('blender',2),('comfyui',2),('voicevox',2),('ollama',2),('docker',2),('wsl',1.5),
        ('three.js',2),('react',1.5),('metahuman',2),('mcp',1.5),('セットアップ',2),
        ('導入',1.5),('起動',1.5),('実行',1.5),('ダウンロード',1.5)]:
        if kw in t: scores['B'] += w * t.count(kw)
    # C: 設計判断
    for kw,w in [('構造',2),('アーキテクチャ',3),('設計',2),('テンプレート',2),('パイプライン',2),
        ('ワークフロー',2),('方針',2),('戦略',2),('どっちがいい',3),('どちらがいい',3),('比較',1.5),
        ('選択',1.5),('パターン',1.5),('フレームワーク',2),('分離',1.5),('統合',1.5),('自動化',2),
        ('代替',2),('候補',1.5),('提案',1.5),('アプローチ',2),('全体像',2),('構成',1.5),
        ('にしよう',1.5),('にしましょう',1.5)]:
        if kw in t: scores['C'] += w * t.count(kw)
    # D: 品質フィードバック
    for kw,w in [('ありがとう',2),('すごい',2),('いいね',2),('素晴らしい',2),('完璧',3),('ok',1.5),
        ('いい感じ',2),('助かる',2),('できた',1.5),('よかった',1.5),('さすが',2),('最高',2),
        ('違う',2),('ダメ',2),('だめ',2),('間違い',2),('間違って',2),('やり直し',3),
        ('もう一度',1.5),('こうじゃない',3),('そうじゃなく',3),('惜しい',2),('うまくいった',2),
        ('成功',1.5),('失敗',1.5),('perfect',2),('great',1.5),('good',1),('nice',1.5),
        ('wrong',2),('いいけど',1.5)]:
        if kw in t: scores['D'] += w * t.count(kw)
    # E: コンテキスト補足
    for kw,w in [('前回',3),('引き継ぎ',3),('続き',2),('さっき',2),('先ほど',2),('ちなみに',2),
        ('補足',3),('背景',2),('経緯',2),('状況',1.5),('実は',2),('というのも',2),('参考に',2),
        ('読んで',1.5),('確認して',1),('ところで',1.5),('報告',1.5),('セッション',1.5),
        ('メモリ',1.5),('claude.md',2),('memory',1.5),('handoff',2)]:
        if kw in t: scores['E'] += w * t.count(kw)
    mx = max(scores.values())
    if mx < 1.5: return 'F'
    return max(scores, key=scores.get)

cat_names = {'A':'教育的意図の伝達','B':'技術的指示','C':'設計判断','D':'品質フィードバック','E':'コンテキスト補足','F':'その他'}
cat_defs = {
    'A':'学習目標，学生の理解度，臨床的背景など教育的文脈の伝達',
    'B':'具体的な実装指示，コード修正依頼，環境構築・ツール導入の指示',
    'C':'構造の決定，テンプレート化，アーキテクチャ・方針選択に関する判断',
    'D':'肯定的・否定的評価，成果物への修正要求',
    'E':'前回セッションからの引き継ぎ，状況説明，背景情報の補足',
    'F':'上記に該当しない発話（挨拶，短い確認応答等）',
}

classified = []
monthly_cats = defaultdict(Counter)
total_cats = Counter()
device_cats = defaultdict(Counter)

for ym,text,dt,src,dev,sid in human_msgs:
    cat = classify(text)
    classified.append((ym,cat,text,dt,src,dev,sid))
    monthly_cats[ym][cat] += 1
    total_cats[cat] += 1
    device_cats[dev][cat] += 1

for cat in 'ABCDEF':
    n = total_cats[cat]; pct = n/len(human_msgs)*100
    print(f"  {cat}: {cat_names[cat]} = {n} ({pct:.1f}%)")

# フェーズ定義（Claude Codeは2026-01〜03のみ）
phases = {
    '初期 (2026-01)': ('2026-01','2026-01'),
    '前期 (2026-02前半)': ('2026-02','2026-02'),  # 月単位で分割
    '後期 (2026-03)': ('2026-03','2026-03'),
}
# より細かくweek単位でフェーズ定義
week_phases = {
    '第1週 (2/14-2/20)': [],
    '第2週 (2/21-2/27)': [],
    '第3週 (2/28-3/6)': [],
    '第4週 (3/7-3/13)': [],
    '第5週 (3/14-3/16)': [],
}
for ym,cat,text,dt,src,dev,sid in classified:
    jst = dt + timedelta(hours=9)
    d = jst.date()
    from datetime import date
    if d < date(2026,2,21): wp = '第1週 (2/14-2/20)'
    elif d < date(2026,2,28): wp = '第2週 (2/21-2/27)'
    elif d < date(2026,3,7): wp = '第3週 (2/28-3/6)'
    elif d < date(2026,3,14): wp = '第4週 (3/7-3/13)'
    else: wp = '第5週 (3/14-3/16)'
    week_phases[wp].append((cat,text,dt,src,dev))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 分析2: シーケンスパターン
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 分析2: シーケンスパターン ===")

# セッション単位でシーケンス構築
bigrams = Counter(); trigrams = Counter()
cat_transitions = Counter()
conv_lengths = []

# 協働パターン用3-gram
cat_trigrams = Counter()

for sid, sdata in all_sessions.items():
    msgs = sdata['messages']
    conv_lengths.append(len(msgs))
    senders = [m['sender'] for m in msgs]
    # sender bigrams
    for i in range(len(senders)-1):
        bigrams[(senders[i],senders[i+1])] += 1
    for i in range(len(senders)-2):
        trigrams[(senders[i],senders[i+1],senders[i+2])] += 1
    # human分類遷移
    h_cats = [classify(m['text']) for m in msgs if m['sender']=='human']
    for i in range(len(h_cats)-1):
        cat_transitions[(h_cats[i],h_cats[i+1])] += 1
    for i in range(len(h_cats)-2):
        cat_trigrams[(h_cats[i],h_cats[i+1],h_cats[i+2])] += 1

total_bi = sum(bigrams.values())
print(f"  会話数: {len(all_sessions)}, 平均長: {sum(conv_lengths)/len(conv_lengths):.1f}")

# ツール使用パターン分析
tool_after_human = Counter()  # human発話分類→次のassistantのツール
for sid, sdata in all_sessions.items():
    msgs = sdata['messages']
    for i in range(len(msgs)-1):
        if msgs[i]['sender'] == 'human' and msgs[i+1]['sender'] == 'assistant':
            cat = classify(msgs[i]['text'])
            for t in msgs[i+1].get('tools', []):
                tool_after_human[(cat, t)] += 1

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 分析3: 具体性の推移
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 分析3: 具体性 ===")

proper_nouns = set([
    'UE5','Unity','Blender','MetaHuman','VOICEVOX','ComfyUI','ELYZA','Nemotron','Ollama',
    'Docker','WSL','NVIDIA','RTX','CUDA','Three.js','React','Next.js','Python','JavaScript',
    'TypeScript','HTML','CSS','ffmpeg','Git','GitHub','npm','pip','COPD','VR','AR','DX','ICT',
    'AI','LLM','TTS','MCP','Moshi','PersonaPlex','Qwen','Flux','Remotion','WebGL','OpenCV',
    'GGUF','tmux','MSYS2','Selenium','PowerPoint','PPTX','Voicebox','WakuFact','Audio2Face',
    'ACE','uLipSync','KEIJI','Windows','Linux','Ubuntu','Mac','Chrome','API','REST','JSON',
    'JSONL','CSV','MD','PDF','GLB','FBX','PNG','JPG','MP4','WAV','Sketchfab','PolyHaven',
    'Hyper3D','JSISE','kangodx','Shogun',
])
num_pat = re.compile(r'\b\d+(\.\d+)?\b')
path_pat = re.compile(r'[A-Za-z]:\\[^\s]+|/[a-z][^\s]*|https?://[^\s]+|localhost:\d+')

def calc_specificity(text):
    t_lower = text.lower()
    nouns = sum(1 for pn in proper_nouns if pn.lower() in t_lower)
    nums = len(num_pat.findall(text))
    paths = len(path_pat.findall(text))
    length = max(len(text),1)
    density = (nouns + nums + paths) / length * 100
    return nouns, nums, paths, density

monthly_spec = defaultdict(lambda: {'nouns':[],'nums':[],'paths':[],'density':[],'lengths':[]})
for ym,text,dt,src,dev,sid in human_msgs:
    n,nu,p,d = calc_specificity(text)
    monthly_spec[ym]['nouns'].append(n); monthly_spec[ym]['nums'].append(nu)
    monthly_spec[ym]['paths'].append(p); monthly_spec[ym]['density'].append(d)
    monthly_spec[ym]['lengths'].append(len(text))

# 週別の具体性
week_spec = defaultdict(lambda: {'nouns':[],'nums':[],'paths':[],'density':[],'lengths':[]})
for ym,text,dt,src,dev,sid in human_msgs:
    jst = dt + timedelta(hours=9)
    d_date = jst.date()
    from datetime import date
    if d_date < date(2026,2,21): wp = '第1週 (2/14-2/20)'
    elif d_date < date(2026,2,28): wp = '第2週 (2/21-2/27)'
    elif d_date < date(2026,3,7): wp = '第3週 (2/28-3/6)'
    elif d_date < date(2026,3,14): wp = '第4週 (3/7-3/13)'
    else: wp = '第5週 (3/14-3/16)'
    n,nu,p,dens = calc_specificity(text)
    week_spec[wp]['nouns'].append(n); week_spec[wp]['nums'].append(nu)
    week_spec[wp]['paths'].append(p); week_spec[wp]['density'].append(dens)
    week_spec[wp]['lengths'].append(len(text))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 分析4: 教育的専門知識の言語化
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== 分析4: 教育的専門知識 ===")

edu_kw_w = [
    ('看護教育',5),('模擬患者',5),('臨床判断',5),('看護過程',5),('フィジカルアセスメント',5),
    ('シミュレーション教育',5),('学習目標',4),('臨床実習',4),('OSCE',5),('カリキュラム',4),
    ('教育効果',4),('看護計画',4),('看護診断',4),('問診',3),('バイタルサイン',4),
    ('患者理解',4),('コミュニケーション',3),('学生',3),('臨床',2),('教育',2),('実習',2),
    ('看護師',2),('患者',2),('症状',2),('アセスメント',3),('ケア',2),('訪問看護',3),
    ('経営',3),('国家試験',3),('看護技術',4),('COPD',3),('デジタル模擬患者',5),
    ('ビジュアルノベル',3),('ナイチンゲール',3),('ICT',2),('DX',2),
]

def edu_score(text):
    t = text.lower(); score = 0
    for kw,w in edu_kw_w:
        if kw.lower() in t: score += w
    if len(text) > 2000: score *= 0.3
    if len(text) < 15: score *= 0.2
    return score

# 週フェーズ別に抽出
r4 = []
r4.append("## 分析4: 教育的専門知識の言語化の実例（Claude Code版）")
r4.append("")
r4.append("各フェーズから，教育的専門知識スコアの高い代表的発話を10件ずつ抽出した．")
r4.append("Claude Codeではユーザーがターミナル環境でAIに直接指示するため，")
r4.append("Web/Desktop版と比較してより具体的・技術的な文脈で教育的知識が言語化される傾向がある．")
r4.append("")

for wp_name in ['第1週 (2/14-2/20)','第2週 (2/21-2/27)','第3週 (2/28-3/6)','第4週 (3/7-3/13)','第5週 (3/14-3/16)']:
    items = week_phases[wp_name]
    scored = []
    for cat,text,dt,src,dev in items:
        sc = edu_score(text)
        if sc >= 2:
            scored.append((sc,text,dt,src,dev))
    scored.sort(key=lambda x: -x[0])
    seen = set(); unique = []
    for sc,text,dt,src,dev in scored:
        key = text[:50]
        if key not in seen: seen.add(key); unique.append((sc,text,dt,src,dev))
    top10 = unique[:10]

    idx = list(week_phases.keys()).index(wp_name) + 1
    r4.append(f"### 4.{idx} {wp_name}")
    r4.append(f"（抽出対象: {len(scored)}件 → 上位{len(top10)}件）")
    r4.append("")
    if not top10:
        r4.append("*該当メッセージなし*"); r4.append(""); continue
    for i,(sc,text,dt,src,dev) in enumerate(top10,1):
        clean = text.replace('\n',' ').replace('\r','').strip()
        if len(clean) > 400: clean = clean[:400] + '…（以下略）'
        jst = dt + timedelta(hours=9)
        r4.append(f"**例{i}** [{jst.strftime('%m/%d %H:%M')}, {dev}, スコア:{sc:.0f}]")
        r4.append(f"> {clean}")
        r4.append("")
    print(f"  {wp_name}: {len(scored)}→{len(top10)}件")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# レポート出力
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n=== レポート出力 ===")
r = []

r.append("# Claude Code会話ログの定量分析（JSISE論文用）")
r.append("")
r.append("## メタ情報")
r.append("")
r.append(f"- **分析日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
r.append(f"- **データソース**: Claude Code JSONL（RTX 4090 Win/WSL + MacBook）")
r.append(f"- **総セッション数**: {len(all_sessions):,}")
r.append(f"- **総メッセージ数**: {len(all_messages):,}（うちHuman: {len(human_msgs):,}）")
r.append(f"- **分析期間**: {all_months[0]} 〜 {all_months[-1]}")
r.append(f"- **分析手法**: キーワード重み付けスコアリングによる自動分類")
r.append("")

# デバイス別内訳
r.append("### データソース別内訳")
r.append("")
r.append("| デバイス・ソース | セッション | Human | Assistant | 合計 |")
r.append("|---|---|---|---|---|")
src_count = defaultdict(lambda: {'s':set(),'h':0,'a':0})
for sid,sdata in all_sessions.items():
    key = f"{sdata['device']} / {sdata['source']}"
    src_count[key]['s'].add(sid)
    for m in sdata['messages']:
        if m['sender']=='human': src_count[key]['h']+=1
        else: src_count[key]['a']+=1
for key in sorted(src_count.keys(), key=lambda k: -src_count[k]['h']-src_count[k]['a']):
    d = src_count[key]
    r.append(f"| {key} | {len(d['s'])} | {d['h']:,} | {d['a']:,} | {d['h']+d['a']:,} |")
r.append(f"| **合計** | **{len(all_sessions)}** | **{len(human_msgs):,}** | **{len(all_messages)-len(human_msgs):,}** | **{len(all_messages):,}** |")

# ━━ 分析1 ━━
r.append("\n---\n")
r.append("## 分析1: Humanメッセージの発話行為コーディング")
r.append("")
r.append("### 1.1 コーディングスキーム")
r.append("")
r.append("| コード | カテゴリ | 定義 | 件数 | 比率 |")
r.append("|---|---|---|---|---|")
for cat in 'ABCDEF':
    n = total_cats[cat]; pct = n/len(human_msgs)*100
    r.append(f"| {cat} | {cat_names[cat]} | {cat_defs[cat]} | {n:,} | {pct:.1f}% |")

r.append(f"\n**分析対象**: {len(human_msgs):,} Humanメッセージ")

r.append("\n### 1.2 月別コーディング比率の推移")
r.append("")
r.append("| 月 | 総数 | A:教育意図 | B:技術指示 | C:設計判断 | D:品質FB | E:文脈補足 | F:その他 |")
r.append("|---|---|---|---|---|---|---|---|")
for ym in all_months:
    cats = monthly_cats[ym]; total = sum(cats.values())
    if total == 0: continue
    vals = [f"{cats[c]} ({cats[c]/total*100:.0f}%)" for c in 'ABCDEF']
    r.append(f"| {ym} | {total} | " + " | ".join(vals) + " |")

r.append("\n### 1.3 週別コーディング比率")
r.append("")
r.append("| フェーズ | 総数 | A:教育意図 | B:技術指示 | C:設計判断 | D:品質FB | E:文脈補足 | F:その他 |")
r.append("|---|---|---|---|---|---|---|---|")
for wp_name in week_phases:
    items = week_phases[wp_name]
    if not items: continue
    wc = Counter(cat for cat,_,_,_,_ in items)
    total = sum(wc.values())
    vals = [f"{wc[c]} ({wc[c]/total*100:.0f}%)" for c in 'ABCDEF']
    r.append(f"| {wp_name} | {total} | " + " | ".join(vals) + " |")

r.append("\n### 1.4 デバイス別コーディング比率")
r.append("")
r.append("| デバイス | 総数 | A:教育意図 | B:技術指示 | C:設計判断 | D:品質FB | E:文脈補足 | F:その他 |")
r.append("|---|---|---|---|---|---|---|---|")
for dev in sorted(device_cats.keys()):
    dc = device_cats[dev]; total = sum(dc.values())
    if total == 0: continue
    vals = [f"{dc[c]} ({dc[c]/total*100:.0f}%)" for c in 'ABCDEF']
    r.append(f"| {dev} | {total} | " + " | ".join(vals) + " |")

# ━━ 分析2 ━━
r.append("\n---\n")
r.append("## 分析2: やり取りのシーケンスパターン")
r.append("")
r.append("### 2.1 基本統計")
r.append("")
r.append(f"- 総セッション数: {len(all_sessions):,}")
r.append(f"- メッセージ数/セッション: 平均 {sum(conv_lengths)/len(conv_lengths):.1f}, 中央値 {sorted(conv_lengths)[len(conv_lengths)//2]}")
r.append(f"- 最長セッション: {max(conv_lengths)} メッセージ")

r.append("\n### 2.2 発話者遷移パターン（2-gram）")
r.append("")
r.append("| パターン | 頻度 | 比率 |")
r.append("|---|---|---|")
for (a,b),count in bigrams.most_common():
    pct = count/total_bi*100
    r.append(f"| {a} → {b} | {count:,} | {pct:.1f}% |")

r.append("\n### 2.3 発話者遷移パターン（3-gram）")
r.append("")
r.append("| パターン | 頻度 |")
r.append("|---|---|")
for pat,count in trigrams.most_common(8):
    r.append(f"| {'→'.join(pat)} | {count:,} |")

r.append("\n### 2.4 Human発話の分類遷移パターン TOP20")
r.append("")
r.append("| 遷移 | 頻度 | 解釈 |")
r.append("|---|---|---|")
interps = {
    ('B','B'):'連続的技術指示（段階的な実装の進行）',
    ('B','D'):'実装結果への評価（指示→確認サイクル）',
    ('D','B'):'評価後の次の指示（フィードバック駆動型開発）',
    ('A','B'):'教育的文脈提示→技術的実装依頼',
    ('B','A'):'技術実装後に教育的観点から再評価',
    ('B','C'):'実装中に設計判断が必要になった場面',
    ('C','B'):'設計決定後の実装着手',
    ('D','D'):'連続的フィードバック（品質の段階的調整）',
    ('E','B'):'文脈共有→作業開始（セッション再開パターン）',
    ('A','A'):'教育的議論の深化',
    ('F','B'):'確認後の技術指示',
    ('B','F'):'技術指示後の簡易確認',
    ('B','E'):'実装中の追加文脈提供',
    ('F','F'):'短い応答の連続（確認のやり取り）',
    ('E','A'):'文脈共有→教育的意図の説明',
    ('C','C'):'設計議論の継続',
    ('A','C'):'教育目標→設計判断',
    ('A','D'):'教育的意図の提示→成果評価',
    ('D','A'):'評価→教育的観点からの再指示',
    ('E','E'):'文脈情報の追加提供',
}
for (a,b),count in cat_transitions.most_common(20):
    interp = interps.get((a,b),'')
    r.append(f"| {cat_names[a]}({a})→{cat_names[b]}({b}) | {count:,} | {interp} |")

# 協働パターン（3-gram）
r.append("\n### 2.5 典型的な協働パターン（Human発話3-gram）")
r.append("")
r.append("| パターン | 頻度 | 解釈 |")
r.append("|---|---|---|")
trigram_interps = {
    ('B','B','B'):'連続的技術指示（集中実装フェーズ）',
    ('B','D','B'):'実装→評価→修正の反復サイクル',
    ('B','B','D'):'連続実装後の評価',
    ('F','F','F'):'短い応答の連続',
    ('F','B','F'):'技術指示の前後に確認',
    ('F','F','B'):'確認を経て技術指示へ',
    ('B','F','B'):'技術指示→簡易確認→次の指示',
    ('F','B','B'):'確認後に連続実装',
    ('D','B','B'):'評価後の連続実装',
    ('B','B','F'):'連続実装後に確認',
    ('A','B','D'):'教育意図→実装→評価（教育者主導サイクル）',
    ('E','B','B'):'セッション再開→連続実装',
    ('A','A','B'):'教育的議論→技術実装',
    ('C','B','D'):'設計→実装→評価（設計駆動開発）',
    ('A','B','B'):'教育的指示→連続実装',
}
for (a,b,c),count in cat_trigrams.most_common(15):
    key = (a,b,c)
    interp = trigram_interps.get(key,'')
    r.append(f"| {a}→{b}→{c} | {count:,} | {interp} |")

# ツール使用と発話分類の関連
r.append("\n### 2.6 発話分類別のツール使用パターン")
r.append("")
r.append("ユーザの発話カテゴリに応じてAssistantがどのツールを使用したかの分析．")
r.append("")
for cat in 'ABCDEF':
    cat_tools = Counter()
    for (c,t),cnt in tool_after_human.items():
        if c == cat: cat_tools[t] += cnt
    if not cat_tools: continue
    top3 = cat_tools.most_common(3)
    total_t = sum(cat_tools.values())
    tools_str = ', '.join(f"{t}({c}, {c/total_t*100:.0f}%)" for t,c in top3)
    r.append(f"- **{cat}: {cat_names[cat]}** → {tools_str}")
r.append("")

# ━━ 分析3 ━━
r.append("\n---\n")
r.append("## 分析3: メッセージの具体性の推移")
r.append("")
r.append("### 3.1 月別具体性指標")
r.append("")
r.append("| 月 | 件数 | 平均文字数 | 固有名詞/msg | 数値/msg | パスURL/msg | 具体性密度(/100字) |")
r.append("|---|---|---|---|---|---|---|")
for ym in all_months:
    d = monthly_spec[ym]
    if not d['density']: continue
    n = len(d['density'])
    r.append(f"| {ym} | {n} | {sum(d['lengths'])/n:.0f} | {sum(d['nouns'])/n:.2f} | {sum(d['nums'])/n:.2f} | {sum(d['paths'])/n:.2f} | {sum(d['density'])/n:.2f} |")

r.append("\n### 3.2 週別具体性指標")
r.append("")
r.append("| フェーズ | 件数 | 平均文字数 | 固有名詞/msg | 数値/msg | パスURL/msg | 具体性密度(/100字) |")
r.append("|---|---|---|---|---|---|---|")
for wp in ['第1週 (2/14-2/20)','第2週 (2/21-2/27)','第3週 (2/28-3/6)','第4週 (3/7-3/13)','第5週 (3/14-3/16)']:
    d = week_spec[wp]
    if not d['density']: continue
    n = len(d['density'])
    r.append(f"| {wp} | {n} | {sum(d['lengths'])/n:.0f} | {sum(d['nouns'])/n:.2f} | {sum(d['nums'])/n:.2f} | {sum(d['paths'])/n:.2f} | {sum(d['density'])/n:.2f} |")

# デバイス別
r.append("\n### 3.3 デバイス別具体性指標")
r.append("")
dev_spec = defaultdict(lambda: {'nouns':[],'nums':[],'paths':[],'density':[],'lengths':[]})
for ym,text,dt,src,dev,sid in human_msgs:
    nn,nu,p,dens = calc_specificity(text)
    dev_spec[dev]['nouns'].append(nn); dev_spec[dev]['nums'].append(nu)
    dev_spec[dev]['paths'].append(p); dev_spec[dev]['density'].append(dens)
    dev_spec[dev]['lengths'].append(len(text))

r.append("| デバイス | 件数 | 平均文字数 | 固有名詞/msg | 数値/msg | パスURL/msg | 具体性密度(/100字) |")
r.append("|---|---|---|---|---|---|---|")
for dev in sorted(dev_spec.keys()):
    d = dev_spec[dev]; n = len(d['density'])
    r.append(f"| {dev} | {n} | {sum(d['lengths'])/n:.0f} | {sum(d['nouns'])/n:.2f} | {sum(d['nums'])/n:.2f} | {sum(d['paths'])/n:.2f} | {sum(d['density'])/n:.2f} |")

# ━━ 分析4 ━━
r.append("\n---\n")
r.extend(r4)

# 分析手法の限界
r.append("\n---\n")
r.append("## 分析手法の限界と留意点")
r.append("")
r.append("1. **Claude Code固有の特徴**: Claude Codeはターミナル環境で動作するため，Web/Desktop版と比較して")
r.append("   (a)指示がより短く具体的，(b)コード・パスの直接貼り付けが多い，(c)「その他」カテゴリに短い操作的発話が集中する傾向がある．")
r.append("2. **自動セッションの影響**: WSL multi-agent-shogun（495セッション）はシステム自動生成メッセージを含むため，")
r.append("   ユーザーの意図分析としてはWindows主セッション（64件）およびMacBookセッション（20件）が中心的な分析対象となる．")
r.append("3. **短期間データ**: Claude Code利用期間は2026年2月〜3月の約1.5か月であり，conversations.json（2025年1月〜2026年3月，15か月）と比較して")
r.append("   長期的な変化の分析には限界がある．ただし，ツール使用パターンやセッション内のシーケンス分析はClaude Code固有の知見を提供する．")
r.append("4. **分類精度**: キーワードベース分類のため，文脈依存の分類（暗黙の教育的判断等）は捕捉できない．")

# Web/Desktop版との比較
r.append("\n---\n")
r.append("## 参考: Web/Desktop版（conversations.json）との比較")
r.append("")
r.append("| 指標 | Web/Desktop | Claude Code |")
r.append("|---|---|---|")
r.append(f"| 期間 | 2025-01〜2026-03（15か月） | 2026-01〜2026-03（約2か月） |")
r.append(f"| 総メッセージ | 12,849 | {len(all_messages):,} |")
r.append(f"| Humanメッセージ | 6,362 | {len(human_msgs):,} |")
r.append(f"| A:教育的意図 | 6.8% | {total_cats['A']/len(human_msgs)*100:.1f}% |")
r.append(f"| B:技術的指示 | 14.6% | {total_cats['B']/len(human_msgs)*100:.1f}% |")
r.append(f"| C:設計判断 | 3.2% | {total_cats['C']/len(human_msgs)*100:.1f}% |")
r.append(f"| D:品質FB | 6.6% | {total_cats['D']/len(human_msgs)*100:.1f}% |")
r.append(f"| E:文脈補足 | 3.1% | {total_cats['E']/len(human_msgs)*100:.1f}% |")
r.append(f"| F:その他 | 65.8% | {total_cats['F']/len(human_msgs)*100:.1f}% |")
r.append(f"| 具体性密度(導入期→統合期) | 0.38→1.40 | (月別参照) |")
r.append(f"| ツール呼び出し | なし | {sum(sum(len(m['tools']) for m in s['messages']) for s in all_sessions.values()):,}回 |")

r.append(f"\n---\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by cc_jsise_analysis.py*")

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(r))
print(f"\n出力: {OUTPUT}")
print(f"行数: {len(r)}")
