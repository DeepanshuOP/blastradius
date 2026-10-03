"""Freshness guard: refuse to regenerate tables from a stale interim artifact.

Why this exists
---------------
On 2026-10-03 `data/interim/outcomes.parquet` (mtime 2026-08-31 21:02) was found
to predate `data/interim/parsed_outcomes.parquet` (2026-09-02 16:51), which is
one of its four inputs. The labels had never been rebuilt after that parse, and
33 `test_id` values existed only in the vanished parse generation. Every figure
derived from that `outcomes.parquet` -- Gate 1's strict positive count among them
-- was therefore computed against inputs that were no longer on disk, and nothing
in the pipeline complained. See DECISIONS.md D-49.

`make tables` runs this first. A gate placed behind a step that can fail is not a
gate, so this runs before any regeneration, and exits non-zero on the first
staleness it finds.

What is checked
---------------
Only derivation edges that are read directly out of the pipeline source, so the
guard cannot drift from the code it guards:

- `base_outcomes.parquet` <- `base_resolution_new.parquet`
  (`analysis/parse_base_logs.py`, `run()`)
- `outcomes.parquet` <- `base_resolution_new.parquet`, `instances_raw.parquet`,
  `parsed_outcomes.parquet`, `base_outcomes.parquet`
  (`src/label/fault_revealing.py`, `__main__`)

What is deliberately NOT checked
--------------------------------
`parsed_outcomes.parquet` against the raw logs under `data/raw/`. Raw logs are
pruned and re-fetched by design (success-run logs are deleted after parsing per
the storage constraint), so their mtimes move for reasons that say nothing about
whether the parse is current. Comparing against them would raise false alarms,
and a guard that cries wolf gets disabled. The parse's own currency is pinned by
`CORPUS_PIN.json` instead.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

__all__ = ["DERIVATIONS", "Staleness", "find_stale", "format_report"]

DEFAULT_ROOT = Path("data/interim")

#: artifact -> the inputs it is derived from, as read from the pipeline source.
DERIVATIONS: dict[str, tuple[str, ...]] = {
    "base_outcomes.parquet": ("base_resolution_new.parquet",),
    "outcomes.parquet": (
        "base_resolution_new.parquet",
        "instances_raw.parquet",
        "parsed_outcomes.parquet",
        "base_outcomes.parquet",
    ),
}


@dataclass(frozen=True)
class Staleness:
    """One artifact that is older than one of its inputs.

    Attributes:
        artifact: Name of the derived artifact, relative to the interim root.
        artifact_mtime_ns: Modification time of the artifact, in nanoseconds.
        input_name: Name of the input that is newer than the artifact.
        input_mtime_ns: Modification time of that input, in nanoseconds.
    """

    artifact: str
    artifact_mtime_ns: int
    input_name: str
    input_mtime_ns: int

    @property
    def lag_seconds(self) -> float:
        """How far the artifact trails the input, in seconds."""
        return (self.input_mtime_ns - self.artifact_mtime_ns) / 1e9


def find_stale(
    root: Path = DEFAULT_ROOT,
    derivations: dict[str, tuple[str, ...]] | None = None,
) -> tuple[list[Staleness], list[str]]:
    """Find every artifact under `root` that is older than one of its inputs.

    An artifact whose mtime equals its input's is treated as fresh: the pipeline
    writes inputs before outputs, and equal timestamps mean the filesystem could
    not resolve the gap, not that the output is behind.

    A missing artifact or missing input is skipped rather than reported as stale.
    Nothing can be stale if it does not exist, and the regeneration step that
    needs it fails with a more specific error than this guard could give.

    Args:
        root: Directory holding the interim artifacts.
        derivations: Map of artifact name to its input names. Defaults to
            `DERIVATIONS`.

    Returns:
        A pair of (staleness findings, names skipped because a path was absent).
    """
    table = DERIVATIONS if derivations is None else derivations
    findings: list[Staleness] = []
    skipped: list[str] = []

    for artifact, inputs in sorted(table.items()):
        artifact_path = root / artifact
        if not artifact_path.exists():
            skipped.append(f"{artifact} (artifact absent)")
            continue
        artifact_mtime = artifact_path.stat().st_mtime_ns

        for input_name in inputs:
            input_path = root / input_name
            if not input_path.exists():
                skipped.append(f"{artifact} <- {input_name} (input absent)")
                continue
            input_mtime = input_path.stat().st_mtime_ns
            if artifact_mtime < input_mtime:
                findings.append(
                    Staleness(
                        artifact=artifact,
                        artifact_mtime_ns=artifact_mtime,
                        input_name=input_name,
                        input_mtime_ns=input_mtime,
                    )
                )

    return findings, skipped


def format_report(findings: list[Staleness], root: Path) -> str:
    """Render findings as an operator-facing error naming the fix.

    Args:
        findings: Staleness findings, as returned by `find_stale`.
        root: Interim root, for the paths printed in the message.

    Returns:
        The multi-line error text.
    """
    lines = [
        "STALE INTERIM ARTIFACT -- refusing to regenerate tables.",
        "",
        "An artifact is older than an input it is derived from, so any number",
        "computed from it would describe inputs that are no longer on disk.",
        "This is the defect recorded in DECISIONS.md D-49.",
        "",
    ]
    for finding in findings:
        lines += [
            f"  {root / finding.artifact}",
            f"    is older than {root / finding.input_name}",
            f"    by {finding.lag_seconds:,.1f} s",
        ]
    lines += [
        "",
        "Rebuild in dependency order, then re-run `make tables`:",
        "  uv run python analysis/corpus_parse.py --as-of <CORPUS_PIN as_of> --overwrite",
        "  uv run python analysis/parse_base_logs.py",
        "  uv run python src/label/fault_revealing.py",
    ]
    return "\n".join(lines)


def main() -> None:
    """Exit non-zero if any interim artifact is older than one of its inputs."""
    parser = argparse.ArgumentParser(
        description="Refuse to regenerate tables from a stale interim artifact"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=f"Interim artifact directory (default: {DEFAULT_ROOT})",
    )
    args = parser.parse_args()

    findings, skipped = find_stale(args.root)
    for name in skipped:
        print(f"[freshness] skipped: {name}")

    if findings:
        print(format_report(findings, args.root), file=sys.stderr)
        raise SystemExit(1)

    print(
        f"[freshness] OK: {len(DERIVATIONS)} artifacts checked against their inputs "
        f"under {args.root}"
    )


if __name__ == "__main__":
    main()
