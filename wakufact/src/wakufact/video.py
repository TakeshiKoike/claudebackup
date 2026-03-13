"""動画合成 + ASS字幕生成"""

import subprocess
from pathlib import Path

from .audio import get_duration

# 1行あたり最大文字数 (全角基準、1080px - margin80px)
_MAX_CHARS_TITLE = 10   # 100px font
_MAX_CHARS_DEFAULT = 17  # 56px font


def fmt_time(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def _wrap_text(text: str, max_chars: int) -> str:
    """テキストを max_chars 文字ごとに \\N で改行する (句読点を行頭に残さない)。"""
    lines = text.split("\\N")
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
                cut = max_chars
                for sep in ("で", "に", "を", "が", "は", "の", "も", "て", "と"):
                    pos = line.rfind(sep, 0, max_chars)
                    if pos > 0:
                        cut = pos + len(sep)
                        break
            wrapped.append(line[:cut])
            line = line[cut:]
        if line:
            wrapped.append(line)
    return "\\N".join(wrapped)


def generate_ass(
    ep_num: int,
    title: str,
    sections: list[dict],
    timings: list[tuple],
    total: float,
    output_path: Path,
):
    """ASS字幕ファイル生成"""
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
    # タイトル
    wrapped_title = _wrap_text(title, _MAX_CHARS_TITLE)
    ass += f"Dialogue: 1,{fmt_time(0.0)},{fmt_time(3.0)},Title,,0,0,0,,{wrapped_title}\n"

    # 字幕
    for sec, timing in zip(sections, timings):
        sub_text = sec.get("subtitle", sec["text"])
        wrapped = _wrap_text(sub_text, _MAX_CHARS_DEFAULT)
        ass += f"Dialogue: 0,{fmt_time(timing[1])},{fmt_time(timing[2])},Default,,0,0,0,,{wrapped}\n"

    # CTA
    cta_start = timings[-1][1] + 1.0
    cta = _wrap_text("フォローして次の雑学も見てね！", _MAX_CHARS_TITLE)
    ass += f"Dialogue: 1,{fmt_time(cta_start)},{fmt_time(total)},Title,,0,0,0,,{cta}\n"

    output_path.write_text(ass)
    return output_path


def generate_imglist(
    image_labels: list[str],
    timings: list[tuple],
    sections: list[dict],
    total: float,
    images_dir: Path,
) -> Path:
    """画像タイミングリスト生成 (画像数=音声数の1:1対応)"""
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
        img_lines.append(f"file '{img_path}'")
        img_lines.append(f"duration {end - start:.3f}")
    last_img = (images_dir / img_timings[-1][0]).resolve()
    img_lines.append(f"file '{last_img}'")

    imglist = images_dir / "imglist.txt"
    imglist.write_text("\n".join(img_lines))
    return imglist


def composite(
    imglist: Path,
    audio: Path,
    subtitles: Path,
    output_path: Path,
) -> Path:
    """画像スライドショー + 音声 + 字幕 → MP4 (2パス)

    concat デマルチプレクサと ASS フィルタのタイムスタンプ不整合を
    回避するため、まず動画を作成してから字幕を焼き込む。
    """
    tmp = output_path.with_suffix(".tmp.mp4")
    # Pass 1: images + audio → video
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(imglist.resolve()),
        "-i", str(audio.resolve()),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(tmp),
    ], capture_output=True, check=True)
    # Pass 2: burn subtitles
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(tmp),
        "-vf", f"ass={subtitles.resolve()}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ], capture_output=True, check=True)
    tmp.unlink()
    return output_path
