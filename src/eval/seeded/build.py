"""Build BR-Seeded (E3): PR-shaped changes with one seeded bug, verified by running the suites.

`make seeded` (network: clones and installs; NOT part of `make tables`).

For each repo: pin HEAD, build a venv, run the full suite at the pinned sha (pre-existing
failures are excluded from every later check), enumerate mutations (`mutate.py`), keep a
mutant only if at least one test fails and the run finishes inside the timeout, add 2-3
harmless distractor edits to OTHER source files (verified to leave the suite green), and
sample deterministically (seed 0), stratified by operator.

No LLM. Deterministic given the pinned shas and the host's test timings.
"""

from __future__ import annotations

import ast
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from src.eval.seeded.mutate import OPERATORS, Mutation, apply, find_mutations

ROOT = Path(__file__).resolve().parents[3]
# BR_SEEDED_DIR points replays at a copy (venvs included, with their .pth paths rewritten) so they do not queue behind
# a live run on the same working trees.
SEEDED = Path(os.environ["BR_SEEDED_DIR"]) if os.environ.get("BR_SEEDED_DIR") else ROOT / "data" / "seeded"
REPOS = SEEDED / "repos"
VENVS = SEEDED / "venvs"
OUT = ROOT / "eval" / "seeded"
SUITE_TIMEOUT_S = 120
PER_REPO = 22
OUTPUT_CAP = 4000
MAX_LISTED_FAILURES = 20
SEED = 0

SPECS = [
    {"slug": "shopcart", "local": "src/agents/demo/sample_repo", "src_dirs": ["shopcart"], "installs": ["pytest"]},
    {"slug": "itsdangerous", "url": "https://github.com/pallets/itsdangerous", "src_dirs": ["src/itsdangerous"],
     "installs": ["-e", ".", "pytest", "freezegun"]},
    {"slug": "markupsafe", "url": "https://github.com/pallets/markupsafe", "src_dirs": ["src/markupsafe"],
     "installs": ["-e", ".", "pytest"]},
    # more-itertools was tried first and rejected: its full suite takes 79 s (limit: 60 s offline).
    {"slug": "click", "url": "https://github.com/pallets/click", "src_dirs": ["src/click"],
     "installs": ["-e", ".", "pytest"]},
]


@dataclass
class Suite:
    """Result of one full-suite run."""

    finished: bool
    wall_s: float
    results: dict[str, tuple[str, str]] = field(default_factory=dict)  # test_id -> (outcome, output)

    @property
    def failing(self) -> dict[str, str]:
        return {t: o for t, (s, o) in self.results.items() if s in ("failed", "error")}


def git(repo: Path, *args: str, check: bool = True) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "br-seeded", "GIT_AUTHOR_EMAIL": "br@example.invalid",
           "GIT_COMMITTER_NAME": "br-seeded", "GIT_COMMITTER_EMAIL": "br@example.invalid",
           "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}
    return subprocess.run(["git", "-C", str(repo), "-c", "core.autocrlf=false", *args], capture_output=True,
                          text=True, check=check, env=env).stdout


