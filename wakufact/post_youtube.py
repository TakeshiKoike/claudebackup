#!/usr/bin/env python3
"""
WakuFact - YouTube Shorts 自動投稿スクリプト

初回セットアップ:
  1. Google Cloud Console (https://console.cloud.google.com/) でプロジェクト作成
  2. YouTube Data API v3 を有効化
  3. OAuth 2.0 クライアントID作成 (デスクトップアプリ)
  4. JSONをダウンロード → wakufact/client_secret.json に配置
  5. OAuth同意画面 → テストユーザーに自分のGoogleアカウント追加
  6. python3 post_youtube.py --auth  (ブラウザで認証、token.json生成)

使い方:
  python3 post_youtube.py 5 6 7 8          # EP05-08を投稿
  python3 post_youtube.py --auth            # 認証のみ
  python3 post_youtube.py --check           # 認証状態確認
"""

import json
import sys
import time
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

BASE = Path(__file__).parent
CLIENT_SECRET = BASE / "client_secret.json"
TOKEN_FILE = BASE / "youtube_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.readonly"]

# カテゴリ → YouTube categoryId マッピング
CATEGORY_MAP = {
    "動物": "15",       # Pets & Animals
    "人体": "27",       # Education
    "歴史": "27",       # Education
    "テクノロジー": "28", # Science & Technology
    "宇宙": "28",       # Science & Technology
    "食べ物": "27",     # Education
    "自然": "27",       # Education
}
DEFAULT_CATEGORY = "27"  # Education


def get_credentials():
    """OAuth認証情報を取得（トークンリフレッシュ含む）"""
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("トークンリフレッシュ中...")
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET.exists():
                print(f"エラー: {CLIENT_SECRET} が見つかりません")
                print("Google Cloud Console からOAuth クライアントIDのJSONをダウンロードしてください")
                sys.exit(1)
            print("ブラウザで認証してください...")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())
        print(f"トークン保存: {TOKEN_FILE}")

    return creds


def upload_short(youtube, video_path, title, description, tags, category_id, privacy="public"):
    """YouTube Shortsとして動画をアップロード"""
    # #Shorts をタイトルと説明に含める
    if "#Shorts" not in title:
        title = f"{title} #Shorts"
    if "#Shorts" not in description:
        description += "\n\n#Shorts"

    body = {
        "snippet": {
            "title": title[:100],  # 最大100文字
            "description": description[:5000],
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "ja",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=256 * 1024,
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"  アップロード: {pct}%")

    video_id = response["id"]
    return video_id


def post_episode(youtube, ep_num, lang="jp"):
    """エピソードをYouTubeにアップロード"""
    with open(BASE / "batch_001_post_metadata.json", encoding="utf-8") as f:
        metadata = json.load(f)

    ep_data = metadata["episodes"][ep_num - 1]
    platform_key = f"youtube_shorts_{lang}"
    post_data = ep_data["platforms"][platform_key]

    title = post_data["title"]
    description = post_data["description"]
    tags = [t.strip().lstrip("#") for t in post_data["tags"].split("  ") if t.strip()] if isinstance(post_data["tags"], str) else post_data["tags"]
    # 追加ハッシュタグ
    extra_tags = ["fyp", "foryou", "foryoupage", "viral", "tiktok", "trending", "duet",
                  "funny", "comedy", "trend", "humor", "greenscreen", "anime", "love",
                  "stitch", "meme", "pov", "football", "explore", "like", "dance", "bts",
                  "learnontiktok", "food", "memes", "greenscreenvideo", "video"]
    tags = list(dict.fromkeys(tags + extra_tags))  # 重複除去
    category = ep_data.get("category", "")
    category_id = CATEGORY_MAP.get(category, DEFAULT_CATEGORY)

    # 動画ファイル（最新バージョン）
    ep_dir = BASE / f"ep{ep_num:02d}" / "output"
    videos = sorted(ep_dir.glob(f"wakufact_ep{ep_num:02d}_jp_sub_v*.mp4"))
    if not videos:
        print(f"エラー: EP{ep_num:02d} の動画が見つかりません")
        return None
    video_path = videos[-1]

    size_mb = video_path.stat().st_size / (1024 * 1024)
    print(f"\n=== EP{ep_num:02d} YouTube投稿 ===")
    print(f"  動画: {video_path.name} ({size_mb:.1f}MB)")
    print(f"  タイトル: {title}")
    print(f"  カテゴリ: {category} → {category_id}")
    print(f"  アップロード中...")

    video_id = upload_short(youtube, video_path, title, description, tags, category_id)
    url = f"https://youtube.com/shorts/{video_id}"
    print(f"  完了: {url}")
    return url


if __name__ == "__main__":
    if "--auth" in sys.argv:
        creds = get_credentials()
        youtube = build("youtube", "v3", credentials=creds)
        resp = youtube.channels().list(part="snippet", mine=True).execute()
        if resp["items"]:
            ch = resp["items"][0]["snippet"]
            print(f"認証OK: {ch['title']}")
        sys.exit(0)

    if "--check" in sys.argv:
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            if creds.valid:
                print("認証OK（トークン有効）")
            elif creds.expired and creds.refresh_token:
                print("トークン期限切れ（リフレッシュ可能）")
            else:
                print("トークン無効（再認証必要）")
        else:
            print("未認証（python3 post_youtube.py --auth を実行）")
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: python3 post_youtube.py <ep_num> [ep_num ...]")
        print("       python3 post_youtube.py --auth")
        sys.exit(1)

    ep_nums = [int(x) for x in sys.argv[1:] if x.isdigit()]
    if not ep_nums:
        print("エピソード番号を指定してください")
        sys.exit(1)

    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    results = {}
    for ep_num in ep_nums:
        results[ep_num] = post_episode(youtube, ep_num)
        if len(ep_nums) > 1:
            time.sleep(10)  # レート制限対策

    print(f"\n{'='*50}")
    print("=== 結果 ===")
    for ep, url in results.items():
        print(f"  EP{ep:02d}: {url or 'FAILED'}")
