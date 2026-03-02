#!/usr/bin/env python3
"""
WakuFact - VOICEVOX台本分割ツール
台本を適切なセクションに分割し、VOICEVOX API用JSONを出力する
"""

import json
import re
import sys
from pathlib import Path

# VOICEVOX話者ID（お好みで変更）
SPEAKERS = {
    "ずんだもん（ノーマル）": 3,
    "四国めたん（ノーマル）": 2,
    "春日部つむぎ": 8,
    "波音リツ": 9,
    "玄野武宏（ノーマル）": 11,
    "白上虎太郎（ノーマル）": 12,
}

DEFAULT_SPEAKER_ID = 3  # ずんだもん

# セクション定義
SECTION_CONFIG = {
    "hook": {
        "label": "フック",
        "speed_scale": 1.1,
        "pitch_scale": 0.02,
        "intonation_scale": 1.3,
        "pause_after_ms": 800,
    },
    "develop_1": {
        "label": "展開1",
        "speed_scale": 1.0,
        "pitch_scale": 0.0,
        "intonation_scale": 1.1,
        "pause_after_ms": 500,
    },
    "develop_2": {
        "label": "展開2（驚き）",
        "speed_scale": 0.95,
        "pitch_scale": 0.0,
        "intonation_scale": 1.2,
        "pause_after_ms": 600,
    },
    "develop_3": {
        "label": "展開3",
        "speed_scale": 1.0,
        "pitch_scale": 0.0,
        "intonation_scale": 1.1,
        "pause_after_ms": 500,
    },
    "climax": {
        "label": "クライマックス",
        "speed_scale": 0.9,
        "pitch_scale": 0.02,
        "intonation_scale": 1.4,
        "pause_after_ms": 1000,
    },
    "cta": {
        "label": "CTA",
        "speed_scale": 1.05,
        "pitch_scale": 0.0,
        "intonation_scale": 1.2,
        "pause_after_ms": 0,
    },
}


def split_script_to_sentences(script: str) -> list[str]:
    """台本を文単位に分割"""
    sentences = re.split(r'(?<=[。！？])', script)
    return [s.strip() for s in sentences if s.strip()]


def assign_sections(sentences: list[str]) -> list[dict]:
    """文をセクションに割り当て"""
    total = len(sentences)
    if total == 0:
        return []

    section_keys = list(SECTION_CONFIG.keys())
    num_sections = len(section_keys)

    # 均等に分配（hookは1-2文、CTAは最後の1文）
    sections = []

    # CTA: 最後の1文
    cta_count = 1
    # Hook: 最初の1-2文
    hook_count = min(2, max(1, total // num_sections))
    # 残りを4セクションに均等分配
    remaining = total - hook_count - cta_count
    per_section = max(1, remaining // 4)

    idx = 0
    for i, key in enumerate(section_keys):
        config = SECTION_CONFIG[key]
        if key == "hook":
            count = hook_count
        elif key == "cta":
            count = cta_count
        elif key == "climax":
            # climaxは残り全部（端数調整）
            count = total - idx - cta_count
        else:
            count = min(per_section, total - idx - cta_count - (num_sections - 1 - i))
            count = max(1, count)

        section_sentences = sentences[idx:idx + count]
        if not section_sentences and idx < total:
            continue

        if section_sentences:
            sections.append({
                "section": key,
                "label": config["label"],
                "text": "".join(section_sentences),
                "speed_scale": config["speed_scale"],
                "pitch_scale": config["pitch_scale"],
                "intonation_scale": config["intonation_scale"],
                "pause_after_ms": config["pause_after_ms"],
            })
            idx += count

    return sections


def generate_voicevox_data(episode: dict, speaker_id: int = DEFAULT_SPEAKER_ID) -> dict:
    """1エピソード分のVOICEVOX用データを生成"""
    script_jp = episode["script_jp"]
    sentences = split_script_to_sentences(script_jp)
    sections = assign_sections(sentences)

    # フック文をhook_jpから取得して先頭に設定
    hook_text = episode.get("hook_jp", "")
    if hook_text and sections and sections[0]["section"] == "hook":
        # hook_jpがscript_jpと異なる場合は差し替え
        if hook_text not in sections[0]["text"]:
            sections[0]["text"] = hook_text

    return {
        "ep": episode["ep"],
        "title_jp": episode["title_jp"],
        "category": episode["category"],
        "speaker_id": speaker_id,
        "total_sections": len(sections),
        "sections": sections,
        "cta_text": episode.get("cta", ""),
    }


def main():
    input_path = Path(__file__).parent / "batch_001_trivia_50.json"
    output_path = Path(__file__).parent / "batch_001_voicevox_scripts.json"

    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 話者ローテーション（バリエーション確保）
    speaker_rotation = [3, 2, 8, 3, 2, 8]  # ずんだもん、四国めたん、春日部つむぎ

    results = []
    for i, ep in enumerate(data["episodes"]):
        speaker_id = speaker_rotation[i % len(speaker_rotation)]
        result = generate_voicevox_data(ep, speaker_id)
        results.append(result)

    output = {
        "batch_id": "wakufact_batch_001_voicevox",
        "generated_date": data["generated_date"],
        "total_episodes": len(results),
        "available_speakers": SPEAKERS,
        "default_speaker_id": DEFAULT_SPEAKER_ID,
        "episodes": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Generated VOICEVOX scripts for {output['total_episodes']} episodes")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
