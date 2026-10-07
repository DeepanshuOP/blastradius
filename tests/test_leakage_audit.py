"""The leakage audit catches injected leaks and passes clean evidence (real git repo, hand counts)."""

from __future__ import annotations

import pandas as pd

from analysis import leakage_audit
from analysis.cochange_trailing import RepoHistory
from analysis.leakage_audit import audit_cochange, audit_historical
from tests.test_cochange_trailing import DAY, T0
from tests.test_rq1_divergence import REPO, make_data, trailing_data


def test_clean_historical_evidence_has_no_violations() -> None:
    c = audit_historical(make_data(), "strict")
    assert c["audited"] == 1 and c["with_evidence"] == 1
    assert (c["not_before"], c["own_run"], c["non_strict"], c["duplicated"]) == (0, 0, 0, 0)
    assert (c["rows"], c["distinct_labels"]) == (3, 3)


def test_injected_historical_leaks_are_each_counted() -> None:
    data = make_data()
    leaks = pd.DataFrame({
        "repo": [REPO] * 3, "run_id": [1, 95, 90], "test_id": ["t::a", "t::q", "t::a"],
        "split": ["strict", "relaxed", "strict"],
        "run_started_at": ["2026-02-01", "2026-03-01", "2026-01-01"],
        "resolved_path": ["tests/test_a.py"] * 3})
    data.hist_all = pd.concat([data.hist_all, leaks], ignore_index=True)
    # give every row an earlier start so the time filter keeps them; the audit must still see the own run
    data.hist_all["run_started_at"] = "2026-01-01"
    c = audit_historical(data, "strict")
    assert c["own_run"] == 1          # ...but run 1 is the instance's own run
    assert c["non_strict"] == 1       # run 95's relaxed row
    assert c["duplicated"] == 1       # (90, t::a) twice
    assert c["not_before"] == 0


def test_evidence_from_a_later_run_is_flagged_when_the_filter_is_bypassed(monkeypatch) -> None:
    data = make_data()
    later = data.hist_all.iloc[[0]].assign(run_id=99, run_started_at="2026-03-01")
    frame = pd.concat([data.hist_all, later], ignore_index=True)
    monkeypatch.setattr(leakage_audit, "historical_evidence", lambda d, repo, row, hist="strict": frame)
    assert audit_historical(data, "strict")["not_before"] == 1


def test_trailing_cochange_evidence_is_clean_and_the_static_table_is_exposed(tmp_path, monkeypatch) -> None:
    data, sha = trailing_data(tmp_path)
    (tmp_path / "repo").rename(tmp_path / "acme__widgets")
    monkeypatch.setattr(leakage_audit, "CLONES_DIR", tmp_path)
    cur, leg = audit_cochange(data, as_of_ts=T0 + 30 * DAY)
    assert (cur["audited"], cur["with_evidence"]) == (1, 1)
    assert (cur["not_before"], cur["own_head"], cur["not_in_git"], cur["outside_window"]) == (0, 0, 0, 0)
    assert cur["commits"] == 4  # d1, d2, d2c, d3 touch A before day 4
    assert (leg["exposed"], leg["future_commit"]) == (1, 1)  # the day-10 commit lies in [run, as_of] and touches A


def test_a_commit_after_the_run_is_caught_even_if_the_history_returns_it(tmp_path, monkeypatch) -> None:
    data, sha = trailing_data(tmp_path)
    (tmp_path / "repo").rename(tmp_path / "acme__widgets")
    monkeypatch.setattr(leakage_audit, "CLONES_DIR", tmp_path)
    h = data.history[REPO]
    monkeypatch.setattr(RepoHistory, "commits_touching",
                        lambda self, path, cutoff_ts, exclude_sha=None: [c for c in self.commits if path in c.files])
    cur, _ = audit_cochange(data, as_of_ts=T0 + 30 * DAY)
    assert cur["not_before"] == 1 and cur["own_head"] == 1  # d10 is after the run AND is the instance's head
