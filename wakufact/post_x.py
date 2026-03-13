#!/usr/bin/env python3
"""WakuFact - X (Twitter) 自動投稿スクリプト"""

import json
import sys
import time
from pathlib import Path

import tweepy
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

# OAuth 1.0 認証（動画アップロードに必要）
auth = tweepy.OAuth1UserHandler(
    os.environ["X_CONSUMER_KEY"],
    os.environ["X_CONSUMER_SECRET"],
    os.environ["X_ACCESS_TOKEN"],
    os.environ["X_ACCESS_TOKEN_SECRET"],
)

# API v1.1（メディアアップロード用）
api_v1 = tweepy.API(auth)

# API v2（ツイート投稿用）
client = tweepy.Client(
    consumer_key=os.environ["X_CONSUMER_KEY"],
    consumer_secret=os.environ["X_CONSUMER_SECRET"],
    access_token=os.environ["X_ACCESS_TOKEN"],
    access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
)

BASE = Path(__file__).parent


def post_episode(ep_num: int, lang: str = "jp"):
    """エピソードをXに投稿"""
    # メタデータ読み込み
    with open(BASE / "batch_001_post_metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    ep_data = metadata["episodes"][ep_num - 1]
    platform_key = f"x_{lang}"
    post_data = ep_data["platforms"][platform_key]

    tweet_text = post_data["tweet"]

    # 動画ファイル検索（最新バージョン）
    ep_dir = BASE / f"ep{ep_num:02d}" / "output"
    videos = sorted(ep_dir.glob(f"wakufact_ep{ep_num:02d}_jp_sub_v*.mp4"))
    if not videos:
        print(f"エラー: EP{ep_num:02d} の動画が見つかりません")
        return None
    video_path = videos[-1]

    print(f"=== EP{ep_num:02d} X投稿 ===")
    print(f"  動画: {video_path.name}")
    print(f"  ツイート: {tweet_text[:60]}...")
    print(f"  動画アップロード中...")

    # 動画アップロード（v1.1 chunked upload）
    media = api_v1.media_upload(
        filename=str(video_path),
        media_category="tweet_video",
        chunked=True,
    )

    # アップロード完了を待つ
    if hasattr(media, "processing_info"):
        _wait_for_processing(media)

    print(f"  メディアID: {media.media_id}")
    print(f"  ツイート投稿中...")

    # ツイート投稿（v2）
    response = client.create_tweet(
        text=tweet_text,
        media_ids=[str(media.media_id)],
    )

    tweet_id = response.data["id"]
    tweet_url = f"https://x.com/wakufact/status/{tweet_id}"
    print(f"  投稿完了: {tweet_url}")
    return tweet_url


def _wait_for_processing(media):
    """動画処理完了を待つ"""
    processing = media.processing_info
    while processing and processing.get("state") in ("pending", "in_progress"):
        wait_sec = processing.get("check_after_secs", 5)
        print(f"  処理中... ({wait_sec}秒待機)")
        time.sleep(wait_sec)
        status = api_v1.get_media_upload_status(media.media_id)
        processing = status.processing_info


if __name__ == "__main__":
    ep = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    lang = sys.argv[2] if len(sys.argv) > 2 else "jp"
    post_episode(ep, lang)
