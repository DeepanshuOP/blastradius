"""`author_login` must never leave `analysis/build_release.py` in the clear.

ROADMAP 22.4 makes the pseudonymisation of `author_login` a release blocker.
Commit 1343287 shipped a bundle that only *checked for the key by name* and
copied the column through untouched, so the blocker was reported as cleared
while 165,349 live logins sat in `release/v0.1/instances.parquet`. These tests
pin both halves of the fix: the digest itself against an independently computed
reference, and `build()` end to end against a real parquet file.
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

import duckdb
import pytest

from analysis.build_release import (
    PSEUDONYM_HEX_LEN,
    build,
    checksum_manifest,
    pseudonymise,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
VECTORS = REPO_ROOT / "tests/fixtures/release/pseudonym_vectors.csv"
TEST_KEY = b"br-bench-test-key-do-not-use"

#: Login shapes the corpus really contains, without naming a real account; see
#: tests/fixtures/release/README.md for why no corpus login is checked in.
SAMPLE_LOGINS = ["octocat", "dependabot[bot]", "a", "ünïcödé-user", None]


def _vectors() -> list[tuple[str, str]]:
    with VECTORS.open(encoding="utf-8", newline="") as handle:
        return [(row["login"], row["pseudonym"]) for row in csv.DictReader(handle)]


@pytest.mark.parametrize("login,expected", _vectors())
def test_pseudonymise_matches_reference_hmac(login: str, expected: str) -> None:
    """The digest matches the openssl-computed vector, byte for byte."""
    assert pseudonymise(login, TEST_KEY) == expected


def test_pseudonymise_is_deterministic_and_key_separated() -> None:
    """Same key, same pseudonym; different key, different pseudonym."""
    assert pseudonymise("octocat", TEST_KEY) == pseudonymise("octocat", TEST_KEY)
    assert pseudonymise("octocat", TEST_KEY) != pseudonymise("octocat", b"other-key")


def test_pseudonymise_is_injective_over_the_vectors() -> None:
    """Distinct logins must not collapse onto one pseudonym."""
    pseudonyms = [p for _, p in _vectors()]
    assert len(set(pseudonyms)) == len(pseudonyms)
    assert all(len(p) == PSEUDONYM_HEX_LEN for p in pseudonyms)


@pytest.fixture()
def interim(tmp_path: Path) -> Path:
    """A real interim directory holding a real `instances_raw.parquet`."""
    out = tmp_path / "interim"
    out.mkdir()
    con = duckdb.connect()
    con.execute("create table t(instance_id varchar, repo varchar, author_login varchar)")
    con.executemany(
        "insert into t values (?, ?, ?)",
        [(f"i{n}", "o/r", login) for n, login in enumerate(SAMPLE_LOGINS)],
    )
    # Duplicate one login so the distinct-count assertion is not trivially the
    # row count.
    con.execute("insert into t values ('i99', 'o/r', 'octocat')")
    con.execute(
        f"copy t to '{(out / 'instances_raw.parquet').as_posix()}' (format parquet)"
    )
    return out


def _logins(table: Path) -> list[str | None]:
    con = duckdb.connect()
    return [
        row[0]
        for row in con.execute(
            f"select author_login from read_parquet('{table.as_posix()}') "
            "order by instance_id"
        ).fetchall()
    ]


def test_build_with_key_replaces_every_login(tmp_path: Path, interim: Path) -> None:
    """With a key, no raw login survives and every value is a hex pseudonym."""
    out = tmp_path / "bundle"
    counts = build(out, interim, key=TEST_KEY)

    assert counts["_authors_pseudonymised"] == 4  # distinct non-null logins
    shipped = _logins(out / "instances.parquet")
    real = {login for login in SAMPLE_LOGINS if login is not None}

    assert not real & {value for value in shipped if value is not None}
    for value in shipped:
        if value is None:
            continue
        assert len(value) == PSEUDONYM_HEX_LEN
        assert set(value) <= set("0123456789abcdef"), "pseudonym is not lowercase hex"
    assert shipped.count(None) == 1, "a null login must stay null, not become a hash"
    assert pseudonymise("octocat", TEST_KEY) in shipped


def test_build_without_key_raises_and_touches_nothing(
    tmp_path: Path, interim: Path
) -> None:
    """No key: build() refuses before creating or removing anything."""
    out = tmp_path / "bundle"
    with pytest.raises(ValueError):
        build(out, interim, key=b"")
    assert not out.exists()

    out.mkdir()
    (out / "keep.txt").write_text("existing bundle", encoding="utf-8")
    with pytest.raises(ValueError):
        build(out, interim, key=b"")
    assert [p.name for p in out.iterdir()] == ["keep.txt"]


def _run_main(out: Path, interim: Path, key: str | None) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != "BR_PSEUDONYM_KEY"}
    if key is not None:
        env["BR_PSEUDONYM_KEY"] = key
    return subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "analysis/build_release.py"),
            "--out-dir",
            str(out),
            "--interim",
            str(interim),
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_without_key_exits_nonzero_and_writes_no_files(
    tmp_path: Path, interim: Path
) -> None:
    """The CLI without BR_PSEUDONYM_KEY exits 1 and leaves no bundle, partial or whole."""
    out = tmp_path / "bundle"
    result = _run_main(out, interim, key=None)

    assert result.returncode != 0
    assert "BR_PSEUDONYM_KEY" in result.stderr
    assert not out.exists(), "a partial bundle directory was created"
    assert list(tmp_path.rglob("NOT_PUBLISHABLE.md")) == []


def test_cli_with_key_succeeds_without_not_publishable(
    tmp_path: Path, interim: Path
) -> None:
    """With a key the CLI exits 0, ships a manifest, and never writes NOT_PUBLISHABLE.md."""
    out = tmp_path / "bundle"
    result = _run_main(out, interim, key="cli-test-key")

    assert result.returncode == 0, result.stderr
    assert (out / "CHECKSUMS.sha256").exists()
    assert not (out / "NOT_PUBLISHABLE.md").exists()
    assert "cli-test-key" not in result.stdout + result.stderr


def test_pseudonymisation_is_byte_stable_across_rebuilds(
    tmp_path: Path, interim: Path
) -> None:
    """Two builds under one key agree on every shipped byte (determinism)."""
    first = tmp_path / "a"
    second = tmp_path / "b"
    build(first, interim, key=TEST_KEY)
    build(second, interim, key=TEST_KEY)
    assert checksum_manifest(first) == checksum_manifest(second)


def test_no_leftover_temp_table_in_the_bundle(tmp_path: Path, interim: Path) -> None:
    """The in-place rewrite must not leave its scratch parquet behind."""
    out = tmp_path / "bundle"
    build(out, interim, key=TEST_KEY)
    assert [p.name for p in sorted(out.glob("*.pseudonymised.parquet"))] == []
