import json
from pathlib import Path


def test_quote_skill_trigger_from_fixture():
    repo_root = Path(__file__).resolve().parents[2]
    fixtures_dir = repo_root / "tests" / "fixtures"
    manifest_path = fixtures_dir / "quote_card_trigger_cases.jsonl"
    assert manifest_path.exists(), "Missing tests/fixtures/quote_card_trigger_cases.jsonl manifest."
    manifest = {}
    with manifest_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            case = json.loads(line)
            manifest[case["log_file"]] = case

    json_files = sorted((fixtures_dir / name) for name in manifest)

    for path in json_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        events = data.get("events", [])
        trigger = any(
            event.get("type") == "item.started"
            and event.get("item", {}).get("type") == "command_execution"
            and "quote-card-trigger" in event.get("item", {}).get("command", "")
            for event in events
        )
        case = manifest.get(path.name, {})
        expected = case.get("expected_trigger", True)
        if trigger != expected:
            prompt = case.get("prompt", "").strip()
            error_message = (
                f"{path.name}: trigger mismatch (expected {expected}, got {trigger}).\n"
                f"Prompt:\n{prompt}"
            )
            raise AssertionError(error_message)
