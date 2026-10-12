"""Strategy arena (Live Lab, D-65): every number against a real recorded run, with hand-derived expected values.

Fixture: `tests/fixtures/lab/arena/pr1_run.jsonl` holds the measured events of one live lab run of the PR 1 change
shape on itsdangerous (`eval/lab/pr1_timed.py`: `if age > max_age` becomes `if age < max_age` in
TimestampSigner.unsign), no model: 297 executed cases, 5 failing. `pr1_graph.json` is that run's base-commit graph and
`history_itsdangerous.jsonl` the history line that run appended.

Expected values were counted outside the code under test (shell `sort` and `grep -c` over the fixture):
  * alphabetical ids: the first failing id, ...test_timed.py::TestTimedSerializer::test_max_age, is line 283;
  * cases per collected file: test_url_safe 130, test_timed 101, test_serializer 41, test_signer 17, test_encoding 8;
  * the bot's own tests.done event puts the first failure of the order the run used (E1 file rank only, before the
    test-case rule of 2026-10-12) at 127; the BlastRadius row is now the rule's order, whose hand-computed expectations
    live in tests/test_lab_order.py (first failure at test 17, 37.5 ms);
  * the test files whose imports reach timed.py: test_timed (imports itsdangerous.timed), test_url_safe (imports
    itsdangerous.url_safe, which imports timed); test_serializer through the graph's tests_by_convention edge
    test_iter_unsigners -> TimedSerializer.iter_unsigners. test_signer and test_encoding import neither.
    So static RTS keeps 41 + 101 + 130 = 272 cases and drops the 17 + 8 = 25 test_signer / test_encoding cases, all of
    which sort before test_timed: its first failure moves from 283 to 283 - 25 = 258.
  * each of the 5 failing ids names exactly one case, so a history that holds exactly those 5 ids selects 5 cases.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

import pytest

from tests.conftest import requires_data

from src.lab import arena

FIX = Path(__file__).parent / "fixtures" / "lab" / "arena"
RULE: dict = {}


def load() -> tuple[list[dict], dict, list[str], dict, list[dict]]:
    """Results, change, at-risk files, graph, history; `RULE` is set as a side effect (the BlastRadius order's input)."""
    global RULE
    evs = [json.loads(ln) for ln in (FIX / "pr1_run.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]
    results = [e["data"] for e in evs if e["type"] == "test.result"]
    change = next(e["data"] for e in evs if e["type"] == "change.applied")
    order = next(e["data"] for e in evs if e["type"] == "impact.ranking")["at_risk_files"]
    view = json.loads((FIX / "pr1_graph.json").read_text(encoding="utf-8"))
    hist = arena.read_history("itsdangerous", FIX / "history_itsdangerous.jsonl")
    ranking = next(e["data"] for e in evs if e["type"] == "impact.ranking")
    from src.lab import order as case_order

    RULE = case_order.rule_payload(ranking["rows"], order, view, change["changed_nodes"])
    return results, change, order, view, hist


def row(doc: dict, sid: str) -> dict:
    return next(s for s in doc["strategies"] if s["id"] == sid)


def test_arena_numbers_against_hand_counts() -> None:
    results, change, order, view, hist = load()
    no_cc = (Counter(), 0, "no usable git history before the base (a pinned snapshot or shallow clone with one commit)")
    doc = arena.compute(results, order_files=order, view=view, changed_nodes=change["changed_nodes"],
                        changed_fns=change["changed_functions"], coverage=None, history=hist, cochange=no_cc, rule=RULE)
    assert (doc["n_cases"], doc["n_failing"]) == (297, 5)

    r = row(doc, "retest-all")
    assert (r["selected"], r["caught"], r["recall"], r["first_failure_position"], r["missed"]) == (297, 5, 1.0, 283, [])

    b = row(doc, "blastradius")
    assert (b["selected"], b["caught"], b["recall"], b["first_failure_position"]) == (297, 5, 1.0, 17)
    assert b["first_failure_ms"] == 37.5 and b["orders_all"] is True and b["kind"] == "orderer"
    assert (r["kind"], row(doc, "static-rts")["kind"]) == ("orderer", "selector")

    s = row(doc, "static-rts")
    assert (s["selected"], s["caught"], s["recall"], s["first_failure_position"]) == (272, 5, 1.0, 258)
    assert s["pct"] == round(100 * 272 / 297, 2)

    h = row(doc, "history")
    assert (h["status"], h["selected"], h["caught"], h["recall"], h["first_failure_position"]) == ("ok", 5, 5, 1.0, 1)

    c = row(doc, "cochange")
    assert c["status"] == "unavailable" and c["recall"] is None and "one commit" in c["note"]
    cov = row(doc, "coverage")
    assert cov["status"] == "unavailable"

    # times: the CI time of retest-all is the whole suite's measured time; BlastRadius selected everything too
    assert r["ci_ms"] == doc["suite_ms"] == b["ci_ms"]
    assert b["first_failure_ms"] < r["first_failure_ms"]
    assert doc["basis"] == "computed from this run's full-suite results; not run separately"
    # `needs`: what each approach requires before it can work
    assert r["needs"] == "nothing" and row(doc, "static-rts")["needs"] == "code graph"
    assert b["needs"] == "graph and model (E1)"
    assert row(doc, "history")["needs"] == "earlier runs (1 in this repository's lab history)"
    assert row(doc, "cochange")["needs"] == "git history (none usable here)"
    assert row(doc, "coverage")["needs"] == "an instrumented coverage run at base (not available here)"


def test_cold_start_history_selects_nothing_and_says_so() -> None:
    results, change, order, view, _ = load()
    doc = arena.compute(results, order_files=order, view=view, changed_nodes=change["changed_nodes"],
                        changed_fns=change["changed_functions"], coverage=None, history=[], cochange=(Counter(), 0, "none"), rule=RULE)
    h = row(doc, "history")
    assert (h["status"], h["selected"], h["caught"], h["note"]) == ("cold-start", 0, 0, "cold start: no history")
    assert len(h["missed"]) == 5
    assert "no earlier runs" in doc["takeaway"]


def test_takeaway_is_generated_from_the_numbers() -> None:
    results, change, order, view, hist = load()
    doc = arena.compute(results, order_files=order, view=view, changed_nodes=change["changed_nodes"],
                        changed_fns=change["changed_functions"], coverage=None, history=hist, cochange=(Counter(), 0, "none"), rule=RULE)
    # cheapest selector with full recall: history (5 cases, 1.68%), so the sentence must name it with 2%
    assert doc["takeaway"].startswith("BlastRadius ordered all 297 tests and reached its first failure at test 17 (38 ms); "
                                      "retest-all reached it at test 283 (")
    assert "failure history, ran 2% of the suite" in doc["takeaway"]


def test_history_store_round_trip(tmp_path: Path) -> None:
    p = tmp_path / "h.jsonl"
    line = json.loads((FIX / "history_itsdangerous.jsonl").read_text(encoding="utf-8").splitlines()[0])
    arena.append_history("itsdangerous", line, p)
    arena.append_history("itsdangerous", line, p)
    assert arena.read_history("itsdangerous", p) == [line, line]


NEEDS = ("data/seeded/repos/itsdangerous", "data/seeded/venvs/itsdangerous/bin/python")


@pytest.fixture(scope="module")
def seeded():
    from analysis.demo_check import scratch_seeded

    d = scratch_seeded()
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


@requires_data(*NEEDS)
def test_coverage_plugin_is_deterministic_and_sees_unsign(seeded, tmp_path, monkeypatch) -> None:
    from src.lab.workspace import git

    repo = seeded / "repos" / "itsdangerous"
    py = str(seeded / "venvs" / "itsdangerous" / "bin" / "python")
    base = git(repo, "rev-parse", "HEAD")
    docs = []
    for k in (1, 2):                                   # two cold runs, two empty caches
        monkeypatch.setattr(arena, "COVERAGE_DIR", tmp_path / f"cov{k}")
        docs.append(arena.run_coverage(repo, base, py, "itsdangerous"))
    a, b = docs
    assert a["status"] == b["status"] == "ok" and not a["cached"] and not b["cached"]
    assert a["tests"] == b["tests"] and a["n_tests"] == b["n_tests"] == 297
    t = a["tests"]["tests/test_itsdangerous/test_timed.py::TestTimestampSigner::test_max_age"]
    assert any(f[0] == "src/itsdangerous/timed.py" and f[2] == "TimestampSigner.unsign" for f in t["functions"])
    enc = [v for k, v in a["tests"].items() if k.startswith("tests/test_itsdangerous/test_encoding.py::")]
    assert enc and all(not any(f[0] == "src/itsdangerous/timed.py" for f in v["functions"]) for v in enc)
    # a third call is served from the cache and says so
    assert arena.run_coverage(repo, base, py, "itsdangerous")["cached"] is True


@requires_data(*NEEDS)
def test_cochange_reports_a_snapshot_honestly(seeded) -> None:
    from src.lab.workspace import git

    repo = seeded / "repos" / "itsdangerous"
    counts, used, reason = arena.cochange_counts(repo, git(repo, "rev-parse", "HEAD"), ["src/itsdangerous/timed.py"])
    assert (len(counts), used) == (0, 0) and "one commit" in reason


def _git(cwd: Path, *a: str) -> str:
    import subprocess

    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@example.invalid", "PATH": __import__("os").environ["PATH"], "HOME": str(cwd)}
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True, env=env).stdout.strip()


def test_cochange_runs_after_upstream_history_is_fetched(tmp_path: Path) -> None:
    """A real local upstream with three commits; the scratch clone has one. Fetching the pin's history through the
    cache makes co-change possible; before the fetch the arena's own reason applies."""
    from src.lab import workspace

    up = tmp_path / "upstream"
    up.mkdir()
    _git(up, "init", "-q", "-b", "main")
    (up / "src").mkdir()
    (up / "tests").mkdir()
    for step, files in enumerate([{"src/a.py": "1", "tests/test_a.py": "1", "src/b.py": "1", "tests/test_b.py": "1"},
                                  {"src/a.py": "2", "tests/test_a.py": "2"},
                                  {"src/b.py": "2", "tests/test_b.py": "2"}]):
        for f, text in files.items():
            (up / f).write_text(text + "\n", encoding="utf-8")
        _git(up, "add", *files)
        _git(up, "commit", "-q", "-m", f"c{step}")
    sha = _git(up, "rev-parse", "HEAD")
    scratch = tmp_path / "scratch"
    _git(tmp_path, "clone", "-q", "--depth=1", f"file://{up}", str(scratch))

    counts, used, reason = arena.cochange_counts(scratch, sha, ["src/a.py"])
    assert used == 0 and "one commit" in reason

    info = workspace.fetch_history(scratch, f"file://{up}", sha, tmp_path / "cache.git")
    assert info["status"] == "fetched" and info["commits"] == 3 and info["reason"] == ""
    counts, used, reason = arena.cochange_counts(scratch, sha, ["src/a.py"])
    assert reason is None and used == 2                     # c1 and c2; c0 is the root commit
    assert dict(counts) == {"tests/test_a.py": 1}           # only c1 changed src/a.py together with a test file

    again = workspace.fetch_history(scratch, f"file://{up}", sha, tmp_path / "cache.git")
    assert again["status"] == "cached" and again["commits"] == 3


def test_unreachable_upstream_is_reported_not_raised(tmp_path: Path) -> None:
    from src.lab import workspace

    scratch = tmp_path / "s"
    _git(tmp_path, "init", "-q", "-b", "main", str(scratch))
    info = workspace.fetch_history(scratch, f"file://{tmp_path / 'no-such-upstream'}", "0" * 40, tmp_path / "c.git")
    assert info["status"] == "unavailable" and info["commits"] == 0 and info["reason"]
