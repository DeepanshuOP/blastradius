"""`make tables` must never fetch; the fetch is the explicit `fetch-base-logs`.

D-49: the PAT-gated fetch inside `tables` ran silently whenever a token was in
the shell, moving base logs under the pinned corpus. It now lives in its own
target. The fixture is the real `Makefile`, queried with `make -n` (dry run, so
nothing executes and no network is touched).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from src.harvest.ratelimit import DEFAULT_ENV_KEYS

REPO_ROOT = Path(__file__).resolve().parent.parent
FETCH_SCRIPT = "fetch_base_logs"


def _make_n(target: str, **env: str) -> subprocess.CompletedProcess[str]:
    """Dry-run `make -n <target>` with only `env` as PAT variables."""
    clean = {k: v for k, v in os.environ.items() if not k.startswith("GITHUB_PAT")}
    clean.update(env)
    return subprocess.run(
        ["make", "-n", target],
        capture_output=True,
        text=True,
        env=clean,
        cwd=REPO_ROOT,
    )


@pytest.mark.parametrize("env", [{}, {"GITHUB_PAT_1": "dummy"}])
def test_tables_never_mentions_the_fetch(env: dict[str, str]) -> None:
    """With or without a PAT, `make -n tables` has no fetch_base_logs."""
    proc = _make_n("tables", **env)
    assert proc.returncode == 0, proc.stderr
    assert FETCH_SCRIPT not in proc.stdout


@pytest.mark.parametrize("key", DEFAULT_ENV_KEYS)
def test_fetch_target_accepts_any_single_token(key: str) -> None:
    """Each key TokenPool accepts is enough for the explicit target."""
    proc = _make_n("fetch-base-logs", **{key: "dummy"})
    assert proc.returncode == 0, proc.stderr
    assert "analysis/fetch_base_logs.py" in proc.stdout


def test_fetch_target_requires_a_pat() -> None:
    """Without any token the explicit target refuses (the gate is a real shell)."""
    gate = subprocess.run(
        ["make", "fetch-base-logs"],
        capture_output=True,
        text=True,
        env={k: v for k, v in os.environ.items() if not k.startswith("GITHUB_PAT")}
        | {"PATH": os.environ["PATH"]},
        cwd=REPO_ROOT,
    )
    assert gate.returncode != 0
    assert "GITHUB_PAT" in gate.stderr
