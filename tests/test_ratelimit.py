"""Tests for src.harvest.ratelimit — TokenPool and get_with_backoff.

Uses `responses` to intercept requests at the transport layer; no test may
make a real network call. time.sleep is patched everywhere so the suite
stays fast and so backoff durations are assertable.
"""

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest
import requests
import responses

import src.harvest.ratelimit as ratelimit
from src.harvest.ratelimit import AllTokensDead, TokenPool, get_with_backoff

URL = "https://api.github.com/repos/x/y"


def test_acquire_selects_token_with_most_remaining_quota():
    pool = TokenPool(["tok_a", "tok_b", "tok_c"])
    future = time.time() + 3600
    pool.update(0, remaining=10, reset_at=future)
    pool.update(1, remaining=4000, reset_at=future)
    pool.update(2, remaining=500, reset_at=future)

    idx, headers = pool.acquire()

    assert idx == 1
    assert headers["Authorization"] == "token tok_b"


@patch("src.harvest.ratelimit.time.sleep")
def test_acquire_sleeps_until_earliest_reset_when_all_exhausted(mock_sleep, capsys):
    pool = TokenPool(["tok_a", "tok_b"])
    now = time.time()
    pool.update(0, remaining=0, reset_at=now + 50)
    pool.update(1, remaining=0, reset_at=now + 30)

    idx, _headers = pool.acquire()

    assert idx == 1
    assert mock_sleep.call_count == 1
    (waited,) = mock_sleep.call_args.args
    assert 29.0 <= waited <= 30.0

    err = capsys.readouterr().err
    lines = [line for line in err.splitlines() if line.strip()]
    assert len(lines) == 2
    assert "token_idx=1" in lines[0]
    assert "29." in lines[0] or "30." in lines[0]
    assert "token_idx=1" in lines[1]
    assert "woke after" in lines[1]


@patch("src.harvest.ratelimit.time.sleep")
def test_acquire_clamps_wait_exceeding_max_reset_wait(mock_sleep, capsys):
    pool = TokenPool(["tok_a"])
    now = time.time()
    pool.update(0, remaining=0, reset_at=now + 10_000)

    idx, _headers = pool.acquire()

    assert idx == 0
    assert mock_sleep.call_count == 1
    (waited,) = mock_sleep.call_args.args
    assert waited == ratelimit.MAX_RESET_WAIT_SECONDS

    err = capsys.readouterr().err
    lines = [line for line in err.splitlines() if line.strip()]
    assert any("clamping" in line and "10000.0" in line for line in lines)
    assert any(str(ratelimit.MAX_RESET_WAIT_SECONDS) in line for line in lines)


@patch("src.harvest.ratelimit.time.sleep")
def test_acquire_treats_zero_reset_at_as_blocked_not_handed_out_unslept(mock_sleep):
    pool = TokenPool(["tok_a"])
    pool.update(0, remaining=0, reset_at=None)  # reset_at stays default 0.0

    idx, _headers = pool.acquire()

    assert idx == 0
    assert mock_sleep.call_count == 1
    (waited,) = mock_sleep.call_args.args
    assert waited == ratelimit.FALLBACK_RESET_WAIT_SECONDS


@patch("src.harvest.ratelimit.time.sleep")
def test_acquire_sleep_writes_no_line_to_request_log(mock_sleep):
    pool = TokenPool(["tok_a"])
    now = time.time()
    pool.update(0, remaining=0, reset_at=now + 5)

    pool.acquire()

    assert not ratelimit.LOG_PATH.exists()


@responses.activate
@patch("src.harvest.ratelimit.time.sleep")
def test_primary_exhaustion_routes_to_other_token_and_succeeds(mock_sleep):
    """End-to-end coverage of the primary_exhausted branch: a 403 carrying
    X-RateLimit-Remaining: 0 must retry (not raise) and route to the pool's
    other token rather than re-blocking on the exhausted one."""
    responses.add(
        responses.GET,
        URL,
        status=403,
        headers={
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + 3600),
        },
        body='{"message": "API rate limit exceeded"}',
    )
    responses.add(
        responses.GET,
        URL,
        status=200,
        json={"ok": True},
        headers={"X-RateLimit-Remaining": "4999"},
    )

    pool = TokenPool(["tok_a", "tok_b"])
    resp = get_with_backoff(URL, pool=pool)

    assert resp.status_code == 200
    assert len(responses.calls) == 2
    mock_sleep.assert_not_called()


