"""Live Lab engine (D-65): stage order, streamed results, triage units, replay, injection, no writes to seeded data.

Real fixtures only: the prepared repositories of `data/seeded`, copied to a scratch directory (so a live E3 run that
holds the originals cannot disturb the checks) and run for real with `llm=None`.
"""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.conftest import requires_data

from src.eval.seeded import mutate
from src.lab import __main__ as labmain
from src.lab import workspace
from src.lab.engine import Lab, LabArgs
from src.lab.events import STAGES, Emitter, validate_event

ROOT = Path(__file__).resolve().parents[1]
NEEDS = ("data/seeded/repos/itsdangerous", "data/seeded/venvs/itsdangerous/bin/python",
         "data/seeded/repos/markupsafe", "data/seeded/venvs/markupsafe/bin/python")


def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file() and not p.is_symlink():
            h.update(str(p.relative_to(root)).encode())
            h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def run_lab(args: LabArgs) -> list[dict]:
    em = Emitter(io.StringIO())
    lab = Lab(args, em, None)
    try:
        lab.run()
    finally:
        lab.cleanup()
    return em.history


@pytest.fixture(scope="module")
def seeded_copy():
    from analysis.demo_check import scratch_seeded

    d = scratch_seeded()
    mp = pytest.MonkeyPatch()
    mp.setattr(workspace, "REPOS", d / "repos")
    mp.setattr(workspace, "VENVS", d / "venvs")
    from src.lab import arena                      # the arena's history and coverage cache go to a throw-away directory
    state = Path(workspace.new_scratch("arena-state"))
    mp.setattr(arena, "HISTORY_DIR", state / "history")
    mp.setattr(arena, "COVERAGE_DIR", state / "coverage")
    before = tree_hash(d)
    try:
        yield d, before
    finally:
        mp.undo()
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture(scope="module")
def itsdangerous_run(seeded_copy):
    return run_lab(LabArgs(repo="itsdangerous", task="itsdangerous-ARITH_SWAP-00", use_llm=False))


@requires_data(*NEEDS)
def test_stage_order_streamed_results_unique_triage_and_repair_skipped(itsdangerous_run, seeded_copy) -> None:
    evs = itsdangerous_run
    assert all(not validate_event(e) for e in evs), [validate_event(e) for e in evs if validate_event(e)][:3]
    # decision-log records (D-71) interleave with the stages they describe, so they are left out of the order check
    first = list(dict.fromkeys(e["stage"] for e in evs if e["stage"] != "audit"))
    pipeline = [s for s in STAGES if s != "audit"]
    assert first == [s for s in pipeline if s in first] and first == pipeline, first
    assert any(e["type"] == "audit.record" for e in evs)
    assert next(e for e in evs if e["type"] == "audit.verify")["data"]["ok"] is True
    assert [e["seq"] for e in evs] == list(range(1, len(evs) + 1))

    results = [e for e in evs if e["type"] == "test.result"]
    done = next(e for e in evs if e["type"] == "tests.done")["data"]
    d, _ = seeded_copy
    py = d / "venvs" / "itsdangerous" / "bin" / "python"
    # the suite size, counted independently by pytest's own collection in a throw-away copy of the repository
    tmp = workspace.new_scratch("collect")
    try:
        repo = shutil.copytree(d / "repos" / "itsdangerous", tmp / "r", ignore=shutil.ignore_patterns("__pycache__"))
        out = subprocess.run([str(py), "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"], cwd=repo,
                             capture_output=True, text=True, env={"PYTHONPATH": f"{repo}:{repo / 'src'}",
                                                                  "PYTHONDONTWRITEBYTECODE": "1", "PATH": "/usr/bin"})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    suite = sum(1 for ln in out.stdout.splitlines() if "::" in ln)
    assert suite > 100 and len(results) == suite == done["counts"]["total"] == done["n_results"]

    tri = next(e for e in evs if e["type"] == "triage.result")["data"]
    ids = [r["test"] for r in tri["rows"]]
    assert len(ids) == len(set(ids)) and sum(tri["counts"].values()) == len(ids)
    failed_ids = {r["data"]["id"] for r in results if r["data"]["outcome"] in ("failed", "error")}
    assert set(ids) == failed_ids and len(ids) < done["counts"]["failed"]          # duplicates collapsed, stated
    assert tri["failing_cases"] == done["counts"]["failed"] and tri["unit"] == "unique canonical test ids"
    assert all(r["base_outcome"] in ("passed", "failed", "error", "skipped", "absent") for r in tri["rows"])

    rep = [e for e in evs if e["stage"] == "repair"]
    assert len(rep) == 1 and rep[0]["type"] == "repair.skipped" and rep[0]["status"] == "skipped"
    assert "no model" in rep[0]["data"]["reason"]
    assert next(e for e in evs if e["type"] == "validate.verdict")["status"] == "skipped"

    race = next(e for e in evs if e["type"] == "tests.race")["data"]
    risk, alpha = race["lanes"]
    assert race["order_respected"] is True
    assert len(risk["ticks"]) == len(alpha["ticks"]) == suite
    assert "computed" in alpha["basis"] and "not separately run" in alpha["basis"].replace("was not run separately",
                                                                                       "not separately run")


