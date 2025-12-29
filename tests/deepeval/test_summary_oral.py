from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, TypedDict

from deepeval import evaluate
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.metrics import SummarizationMetric
from deepeval.test_case import LLMTestCase


class CodexResponse(TypedDict, total=False):
    command: str
    cwd: str
    success: bool
    exit_code: int | None
    events: list[dict]
    stderr: str


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_codex_exec import run_codex  # noqa: E402

CREATE_NOTE_MARKER = "skills/add-card/scripts/create_note.py"
DEFAULT_TIMEOUT = 60.0
DEFAULT_WORKING_DIR = REPO_ROOT / "codex_tmp"
DEFAULT_SANDBOX = "workspace-write"
CACHE_FILE = REPO_ROOT / "tests" / "fixtures" / "summary_oral_cache.json"


def _load_cache() -> Dict[str, CodexResponse]:
    if not CACHE_FILE.exists():
        return {}
    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if isinstance(data, dict):
        result: Dict[str, CodexResponse] = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[str(key)] = value  # type: ignore[assignment]
        return result
    return {}


def _save_cache(cache: Dict[str, CodexResponse]) -> None:
    CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

skill = "[$add-card](/Users/husongtao/.codex/skills/add-card/SKILL.md) "

goldens = [
    Golden(input=skill + "今天复盘账会的提醒是关于今天晚上前要完成登录功能的买点验证。"),
    Golden(
        input=skill
        + "今天有一些反思,需要记录一下。 比如说需要提前准备演示的环境。 这里面应该可以向研发申请额外的测试机器。 "
    ),
]


def load_codex_response(prompt: str) -> CodexResponse:
    """Run Codex once for the given prompt and return the raw response."""
    cache = _load_cache()
    cache_key = _hash_prompt(prompt)
    cached = cache.get(cache_key)
    if cached:
        return cached

    DEFAULT_WORKING_DIR.mkdir(parents=True, exist_ok=True)
    result = run_codex(
        prompt=prompt,
        extra_args=[],
        repo_root=REPO_ROOT,
        timeout=DEFAULT_TIMEOUT,
        working_dir=DEFAULT_WORKING_DIR,
        sandbox=DEFAULT_SANDBOX,
    )
    if not result.get("success"):
        raise RuntimeError("run_codex_exec.run_codex reported failure.")

    cache[cache_key] = result  # type: ignore[assignment]
    _save_cache(cache)
    return result


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
    response = load_codex_response(golden.input)
    summary = extract_card_summary(response.get("events", []))
    test_cases.append(LLMTestCase(input=golden.input, actual_output=summary))

evaluate(
    test_cases=test_cases,
    metrics=[SummarizationMetric()],
)
