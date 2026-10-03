"""Generate the blank Holdout v5 hand-labelling worksheet.

Why this exists
---------------
The Holdout v5 scoring of 2026-09-04 (`docs/session/080-...`) derived each
fixture's **Expected Class** from the operator's identifier list by rule rather
than taking it as an independent hand label. Under D-38 a scoring event whose
ground truth was produced by any automated extraction is VOID: no measurement
occurred and the corpus is NOT consumed. D-38 further provides that "a voided
corpus may be labelled again by hand and scored once", so the v5 slot is still
open and this regenerates its instrument.

D-38 compliance
---------------
Nothing in the emitted worksheet is produced by BlastRadius parsing logic. In
particular the excerpt window is chosen **content-blind**: it is the final
`EXCERPT_LINES` lines of the log body, with no regex, no grep and no reference
to where failures appear. Choosing an excerpt by searching for failure lines
would be exactly the machine-assisted labelling D-38 forbids. The excerpt is a
locator only; the checked-in fixture is authoritative and its path is printed in
every section.

Every answer field is emitted empty. Build Tool is an answer field, not a given,
because naming the harness would narrow the classification the operator is being
asked to make. Expected Class must be filled independently of the identifier
list -- that independence is the whole point of the re-label.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

__all__ = ["EXCERPT_LINES", "build_worksheet", "section_for"]

FIXTURE_DIR = Path("tests/fixtures/holdout_v5")
DEFAULT_OUT = Path("docs/phase/029-holdout-v5-worksheet.md")

#: Content-blind excerpt window: the final N lines of the log body.
EXCERPT_LINES = 120

HEADER = """# Holdout v5 Hand-Labelling Worksheet (blind re-label under D-38)

**Target corpus**: `tests/fixtures/holdout_v5/` ({n} logs)
**Generated**: {date} by `analysis/build_holdout_v5_worksheet.py`
**Governing decisions**: D-27, D-29, D-37, D-38
**Protocol**: `docs/phase/013B-holdout-v5-protocol.md` (APPROVED, seed `20261111`)
**Supersedes**: `docs/phase/024-holdout-v5-worksheet.md`, whose scoring was VOID
under D-38 because Expected Class was derived by rule rather than hand-labelled.
The corpus was therefore never consumed and is labelled again here.

## How to fill this in

Every field below is blank and must stay blank until a human fills it. No
BlastRadius code, grep or regex produced any value in this file, and none may be
used to fill it (D-38).

1. Open the fixture named in the section. **The full fixture is authoritative.**
   The excerpt is the final {excerpt} lines only, chosen without looking at the
   content, so a failure earlier in the log will not appear in it.
2. Fill **Build Tool** yourself from the log. It is deliberately not given.
3. Fill **Expected Class** as an independent judgement, one of
   `TEST_FAILURE`, `NO_TEST_OUTPUT`, `TEST_RAN_CLEAN`. Do **not** derive it from
   how many identifiers you listed -- deriving it is what voided the last run.
4. Fill **Expected Identifier Count** and **Expected Identifiers**. Write
   `NO_TEST_OUTCOMES` for the identifier list when there are none.
5. Fill **Confidence** as `CERTAIN` or `UNCERTAIN`.

`analysis/score_holdout_v5.py` refuses to run while any cell is empty, and
refuses to run a second time. Scoring is a single irreversible event (D-37).

## Isolation

Zero job-id overlap with the development fixtures, holdout v1/v2, v3, v4, or with
any log examined during the 2026-10-03 parameter-type characterisation
(`docs/session/holdout-exclusion.txt` and the 13 jobs listed in the step-2
supersession table). Verified before generation.

---
"""

SECTION = """## {index}. `{name}`

- **Fixture path**: `{path}` (authoritative; read this, not the excerpt)
- **Repository**: `{repo}`
- **Content hash (sha256, first 16)**: `{digest}`
- **Body size**: {nbytes:,} bytes, {nlines:,} lines
- **Excerpt**: final {shown} of {nlines:,} lines, content-blind

```text
{excerpt}
```

### Answers (fill every field; leave nothing blank)

- **Build Tool:**
- **Expected Class:**
- **Expected Identifier Count:**
- **Expected Identifiers:**
- **Confidence:**

---
"""


def section_for(index: int, path: Path) -> str:
    """Render one worksheet section for a fixture.

    Args:
        index: 1-based section index.
        path: Path to the checked-in fixture log.

    Returns:
        The section's markdown, with every answer field empty.
    """
    body = path.read_text(encoding="utf-8", errors="replace")
    lines = body.splitlines()
    excerpt = "\n".join(lines[-EXCERPT_LINES:])
    repo = path.name.rsplit("__", 1)[0].replace("__", "/")
    digest = hashlib.sha256(body.encode("utf-8", errors="replace")).hexdigest()[:16]
    return SECTION.format(
        index=index,
        name=path.name,
        path=path.as_posix(),
        repo=repo,
        digest=digest,
        nbytes=len(body.encode("utf-8", errors="replace")),
        nlines=len(lines),
        shown=min(EXCERPT_LINES, len(lines)),
        excerpt=excerpt,
    )


def build_worksheet(fixture_dir: Path, date: str) -> str:
    """Build the whole blank worksheet.

    Args:
        fixture_dir: Directory of checked-in holdout v5 fixtures.
        date: ISO date to stamp in the header.

    Returns:
        The worksheet markdown.

    Raises:
        SystemExit: If the fixture directory holds no `.txt` logs.
    """
    fixtures = sorted(fixture_dir.glob("*.txt"))
    if not fixtures:
        raise SystemExit(f"no fixtures found under {fixture_dir}")
    parts = [
        HEADER.format(n=len(fixtures), date=date, excerpt=EXCERPT_LINES)
    ]
    parts += [section_for(i, p) for i, p in enumerate(fixtures, start=1)]
    return "\n".join(parts)


def main() -> None:
    """Write the blank worksheet to disk."""
    parser = argparse.ArgumentParser(description="Generate the blank v5 worksheet")
    parser.add_argument("--fixture-dir", type=Path, default=FIXTURE_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--date", default="2026-10-03")
    args = parser.parse_args()

    text = build_worksheet(args.fixture_dir, args.date)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out} ({len(text.splitlines()):,} lines)")


if __name__ == "__main__":
    main()
