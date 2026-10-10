"""E1 feature layer against a hand-computed, checked-in fixture (`tests/fixtures/e1/`).

Fixture time T = 2026-06-01T00:00:00Z (epoch 1780272000); see make_fixture.py for the
offsets. Every expected value below was worked out by hand from that file, not
read back from the code under test.
"""

import json
import math
import os
import subprocess
from pathlib import Path

import pandas as pd
import pytest

from analysis.cochange_trailing import Commit, RepoHistory
from analysis.rq1_divergence import Rq1Data
from src.features.context import BrBenchHistory, ChangeContext, LocalGitHistory
from src.features.test_features import dir_distance, featurize, module_of, path_tokens

FX = Path(__file__).parent / "fixtures" / "e1"
T = 1780272000
DAY = 86400


@pytest.fixture(scope="module")
def hist() -> BrBenchHistory:
    strict = pd.read_parquet(FX / "strict.parquet")
    head = pd.read_parquet(FX / "head_all.parquet")
    runs = pd.read_parquet(FX / "runs.parquet")
    changed = pd.read_parquet(FX / "changed.parquet")
    commits = pd.read_parquet(FX / "commits.parquet")
    sl = strict.merge(runs[["repo", "run_id", "pr_number", "head_sha"]], on=["repo", "run_id"])
    bound = {(r.repo, r.test_id): r.resolved_path for r in strict.itertuples()}
    pr_to_changed: dict = {}
    for r in changed.itertuples():
        pr_to_changed.setdefault((r.repo, str(r.pr_number)), set()).add(r.filename)
    valid = sl.drop_duplicates("run_id")
    history = {"o/a": RepoHistory([Commit(r.sha, int(r.ts), tuple(r.files.split("|"))) for r in commits.itertuples()],
                                  365, 2)}
    data = Rq1Data(strict_labels=sl, bound=bound, pr_to_changed=pr_to_changed, co_support_map={}, co_lookup={},
                   hist_all=strict, language_of={}, n_strict_instances=len(valid), valid_runs=valid,
                   history=history, head_sha_of=dict(zip(runs.run_id, runs.head_sha)), hist_legacy=head)
    return BrBenchHistory(data)


def ctx_a() -> ChangeContext:
    return ChangeContext(repo="o/a", instance_key=("o/a", 100), ts=T, changed_files=("src/cart.py",),
                         n_lines_changed=12, touches_test_file=False, touches_build_config=True,
                         touches_ci_config=False, is_docs_only=False, head_sha="h100")


CANDS = ["tests/test_cart.py", "tests/test_other.py", "tests/unit/test_zeta.py"]


def test_history_family_strictly_before(hist: BrBenchHistory) -> None:
    df = featurize(ctx_a(), CANDS, hist.for_repo("o/a")).set_index("test_file")
    row = df.loc["tests/test_cart.py"]
    # strict failures at 120, 90, 60, 10 days before T; the ones at exactly T and at T+1 d are invisible
    assert row.hist_fail_count == 4
    assert row.hist_fail_30d == 1
    assert row.hist_fail_90d == 3  # 90 d is inside [T-90d, T): the boundary is inclusive below
    assert row.hist_days_since_last == 10.0
    assert row.hist_head_fail_count == 6  # the 4 strict + inherited (40 d) + flaky (5 d)
    assert df.loc["tests/test_other.py", "hist_fail_count"] == 0
    assert math.isnan(df.loc["tests/test_other.py", "hist_days_since_last"])
    assert list(df.hist_repo_rank) == [1, 2, 3]  # ties broken by path


def test_failure_at_exactly_ts_does_not_count(hist: BrBenchHistory) -> None:
    h = hist.for_repo("o/a")
    assert len(h.failures_before("tests/test_cart.py", T)) == 4
    assert len(h.failures_before("tests/test_cart.py", T + 1)) == 5  # the run at exactly T appears one second later
    assert h.head_failures_before("tests/test_cart.py", T + 1)[-1] == T


def test_repos_do_not_leak(hist: BrBenchHistory) -> None:
    # o/c failed the same file name 5 days before T; it must not reach o/a, and o/c sees only its own
    assert len(hist.for_repo("o/c").failures_before("tests/test_cart.py", T)) == 1
    assert len(hist.for_repo("o/a").failures_before("tests/test_cart.py", T)) == 4


def test_cochange_support_threshold_and_window(hist: BrBenchHistory) -> None:
    h = hist.for_repo("o/a")
    # five commits in [T-365d, T) touch src/cart.py; three contain test_cart.py -> support 3, conf 3/5.
    # the commits at T, T+2d and 400 d before T are outside; test_other.py has support 1 (< 2).
    assert h.cochange_stats("src/cart.py", "tests/test_cart.py", T, "h100") == (3, 0.6)
    assert h.cochange_stats("src/cart.py", "tests/test_other.py", T, "h100") == (0, 0.0)
    assert set(h.cochange_partners("src/cart.py", T)) == {"tests/test_cart.py"}


def test_cofailure(hist: BrBenchHistory) -> None:
    h = hist.for_repo("o/a")
    # runs 1, 2, 3 changed src/cart.py and had test_cart.py as a label; run 4 changed another file
    assert h.cofailure_count("src/cart.py", "tests/test_cart.py", T) == 3
    assert h.cofailure_count("src/other.py", "tests/test_cart.py", T) == 1


