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

import pytest

import src.harvest.ratelimit as ratelimit


@pytest.fixture(autouse=True)
def _isolate_request_log(tmp_path, monkeypatch):
    monkeypatch.setattr(ratelimit, "LOG_PATH", tmp_path / "requests.jsonl")
