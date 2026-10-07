"""RQ1 evaluation on a tiny hand-built instance with hand-computed expectations."""

from __future__ import annotations

import pandas as pd

from analysis.rq1_divergence import Rq1Data, evaluate_k, ground_truth, summarize

REPO = "acme/widgets"


def make_data() -> Rq1Data:
    strict = pd.DataFrame(
        {"run_id": [1, 1], "test_id": ["t::a", "t::env"], "split": ["strict", "strict"],
         "repo": [REPO, REPO], "pr_number": [7, 7], "run_started_at": ["2026-02-01", "2026-02-01"]}
    )
    hist = pd.DataFrame(
        {"repo": [REPO] * 3, "run_started_at": ["2026-01-01"] * 3,
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
    )


def test_all_partner_and_test_restricted_scores_at_k2() -> None:
    data = make_data()
    gt = ground_truth(data)
    assert gt == {(REPO, 1): {"tests/test_a.py", "tests/test_env.py"}}
    df = evaluate_k(data, gt, 2)
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
    assert evaluate_k(data, gt, 2).iloc[0]["co_r"] == 1.0
    assert ground_truth(data, exclude={(1, "t::env"), (1, "t::a")}) == {}
    assert evaluate_k(data, {}, 2).empty


def test_summarize_reports_every_method_with_n_over_d_micro_rates() -> None:
    rows = summarize(evaluate_k(make_data(), ground_truth(make_data()), 2))
    assert [r[0] for r in rows] == [
        "co-change, all partner files", "co-change, restricted to test files",
        "changeset baseline", "historical-frequency baseline",
    ]
    assert rows[0][5] == "1/2 (50.00%)" and rows[0][6] == "1/2 (50.00%)"


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
