"""BR-Seeded, hard-distractor variant (E3, D-60 preregistration): the SAME 70 mutants plus 4-6 no-op edits
inside functions the failing tests execute.

The standard variant puts its distractors in unrelated files, so searching the diff is nearly enough to find the
bug. Here the diff also holds no-op edits inside the code paths of the failing tests, so "touched by the diff" no
longer isolates the bug. Edits are minimal source-span text edits (no `ast.unparse`):

    COMMENT  a comment line inserted before the first statement of the function body (docstring skipped)
    PARENS   redundant parentheses around a `return` expression or a single-line assignment's right-hand side

Candidates are taken in this order, never the mutated function itself, and only if a failing test executes them:
(1) functions of the mutated file, (2) functions named in the failing tests' tracebacks, (3) other functions of the
same package. A distractor is kept only if, with the whole set applied, the full suite is green without the mutant
and the mutant fails exactly the same tests as the mutant alone.

`python -m src.eval.seeded.hard` writes `eval/seeded/tasks_hard.jsonl` (network not needed once `make seeded` ran).
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from src.eval.seeded.build import OUT, REPOS, SEEDED, VENVS, git, run_suite, source_files
from src.eval.seeded.validate import head_state

MIN_D, MAX_D = 4, 6
_LOC = re.compile(r"([\w./\-]+\.py):(\d+)")


@dataclass(frozen=True)
class Func:
    file: str
    qualname: str
    start: int   # first body line after the docstring
    end: int
    first_stmt_line: int
    first_stmt_col: int


def functions_of(path: str, text: str) -> list[Func]:
    """Top-level functions and methods with their body span (docstring excluded)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    out: list[Func] = []

    def visit(node: ast.AST, prefix: str) -> None:
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                body = list(ch.body)
                if (body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    body = body[1:]
                if body:
                    out.append(Func(path, f"{prefix}{ch.name}", ch.lineno, ch.end_lineno, body[0].lineno,
                                    body[0].col_offset))
            elif isinstance(ch, ast.ClassDef):
                visit(ch, f"{prefix}{ch.name}.")

    visit(tree, "")
    return out


Edit = tuple[str, int, int, str, str]  # (kind, 1-based line, char column, old text, new text)


def noop_edit(text: str, fn: Func) -> Edit | None:
    """One semantic no-op edit inside `fn`, or None if none applies. Positions are line and column, so the
    same edit applies to the head-state text and to the unmutated text (a one-line mutant does not move lines)."""
    lines = text.splitlines(keepends=True)
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if getattr(node, "lineno", 0) and fn.start <= node.lineno <= fn.end and isinstance(node, (ast.Return, ast.Assign)):
            val = node.value
            if (val is not None and node.lineno == node.end_lineno and val.lineno == val.end_lineno
                    and not isinstance(val, (ast.Constant, ast.Tuple, ast.GeneratorExp, ast.Starred, ast.Yield,
                                             ast.YieldFrom, ast.Await, ast.NamedExpr))):
                line = lines[val.lineno - 1]
                col = len(line.encode()[:val.col_offset].decode())
                end = len(line.encode()[:val.end_col_offset].decode())
                old = line[col:end]
                if old and not (old.startswith("(") and old.endswith(")")):
                    return ("PARENS", val.lineno, col, old, f"({old})")
    ln = fn.first_stmt_line
    indent = " " * fn.first_stmt_col
    if ln <= len(lines) and lines[ln - 1].startswith(indent):
        return ("COMMENT", ln, 0, "", f"{indent}# reviewed: no functional change intended\n")
    return None


def apply_edits(text: str, edits: list[Edit]) -> str:
    """Apply edits bottom-up so earlier line numbers stay valid."""
    lines = text.splitlines(keepends=True)
    for kind, ln, col, old, new in sorted(edits, key=lambda e: (e[1], e[2]), reverse=True):
        if kind == "COMMENT":
            lines.insert(ln - 1, new)
        else:
            line = lines[ln - 1]
            assert line[col:col + len(old)] == old, "edit does not match the text"
            lines[ln - 1] = line[:col] + new + line[col + len(old):]
    return "".join(lines)


def suite_outcome_same(repo: Path, py: Path, old: dict[str, str], new: dict[str, str], expected_fail: set[str],
                       preexisting: set[str]) -> bool:
    """Write `new` over the working tree, run the full suite, restore `old`; True iff the failing set (minus
    pre-existing failures) equals `expected_fail`. This is the gate every distractor must pass."""
    try:
        for f, t in new.items():
            (repo / f).write_text(t, encoding="utf-8")
        r = run_suite(repo, py)
        return r.finished and (set(r.failing) - preexisting) == expected_fail
    finally:
        for f, t in old.items():
            (repo / f).write_text(t, encoding="utf-8")


def _node_id(test_id: str, files: set[str]) -> str | None:
    """pytest node id of a JUnit `classname::name`; leading directories the rootdir added are skipped."""
    cls, _, name = test_id.partition("::")
    parts = cls.split(".")
    for i in range(len(parts)):
        for k in range(len(parts), i, -1):
            cand = "/".join(parts[i:k]) + ".py"
            if cand in files:
                return "::".join([cand, *parts[k:], name])
    return None


def executed_lines(repo: Path, py: Path, node_ids: list[str]) -> dict[str, set[int]]:
    """Lines executed by exactly those tests (coverage run inside the repo's own venv)."""
    with tempfile.TemporaryDirectory() as td:
        data = Path(td) / ".cov"
        rc = Path(td) / "empty.rc"  # the repo's own coverage config (source = [...]) would hide the package
        rc.write_text("[run]\n")
        subprocess.run([str(py), "-m", "coverage", "run", f"--rcfile={rc}", f"--data-file={data}", f"--include={repo.resolve()}/*", "-m", "pytest", "-q",
                        "-p", "no:cacheprovider", *node_ids], cwd=repo, capture_output=True, text=True, timeout=300)
        out = Path(td) / "cov.json"
        subprocess.run([str(py), "-m", "coverage", "json", f"--rcfile={rc}", f"--data-file={data}", "-o", str(out)], cwd=repo,
                       capture_output=True, text=True)
        if not out.exists():
            return {}
        d = json.loads(out.read_text())
    res: dict[str, set[int]] = {}
    for f, v in d.get("files", {}).items():
        res[Path(f).as_posix()] = set(v.get("executed_lines", []))
    return res


def ensure_coverage(slug: str) -> Path:
    py = VENVS / slug / "bin" / "python"
    chk = subprocess.run([str(py), "-c", "import coverage"], capture_output=True)
    if chk.returncode != 0:
        subprocess.run(["uv", "pip", "install", "-q", "--python", str(py), "coverage"], check=True)
    return py


def build_task(task: dict, pins: dict) -> dict:
    slug = task["repo"]
    repo = REPOS / slug
    py = ensure_coverage(slug)
    src_dirs = pins[slug]["src_dirs"]
    with head_state(repo, task["pr_diff"]):
        srcs = source_files(repo, {"src_dirs": src_dirs})
        tracked = set(subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True).stdout.split())
        nodes = [n for n in (_node_id(t["test_id"], tracked) for t in task["failing_tests"]) if n]
        cov = executed_lines(repo, py, nodes) if nodes else {}

        def abs_key(f: str) -> str | None:
            for k in cov:
                if k.endswith(f) or f.endswith(k):
                    return k
            return None

        texts = {f: (repo / f).read_text(encoding="utf-8") for f in srcs}
        funcs = {f: functions_of(f, t) for f, t in texts.items()}

        def executed(fn: Func) -> bool:
            k = abs_key(fn.file)
            return bool(k) and any(fn.start <= ln <= fn.end for ln in cov[k])

        gt = next((x for x in funcs.get(task["gt_file"], []) if x.qualname == task["gt_function"]), None)
        trace_hits: set[tuple[str, str]] = set()
        for t in task["failing_tests"]:
            for path, ln in _LOC.findall(t.get("output", "")):
                for f in srcs:
                    if f.endswith(path) or path.endswith(f):
                        for fn in funcs[f]:
                            if fn.start <= int(ln) <= fn.end:
                                trace_hits.add((fn.file, fn.qualname))
        order: list[Func] = []
        same = [fn for fn in funcs.get(task["gt_file"], []) if fn != gt]
        traced = [fn for f in srcs for fn in funcs[f] if (fn.file, fn.qualname) in trace_hits and fn != gt]
        pkg = str(Path(task["gt_file"]).parent)
        module = [fn for f in srcs if str(Path(f).parent) == pkg for fn in funcs[f] if fn != gt]
        for fn in same + traced + module:
            if fn not in order and (fn.file, fn.qualname) != (task["gt_file"], task["gt_function"]) and executed(fn):
                order.append(fn)
        # one edit per function (functions never overlap), never inside the mutated line
        chosen: list[tuple[Func, Edit]] = []
        for fn in order:
            if len(chosen) >= MAX_D:
                break
            if fn.file == task["gt_file"] and fn.start <= task["gt_line"] <= fn.end:
                continue
            e = noop_edit(texts[fn.file], fn)
            if e is not None:
                chosen.append((fn, e))
        preexisting = set(task["preexisting_failures"])
        mutant_fail = set(run_suite(repo, py).failing) - preexisting  # head state: mutant + old distractors
        orig_line = task["original_snippet"]

        def with_edits(items: list[tuple[Func, Edit]], revert_mutant: bool) -> dict[str, str]:
            cur = dict(texts)
            if revert_mutant:
                ls = cur[task["gt_file"]].splitlines(keepends=True)
                ls[task["gt_line"] - 1] = orig_line + ("\n" if ls[task["gt_line"] - 1].endswith("\n") else "")
                cur[task["gt_file"]] = "".join(ls)
                # the old distractors stay (they are no-ops); only the mutant is reverted
            by_file: dict[str, list[Edit]] = {}
            for fn, e in items:
                by_file.setdefault(fn.file, []).append(e)
            return {f: apply_edits(t, by_file.get(f, [])) for f, t in cur.items()}

        def ok(items: list[tuple[Func, Edit]]) -> bool:
            return (suite_outcome_same(repo, py, texts, with_edits(items, False), mutant_fail, preexisting)
                    and suite_outcome_same(repo, py, texts, with_edits(items, True), set(), preexisting))

        kept = list(chosen)
        if kept and not ok(kept):
            kept = [it for it in chosen if ok([it])]
            if kept and not ok(kept):
                kept = kept[:1]
        final = with_edits(kept, False)
        for f, t in final.items():
            (repo / f).write_text(t, encoding="utf-8")
        hard_diff = git(repo, "diff", "--no-color", "-U3")
        for f, t in texts.items():
            (repo / f).write_text(t, encoding="utf-8")
    return {**{k: v for k, v in task.items() if k != "pr_diff"}, "variant": "hard", "pr_diff": hard_diff,
            "hard_distractors": [{"file": fn.file, "function": fn.qualname, "kind": e[0], "line": e[1]} for fn, e in kept],
            "n_hard_distractors": len(kept), "easy_pr_diff": task["pr_diff"]}


def main() -> int:
    tasks = [json.loads(ln) for ln in (OUT / "tasks.jsonl").read_text().splitlines() if ln.strip()]
    pins = json.loads((OUT / "repos.json").read_text())
    only = set(sys.argv[1:])
    out = []
    for t in tasks:
        if only and t["repo"] not in only:
            continue
        h = build_task(t, pins)
        out.append(h)
        print(f"{h['task_id']}: {h['n_hard_distractors']} hard distractors", flush=True)
    with (OUT / "tasks_hard.jsonl").open("w", encoding="utf-8") as fh:
        for h in out:
            fh.write(json.dumps(h, sort_keys=True) + "\n")
    ns = sorted(h["n_hard_distractors"] for h in out)
    if ns:
        print(f"distractors per task: min {ns[0]} / median {ns[len(ns) // 2]} / max {ns[-1]}; "
              f">= {MIN_D}: {sum(1 for n in ns if n >= MIN_D)} of {len(ns)} tasks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
