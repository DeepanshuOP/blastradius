"""Corpus inclusion: a head run that executed no tests is excluded, not labelled.

Distinct from integrity invariant 6, which governs the BASE side. This is the
HEAD side: if the run under test never executed a test, there is nothing for a
fault-revealing label to be about.

The fixture is the real `agno-agi/agno` job log checked in under
`tests/fixtures/base_verify/` — conclusion `success`, one job, "Lint PR Title
and Body", which parses to NO_TEST_OUTPUT. Fixture values are ground truth.
"""

from pathlib import Path

import pandas as pd

from src.label.fault_revealing import compute_labels
from src.parse.dispatch import classify_dispatch_log

LOG = Path(__file__).parent / "fixtures" / "base_verify" / "agno-agi__agno__job97433407085__log.txt"

HEAD_RUN_ID = 97433407085
REPO = "agno-agi/agno"


def _frames(head_parsed_rows):
    """Build the four frames `compute_labels` takes, around one head run."""
    res = pd.DataFrame(
        [{"run_id": HEAD_RUN_ID, "repo": REPO, "status": "exact_green"}]
    )
    instances = pd.DataFrame(
        [
            {
                "run_id": HEAD_RUN_ID,
                "repo": REPO,
                "workflow_name": "Lint PR Title and Body",
                "workflow_id": 1,
                "head_sha": "0" * 40,
            }
        ]
    )
    head_parsed = pd.DataFrame(
        head_parsed_rows, columns=["run_id", "test_id"]
    ).astype({"run_id": "int64"})
    base_parsed = pd.DataFrame(columns=["run_id", "test_id"]).astype({"run_id": "int64"})
    return res, instances, head_parsed, base_parsed


def test_the_fixture_head_log_really_parses_to_no_test_output():
    """The zero below must be a measured zero, not a zero by construction."""
    classification, ids, _ = classify_dispatch_log(
        LOG.read_text(encoding="utf-8", errors="replace")
    )

    assert classification == "NO_TEST_OUTPUT"
    assert ids == set()


def test_head_with_no_tests_is_excluded_and_emits_zero_labels():
    res, instances, head_parsed, base_parsed = _frames([])

    outcomes, stats = compute_labels(res, instances, head_parsed, base_parsed)

    assert stats["head_no_tests_count"] == 1
    assert len(outcomes) == 0


def test_the_same_run_with_tests_is_included_and_emits_labels():
    """The counter must be seen to move, per docs/AGENT_RULES.md.

    Same resolution row, same instance: the ONLY difference is that the head
    parsed a test. If this did not produce a label, the zero above would be an
    artifact of the frame shape rather than of the inclusion rule.
    """
    res, instances, head_parsed, base_parsed = _frames(
        [(HEAD_RUN_ID, "com.example.FooTest#testBar")]
    )

    outcomes, stats = compute_labels(res, instances, head_parsed, base_parsed)

    assert stats["head_no_tests_count"] == 0
    assert len(outcomes) > 0
    assert set(outcomes["split"]) == {"all", "relaxed", "strict"}
