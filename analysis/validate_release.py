"""T1.6a: validate a release directory against `schema.json`.

Checks, per table: the file exists, the column set equals the schema's (no
missing, no extra), each column's DuckDB type equals the declared type, every
`nullable: false` column holds no NULL, and every enum column holds only
declared values. DuckDB only; reads, never writes.

Usage: ``python analysis/validate_release.py <release_dir> <schema.json>``
Exit 0 prints ``PASS``; exit 1 prints ``FAIL`` and one line per violation.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import duckdb

__all__ = ["validate"]


def validate(release_dir: Path, schema_json: Path) -> list[str]:
    """Check every table in `schema_json` against `release_dir`.

    Args:
        release_dir: Directory holding the parquet files.
        schema_json: Schema produced by `analysis/release_schema.py`.

    Returns:
        Violation messages; empty when the release conforms.
    """
    schema = json.loads(schema_json.read_text(encoding="utf-8"))["tables"]
    con = duckdb.connect()
    errors: list[str] = []
    for fname, cols in sorted(schema.items()):
        path = release_dir / fname
        if not path.exists():
            errors.append(f"{fname}: file missing")
            continue
        src = f"read_parquet('{path.as_posix()}')"
        actual = {r[0]: r[1] for r in con.execute(f"describe select * from {src}").fetchall()}
        want = {c["name"]: c for c in cols}
        for name in sorted(set(want) - set(actual)):
            errors.append(f"{fname}: missing column {name}")
        for name in sorted(set(actual) - set(want)):
            errors.append(f"{fname}: unexpected column {name}")
        for name in sorted(set(want) & set(actual)):
            spec, col = want[name], f'"{name}"'
            if actual[name] != spec["type"]:
                errors.append(f"{fname}.{name}: type {actual[name]} != {spec['type']}")
            if not spec["nullable"]:
                n = con.execute(f"select count(*) from {src} where {col} is null").fetchone()[0]
                if n:
                    errors.append(f"{fname}.{name}: {n} NULLs in a non-nullable column")
            if spec["enum"] is not None:
                bad = [r[0] for r in con.execute(
                    f"select distinct {col} from {src} where {col} is not null "
                    f"and {col} not in (select unnest(?::varchar[]))", [spec["enum"]]).fetchall()]
                if bad:
                    errors.append(f"{fname}.{name}: values outside enum: {sorted(bad)[:5]}")
    return errors


def main(argv: list[str]) -> int:
    """CLI entry point; see module docstring."""
    errors = validate(Path(argv[1]), Path(argv[2]))
    if errors:
        print(f"FAIL ({len(errors)} violations)")
        for e in errors:
            print(f"  {e}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
