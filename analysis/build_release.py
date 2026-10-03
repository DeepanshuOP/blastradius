"""Build the BR-Bench release bundle locally. Nothing here publishes anything.

Naming is fixed by D-08: the project is BlastRadius, the dataset is **BR-Bench**.
That naming becomes one-way only once a DOI is minted, which has not happened,
so this bundle is still freely renameable.

Contents follow ROADMAP 22.1, restricted to tables that exist at this commit:

| 22.1 file | Source | Status |
|---|---|---|
| `instances.parquet` | `data/interim/instances_raw.parquet` | shipped |
| `outcomes.parquet` | `data/interim/outcomes.parquet` | shipped |
| `cochange.parquet` | `data/interim/cochange.parquet` | shipped |
| `failure_messages.parquet` | split out of `parsed_outcomes.parquet` | shipped, separated per 22.1 |
| `graph_nodes` / `graph_edges` | -- | excluded: D-48 keeps the graph layer out of `release/` |
| `gold.parquet` | -- | absent: the causal subset is CUT |
| `identity_map.parquet` | -- | absent: never built |

Pseudonymisation
----------------
`instances.parquet` carries `author_login`, a real GitHub login. The release is
publishable only once that column is pseudonymised under a key the operator
holds, so when `BR_PSEUDONYM_KEY` is set every login is replaced in place by
`HMAC-SHA256(key, login)` truncated to 16 hex characters. The key is read from
the environment and used only as HMAC material: it is never printed, logged,
written into the bundle or included in any error message.

When the key is absent this script still builds the bundle -- the Architect
asked for a local build -- but the logins stay live, so it writes
`NOT_PUBLISHABLE.md` into the tree and says so on stdout.

The mapping is deterministic for a fixed key, which is the point: the same
author is the same pseudonym across tables and across rebuilds, and nobody
without the key can invert it. Rotating the key renames every author.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import os
from pathlib import Path
import shutil

import duckdb

__all__ = [
    "CANARY",
    "DATASET_NAME",
    "PSEUDONYM_HEX_LEN",
    "build",
    "checksum_manifest",
    "pseudonymise",
]

DATASET_NAME = "BR-Bench"
PSEUDONYM_KEY_NAME = "BR_PSEUDONYM_KEY"

#: Truncation length of the hex pseudonym. 16 hex characters is 64 bits, which
#: keeps a collision over a corpus this size (low thousands of authors)
#: negligible while staying short enough to read in a table.
PSEUDONYM_HEX_LEN = 16

#: Documented canary (ROADMAP T1.7, risk T11). A fixed, unique, high-entropy
#: string shipped in the bundle so that if BR-Bench is later absorbed into an
#: LLM training corpus, asking a model to reproduce it detects the
#: contamination. It is deliberately constant across releases: a canary that
#: changes per build cannot be searched for. One line in the datasheet explains
#: it, which is all T1.7 asks for.
CANARY = "BR-BENCH-CANARY-4f9ac1e07b2d4c8ea35d6b0917fe82c5"

CANARY_DOC = f"""# BR-Bench canary string

{CANARY}

This string exists so that contamination of future language-model training
corpora by BR-Bench is detectable. It appears nowhere else. If a model can
reproduce it when prompted, BR-Bench is in its training data, and any evaluation
of that model on BR-Bench is invalid.

Do not remove this file when redistributing the dataset. Do not paste the string
into a public issue, gist, forum post or model prompt -- doing so contaminates
the canary itself and destroys its only purpose.

Governing: ROADMAP T1.7, risk T11.
"""

NOT_PUBLISHABLE = f"""# NOT PUBLISHABLE — {DATASET_NAME} local build

This bundle must not be uploaded, shared or attached to a DOI in its current
form.

`instances.parquet` carries `author_login`, a real GitHub login for every
instance. ROADMAP 22.4 requires that column pseudonymised before release.
`{PSEUDONYM_KEY_NAME}` was absent from the environment when this bundle was
built, so no pseudonymisation was applied and the column holds live logins.

