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

_FLAG_RE = re.compile(r"<!--\s*wechat:\s*(.*?)\s*-->", re.DOTALL)


def parse_metadata(md: str) -> dict:
    """Return {cover, title} from the wechat comment, if present."""
    m = _FLAG_RE.search(md)
    if not m:
        return {}
    out: dict = {}
    for part in m.group(1).split(";"):
        if ":" not in part:
            continue
        key, _, val = part.partition(":")
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


# ── Inline markup: escape first, then add tags ───────────────────────────────


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    # links: no <a> allowed, render as "text (url)"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r'<code style="color:#c0341d;">\1</code>', text)
    # italic: _x_ or *x*, avoid word-internal underscores
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


# ── Block parser ─────────────────────────────────────────────────────────────


def render(md: str) -> tuple[str, str]:
    """Return (title, content_html). Title comes from the first H1."""
    body = _FLAG_RE.sub("", md)
    lines = body.splitlines()

    title = ""
    blocks: list[str] = []
    para: list[str] = []

    def flush() -> None:
        if para:
            blocks.append(_p(_inline(" ".join(para).strip())))
            para.clear()

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
    return plain_title, content
