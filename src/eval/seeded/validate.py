"""Apply a seeded PR, and judge a candidate patch by the FULL suite (E3's acceptance rule).

A patch is accepted only if every test that passed at the base passes again. Target tests
passing while another test fails is an *overfit* patch and is rejected.
"""

from __future__ import annotations

import contextlib
import fcntl
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

from src.eval.seeded.build import Suite, git, run_suite


@contextlib.contextmanager
def repo_lock(repo: Path) -> Iterator[None]:
    """Hold an exclusive lock on a seeded repo's working tree (blocks until another process lets go).

    `head_state` rewrites the tree (`git checkout -- .`, `git apply`), so two runs on the same repo would read
    each other's half-applied diffs: chunk line ranges from one tree rendered from another, prompts that never
    replay. The lock file lives inside `.git/` so it is never part of the working tree.
    """
    lock = repo / ".git" / "br-seeded.lock"
    with lock.open("a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


@contextlib.contextmanager
def head_state(repo: Path, pr_diff: str) -> Iterator[None]:
    """Apply `pr_diff` to the working tree for the duration of the block, then restore it.

    The repo is locked for the whole block (see :func:`repo_lock`), so concurrent runs take turns.

    Raises:
        RuntimeError: If the diff does not apply to a clean tree.
    """
    with repo_lock(repo):
        git(repo, "checkout", "--", ".")
        p = subprocess.run(["git", "-C", str(repo), "apply", "--whitespace=nowarn", "-"], input=pr_diff,
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"pr_diff does not apply: {p.stderr[:300]}")
        try:
            yield
        finally:
            git(repo, "checkout", "--", ".")


@dataclass
class Verdict:
    """What the full suite said about one candidate patch."""

    accepted: bool
    target_pass: bool
    overfit: bool
    failing_output: str
    n_new_failures: int
    finished: bool


def make_validator(repo: Path, python: Path, preexisting: set[str], target_tests: list[str],
                   on_verdict: Callable[[Verdict], None] | None = None) -> Callable[[dict[str, str]], tuple[bool, str]]:
    """Build the `validate(files) -> (accepted, failing_output)` callable `RepairAgent.run` expects.

    The repo must already be in the failing state (inside :func:`head_state`). Each call writes the
    patched files, runs the whole suite, and restores the files it touched.

    Args:
        repo: Working tree in the failing state.
        python: Interpreter of the repo's venv.
        preexisting: Test ids failing at the base (never counted).
        target_tests: The tests that failed because of the change.
        on_verdict: Optional callback with the :class:`Verdict`.
    """
    def validate(files: dict[str, str]) -> tuple[bool, str]:
        before = {p: (repo / p).read_text(encoding="utf-8") for p in files}
        try:
            for p, text in files.items():
                (repo / p).write_text(text, encoding="utf-8")
            res: Suite = run_suite(repo, python)
        finally:
            for p, text in before.items():
                (repo / p).write_text(text, encoding="utf-8")
        fails = {t: o for t, o in res.failing.items() if t not in preexisting}
        target_ok = res.finished and not any(t in fails for t in target_tests)
        v = Verdict(accepted=res.finished and not fails, target_pass=target_ok,
                    overfit=target_ok and bool(fails), failing_output="\n".join(
                        f"{t}\n{o}" for t, o in sorted(fails.items())[:3]), n_new_failures=len(fails),
                    finished=res.finished)
        if on_verdict:
            on_verdict(v)
        return v.accepted, v.failing_output
    return validate
