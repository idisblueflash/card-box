import json
from pathlib import Path

import deepeval  # noqa: F401 - ensures DeepEval plugins register


FIXTURE_PATH = Path(__file__).resolve().parents[2] / "output" / "codex_run.json"


def test_quote_card_trigger_present():
    assert FIXTURE_PATH.exists(), "Missing output/codex_run.json; generate via run_codex_exec.py."
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    events = data.get("events", [])
    assert any(
        event.get("type") == "item.started"
        and event.get("item", {}).get("type") == "command_execution"
        and "quote-card-trigger" in event.get("item", {}).get("command", "")
        for event in events
    ), "quote-card-trigger command execution not found in codex_run.json"
