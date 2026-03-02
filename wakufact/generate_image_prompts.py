#!/usr/bin/env python3
"""
WakuFact - ComfyUI画像プロンプトバッチ生成
各エピソードの台本からFlux用の画像プロンプトを自動生成する
"""

import json
import sys
from pathlib import Path

# エピソードごとの画像枚数（40-55秒のショート動画用）
IMAGES_PER_EPISODE = 7

# タイミング定義（秒）
TIMING_TEMPLATE = [
    {"label": "hook",      "start": 0.0,  "end": 5.0,  "description": "フック・掴み"},
    {"label": "intro",     "start": 5.0,  "end": 12.0, "description": "導入・問題提起"},
    {"label": "develop_1", "start": 12.0, "end": 20.0, "description": "展開1・核心の説明"},
    {"label": "develop_2", "start": 20.0, "end": 28.0, "description": "展開2・驚きの事実"},
    {"label": "develop_3", "start": 28.0, "end": 36.0, "description": "展開3・追加情報"},
    {"label": "climax",    "start": 36.0, "end": 44.0, "description": "クライマックス・最大の驚き"},
    {"label": "cta",       "start": 44.0, "end": 50.0, "description": "まとめ・CTA"},
]

# Flux共通設定
FLUX_BASE = {
    "width": 1080,
    "height": 1920,
    "steps": 30,
    "cfg_scale": 3.5,
    "sampler": "euler",
    "scheduler": "normal",
}

# カテゴリ別のビジュアルスタイルガイド
CATEGORY_STYLES = {
    "食べ物": "vibrant food photography style, macro details, warm lighting, appetizing colors",
    "人体": "scientific illustration style, anatomical accuracy, clean medical visualization, neon accents on dark background",
    "宇宙": "cinematic space art, NASA photography style, deep cosmic colors, dramatic lighting, ultra detailed nebulae",
    "動物": "national geographic wildlife photography, dramatic natural lighting, incredible detail, nature documentary quality",
    "歴史": "historical painting meets modern digital art, dramatic lighting, period-accurate details, cinematic composition",
    "テクノロジー": "sleek tech visualization, clean modern design, holographic elements, blue and white color scheme",
    "自然": "breathtaking landscape photography, BBC Earth documentary quality, dramatic weather, golden hour lighting",
}

NEGATIVE_PROMPT = "text, watermark, logo, signature, blurry, low quality, deformed, ugly, oversaturated, cartoon, anime, 3d render, stock photo feel, generic, boring composition"


def parse_visual_direction(visual_direction: str) -> list[str]:
    """visual_directionをシーン別のキーワードリストに分割"""
    scenes = [s.strip() for s in visual_direction.split(".") if s.strip()]
    if not scenes:
        scenes = [s.strip() for s in visual_direction.split(",") if s.strip()]
    return scenes


def generate_prompts_for_episode(episode: dict) -> dict:
    """1エピソード分の画像プロンプトを生成"""
    ep_num = episode["ep"]
    category = episode["category"]
    title = episode["title_en"]
    visual_dir = episode["visual_direction"]
    style = CATEGORY_STYLES.get(category, "")

    scenes = parse_visual_direction(visual_dir)

    images = []
    for i, timing in enumerate(TIMING_TEMPLATE):
        scene_hint = scenes[i] if i < len(scenes) else scenes[-1] if scenes else title

        prompt = f"{scene_hint}, {style}, cinematic composition, 9:16 vertical format, high detail, 4k quality"

        images.append({
            "image_number": i + 1,
            "label": timing["label"],
            "timing": {"start": timing["start"], "end": timing["end"]},
            "description_jp": timing["description"],
            "prompt": prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            **FLUX_BASE,
        })

    return {
        "ep": ep_num,
        "category": category,
        "title_en": title,
        "title_jp": episode["title_jp"],
        "total_images": len(images),
        "images": images,
    }


def main():
    input_path = Path(__file__).parent / "batch_001_trivia_50.json"
    output_path = Path(__file__).parent / "batch_001_image_prompts.json"

    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for ep in data["episodes"]:
        result = generate_prompts_for_episode(ep)
        results.append(result)

    output = {
        "batch_id": "wakufact_batch_001_images",
        "generated_date": data["generated_date"],
        "total_episodes": len(results),
        "total_images": len(results) * IMAGES_PER_EPISODE,
        "flux_settings": FLUX_BASE,
        "episodes": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Generated {output['total_images']} image prompts for {output['total_episodes']} episodes")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
