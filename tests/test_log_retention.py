"""The retention probe's MIXED counter must be reachable.

`analysis/verify_exact_green.probe_retention` reports "0 MIXED", and that zero
is what licenses the probe-then-infer optimisation. Per the zero-is-not-evidence
rule in `docs/AGENT_RULES.md`, a zero proves nothing until the counter has been
seen to increment — so these tests drive the classifier to every one of its
outcomes, MIXED included.

No data or network needed; runs on a fresh clone.
"""

import pytest

from analysis.verify_exact_green import classify_retention


def test_a_run_with_no_expired_log_does_not_qualify():
    assert classify_retention([200, 200, 404]) is None


def test_every_job_expired_is_all_410():
    assert classify_retention([410, 410, 410]) == "all_410"


def test_expired_plus_404_is_still_unreadable_not_mixed():
    """404 is the separate undiagnosed defect, not a surviving log."""
    assert classify_retention([410, 404, 410]) == "expired_404"


@pytest.mark.parametrize(
    "statuses",
    [
        [410, 200],
        [200, 410],
        [410, 404, 200, 410],
    ],
)
def test_a_readable_log_beside_an_expired_one_is_MIXED(statuses):
    """THE counter that must be able to increment.

    If this ever fires against real data, one probe cannot speak for a whole
    run and the probe-then-infer optimisation is unsound.
    """
    assert classify_retention(statuses) == "MIXED"


def test_single_job_run_expired():
    assert classify_retention([410]) == "all_410"
