import json
from pathlib import Path


def test_quote_skill_trigger_from_fixture():
    repo_root = Path(__file__).resolve().parents[2]
    result_path = repo_root / "output" / "codex_run.json"
    assert result_path.exists(), "Missing output/codex_run.json fixture."

    data = json.loads(result_path.read_text(encoding="utf-8"))
    events = data.get("events", [])
    trigger = any(
        event.get("type") == "item.started"
        and event.get("item", {}).get("type") == "command_execution"
        and "quote-card-trigger" in event.get("item", {}).get("command", "")
        for event in events
    )
    assert trigger, "quote-card-trigger was not invoked for pure blockquote input."
