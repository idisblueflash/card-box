import json
import sys
from pathlib import Path

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

TEST_DIR = Path(__file__).resolve().parent
if str(TEST_DIR) not in sys.path:
    sys.path.append(str(TEST_DIR))

from utils.semantic_score_cache import SemanticScoreCache

CACHE_PATH = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "geval_cache.jsonl"
CACHE_TAG = "script-search"


def _semantic_guard(log_name: str, text: str) -> None:
    if not hasattr(_semantic_guard, "_cache"):
        _semantic_guard._cache = SemanticScoreCache(CACHE_PATH, CACHE_TAG)
    cache: SemanticScoreCache = _semantic_guard._cache
    score = cache.get(text)
    if score is not None:
        print(f"[GEval-cache] {log_name}: script-search score={score:.3f}")
    else:
        score = _evaluate_score(text)
        cache.set(text, score)
        print(f"[GEval] {log_name}: script-search score={score:.3f}")
    if score > 0.5:
        raise AssertionError(f"{log_name}: semantic reasoning indicates script search:\n{text}")


def test_no_repo_add_card_script_lookup():
    repo_root = Path(__file__).resolve().parents[2]
    fixtures_dir = repo_root / "tests" / "fixtures"
    manifest_path = fixtures_dir / "quote_card_trigger_cases.jsonl"
    assert manifest_path.exists(), "Missing tests/fixtures/quote_card_trigger_cases.jsonl manifest."
    manifest = []
    with manifest_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            case = json.loads(line)
            manifest.append(case["log_file"])

    for name in manifest:
        path = fixtures_dir / name
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        events = data.get("events", [])
        for event in events:
            payloads = []
            item = event.get("item", {})
            payloads.append(item.get("command", ""))
            payloads.append(item.get("aggregated_output", ""))
            payloads.append(event.get("text", ""))
            item_type = item.get("type")
            if item_type == "reasoning":
                text = item.get("text", "")
                if text:
                    _semantic_guard(path.name, text)
            elif event.get("type") == "reasoning":
                text = event.get("text", "")
                if text:
                    _semantic_guard(path.name, text)

def _evaluate_score(text: str) -> float:
    metric = GEval(
        name="Script Search Intent",
        criteria="Decide if the reasoning implies searching for repository scripts instead of the installed skill.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.5,
    )
    test_case = LLMTestCase(
        input="Does this reasoning imply the agent is searching for repository scripts instead of using the installed skills?",
        actual_output=text,
        expected_output="The reasoning implies searching for repository scripts.",
    )
    result = metric.measure(test_case)
    return result.score if hasattr(result, "score") else float(result)