def test_full_row(hist: BrBenchHistory) -> None:
    df = featurize(ctx_a(), CANDS, hist.for_repo("o/a")).set_index("test_file")
    r = df.loc["tests/test_cart.py"]
    assert (r.cochg_max_support, r.cochg_sum_support, r.cochg_max_conf, r.cochg_sum_conf) == (3, 3, 0.6, 0.6)
    assert r.cochg_n_files_with_partner == 1
    assert (r.cofail_max, r.cofail_sum) == (3, 3)
    # tokens {tests,test,cart,py} vs {src,cart,py}: 2 shared of 5
    assert r.prox_max_jaccard == pytest.approx(0.4)
    assert r.prox_min_dir_dist == 2 and r.prox_name_contains_stem == 1 and r.prox_same_module == 1
    assert r.prox_in_change == 0
    assert (r.chg_n_files, r.chg_n_lines, r.chg_touches_test, r.chg_touches_build) == (1, 12, 0, 1)
    z = df.loc["tests/unit/test_zeta.py"]
    assert z.prox_max_jaccard == pytest.approx(1 / 7)  # {py} of {tests,unit,test,zeta,py,src,cart}
    assert z.prox_min_dir_dist == 3 and z.prox_name_contains_stem == 0
    o = df.loc["tests/test_other.py"]
    assert o.prox_max_jaccard == pytest.approx(1 / 6) and o.cochg_max_support == 0


def test_cold_start_repo_has_zero_history(hist: BrBenchHistory) -> None:
    ctx = ChangeContext("o/b", ("o/b", 200), T, ("lib/core.py",), head_sha="h200")
    df = featurize(ctx, ["tests/test_core.py"], hist.for_repo("o/b"))
    r = df.iloc[0]
    assert r.hist_fail_count == 0 and r.cochg_sum_support == 0 and r.cofail_sum == 0
    assert math.isnan(r.hist_days_since_last)


def test_path_helpers() -> None:
    assert path_tokens("src/UserService_test.py") == {"src", "user", "service", "test", "py"}
    assert path_tokens("a/HTTPServerTest.java") == {"a", "http", "server", "test", "java"}
    assert dir_distance("a/b/x.py", "a/b/y.py") == 0
    assert dir_distance("a/b/x.py", "a/c/d/y.py") == 3  # up 1 from a/b, down 2 to a/c/d
    assert module_of("pkgs/core/src/m.py") == "pkgs/core"
    assert module_of("pkgs/core/tests/test_m.py") == "pkgs/core"
    assert module_of("tests/test_x.py") == ""
    assert module_of("alpha/mod.py") == "alpha"


# ---- LocalGitHistory on a real tiny git repo -------------------------------------------------
def _git(cwd: Path, *args: str, when: str | None = None) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}
    if when:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True, env=env).stdout.strip()


def test_local_git_history(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init", "-q")
    shas = []
    plan = [("2026-01-01T00:00:00Z", ["src/a.py", "tests/test_a.py"]),
            ("2026-01-02T00:00:00Z", ["src/a.py", "tests/test_a.py"]),
            ("2026-01-03T00:00:00Z", ["src/a.py", "README.md"])]
    for i, (when, files) in enumerate(plan):
        for f in files:
            p = repo / f
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"{f} v{i}\n")
        _git(repo, "add", *files)
        _git(repo, "commit", "-q", "-m", f"c{i}", when=when)
        shas.append(_git(repo, "rev-parse", "HEAD"))
    state = repo / ".blastradius" / "history"
    state.mkdir(parents=True)
    (state / "test_outcomes.jsonl").write_text("\n".join(json.dumps(e) for e in [
        {"ts": "2026-01-02T12:00:00+00:00", "commit": shas[1], "test_id": "tests/test_a.py::test_x", "outcome": "failed"},
        {"ts": "2026-01-03T12:00:00+00:00", "commit": shas[2], "test_id": "tests/test_a.py::test_x", "outcome": "error"},
        {"ts": "2026-01-03T12:00:00+00:00", "commit": shas[2], "test_id": "tests/test_a.py::test_y", "outcome": "passed"},
    ]) + "\n")
    h = LocalGitHistory(repo)
    cutoff = 1767484800  # 2026-01-04T00:00:00Z
    assert len(h.failures_before("tests/test_a.py", cutoff)) == 2
    assert len(h.failures_before("tests/test_a.py", 1767355200)) == 0  # 2026-01-02T12:00:00Z itself is excluded
    assert len(h.failures_before("tests/test_a.py", 1767355201)) == 1
    assert h.cochange_stats("src/a.py", "tests/test_a.py", cutoff) == (2, 2 / 3)
    assert h.cofailure_count("src/a.py", "tests/test_a.py", cutoff) == 2
    assert h.cofailure_count("README.md", "tests/test_a.py", cutoff) == 1
    df = featurize(ChangeContext("r", ("r", 1), cutoff, ("src/a.py",)), ["tests/test_a.py"], h)
    assert df.iloc[0].hist_fail_count == 2 and df.iloc[0].cochg_max_support == 2
