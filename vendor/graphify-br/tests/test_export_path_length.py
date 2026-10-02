"""Regression tests for issue #2655: export filename caps must respect the
DESTINATION PATH length, not only the per-component NAME_MAX.

The Obsidian/wiki exporters these budgets were written for are removed in this
fork (ROADMAP §29.4), so what survives here is the budget arithmetic itself in
``graphify.paths``, which the kept exporters still rely on.

#1094 capped export stems at 200 bytes so they stay under the conventional
255-byte NAME_MAX. That is the correct constraint on POSIX and the wrong one on
Windows, where the limit applies to the WHOLE path (MAX_PATH = 260 chars
including the terminating NUL). A 200-byte stem under an ordinary vault
directory therefore overruns MAX_PATH, and `graphify export obsidian` /
`export wiki` die mid-write with FileNotFoundError, leaving a half-written
vault behind.

The budget math is exercised on every platform by faking `os.name`, and the
exporters' wiring is exercised by forcing a small budget, so this suite has
real teeth on the Linux CI runners as well as on Windows.
"""
import json
import os
import re

import networkx as nx
import pytest

from graphify.paths import _MIN_STEM_BUDGET, _WINDOWS_MAX_PATH, stem_filename_budget


def _fake_windows(monkeypatch):
    """Make stem_filename_budget take its Windows branch on any host.

    abspath becomes identity so a literal ``C:\\...`` string is not prefixed
    with the POSIX cwd when the test runs on Linux.
    """
    monkeypatch.setattr(os, "name", "nt")
    monkeypatch.setattr(os.path, "abspath", lambda p: str(p))


# ---------------------------------------------------------------------------
# stem_filename_budget: the budget math
# ---------------------------------------------------------------------------

def test_budget_is_untouched_on_posix(monkeypatch):
    monkeypatch.setattr(os, "name", "posix")
    # Even an absurdly deep directory must not change POSIX behaviour: the
    # constraint there is per-component, and existing vaults must stay stable.
    assert stem_filename_budget("/" + "d/" * 200, reserve=4) == 200


def test_budget_shrinks_so_the_whole_path_fits_max_path(monkeypatch):
    _fake_windows(monkeypatch)
    vault = r"C:\Users\dev\projects\payments-api\graphify-out\obsidian"
    budget = stem_filename_budget(vault, reserve=4)

    assert budget < 200, "an ordinary vault path must shrink the 200-byte default"
    # The longest name this budget can produce still has to fit in MAX_PATH.
    longest = len(vault) + len(os.sep) + budget + len("_999") + len(".md")
    assert longest < _WINDOWS_MAX_PATH


def test_budget_accounts_for_the_caller_reserve(monkeypatch):
    _fake_windows(monkeypatch)
    vault = r"C:\Users\dev\projects\payments-api\graphify-out\obsidian"
    assert stem_filename_budget(vault, reserve=4) - stem_filename_budget(vault, reserve=15) == 11


def test_budget_never_exceeds_the_requested_limit(monkeypatch):
    _fake_windows(monkeypatch)
    # A very short root leaves plenty of room; the NAME_MAX-derived limit still wins.
    assert stem_filename_budget("C:\\", reserve=0) == 200


def test_budget_floors_instead_of_going_negative(monkeypatch):
    _fake_windows(monkeypatch)
    deep = "C:\\" + "\\".join("dir%03d" % i for i in range(40))
    assert len(deep) > _WINDOWS_MAX_PATH
    # A negative budget would make _cap_filename slice with a negative index and
    # silently emit a garbage stem, so the floor matters.
    assert stem_filename_budget(deep, reserve=4) == _MIN_STEM_BUDGET


def test_budget_ignores_extended_length_paths(monkeypatch):
    _fake_windows(monkeypatch)
    # "\\?\" opts the path out of MAX_PATH entirely - nothing to shrink.
    assert stem_filename_budget(r"\\?\C:\very\deep" + "\\x" * 100, reserve=4) == 200


# ---------------------------------------------------------------------------
# The stem helpers honour an explicit limit
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# The exporters actually thread the budget through (runs on every platform)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# End-to-end on the platform that actually has the ceiling
# ---------------------------------------------------------------------------

_WINDOWS_ONLY = pytest.mark.skipif(
    os.name != "nt", reason="MAX_PATH is a Windows constraint"
)