@responses.activate
@patch("src.harvest.ratelimit.time.sleep")
def test_retries_on_429_and_succeeds_on_attempt_3(mock_sleep):
    responses.add(responses.GET, URL, status=429, headers={"Retry-After": "1"})
    responses.add(responses.GET, URL, status=429, headers={"Retry-After": "1"})
    responses.add(
        responses.GET,
        URL,
        status=200,
        json={"ok": True},
        headers={"X-RateLimit-Remaining": "4999"},
    )

    pool = TokenPool(["tok_a"])
    resp = get_with_backoff(URL, pool=pool)

    assert resp.status_code == 200
    assert len(responses.calls) == 3
    assert mock_sleep.call_count == 2
    for call in mock_sleep.call_args_list:
        assert call.args[0] == 1.0


@responses.activate
@patch("src.harvest.ratelimit.time.sleep")
def test_raises_after_6_failed_attempts(mock_sleep):
    for _ in range(6):
        responses.add(responses.GET, URL, status=503)

    pool = TokenPool(["tok_a"])
    with pytest.raises(requests.HTTPError):
        get_with_backoff(URL, pool=pool)

    assert len(responses.calls) == 6


@responses.activate
@patch("src.harvest.ratelimit.time.sleep")
def test_connection_error_then_success_logs_null_status(mock_sleep):
    responses.add(responses.GET, URL, body=requests.exceptions.ConnectionError())
    responses.add(
        responses.GET,
        URL,
        status=200,
        json={"ok": True},
        headers={"X-RateLimit-Remaining": "4999"},
    )

    pool = TokenPool(["tok_a"])
    resp = get_with_backoff(URL, pool=pool)

    assert resp.status_code == 200
    assert len(responses.calls) == 2

    lines = Path(ratelimit.LOG_PATH).read_text(encoding="utf-8").strip().splitlines()
    last_two = [json.loads(line) for line in lines[-2:]]
    assert last_two[0]["status"] is None
    assert last_two[0]["error"] == "ConnectionError"
    assert last_two[1]["status"] == 200


@responses.activate
@patch("src.harvest.ratelimit.time.sleep")
def test_404_raises_immediately_after_exactly_one_request(mock_sleep):
    responses.add(responses.GET, URL, status=404)

    pool = TokenPool(["tok_a"])
    with pytest.raises(requests.HTTPError):
        get_with_backoff(URL, pool=pool)

    assert len(responses.calls) == 1
    mock_sleep.assert_not_called()


@responses.activate
@patch("src.harvest.ratelimit.time.sleep")
def test_log_destination_is_injectable_and_real_log_untouched(mock_sleep, tmp_path, monkeypatch):
    """Regression test for the log-injection fix (§8.2, §34.1 Rule 6):
    get_with_backoff must write to whatever LOG_PATH currently resolves to
    — here, redirected to a location distinct from both the real log and
    conftest's own autouse tmp_path — and must never fall back to the real
    logs/requests.jsonl once redirected."""
    responses.add(
        responses.GET,
        URL,
        status=200,
        json={"ok": True},
        headers={"X-RateLimit-Remaining": "4999"},
    )
    custom_log = tmp_path / "custom" / "requests.jsonl"
    monkeypatch.setattr(ratelimit, "LOG_PATH", custom_log)
    real_log = Path("logs/requests.jsonl")
    real_log_before = real_log.read_bytes() if real_log.exists() else None

    pool = TokenPool(["tok_a"])
    get_with_backoff(URL, pool=pool)

    assert custom_log.exists()
    entry = json.loads(custom_log.read_text(encoding="utf-8").strip())
    assert entry["status"] == 200

    real_log_after = real_log.read_bytes() if real_log.exists() else None
    assert real_log_after == real_log_before


