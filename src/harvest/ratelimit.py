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
import sys
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

# One hour (GitHub's primary rate-limit window) plus slack for clock skew.
# A wait longer than this is more likely a malformed/stale X-RateLimit-Reset
# than a real 65-minute-away reset, so it gets clamped rather than honored —
# an early wake just re-403s and the existing retry loop handles that.
MAX_RESET_WAIT_SECONDS = 3900

# Used when a token has remaining <= 0 but no usable reset_at (never
# observed, or stale/in the past). We can't trust any specific duration in
# that case, so re-probe at the same cadence as ordinary retry backoff
# (BACKOFF_CAP_SECONDS) rather than blind-guessing up to an hour: the next
# real response supplies an authoritative reset_at, and acquire() will wait
# correctly from then on.
FALLBACK_RESET_WAIT_SECONDS = 60.0


@dataclass
class _TokenState:
    token: str
    remaining: int = DEFAULT_REMAINING
    reset_at: float = 0.0  # epoch seconds; 0.0 means never observed
    dead: bool = False
    dead_reason: str | None = None


class AllTokensDead(RuntimeError):
    """Every token in the pool has been evicted as permanently unusable;
    unlike quota exhaustion this can never recover within the process."""


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
        live = [i for i, s in enumerate(self._states) if not s.dead]
        if not live:
            raise AllTokensDead(
                "every token in the pool has been evicted as permanently unusable"
            )

        blocked = {i for i in live if self._states[i].remaining <= 0}

        if blocked and len(blocked) == len(live):

            def _raw_wait(idx: int) -> float:
                reset_at = self._states[idx].reset_at
                if reset_at > now:
                    return reset_at - now
                return FALLBACK_RESET_WAIT_SECONDS

            chosen = min(blocked, key=_raw_wait)
            raw_wait = _raw_wait(chosen)
            wait = min(raw_wait, MAX_RESET_WAIT_SECONDS)

            if raw_wait > MAX_RESET_WAIT_SECONDS:
                print(
                    f"[ratelimit] token_idx={chosen} computed wait "
                    f"{raw_wait:.1f}s exceeds MAX_RESET_WAIT_SECONDS="
                    f"{MAX_RESET_WAIT_SECONDS}s; clamping to {wait:.1f}s",
                    file=sys.stderr,
                )

            end_at = datetime.fromtimestamp(now + wait, tz=timezone.utc).isoformat()
            print(
                f"[ratelimit] token_idx={chosen} exhausted; sleeping "
                f"{wait:.1f}s until {end_at} (all tokens blocked)",
                file=sys.stderr,
            )
            sleep_start = time.monotonic()
            time.sleep(wait)
            elapsed = time.monotonic() - sleep_start
            print(
                f"[ratelimit] token_idx={chosen} woke after {elapsed:.1f}s "
                f"(expected {wait:.1f}s)",
                file=sys.stderr,
            )
            return chosen, self._headers_for(chosen)

        candidates = [i for i in live if i not in blocked]
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

    def evict(self, idx: int, reason: str) -> None:
        """Mark token `idx` permanently dead. Unlike quota exhaustion
        (remaining <= 0), a dead token is never reconsidered by acquire()
        for the rest of the process. Evicting an already-dead token is a
        no-op — no double log line, no error."""
        state = self._states[idx]
        if state.dead:
            return
        state.dead = True
        state.dead_reason = reason
        live_count = sum(1 for s in self._states if not s.dead)
        print(
            f"[ratelimit] {_now_iso()} token_idx={idx} evicted: {reason} "
            f"({live_count} token(s) still live)",
            file=sys.stderr,
        )

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



class TransferDeadlineExceeded(requests.exceptions.RequestException):
    pass
class ByteCeilingExceeded(requests.exceptions.RequestException):
    pass

TRANSFER_DEADLINE_SECONDS = 29704
BYTE_CEILING = 15 * 1024 * 1024

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
                url, params=params, headers=headers, timeout=TIMEOUT, stream=True
            )
            
            body = b""
            for chunk in response.iter_content(chunk_size=65536):
                body += chunk
                if len(body) > 15 * 1024 * 1024:
                    response.close()
                    raise ByteCeilingExceeded("Response exceeded 15 MB")
                if time.monotonic() - start > 29704:
                    response.close()
                    raise TransferDeadlineExceeded("Transfer took longer than 29704s")
            
            response._content = body
            response._content_consumed = True
            
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
            if isinstance(exc, requests.exceptions.InvalidHeader):
                pool.evict(token_idx, "malformed header")
                raise
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
            if status == 401:
                pool.evict(token_idx, "401 unauthorized")
            raise

    if last_exc is not None:
        raise last_exc
    raise RuntimeError("get_with_backoff exhausted attempts without a response")
