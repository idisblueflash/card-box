from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, TypedDict


class CodexResponse(TypedDict, total=False):
    command: str
    cwd: str
    success: bool
    exit_code: int | None
    events: list[dict]
    stderr: str


class CacheEntry(TypedDict):
    prompt: str
    response: CodexResponse


def load_cache(path: Path) -> Dict[str, CacheEntry]:
    """Load cache from disk, upgrading legacy structures if needed."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(data, dict):
        return {}

    result: Dict[str, CacheEntry] = {}
    legacy_found = False
    for key, value in data.items():
        if not isinstance(value, dict):
            continue
        response = value.get("response")
        prompt_value = value.get("prompt", "")
        if isinstance(response, dict):
            result[str(key)] = {
                "prompt": str(prompt_value),
                "response": response,  # type: ignore[assignment]
            }
            continue
        if "events" in value:
            legacy_found = True
            result[str(key)] = {
                "prompt": str(prompt_value),
                "response": value,  # type: ignore[assignment]
            }
    if legacy_found:
        save_cache(path, result)
    return result


def save_cache(path: Path, cache: Dict[str, CacheEntry]) -> None:
    """Persist cache to disk."""
    path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def hash_prompt(prompt: str) -> str:
    """Stable hash for a prompt string."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()
