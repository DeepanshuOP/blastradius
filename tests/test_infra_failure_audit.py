"""`analysis/infra_failure_audit.py` label classification, on hand-built rows."""

from __future__ import annotations

import pandas as pd

from analysis.infra_failure_audit import classify_labels, instance_table


def frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    strict = pd.DataFrame(
        {"run_id": [1, 1, 2, 3, 4, 5], "test_id": ["a", "b", "c", "d", "e", "f"], "split": ["strict"] * 6}
    )
    parsed = pd.DataFrame(
        {
            "run_id": [1, 1, 1, 2, 3, 5],
            "test_id": ["a", "a", "b", "c", "d", "f"],
            "job_id": [10, 11, 10, 20, 30, 50],
            # a: one matrix leg timed out, the other asserted -> code wins
            # b: CUDA unavailable -> environment; c: nothing recorded; d: unmatched text; f: only a timeout
            "failure_message": ["TimeoutError", "AssertionError: x", "RuntimeError: No CUDA GPUs are available",
                                None, "something odd", "asyncio.exceptions.TimeoutError"],
        }
    )
    return strict, parsed


def test_per_label_rule_and_unknown_split() -> None:
    labels = classify_labels(*frames()).set_index("test_id")
    assert labels.loc["a", "cls"] == "code-level"
    assert labels.loc["b", "cls"] == "environment"
    assert labels.loc["b", "rule"] == "cuda-gpu-unavailable"
    assert labels.loc["c", "rule"] == "no message recorded"
    assert labels.loc["d", "rule"] == "message matched no pattern"
    # label e has no parsed row at all: no evidence, not dropped
    assert labels.loc["e", "cls"] == "unknown" and labels.loc["e", "rule"] == "no message recorded"
    assert labels.loc["f", "cls"] == "timeout"  # a timeout is not folded into environment
    assert len(labels) == 6


def test_instance_rates_are_n_over_d() -> None:
    rows = dict((m, v) for m, v in instance_table(classify_labels(*frames())))
    assert rows["instances with >= 1 environment-strict label"] == "1/5 (20.00%)"
    assert rows["instances whose labels are ALL environment-strict"] == "0/5 (0.00%)"
    assert rows["instances with >= 1 timeout label"] == "1/5 (20.00%)"
    assert rows["instances whose labels are ALL environment-strict or timeout"] == "1/5 (20.00%)"
    assert rows["instances with >= 1 code-level label"] == "1/5 (20.00%)"
    assert rows["instances whose labels are ALL unknown"] == "3/5 (60.00%)"
