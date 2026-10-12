"""The lab's LLM cache: its own file (`eval/llm_cache/lab_<model>.jsonl`, written) plus read-only fallbacks.

The fallbacks are earlier recordings of the *same code path* (the PR bot's cache). A request is keyed by everything that
determines the answer, so a hit is the model's real earlier answer to this exact prompt, not an approximation. E3's
caches are never read or written here.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.agents.llm_cache import LLMCache, model_slug

CACHE_DIR = Path(__file__).resolve().parents[2] / "eval" / "llm_cache"


class LabCache(LLMCache):
    """`LLMCache` that also answers from read-only recordings; `put` only ever appends to its own file."""

    def __init__(self, path: Path, fallbacks: list[Path] | None = None) -> None:
        super().__init__(path)
        self.origin_of: dict[str, str] = {k: Path(path).name for k in self._records}
        for fb in fallbacks or []:
            if not fb.exists():
                continue
            for line in fb.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    if rec["key"] not in self._records:
                        self._records[rec["key"]] = rec
                        self.origin_of[rec["key"]] = fb.name

    def origin(self, key: str) -> str | None:
        """The file a recorded answer came from (None when not recorded)."""
        return self.origin_of.get(key)


def for_model(model: str) -> LabCache:
    """The cache of one model: `lab_<slug>.jsonl`, falling back to `bot_<slug>.jsonl` (read-only)."""
    slug = model_slug(model)
    return LabCache(CACHE_DIR / f"lab_{slug}.jsonl", [CACHE_DIR / f"bot_{slug}.jsonl"])
