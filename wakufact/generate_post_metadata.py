#!/usr/bin/env python3
"""
WakuFact - 投稿メタデータ自動生成
各エピソードから4プラットフォーム分の投稿テキストを日英で生成
"""

import json
import sys
from pathlib import Path

# カテゴリ別ハッシュタグ
CATEGORY_TAGS = {
    "食べ物": {
        "jp": ["#雑学", "#食べ物雑学", "#豆知識", "#知らなかった", "#食の科学"],
        "en": ["#foodfacts", "#didyouknow", "#funfacts", "#foodscience", "#mindblown"],
    },
    "人体": {
        "jp": ["#雑学", "#人体の不思議", "#豆知識", "#科学", "#知らなかった"],
        "en": ["#bodyfacts", "#humanfacts", "#didyouknow", "#science", "#mindblown"],
    },
    "宇宙": {
        "jp": ["#雑学", "#宇宙", "#豆知識", "#NASA", "#宇宙の不思議"],
        "en": ["#spacefacts", "#universe", "#NASA", "#astronomy", "#mindblown"],
    },
    "動物": {
        "jp": ["#雑学", "#動物雑学", "#豆知識", "#動物", "#知らなかった"],
        "en": ["#animalfacts", "#wildlife", "#didyouknow", "#nature", "#animals"],
    },
    "歴史": {
        "jp": ["#雑学", "#歴史雑学", "#豆知識", "#歴史", "#知らなかった"],
        "en": ["#historyfacts", "#history", "#didyouknow", "#funfacts", "#mindblown"],
    },
    "テクノロジー": {
        "jp": ["#雑学", "#テクノロジー", "#豆知識", "#IT", "#知らなかった"],
        "en": ["#techfacts", "#technology", "#didyouknow", "#innovation", "#mindblown"],
    },
    "自然": {
        "jp": ["#雑学", "#自然", "#豆知識", "#地球", "#知らなかった"],
        "en": ["#naturefacts", "#earth", "#didyouknow", "#science", "#mindblown"],
    },
}

BRAND_TAGS = {
    "jp": ["#WakuFact", "#ワクファクト", "#毎日雑学"],
    "en": ["#WakuFact", "#facts", "#dailyfacts"],
}


def generate_youtube_metadata(ep: dict, lang: str) -> dict:
    """YouTube Shorts用メタデータ"""
    is_jp = lang == "jp"
    title = ep["title_jp"] if is_jp else ep["title_en"]
    hook = ep["hook_jp"] if is_jp else ep["hook_en"]
    cat_tags = CATEGORY_TAGS.get(ep["category"], {}).get(lang, [])
    brand = BRAND_TAGS[lang]

    if is_jp:
        description = f"{hook}\n\n{ep['script_jp'][:100]}...\n\n{'  '.join(cat_tags + brand)}\n\n#Shorts"
    else:
        description = f"{hook}\n\n{ep['script_en'][:100]}...\n\n{'  '.join(cat_tags + brand)}\n\n#Shorts"

    return {
        "platform": "youtube_shorts",
        "language": lang,
        "title": f"{title} #Shorts",
        "description": description,
        "tags": cat_tags + brand + (["#Shorts", "#雑学動画"] if is_jp else ["#Shorts", "#factsshorts"]),
    }


def generate_tiktok_metadata(ep: dict, lang: str) -> dict:
    """TikTok用メタデータ"""
    is_jp = lang == "jp"
    hook = ep["hook_jp"] if is_jp else ep["hook_en"]
    cat_tags = CATEGORY_TAGS.get(ep["category"], {}).get(lang, [])
    brand = BRAND_TAGS[lang]

    all_tags = cat_tags + brand + (["#TikTok教室", "#へぇ"] if is_jp else ["#learnontiktok", "#fyp"])
    caption = f"{hook}\n\n{'  '.join(all_tags)}"

    return {
        "platform": "tiktok",
        "language": lang,
        "caption": caption,
        "tags": all_tags,
        "sound": ep.get("bgm_style", ""),
    }


def generate_instagram_metadata(ep: dict, lang: str) -> dict:
    """Instagram Reels用メタデータ"""
    is_jp = lang == "jp"
    title = ep["title_jp"] if is_jp else ep["title_en"]
    hook = ep["hook_jp"] if is_jp else ep["hook_en"]
    cat_tags = CATEGORY_TAGS.get(ep["category"], {}).get(lang, [])
    brand = BRAND_TAGS[lang]

    if is_jp:
        caption = f"💡 {title}\n\n{hook}\n\n続きは動画で👆\n\n{'  '.join(cat_tags + brand + ['#リール', '#インスタ雑学'])}"
    else:
        caption = f"💡 {title}\n\n{hook}\n\nWatch to find out 👆\n\n{'  '.join(cat_tags + brand + ['#reels', '#instafacts'])}"

    return {
        "platform": "instagram_reels",
        "language": lang,
        "caption": caption,
        "tags": cat_tags + brand,
        "cover_text": title,
    }


def generate_x_metadata(ep: dict, lang: str) -> dict:
    """X (Twitter)用メタデータ"""
    is_jp = lang == "jp"
    title = ep["title_jp"] if is_jp else ep["title_en"]
    hook = ep["hook_jp"] if is_jp else ep["hook_en"]
    cat_tags = CATEGORY_TAGS.get(ep["category"], {}).get(lang, [])[:3]
    brand = BRAND_TAGS[lang][:1]

    # 280文字制限を意識
    tweet = f"{hook}\n\n{' '.join(cat_tags + brand)}"
    if len(tweet) > 270:
        tweet = f"{hook}\n{' '.join(brand)}"

    return {
        "platform": "x",
        "language": lang,
        "tweet": tweet,
        "tags": cat_tags + brand,
        "alt_text": title,
    }


def generate_metadata_for_episode(ep: dict) -> dict:
    """1エピソード分の全プラットフォームメタデータを生成"""
    platforms = {}
    for lang in ["jp", "en"]:
        platforms[f"youtube_shorts_{lang}"] = generate_youtube_metadata(ep, lang)
        platforms[f"tiktok_{lang}"] = generate_tiktok_metadata(ep, lang)
        platforms[f"instagram_{lang}"] = generate_instagram_metadata(ep, lang)
        platforms[f"x_{lang}"] = generate_x_metadata(ep, lang)

    return {
        "ep": ep["ep"],
        "title_jp": ep["title_jp"],
        "title_en": ep["title_en"],
        "category": ep["category"],
        "total_posts": len(platforms),
        "platforms": platforms,
    }


def main():
    input_path = Path(__file__).parent / "batch_001_trivia_50.json"
    output_path = Path(__file__).parent / "batch_001_post_metadata.json"

    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for ep in data["episodes"]:
        result = generate_metadata_for_episode(ep)
        results.append(result)

    total_posts = sum(r["total_posts"] for r in results)

    output = {
        "batch_id": "wakufact_batch_001_metadata",
        "generated_date": data["generated_date"],
        "total_episodes": len(results),
        "total_posts": total_posts,
        "platforms": ["youtube_shorts", "tiktok", "instagram_reels", "x"],
        "languages": ["jp", "en"],
        "episodes": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Generated {total_posts} post metadata entries for {output['total_episodes']} episodes")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
