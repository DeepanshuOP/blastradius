"""`make tables` is offline by construction (BR_OFFLINE=1).

Real Makefile via `make -n`; the socket guard replaces `socket.socket` so any
attempt to open one fails the test, rather than mocking an HTTP library.
"""

from __future__ import annotations

import os
import socket
import subprocess
from pathlib import Path

import pytest

from src.harvest.ratelimit import OfflineError, TokenPool, get_with_backoff

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("env", [{}, {"GITHUB_PAT_1": "dummy"}])
def test_make_tables_mentions_no_network_step(env: dict[str, str]) -> None:
    clean = {k: v for k, v in os.environ.items() if not k.startswith("GITHUB_PAT")}
    clean.update(env)
    proc = subprocess.run(
        ["make", "-n", "tables"], capture_output=True, text=True, env=clean, cwd=REPO_ROOT
    )
    assert proc.returncode == 0, proc.stderr
    assert "resolve_bases" not in proc.stdout
    assert "fetch_base_logs" not in proc.stdout


def test_make_tables_exports_br_offline() -> None:
    """The Makefile exports it to the `tables` recipe (and nothing else)."""
    lines = (REPO_ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
    assert "tables: export BR_OFFLINE=1" in lines
    assert not any(ln.startswith(("resolve-bases:", "fetch-base-logs:")) and "BR_OFFLINE" in ln
                   for ln in lines)


def test_resolve_bases_is_its_own_target() -> None:
    proc = subprocess.run(
        ["make", "-n", "resolve-bases"],
        capture_output=True, text=True, cwd=REPO_ROOT,
        env={**{k: v for k, v in os.environ.items() if not k.startswith("GITHUB_PAT")},
             "GITHUB_PAT_2": "dummy"},
    )
    assert proc.returncode == 0, proc.stderr
    assert "analysis/resolve_bases.py" in proc.stdout


def test_get_with_backoff_refuses_offline_without_opening_a_socket(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("BR_OFFLINE", "1")
    monkeypatch.setattr("src.harvest.ratelimit.LOG_PATH", tmp_path / "requests.jsonl")
    opened: list[object] = []

    def no_socket(*a: object, **k: object) -> None:
        opened.append(a)
        raise AssertionError("a socket was opened under BR_OFFLINE=1")

    monkeypatch.setattr(socket, "socket", no_socket)
    monkeypatch.setattr(socket, "create_connection", no_socket)
    with pytest.raises(OfflineError):
        get_with_backoff("https://api.github.com/rate_limit", pool=TokenPool(["x"]))
    assert opened == []
    assert not (tmp_path / "requests.jsonl").exists()
