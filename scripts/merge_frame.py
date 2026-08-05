"""Merge the two SEART exports (Java, Python) into data/frame/repos_raw.csv.

Stage 1 of T0.1a (ROADMAP §23.1, §23.3; data/frame/QUERY.md §3). Reads the
two raw SEART CSV exports, verifies they are what the query spec says they
should be, and concatenates them Java-first into a single merged file with
one header row. Does not normalize columns — that is src/harvest/frame.py,
not written yet.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

FRAME_DIR = Path("data/frame")
JAVA_PATH = FRAME_DIR / "seart_a.csv"
PYTHON_PATH = FRAME_DIR / "seart_b.csv"
OUTPUT_PATH = FRAME_DIR / "repos_raw.csv"


def _read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = reader.fieldnames
        rows = list(reader)
    return list(header), rows


def _fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    java_header, java_rows = _read_rows(JAVA_PATH)
    python_header, python_rows = _read_rows(PYTHON_PATH)

    # 2. headers identical
    if java_header != python_header:
        print("Header mismatch.")
        print(f"{JAVA_PATH} header:\n  {java_header}")
        print(f"{PYTHON_PATH} header:\n  {python_header}")
        _fail("headers differ between the two exports")
    header = java_header

    # 3. exactly one distinct mainLanguage per file, and they differ
    java_langs = {row["mainLanguage"] for row in java_rows}
    python_langs = {row["mainLanguage"] for row in python_rows}
    print(f"mainLanguage values in {JAVA_PATH.name}: {sorted(java_langs)}")
    print(f"mainLanguage values in {PYTHON_PATH.name}: {sorted(python_langs)}")
    if len(java_langs) != 1:
        _fail(f"{JAVA_PATH} contains more than one mainLanguage value: {sorted(java_langs)}")
    if len(python_langs) != 1:
        _fail(f"{PYTHON_PATH} contains more than one mainLanguage value: {sorted(python_langs)}")
    if java_langs == python_langs:
        _fail(f"both files report the same mainLanguage: {java_langs}")

    # 4. isFork must be false and license must be non-empty, everywhere
    fork_violations = []
    license_violations = []
    for path, rows in ((JAVA_PATH, java_rows), (PYTHON_PATH, python_rows)):
        for row in rows:
            if row["isFork"].strip().lower() != "false":
                fork_violations.append((path.name, row["name"], row["isFork"]))
            if not row["license"].strip():
                license_violations.append((path.name, row["name"]))

    print(f"isFork violations: {len(fork_violations)}")
    for source, name, value in fork_violations:
        print(f"  VIOLATION isFork={value!r} source={source} repo={name}")

    print(f"empty-license violations: {len(license_violations)}")
    for source, name in license_violations:
        print(f"  VIOLATION license='' source={source} repo={name}")

    if fork_violations or license_violations:
        _fail(
            f"{len(fork_violations)} isFork violation(s), "
            f"{len(license_violations)} empty-license violation(s) — "
            "a form control did not apply as expected"
        )

    # 5. write merged file, Java rows first then Python, one header row
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(java_rows)
        writer.writerows(python_rows)

    # 6. stage-0 attrition report
    java_names = [row["name"] for row in java_rows]
    python_names = [row["name"] for row in python_rows]
    duplicate_names = set(java_names) & set(python_names)

    java_empty_lang = sum(1 for row in java_rows if not row["mainLanguage"].strip())
    python_empty_lang = sum(1 for row in python_rows if not row["mainLanguage"].strip())

    java_last_commits = [row["lastCommit"] for row in java_rows if row["lastCommit"].strip()]
    python_last_commits = [row["lastCommit"] for row in python_rows if row["lastCommit"].strip()]

    print()
    print("=== Stage-0 attrition report ===")
    print(f"Java rows:     {len(java_rows)}")
    print(f"Python rows:   {len(python_rows)}")
    print(f"Combined rows: {len(java_rows) + len(python_rows)}")
    print(f"Duplicate 'name' values across the two files: {len(duplicate_names)}")
    if duplicate_names:
        for name in sorted(duplicate_names):
            print(f"  DUPLICATE: {name}")
    print(f"Rows with empty mainLanguage: Java={java_empty_lang}, Python={python_empty_lang}")
    print(
        f"lastCommit range (Java):   {min(java_last_commits)}  ->  {max(java_last_commits)}"
    )
    print(
        f"lastCommit range (Python): {min(python_last_commits)}  ->  {max(python_last_commits)}"
    )
    print()
    print(f"Wrote {OUTPUT_PATH} ({len(java_rows) + len(python_rows)} data rows + 1 header)")


if __name__ == "__main__":
    main()
