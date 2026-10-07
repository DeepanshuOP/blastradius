"""Bind observed `test_id`s to test files in the corpus repos' git trees.

Clone completeness is a GUARD, not a filter. This script used to scope itself
to whatever happened to be present in `data/clones/`, so its denominator was a
property of the machine rather than of the corpus: with 3 of 43 repos cloned it
reported 364 rows and looked like a successful run. The figure is defined over
all 43 repos the pinned corpus observes test outcomes for, and a figure computed
over a subset is not comparable. So a missing clone is a hard error that names
the repos, never a silently smaller report.

D-50: binding resolves each repo against its PINNED commit
(`docs/CLONE_PINS.json`), never live HEAD. Live-HEAD binding drifted across
machines (D-47 5,622 / 3,819; Prisha 5,623 / 3,801; Deepanshu 5,643 / 3,820).
`--write-pins` records the current HEADs.
"""

import json
import pandas as pd
import subprocess
import sys
from pathlib import Path

from src.parse.test_ids import normalize_test_id
from src.parse.test_files import resolve_test_file, _get_git_tree

__all__ = [
    "CLONES_DIR",
    "CLONE_PINS",
    "bind_tests",
    "head_sha",
    "load_pins",
    "write_pins",
    "PARSED_OUTCOMES",
    "clone_dir_for",
    "corpus_repos",
    "is_usable_clone",
    "missing_clones",
    "require_complete_clones",
]

#: The pinned corpus's test-bearing repos are defined by this table, not by
#: whatever is on disk. Every repo with at least one observed `test_id` must be
#: cloned for the binding figure to mean what D-47 says it means.
PARSED_OUTCOMES = Path("data/interim/parsed_outcomes.parquet")
CLONES_DIR = Path("data/clones")
#: D-50: the commit each corpus clone is bound AGAINST. Live HEAD drifted across
#: machines (5,622 / 5,623 / 5,643 combined), so binding never reads HEAD.
CLONE_PINS = Path("docs/CLONE_PINS.json")


def clone_dir_for(repo: str, clones_dir: Path = CLONES_DIR) -> Path:
    """Map `owner/name` to its clone directory.

    Args:
        repo: Repo in `owner/name` form.
        clones_dir: Root holding the clones.

    Returns:
        The `clones_dir/owner__name` path, cloned or not.
    """
    return clones_dir / repo.replace("/", "__")


def corpus_repos(parsed_outcomes: Path = PARSED_OUTCOMES) -> list[str]:
    """Repos the pinned corpus observes at least one `test_id` for.

    Args:
        parsed_outcomes: The parsed-outcomes table defining the corpus.

    Returns:
        Sorted `owner/name` repos. This is the binding denominator's scope.
    """
    df = pd.read_parquet(parsed_outcomes, columns=["repo", "test_id"])
    return sorted(df.loc[df["test_id"].notna(), "repo"].unique().tolist())


