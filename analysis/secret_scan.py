"""Secret scan over the packaged release bundle.

Promoted from the throwaway ``tmp_scan.py`` that produced the Phase 009-B
secret-scan result. T1.6b makes that result a release blocker, and a blocker
that cannot be re-run is not a blocker.

Scans every ``.parquet`` and ``.csv`` under a release directory for
credential-shaped and identity-shaped strings, using the same four patterns the
009-B scan used. Findings carry one of two severities, so that harvested public
data is never confused with our own credentials (see ``docs/HANDOFF.md`` §12):

* ``BLOCKER`` — ``github_token``, ``bearer_token``. Any hit makes :func:`main`
  exit non-zero, which fails ``make tables``. Neither shape can occur in
  harvested public source data.
* ``REVIEW`` — ``email``, ``internal_host``. Reported, never fatal.

``internal_host`` is REVIEW rather than BLOCKER on measured evidence, not on
convenience. Run against ``release/v0.1`` it produces six matches, all of them
harvested public identifiers and none of them a host we control:
``org.knowm.xchart.internal`` and ``jdk.internal`` are Java package fragments;
``Dockerfile.local``, ``ConnectDialog.internal``, ``heuristicEngine.corp`` and
``org.jkiss.dbeaver.app.local`` are filenames from public repositories. All 25
``email`` matches on the same bundle are Apple asset filenames of the form
``AppIcon-20x20@2x.png``. Gating a release on either class would fail every
build on noise, which is how a blocker stops being read. A real ``.corp`` host
still gets printed for a human to triage — it is just not the thing that stops
the build.

Matched text is never printed in full. Every sample is redacted to its first
three characters plus its length, so running the scan can never itself leak a
credential into a log, a report, or the paper.

Only ``.parquet`` and ``.csv`` are scanned. That matches the 009-B scan exactly
so its result stays reproducible; the bundle's ``.md`` and ``.txt`` members
(``DATASHEET.md``, ``CANARY.txt``) are out of scope for this script.

Importing this module has no side effects. Run it with::

    uv run python analysis/secret_scan.py [--root release] [--as-of ISO8601] [--limit N]
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd

from analysis.cochange_mine import parse_iso_datetime

#: Regex per finding class. Kept byte-identical to the 009-B scan so that
#: result remains reproducible; changing one is a re-scan, not an edit.
PATTERNS: dict[str, str] = {
    "github_token": r"gh[pousr]_[a-zA-Z0-9]{36}",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "bearer_token": r"Bearer\s+[a-zA-Z0-9-._~+/]+",
    "internal_host": r"[a-zA-Z0-9.-]+\.(?:corp|internal|local)",
}

#: Finding classes that block a release. Everything else is advisory. See the
#: module docstring for why ``internal_host`` is not on this list.
BLOCKER_PATTERNS: frozenset[str] = frozenset({"github_token", "bearer_token"})

#: File extensions the 009-B scan covered.
SCANNED_SUFFIXES: tuple[str, ...] = (".parquet", ".csv")

DEFAULT_ROOT = "release"


def redact(value: str) -> str:
    """Reduce a matched string to a non-recoverable summary.

    Args:
        value: The raw matched text. Never returned, never logged.

    Returns:
        The first three characters followed by the total length, e.g.
        ``ghp_…(40)`` becomes ``ghp…(40)``.
    """
    return f"{value[:3]}…({len(value)})"


def scan_text(text: str) -> dict[str, set[str]]:
    """Apply every pattern to one blob of text.

    Args:
        text: Concatenated string values from a single column.

    Returns:
        Mapping of finding class to the set of distinct raw matches. Classes
        with no match are omitted.
    """
    found: dict[str, set[str]] = {}
    for name, pattern in PATTERNS.items():
        matches = set(re.findall(pattern, text))
        if matches:
            found[name] = matches
    return found


def iter_data_files(
    root: Path,
    as_of: datetime.datetime | None = None,
    limit: int | None = None,
) -> tuple[list[Path], int]:
    """Enumerate the release files this scan covers, deterministically.

    Args:
        root: Release directory to walk.
        as_of: If given, files modified strictly after this instant are
            skipped, so a pinned re-run scans the same bundle a past run did.
        limit: If given, stop after this many files. Files are sorted by path
            first, so a limited run is a prefix of the full run rather than an
            arbitrary sample.

    Returns:
        A ``(files, skipped_by_as_of)`` pair.
    """
    candidates = sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and p.suffix in SCANNED_SUFFIXES
    )

    files: list[Path] = []
    skipped = 0
    for path in candidates:
        if as_of is not None:
            mtime = datetime.datetime.fromtimestamp(
                path.stat().st_mtime, tz=datetime.timezone.utc
            )
            if mtime > as_of:
                skipped += 1
                continue
        files.append(path)
        if limit is not None and len(files) >= limit:
            break

    return files, skipped


def scan_file(path: Path) -> list[dict[str, object]]:
    """Scan one parquet or CSV for every pattern, column by column.

    Args:
        path: File to read. Must be ``.parquet`` or ``.csv``.

    Returns:
        One finding dict per (column, finding class) that matched, carrying the
        distinct match count and up to five redacted samples.
    """
    if path.suffix == ".parquet":
        frame = pd.read_parquet(path)
    else:
        frame = pd.read_csv(path)

    findings: list[dict[str, object]] = []
    for column in frame.select_dtypes(include=["object", "string"]).columns:
        text = " ".join(frame[column].dropna().astype(str))
        for name, matches in scan_text(text).items():
            findings.append(
                {
                    "path": str(path),
                    "column": str(column),
                    "pattern": name,
                    "severity": "BLOCKER" if name in BLOCKER_PATTERNS else "REVIEW",
                    "count": len(matches),
                    "samples": [redact(m) for m in sorted(matches)[:5]],
                }
            )
    return findings


def run(
    as_of: str | None = None,
    limit: int | None = None,
    root: str = DEFAULT_ROOT,
) -> dict[str, object]:
    """Scan a release bundle and report every credential-shaped hit.

    Args:
        as_of: ISO-8601 UTC pin. Files modified after it are skipped.
        limit: Maximum number of files to scan.
        root: Release directory to walk.

    Returns:
        Stats dict with ``files_scanned``, ``files_skipped``, ``findings``,
        ``blockers`` and ``review`` keys. ``blockers`` is the number the
        release gate reads.
    """
    root_path = Path(root)
    as_of_dt = parse_iso_datetime(as_of) if as_of else None

    if not root_path.is_dir():
        print(f"No release directory at {root_path}/ — nothing to scan.")
        return {
            "files_scanned": 0,
            "files_skipped": 0,
            "findings": [],
            "blockers": 0,
            "review": 0,
        }

    files, skipped = iter_data_files(root_path, as_of=as_of_dt, limit=limit)

    print(f"Root:      {root_path}")
    print(f"As-of:     {as_of or '(none — scanning current bundle)'}")
    print(f"Patterns:  {', '.join(sorted(PATTERNS))}")
    print(f"Files:     {len(files)} scanned, {skipped} skipped by --as-of")

    findings: list[dict[str, object]] = []
    for path in files:
        print(f"Scanning {path}")
        findings.extend(scan_file(path))

    blockers = sum(1 for f in findings if f["severity"] == "BLOCKER")
    review = len(findings) - blockers

    for finding in findings:
        print(
            f"  [{finding['severity']}] {finding['pattern']} "
            f"in {finding['path']} [{finding['column']}]: "
            f"{finding['count']} unique — samples {finding['samples']}"
        )

    print(f"BLOCKER findings: {blockers}")
    print(f"REVIEW findings:  {review}")
    return {
        "files_scanned": len(files),
        "files_skipped": skipped,
        "findings": findings,
        "blockers": blockers,
        "review": review,
    }


def main(argv: Iterable[str] | None = None) -> int:
    """CLI entry point.

    Returns:
        ``0`` when no BLOCKER finding was made, ``1`` otherwise.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=DEFAULT_ROOT, help="Release directory to scan")
    parser.add_argument(
        "--as-of",
        type=str,
        help="ISO-8601 UTC pin; files modified after it are skipped",
    )
    parser.add_argument("--limit", type=int, help="Limit number of files scanned")
    args = parser.parse_args(list(argv) if argv is not None else None)

    stats = run(as_of=args.as_of, limit=args.limit, root=args.root)
    if stats["blockers"]:
        print("FAIL: credential-shaped strings present in the release bundle.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
