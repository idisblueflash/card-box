#!/usr/bin/env python3
"""Utility to create Obsidian-ready fleeting notes.

The script builds a Markdown file inside the `fleeting` folder (configurable through
CLI arguments). It keeps the filename aligned with the provided title, falling back
to a lightly sanitized variant when illegal path characters appear.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import sys
from typing import List


INVALID_PATH_CHARS = r'[\\/:*?"<>|]'


def sanitize_filename(title: str) -> str:
    """Remove characters that cannot appear in a filename."""
    cleaned = re.sub(INVALID_PATH_CHARS, "", title).strip()
    return cleaned or "Untitled"


def build_content(title: str, summary: str, tags: List[str]) -> str:
    timestamp = datetime.now().isoformat(timespec="seconds")
    tags_block = "\n".join(f"  - {tag}" for tag in tags)
    parts = [
        "---",
        f"title: {title}",
        f"created: {timestamp}",
        "tags:",
        tags_block,
        "---",
        "",
        f"# {title}",
        "",
        summary.strip(),
        "",
    ]
    return "\n".join(parts)


def create_note(folder: Path, title: str, summary: str, tags: List[str]) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(title)
    note_path = folder / f"{filename}.md"
    note_path.write_text(build_content(title, summary, tags), encoding="utf-8")
    return note_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a fleeting note for Obsidian."
    )
    parser.add_argument("--title", required=True, help="Note title, also used as filename.")
    parser.add_argument(
        "--summary",
        required=True,
        help="One to two sentences that summarize the captured voice note.",
    )
    parser.add_argument(
        "--folder",
        default="fleeting",
        help="Target folder for fleeting notes (default: ./fleeting).",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        default=["fleeting"],
        help="Tags to embed in the frontmatter (default: fleeting).",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    note_path = create_note(Path(args.folder), args.title, args.summary, args.tags)
    print(f"Created note at {note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
