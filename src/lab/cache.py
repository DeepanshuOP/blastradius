"""The lab's LLM cache: its own file (`eval/llm_cache/lab_<model>.jsonl`, written) plus read-only fallbacks.

The fallbacks are earlier recordings of the *same code path* (the PR bot's cache). A request is keyed by everything that
determines the answer, so a hit is the model's real earlier answer to this exact prompt, not an approximation. E3's
caches are never read or written here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src.agents.llm import GroqLLM
from src.agents.llm_cache import LLMCache, model_slug

CACHE_DIR = Path(__file__).resolve().parents[2] / "eval" / "llm_cache"
#: The lab's own token ledger. E3's ledger (`usage.jsonl`) is never written by the lab.
LAB_LEDGER = CACHE_DIR / "lab_usage.jsonl"
#: Ledgers whose rows count against the shared Groq daily quota.
QUOTA_LEDGERS = (CACHE_DIR / "usage.jsonl", LAB_LEDGER)


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


def day_tokens(model: str, now: float, ledgers: tuple[Path, ...] = QUOTA_LEDGERS) -> tuple[int, float | None]:
    """Tokens of `model` in the rolling 24 h before `now`, summed over `ledgers`, and when the oldest of them expires.

    Returns:
        `(tokens, oldest timestamp)`; `oldest` is None when there are none.
    """
    cut = now - 86400
    total, oldest = 0, None
    for path in ledgers:
        if not Path(path).exists():
            continue
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            t = datetime.fromisoformat(r["timestamp"]).timestamp()
            if r.get("model") == model and t >= cut:
                total += int(r["tokens"])
                oldest = t if oldest is None else min(oldest, t)
    return total, oldest


@dataclass
class LabGroqLLM(GroqLLM):
    """`GroqLLM` that writes the lab ledger and checks the daily cap against E3's ledger and the lab's together."""

    ledger: Path = LAB_LEDGER
    quota_ledgers: tuple[Path, ...] = field(default=QUOTA_LEDGERS)

    def _day_total(self) -> tuple[int, float | None]:
        return day_tokens(self.model, self.clock(), self.quota_ledgers)
