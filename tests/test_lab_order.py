"""The BlastRadius test-case order (Live Lab, D-65): expected values against a real recorded run.

Rule (fixed 2026-10-12, after the PR 1 case had been seen): keep the E1 file rank; files tied in E1 score form one
tier; inside a tier, test cases run by graph hop distance to the changed functions (shortest first), then by id.

Fixture: `tests/fixtures/lab/arena/pr1_run.jsonl` (the measured events of a live run of the PR 1 change on
itsdangerous, 297 cases, 5 failing, no model) and `pr1_graph.json` (that run's base-commit graph).
`pr1_expected_order.json` is the order the rule gives on it, produced by an implementation that shares nothing with
`src/lab` (graph test nodes found by node-id slug instead of label and containment edges, its own breadth-first search).
It is the ground truth of this file: if a test here fails, the code is wrong, not the expectation.

Facts that can be checked by hand against the fixture:
  * E1 gave five test files the score -0.721 and test_timed.py -1.2063, so there are two tiers;
  * all 8 cases of test_encoding.py exercise functions `unsign` calls (base64_decode, bytes_to_int, want_bytes): two
    hops from it, the closest cases of tier 0, so they run first, ordered by id;
  * the failing cases are the five `test_max_age` cases that compare an age with max_age; three sit in test_url_safe.py
    (tier 0, three hops from `unsign`) and two in test_timed.py (tier 1, so after every case of tier 0, 195 of them).
"""

from __future__ import annotations

import json
from pathlib import Path

from src.agents.regression import junit_test_id
from src.lab import arena, order
from src.lab.plugin import br_order

FIX = Path(__file__).parent / "fixtures" / "lab" / "arena"


def load() -> tuple[list[dict], dict, dict]:
    evs = [json.loads(ln) for ln in (FIX / "pr1_run.jsonl").read_text(encoding="utf-8").splitlines() if ln.strip()]
    results = [e["data"] for e in evs if e["type"] == "test.result"]
    ranking = next(e["data"] for e in evs if e["type"] == "impact.ranking")
    change = next(e["data"] for e in evs if e["type"] == "change.applied")
    view = json.loads((FIX / "pr1_graph.json").read_text(encoding="utf-8"))
    payload = order.rule_payload(ranking["rows"], ranking["at_risk_files"], view, change["changed_nodes"])
    return results, ranking, payload


def test_tiers_are_equal_e1_scores() -> None:
    _, ranking, payload = load()
    t = payload["tiers"]
    five = [f for f in ranking["at_risk_files"] if not f.endswith("test_timed.py")]
    assert {t[f] for f in five} == {0} and t["tests/test_itsdangerous/test_timed.py"] == 1


def test_order_matches_the_hand_computed_order() -> None:
    results, _, payload = load()
    expected = json.loads((FIX / "pr1_expected_order.json").read_text(encoding="utf-8"))
    got = [results[i]["nodeid"] for i in order.derive(results, payload)]
    assert got == expected["order"]
    assert len(got) == 297 and len(set(got)) == 297


def test_first_failure_position_and_time_against_hand_counts() -> None:
    results, _, payload = load()
    idx = order.derive(results, payload)
    fail = [k + 1 for k, i in enumerate(idx) if results[i]["outcome"] in ("failed", "error")]
    assert fail == [17, 18, 19, 202, 207]
    row = arena.score(results, idx)
    assert (row["first_failure_position"], row["first_failure_ms"], row["selected"]) == (17, 37.5, 297)
    # 8 cases of test_encoding (hop 2) + 8 more tier-0 cases (hop 2 or 3, by id) precede the first failure
    first8 = [results[i]["nodeid"] for i in idx[:8]]
    assert all(n.startswith("tests/test_itsdangerous/test_encoding.py::") for n in first8)
    assert first8 == sorted(first8, key=lambda n: n)  # equal hops: by id


def test_file_rank_is_kept_across_tiers() -> None:
    results, _, payload = load()
    idx = order.derive(results, payload)
    files = [results[i]["nodeid"].split("::")[0] for i in idx]
    last_tier0 = max(k for k, f in enumerate(files) if not f.endswith("test_timed.py"))
    first_tier1 = min(k for k, f in enumerate(files) if f.endswith("test_timed.py"))
    assert last_tier0 < first_tier1 and first_tier1 == 196


def test_the_rule_is_idempotent_and_stable() -> None:
    results, _, payload = load()
    idx = order.derive(results, payload)
    again = br_order.order([results[i] for i in idx], payload["tiers"], payload["hops"])
    assert again == list(range(len(results)))          # an already-ordered run is its own order


def test_unreached_cases_sort_last_in_their_tier() -> None:
    cases = [{"id": "t/a.py::test_far", "nodeid": "t/a.py::test_far"},
             {"id": "t/a.py::test_near", "nodeid": "t/a.py::test_near"},
             {"id": "t/a.py::test_none", "nodeid": "t/a.py::test_none"}]
    hops = {"t/a.py::*::test_near": 1, "t/a.py::*::test_far": 3}
    assert br_order.order(cases, {"t/a.py": 0}, hops) == [1, 0, 2]


def test_plugin_core_agrees_with_regression_on_canonical_ids() -> None:
    for file, cls, name in [("tests/t_x.py", "tests.t_x.TestA", "test_a[1]"), ("tests/t_x.py", "tests.t_x", "test_b"),
                            ("tests/t_x.py", "tests.t_y.TestInherited", "test_c")]:
        assert br_order.junit_test_id(file, cls, name) == junit_test_id(file, cls, name)


def test_old_order_is_file_rank_then_collection_order() -> None:
    results = [{"id": "b.py::t2", "nodeid": "b.py::t2"}, {"id": "a.py::t1", "nodeid": "a.py::t1"},
               {"id": "a.py::t0", "nodeid": "a.py::t0"}]
    native = ["a.py::t1", "a.py::t0", "b.py::t2"]
    assert order.old_order(results, native, ["a.py", "b.py"]) == [1, 2, 0]