To clear this blocker:

1. Add `{PSEUDONYM_KEY_NAME}=<a long random secret>` to `.env`. Never commit it.
2. Re-run `uv run python analysis/build_release.py`.
3. Confirm this file is gone from the bundle and that `author_login` holds
   16-character hex pseudonyms.

Until then the Zenodo deposit and the DOI stay unstarted. Both are ONE-WAY
(D-08: naming is one-way after a DOI).
"""


def checksum_manifest(root: Path) -> str:
    """Compute a SHA-256 manifest over every file in the bundle.

    Args:
        root: Bundle root directory.

    Returns:
        Manifest text, one `<sha256>  <relative path>` line per file, sorted by
        path so the manifest itself is byte-reproducible.
    """
    lines = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.name == "CHECKSUMS.sha256":
            continue
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
        lines.append(f"{digest.hexdigest()}  {path.relative_to(root).as_posix()}")
    return "\n".join(lines) + "\n"


def pseudonymise(login: str, key: bytes) -> str:
    """Map a GitHub login to its stable pseudonym under `key`.

    Args:
        login: The real GitHub login.
        key: Secret HMAC key, as read from `BR_PSEUDONYM_KEY`.

    Returns:
        The first `PSEUDONYM_HEX_LEN` hex characters of
        `HMAC-SHA256(key, login)`. Deterministic for a fixed key, and not
        invertible without it.
    """
    digest = hmac.new(key, login.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest[:PSEUDONYM_HEX_LEN]


def _pseudonymise_authors(
    con: "duckdb.DuckDBPyConnection", table: Path, key: bytes
) -> int:
    """Rewrite `author_login` in a parquet file in place, under `key`.

    The mapping is built in Python over the distinct logins and joined back, so
    the key never enters a SQL string and the rewrite is a single pass.

    Args:
        con: Open DuckDB connection.
        table: Parquet file to rewrite; must carry an `author_login` column.
        key: Secret HMAC key.

    Returns:
        Number of distinct logins pseudonymised.

    Raises:
        RuntimeError: If any non-null login survives the join unmapped, which
            would mean a real login shipping in the bundle.
    """
    src = table.as_posix()
    logins = [
        row[0]
        for row in con.execute(
            f"select distinct author_login from read_parquet('{src}') "
            "where author_login is not null"
        ).fetchall()
    ]
    con.execute("create or replace temp table pseudo(login varchar, pseudonym varchar)")
    if logins:
        con.executemany(
            "insert into pseudo values (?, ?)",
            [(login, pseudonymise(login, key)) for login in logins],
        )

    tmp = table.with_suffix(".pseudonymised.parquet")
    con.execute(
        f"""copy (
               select i.* replace (p.pseudonym as author_login)
               from read_parquet('{src}') i
               left join pseudo p on i.author_login = p.login
             ) to '{tmp.as_posix()}' (format parquet, compression zstd)"""
    )
    leaked = con.execute(
        f"select count(*) from read_parquet('{tmp.as_posix()}') "
        f"where author_login is not null "
        f"and not regexp_matches(author_login, '^[0-9a-f]{{{PSEUDONYM_HEX_LEN}}}$')"
    ).fetchone()[0]
    if leaked:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(
            f"{leaked} author_login values are not {PSEUDONYM_HEX_LEN}-hex "
            "pseudonyms after the rewrite; refusing to ship the table"
        )
    tmp.replace(table)
    con.execute("drop table pseudo")
    return len(logins)


def build(out_dir: Path, interim: Path, key: bytes | None = None) -> dict[str, int]:
    """Assemble the bundle and return each table's row count.

    Args:
        out_dir: Bundle root to create (removed first if present).
        interim: Directory holding the interim parquet artifacts.
        key: Secret HMAC key for author pseudonymisation. When None the bundle
            is built with live logins and is not publishable.

    Returns:
        Mapping of shipped filename to row count. When `key` is given the
        mapping also carries `"_authors_pseudonymised"`, the distinct-login
        count, so the caller can report it without re-reading the table.
    """
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    con = duckdb.connect()
    counts: dict[str, int] = {}

    copies = {
        "instances.parquet": interim / "instances_raw.parquet",
        "outcomes.parquet": interim / "outcomes.parquet",
        "cochange.parquet": interim / "cochange.parquet",
    }
    for name, source in copies.items():
        if not source.exists():
            continue
        target = out_dir / name
        con.execute(
            f"copy (select * from read_parquet('{source.as_posix()}')) "
            f"to '{target.as_posix()}' (format parquet, compression zstd)"
        )
        counts[name] = con.execute(
            f"select count(*) from read_parquet('{target.as_posix()}')"
        ).fetchone()[0]

    # 22.1 ships failure messages as their own, separately scanned table.
    parsed = interim / "parsed_outcomes.parquet"
    if parsed.exists():
        target = out_dir / "failure_messages.parquet"
        con.execute(
            f"""copy (
                   select repo, run_id, job_id, test_id, failure_message
                   from read_parquet('{parsed.as_posix()}')
                   where failure_message is not null
                 ) to '{target.as_posix()}' (format parquet, compression zstd)"""
        )
        counts["failure_messages.parquet"] = con.execute(
            f"select count(*) from read_parquet('{target.as_posix()}')"
        ).fetchone()[0]

    instances = out_dir / "instances.parquet"
    if key is not None and instances.exists():
        counts["_authors_pseudonymised"] = _pseudonymise_authors(con, instances, key)

    (out_dir / "CANARY.txt").write_text(CANARY_DOC, encoding="utf-8")
    return counts


def main() -> None:
    """Build the bundle, write the manifest, and report the publish blocker."""
    parser = argparse.ArgumentParser(description=f"Build the {DATASET_NAME} bundle")
    parser.add_argument("--out-dir", type=Path, default=Path("release/v0.1"))
    parser.add_argument("--interim", type=Path, default=Path("data/interim"))
    args = parser.parse_args()

    # The key is HMAC material only: never printed, logged or written out.
    raw_key = os.environ.get(PSEUDONYM_KEY_NAME) or None
    key = raw_key.encode("utf-8") if raw_key else None

    counts = build(args.out_dir, args.interim, key=key)
    n_authors = counts.pop("_authors_pseudonymised", None)

    pseudonymised = key is not None
    if not pseudonymised:
        (args.out_dir / "NOT_PUBLISHABLE.md").write_text(NOT_PUBLISHABLE, encoding="utf-8")

    (args.out_dir / "CHECKSUMS.sha256").write_text(
        checksum_manifest(args.out_dir), encoding="utf-8"
    )

    print(f"{DATASET_NAME} bundle at {args.out_dir} (D-08 naming)")
    for name in sorted(counts):
        size = (args.out_dir / name).stat().st_size
        print(f"  {name:<28} {counts[name]:>12,} rows  {size:>12,} bytes")
    print(f"  CANARY.txt                   documented canary (T1.7)")
    print(f"  CHECKSUMS.sha256             SHA-256 manifest over every file")

    if pseudonymised:
        print(
            f"\npseudonymisation: APPLIED — {n_authors:,} distinct author_login "
            f"values replaced by {PSEUDONYM_HEX_LEN}-hex HMAC-SHA256 pseudonyms."
        )
        print("  The key itself is never printed, logged or shipped.")
    else:
        print(
            f"\nBLOCKED: {PSEUDONYM_KEY_NAME} absent from the environment.\n"
            f"  author_login is NOT pseudonymised; wrote NOT_PUBLISHABLE.md.\n"
            f"  Add {PSEUDONYM_KEY_NAME} to .env and rebuild before any upload.\n"
            "  Zenodo deposit and DOI remain ONE-WAY and unstarted."
        )


if __name__ == "__main__":
    main()
