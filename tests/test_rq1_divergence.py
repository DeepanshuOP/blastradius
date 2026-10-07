"""RQ1 evaluation on a tiny hand-built instance with hand-computed expectations."""

from __future__ import annotations

import pandas as pd

from analysis.cochange_trailing import RepoHistory, read_history
from analysis.rq1_divergence import Rq1Data, evaluate_k, ground_truth, historical_evidence, summarize
from tests.test_cochange_trailing import DAY, T0, make_repo

REPO = "acme/widgets"


def make_data() -> Rq1Data:
    strict = pd.DataFrame(
        {"run_id": [1, 1], "test_id": ["t::a", "t::env"], "split": ["strict", "strict"],
         "repo": [REPO, REPO], "pr_number": [7, 7], "run_started_at": ["2026-02-01", "2026-02-01"]}
    )
    hist = pd.DataFrame(
        {"repo": [REPO] * 3, "run_id": [90, 91, 92], "test_id": ["t::a", "t::a2", "t::z"],
         "split": ["strict"] * 3, "run_started_at": ["2026-01-01"] * 3,
         "resolved_path": ["tests/test_a.py", "tests/test_a.py", "tests/test_z.py"]}
    )
    return Rq1Data(
        strict_labels=strict,
        bound={(REPO, "t::a"): "tests/test_a.py", (REPO, "t::env"): "tests/test_env.py"},
        pr_to_changed={(REPO, "7"): {"src/A.py"}},
        co_support_map={},
        co_lookup={REPO: {"src/A.py": ["src/B.py", "tests/test_a.py", "docs/x.md"]}},
        hist_all=hist,
        language_of={1: "Python"},
        n_strict_instances=1,
        valid_runs=strict.drop_duplicates("run_id"),
        hist_legacy=pd.concat([hist.assign(split="all"), hist.assign(split="relaxed"), hist]),
    )


def test_all_partner_and_test_restricted_scores_at_k2() -> None:
    data = make_data()
    gt = ground_truth(data)
    assert gt == {(REPO, 1): {"tests/test_a.py", "tests/test_env.py"}}
    df = evaluate_k(data, gt, 2, cochange="static")
    r = df.iloc[0]
    # all partners, k=2: {src/B.py, tests/test_a.py}: 1 hit of 2 predicted, of 2 actual
    assert (r["co_hit"], r["co_size"]) == (1, 2)
    assert (r["co_p"], r["co_r"], r["co_j"]) == (0.5, 0.5, 1 / 3)
    # restricted to test files BEFORE the cut: {tests/test_a.py}
    assert (r["co_test_hit"], r["co_test_size"]) == (1, 1)
    assert (r["co_test_p"], r["co_test_r"]) == (1.0, 0.5)
    # changeset {src/A.py} hits nothing; history top-2 = {test_a, test_z}: 1 hit
    assert r["b1_hit"] == 0 and r["b2_hit"] == 1 and r["b2_size"] == 2
    assert r["language"] == "Python"


def test_excluding_a_label_changes_ground_truth_and_can_drop_the_instance() -> None:
    data = make_data()
    gt = ground_truth(data, exclude={(1, "t::env")})
    assert gt == {(REPO, 1): {"tests/test_a.py"}}
    assert evaluate_k(data, gt, 2, cochange="static").iloc[0]["co_r"] == 1.0
    assert ground_truth(data, exclude={(1, "t::env"), (1, "t::a")}) == {}
    assert evaluate_k(data, {}, 2, cochange="static").empty


def test_summarize_reports_every_method_with_n_over_d_micro_rates() -> None:
    rows = summarize(evaluate_k(make_data(), ground_truth(make_data()), 2, cochange="static"))
    assert [r[0] for r in rows] == [
        "co-change, all partner files", "co-change, restricted to test files",
        "changeset baseline", "historical-frequency baseline",
    ]
    assert rows[0][5] == "1/2 (50.00%)" and rows[0][6] == "1/2 (50.00%)"


def test_historical_baseline_counts_each_test_instance_failure_once() -> None:
    """test_a.py has two strict failures in earlier instances -> frequency 2; the legacy read triples them."""
    data = make_data()
    row = data.valid_runs.iloc[0]
    strict = historical_evidence(data, REPO, row, "strict")
    assert len(strict) == 3 and not strict.duplicated(["run_id", "test_id"]).any()
    assert strict["resolved_path"].value_counts().to_dict() == {"tests/test_a.py": 2, "tests/test_z.py": 1}
    legacy = historical_evidence(data, REPO, row, "legacy")
    assert len(legacy) == 9 and legacy["resolved_path"].value_counts()["tests/test_a.py"] == 6


