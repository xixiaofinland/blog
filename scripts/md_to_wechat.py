"""Convert a book-thread Markdown file into WeChat-safe inline-styled HTML.

WeChat's editor strips <a>, <ol>, <li>, external CSS and most tags, so every
element carries inline styles and links become plain text. This is the piece
neither this repo nor viikkoja had: a real Markdown -> WeChat renderer.

Also parses the optional metadata comment at the top of a thread:

    <!-- wechat: cover: https://.../book.jpg; title: Short override -->

`cover` and `title` are both optional. No comment -> default cover + H1 title.
"""

import html
import re

# ── Metadata flag ──────────────────────────────────────────────────────────

_COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)
_META_KEYS = {"book", "cover", "title"}
_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def first_image(md: str) -> str | None:
    """Return the src of the first inline Markdown image, or None.

    Used as the WeChat cover source: the same cover shown in the blog thread.
    """
    m = _IMG_RE.search(md)
    return m.group(1).strip() if m else None


def parse_metadata(md: str) -> dict:
    """Read flat metadata from HTML comments (all optional, all invisible in mdBook):

        <!-- book: Trillion Dollar Coach -->
        <!-- cover: https://example.com/jacket.jpg -->
        <!-- title: A shorter WeChat title -->

    Separate comments or one ';'-separated comment both work. Only book/cover/title
    keys are read; any other comment is ignored.
    """
    out: dict = {}
    for body in _COMMENT_RE.findall(md):
        for part in body.split(";"):
            key, sep, val = part.partition(":")
            if sep and key.strip().lower() in _META_KEYS:
                out[key.strip().lower()] = val.strip()
    return out


# ── Inline styling (mirrors viikkoja's WeChat-safe look) ─────────────────────


def _p(inner: str) -> str:
    return (
        '<p style="margin:0 0 16px;font-size:16px;color:#333;'
        f'line-height:1.85;">{inner}</p>'
    )


def _h2(inner: str) -> str:
    return (
        '<p style="margin:28px 0 12px;font-size:18px;font-weight:800;'
        "color:#e87b1a;line-height:1.6;padding-bottom:8px;"
        f'border-bottom:1px solid #f0d8b8;">{inner}</p>'
    )


def _h3(inner: str) -> str:
    return (
        '<p style="margin:22px 0 10px;font-size:16px;font-weight:700;'
        f'color:#1a1a1a;line-height:1.6;">{inner}</p>'
    )


def _divider() -> str:
    return (
        '<p style="margin:24px 0;text-align:center;color:#c9a06a;'
        'font-size:14px;letter-spacing:0.4em;">· · ·</p>'
    )


def _meta(rows: list[str]) -> str:
    """Render the top-of-thread blockquote (rating / medium / language) as a card.

    In mdBook these are ``>`` lines; WeChat has no blockquote, so collect the
    rows into one warm-toned box that reads as a book's at-a-glance metadata.
    """
    inner = "".join(
        '<p style="margin:0 0 6px;font-size:14px;color:#666;'
        f'line-height:1.75;">{_inline(r)}</p>'
        for r in rows
    )
    return (
        '<section style="margin:0 0 24px;padding:12px 16px 6px;'
        'background:#faf6f0;border-left:3px solid #e87b1a;'
        f'border-radius:4px;">{inner}</section>'
    )


def img_placeholder(idx: int) -> str:
    """Placeholder src emitted for the idx-th inline body image.

    render() cannot upload images to WeChat (no token here), so it emits this
    marker as the <img src>. The publish step uploads each image in order and
    swaps the marker for the WeChat-hosted URL.
    """
    return f"%%WXIMG{idx}%%"


def _img(idx: int) -> str:
    return (
        '<p style="text-align:center;margin:0 0 20px;">'
        f'<img src="{img_placeholder(idx)}" style="max-width:100%;border-radius:4px;"/>'
        "</p>"
    )


# ── Inline markup: escape first, then add tags ───────────────────────────────


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    # images are handled as the cover, not shown inline in the WeChat body
    text = _IMG_RE.sub("", text)
    # links: no <a> allowed, render as "text (url)"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r'<code style="color:#c0341d;">\1</code>', text)
    # italic: _x_ or *x*, avoid word-internal underscores
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


# ── Block parser ─────────────────────────────────────────────────────────────


def render(md: str) -> tuple[str, str, list[str]]:
    """Return (title, content_html, image_srcs).

    Title comes from the first H1. `image_srcs` lists the inline body images in
    document order; the content carries an ``img_placeholder(i)`` marker for
    each, which the publish step swaps for the uploaded WeChat URL.
    """
    body = _COMMENT_RE.sub("", md)
    lines = body.splitlines()

    title = ""
    blocks: list[str] = []
    para: list[str] = []
    meta: list[str] = []
    images: list[str] = []

    def flush() -> None:
        if para:
            blocks.append(_p(_inline(" ".join(para).strip())))
            para.clear()
        if meta:
            blocks.append(_meta(list(meta)))
            meta.clear()

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if stripped in ("---", "***", "___"):
            flush()
            blocks.append(_divider())
            continue
        if stripped.startswith(">"):  # blockquote -> metadata card; keep accruing rows
            if para:
                blocks.append(_p(_inline(" ".join(para).strip())))
                para.clear()
            row = stripped[1:].strip()
            if row:
                meta.append(row)
            continue
        if stripped.startswith("!["):  # standalone image line -> inline body image
            flush()
            m = _IMG_RE.search(stripped)
            if m:
                blocks.append(_img(len(images)))
                images.append(m.group(1).strip())
            continue
        if stripped.startswith("# "):
            flush()
            if not title:
                title = _inline(stripped[2:].strip())
            continue
        if stripped.startswith("### "):
            flush()
            blocks.append(_h3(_inline(stripped[4:].strip())))
            continue
        if stripped.startswith("## "):
            flush()
            blocks.append(_h2(_inline(stripped[3:].strip())))
            continue
        para.append(stripped)
    flush()

    content = (
        '<section style="padding:12px 8px;font-family:-apple-system,BlinkMacSystemFont,'
        f'\'Segoe UI\',sans-serif;">{"".join(blocks)}</section>'
    )
    # strip any residual inline tags from the plain-text title
    plain_title = re.sub(r"<[^>]+>", "", title)
    return plain_title, content, images
