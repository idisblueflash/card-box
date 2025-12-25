import json
from pathlib import Path
from typing import Dict, Tuple


class SemanticScoreCache:
    def __init__(self, path: Path, tag: str):
        self.path = path
        self.tag = tag
        self._cache = self._load_cache()

    def _load_cache(self) -> Dict[Tuple[str, str], float]:
        cache: Dict[Tuple[str, str], float] = {}
        if self.path.exists():
            with self.path.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    tag = entry.get("tag")
                    if not tag:
                        continue
                    key = (tag, entry["text"])
                    cache[key] = entry["score"]
        return cache

    def get(self, text: str) -> float | None:
        key = (self.tag, text)
        return self._cache.get(key)

    def set(self, text: str, score: float) -> None:
        key = (self.tag, text)
        self._cache[key] = score
        self._append_cache(text, score)

    def _append_cache(self, text: str, score: float) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps({"tag": self.tag, "text": text, "score": score}, ensure_ascii=False) + "\n"
            )
