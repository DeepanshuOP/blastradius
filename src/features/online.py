"""Rank a live repository's test files with the E1 model (the agents' entry to the shared feature layer).

Uses the same `featurize` as the offline benchmark, with `LocalGitHistory` as the history:
trailing co-change from `git log`, failure history from `.blastradius/history/test_outcomes.jsonl`.
Returns None when no E1 model is on disk, so callers keep their heuristic fallback.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from src.features.context import ChangeContext, LocalGitHistory
from src.parse.changeset import is_conventional_test_file

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "e1_lgbm_v1.txt"
FIXED_TS = 1_791_590_400  # 2026-10-10T00:00:00Z: used when a caller gives no clock, so ranking is reproducible
_BUILD = ("build.gradle", "pom.xml", "setup.py", "pyproject.toml", "setup.cfg")


@dataclass
class RankedTest:
    """One test file with its E1 score and the three features that moved it most."""

    test_file: str
    score: float
    top_features: list[str] = field(default_factory=list)


def tracked_files(repo: Path) -> list[str]:
    """`git ls-files` of the working copy (empty list when it is not a git repo)."""
    r = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True, check=False,
                       env={**os.environ, "GIT_NO_LAZY_FETCH": "1"})
    return [ln for ln in r.stdout.splitlines() if ln]


def context_from_files(repo: str, changed: list[str], n_lines: int = 0, ts: int | None = None) -> ChangeContext:
    """A :class:`ChangeContext` for a list of changed files."""
    lower = [c.lower() for c in changed]
    return ChangeContext(
        repo=repo, instance_key=(repo, 0), ts=ts or FIXED_TS, changed_files=tuple(sorted(changed)),
        n_lines_changed=n_lines, touches_test_file=any("test" in c for c in lower),
        touches_build_config=any(c.endswith(_BUILD) for c in lower),
        touches_ci_config=any(".github/workflows" in c or c.endswith(".travis.yml") for c in changed),
        is_docs_only=bool(changed) and all(c.endswith((".md", ".rst", ".txt")) or c.startswith("docs/") for c in lower))


def diff_stats(diff: str) -> tuple[list[str], int]:
    """Changed paths and added+removed line count of a unified diff."""
    files = re.findall(r"^\+\+\+ b/(.+)$", diff, re.M)
    n = sum(1 for ln in diff.splitlines() if (ln.startswith("+") and not ln.startswith("+++"))
            or (ln.startswith("-") and not ln.startswith("---")))
    return files, n


def rank_tests(repo: Path, changed: list[str], n_lines: int = 0, ts: int | None = None,
               model_path: Path = MODEL_PATH, explain_top: int = 3) -> list[RankedTest] | None:
    """Rank every conventional test file of `repo` by E1 score for a change touching `changed`.

    Args:
        repo: Working copy.
        changed: Changed paths.
        n_lines: Added plus removed lines.
        ts: Prediction time (epoch s); a fixed constant when omitted.
        model_path: The E1 text model (its JSON manifest lists the feature order).
        explain_top: Number of SHAP contributions to render per test.

    Returns:
        Tests best first (ties by path), or None if the model or lightgbm is unavailable.
    """
    if not model_path.exists():
        return None
    try:
        from src.models import e1_ranker as R
    except ImportError:
        return None
    cands = sorted(f for f in tracked_files(repo) if is_conventional_test_file(f))
    if not cands:
        return []
    from src.features.test_features import featurize

    booster, manifest = R.load(model_path)
    cols = manifest["feature_list"]
    hist = LocalGitHistory(repo)
    ctx = context_from_files(repo.name, changed, n_lines, ts)
    df = featurize(ctx, cands, hist)
    scores = R.predict(booster, df, cols)
    contrib = R.explain(booster, df, cols)[:, :-1] if explain_top else None
    out = []
    for i, f in enumerate(df["test_file"]):
        tops: list[str] = []
        if contrib is not None:
            idx = sorted(range(len(cols)), key=lambda j: -abs(contrib[i, j]))[:explain_top]
            tops = [f"{cols[j]}={df.iloc[i][cols[j]]:g} ({contrib[i, j]:+.2f})" for j in idx if contrib[i, j] != 0]
        out.append(RankedTest(f, float(scores[i]), tops))
    out.sort(key=lambda r: (-r.score, r.test_file))
    return out