def test_historical_evidence_excludes_runs_starting_at_or_after_the_instance() -> None:
    data = make_data()
    late = pd.DataFrame({"repo": [REPO] * 2, "run_id": [1, 95], "test_id": ["t::a", "t::q"], "split": ["strict"] * 2,
                         "run_started_at": ["2026-02-01", "2026-03-01"],
                         "resolved_path": ["tests/test_a.py", "tests/test_q.py"]})
    data.hist_all = pd.concat([data.hist_all, late], ignore_index=True)
    ev = historical_evidence(data, REPO, data.valid_runs.iloc[0], "strict")
    assert set(ev["run_id"]) == {90, 91, 92}  # not the instance's own run 1, not the later run 95


def trailing_data(tmp_path) -> tuple[Rq1Data, dict]:
    """The instance changes src/A.py (started day 4). B co-changed with A before it, C only after."""
    repo_dir, sha = make_repo(tmp_path)
    started = pd.Timestamp(T0 + 4 * DAY, unit="s", tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    strict = pd.DataFrame({"run_id": [1], "test_id": ["t::b"], "split": ["strict"], "repo": [REPO],
                           "pr_number": [7], "run_started_at": [started]})
    hist = RepoHistory(read_history(repo_dir, "HEAD", T0, T0 + 30 * DAY))
    data = Rq1Data(
        strict_labels=strict, bound={(REPO, "t::b"): "src/B.py"}, pr_to_changed={(REPO, "7"): {"src/A.py"}},
        co_support_map={}, co_lookup={REPO: {"src/A.py": ["src/B.py", "src/C.py"]}},
        hist_all=pd.DataFrame(columns=["repo", "run_id", "test_id", "split", "run_started_at", "resolved_path"]),
        language_of={1: "Java"}, n_strict_instances=1, valid_runs=strict, history={REPO: hist},
        head_sha_of={1: sha["d10"]},
    )
    return data, sha


def test_trailing_mode_ignores_commits_after_the_run_and_the_static_table_does_not(tmp_path) -> None:
    data, _ = trailing_data(tmp_path)
    gt = ground_truth(data)
    trailing = evaluate_k(data, gt, 5, cochange="trailing").iloc[0]
    static = evaluate_k(data, gt, 5, cochange="static").iloc[0]
    assert (trailing["co_size"], trailing["co_hit"]) == (1, 1)  # only B (support 3 before day 4; C has 1)
    assert (static["co_size"], static["co_hit"]) == (2, 1)      # the static table also offers C


def test_trailing_mode_does_not_use_the_instances_own_head_commit(tmp_path) -> None:
    data, sha = trailing_data(tmp_path)
    data.head_sha_of = {1: sha["d3"]}  # pretend the instance's head is the day-3 commit
    [row] = [evaluate_k(data, ground_truth(data), 5, cochange="trailing").iloc[0]]
    # with d3 excluded B has support 2 of A's 3 remaining commits: still a partner, still one hit
    assert (row["co_size"], row["co_hit"]) == (1, 1)
    data.cache.clear()
    data.history[REPO] = RepoHistory(data.history[REPO].commits, min_support=3)
    assert evaluate_k(data, ground_truth(data), 5, cochange="trailing").empty  # support 2 < 3: no partner


def test_figures_are_written_deterministically_when_matplotlib_is_present(tmp_path, monkeypatch) -> None:
    import pytest

    pytest.importorskip("matplotlib")
    import pandas as pd

    from analysis.rq1_divergence import write_figures

    dist = pd.Series([3, 2], index=["0", "1-2"], name="count")
    perf = [(0.1, 0.2), (0.1, 0.3), (0.1, 0.4)]
    monkeypatch.chdir(tmp_path)
    assert write_figures(dist, [5, 10, 20], perf, perf, perf, perf)
    first = {p.name: p.read_bytes() for p in (tmp_path / "paper/generated").glob("*.pdf")}
    assert set(first) == {"fig1_applicability.pdf", "fig2_accuracy.pdf"}
    write_figures(dist, [5, 10, 20], perf, perf, perf, perf)
    assert first == {p.name: p.read_bytes() for p in (tmp_path / "paper/generated").glob("*.pdf")}
