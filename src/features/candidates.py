"""Candidate test files for a prediction: what the ranker chooses among.

A candidate is a conventional test file (`is_conventional_test_file`) in the
repo's PINNED clone (D-50, never live HEAD), plus every bound ground-truth test
file of that repo seen in the data strictly before the cutoff. The instance's
own ground-truth files are added if they exist in the pinned tree, because
binding was made against that tree and the benchmark must be able to recall
every label (a file the candidate set cannot contain is a recall ceiling, not a
model error).

Caveat reported by `analysis/build_e1_features.py`: a ground-truth file that is
NOT conventional-looking and was never seen before is a candidate only for the
instance in which it is a label. No feature exposes candidate provenance, and
the build reports how many positives this applies to.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from src.parse.changeset import is_conventional_test_file

CLONES_DIR = Path("data/clones")
CLONE_PINS = Path("docs/CLONE_PINS.json")


@dataclass
class RepoCandidates:
    """Per-repo candidate source.

    Attributes:
        tree_files: Conventional test files in the pinned tree (empty if no clone).
        tree: Every file in the pinned tree (None if there is no usable clone).
        source: `pinned-clone` or `fallback-bound-and-changeset`.
    """

    tree_files: list[str] = field(default_factory=list)
    tree: frozenset[str] | None = None
    source: str = "fallback-bound-and-changeset"


def list_tree(clone: Path, rev: str) -> list[str] | None:
    """Files of `rev` in `clone` (no network), or None if the clone cannot answer.

    Args:
        clone: Path to the clone.
        rev: A pinned commit.

    Returns:
        Sorted repo-relative paths, or None.
    """
    if not clone.is_dir():
        return None
    r = subprocess.run(["git", "-C", str(clone), "ls-tree", "-r", "--name-only", rev], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", check=False,
                       env={**os.environ, "GIT_NO_LAZY_FETCH": "1"})
    if r.returncode != 0:
        return None
    return sorted(p for p in r.stdout.split("\n") if p)


def load_repo_candidates(repo: str, clones_dir: Path = CLONES_DIR, pins_path: Path = CLONE_PINS) -> RepoCandidates:
    """Read one repo's pinned tree.

    Args:
        repo: `owner/name`.
        clones_dir: Root of the clones.
        pins_path: `docs/CLONE_PINS.json`.

    Returns:
        The tree-derived candidate source; the fallback marker when no tree is readable.
    """
    pins = json.loads(Path(pins_path).read_text())["pins"]
    if repo not in pins:
        return RepoCandidates()
    files = list_tree(Path(clones_dir) / repo.replace("/", "__"), pins[repo])
    if files is None:
        return RepoCandidates()
    return RepoCandidates([f for f in files if is_conventional_test_file(f)], frozenset(files), "pinned-clone")


def candidates_for(rc: RepoCandidates, seen_before: set[str], own_ground_truth: set[str] | None = None) -> list[str]:
    """The candidate list of one instance.

    Args:
        rc: The repo's pinned-tree source.
        seen_before: Bound ground-truth test files of this repo from instances strictly before the cutoff
            (and, on the fallback path, changeset test files seen before it).
        own_ground_truth: The instance's own ground-truth files; kept only if present in the pinned tree.

    Returns:
        Sorted, de-duplicated candidate paths.
    """
    out = set(rc.tree_files) | set(seen_before)
    if own_ground_truth:
        out |= {f for f in own_ground_truth if rc.tree is None or f in rc.tree}
    return sorted(out)
