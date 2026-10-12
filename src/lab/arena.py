"""Strategy arena (Live Lab, D-65): how other approaches would have selected tests on this change, against ours.

Every strategy is an approach re-implemented here and scored on the SAME measured full-suite results of the current
run; none is run separately and none is a vendor's product:

    retest-all      every test, alphabetical                          Jenkins / GitHub Actions default
    static-rts      tests whose file reaches the change in the graph   STARTS-style static RTS (file level)
    coverage        tests whose recorded coverage at the base commit   the approach Datadog TIA documents
                    touches a changed function
    history         tests ranked by earlier failures in this repo      Develocity / Meta-style predictive selection
    cochange        tests of files that changed together in git        change-impact-analysis proxy (RQ1)
    blastradius     the at-risk files of the E1 ranking, in order      ours

The unit is a test case (one executed item). Recall is failing cases selected / all failing cases. Times are sums of
this run's measured per-case durations. Nothing here calls a model; nothing here is a paper number (D-65).
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from collections import Counter, deque
from pathlib import Path

from src.lab.workspace import LAB_ROOT, git

FAILED = ("failed", "error")
BASIS = "computed from this run's full-suite results; not run separately"
COVERAGE_TIMEOUT_S = 120
HISTORY_DIR = LAB_ROOT / "history"
COVERAGE_DIR = LAB_ROOT / "coverage"
COCHANGE_MAX_COMMITS = 500
COCHANGE_MAX_FILES = 50          # a commit touching more files than this is a bulk change, not evidence of coupling
PLUGIN_DIR = Path(__file__).resolve().parent / "plugin"

STRATEGIES = (
    ("retest-all", "Retest-all", "every test, alphabetical", "Jenkins / GitHub Actions default", False),
    ("static-rts", "Static reachability (RTS)", "tests whose file reaches the change in the code graph", "STARTS-style static RTS", False),
    ("coverage", "Per-test coverage", "tests whose base-commit coverage touches a changed function", "the approach Datadog TIA documents", False),
    ("history", "Failure history", "tests ranked by earlier failures in this repo", "Develocity / Meta-style predictive selection", False),
    ("cochange", "Co-change", "tests of files that changed together in git history", "change-impact-analysis proxy (RQ1)", False),
    ("blastradius", "BlastRadius", "E1 ranking + graph: the at-risk test files, in rank order", "ours", True),
)


def case_file(r: dict) -> str:
    """The file a test case was collected from (the node id, not the canonical id's defining file)."""
    return (r.get("nodeid") or r["id"]).split("::")[0]


def score(results: list[dict], order: list[int] | None, *, status: str = "ok", note: str = "") -> dict:
    """Score a selection given as indices into `results`, in the strategy's own order (None: unavailable)."""
    n = len(results)
    failing = [i for i, r in enumerate(results) if r["outcome"] in FAILED]
    if order is None:
        return {"status": "unavailable", "note": note, "selected": 0, "pct": 0.0, "caught": 0, "n_failing": len(failing),
                "recall": None, "first_failure_position": None, "first_failure_ms": None, "ci_ms": 0.0, "missed": []}
    sel = set(order)
    ms = [float(r["duration_s"]) * 1000 for r in results]
    ff = next((k for k, i in enumerate(order) if results[i]["outcome"] in FAILED), None)
    caught = sum(1 for i in failing if i in sel)
    missed = list(dict.fromkeys(results[i]["id"] for i in failing if i not in sel))
    return {"status": status, "note": note, "selected": len(order), "pct": round(100.0 * len(order) / n, 2) if n else 0.0,
            "caught": caught, "n_failing": len(failing), "recall": round(caught / len(failing), 4) if failing else None,
            "first_failure_position": ff + 1 if ff is not None else None,
            "first_failure_ms": round(sum(ms[i] for i in order[: ff + 1]), 1) if ff is not None else None,
            "ci_ms": round(sum(ms[i] for i in order), 1), "missed": missed}


def alphabetical(results: list[dict], keep=lambda i: True) -> list[int]:
    return sorted((i for i in range(len(results)) if keep(i)), key=lambda i: (results[i]["id"], i))


# -- static reachability ---------------------------------------------------------------------------------------------
def reaching_test_files(view: dict, changed: list[str]) -> set[str]:
    """Test files whose file node reaches a changed node along directed graph edges (caller -> callee, importer ->
    imported, container -> member): the file-level dependency closure STARTS computes for test classes."""
    radj: dict[str, list[str]] = {}
    for e in view["edges"]:
        radj.setdefault(e["target"], []).append(e["source"])
    seen = set(changed)
    q = deque(changed)
    while q:                                       # reverse BFS from the change: everything that depends on it
        cur = q.popleft()
        for src in radj.get(cur, ()):
            if src not in seen:
                seen.add(src)
                q.append(src)
    return {n["file"] for n in view["nodes"] if n["type"] == "file" and n["id"] in seen and n.get("is_test_file")}


# -- coverage --------------------------------------------------------------------------------------------------------
def _norm(q: str) -> str:
    return q.replace(".<locals>", "")


def run_coverage(repo_dir: Path, base: str, python: str, key: str, timeout: int = COVERAGE_TIMEOUT_S) -> dict:
    """Per-test function coverage at the base commit, recorded once per repository and commit and cached.

    Returns:
        `{"status": "ok", "wall_s", "cached", "n_tests", "n_functions", "tests": {nodeid: {"id", "functions"}}}`,
        or `{"status": "skipped", "reason"}` when the suite is too slow (> `timeout` s) or does not run.
    """
    from src.agents import gitops
    from src.agents.regression import junit_test_id

    cache = COVERAGE_DIR / f"{key}-{base[:12]}.json"
    if cache.exists():
        doc = json.loads(cache.read_text(encoding="utf-8"))
        return {**doc, "cached": True}
    COVERAGE_DIR.mkdir(parents=True, exist_ok=True)
    with gitops.worktree(repo_dir, base) as tree:
        out = tree.parent / "coverage.json"
        paths = [str(PLUGIN_DIR), str(tree)] + ([str(tree / "src")] if (tree / "src").is_dir() else [])
        env = {**os.environ, "PYTHONPATH": os.pathsep.join(paths), "PYTHONDONTWRITEBYTECODE": "1",
               "BR_LAB_COV": str(out), "BR_LAB_COV_ROOT": str(tree)}
        env.pop("BR_LAB_FD", None)
        t0 = time.perf_counter()
        try:
            subprocess.run([python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "br_cov_plugin"], cwd=tree,
                           env=env, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"status": "skipped", "reason": f"the coverage run exceeded {timeout} s on this repository, so the strategy is skipped"}
        wall = round(time.perf_counter() - t0, 2)
        if not out.exists():
            return {"status": "skipped", "reason": "the coverage run wrote no output (pytest did not start)"}
        raw = json.loads(out.read_text(encoding="utf-8"))["tests"]
    tests = {nid: {"id": junit_test_id(t["file"], t["classname"], t["name"]), "functions": t["functions"]}
             for nid, t in sorted(raw.items())}
    doc = {"status": "ok", "wall_s": wall, "n_tests": len(tests),
           "n_functions": len({(f[0], f[2]) for t in tests.values() for f in t["functions"]}), "tests": tests}
    cache.write_text(json.dumps(doc, separators=(",", ":"), sort_keys=True), encoding="utf-8")
    return {**doc, "cached": False}


def coverage_selection(results: list[dict], cov: dict, changed_fns: list[dict]) -> tuple[list[int], str]:
    """Indices of cases whose recorded functions include a changed function (or, for a module-level change, any
    function of the changed file)."""
    fns = {(d["file"], _norm(d["function"])) for d in changed_fns if d["function"] != "<module>"}
    files = {d["file"] for d in changed_fns if d["function"] == "<module>"}
    by_node = cov["tests"]
    keep = []
    for i, r in enumerate(results):
        t = by_node.get(r.get("nodeid") or "")
        if not t:
            continue
        hit = any((f[0], _norm(f[2])) in fns or f[0] in files for f in t["functions"])
        if hit:
            keep.append(i)
    note = "module-level change: tests covering any function of the changed file" if files and not fns else ""
    return sorted(keep, key=lambda i: (results[i]["id"], i)), note


# -- failure history -------------------------------------------------------------------------------------------------
def history_path(repo_key: str) -> Path:
    return HISTORY_DIR / f"{repo_key}.jsonl"


def read_history(repo_key: str, path: Path | None = None) -> list[dict]:
    """Earlier lab runs of this repository: `{run_id, date, change, failed: [test ids], n_cases}` per line."""
    p = path or history_path(repo_key)
    if not p.exists():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def append_history(repo_key: str, run: dict, path: Path | None = None) -> None:
    p = path or history_path(repo_key)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(run, sort_keys=True) + "\n")


