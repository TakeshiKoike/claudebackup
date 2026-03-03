"""VOICEVOX音声合成 + ffmpeg音声処理"""

import json
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

VOICEVOX_URL = "http://localhost:50021"
VOICEVOX_SPEAKER = 3


def get_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def synthesize(text: str, output_path: Path, speaker_id: int = VOICEVOX_SPEAKER,
               speed: float = 1.0, url: str = VOICEVOX_URL) -> float:
    """VOICEVOX音声合成。戻り値は秒数。"""
    params = urllib.parse.urlencode({"text": text, "speaker": speaker_id})
    req = urllib.request.Request(f"{url}/audio_query?{params}", method="POST")
    with urllib.request.urlopen(req) as resp:
        query = json.loads(resp.read())
    query["speedScale"] = speed

    params = urllib.parse.urlencode({"speaker": speaker_id})
    req = urllib.request.Request(
        f"{url}/synthesis?{params}",
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        output_path.write_bytes(resp.read())
    return get_duration(output_path)


def make_silence(output_path: Path, duration_ms: int):
    """無音WAV生成"""
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anullsrc=r=24000:cl=mono",
        "-t", str(duration_ms / 1000),
        str(output_path),
    ], capture_output=True, check=True)


def concat_audio(file_list: list[Path], output_path: Path) -> float:
    """WAVファイルを結合。戻り値は合計秒数。"""
    concat_txt = output_path.parent / "concat.txt"
    lines = [f"file '{f.resolve()}'" for f in file_list]
    concat_txt.write_text("\n".join(lines))
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt), "-c", "copy", str(output_path),
    ], capture_output=True, check=True)
    return get_duration(output_path)
