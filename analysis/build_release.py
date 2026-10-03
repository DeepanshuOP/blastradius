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
holds. When `BR_PSEUDONYM_KEY` is absent from the environment this script still
builds the bundle -- the Architect asked for a local build -- but writes
`NOT_PUBLISHABLE.md` into the tree and says so on stdout. Presence is checked by
key NAME only; the value is never read, printed or logged.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil

import duckdb

__all__ = ["CANARY", "DATASET_NAME", "build", "checksum_manifest"]

DATASET_NAME = "BR-Bench"
PSEUDONYM_KEY_NAME = "BR_PSEUDONYM_KEY"

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


def build(out_dir: Path, interim: Path) -> dict[str, int]:
    """Assemble the bundle and return each table's row count.

    Args:
        out_dir: Bundle root to create (removed first if present).
        interim: Directory holding the interim parquet artifacts.

    Returns:
        Mapping of shipped filename to row count.
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

    (out_dir / "CANARY.txt").write_text(CANARY_DOC, encoding="utf-8")
    return counts


def main() -> None:
    """Build the bundle, write the manifest, and report the publish blocker."""
    parser = argparse.ArgumentParser(description=f"Build the {DATASET_NAME} bundle")
    parser.add_argument("--out-dir", type=Path, default=Path("release/v0.1"))
    parser.add_argument("--interim", type=Path, default=Path("data/interim"))
    args = parser.parse_args()

    counts = build(args.out_dir, args.interim)

    # Key NAME only. The value is never read.
    pseudonymised = PSEUDONYM_KEY_NAME in os.environ
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
        print("\npseudonymisation: key present by name; apply it before publishing")
    else:
        print(
            f"\nBLOCKED: {PSEUDONYM_KEY_NAME} absent from the environment.\n"
            f"  author_login is NOT pseudonymised; wrote NOT_PUBLISHABLE.md.\n"
            f"  Add {PSEUDONYM_KEY_NAME} to .env and rebuild before any upload.\n"
            "  Zenodo deposit and DOI remain ONE-WAY and unstarted."
        )


if __name__ == "__main__":
    main()
