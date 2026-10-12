"""Live Lab, Part 4 (D-65): break it yourself, the test-gap alert, the suite-strength probe, pull-request changes.

Real fixtures only: the prepared itsdangerous repository (copied to a scratch directory) run for real with no model.
The reference case is CMP_FLIP on src/itsdangerous/timed.py:141 (`if age > max_age:` becomes `if age >= max_age:`),
which the whole suite lets through: test_max_age freezes time, signs, ticks 10 s and expects SignatureExpired only
once the age passes max_age = 10, so no test sits on the boundary age == max_age.
"""

from __future__ import annotations

import io
import json
import shutil
import sys
from pathlib import Path

import pytest

from tests.conftest import requires_data

from src.lab import __main__ as labmain
from src.lab import arena, changes, workspace
from src.lab.engine import Lab, LabArgs
from src.lab.events import Emitter, validate_event

NEEDS = ("data/seeded/repos/itsdangerous", "data/seeded/venvs/itsdangerous/bin/python", "data/seeded/repos/shopcart")


@pytest.fixture(scope="module")
def seeded():
    from analysis.demo_check import scratch_seeded

    d = scratch_seeded()
    state = Path(workspace.new_scratch("arena-state"))
    mp = pytest.MonkeyPatch()
    mp.setattr(workspace, "REPOS", d / "repos")
    mp.setattr(workspace, "VENVS", d / "venvs")
    mp.setattr(arena, "HISTORY_DIR", state / "history")
    mp.setattr(arena, "COVERAGE_DIR", state / "coverage")
    try:
        yield d
    finally:
        mp.undo()
        shutil.rmtree(d, ignore_errors=True)
        shutil.rmtree(state, ignore_errors=True)


def test_mutation_listing_carries_function_spans() -> None:
    src = Path("data/seeded/repos/itsdangerous/src/itsdangerous/timed.py")
    if not src.exists():
        pytest.skip("data/seeded is not prepared")
    fns = {f["function"]: f for f in changes.mutations_of(src.read_text(encoding="utf-8"))}
    u = fns["TimestampSigner.unsign"]
    # the implementation (the third `def unsign`, after two @t.overload stubs at 56-63 and 64-71) spans 72-158
    assert (u["start"], u["def_line"], u["end"]) == (72, 72, 158)
    assert {"operator": "CMP_FLIP", "line": 141, "col": 19, "old": ">", "new": ">="} in u["mutations"]


@requires_data(*NEEDS)
def test_cmp_flip_on_timed_141_is_a_test_gap(seeded) -> None:
    em = Emitter(io.StringIO())
    lab = Lab(LabArgs(repo="itsdangerous", inject=("src/itsdangerous/timed.py", "TimestampSigner.unsign", "CMP_FLIP", 141),
                      use_llm=False), em, None)
    try:
        lab.run()
    finally:
        lab.cleanup()
    evs = em.history
    assert all(not validate_event(e) for e in evs)
    done = next(e for e in evs if e["type"] == "tests.done")["data"]
    assert done["counts"]["failed"] == done["counts"]["error"] == 0 and done["counts"]["total"] == 297
    gap = next(e for e in evs if e["type"] == "arena.gap")["data"]
    assert (gap["line"], gap["old"], gap["new"]) == (141, ">", ">=")
    assert gap["before"].strip() == "if age > max_age:" and gap["after"].strip() == "if age >= max_age:"
    assert "tests/test_itsdangerous/test_timed.py::TestTimestampSigner::test_max_age" in gap["covering"]
    assert gap["graph_files"] == ["tests/test_itsdangerous/test_serializer.py", "tests/test_itsdangerous/test_timed.py",
                                  "tests/test_itsdangerous/test_url_safe.py"]
    assert gap["sentence"].startswith("All 297 tests passed with `>` changed to `>=` on line 141")


@requires_data(*NEEDS)
def test_a_caught_injection_raises_no_gap(seeded) -> None:
    em = Emitter(io.StringIO())
    lab = Lab(LabArgs(repo="itsdangerous", inject=("src/itsdangerous/timed.py", "TimestampSigner.unsign", "ARITH_SWAP", 139),
                      use_llm=False), em, None)
    try:
        lab.run()
    finally:
        lab.cleanup()
    assert next(e for e in em.history if e["type"] == "tests.done")["data"]["counts"]["failed"] > 0
    assert not any(e["type"] == "arena.gap" for e in em.history)


@requires_data(*NEEDS)
def test_probe_runs_five_mutants_and_finds_the_survivor(seeded, monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["src.lab", "probe"])
    labmain.main(["probe", "--repo", "itsdangerous", "--file", "src/itsdangerous/timed.py", "--function", "TimestampSigner.unsign"])
    out = [json.loads(ln) for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert all(not validate_event(e) for e in out)
    final = next(e for e in out if e["type"] == "arena.probe" and e["status"] == "ok")["data"]
    rows = {(r["operator"], r["line"]): r for r in final["rows"]}
    assert final["n"] == 5 and len(final["rows"]) == 5 and final["caught"] + final["survived"] == 5
    # one of each operator first, in line order: NEGATE_COND 102, ARITH_SWAP 139, CMP_FLIP 141, then 103, 148
    assert [(r["operator"], r["line"]) for r in final["rows"]] == [("NEGATE_COND", 102), ("ARITH_SWAP", 139), ("CMP_FLIP", 141),
                                                                    ("NEGATE_COND", 103), ("CMP_FLIP", 148)]
    assert rows[("CMP_FLIP", 141)]["caught"] is False and rows[("CMP_FLIP", 141)]["failed"] == 0
    assert rows[("ARITH_SWAP", 139)]["caught"] is True
    # the repository copy is restored after every mutant
    text = (seeded / "repos" / "itsdangerous" / "src" / "itsdangerous" / "timed.py").read_text(encoding="utf-8")
    assert "if age > max_age:" in text


@requires_data(*NEEDS)
def test_pull_request_change_is_merge_base_to_head(seeded, tmp_path) -> None:
    from src.lab.workspace import git, prepare_seeded

    ws = prepare_seeded("shopcart", tmp_path)
    base = ws.base
    f = ws.repo_dir / "shopcart" / "cart.py"
    f.write_text(f.read_text(encoding="utf-8") + "\n# reviewed\n", encoding="utf-8")
    git(ws.repo_dir, "add", "-u")
    git(ws.repo_dir, "commit", "-q", "-m", "pr head")
    head = git(ws.repo_dir, "rev-parse", "HEAD")
    ch = changes.from_pr(ws, {"merge_base": base, "head": head, "number": 7, "html_url": "https://github.com/o/r/pull/7",
                              "title": "t", "merged": True, "base_sha": base, "head_sha": head})
    assert (ch.base, ch.head, ch.changed_files) == (base, head, ["shopcart/cart.py"])
    assert ch.source["kind"] == "pr" and ch.source["number"] == 7
    assert "+# reviewed" in ch.diff and ch.base_sources["shopcart/cart.py"] == git(ws.repo_dir, "show", f"{base}:shopcart/cart.py")


def test_pr_url_pattern() -> None:
    assert workspace.PR_RE.match("https://github.com/tkem/cachetools/pull/424")
    assert not workspace.PR_RE.match("https://github.com/tkem/cachetools/pull/424/files")
    assert not workspace.PR_RE.match("https://example.com/tkem/cachetools/pull/424")