@requires_data(*NEEDS)
def test_replay_reproduces_the_recorded_events_except_ts(itsdangerous_run, tmp_path, monkeypatch, capsys) -> None:
    recorded = [{k: v for k, v in e.items()} for e in itsdangerous_run]
    (tmp_path / "t.jsonl").write_text("\n".join(json.dumps(e) for e in recorded) + "\n", encoding="utf-8")
    monkeypatch.setattr(labmain, "RUNS", tmp_path)
    assert labmain._replay("t", 1e9) == 0
    out = [json.loads(ln) for ln in capsys.readouterr().out.splitlines()]
    assert len(out) == len(recorded) and all(e["replay"] is True for e in out)
    strip = lambda e: {k: v for k, v in e.items() if k not in ("ts", "replay")}   # noqa: E731
    assert [strip(e) for e in out] == [strip(e) for e in recorded]
    assert all(not validate_event(e) for e in out)


@requires_data(*NEEDS)
def test_inject_bug_yields_the_diff_mutate_apply_gives(seeded_copy) -> None:
    d, _ = seeded_copy
    path = "src/markupsafe/__init__.py"
    text = (d / "repos" / "markupsafe" / path).read_text(encoding="utf-8")
    m = next(m for m in mutate.find_mutations(text) if m.function and m.function != "<module>")
    evs = run_lab(LabArgs(repo="markupsafe", inject=(path, m.function, m.operator, m.line), use_llm=False))
    ch = next(e for e in evs if e["type"] == "change.applied")["data"]
    expected = mutate.apply(text, m).splitlines()
    got = [ln[1:] for ln in ch["diff"].splitlines() if ln.startswith("+") and not ln.startswith("+++")]
    gone = [ln[1:] for ln in ch["diff"].splitlines() if ln.startswith("-") and not ln.startswith("---")]
    assert ch["changed_files"] == [path] and len(got) == len(gone) == 1
    assert got[0] == expected[m.line - 1] and gone[0] == text.splitlines()[m.line - 1]
    assert ch["source"]["operator"] == m.operator and ch["source"]["function"] == m.function
    assert any(c["function"] == m.function for c in ch["changed_functions"])        # mapped onto the graph node
    # and the suite really ran on the mutant: every test.result carries a measured duration
    assert any(e["type"] == "test.result" for e in evs)


@requires_data(*NEEDS)
def test_seeded_tree_is_unchanged_after_runs(seeded_copy, itsdangerous_run) -> None:
    d, before = seeded_copy
    assert tree_hash(d) == before


def test_event_schema_rejects_a_malformed_event() -> None:
    assert validate_event({"seq": 1}) and validate_event(
        {"seq": 1, "ts": "x", "stage": "tests", "type": "nonsense", "status": "ok", "dur_ms": 0, "data": {}})
    assert not validate_event({"seq": 1, "ts": "x", "stage": "tests", "type": "test.result", "status": "ok",
                               "dur_ms": 1, "data": {"id": "a::b", "outcome": "passed", "duration_s": 0.1}})


@requires_data("data/seeded/repos/click")
def test_graph_command_stdout_is_json_on_a_cache_miss(tmp_path) -> None:
    """A cache miss runs vendored graphify, whose status lines must reach stderr, never the JSON on stdout."""
    import os
    import sys

    p = subprocess.run([sys.executable, "-m", "src.lab", "graph", "--repo", "click"], cwd=ROOT, capture_output=True,
                       text=True, timeout=600, env={**os.environ, "TMPDIR": str(tmp_path)})   # empty LAB_ROOT: no cached graph
    assert p.returncode == 0, p.stderr[-2000:]
    view = json.loads(p.stdout)
    assert view["repo"] == "click" and view["counts"]["nodes"]["test"] > 0
    assert "[graphify] Deduplicated" in p.stderr
