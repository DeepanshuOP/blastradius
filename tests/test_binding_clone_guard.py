"""The binding report must refuse an incomplete clone set, not shrink quietly.

`analysis/binding_report.py` once scoped itself to whatever was present in
`data/clones/`, which made its denominator a property of the machine. With 3 of
43 repos cloned it reported 364 rows and exited 0, a figure not comparable with
the published binding figures (now D-50's 5,643 / 5,985 and 3,820 / 5,985, which
supersede D-47's 5,622 / 3,819). These tests pin the guard that
turns that into a hard error.

The corpus list is read from the REAL `data/interim/parsed_outcomes.parquet`.
Clone sets are real directories under `tmp_path` holding real `git init`
repositories -- nothing here is mocked.
"""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from analysis.binding_report import (
    PARSED_OUTCOMES,
    clone_dir_for,
    corpus_repos,
    is_usable_clone,
    missing_clones,
    require_complete_clones,
)
from tests.conftest import requires_data

PARSED = PARSED_OUTCOMES.as_posix()


_GIT_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
    "PATH": "/usr/bin:/bin",
}


def _make_clone(root: Path, repo: str) -> Path:
    """Create a real git repository, with a commit, at the clone path.

    The commit matters: a repository with no commit answers `git ls-tree`
    with nothing, and the guard rejects that for the same reason it rejects a
    partial clone -- it cannot bind.
    """
    path = clone_dir_for(repo, root)
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
    (path / "Test.java").write_text("// fixture\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(path), "add", "Test.java"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(path), "commit", "-qm", "fixture"],
        check=True,
        capture_output=True,
        env={**_GIT_ENV, "HOME": str(root)},
    )
    return path


def test_clone_dir_follows_the_owner__name_convention() -> None:
    """`owner/name` maps to `<clones>/owner__name`."""
    assert clone_dir_for("apache/beam", Path("data/clones")) == Path(
        "data/clones/apache__beam"
    )


@requires_data(PARSED)
def test_corpus_repos_comes_from_the_table_not_the_disk() -> None:
    """The scope is every repo with an observed test_id, sorted and distinct."""
    repos = corpus_repos()
    assert repos, "no corpus repos found"
    assert repos == sorted(repos)
    assert len(repos) == len(set(repos))
    assert all("/" in r for r in repos)


@requires_data(PARSED)
def test_an_empty_clones_dir_reports_every_repo_missing(tmp_path: Path) -> None:
    """Nothing cloned means nothing is silently in scope."""
    assert missing_clones(clones_dir=tmp_path) == corpus_repos()


@requires_data(PARSED)
def test_a_complete_clone_set_has_no_missing_repos(tmp_path: Path) -> None:
    for repo in corpus_repos():
        _make_clone(tmp_path, repo)
    assert missing_clones(clones_dir=tmp_path) == []


@requires_data(PARSED)
def test_require_complete_clones_passes_and_returns_every_repo(
    tmp_path: Path,
) -> None:
    for repo in corpus_repos():
        _make_clone(tmp_path, repo)
    assert require_complete_clones(clones_dir=tmp_path) == corpus_repos()


@requires_data(PARSED)
def test_one_missing_repo_blocks_the_run_and_is_named(tmp_path: Path) -> None:
    """The error must name the repo that is missing, not just the count."""
    repos = corpus_repos()
    absent = repos[0]
    for repo in repos[1:]:
        _make_clone(tmp_path, repo)

    with pytest.raises(SystemExit) as excinfo:
        require_complete_clones(clones_dir=tmp_path)

    message = str(excinfo.value)
    assert "BLOCKED" in message
    assert absent in message, "the missing repo is not named in the error"
    assert str(clone_dir_for(absent, tmp_path)) in message
    assert f"1 of {len(repos)}" in message
    for present in repos[1:]:
        assert f"  {present:<45} ->" not in message, "listed a repo that IS cloned"


