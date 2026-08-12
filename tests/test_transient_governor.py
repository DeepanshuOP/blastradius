"""Tests for src.harvest.frame.TransientGovernor.

Uses `responses` to intercept the GET /rate_limit probe at the transport
layer, same convention as test_ratelimit.py and test_frame.py. Both
time.monotonic and time.sleep are injected (never patched at the module
level) so no test performs a real sleep.
"""

from unittest.mock import Mock

import pytest
import responses

from src.harvest.frame import AbortRun, PROBE_URL, TransientGovernor
from src.harvest.ratelimit import TokenPool


def _governor(pool, sleep):
    return TransientGovernor(pool, sleep=sleep, monotonic=lambda: 0.0)


@responses.activate
def test_probe_success_resumes_and_resets_counter():
    responses.add(
        responses.GET,
        PROBE_URL,
        json={"resources": {"core": {"remaining": 5000}}},
        status=200,
    )
    pool = TokenPool(["tok_a", "tok_b"])
    sleep = Mock()
    governor = _governor(pool, sleep)

    for _ in range(5):
        governor.record_transient(status=503, token_idx=0)

    sleep.assert_called_once_with(60.0)

    # Counter reset to 0 by the successful probe: four more transients
    # alone must not re-trigger the ladder.
    for _ in range(4):
        governor.record_transient(status=503, token_idx=0)
    sleep.assert_called_once_with(60.0)


@responses.activate
def test_probe_fails_every_rung_aborts_with_full_ladder_sum():
    responses.add(responses.GET, PROBE_URL, status=503)
    pool = TokenPool(["tok_a", "tok_b"])
    sleep = Mock()
    governor = _governor(pool, sleep)

    with pytest.raises(AbortRun):
        for _ in range(5):
            governor.record_transient(status=503, token_idx=0)

    total_slept = sum(call.args[0] for call in sleep.call_args_list)
    assert total_slept == 1260.0


@responses.activate
def test_interleaved_transients_never_five_in_a_row_never_pauses():
    pool = TokenPool(["tok_a", "tok_b"])
    sleep = Mock()
    governor = _governor(pool, sleep)

    for _ in range(10):
        for _ in range(4):
            governor.record_transient(status=503, token_idx=0)
        governor.record_success()

    sleep.assert_not_called()


@responses.activate
def test_flapping_recovery_without_reset_escalates_and_eventually_aborts():
    responses.add(
        responses.GET,
        PROBE_URL,
        json={"resources": {"core": {"remaining": 5000}}},
        status=200,
    )
    pool = TokenPool(["tok_a", "tok_b"])
    sleep = Mock()
    governor = _governor(pool, sleep)

    with pytest.raises(AbortRun):
        for _entry in range(4):
            for _ in range(5):
                governor.record_transient(status=503, token_idx=0)

    slept = [call.args[0] for call in sleep.call_args_list]
    assert slept == [60.0, 300.0, 900.0]


@responses.activate
def test_recovery_after_three_consecutive_successes_resets_sticky_rung():
    responses.add(
        responses.GET,
        PROBE_URL,
        json={"resources": {"core": {"remaining": 5000}}},
        status=200,
    )
    pool = TokenPool(["tok_a", "tok_b"])
    sleep = Mock()
    governor = _governor(pool, sleep)

    for _ in range(5):
        governor.record_transient(status=503, token_idx=0)
    sleep.assert_called_once_with(60.0)

    governor.record_success()
    governor.record_success()
    governor.record_success()  # 3rd consecutive success resets rung_index

    for _ in range(5):
        governor.record_transient(status=503, token_idx=0)

    assert sleep.call_args_list[-1].args[0] == 60.0
