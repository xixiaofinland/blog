"""Minimal WeChat Official Account (公众号) MP API client. Stdlib only.

Ported from viikkoja's newsbot.distribute.wechat, trimmed to the three
side-effect-free calls this repo needs: fetch token, upload a cover image,
create a draft. It NEVER publishes (no freepublish/submit) — every run creates
a DRAFT you approve by hand in the MP backend.

The access token must be supplied via the WECHAT_TOKEN env var. WeChat's token
endpoint requires an IP-whitelisted caller, so a static VM pre-fetches the
token and pushes it to this repo's WECHAT_TOKEN secret (see scripts/README.md).
"""

import json
import os
import urllib.parse
import urllib.request
import uuid

WECHAT_API = "https://api.weixin.qq.com/cgi-bin"


def find_cover_url(book_title: str) -> str | None:
    """Look up a book cover on Open Library by title. Returns an image URL or None.

    Free, no API key. Good coverage for English books, spotty for Chinese ones,
    hence the caller falls back to the default cover when this returns None.
    """
    q = urllib.parse.urlencode({"title": book_title, "limit": "1", "fields": "cover_i"})
    try:
        with urllib.request.urlopen(f"https://openlibrary.org/search.json?{q}", timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None
    docs = data.get("docs") or []
    cover_i = docs[0].get("cover_i") if docs else None
    if not cover_i:
        return None
    return f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"


def get_token() -> str:
    token = os.environ.get("WECHAT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("WECHAT_TOKEN not set. The VM must pre-fetch it into the repo secret.")
    return token


def _post_json(url: str, payload: dict) -> dict:
    # ensure_ascii=False keeps Chinese readable in the request body
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json; charset=utf-8"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post_multipart_image(url: str, filename: str, content: bytes, ctype: str) -> dict:
    boundary = "----wechatbook" + uuid.uuid4().hex
    pre = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="media"; filename="{filename}"\r\n'
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode("utf-8")
    body = pre + content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def upload_cover_from_url(token: str, image_url: str) -> str:
    """Download a book cover from a URL, upload as WeChat material. Returns media_id."""
    with urllib.request.urlopen(image_url, timeout=30) as img:
        content = img.read()
        ct = img.headers.get("content-type", "image/jpeg")
    ext = "jpg" if ("jpeg" in ct or "jpg" in ct) else "png"
    return _upload(token, f"cover.{ext}", content, ct)


def upload_cover_from_file(token: str, path: str) -> str:
    """Upload a local cover image file as WeChat material. Returns media_id."""
    with open(path, "rb") as f:
        content = f.read()
    ctype = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return _upload(token, os.path.basename(path), content, ctype)


def _upload(token: str, filename: str, content: bytes, ctype: str) -> str:
    url = f"{WECHAT_API}/material/add_material?access_token={token}&type=image"
    data = _post_multipart_image(url, filename, content, ctype)
    if "media_id" not in data:
        raise RuntimeError(f"WeChat image upload error: {data}")
    return data["media_id"]


def create_draft(
    token: str,
    title: str,
    content_html: str,
    thumb_media_id: str,
    digest: str,
    source_url: str,
    author: str,
) -> str:
    """Create a DRAFT article. Returns the draft media_id. Does not publish."""
    url = f"{WECHAT_API}/draft/add?access_token={token}"
    data = _post_json(
        url,
        {
            "articles": [
                {
                    "title": title,
                    "author": author,
                    "digest": digest,
                    "show_cover_pic": 0,
                    "content": content_html,
                    "content_source_url": source_url,
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": 0,
                    "only_fans_can_comment": 0,
                }
            ]
        },
    )
    if "media_id" not in data:
        raise RuntimeError(f"WeChat draft creation error: {data}")
    return data["media_id"]
