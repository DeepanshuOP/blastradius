"""The reviewer challenge (Live Lab, D-65): a seeded random choice of one function and one mutation operator.

"Will the tests catch this bug?" needs a bug the reviewer did not choose and the lab did not rehearse. The choice is a
pure function of (repository text, seed): the same seed on the same pinned repository names the same function, operator
and line, so a reviewer can ask for the seed shown on screen again. Nothing here runs repository code or calls a model.
"""

from __future__ import annotations

import random
from pathlib import Path

from src.lab import changes

SEED_MAX = 2 ** 31 - 1


def candidates(repo_dir: Path, src_dirs: list[str]) -> list[dict]:
    """Every function of the repository's source files that has at least one applicable mutation.

    Returns:
        `[{"file", "function", "mutations": [{"operator", "line", "col", "old", "new"}]}]`, sorted by (file, function).
        Test files and `conftest.py` are not candidates (a bug is injected in the code under test).
    """
    out: list[dict] = []
    roots = [repo_dir / d for d in src_dirs] or [repo_dir]
    files = sorted({p for r in roots if r.is_dir() for p in r.rglob("*.py")
                    if "__pycache__" not in p.parts and not p.name.startswith("test_") and p.name != "conftest.py"
                    and "tests" not in p.relative_to(repo_dir).parts})
    for p in files:
        rel = p.relative_to(repo_dir).as_posix()
        try:
            fns = changes.mutations_of(p.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, ValueError):
            continue
        for f in fns:
            if f["mutations"]:
                out.append({"file": rel, "function": f["function"],
                            "mutations": sorted(f["mutations"], key=lambda m: (m["line"], m["col"], m["operator"]))})
    return sorted(out, key=lambda c: (c["file"], c["function"]))


def pick(cands: list[dict], seed: int) -> dict:
    """The function and operator `seed` chooses: a uniform function, then a uniform operator of that function (the
    first mutation of that operator in line order).

    Raises:
        ValueError: When there is nothing to choose from.
    """
    if not cands:
        raise ValueError("this repository has no function with an applicable mutation operator")
    rng = random.Random(int(seed))
    c = cands[rng.randrange(len(cands))]
    ops = sorted({m["operator"] for m in c["mutations"]})
    op = ops[rng.randrange(len(ops))]
    m = next(x for x in c["mutations"] if x["operator"] == op)
    return {"seed": int(seed), "file": c["file"], "function": c["function"], "operator": op, "line": m["line"],
            "old": m["old"], "new": m["new"], "n_functions": len(cands), "n_operators": len(ops)}


def pick_for(slug: str, seed: int) -> dict:
    """`pick` over a prepared repository (read-only: the pinned working tree under data/seeded)."""
    from src.lab.workspace import PREPARED, REPOS, prepared_info

    if slug not in PREPARED:
        raise ValueError(f"{slug!r} is not a prepared repository")
    return pick(candidates(REPOS / slug, list(prepared_info().get(slug, {}).get("src_dirs", []))), seed)
