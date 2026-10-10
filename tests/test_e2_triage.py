"""E2 triage: features strictly before the run, the two rules, and the metrics, on 12 hand-built pairs.

Five runs of one repo on branch `main`, one day apart (day 1..5). Failure events:

    r1: A "boom 1"      B "x"
    r2: A "boom 2"      C "y"
    r3: A "boom 3"      D "z"
    r4: B "x"           E "q"
    r5: A "boom 9"      F "boom 5"     E "q"      G "new unique"       <- the four pairs triaged

That is 12 (run, test) pairs. Digits are masked in message hashes, so every "boom N" is one message.
"""

import math

import numpy as np
import pandas as pd
import pytest

from analysis.rq3_triage import SMALL_SAMPLE_MIN, load_labels  # noqa: F401  (import must work offline)
from analysis.rq3_triage import metrics
from src.features.triage_features import RULE_BRANCH_N, TriageHistory, fclass_onehot, message_hash

DAY = 86400
T0 = 1_700_000_000
EVENTS = [
    (1, "A", "boom 1"), (1, "B", "x"), (2, "A", "boom 2"), (2, "C", "y"), (3, "A", "boom 3"), (3, "D", "z"),
    (4, "B", "x"), (4, "E", "q"), (5, "A", "boom 9"), (5, "F", "boom 5"), (5, "E", "q"), (5, "G", "new unique"),
]


def history() -> TriageHistory:
    ev = pd.DataFrame([{"repo": "r", "run_id": rid, "ts": T0 + rid * DAY, "test_id": t, "base_ref": "main",
                        "msg_hash": message_hash(m)} for rid, t, m in EVENTS])
    return TriageHistory(ev)


def test_message_hash_masks_numbers_and_ids() -> None:
    assert message_hash("boom 1") == message_hash("boom 22")
    assert message_hash("Failed at 0xDEADBEEF line 7") == message_hash("failed at 0x1234abcd line 9")
    assert message_hash("boom") != message_hash("bang")
    assert message_hash("") is None and message_hash(None) is None


def test_prior_failures_are_strictly_before() -> None:
    h = history()
    ts5 = T0 + 5 * DAY
    assert h.prior_failures("r", "A", ts5) == 3             # r1, r2, r3; r5's own event is not before itself
    assert h.prior_failures("r", "A", ts5, within_days=2) == 1   # [day 3, day 5): r3 only (day 4 has no A)
    assert h.prior_failures("r", "A", T0 + 3 * DAY) == 2   # r3's own event at exactly ts is excluded
    assert h.prior_failures("r", "G", ts5) == 0
    assert h.prior_failures("other", "A", ts5) == 0        # repos are separate


def test_rule_branch_previous_runs() -> None:
    h = history()
    ts5 = T0 + 5 * DAY
    assert RULE_BRANCH_N == 3
    assert h.failed_in_previous("r", "main", "A", ts5, 3) is True    # r2 and r3 are among the previous 3 (r4, r3, r2)
    assert h.failed_in_previous("r", "main", "E", ts5, 3) is True    # r4
    assert h.failed_in_previous("r", "main", "D", ts5, 1) is False   # only r4 is in the last 1 run
    assert h.failed_in_previous("r", "main", "D", ts5, 3) is True    # r3
    assert h.failed_in_previous("r", "main", "C", ts5, 2) is False   # r2 is 3 runs back
    assert h.failed_in_previous("r", "main", "G", ts5, 10) is False
    assert h.failed_in_previous("r", "dev", "A", ts5, 3) is False    # other branch


def test_rule_message_seen_before() -> None:
    h = history()
    ts5 = T0 + 5 * DAY
    assert h.message_seen("r", message_hash("boom 5"), ts5) is True     # "boom N" first seen at r1
    assert h.message_seen("r", message_hash("new unique"), ts5) is False
    assert h.message_seen("r", message_hash("boom 1"), T0 + 1 * DAY) is False  # first seen AT ts is not before
    assert h.message_seen("r", None, ts5) is False


def test_failure_class_onehot() -> None:
    f = fclass_onehot("java.net.ConnectException: Connection refused")
    assert f["fclass_environment"] == 1 and sum(f.values()) == 1
    assert fclass_onehot("AssertionError: expected 1")["fclass_code"] == 1
    assert fclass_onehot("")["fclass_unknown"] == 1


def test_metrics_hand_computed() -> None:
    # 8 pairs: truth not-mine = [1,1,1,0,0,0,0,0]; prediction not-mine = [1,1,0,1,0,0,0,0]
    # labels: inherited, flaky, inherited, mine x5
    label = np.array(["inherited", "flaky", "inherited"] + ["mine"] * 5)
    y = label != "mine"
    pred = np.array([1, 1, 0, 1, 0, 0, 0, 0], dtype=bool)
    m = metrics(y, pred, None, label)
    assert (m["p"], m["r"]) == (pytest.approx(2 / 3), pytest.approx(2 / 3))
    assert m["f1"] == pytest.approx(2 / 3)
    assert m["mine_p"] == pytest.approx(4 / 5)          # predicted mine: idx 2,4,5,6,7 -> 4 truly mine
    assert m["mine_r"] == pytest.approx(4 / 5)
    assert m["inherited_cleared"] == 1 and m["inherited_total"] == 2
    assert m["flaky_cleared"] == 1
    assert m["mine_wrongly_cleared"] == 1 and m["mine_total"] == 5   # the dangerous error
    assert math.isnan(m["pr_auc"])                                  # no score given


def test_metrics_with_scores_and_blame_all() -> None:
    label = np.array(["inherited", "mine", "mine", "flaky"])
    y = label != "mine"
    score = np.array([0.9, 0.2, 0.4, 0.8])
    m = metrics(y, score >= 0.5, score, label)
    assert m["roc_auc"] == 1.0 and m["pr_auc"] == 1.0
    blame_all = metrics(y, np.zeros(4, bool), None, label)
    assert blame_all["r"] == 0.0 and blame_all["mine_wrongly_cleared"] == 0 and blame_all["mine_r"] == 1.0
    assert math.isnan(blame_all["p"])
