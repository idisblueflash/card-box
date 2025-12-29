from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.deepeval.utils import summary_oral_cache as cache_utils  # noqa: E402


def test_load_cache_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "cache.json"
    assert cache_utils.load_cache(path) == {}


def test_save_and_load_cache_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "cache.json"
    original = {
        "abc": {
            "prompt": "test prompt",
            "response": {"command": "cmd", "success": True, "events": []},
        }
    }
    cache_utils.save_cache(path, original)
    loaded = cache_utils.load_cache(path)
    assert loaded == original


def test_load_cache_migrates_legacy_entries(tmp_path: Path) -> None:
    path = tmp_path / "cache.json"
    legacy = {
        "legacy_key": {
            "command": "cmd",
            "success": True,
            "events": [],
        }
    }
    path.write_text(json.dumps(legacy, ensure_ascii=False), encoding="utf-8")
    loaded = cache_utils.load_cache(path)
    assert "legacy_key" in loaded
    entry = loaded["legacy_key"]
    assert entry["prompt"] == ""
    assert entry["response"]["command"] == "cmd"
    updated = json.loads(path.read_text(encoding="utf-8"))
    assert "response" in updated["legacy_key"]


def test_hash_prompt_is_stable() -> None:
    first = cache_utils.hash_prompt("hello")
    second = cache_utils.hash_prompt("hello")
    assert first == second
    assert first != cache_utils.hash_prompt("world")
