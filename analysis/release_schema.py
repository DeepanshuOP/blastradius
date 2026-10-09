"""Generate `schema.json` from the "Release schema v0.2 (D-54)" section of docs/SCHEMAS.md.

The markdown tables are the contract; this module only transcribes them, so the
JSON cannot drift from the prose. Each `### <table>.parquet` heading opens a
table whose rows are `| column | type | nullable | coverage | source |`.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

__all__ = ["SECTION_HEADING", "generate", "parse_section"]

SECTION_HEADING = "## Release schema v0.2 (D-54)"
_TYPE_RE = re.compile(r"^[A-Z]+(?:\[\])?")
_NAME_RE = re.compile(r"^`?([A-Za-z_][A-Za-z0-9_]*)`?(?:\s*\((?:NEW|CAST|FILLED)\))?$")


def parse_section(text: str) -> dict[str, list[dict]]:
    """Parse the v0.2 section into per-table column specs.

    Args:
        text: Full contents of docs/SCHEMAS.md.

    Returns:
        Mapping of file name (`instances.parquet`) to an ordered list of
        `{"name", "type", "nullable", "enum"}` dicts; `enum` is a sorted list
        or `None`.

    Raises:
        ValueError: If the section is missing or a table row cannot be parsed.
    """
    if SECTION_HEADING not in text:
        raise ValueError(f"{SECTION_HEADING!r} not found")
    tables: dict[str, list[dict]] = {}
    current: str | None = None
    for line in text.split(SECTION_HEADING, 1)[1].splitlines():
        heading = re.match(r"^### (\w+\.parquet)", line)
        if heading:
            current = heading.group(1)
            tables[current] = []
            continue
        if current is None or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] in ("column", "") or set(cells[0]) <= {"-", " "}:
            continue
        name = _NAME_RE.match(cells[0])
        type_ = _TYPE_RE.match(cells[1])
        if not name or not type_ or cells[2] not in ("yes", "no"):
            continue  # a prose table row (e.g. Not shipped), not a column spec
        enum = None
        if "enum" in cells[1]:
            enum = sorted(re.findall(r"`([^`]+)`", cells[1].split("enum", 1)[1]))
        tables[current].append({
            "name": name.group(1), "type": type_.group(0),
            "nullable": cells[2] == "yes", "enum": enum,
        })
    tables = {k: v for k, v in tables.items() if v}
    if not tables:
        raise ValueError("no column tables parsed")
    return tables


def generate(schemas_md: Path, out: Path) -> dict:
    """Write `schema.json` for release v0.2.

    Args:
        schemas_md: Path to docs/SCHEMAS.md.
        out: Destination `schema.json`.

    Returns:
        The schema document written.
    """
    doc = {
        "release_schema": "v0.2",
        "decision": "D-54",
        "source": "docs/SCHEMAS.md#release-schema-v02-d-54",
        "tables": parse_section(schemas_md.read_text(encoding="utf-8")),
    }
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return doc


if __name__ == "__main__":
    generate(Path(sys.argv[1]), Path(sys.argv[2]))