def prepare_repo(spec: dict, pins: dict) -> tuple[Path, Path]:
    """Clone (or copy) the repo, pin or verify its sha, and build its venv.

    Returns:
        `(repo_dir, python_executable)`.
    """
    slug = spec["slug"]
    repo = REPOS / slug
    REPOS.mkdir(parents=True, exist_ok=True)
    if not repo.exists():
        if "local" in spec:
            shutil.copytree(ROOT / spec["local"], repo, ignore=shutil.ignore_patterns("__pycache__", "*.pyc",
                                                                                       ".pytest_cache"))
            git(repo, "init", "-q")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "shopcart sample repo")
        else:
            subprocess.run(["git", "clone", "--quiet", "--depth", "1", spec["url"], str(repo)], check=True,
                           env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    sha = git(repo, "rev-parse", "HEAD").strip()
    if slug in pins and pins[slug]["sha"] != sha:
        raise SystemExit(f"{slug}: HEAD {sha} != pinned {pins[slug]['sha']}")
    venv = VENVS / slug
    py = venv / "bin" / "python"
    if not py.exists():
        VENVS.mkdir(parents=True, exist_ok=True)
        subprocess.run(["uv", "venv", "-q", "--python", "3.11", str(venv)], check=True)
        args = [a if a != "." else str(repo) for a in spec["installs"]]
        subprocess.run(["uv", "pip", "install", "-q", "--python", str(py), *args], check=True)
    pins.setdefault(slug, {"url": spec.get("url", spec.get("local")), "sha": sha, "installs": spec["installs"],
                           "src_dirs": spec["src_dirs"], "python": "3.11"})
    return repo, py


def run_suite(repo: Path, py: Path, timeout: int = SUITE_TIMEOUT_S) -> Suite:
    """Run the whole test suite once and parse JUnit XML."""
    with tempfile.TemporaryDirectory() as td:
        xml_path = Path(td) / "r.xml"
        cmd = [str(py), "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={xml_path}",
               "-o", "junit_family=xunit1", "--no-header"]
        t0 = time.time()
        try:
            subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=timeout,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        except subprocess.TimeoutExpired:
            return Suite(False, time.time() - t0)
        wall = time.time() - t0
        if not xml_path.exists():
            return Suite(False, wall)
        out: dict[str, tuple[str, str]] = {}
        for tc in ET.parse(xml_path).getroot().iter("testcase"):
            tid = f"{tc.get('classname', '')}::{tc.get('name', '')}"
            bad = tc.find("failure")
            err = tc.find("error")
            skip = tc.find("skipped")
            node = bad if bad is not None else err
            if node is not None:
                body = (node.get("message") or "") + "\n" + (node.text or "")
                out[tid] = ("failed" if bad is not None else "error", body.strip()[:OUTPUT_CAP])
            else:
                out[tid] = ("skipped" if skip is not None else "passed", "")
        return Suite(True, wall, out)


def source_files(repo: Path, spec: dict) -> list[str]:
    """Non-test Python source files under the spec's source dirs, repo-relative."""
    files = []
    for d in spec["src_dirs"]:
        for p in sorted((repo / d).rglob("*.py")):
            rel = p.relative_to(repo).as_posix()
            if "/tests/" in rel or "/test_" in rel or rel.endswith("conftest.py") or "/_vendor/" in rel:
                continue
            files.append(rel)
    return files


# ---- harmless distractors ------------------------------------------------------------------
def distractor_edits(source: str, rng: random.Random) -> list[tuple[str, int, str, str]]:
    """Candidate harmless edits of one file as `(kind, start, old_text, new_text)` span replacements."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    lines = source.splitlines(keepends=True)
    starts = [0]
    for ln in lines:
        starts.append(starts[-1] + len(ln))
    out = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            first = min([node.lineno] + [d.lineno for d in node.decorator_list])
            out.append(("COMMENT", starts[first - 1], "", "# reviewed: no functional change intended\n"))
    for node in ast.walk(tree):
        if (isinstance(node, ast.FunctionDef) and node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(getattr(node.body[0], "value", None), ast.Constant)
                and isinstance(node.body[0].value.value, str) and node.body[0].lineno == node.body[0].end_lineno):
            ex = node.body[0]
            line = lines[ex.lineno - 1]
            if line.rstrip().endswith('."""'):
                idx = starts[ex.lineno - 1] + line.rstrip().rindex('"""')
                out.append(("DOCSTRING", idx, "", " Behaviour is unchanged."))
        if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, (ast.Name, ast.Attribute)) and node.lineno == node.end_lineno
                and node.value.lineno == node.value.end_lineno):
            line = lines[node.lineno - 1]
            col = len(line.encode()[:node.value.col_offset].decode())
            end = len(line.encode()[:node.value.end_col_offset].decode())
            s = starts[node.lineno - 1]
            out.append(("PARENS", s + col, line[col:end], f"({line[col:end]})"))
    rng.shuffle(out)
    return out


def apply_edit(source: str, edit: tuple[str, int, str, str]) -> str:
    _, start, old, new = edit
    assert source[start:start + len(old)] == old
    return source[:start] + new + source[start + len(old):]


# ---- build ---------------------------------------------------------------------------------
def build_repo(spec: dict, pins: dict, rng_seed: int = SEED) -> list[dict]:
    """All accepted tasks for one repo (up to PER_REPO, stratified by operator)."""
    repo, py = prepare_repo(spec, pins)
    base = run_suite(repo, py)
    if not base.finished:
        raise SystemExit(f"{spec['slug']}: baseline suite did not finish in {SUITE_TIMEOUT_S}s")
    preexisting = set(base.failing)
    print(f"[{spec['slug']}] {len(base.results)} tests in {base.wall_s:.1f}s, {len(preexisting)} pre-existing failures",
          flush=True)
    files = source_files(repo, spec)
    originals = {f: (repo / f).read_text(encoding="utf-8") for f in files}
    cands: dict[str, list[tuple[str, Mutation]]] = defaultdict(list)
    rng = random.Random(f"{spec['slug']}-{rng_seed}")
    for f in files:
        for m in find_mutations(originals[f]):
            if m.function != "<module>":
                cands[m.operator].append((f, m))
    for op in cands:
        cands[op].sort(key=lambda fm: (fm[0], fm[1].start))
        rng.shuffle(cands[op])
    tasks: list[dict] = []
    per_op = Counter()
    tried = Counter()
    ops = [o for o in OPERATORS if cands.get(o)]
    pools = {o: list(cands[o]) for o in ops}
    budget = PER_REPO * 8  # screening runs, so a repo with few killable mutants still terminates
    while len(tasks) < PER_REPO and any(pools.values()) and sum(tried.values()) < budget:
        for op in ops:
            if len(tasks) >= PER_REPO:
                break
            if not pools[op]:
                continue
            f, m = pools[op].pop()
            tried[op] += 1
            (repo / f).write_text(apply(originals[f], m), encoding="utf-8")
            try:
                res = run_suite(repo, py)
            finally:
                (repo / f).write_text(originals[f], encoding="utf-8")
            new_fail = {t: o for t, o in res.failing.items() if t not in preexisting}
            if not res.finished or not new_fail:
                continue
            task = assemble(spec, repo, py, f, m, originals, preexisting, len(tasks), per_op[op], random.Random(
                f"{spec['slug']}-{op}-{per_op[op]}-{rng_seed}"))
            if task:
                per_op[op] += 1
                tasks.append(task)
                print(f"[{spec['slug']}] + {task['task_id']} ({len(task['failing_tests'])} failing)", flush=True)
    print(f"[{spec['slug']}] screened {sum(tried.values())} mutants, kept {len(tasks)}", flush=True)
    git(repo, "checkout", "--", ".")
    return tasks