@responses.activate
@patch("src.harvest.ratelimit.time.sleep")
def test_unhandled_request_exception_subclass_still_logs(mock_sleep, tmp_path, monkeypatch):
    """Regression for the dead-token cascade: any requests.RequestException,
    not just ConnectionError/Timeout, must produce a log line before
    retrying or raising — a narrower except clause is exactly what let 10
    of 20 failures in that run vanish with zero trace."""
    custom_log = tmp_path / "requests.jsonl"
    monkeypatch.setattr(ratelimit, "LOG_PATH", custom_log)
    responses.add(responses.GET, URL, body=requests.exceptions.ChunkedEncodingError("boom"))
    responses.add(
        responses.GET,
        URL,
        status=200,
        json={"ok": True},
        headers={"X-RateLimit-Remaining": "4999"},
    )

    pool = TokenPool(["tok_a"])
    resp = get_with_backoff(URL, pool=pool)

    assert resp.status_code == 200
    lines = custom_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["status"] is None
    assert first["error"] == "ChunkedEncodingError"


@responses.activate
@patch("src.harvest.ratelimit.time.sleep")
def test_403_with_retry_after_logs_retry_after_and_body_snippet(mock_sleep, tmp_path, monkeypatch):
    """§6's rate-limit detector needs Retry-After and response body text in
    the log to ever detect secondary limiting — previously neither field
    was recorded at all, so grepping for evidence always found nothing."""
    custom_log = tmp_path / "requests.jsonl"
    monkeypatch.setattr(ratelimit, "LOG_PATH", custom_log)
    for _ in range(6):
        responses.add(
            responses.GET,
            URL,
            status=403,
            headers={"Retry-After": "30"},
            body='{"message": "secondary rate limit"}',
        )

    pool = TokenPool(["tok_a"])
    with pytest.raises(requests.HTTPError):
        get_with_backoff(URL, pool=pool)

    lines = [json.loads(line) for line in custom_log.read_text(encoding="utf-8").strip().splitlines()]
    assert lines[0]["retry_after"] == "30"
    assert "secondary rate limit" in lines[0]["body_snippet"]


def test_evicted_token_never_selected_across_many_acquires():
    pool = TokenPool(["tok_a", "tok_b", "tok_c"])
    pool.evict(1, "401 unauthorized")

    seen = {pool.acquire()[0] for _ in range(20)}

    assert 1 not in seen
    assert seen == {0, 2}


@patch("src.harvest.ratelimit.time.sleep")
def test_all_tokens_dead_raises_without_sleeping(mock_sleep):
    pool = TokenPool(["tok_a", "tok_b", "tok_c"])
    pool.evict(0, "401 unauthorized")
    pool.evict(1, "401 unauthorized")
    pool.evict(2, "401 unauthorized")

    with pytest.raises(ratelimit.AllTokensDead):
        pool.acquire()

    mock_sleep.assert_not_called()


@patch("src.harvest.ratelimit.time.sleep")
def test_dead_token_excluded_while_live_but_exhausted_token_still_used(mock_sleep):
    pool = TokenPool(["tok_a", "tok_b"])
    pool.evict(0, "401 unauthorized")
    now = time.time()
    pool.update(1, remaining=0, reset_at=now + 30)

    idx, _headers = pool.acquire()

    assert idx == 1
    assert mock_sleep.call_count == 1


def test_evict_same_index_twice_logs_once_and_does_not_raise(capsys):
    pool = TokenPool(["tok_a"])
    pool.evict(0, "401 unauthorized")
    pool.evict(0, "401 unauthorized")

    err = capsys.readouterr().err
    lines = [line for line in err.splitlines() if line.strip()]
    assert len(lines) == 1
    assert "token_idx=0" in lines[0]
    assert "401 unauthorized" in lines[0]
    assert "tok_a" not in err
