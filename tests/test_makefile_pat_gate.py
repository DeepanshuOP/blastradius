"""The `make tables` base-log fetch must be SKIPPED without a PAT, not removed.

D-49's fix made `analysis/fetch_base_logs.py` non-fatal when no GitHub token is
configured. The failure mode this guards against is the gate drifting into a
silent removal of the step: either the fetch leaving the conditional entirely,
or the condition naming fewer tokens than `TokenPool` actually accepts, so an
operator holding only `GITHUB_PAT_2` gets a skip they never asked for.

The fixture is the real `Makefile`. The gate's own shell text is extracted and
executed under `sh` with the fetch stubbed out, so what is asserted is the
branch that really runs, not a regex standing in for it.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from src.harvest.ratelimit import DEFAULT_ENV_KEYS

REPO_ROOT = Path(__file__).resolve().parent.parent
MAKEFILE = REPO_ROOT / "Makefile"
FETCH_SCRIPT = "analysis/fetch_base_logs.py"


def _gate_shell() -> str:
    """Extract the PAT gate from the `tables` recipe as runnable shell.

    Returns:
        The `if ... fi` block with Make's recipe tabs, `$$` escaping and
        line continuations undone, and the fetch command replaced by
        `echo FETCH` so the test needs neither PATs nor the network.
    """
    text = MAKEFILE.read_text(encoding="utf-8")
    match = re.search(
        r"^\t@?(if \[ -n .*?\bfi)$", text, re.MULTILINE | re.DOTALL
    )
    assert match is not None, "no `if [ -n ... ] ... fi` gate found in Makefile"
    block = match.group(1)
    block = block.replace("\\\n", "\n").replace("\t", "")
    block = block.replace("$$", "$")
    block = re.sub(
        rf"uv run python {re.escape(FETCH_SCRIPT)};", "echo FETCH;", block
    )
    return block


def _run_gate(**env: str) -> str:
    """Run the extracted gate with `env` as the ONLY PAT variables set."""
    clean = {"PATH": "/usr/bin:/bin", "HOME": "/nonexistent"}
    clean.update(env)
    proc = subprocess.run(
        ["sh", "-c", _gate_shell()],
        capture_output=True,
        text=True,
        env=clean,
        cwd=REPO_ROOT,
        check=True,
    )
    return proc.stdout


def test_fetch_is_inside_the_conditional() -> None:
    """The fetch must appear only in the gate's then-branch, never bare."""
    gate = _gate_shell()
    assert "echo FETCH" in gate, "fetch command is not inside the gate"

    recipe = MAKEFILE.read_text(encoding="utf-8")
    bare = [
        line
        for line in recipe.splitlines()
        if FETCH_SCRIPT in line and not line.lstrip().startswith("#")
        and "\\" not in line
    ]
    assert bare == [], f"fetch invoked outside the gate: {bare}"


@pytest.mark.parametrize("key", DEFAULT_ENV_KEYS)
def test_any_single_token_runs_the_fetch(key: str) -> None:
    """Each key TokenPool accepts must on its own be enough to fetch."""
    out = _run_gate(**{key: "ghp_stub"})
    assert "FETCH" in out, f"{key} alone did not trigger the fetch: {out!r}"
    assert "SKIP" not in out


def test_no_token_skips_loudly() -> None:
    """With no PAT the step is skipped, and says so rather than failing."""
    out = _run_gate()
    assert "FETCH" not in out
    assert "SKIP" in out
    assert FETCH_SCRIPT in out


def test_empty_token_counts_as_absent() -> None:
    """An exported-but-empty PAT is not a usable token (TokenPool drops it)."""
    out = _run_gate(GITHUB_PAT_1="", GITHUB_PAT_2="", GITHUB_PAT_3="")
    assert "FETCH" not in out
    assert "SKIP" in out
