#!/usr/bin/env python3
"""Run `codex exec` with inline text and emit a JSON summary."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Any, List


def read_prompt(text: str | None, file_path: str | None) -> str:
    if text is not None:
        return text
    if file_path is not None:
        return Path(file_path).read_text(encoding="utf-8")
    raise ValueError("Provide --text or --file.")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Wrap `codex exec` and print JSON output for the entire run."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="Prompt text to feed into Codex.")
    source.add_argument("--file", help="Path to a file containing the prompt.")
    parser.add_argument(
        "--codex-arg",
        action="append",
        default=[],
        help="Additional argument to pass directly to `codex exec` "
        "(repeatable, e.g. --codex-arg='-m gpt-4o-mini').",
    )
    parser.add_argument(
        "--working-dir",
        default=".",
        help="Directory from which to run `codex exec` (default: current directory).",
    )
    parser.add_argument(
        "--output-file",
        help="Optional path to write the JSON result (in addition to stdout).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Maximum seconds to wait for `codex exec` to finish (default: 60).",
    )
    return parser.parse_args(argv)


def run_codex(prompt: str, extra_args: List[str], cwd: str, timeout: float) -> dict[str, Any]:
    cmd = ["codex", "exec", "--json", "-"]
    cmd.extend(extra_args)
    try:
        process = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            cwd=cwd,
            timeout=timeout,
        )
    except TimeoutExpired as exc:
        return {
            "command": " ".join(shlex.quote(part) for part in cmd),
            "cwd": str(Path(cwd).resolve()),
            "success": False,
            "exit_code": None,
            "error": f"Timed out after {timeout} seconds.",
            "events": [],
            "stderr": exc.stderr,
        }

    events: List[Any] = []
    for line in process.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append({"type": "raw", "data": line})

    result: dict[str, Any] = {
        "command": " ".join(shlex.quote(part) for part in cmd),
        "cwd": str(Path(cwd).resolve()),
        "success": process.returncode == 0,
        "exit_code": process.returncode,
        "events": events,
    }
    if process.stderr:
        result["stderr"] = process.stderr
    return result


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    prompt = read_prompt(args.text, args.file)
    result = run_codex(prompt, args.codex_arg, args.working_dir, args.timeout)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    if args.output_file:
        Path(args.output_file).write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return 0 if result["success"] else result["exit_code"] or 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
