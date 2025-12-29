from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Iterable

from deepeval import evaluate
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.metrics import SummarizationMetric
from deepeval.test_case import LLMTestCase


REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_EXEC_SCRIPT = REPO_ROOT / "scripts" / "run_codex_exec.py"
DEFAULT_OUTPUT = REPO_ROOT / "tmp.json"
CREATE_NOTE_MARKER = "add-card/scripts/create_note.py"

skill = "[$add-card](/Users/husongtao/.codex/skills/add-card/SKILL.md) "

goldens = [
    Golden(input=skill + "今天复盘账会的提醒是关于今天晚上前要完成登录功能的买点验证。"),
    Golden(
        input=skill
        + "今天有一些反思,需要记录一下。 比如说需要提前准备演示的环境。 这里面应该可以向研发申请额外的测试机器。 "
    ),
]


def load_codex_response(prompt: str) -> str:
    """Run Codex once for the given prompt and return the note summary."""
    cmd = [
        "python3",
        str(RUN_EXEC_SCRIPT),
        "--text",
        prompt,
        "--output-file",
        str(DEFAULT_OUTPUT),
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"run_codex_exec.py failed with exit {proc.returncode}: {proc.stderr}"
        )

    data = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
    return extract_card_summary(data.get("events", []))


def extract_card_summary(events: Iterable[dict]) -> str:
    """Parse aggregated_output of the create_note command and return summary."""
    for event in events:
        if event.get("type") != "item.completed":
            continue
        item = event.get("item") or {}
        if item.get("type") != "command_execution":
            continue
        command = item.get("command", "")
        if CREATE_NOTE_MARKER not in command:
            continue
        body = item.get("aggregated_output") or ""
        summary = parse_summary_from_aggregated_output(body)
        if summary:
            return summary
    raise ValueError("No create_note command output with summary found.")


def parse_summary_from_aggregated_output(output: str) -> str:
    """Extract card_json block from aggregated output and return its summary."""
    match = re.search(r"```card_json\s*(\{.*?\})\s*```", output, re.DOTALL)
    if not match:
        return ""
    try:
        card = json.loads(match.group(1))
    except json.JSONDecodeError:
        return ""
    summary = card.get("summary")
    return summary or ""


dataset = EvaluationDataset(goldens)
test_cases = []

for golden in dataset.goldens:
    res = load_codex_response(golden.input)
    test_cases.append(LLMTestCase(input=golden.input, actual_output=res))

evaluate(
    test_cases=test_cases,
    metrics=[SummarizationMetric()],
)
