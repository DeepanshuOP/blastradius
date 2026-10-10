"""Request/response cache for LLM calls (D-58): every call is replayable offline.

One JSONL file per model (`eval/llm_cache/e3_<model-slug>.jsonl` for E3,
`src/agents/demo/llm_cache.jsonl` for the demo). A record is keyed by the sha256
of everything that determines the answer: provider, model, system prompt,
messages and the sampling parameters. Credentials are never part of a record.

`BR_LLM_REPLAY=1` (or `replay=True`) makes a miss an error instead of a network
call, so `make repair-eval` can prove it is offline.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


class CacheMiss(RuntimeError):
    """Replay mode asked for a request that was never recorded."""


def model_slug(model: str) -> str:
    """Filesystem-safe model name (`openai/gpt-oss-120b` -> `openai_gpt-oss-120b`)."""
    return "".join(c if c.isalnum() or c in "-._" else "_" for c in model)


def cache_key(provider: str, model: str, system: str, messages: list[dict], params: dict) -> str:
    """sha256 over the canonical JSON of the request."""
    payload = {"provider": provider, "model": model, "system": system, "messages": messages, "params": params}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


@dataclass
class LLMCache:
    """Append-only JSONL cache.

    Attributes:
        path: The cache file.
        replay: A miss raises :class:`CacheMiss` instead of returning None.
    """

    path: Path
    replay: bool = False

    def __post_init__(self) -> None:
        self.path = Path(self.path)
        self.replay = self.replay or os.environ.get("BR_LLM_REPLAY") == "1"
        self._records: dict[str, dict] = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    self._records[rec["key"]] = rec

    def __len__(self) -> int:
        return len(self._records)

    def __contains__(self, key: str) -> bool:
        """True when `key` is recorded. Never raises (unlike :meth:`get` in replay mode)."""
        return key in self._records

    def user_messages(self) -> list[str]:
        """The user message of every record (used to find recorded retries of a prompt)."""
        out = []
        for r in self._records.values():
            msgs = (r.get("request") or {}).get("messages") or []
            if msgs:
                out.append(msgs[0].get("content", ""))
        return out

    def get(self, key: str) -> dict | None:
        """The stored record, or None; raises in replay mode on a miss."""
        rec = self._records.get(key)
        if rec is None and self.replay:
            raise CacheMiss(f"no cached response for {key[:12]} in {self.path} (replay mode)")
        return rec

    def put(self, key: str, request: dict, response_text: str, usage: dict | None, model: str,
            provider_id: str | None = None, latency_s: float | None = None) -> dict:
        """Append one record (never overwrites an existing key)."""
        if key in self._records:
            return self._records[key]
        rec = {"key": key, "request": request, "response_text": response_text, "usage": usage, "model": model,
               "provider_id": provider_id, "latency_s": latency_s,
               "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
        self._records[key] = rec
        return rec
