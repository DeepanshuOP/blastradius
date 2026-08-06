"""GitHub API rate-limit governor.

get_with_backoff() is the sole HTTP entry point for the codebase (T0.2b,
ROADMAP §8.2). TokenPool tracks per-token remaining quota read from
X-RateLimit-Remaining / X-RateLimit-Reset and hands out pre-built request
headers — token values never leave the pool.
"""

from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests

DEFAULT_ENV_KEYS: tuple[str, ...] = ("GITHUB_PAT_1", "GITHUB_PAT_2", "GITHUB_PAT_3")
DEFAULT_REMAINING = 5000
MAX_ATTEMPTS = 6
BACKOFF_BASE_SECONDS = 1.0
BACKOFF_CAP_SECONDS = 60.0
TIMEOUT = (5, 30)  # (connect, read) seconds
LOG_PATH = Path("logs/requests.jsonl")
RETRYABLE_STATUSES = (429, 500, 502, 503, 504)


@dataclass
class _TokenState:
    token: str
    remaining: int = DEFAULT_REMAINING
    reset_at: float = 0.0  # epoch seconds; 0.0 means never observed


class TokenPool:
    """Quota-aware round-robin pool over one or more GitHub PATs.

    Tokens are supplied once at construction and never exposed again:
    acquire() returns an index and pre-built headers, not the token string.
    """

    def __init__(self, tokens: list[str]) -> None:
        if not tokens:
            raise ValueError("TokenPool requires at least one token")
        self._tokens = list(tokens)
        self._states = [_TokenState(token=t) for t in tokens]
        self._rr_cursor = 0

    @classmethod
    def from_env(cls, key_names: tuple[str, ...] = DEFAULT_ENV_KEYS) -> "TokenPool":
        tokens = [os.environ[k] for k in key_names if os.environ.get(k)]
        if not tokens:
            raise ValueError(f"no GitHub PAT found in environment among {key_names}")
        return cls(tokens)

    def __len__(self) -> int:
        return len(self._states)

    def acquire(self) -> tuple[int, dict[str, str]]:
        now = time.time()
        blocked = {
            i
            for i, s in enumerate(self._states)
            if s.remaining <= 0 and s.reset_at > now
        }

        if blocked and len(blocked) == len(self._states):
            earliest_idx = min(blocked, key=lambda i: self._states[i].reset_at)
            wait = max(0.0, self._states[earliest_idx].reset_at - now)
            time.sleep(wait)
            return earliest_idx, self._headers_for(earliest_idx)

        candidates = [i for i in range(len(self._states)) if i not in blocked]
        max_remaining = max(self._states[i].remaining for i in candidates)
        tied = [i for i in candidates if self._states[i].remaining == max_remaining]

        chosen = tied[0]
        for i in range(len(self._states)):
            idx = (self._rr_cursor + i) % len(self._states)
            if idx in tied:
                chosen = idx
                break
        self._rr_cursor = (chosen + 1) % len(self._states)

        return chosen, self._headers_for(chosen)

    def update(
        self, token_idx: int, *, remaining: int | None, reset_at: float | None
    ) -> None:
        state = self._states[token_idx]
        if remaining is not None:
            state.remaining = remaining
        if reset_at is not None:
            state.reset_at = reset_at

    def _headers_for(self, idx: int) -> dict[str, str]:
        return {
            "Authorization": f"token {self._tokens[idx]}",
            "Accept": "application/vnd.github+json",
        }


def _backoff_delay(attempt: int) -> float:
    ceiling = min(BACKOFF_CAP_SECONDS, BACKOFF_BASE_SECONDS * (2 ** (attempt - 1)))
    return random.uniform(0, ceiling)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(entry: dict, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def get_with_backoff(
    url: str,
    params: dict | None = None,
    *,
    pool: TokenPool,
    max_attempts: int = MAX_ATTEMPTS,
) -> requests.Response:
    """The sole HTTP entry point in the codebase. See module docstring."""
    last_exc: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        token_idx, headers = pool.acquire()
        start = time.monotonic()

        try:
            response = requests.get(
                url, params=params, headers=headers, timeout=TIMEOUT
            )
        except requests.exceptions.RequestException as exc:
            # Broadened from (ConnectionError, Timeout): any RequestException
            # raised by requests.get() itself — InvalidHeader, a broken
            # credential's malformed Authorization value, whatever — must
            # still produce a log line before retrying or raising. A narrower
            # except clause here is exactly what let 10 of 20 failures in the
            # dead-token cascade vanish with zero trace (§8.2, §34.1 Rule 6).
            exc.token_idx = token_idx
            duration_ms = (time.monotonic() - start) * 1000
            _log(
                {
                    "ts": _now_iso(),
                    "url": url,
                    "status": None,
                    "token_idx": token_idx,
                    "remaining": None,
                    "duration_ms": duration_ms,
                    "attempt": attempt,
                    "error": type(exc).__name__,
                },
                LOG_PATH,
            )
            last_exc = exc
            if attempt == max_attempts:
                raise
            time.sleep(_backoff_delay(attempt))
            continue

        duration_ms = (time.monotonic() - start) * 1000
        remaining_hdr = response.headers.get("X-RateLimit-Remaining")
        remaining = int(remaining_hdr) if remaining_hdr is not None else None
        reset_hdr = response.headers.get("X-RateLimit-Reset")
        reset_at = float(reset_hdr) if reset_hdr is not None else None
        if remaining is not None or reset_at is not None:
            pool.update(token_idx, remaining=remaining, reset_at=reset_at)

        log_entry = {
            "ts": _now_iso(),
            "url": url,
            "status": response.status_code,
            "token_idx": token_idx,
            "remaining": remaining,
            "duration_ms": duration_ms,
            "attempt": attempt,
        }
        retry_after = response.headers.get("Retry-After")
        if not response.ok:
            # §6's rate-limit-exhaustion detector needs this to exist at
            # all: previously _log() recorded neither Retry-After nor any
            # response body text, so grepping the log for secondary-limit
            # evidence always returned nothing regardless of whether it
            # happened. body_snippet is response.text only — server-supplied
            # inbound content — never response.request.headers or the pool,
            # so no token value can appear in it.
            log_entry["retry_after"] = retry_after
            log_entry["body_snippet"] = response.text[:200] if response.text else None
        _log(log_entry, LOG_PATH)

        if response.ok:
            return response

        status = response.status_code
        secondary_limited = status in (403, 429) and (
            retry_after is not None
            or "secondary rate limit" in response.text.lower()
        )
        primary_exhausted = (
            status in (403, 429) and not secondary_limited and remaining == 0
        )

        if attempt == max_attempts:
            try:
                response.raise_for_status()
            except requests.HTTPError as http_exc:
                http_exc.token_idx = token_idx
                raise

        if primary_exhausted:
            # pool.update() above already recorded remaining=0 for this
            # token; the next acquire() routes to a different one.
            continue

        if secondary_limited:
            wait = float(retry_after) if retry_after is not None else _backoff_delay(
                attempt
            )
            time.sleep(wait)
            continue

        if status in RETRYABLE_STATUSES:
            time.sleep(_backoff_delay(attempt))
            continue

        # Non-retryable 4xx (401, 404, 422, plain 403, ...) — do not burn
        # attempts on a request that will never succeed.
        try:
            response.raise_for_status()
        except requests.HTTPError as http_exc:
            http_exc.token_idx = token_idx
            raise

    if last_exc is not None:
        raise last_exc
    raise RuntimeError("get_with_backoff exhausted attempts without a response")
