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

from src.harvest.ratelimit import LOG_PATH, TokenPool, get_with_backoff

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
def test_acquire_sleeps_until_earliest_reset_when_all_exhausted(mock_sleep):
    pool = TokenPool(["tok_a", "tok_b"])
    now = time.time()
    pool.update(0, remaining=0, reset_at=now + 50)
    pool.update(1, remaining=0, reset_at=now + 30)

    idx, _headers = pool.acquire()

    assert idx == 1
    assert mock_sleep.call_count == 1
    (waited,) = mock_sleep.call_args.args
    assert 29.0 <= waited <= 30.0


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

    lines = Path(LOG_PATH).read_text(encoding="utf-8").strip().splitlines()
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