def is_usable_clone(path: Path, pin: str | None = None) -> bool:
    """Whether `path` is a git repository that can answer the binding query.

    Presence of a `.git` directory is NOT sufficient, and trusting it is how a
    corrupt figure gets produced. `data/clones/` lives inside the BlastRadius
    working tree, so an interrupted `git clone` leaves a partial `.git` that
    git discovery falls straight through, resolving to the PARENT repository
    instead. `git -C <dir> rev-parse HEAD` then happily answers with
    BlastRadius's own HEAD, and binding would run against this repo's file
    tree while reporting the corpus repo's name.

    So the check is that the resolved git directory actually lives inside
    `path`, that HEAD resolves, and that `git ls-tree -r HEAD` returns at least
    one path -- the exact call `src/parse/test_files.py::_get_git_tree` makes.

    With `pin`, the tree that must answer is the PINNED commit's, not HEAD's
    (D-50): the pinned commit must exist locally and `git ls-tree -r <pin>` must
    return a path. Only tree objects are needed, so a blobless
    (`--filter=blob:none`) clone passes.

    Args:
        path: Candidate clone directory.
        pin: Pinned commit sha to require, or None to check HEAD (legacy).

    Returns:
        True if binding can read a non-empty tree from it.
    """
    rev = pin if pin else "HEAD"
    if not path.is_dir():
        return False
    try:
        git_dir = subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "--absolute-git-dir"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, OSError):
        return False

    resolved = Path(git_dir).resolve()
    root = path.resolve()
    if resolved != root and root not in resolved.parents:
        # Discovery escaped to an enclosing repository.
        return False

    try:
        tree = subprocess.check_output(
            ["git", "-C", str(path), "ls-tree", "-r", rev, "--name-only"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, OSError):
        return False
    return bool(tree.strip())


def head_sha(path: Path) -> str:
    """The full sha `HEAD` currently resolves to in the clone at `path`.

    Args:
        path: Clone directory.

    Returns:
        40-hex commit sha.
    """
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def load_pins(path: Path = CLONE_PINS) -> dict[str, str]:
    """Read `docs/CLONE_PINS.json`.

    Args:
        path: The pin file.

    Returns:
        `{owner/name: commit sha}`.

    Raises:
        SystemExit: If the file is absent (binding refuses to fall back to HEAD).
    """
    if not path.exists():
        raise SystemExit(
            f"BLOCKED: {path} is absent. Binding resolves against pinned commits "
            "(D-50), never live HEAD. Write it with "
            "`python analysis/binding_report.py --write-pins`."
        )
    return json.loads(path.read_text(encoding="utf-8"))["pins"]


def write_pins(
    parsed_outcomes: Path = PARSED_OUTCOMES,
    clones_dir: Path = CLONES_DIR,
    path: Path = CLONE_PINS,
) -> dict[str, str]:
    """Record every corpus clone's CURRENT HEAD as its pin (deterministic JSON).

    Refuses to pin a clone that is not usable at HEAD.

    Args:
        parsed_outcomes: The parsed-outcomes table defining the corpus.
        clones_dir: Root holding the clones.
        path: Where to write.

    Returns:
        The pins written.
    """
    missing = missing_clones(parsed_outcomes, clones_dir)
    if missing:
        raise SystemExit(f"cannot pin: unusable clones: {', '.join(missing)}")
    pins = {r: head_sha(clone_dir_for(r, clones_dir)) for r in corpus_repos(parsed_outcomes)}
    doc = {
        "description": "Commit each corpus clone is bound against (D-50). "
        "Binding never reads live HEAD.",
        "pins": pins,
    }
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return pins


def missing_clones(
    parsed_outcomes: Path = PARSED_OUTCOMES,
    clones_dir: Path = CLONES_DIR,
    pins: dict[str, str] | None = None,
) -> list[str]:
    """Corpus repos with no usable clone on disk.

    "Usable" is :func:`is_usable_clone`, not merely "the directory exists".

    With `pins`, a repo is also missing when it has no pin or its pinned tree
    is not in the clone.

    Args:
        parsed_outcomes: The parsed-outcomes table defining the corpus.
        clones_dir: Root holding the clones.
        pins: `{repo: sha}` to require, or None to check HEAD (legacy).

    Returns:
        Sorted repos needing a clone.
    """
    return [
        repo
        for repo in corpus_repos(parsed_outcomes)
        if not is_usable_clone(
            clone_dir_for(repo, clones_dir),
            None if pins is None else pins.get(repo, "unpinned"),
        )
    ]


def require_complete_clones(
    parsed_outcomes: Path = PARSED_OUTCOMES,
    clones_dir: Path = CLONES_DIR,
    pins: dict[str, str] | None = None,
) -> list[str]:
    """Refuse to produce a binding figure over an incomplete clone set.

    Args:
        parsed_outcomes: The parsed-outcomes table defining the corpus.
        clones_dir: Root holding the clones.

    Returns:
        The full list of corpus repos, all of them cloned.

    Raises:
        SystemExit: If any corpus repo is missing, with every missing repo and
            its expected clone path named in the message.
    """
    repos = corpus_repos(parsed_outcomes)
    missing = missing_clones(parsed_outcomes, clones_dir, pins)
    if missing:
        lines = [
            f"BLOCKED: {len(missing)} of {len(repos)} corpus repos are not cloned "
            f"under {clones_dir}/.",
            "",
            "The binding figure is defined over all corpus repos at their pinned commits",
            "(D-50, docs/CLONE_PINS.json). Computing it over a subset",
            "would report a smaller number that is not comparable with those, so this",
            "is an error rather than a smaller run.",
            "",
            "Missing:",
        ]
        lines += [
            f"  {repo:<45} -> {clone_dir_for(repo, clones_dir)}" for repo in missing
        ]
        lines += [
            "",
            "Clone each one (github.com over HTTPS, no API) and re-run, e.g.:",
            f"  git clone https://github.com/{missing[0]}.git "
            f"{clone_dir_for(missing[0], clones_dir)}",
        ]
        raise SystemExit("\n".join(lines))
    return repos

def bind_tests(
    distinct_tests: pd.DataFrame,
    pins: dict[str, str],
    clones_dir: Path = CLONES_DIR,
) -> pd.DataFrame:
    """Bind each `(repo, test_id)` against the repo's PINNED tree, never HEAD.

    Args:
        distinct_tests: Columns repo, test_id, harness, is_fqcn_qualified.
        pins: `{repo: commit sha}` (D-50).
        clones_dir: Root holding the clones.

    Returns:
        The input plus resolved_path, status, candidates_considered.
    """
    df_cloned = distinct_tests.copy()
    trees: dict[str, dict[str, list[str]]] = {}
    for repo in sorted(df_cloned["repo"].unique()):
        try:
            tree_paths = _get_git_tree(clone_dir_for(repo, clones_dir), pins[repo])
        except subprocess.CalledProcessError:
            tree_paths = set()
        tree_idx: dict[str, list[str]] = {}
        for p in sorted(tree_paths):
            tree_idx.setdefault(p.split("/")[-1], []).append(p)
        trees[repo] = tree_idx

    paths, statuses, candidates_considered = [], [], []
    for _, row in df_cloned.iterrows():
        repo = row["repo"]
        tid = normalize_test_id(row["test_id"])
        if not tid:
            paths.append(None)
            statuses.append("unqualified")
            candidates_considered.append(0)
            continue
        res = resolve_test_file(tid, clone_dir_for(repo, clones_dir), _tree_cache=trees[repo])
        paths.append(res.path)
        statuses.append(res.status)
        candidates_considered.append(res.candidates_considered)
    df_cloned["resolved_path"] = paths
    df_cloned["status"] = statuses
    df_cloned["candidates_considered"] = candidates_considered
    return df_cloned


def main():
    if "--write-pins" in sys.argv:
        pins = write_pins()
        print(f"Wrote {CLONE_PINS}: {len(pins)} pins")
        return

    print("Loading parsed outcomes...")
    df = pd.read_parquet('data/interim/parsed_outcomes.parquet')

    # We only care about distinct test_ids whose repo is cloned.
    # Group by (repo, test_id)
    distinct_tests = df[['repo', 'test_id', 'harness', 'is_fqcn_qualified']].drop_duplicates()

    # Guard, not a filter: a missing clone or pinned tree is an error that names the repos.
    clones_dir = CLONES_DIR
    pins = load_pins()
    cloned_repos = require_complete_clones(clones_dir=clones_dir, pins=pins)

    df_cloned = distinct_tests[distinct_tests['repo'].isin(cloned_repos)].copy()
    print(f"Clones: {len(cloned_repos)} / {len(cloned_repos)} corpus repos present, bound at pinned commits ({CLONE_PINS})")
    print(f"Total distinct test_ids in cloned repos: {len(df_cloned)}")

    df_cloned = bind_tests(df_cloned, pins, clones_dir)
    
    df_cloned.to_parquet('data/interim/binding.parquet', index=False)
    print("Wrote data/interim/binding.parquet")

    # Overall binding rate
    exact_count = (df_cloned['status'] == 'exact').sum()
    total = len(df_cloned)
    print(f"\nOverall binding rate: {exact_count} / {total} ({(exact_count/total)*100:.2f}%)")
    
    # Status breakdown
    print("\nStatus breakdown:")
    counts = df_cloned['status'].value_counts()
    for status, count in counts.items():
        print(f"  {status}: {count} ({(count/total)*100:.2f}%)")
        
    # Binding rate per (repo, harness)
    print("\nBinding rate per (repo, harness):")
    grouped = df_cloned.groupby(['repo', 'harness'])
    repo_rates = {}
    for (repo, harness), group in grouped:
        g_exact = (group['status'] == 'exact').sum()
        g_total = len(group)
        rate = g_exact / g_total
        repo_rates[repo] = rate
        print(f"  {repo} [{harness}]: {g_exact} / {g_total} ({rate*100:.2f}%)")
        
    # How many repos fall below 70%
    below_70 = sum(1 for r in repo_rates.values() if r < 0.70)
    print(f"\nRepos below 70% gate: {below_70} / {len(repo_rates)}")
    
    # Binding rate by is_fqcn_qualified
    print("\nBinding rate by is_fqcn_qualified:")
    for fqcn_val, group in df_cloned.groupby('is_fqcn_qualified'):
        g_exact = (group['status'] == 'exact').sum()
        g_total = len(group)
        print(f"  {fqcn_val}: {g_exact} / {g_total} ({(g_exact/g_total)*100:.2f}%)")
        
    # 20 sampled UNBOUND test_ids printed verbatim with their status
    print("\n20 sampled UNBOUND test_ids:")
    unbound = df_cloned[df_cloned['status'] != 'exact'].sample(n=min(20, (df_cloned['status'] != 'exact').sum()), random_state=42)
    for _, row in unbound.iterrows():
        print(f"  Repo: {row['repo']} | Status: {row['status']} | ID: {row['test_id']}")

if __name__ == "__main__":
    main()
