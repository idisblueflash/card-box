#!/usr/bin/env python3
"""Batch runner that feeds prompts to run_codex_exec.py."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
from typing import Any, Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch Codex exec runner for JSONL prompts.")
    parser.add_argument(
        "--input-file",
        default="tests/fixtures/quote_card_trigger_cases.jsonl",
        help="Path to the JSONL file that stores prompts (default: tests/fixtures/quote_card_trigger_cases.jsonl).",
    )
    parser.add_argument(
        "--output-dir",
        default="tests/fixtures",
        help="Directory to store generated codex_run JSON files (default: tests/fixtures).",
    )
    parser.add_argument(
        "--prefix",
        default="codex_run_case",
        help="Filename prefix for generated JSON files (default: codex_run_case).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Timeout (seconds) for each run_codex_exec invocation (default: 60).",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel workers (default: 1).",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        help="Limit the number of cases to run (useful for smoke tests).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files (default: skip existing).",
    )
    return parser.parse_args()


def load_cases(path: Path, max_cases: int | None) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            cases.append(json.loads(line))
            if max_cases and len(cases) >= max_cases:
                break
    return cases


def run_single(
    case_idx: int,
    case: Dict[str, Any],
    script_path: Path,
    output_path: Path,
    timeout: float,
) -> tuple[int, bool, str]:
    cmd = [
        "python3",
        str(script_path),
        "--text",
        case["prompt"],
        "--timeout",
        str(timeout),
        "--output-file",
        str(output_path),
    ]
    try:
        subprocess.run(cmd, check=True, cwd=script_path.parents[1])
        return case_idx, True, ""
    except subprocess.CalledProcessError as exc:
        return case_idx, False, f"Command failed (exit {exc.returncode}): {' '.join(cmd)}"


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_file).resolve()
    base_dir = input_path.parent
    output_dir = Path(args.output_dir).resolve()
    script = Path(__file__).resolve().with_name("run_codex_exec.py")

    output_dir.mkdir(parents=True, exist_ok=True)
    cases = load_cases(input_path, args.max_cases)
    if not cases:
        print(f"No cases loaded from {input_path}")
        return 1

    tasks = []
    with ThreadPoolExecutor(max_workers=max(1, args.parallel)) as executor:
        for idx, case in enumerate(cases, start=1):
            log_file = case.get("log_file")
            if log_file:
                output_path = Path(log_file)
                if not output_path.is_absolute():
                    output_path = base_dir / output_path
            else:
                output_path = output_dir / f"{args.prefix}_{idx}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if output_path.exists() and not args.overwrite:
                print(f"[skip] Case {idx} -> {output_path} already exists.")
                continue
            print(f"[run ] Case {idx} -> {output_path}")
            tasks.append(
                executor.submit(
                    run_single,
                    idx,
                    case,
                    script,
                    output_path,
                    args.timeout,
                )
            )

        for future in as_completed(tasks):
            idx, success, message = future.result()
            if success:
                print(f"[done] Case {idx} finished successfully.")
            else:
                print(f"[fail] Case {idx} failed: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