def assemble(spec, repo: Path, py: Path, f: str, m: Mutation, originals: dict, preexisting: set, n: int,
             k: int, rng: random.Random) -> dict | None:
    """Add distractors to a surviving mutant, verify, and produce the task record."""
    mutated = apply(originals[f], m)
    # distractors: other files only; verified green on their own
    others = [p for p in originals if p != f]
    rng.shuffle(others)
    chosen: dict[str, str] = {}
    for p in others:
        if len(chosen) >= 3:
            break
        edits = distractor_edits(originals[p], rng)
        if not edits:
            continue
        chosen[p] = apply_edit(originals[p], edits[0])
    for p, txt in chosen.items():
        (repo / p).write_text(txt, encoding="utf-8")
    try:
        green = run_suite(repo, py)
        if chosen and (not green.finished or any(t not in preexisting for t in green.failing)):
            # a distractor was not harmless: drop them all rather than guess which one
            for p in chosen:
                (repo / p).write_text(originals[p], encoding="utf-8")
            chosen = {}
        distractor_patch = git(repo, "diff", "--no-color", "-U3")
        for p in chosen:
            (repo / p).write_text(originals[p], encoding="utf-8")
        # mutant alone
        (repo / f).write_text(mutated, encoding="utf-8")
        mutant_patch = git(repo, "diff", "--no-color", "-U3")
        for p, txt in chosen.items():
            (repo / p).write_text(txt, encoding="utf-8")
        pr_diff = git(repo, "diff", "--no-color", "-U3")
        res = run_suite(repo, py)
    finally:
        for p in list(originals):
            (repo / p).write_text(originals[p], encoding="utf-8")
    new_fail = {t: o for t, o in res.failing.items() if t not in preexisting}
    if not res.finished or not new_fail:
        return None
    if sum(1 for ln in mutant_patch.splitlines() if ln.startswith("@@")) != 1:
        return None
    line_idx = m.line - 1
    src_lines = originals[f].splitlines()
    mut_lines = mutated.splitlines()
    listed = [{"test_id": t, "output": o[:OUTPUT_CAP]} for t, o in sorted(new_fail.items())[:MAX_LISTED_FAILURES]]
    return {
        "task_id": f"{spec['slug']}-{m.operator}-{k:02d}", "repo": spec["slug"],
        "base_sha": git(repo, "rev-parse", "HEAD").strip(), "operator": m.operator,
        "mutant_patch": mutant_patch, "distractor_patch": distractor_patch, "pr_diff": pr_diff,
        "failing_tests": listed, "n_failing": len(new_fail),
        "gt_file": f, "gt_function": m.function, "gt_line": m.line,
        "original_snippet": src_lines[line_idx], "mutated_snippet": mut_lines[line_idx],
        "distractor_files": sorted(chosen), "preexisting_failures": sorted(preexisting),
    }


def main(argv: list[str] | None = None) -> int:
    only = set(argv or sys.argv[1:])
    OUT.mkdir(parents=True, exist_ok=True)
    pins_path = OUT / "repos.json"
    pins = json.loads(pins_path.read_text()) if pins_path.exists() else {}
    all_tasks: list[dict] = []
    for spec in SPECS:
        if only and spec["slug"] not in only:
            continue
        all_tasks += build_repo(spec, pins)
    pins_path.write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (OUT / "tasks.jsonl").open("w", encoding="utf-8") as fh:
        for t in all_tasks:
            fh.write(json.dumps(t, sort_keys=True) + "\n")
    table = defaultdict(Counter)
    for t in all_tasks:
        table[t["repo"]][t["operator"]] += 1
    ops = [o for o in OPERATORS]
    print("\nrepo".ljust(16) + "".join(o.rjust(13) for o in ops) + "total".rjust(8))
    for repo, c in table.items():
        print(repo.ljust(15) + "".join(str(c[o]).rjust(13) for o in ops) + str(sum(c.values())).rjust(8))
    print(f"{len(all_tasks)} tasks written to {OUT / 'tasks.jsonl'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
