"""Create a WeChat DRAFT from one book-thread Markdown file.

Usage:
    WECHAT_TOKEN=... python3 scripts/publish_book_wechat.py --thread src/<book>.md

Prints the draft media_id. Review and publish manually in the MP backend.
Each run creates a NEW draft, so delete superseded ones. Never auto-publishes.
"""

import argparse
import os
import sys
from pathlib import Path

import md_to_wechat as md
import wechat_client as wc

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://xixiaofinland.com"
AUTHOR = "Xi Xiao"
DEFAULT_COVER = REPO_ROOT / "src" / "img" / "wechat" / "book-cover.png"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--thread", required=True, help="Path to the book thread .md (e.g. src/foo.md)")
    args = ap.parse_args()

    path = (REPO_ROOT / args.thread).resolve() if not os.path.isabs(args.thread) else Path(args.thread)
    if not path.is_file():
        print(f"error: thread not found: {args.thread}", file=sys.stderr)
        return 1

    source = path.read_text(encoding="utf-8")
    meta = md.parse_metadata(source)
    title, content = md.render(source)

    if meta.get("title"):
        title = meta["title"]
    if not title:
        print("error: no # H1 title found and no title override", file=sys.stderr)
        return 1
    if len(title) > 64:
        print(
            f"error: title is {len(title)} chars, WeChat limit is 64. "
            "Shorten the H1 or add 'title:' to the wechat comment.",
            file=sys.stderr,
        )
        return 1

    token = wc.get_token()

    cover_url = meta.get("cover")
    if cover_url:
        thumb = wc.upload_cover_from_url(token, cover_url)
    elif DEFAULT_COVER.is_file():
        thumb = wc.upload_cover_from_file(token, str(DEFAULT_COVER))
    else:
        print(f"error: no cover URL in thread and default missing: {DEFAULT_COVER}", file=sys.stderr)
        return 1

    slug = path.stem
    source_url = f"{BASE_URL}/{slug}.html?utm_source=wechat"

    media_id = wc.create_draft(
        token=token,
        title=title,
        content_html=content,
        thumb_media_id=thumb,
        digest="",  # empty -> WeChat auto-derives from content
        source_url=source_url,
        author=AUTHOR,
    )

    print(f"Draft created: {media_id}")
    print(f"Title: {title}")
    print("Review and publish at https://mp.weixin.qq.com (drafts).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
