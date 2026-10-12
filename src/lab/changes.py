"""Change sources of a lab run, each producing a commit on top of the base commit in the scratch workspace.

    seeded task      a BR-Seeded task's `pr_diff` (standard) or the hard variant's `pr_diff` with its decoy edits
    inject a bug     one mutation operator applied to one function (`src.eval.seeded.mutate`)
    custom edit      the full new text of one file
"""

from __future__ import annotations

import difflib
import json
from dataclasses import dataclass, field
from pathlib import Path

from src.eval.seeded import mutate
from src.lab.workspace import Workspace, git

ROOT = Path(__file__).resolve().parents[2]
TASK_FILES = {"standard": ROOT / "eval" / "seeded" / "tasks.jsonl", "hard": ROOT / "eval" / "seeded" / "tasks_hard.jsonl"}


@dataclass
class Change:
    """A change applied as one commit."""

    source: dict
    base: str
    head: str
    diff: str
    changed_files: list[str]
    base_sources: dict[str, str] = field(default_factory=dict)   # changed path -> text at the base commit
    note: str = ""


def load_task(task_id: str, variant: str = "standard") -> dict:
    """One BR-Seeded task (`variant` picks tasks.jsonl or tasks_hard.jsonl)."""
    path = TASK_FILES[variant]
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln.strip():
            t = json.loads(ln)
            if t["task_id"] == task_id:
                return t
    raise KeyError(f"{task_id} not found in {path.name}")


def list_tasks(repo: str | None = None) -> list[dict]:
    """Task ids with their repo and operator, for both variants (the hard tasks carry their decoy count)."""
    out = []
    for variant, path in TASK_FILES.items():
        for ln in path.read_text(encoding="utf-8").splitlines():
            if ln.strip():
                t = json.loads(ln)
                if repo is None or t["repo"] == repo:
                    out.append({"task_id": t["task_id"], "repo": t["repo"], "operator": t["operator"],
                                "variant": variant, "gt_file": t["gt_file"], "gt_function": t["gt_function"],
                                "n_decoys": t.get("n_hard_distractors", 0) if variant == "hard" else
                                len(t.get("distractor_files", []))})
    return out


def mutations_of(source: str) -> list[dict]:
    """Every mutation applicable to a Python source text, grouped by the function it sits in."""
    by_fn: dict[str, list[dict]] = {}
    starts = [0]
    for ln in source.splitlines(keepends=True):
        starts.append(starts[-1] + len(ln))
    for m in mutate.find_mutations(source):
        by_fn.setdefault(m.function, []).append({"operator": m.operator, "line": m.line, "col": m.start - starts[m.line - 1],
                                                 "old": m.old, "new": m.new})
    return [{"function": f, "mutations": ms} for f, ms in by_fn.items()]


def _commit(ws: Workspace, message: str) -> str:
    git(ws.repo_dir, "add", "-u")
    git(ws.repo_dir, "commit", "-q", "-m", message)
    return git(ws.repo_dir, "rev-parse", "HEAD")


def _finish(ws: Workspace, source: dict, base: str, message: str) -> Change:
    head = _commit(ws, message)
    diff = git(ws.repo_dir, "diff", f"{base}", head)
    files = [f for f in git(ws.repo_dir, "diff", "--name-only", base, head).splitlines() if f]
    srcs = {}
    for f in files:
        try:
            srcs[f] = git(ws.repo_dir, "show", f"{base}:{f}")
        except RuntimeError:
            srcs[f] = ""
    return Change(source, base, head, diff + "\n" if diff else "", files, srcs)


def apply_task(ws: Workspace, task_id: str, variant: str = "standard") -> Change:
    """Apply a seeded task's change. Raises when its diff does not apply to the pinned base."""
    t = load_task(task_id, variant)
    if t["repo"] != ws.name:
        raise ValueError(f"task {task_id} belongs to {t['repo']}, not {ws.name}")
    p = _apply_patch(ws, t["pr_diff"])
    if p:
        raise RuntimeError(f"the task's diff does not apply: {p}")
    ch = _finish(ws, {"kind": "seeded-task", "task_id": task_id, "variant": variant, "operator": t["operator"],
                      "ground_truth": {"file": t["gt_file"], "function": t["gt_function"], "line": t["gt_line"]},
                      "n_decoys": t.get("n_hard_distractors", len(t.get("distractor_files", [])))},
                 ws.base, f"change: seeded task {task_id}")
    return ch


def _apply_patch(ws: Workspace, diff: str) -> str:
    import subprocess

    p = subprocess.run(["git", "-C", str(ws.repo_dir), "apply", "--whitespace=nowarn", "-"], input=diff,
                       capture_output=True, text=True, timeout=60)
    return "" if p.returncode == 0 else (p.stderr or p.stdout).strip()[:300]


def inject_bug(ws: Workspace, file: str, function: str, operator: str, line: int | None = None) -> Change:
    """Apply one mutation of `operator` inside `function` of `file`.

    Raises:
        ValueError: When the file is not Python, or the function has no such operator (the message lists what it has).
    """
    path = ws.repo_dir / file
    if ".." in Path(file).parts or not path.is_file() or not file.endswith(".py"):
        raise ValueError(f"{file} is not a Python file of the repository")
    text = path.read_text(encoding="utf-8")
    cands = [m for m in mutate.find_mutations(text) if m.function == function and m.operator == operator
             and (line is None or m.line == line)]
    if not cands:
        have = sorted({f"{m.operator}@{m.line}" for m in mutate.find_mutations(text) if m.function == function})
        raise ValueError(f"no {operator} mutation in {function} of {file}; available: {', '.join(have) or 'none'}")
    m = cands[0]
    path.write_text(mutate.apply(text, m), encoding="utf-8")
    return _finish(ws, {"kind": "inject", "file": file, "function": function, "operator": operator, "line": m.line,
                        "old": m.old, "new": m.new}, ws.base, f"change: {operator} in {function}")


def custom_edit(ws: Workspace, file: str, new_text: str) -> Change:
    """Replace one file's text."""
    path = ws.repo_dir / file
    if ".." in Path(file).parts or not path.is_file():
        raise ValueError(f"{file} is not a file of the repository")
    path.write_text(new_text, encoding="utf-8")
    ch = _finish(ws, {"kind": "edit", "file": file}, ws.base, f"change: edit {file}")
    if not ch.diff.strip():
        ch.note = "the edit is identical to the file at the base commit"
    return ch


def unified(before: str, after: str, path: str) -> str:
    """A unified diff of two texts (preview in the editor)."""
    return "\n".join(difflib.unified_diff(before.splitlines(), after.splitlines(), f"a/{path}", f"b/{path}",
                                           lineterm="", n=3)) + "\n"
