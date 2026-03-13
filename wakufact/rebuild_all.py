#!/usr/bin/env python3
"""全エピソードの字幕・imglist・動画を音声ファイルから再構築"""

import subprocess
from pathlib import Path

BASE = Path(__file__).parent

# ===== ソースデータ (音声生成に使ったテキストと一致) =====

EP_DATA = {
    1: {
        "title": "バナナはベリー、\nイチゴはベリーじゃない",
        "sections": [
            {"key": "hook", "pause_ms": 800, "text": "あなたが知ってるフルーツの分類、全部ウソかも。"},
            {"key": "develop_1", "pause_ms": 500, "text": "実はバナナって、植物の世界ではベリーなんです。でもイチゴはベリーじゃない。"},
            {"key": "develop_2", "pause_ms": 600, "text": "ベリーっていうのは、ひとつの花から実ができて、その中に種が入ってる果物のこと。バナナはまさにこの条件にぴったり。"},
            {"key": "develop_3", "pause_ms": 500, "text": "一方イチゴは、表面のツブツブが実は本当の実で、赤い部分はただの土台。つまりイチゴはニセモノの果物なんです。"},
            {"key": "climax", "pause_ms": 1000, "text": "ちなみにアボカドもスイカもベリー。ラズベリーはベリーじゃない。"},
            {"key": "cta", "pause_ms": 0, "text": "植物の名前のつけ方、ちょっとおかしいですよね。フォローして次の雑学も見てね。"},
        ],
        "image_labels": ["01_hook", "03_develop_1", "04_develop_2", "05_develop_3", "06_climax", "07_cta"],
    },
    2: {
        "title": "あなたの脳は\n小さな電球1個分の\n電力で動いている",
        "sections": [
            {"key": "hook", "pause_ms": 800, "text": "世界最高のコンピュータは、たった20ワットで動いています。"},
            {"key": "develop_1", "pause_ms": 500, "text": "それはあなたの脳。スマホの充電器より少ない電力で、860億個の脳の細胞が毎秒何兆回もの計算をしている。"},
            {"key": "develop_2", "pause_ms": 600, "text": "同じことをスーパーコンピュータでやると、何百万ワットも必要です。"},
            {"key": "develop_3", "pause_ms": 500, "text": "脳は体重のたった2パーセントなのに、体のエネルギーの20パーセントも使っている。めちゃくちゃ大食いなんです。"},
            {"key": "climax", "pause_ms": 1000, "text": "でもこの20ワットで、言葉を話し、夢を見て、宇宙の謎を考えられる。"},
            {"key": "cta", "pause_ms": 0, "text": "あなたの頭の中には、宇宙で最も効率的なマシンが入っています。フォローして次の雑学も見てね。"},
        ],
        "image_labels": ["01_hook", "03_develop_1", "04_develop_2", "05_develop_3", "06_climax", "07_cta"],
    },
    3: {
        "title": "宇宙はステーキと\nラム酒の匂いがする",
        "sections": [
            {"key": "hook", "pause_ms": 800, "text": "宇宙飛行士が宇宙服を脱いだ瞬間、焼肉の匂いがした。"},
            {"key": "develop_1", "pause_ms": 500, "text": "宇宙から帰ってきて宇宙服を脱ぐと、焼けたステーキ、火薬、そしてラム酒の匂いがする。NASAも認めています。"},
            {"key": "develop_2", "pause_ms": 600, "text": "この匂いの正体は、星が死ぬときに出す化学物質。つまり宇宙の匂いは、星の最後の香りなんです。"},
            {"key": "develop_3", "pause_ms": 500, "text": "ちなみにNASAは2020年に、この匂いを再現した香水のプロジェクトを応援しました。"},
            {"key": "climax", "pause_ms": 1000, "text": "宇宙の香り、嗅いでみたくないですか？"},
            {"key": "cta", "pause_ms": 0, "text": "宇宙にはまだまだ不思議がいっぱい。フォローして次の雑学も見てね。"},
        ],
        "image_labels": ["01_hook", "03_develop_1", "04_develop_2", "05_develop_3", "06_climax", "07_cta"],
    },
    4: {
        "title": "ハチミツは\n3000年経っても\n腐らない",
        "sections": [
            {"key": "hook", "pause_ms": 800, "text": "エジプトのピラミッドから見つかったハチミツ、まだ食べられた。"},
            {"key": "develop_1", "pause_ms": 500, "text": "ピラミッドから3000年前のハチミツが見つかりました。驚くことに、まだ食べられる状態だったんです。"},
            {"key": "develop_2", "pause_ms": 600, "text": "ハチミツが腐らない理由は3つ。まず水分がすごく少ない。バイキンが生きられない。そして強い酸性。"},
            {"key": "develop_3", "pause_ms": 500, "text": "さらにミツバチの出す成分が、天然の消毒液を作り出す。ハチミツは自分で自分を守っているんです。"},
            {"key": "climax", "pause_ms": 1000, "text": "古代エジプト人はハチミツを傷薬に使っていました。3000年後の科学がそれを正しいと証明した。"},
            {"key": "cta", "pause_ms": 0, "text": "自然は最初から答えを知っていたんです。フォローして次の雑学も見てね。"},
        ],
        "image_labels": ["01_hook", "03_develop_1", "04_develop_2", "05_develop_3", "06_climax", "07_cta"],
    },
}

