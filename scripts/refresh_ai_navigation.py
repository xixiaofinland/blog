#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

SUMMARY_PATH = SRC / "SUMMARY.md"
LATEST_PATH = SRC / "ai-latest.md"

LATEST_LIMIT = 7
CURRENT_YEAR = dt.date.today().year

SUMMARY_START = "<!-- AI_NAV_START -->"
SUMMARY_END = "<!-- AI_NAV_END -->"
LATEST_START = "<!-- AI_LATEST_LINKS_START -->"
LATEST_END = "<!-- AI_LATEST_LINKS_END -->"
ARCHIVE_START = "<!-- AI_ARCHIVE_LINKS_START -->"
ARCHIVE_END = "<!-- AI_ARCHIVE_LINKS_END -->"

LINK_RE = re.compile(r"^- \[(?P<title>.+?)\]\((?P<path>[^)]+)\)$", re.MULTILINE)
H1_RE = re.compile(r"^# (?P<title>.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Link:
    title: str
    path: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def ensure_archive_page(path: Path, year: int) -> None:
    if path.exists():
        return

    write_text(
        path,
        "\n".join(
            [
                f"# AI & Machine Learning Archive {year}",
                "",
                (
                    f"Older AI and machine learning threads from {year} land "
                    "here after they rotate out of the sidebar."
                ),
                "",
                ARCHIVE_START,
                ARCHIVE_END,
            ]
        ),
    )


def extract_block(text: str, start_marker: str, end_marker: str) -> str:
    pattern = re.compile(
        rf"{re.escape(start_marker)}(.*?)\s*{re.escape(end_marker)}",
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise ValueError(f"Missing marker block: {start_marker} ... {end_marker}")
    return match.group(1).strip()


def replace_block(
    text: str, start_marker: str, end_marker: str, lines: list[str]
) -> str:
    body = "\n".join(lines)
    replacement = f"{start_marker}\n{body}\n{end_marker}"
    # Allow optional leading horizontal whitespace before end_marker (formatter may indent it)
    pattern = re.compile(
        rf"{re.escape(start_marker)}.*?[ \t]*{re.escape(end_marker)}",
        re.DOTALL,
    )
    if not pattern.search(text):
        raise ValueError(f"Missing marker block: {start_marker} ... {end_marker}")
    return pattern.sub(replacement, text, count=1)


def parse_links(block_text: str) -> list[Link]:
    return [
        Link(match.group("title").strip(), match.group("path").strip())
        for match in LINK_RE.finditer(block_text)
    ]


def unique_links(links: list[Link]) -> list[Link]:
    seen: set[str] = set()
    result: list[Link] = []
    for link in links:
        if link.path in seen:
            continue
        seen.add(link.path)
        result.append(link)
    return result


def normalize_post_path(raw_path: str) -> str:
    raw = Path(raw_path)
    if raw.is_absolute():
        try:
            return raw.resolve().relative_to(SRC.resolve()).as_posix()
        except ValueError as exc:
            raise ValueError(f"Path must live under {SRC}: {raw_path}") from exc

    parts = raw.parts
    if parts and parts[0] == "src":
        raw = Path(*parts[1:])

    normalized = (SRC / raw).resolve()
    try:
        return normalized.relative_to(SRC.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"Path must live under {SRC}: {raw_path}") from exc


def read_post_title(relative_post_path: str) -> str:
    text = read_text(SRC / relative_post_path)
    match = H1_RE.search(text)
    if not match:
        raise ValueError(f"Could not find an H1 title in src/{relative_post_path}")
    return match.group("title").strip()


def post_year(relative_post_path: str) -> int:
    repo_path = f"src/{relative_post_path}"
    proc = subprocess.run(
        [
            "git",
            "log",
            "--follow",
            "--diff-filter=A",
            "--format=%ad",
            "--date=format:%Y",
            "--",
            repo_path,
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    year = proc.stdout.strip().splitlines()
    if year:
        return int(year[0])
    return CURRENT_YEAR


def archive_path(year: int) -> Path:
    return SRC / f"ai-archive-{year}.md"


def load_latest_links() -> list[Link]:
    return parse_links(extract_block(read_text(LATEST_PATH), LATEST_START, LATEST_END))


def discover_archive_years() -> set[int]:
    years = {CURRENT_YEAR}
    for path in SRC.glob("ai-archive-*.md"):
        suffix = path.stem.removeprefix("ai-archive-")
        if suffix.isdigit():
            years.add(int(suffix))
    return years


def load_archive_links(year: int) -> list[Link]:
    path = archive_path(year)
    ensure_archive_page(path, year)
    return parse_links(extract_block(read_text(path), ARCHIVE_START, ARCHIVE_END))


def write_links_block(path: Path, start_marker: str, end_marker: str, links: list[Link]) -> None:
    text = read_text(path)
    rendered = [f"- [{link.title}]({link.path})" for link in links]
    write_text(path, replace_block(text, start_marker, end_marker, rendered))


def write_summary(latest_links: list[Link], archive_links: dict[int, list[Link]]) -> None:
    summary_lines = ["- [AI & Machine Learning](ai.md)"]
    for link in latest_links:
        summary_lines.append(f"  - [{link.title}]({link.path})")

    for year in sorted(archive_links, reverse=True):
        links = archive_links[year]
        if year != CURRENT_YEAR and not links:
            continue

        summary_lines.append(f"  - [Archive {year}](ai-archive-{year}.md)")
        for link in links:
            summary_lines.append(f"    - [{link.title}]({link.path})")

    text = read_text(SUMMARY_PATH)
    write_text(SUMMARY_PATH, replace_block(text, SUMMARY_START, SUMMARY_END, summary_lines))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh the AI navigation block in src/SUMMARY.md."
    )
    parser.add_argument(
        "--add",
        help=(
            "New AI or machine learning post to add to the top of the sidebar, "
            "relative to the repo root or src/."
        ),
    )
    args = parser.parse_args()

    latest_links = load_latest_links()
    archive_links = {
        year: load_archive_links(year) for year in sorted(discover_archive_years(), reverse=True)
    }

    if args.add:
        relative_post_path = normalize_post_path(args.add)
        new_link = Link(read_post_title(relative_post_path), relative_post_path)
        latest_links = [new_link] + [link for link in latest_links if link.path != new_link.path]
        archive_links = {
            year: [link for link in links if link.path != new_link.path]
            for year, links in archive_links.items()
        }

    latest_links = unique_links(latest_links)
    overflow_links = latest_links[LATEST_LIMIT:]
    latest_links = latest_links[:LATEST_LIMIT]

    for overflow_link in overflow_links:
        year = post_year(overflow_link.path)
        archive_links.setdefault(year, [])
        archive_links[year] = [overflow_link] + [
            link for link in archive_links[year] if link.path != overflow_link.path
        ]

    archive_links = {
        year: unique_links(links) for year, links in archive_links.items()
    }

    write_links_block(LATEST_PATH, LATEST_START, LATEST_END, latest_links)
    for year, links in archive_links.items():
        path = archive_path(year)
        ensure_archive_page(path, year)
        write_links_block(path, ARCHIVE_START, ARCHIVE_END, links)

    write_summary(latest_links, archive_links)

    latest_count = len(latest_links)
    archive_count = sum(len(links) for links in archive_links.values())
    print(
        f"Updated AI navigation: {latest_count} latest thread(s), "
        f"{archive_count} archived thread(s)."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)
