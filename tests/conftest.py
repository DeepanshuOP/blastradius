"""Isolates every test's request log from the real logs/requests.jsonl.

get_with_backoff() logs each request via `_log(entry, LOG_PATH)`, resolving
`LOG_PATH` as a plain module global at call time — nothing in ratelimit.py
or frame.py knows tests exist. Redirecting that global to a fresh tmp_path
file for the duration of every test, here, is what makes the real log
injectable without teaching the library code to special-case tests. This
covers both direct get_with_backoff() calls (test_ratelimit.py) and indirect
ones through frame.py's fetch functions (test_frame.py) with no changes to
either module's call sites.
"""

from unittest.mock import MagicMock

import pytest

import src.harvest.frame as frame
import src.harvest.ratelimit as ratelimit


@pytest.fixture(autouse=True)
def _isolate_request_log(tmp_path, monkeypatch):
    monkeypatch.setattr(ratelimit, "LOG_PATH", tmp_path / "requests.jsonl")


@pytest.fixture(autouse=True)
def no_real_sleep(monkeypatch):
    """Suite-wide guard against wall-clock sleeps (ROADMAP §41.2, <=3min SLO).

    Must cover every module that sleeps, named explicitly here so a new one
    doesn't slip through silently: `src.harvest.ratelimit` (acquire()'s
    exhaustion branch and get_with_backoff()'s retry backoff) and
    `src.harvest.frame` (TransientGovernor's pause ladder, via run_frame's
    injected default). Each resolves `time.sleep` as a plain module global
    at call time — never as a bound default parameter, which a monkeypatch
    like this one can't reach after import — so patching it here, once per
    module, covers every call site in it without teaching that module about
    tests. Patched via monkeypatch (not a bare assignment) so it unwinds
    automatically per test, and any test that also does
    `@patch("src.harvest.ratelimit.time.sleep")` layers its own Mock on top
    for the duration of the test body, then unwinds back to this recorder —
    the two do not conflict.

    The MagicMock() is returned so tests can request `no_real_sleep` as a
    fixture and assert on `.call_args_list` / durations it was asked to
    sleep for.
    """
    recorder = MagicMock()
    monkeypatch.setattr(ratelimit.time, "sleep", recorder)
    monkeypatch.setattr(frame.time, "sleep", recorder)
    return recorder