def history_selection(results: list[dict], runs: list[dict]) -> tuple[list[int] | None, str, str]:
    if not runs:
        return [], "cold-start", "cold start: no history"
    count = Counter(t for r in runs for t in set(r.get("failed", [])))
    keep = [i for i, r in enumerate(results) if count.get(r["id"], 0) > 0]
    note = f"history: {len(runs)} earlier run{'s' if len(runs) != 1 else ''}"
    if not keep:
        note += "; no test of this suite failed in them"
    return sorted(keep, key=lambda i: (-count[results[i]["id"]], results[i]["id"], i)), "ok", note


# -- co-change -------------------------------------------------------------------------------------------------------
def cochange_counts(repo_dir: Path, base: str, changed_files: list[str]) -> tuple[Counter, int, str | None]:
    """Test files that changed in the same commit as a changed file, counted over the history before `base`.

    The boundary commit of a shallow clone is skipped (its file list is the whole tree, not a change), and so is any
    commit touching more than COCHANGE_MAX_FILES files.
    """
    from src.parse.changeset import is_conventional_test_file

    shallow = set()
    sf = Path(git(repo_dir, "rev-parse", "--git-dir"))
    sf = (repo_dir / sf if not sf.is_absolute() else sf) / "shallow"
    if sf.exists():
        shallow = {x.strip() for x in sf.read_text().splitlines() if x.strip()}
    log = git(repo_dir, "log", f"-{COCHANGE_MAX_COMMITS}", "--format=%x00%H %P", "--name-only", base, timeout=60)
    counts: Counter = Counter()
    used = 0
    for block in log.split("\x00"):
        lines = [x for x in block.strip().splitlines() if x.strip()]
        if not lines:
            continue
        shas = lines[0].split()
        files = lines[1:]
        if shas[0] in shallow or len(shas) == 1 or len(files) > COCHANGE_MAX_FILES:
            continue                                # boundary of a shallow clone, a root commit, or a bulk commit
        used += 1
        if set(files) & set(changed_files):
            for f in files:
                if is_conventional_test_file(f):
                    counts[f] += 1
    if used == 0:
        return counts, 0, "no usable git history before the base (a pinned snapshot or shallow clone with one commit)"
    return counts, used, None


