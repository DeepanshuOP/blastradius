"""D-50: binding resolves against pinned commits, never live HEAD.

Every repository here is a real `git init` / `git clone` under `tmp_path`;
nothing is mocked. The corpus list is read from the real parquet.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
import pytest

from analysis.binding_report import (
    PARSED_OUTCOMES,
    bind_tests,
    clone_dir_for,
    corpus_repos,
    head_sha,
    is_usable_clone,
    load_pins,
    missing_clones,
    write_pins,
)
from tests.conftest import requires_data

REPO = "acme/widgets"
TEST_ID = "com.acme.FooTest#testIt"
ENV = {
    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
    "PATH": "/usr/bin:/bin", "HOME": "/nonexistent",
}


def git(path: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(path), *args], check=True, capture_output=True, text=True, env=ENV
    ).stdout.strip()


def make_repo(root: Path) -> Path:
    path = clone_dir_for(REPO, root)
    path.mkdir(parents=True)
    git(path, "init", "-q")
    (path / "src/com/acme").mkdir(parents=True)
    (path / "src/com/acme/FooTest.java").write_text("class FooTest {}\n", encoding="utf-8")
    git(path, "add", ".")
    git(path, "commit", "-qm", "add test")
    return path


def frame() -> pd.DataFrame:
    return pd.DataFrame(
        [{"repo": REPO, "test_id": TEST_ID, "harness": "maven", "is_fqcn_qualified": True}]
    )


def test_a_moved_head_still_binds_against_the_pin(tmp_path: Path) -> None:
    clone = make_repo(tmp_path)
    pin = head_sha(clone)
    git(clone, "rm", "-q", "src/com/acme/FooTest.java")
    git(clone, "commit", "-qm", "delete the test file")
    assert head_sha(clone) != pin

    bound = bind_tests(frame(), {REPO: pin}, tmp_path)
    assert bound.loc[0, "status"] == "exact"
    assert bound.loc[0, "resolved_path"] == "src/com/acme/FooTest.java"

    # Against HEAD (the old behaviour) the same id does not bind.
    unbound = bind_tests(frame(), {REPO: head_sha(clone)}, tmp_path)
    assert unbound.loc[0, "status"] != "exact"


def test_a_missing_pinned_sha_is_rejected(tmp_path: Path) -> None:
    clone = make_repo(tmp_path)
    assert is_usable_clone(clone)  # HEAD alone would have passed
    assert not is_usable_clone(clone, pin="0" * 40)
    assert is_usable_clone(clone, pin=head_sha(clone))


@requires_data(PARSED_OUTCOMES.as_posix())
def test_missing_clones_flags_a_repo_whose_pin_is_absent_or_unpinned(tmp_path: Path) -> None:
    repos = corpus_repos()
    pins = {}
    for r in repos:
        path = clone_dir_for(r, tmp_path)
        path.mkdir(parents=True)
        git(path, "init", "-q")
        (path / "T.java").write_text("x\n", encoding="utf-8")
        git(path, "add", ".")
        git(path, "commit", "-qm", "c")
        pins[r] = head_sha(path)
    assert missing_clones(clones_dir=tmp_path, pins=pins) == []
    pins[repos[0]] = "f" * 40
    del pins[repos[1]]
    assert missing_clones(clones_dir=tmp_path, pins=pins) == sorted([repos[0], repos[1]])


def test_a_blobless_clone_passes_at_its_pin(tmp_path: Path) -> None:
    src = make_repo(tmp_path / "src")
    git(src, "config", "uploadpack.allowFilter", "true")
    dst = tmp_path / "dst" / "acme__widgets"
    dst.parent.mkdir()
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "clone", "-q", "--filter=blob:none",
         f"file://{src}", str(dst)],
        check=True, capture_output=True, env=ENV,
    )
    # Blobs are not local, trees are: the pinned tree is all binding needs.
    assert is_usable_clone(dst, pin=head_sha(dst))


@requires_data(PARSED_OUTCOMES.as_posix())
def test_write_pins_records_head_deterministically(tmp_path: Path) -> None:
    clones = tmp_path / "clones"
    for r in corpus_repos():
        path = clone_dir_for(r, clones)
        path.mkdir(parents=True)
        git(path, "init", "-q")
        (path / "T.java").write_text("x\n", encoding="utf-8")
        git(path, "add", ".")
        git(path, "commit", "-qm", "c")
    out = tmp_path / "pins.json"
    first = write_pins(clones_dir=clones, path=out)
    text = out.read_text(encoding="utf-8")
    write_pins(clones_dir=clones, path=out)
    assert out.read_text(encoding="utf-8") == text
    assert load_pins(out) == first
    assert set(first) == set(corpus_repos())
    assert all(first[r] == head_sha(clone_dir_for(r, clones)) for r in first)


def test_load_pins_refuses_when_the_file_is_absent(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        load_pins(tmp_path / "nope.json")
