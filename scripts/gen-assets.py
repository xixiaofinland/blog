#!/usr/bin/env python3
# Prepare a markdown article for LinkedIn publishing.
#
# For each article it produces a linkedin/ subfolder containing:
#   linkedin/<slug>/article.txt   paste-ready text with [IMAGE: filename] placeholders
#   linkedin/<slug>/diagram-N.png rendered mermaid diagrams
#   linkedin/<slug>/code-N-<lang>.png  syntax-highlighted code images
#
# Existing inline images (![](img/...)) become placeholders pointing at their
# original filename — you upload those separately from src/img/.
#
# Usage:
#   python3 scripts/gen-assets.py src/<article>.md
#   python3 scripts/gen-assets.py src/<article>.md --no-code  # skip code blocks

import re
import sys
import subprocess
import tempfile
from pathlib import Path

FREEZE_FLAGS = [
    "--window",
    "--border.radius", "8",
    "--shadow.blur", "20",
    "--shadow.x", "4",
    "--shadow.y", "4",
]
FREEZE_THEME = "dracula"


def extract_blocks(content: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"^```(\w+)\n(.*?)^```", re.DOTALL | re.MULTILINE)
    return [(m.group(1), m.group(2).rstrip()) for m in pattern.finditer(content)]


def render_mermaid(code: str, outpng: Path) -> None:
    with tempfile.NamedTemporaryFile(suffix=".mmd", mode="w", delete=False) as f:
        f.write(code + "\n")
        src = f.name
    subprocess.run(
        ["nix", "run", "nixpkgs#mermaid-cli", "--", "-i", src, "-o", str(outpng)],
        check=True,
    )
    Path(src).unlink()


def render_code(code: str, lang: str, outpng: Path) -> None:
    subprocess.run(
        [
            "nix", "run", "nixpkgs#charm-freeze", "--", "-",
            "--language", lang,
            "--theme", FREEZE_THEME,
            "--output", str(outpng),
            *FREEZE_FLAGS,
        ],
        input=code.encode(),
        check=True,
    )


def build_linkedin_text(content: str, replacements: list[tuple[str, str]]) -> str:
    """Apply replacements (old, new) in order, then clean up for LinkedIn."""
    text = content
    for old, new in replacements:
        text = text.replace(old, new, 1)

    # Strip frontmatter if present
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)

    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def main() -> None:
    args = sys.argv[1:]
    no_code = "--no-code" in args
    files = [a for a in args if not a.startswith("--")]

    if not files:
        print("Usage: gen-assets.py <markdown-file> [--no-code]")
        sys.exit(1)

    infile = Path(files[0])
    if not infile.exists():
        print(f"File not found: {infile}")
        sys.exit(1)

    slug = infile.stem
    outdir = Path("linkedin") / slug
    outdir.mkdir(parents=True, exist_ok=True)

    content = infile.read_text()

    # ── Pass 1: collect all fenced blocks and plan replacements
    block_pattern = re.compile(r"^(```(\w+)\n.*?^```)", re.DOTALL | re.MULTILINE)
    replacements: list[tuple[str, str]] = []  # (original_text, placeholder)
    render_jobs: list[tuple[str, str, Path]] = []  # (lang, code, outpng)

    mermaid_n = 0
    code_n = 0

    for m in block_pattern.finditer(content):
        full_block = m.group(1)
        lang = m.group(2)
        code = full_block[len(f"```{lang}\n"):-3].rstrip()

        if lang == "mermaid":
            mermaid_n += 1
            fname = f"diagram-{mermaid_n}.png"
            outpng = outdir / fname
            replacements.append((full_block, f"[IMAGE: {fname}]"))
            render_jobs.append(("mermaid", code, outpng))
        elif not no_code:
            code_n += 1
            fname = f"code-{code_n}-{lang}.png"
            outpng = outdir / fname
            replacements.append((full_block, f"[IMAGE: {fname}]"))
            render_jobs.append((lang, code, outpng))

    # ── Pass 2: replace existing inline images with placeholders
    img_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    for m in img_pattern.finditer(content):
        full_ref = m.group(0)
        fname = Path(m.group(2)).name
        replacements.append((full_ref, f"[IMAGE: {fname}]"))

    # ── Render assets
    for lang, code, outpng in render_jobs:
        if outpng.exists():
            print(f"skip (exists): {outpng.name}")
            continue
        print(f"rendering: {outpng.name}")
        if lang == "mermaid":
            render_mermaid(code, outpng)
        else:
            render_code(code, lang, outpng)
        print(f"  ok")

    # ── Write article text
    article_text = build_linkedin_text(content, replacements)
    outfile = outdir / "article.txt"
    outfile.write_text(article_text)

    rendered = sum(1 for _, _, p in render_jobs if p.exists())
    existing_imgs = len(img_pattern.findall(content))
    print(f"\nDone.")
    print(f"  {rendered} image(s) rendered to {outdir}/")
    print(f"  {existing_imgs} existing image placeholder(s) — upload from src/img/{slug}/")
    print(f"  Article text: {outfile}")


if __name__ == "__main__":
    main()