# -- the arena -------------------------------------------------------------------------------------------------------
def takeaway(strats: list[dict], n_cases: int, n_failing: int) -> str:
    """One sentence generated from the numbers (never written by hand)."""
    ours = next(s for s in strats if s["ours"])
    ok = [s for s in strats if s["status"] == "ok" and not s["ours"] and s["id"] != "retest-all"]
    if n_failing == 0:
        return (f"No test failed on this change, so no strategy had anything to catch; they differ only in cost: "
                f"BlastRadius would run {ours['pct']:.0f}% of the {n_cases} tests, retest-all 100%.")
    s = (f"BlastRadius ran {ours['pct']:.0f}% of the suite and caught {ours['caught']} of {n_failing} failures"
         + (f", the first at test {ours['first_failure_position']}" if ours["first_failure_position"] else "") + "; ")
    full = sorted([x for x in ok if x["caught"] == n_failing], key=lambda x: x["pct"])
    if full:
        s += f"the cheapest other strategy that caught them all, {full[0]['name'].lower()}, ran {full[0]['pct']:.0f}%"
    else:
        s += "no other selective strategy caught them all"
    worst = [x for x in ok if x["caught"] < n_failing]
    if worst:
        w = min(worst, key=lambda x: (x["caught"], x["pct"]))
        s += f"; {w['name'].lower()} missed {n_failing - w['caught']}"
    cold = [x for x in strats if x["status"] == "cold-start"]
    if cold:
        s += "; failure history had no earlier runs to learn from"
    return s + "."


def compute(results: list[dict], *, order_files: list[str], view: dict, changed_nodes: list[str],
            changed_fns: list[dict], coverage: dict | None, history: list[dict], cochange: tuple[Counter, int, str | None],
            ) -> dict:
    """The arena for one run. `results` are the run's executed cases, in execution order."""
    n = len(results)
    out = []
    for sid, name, what, source, ours in STRATEGIES:
        meta = {"id": sid, "name": name, "what": what, "source": source, "ours": ours}
        if sid == "retest-all":
            row = score(results, alphabetical(results))
        elif sid == "static-rts":
            if not view.get("nodes") or not changed_nodes:
                row = score(results, None, note="unavailable: no graph, or the change maps to no graph node")
            else:
                files = reaching_test_files(view, changed_nodes)
                row = score(results, alphabetical(results, lambda i: case_file(results[i]) in files),
                            note=f"{len(files)} test file(s) reach the change")
        elif sid == "coverage":
            if not coverage or coverage.get("status") != "ok":
                row = score(results, None, note=(coverage or {}).get("reason", "coverage was not recorded"))
            else:
                sel, note = coverage_selection(results, coverage, changed_fns)
                row = score(results, sel, note=note)
        elif sid == "history":
            sel, st, note = history_selection(results, history)
            row = score(results, sel, status=st, note=note)
        elif sid == "cochange":
            counts, used, reason = cochange
            if reason:
                row = score(results, None, note=reason)
            else:
                sel = sorted((i for i in range(n) if counts.get(case_file(results[i]), 0) > 0),
                             key=lambda i: (-counts[case_file(results[i])], results[i]["id"], i))
                row = score(results, sel, note=f"{used} commits of history; {len(counts)} test file(s) co-changed")
        else:
            rank = {f: k for k, f in enumerate(order_files)}
            row = score(results, [i for i in range(n) if case_file(results[i]) in rank],
                        note=f"{len(order_files)} at-risk test file(s), in execution order")
        out.append({**meta, **row})
    n_failing = sum(1 for r in results if r["outcome"] in FAILED)
    return {"basis": BASIS, "unit": "test cases (one executed item each)", "n_cases": n, "n_failing": n_failing,
            "suite_ms": round(sum(float(r["duration_s"]) * 1000 for r in results), 1), "strategies": out,
            "takeaway": takeaway(out, n, n_failing)}