# 1行最大文字数
MAX_TITLE = 10
MAX_DEFAULT = 17


def get_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def fmt_time(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def wrap_text(text, max_chars):
    """テキストを max_chars 文字ごとに \\N で改行 (句読点を行頭に残さない)"""
    lines = text.split("\\N") if "\\N" in text else [text]
    wrapped = []
    for line in lines:
        while len(line) > max_chars:
            # 句読点の直後で切る (句読点が次の行の先頭にならないように)
            best = -1
            for sep in ("。", "、", "！", "？"):
                pos = line.rfind(sep, 0, max_chars)
                if pos > 0 and pos + len(sep) > best:
                    best = pos + len(sep)
            if best > 0:
                cut = best
            else:
                # 助詞の後で切る
                for sep in ("で", "に", "を", "が", "は", "の", "も", "て", "と"):
                    pos = line.rfind(sep, 0, max_chars)
                    if pos > 0:
                        cut = pos + len(sep)
                        break
                else:
                    cut = max_chars
            wrapped.append(line[:cut])
            line = line[cut:]
        if line:
            wrapped.append(line)
    return "\\N".join(wrapped)


def rebuild_episode(ep_num):
    data = EP_DATA[ep_num]
    ep_dir = BASE / f"ep{ep_num:02d}"
    audio_dir = ep_dir / "audio"
    images_dir = ep_dir / "images"
    output_dir = ep_dir / "output"

    sections = data["sections"]
    image_labels = data["image_labels"]

    print(f"\n{'='*50}")
    print(f"EP{ep_num:02d} 再構築")
    print(f"{'='*50}")

    # === 音声ファイルからタイミング計算 ===
    timings = []
    t = 0.0
    for i, sec in enumerate(sections):
        audio_path = audio_dir / f"{i+1:02d}_{sec['key']}.wav"
        if not audio_path.exists():
            print(f"  ERROR: {audio_path} not found!")
            return None
        d = get_duration(audio_path)
        timings.append((sec["key"], t, t + d))
        t += d
        pause_ms = sec.get("pause_ms", 0)
        if pause_ms > 0:
            t += pause_ms / 1000

    combined = audio_dir / "combined.wav"
    total = get_duration(combined)

    print("  タイミング:")
    for key, start, end in timings:
        print(f"    {key}: {start:.2f}s - {end:.2f}s")
    print(f"    total: {total:.2f}s")

    # === 字幕生成 ===
    title_text = data["title"].replace("\n", "\\N")
    title_wrapped = wrap_text(title_text, MAX_TITLE)

    ass = f"""[Script Info]
Title: WakuFact EP{ep_num:02d}
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Hiragino Sans,56,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,8,40,40,600,1
Style: Title,Hiragino Sans,100,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,3,8,40,40,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    # タイトル (最初の3秒)
    ass += f"Dialogue: 1,{fmt_time(0.0)},{fmt_time(3.0)},Title,,0,0,0,,{title_wrapped}\n"

    # 各セクション字幕 (音声と完全一致)
    for sec, timing in zip(sections, timings):
        sub_text = wrap_text(sec["text"], MAX_DEFAULT)
        ass += f"Dialogue: 0,{fmt_time(timing[1])},{fmt_time(timing[2])},Default,,0,0,0,,{sub_text}\n"

    # CTA
    cta_start = timings[-1][1] + 1.0
    cta_text = wrap_text("フォローして次の雑学も見てね！", MAX_TITLE)
    ass += f"Dialogue: 1,{fmt_time(cta_start)},{fmt_time(total)},Title,,0,0,0,,{cta_text}\n"

    sub_path = output_dir / "subtitles.ass"
    sub_path.write_text(ass)
    print(f"  字幕: {sub_path}")

    # 字幕内容を表示して確認
    print("  字幕テキスト:")
    for sec, timing in zip(sections, timings):
        print(f"    [{fmt_time(timing[1])}-{fmt_time(timing[2])}] {sec['text'][:30]}...")

    # === 画像リスト生成 (1:1マッピング) ===
    assert len(image_labels) == len(sections), f"画像{len(image_labels)}枚 != セクション{len(sections)}個"

    img_timings = []
    for j in range(len(timings)):
        sec_end = timings[j][2] + (sections[j].get("pause_ms", 0) / 1000)
        start = img_timings[-1][2] if img_timings else 0.0
        img_timings.append((f"{image_labels[j]}.png", start, sec_end))
    last = img_timings[-1]
    img_timings[-1] = (last[0], last[1], total)

    img_lines = []
    for img_name, start, end in img_timings:
        img_path = (images_dir / img_name).resolve()
        if not img_path.exists():
            print(f"  ERROR: {img_path} not found!")
            return None
        img_lines.append(f"file '{img_path}'")
        img_lines.append(f"duration {end - start:.3f}")
    last_img = (images_dir / img_timings[-1][0]).resolve()
    img_lines.append(f"file '{last_img}'")

    imglist = images_dir / "imglist.txt"
    imglist.write_text("\n".join(img_lines))

    print("  画像タイミング:")
    for img_name, start, end in img_timings:
        print(f"    {img_name}: {start:.2f}s - {end:.2f}s")

    # === 動画合成 ===
    # 既存の最新バージョンを確認
    existing = sorted(output_dir.glob(f"wakufact_ep{ep_num:02d}_jp_sub_v*.mp4"))
    if existing:
        last_ver = int(existing[-1].stem.split("_v")[-1])
        new_ver = last_ver + 1
    else:
        new_ver = 1

    output_path = output_dir / f"wakufact_ep{ep_num:02d}_jp_sub_v{new_ver}.mp4"

    print(f"  合成中 (2パス): {output_path.name}")
    tmp = output_path.with_suffix(".tmp.mp4")
    # Pass 1: images + audio → video
    result = subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(imglist.resolve()),
        "-i", str(combined.resolve()),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(tmp),
    ], capture_output=True)
    if result.returncode != 0:
        print(f"  ERROR Pass1: {result.stderr.decode()[-200:]}")
        return None
    # Pass 2: burn subtitles
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(tmp),
        "-vf", f"ass={sub_path.resolve()}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ], capture_output=True)
    tmp.unlink(missing_ok=True)
    if result.returncode != 0:
        print(f"  ERROR Pass2: {result.stderr.decode()[-200:]}")
        return None

    final_dur = get_duration(output_path)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  完成: {output_path}")
    print(f"  Duration: {final_dur:.1f}s, Size: {size_mb:.1f}MB")
    return output_path


if __name__ == "__main__":
    results = {}
    for ep in [1, 2, 3, 4]:
        results[ep] = rebuild_episode(ep)

    print("\n\n=== 結果 ===")
    for ep, path in results.items():
        status = f"OK: {path.name}" if path else "FAILED"
        print(f"  EP{ep:02d}: {status}")
