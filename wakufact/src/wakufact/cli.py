"""WakuFact CLI エントリーポイント"""

import argparse
import json
import sys
from pathlib import Path

from .producer import produce_episode


def main():
    parser = argparse.ArgumentParser(description="WakuFact - AI雑学ショート動画制作")
    parser.add_argument("episode_json", type=Path,
                        help="エピソード定義JSON (sections + image_prompts)")
    parser.add_argument("--ep", type=int, required=True,
                        help="エピソード番号")
    parser.add_argument("--title", type=str, required=True,
                        help="エピソードタイトル")
    parser.add_argument("--outdir", type=Path, default=Path.cwd(),
                        help="出力ベースディレクトリ (default: cwd)")
    parser.add_argument("--version", type=int, default=1,
                        help="出力バージョン番号 (default: 1)")
    args = parser.parse_args()

    if not args.episode_json.exists():
        print(f"Error: {args.episode_json} not found", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.episode_json.read_text())
    sections = data["sections"]
    image_prompts = data["image_prompts"]

    produce_episode(
        ep_num=args.ep,
        title=args.title,
        sections=sections,
        image_prompts=image_prompts,
        base_dir=args.outdir,
        version=args.version,
    )


if __name__ == "__main__":
    main()
