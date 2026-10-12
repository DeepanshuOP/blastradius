"""Reviewer challenge (Live Lab, D-65): the seeded choice of a function and an operator is a pure function of the
repository text and the seed. Fixture: the pinned shopcart sample repository (`src/agents/demo/sample_repo`, five
functions with mutations, counted by hand below) and a small hand-written source tree."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.lab import challenge

SRC = '''\
def add(a, b):
    return a + b


class Box:
    def full(self, n):
        if n > 3:
            return True
        return False
'''


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "m.py").write_text(SRC, encoding="utf-8")
    (tmp_path / "pkg" / "test_m.py").write_text("def test_x():\n    assert 1 + 1 == 2\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "helper.py").write_text("def h(x):\n    return x + 1\n", encoding="utf-8")
    return tmp_path


def test_candidates_are_source_functions_with_a_mutation_sorted(tree: Path) -> None:
    c = challenge.candidates(tree, [])
    assert [(x["file"], x["function"]) for x in c] == [("pkg/m.py", "Box.full"), ("pkg/m.py", "add")]
    ops = {x["function"]: sorted({m["operator"] for m in x["mutations"]}) for x in c}
    assert "ARITH_SWAP" in ops["add"] and "CMP_FLIP" in ops["Box.full"]


def test_same_seed_same_choice_and_the_choice_is_a_candidate(tree: Path) -> None:
    c = challenge.candidates(tree, [])
    a, b = challenge.pick(c, 42), challenge.pick(c, 42)
    assert a == b and a["seed"] == 42
    assert (a["file"], a["function"]) in {(x["file"], x["function"]) for x in c}
    line = next(m["line"] for x in c if x["function"] == a["function"] for m in x["mutations"] if m["operator"] == a["operator"])
    assert a["line"] == line


def test_seeds_reach_every_function(tree: Path) -> None:
    c = challenge.candidates(tree, [])
    seen = {challenge.pick(c, s)["function"] for s in range(40)}
    assert seen == {"Box.full", "add"}


def test_empty_repository_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no function"):
        challenge.pick([], 1)


def test_prepared_repository_choice_is_stable() -> None:
    from src.lab.workspace import REPOS

    if not (REPOS / "shopcart").is_dir():
        pytest.skip("data/seeded is not present")
    a = challenge.pick_for("shopcart", 3)
    assert a == challenge.pick_for("shopcart", 3)
    assert a["file"].startswith("shopcart/") and not a["file"].split("/")[-1].startswith("test_")
