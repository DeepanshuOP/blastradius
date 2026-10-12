"""Strategy arena (Live Lab, D-65): every number against a real recorded run, with hand-derived expected values.

Fixture: `tests/fixtures/lab/arena/pr1_run.jsonl` holds the measured events of one live lab run of the PR 1 change
shape on itsdangerous (`eval/lab/pr1_timed.py`: `if age > max_age` becomes `if age < max_age` in
TimestampSigner.unsign), no model: 297 executed cases, 5 failing. `pr1_graph.json` is that run's base-commit graph and
`history_itsdangerous.jsonl` the history line that run appended.

Expected values were counted outside the code under test (shell `sort` and `grep -c` over the fixture):
  * alphabetical ids: the first failing id, ...test_timed.py::TestTimedSerializer::test_max_age, is line 283;
  * cases per collected file: test_url_safe 130, test_timed 101, test_serializer 41, test_signer 17, test_encoding 8;
  * the bot's own tests.done event puts the first failure of the executed order at 127;
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


def load() -> tuple[list[dict], dict, list[str], dict, list[dict]]:
    evs = [json.loads(ln) for ln in (FIX / "pr1_run.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]
    results = [e["data"] for e in evs if e["type"] == "test.result"]
    change = next(e["data"] for e in evs if e["type"] == "change.applied")
    order = next(e["data"] for e in evs if e["type"] == "impact.ranking")["at_risk_files"]
    view = json.loads((FIX / "pr1_graph.json").read_text(encoding="utf-8"))
    hist = arena.read_history("itsdangerous", FIX / "history_itsdangerous.jsonl")
    return results, change, order, view, hist


def row(doc: dict, sid: str) -> dict:
    return next(s for s in doc["strategies"] if s["id"] == sid)


def test_arena_numbers_against_hand_counts() -> None:
    results, change, order, view, hist = load()
    no_cc = (Counter(), 0, "no usable git history before the base (a pinned snapshot or shallow clone with one commit)")
    doc = arena.compute(results, order_files=order, view=view, changed_nodes=change["changed_nodes"],
                        changed_fns=change["changed_functions"], coverage=None, history=hist, cochange=no_cc)
    assert (doc["n_cases"], doc["n_failing"]) == (297, 5)

    r = row(doc, "retest-all")
    assert (r["selected"], r["caught"], r["recall"], r["first_failure_position"], r["missed"]) == (297, 5, 1.0, 283, [])

    b = row(doc, "blastradius")
    assert (b["selected"], b["caught"], b["recall"], b["first_failure_position"]) == (297, 5, 1.0, 127)

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


def test_cold_start_history_selects_nothing_and_says_so() -> None:
    results, change, order, view, _ = load()
    doc = arena.compute(results, order_files=order, view=view, changed_nodes=change["changed_nodes"],
                        changed_fns=change["changed_functions"], coverage=None, history=[], cochange=(Counter(), 0, "none"))
    h = row(doc, "history")
    assert (h["status"], h["selected"], h["caught"], h["note"]) == ("cold-start", 0, 0, "cold start: no history")
    assert len(h["missed"]) == 5
    assert "no earlier runs" in doc["takeaway"]


def test_takeaway_is_generated_from_the_numbers() -> None:
    results, change, order, view, hist = load()
    doc = arena.compute(results, order_files=order, view=view, changed_nodes=change["changed_nodes"],
                        changed_fns=change["changed_functions"], coverage=None, history=hist, cochange=(Counter(), 0, "none"))
    # cheapest other strategy with full recall: history (5 cases, 1.68%), so the sentence must name it with 2%
    assert doc["takeaway"].startswith("BlastRadius ran 100% of the suite and caught 5 of 5 failures, the first at test 127;")
    assert "failure history, ran 2%" in doc["takeaway"]


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
