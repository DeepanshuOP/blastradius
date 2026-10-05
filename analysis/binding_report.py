"""Bind observed `test_id`s to test files in the corpus repos' git trees.

Clone completeness is a GUARD, not a filter. This script used to scope itself
to whatever happened to be present in `data/clones/`, so its denominator was a
property of the machine rather than of the corpus: with 3 of 43 repos cloned it
reported 364 rows and looked like a successful run. D-47's published figures
(5,622 / 5,985 combined, 3,819 / 5,985 at full confidence) are defined over all
43 repos the pinned corpus observes test outcomes for, and a figure computed
over a subset is not comparable with them. So a missing clone is now a hard
error that names the repos, never a silently smaller report.
"""

import pandas as pd
import subprocess
import sys
from pathlib import Path

from src.parse.test_ids import normalize_test_id
from src.parse.test_files import resolve_test_file, _get_git_tree

__all__ = [
    "CLONES_DIR",
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


def is_usable_clone(path: Path) -> bool:
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

    Args:
        path: Candidate clone directory.

    Returns:
        True if binding can read a non-empty tree from it.
    """
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
            ["git", "-C", str(path), "ls-tree", "-r", "HEAD", "--name-only"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, OSError):
        return False
    return bool(tree.strip())


def missing_clones(
    parsed_outcomes: Path = PARSED_OUTCOMES, clones_dir: Path = CLONES_DIR
) -> list[str]:
    """Corpus repos with no usable clone on disk.

    "Usable" is :func:`is_usable_clone`, not merely "the directory exists".

    Args:
        parsed_outcomes: The parsed-outcomes table defining the corpus.
        clones_dir: Root holding the clones.

    Returns:
        Sorted repos needing a clone.
    """
    return [
        repo
        for repo in corpus_repos(parsed_outcomes)
        if not is_usable_clone(clone_dir_for(repo, clones_dir))
    ]


def require_complete_clones(
    parsed_outcomes: Path = PARSED_OUTCOMES, clones_dir: Path = CLONES_DIR
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
    missing = missing_clones(parsed_outcomes, clones_dir)
    if missing:
        lines = [
            f"BLOCKED: {len(missing)} of {len(repos)} corpus repos are not cloned "
            f"under {clones_dir}/.",
            "",
            "The binding figure is defined over all corpus repos (D-47: 5,622 / 5,985",
            "combined, 3,819 / 5,985 at full confidence). Computing it over a subset",
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

def main():
    print("Loading parsed outcomes...")
    df = pd.read_parquet('data/interim/parsed_outcomes.parquet')
    
    # We only care about distinct test_ids whose repo is cloned.
    # Group by (repo, test_id)
    distinct_tests = df[['repo', 'test_id', 'harness', 'is_fqcn_qualified']].drop_duplicates()
    
    # Guard, not a filter: a missing clone is an error that names the repos.
    clones_dir = CLONES_DIR
    cloned_repos = require_complete_clones(clones_dir=clones_dir)

    df_cloned = distinct_tests[distinct_tests['repo'].isin(cloned_repos)].copy()
    print(f"Clones: {len(cloned_repos)} / {len(cloned_repos)} corpus repos present")
    print(f"Total distinct test_ids in cloned repos: {len(df_cloned)}")
    
    trees = {}
    for repo in cloned_repos:
        repo_root = clones_dir / repo.replace('/', '__')
        try:
            tree_paths = _get_git_tree(repo_root)
        except subprocess.CalledProcessError:
            tree_paths = set()
        tree_idx = {}
        for p in tree_paths:
            basename = p.split("/")[-1]
            if basename not in tree_idx:
                tree_idx[basename] = []
            tree_idx[basename].append(p)
        trees[repo] = tree_idx
            
    paths = []
    statuses = []
    candidates_considered = []
    
    ambiguous_samples = []
    for idx, row in df_cloned.iterrows():
        repo = row['repo']
        tid_raw = row['test_id']
        repo_root = clones_dir / repo.replace('/', '__')
        
        tid = normalize_test_id(tid_raw)
        if not tid:
            paths.append(None)
            statuses.append("unqualified")
            candidates_considered.append(0)
            continue
            
        res = resolve_test_file(tid, repo_root, _tree_cache=trees[repo])
        paths.append(res.path)
        statuses.append(res.status)
        candidates_considered.append(res.candidates_considered)
        
    df_cloned['resolved_path'] = paths
    df_cloned['status'] = statuses
    df_cloned['candidates_considered'] = candidates_considered
    
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
