"""Each BR-Seeded operator on a hand-written snippet: exact text and one hunk."""

import difflib

import pytest

from src.eval.seeded.mutate import OPERATORS, Mutation, apply, find_mutations

SNIPPET = '''\
class Cart:
    def total(self, items, limit):
        if len(items) > limit:
            return False
        n = len(items) + 1
        for i in range(3):
            n += items[1]
        return True

def ok(a, b):
    return a == b
'''


def only(op: str) -> list[Mutation]:
    return [m for m in find_mutations(SNIPPET) if m.operator == op]


def hunks(before: str, after: str) -> int:
    diff = list(difflib.unified_diff(before.splitlines(), after.splitlines(), lineterm="", n=3))
    return sum(1 for d in diff if d.startswith("@@"))


def test_cmp_flip() -> None:
    ms = only("CMP_FLIP")
    assert [(m.line, m.old, m.new, m.function) for m in ms] == [(3, ">", ">=", "Cart.total"), (11, "==", "!=", "ok")]
    assert apply(SNIPPET, ms[0]).splitlines()[2] == "        if len(items) >= limit:"


def test_arith_swap() -> None:
    (m,) = only("ARITH_SWAP")
    assert (m.line, m.old, m.new) == (5, "+", "-")
    assert apply(SNIPPET, m).splitlines()[4] == "        n = len(items) - 1"


def test_negate_cond_wraps_the_test_only() -> None:
    (m,) = only("NEGATE_COND")
    assert apply(SNIPPET, m).splitlines()[2] == "        if not (len(items) > limit):"


def test_off_by_one_in_range_and_subscript() -> None:
    ms = only("OFF_BY_ONE")
    assert [(m.line, m.old, m.new) for m in ms] == [(6, "3", "4"), (7, "1", "2")]
    assert apply(SNIPPET, ms[0]).splitlines()[5] == "        for i in range(4):"
    assert apply(SNIPPET, ms[1]).splitlines()[6] == "            n += items[2]"


def test_bool_return() -> None:
    ms = only("BOOL_RETURN")
    assert [(m.line, m.old, m.new) for m in ms] == [(4, "False", "True"), (8, "True", "False")]


@pytest.mark.parametrize("op", OPERATORS)
def test_every_edit_is_one_hunk_and_keeps_everything_else(op: str) -> None:
    for m in only(op):
        out = apply(SNIPPET, m)
        assert hunks(SNIPPET, out) == 1
        assert sum(1 for a, b in zip(SNIPPET.splitlines(), out.splitlines()) if a != b) == 1
        assert out.count("\n") == SNIPPET.count("\n")


def test_apply_refuses_a_stale_span() -> None:
    (m,) = only("ARITH_SWAP")
    with pytest.raises(ValueError):
        apply(SNIPPET.replace("+ 1", "+ 2").replace("n = len", "nn = len"), m)


def test_non_ascii_columns_are_byte_offsets() -> None:
    src = 'def f(a):\n    s = "é"; return a < 3\n'
    (m,) = [m for m in find_mutations(src) if m.operator == "CMP_FLIP"]
    assert apply(src, m) == 'def f(a):\n    s = "é"; return a <= 3\n'


def test_unparsable_source_yields_nothing() -> None:
    assert find_mutations("def (:\n") == []


# ---- hard-distractor edits -----------------------------------------------------------------------
HARD_SRC = '''\
def total(items, rate):
    """Sum with tax."""
    base = sum(items)
    return base + base * rate
'''


def test_noop_edits_on_a_hand_written_function() -> None:
    from src.eval.seeded.hard import apply_edits, functions_of, noop_edit

    (fn,) = functions_of("m.py", HARD_SRC)
    assert (fn.qualname, fn.first_stmt_line, fn.first_stmt_col) == ("total", 3, 4)
    e = noop_edit(HARD_SRC, fn)
    # the first single-line assignment/return in the body gets redundant parentheses on its right-hand side
    assert e == ("PARENS", 3, 11, "sum(items)", "(sum(items))")
    assert apply_edits(HARD_SRC, [e]).splitlines()[2] == "    base = (sum(items))"
    comment = ("COMMENT", 3, 0, "", "    # reviewed: no functional change intended\n")
    out = apply_edits(HARD_SRC, [comment, e]).splitlines()
    assert out[2] == "    # reviewed: no functional change intended" and out[3] == "    base = (sum(items))"
    assert out[:2] == HARD_SRC.splitlines()[:2] and len(out) == 5


def test_a_distractor_that_changes_a_test_outcome_is_rejected(tmp_path) -> None:
    import subprocess
    import sys
    from pathlib import Path

    from src.eval.seeded.hard import suite_outcome_same

    (tmp_path / "m.py").write_text("def f(x):\n    return x + 1\n")
    (tmp_path / "test_m.py").write_text("from m import f\n\n\ndef test_f():\n    assert f(1) == 2\n")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    old = {"m.py": (tmp_path / "m.py").read_text()}
    py = Path(sys.executable)
    noop = {"m.py": "def f(x):\n    return (x + 1)\n"}
    breaking = {"m.py": "def f(x):\n    return x + 2\n"}
    assert suite_outcome_same(tmp_path, py, old, noop, set(), set()) is True
    assert suite_outcome_same(tmp_path, py, old, breaking, set(), set()) is False
    assert (tmp_path / "m.py").read_text() == old["m.py"]  # restored either way