@requires_data(PARSED)
def test_the_subset_that_caused_this_guard_is_rejected(tmp_path: Path) -> None:
    """The real 3-of-43 mini-corpus state must not produce a figure."""
    mini = [
        "fla-org/flash-linear-attention",
        "Stirling-Tools/Stirling-PDF",
        "spiculedata/saiku",
    ]
    present = [r for r in mini if r in corpus_repos()]
    assert present, "the mini-corpus repos are not in the corpus table"
    for repo in present:
        _make_clone(tmp_path, repo)

    with pytest.raises(SystemExit) as excinfo:
        require_complete_clones(clones_dir=tmp_path)
    assert "BLOCKED" in str(excinfo.value)
    assert "D-50" in str(excinfo.value), "the error must cite the pinned-binding decision"


@requires_data(PARSED)
def test_a_directory_without_git_counts_as_missing(tmp_path: Path) -> None:
    """A bare directory cannot answer `git ls-tree`, so it is not a clone."""
    repos = corpus_repos()
    for repo in repos[1:]:
        _make_clone(tmp_path, repo)
    # repos[0] exists as a plain directory with no .git inside.
    clone_dir_for(repos[0], tmp_path).mkdir(parents=True)

    assert missing_clones(clones_dir=tmp_path) == [repos[0]]
    with pytest.raises(SystemExit):
        require_complete_clones(clones_dir=tmp_path)


@requires_data(PARSED)
def test_a_bare_clone_with_a_tree_counts_as_present(tmp_path: Path) -> None:
    """`git clone --bare` holds HEAD at the top, not in a `.git` directory."""
    repos = corpus_repos()
    for repo in repos[1:]:
        _make_clone(tmp_path, repo)

    source = _make_clone(tmp_path / "src", repos[0])
    bare = clone_dir_for(repos[0], tmp_path)
    subprocess.run(
        ["git", "clone", "-q", "--bare", str(source), str(bare)],
        check=True,
        capture_output=True,
    )

    assert is_usable_clone(bare)
    assert missing_clones(clones_dir=tmp_path) == []


# --- a partial clone must not borrow the enclosing repository ---------------


@requires_data(PARSED)
def test_a_partial_clone_inside_a_repo_is_not_mistaken_for_a_clone(
    tmp_path: Path,
) -> None:
    """An interrupted clone must not resolve to the ENCLOSING repository.

    This is a real failure that happened: `data/clones/` sits inside the
    BlastRadius working tree, a `git clone` of `apache/flink` was interrupted
    leaving a partial `.git`, git discovery fell through to BlastRadius's own
    repository, and `git -C <dir> rev-parse HEAD` answered with a BlastRadius
    commit. A `.git`-exists check accepted it, so binding would have run
    against the wrong tree under the right repo's name.

    The fixture reproduces the shape exactly: an outer real repository with a
    commit, and a clone directory inside it holding a partial `.git`.
    """
    outer = tmp_path / "outer"
    clones = outer / "clones"
    clones.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(outer)], check=True, capture_output=True)
    (outer / "file.txt").write_text("content", encoding="utf-8")
    env = {
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
        "PATH": "/usr/bin:/bin",
        "HOME": str(tmp_path),
    }
    subprocess.run(
        ["git", "-C", str(outer), "add", "file.txt"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(outer), "commit", "-qm", "c"],
        check=True,
        capture_output=True,
        env=env,
    )
    # Sanity: the outer repo really does answer ls-tree.
    assert is_usable_clone(outer)

    repo = corpus_repos()[0]
    partial = clone_dir_for(repo, clones)
    (partial / ".git").mkdir(parents=True)
    (partial / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

    assert not is_usable_clone(partial), "a partial .git was accepted as a clone"
    assert repo in missing_clones(clones_dir=clones)


@requires_data(PARSED)
def test_an_empty_tree_is_not_a_usable_clone(tmp_path: Path) -> None:
    """`git init` with no commit answers no paths, so it cannot bind."""
    empty = tmp_path / "empty"
    empty.mkdir()
    subprocess.run(["git", "init", "-q", str(empty)], check=True, capture_output=True)
    assert not is_usable_clone(empty)


def test_a_nonexistent_path_is_not_a_usable_clone(tmp_path: Path) -> None:
    assert not is_usable_clone(tmp_path / "nope")
