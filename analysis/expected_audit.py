"""BlastRadius — Harness Failure Count vs EXPECTED.md Arithmetic Audit.

Per ROADMAP §25.3, §9.1 and AGENTS.md.
Independent cross-check comparing test harness-reported failure/error counts
against hand-labelled ground truth in tests/fixtures/logs/EXPECTED.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

FIXTURES_DIR = Path("tests/fixtures/logs")
EXPECTED_MD = FIXTURES_DIR / "EXPECTED.md"

_ANSI_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Summary line patterns
# Maven / Surefire module or aggregate summary: [ERROR/WARNING/INFO] Tests run: N, Failures: F, Errors: E
_MAVEN_AGG_RE = re.compile(
    r"\[(?:ERROR|WARNING|INFO)\]\s+Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+)",
    re.IGNORECASE,
)
# Maven Surefire per-class detail summary: Tests run: N, Failures: F, Errors: E ... -- in pkg.Class
_MAVEN_CLASS_RE = re.compile(
    r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+)(?:,\s*Skipped:\s*\d+)?(?:,\s*Time elapsed:.*?)?(?:\s+<<< FAILURE!\s*--?\s*in\s*|\s+--\s+in\s+)",
    re.IGNORECASE,
)
# Gradle test summary: N tests completed, M failed
_GRADLE_SUMMARY_RE = re.compile(
    r"(\d+)\s+tests?\s+completed,\s*(\d+)\s+failed",
    re.IGNORECASE,
)
# Pytest short test summary: === N failed, M passed ... ===
_PYTEST_SUMMARY_RE = re.compile(
    r"={3,}[^\n\r]*\b(\d+)\s+failed\b[^\n\r]*={3,}",
    re.IGNORECASE,
)


@dataclass
class AuditRow:
    index: int
    filename: str
    build_tool: str
    expected_count: int
    harness_count: int | None  # None if NO_SUMMARY
    summary_type: str
    summary_evidence: str

    @property
    def delta(self) -> int | None:
        if self.harness_count is None:
            return None
        return self.harness_count - self.expected_count


def parse_expected_counts(expected_path: Path = EXPECTED_MD) -> dict[str, dict]:
    """Parse EXPECTED.md to retrieve expected test outcome counts per fixture."""
    content = expected_path.read_text(encoding="utf-8", errors="replace")
    main_doc = content.split("## Analysis of the Four Anomalous Repositories")[0]

    pattern = re.compile(
        r"##\s+(\d+)\.\s+([^\n]+)\n(.*?)(?=\n##\s+\d+\.|\Z)",
        re.DOTALL,
    )
    fixtures: dict[str, dict] = {}
    for m in pattern.finditer(main_doc):
        num = int(m.group(1).strip())
        fname = m.group(2).strip()
        body = m.group(3)

        outcomes_m = re.search(
            r"-\s+\*\*Expected Outcomes:\*\*(.*?)(?=\n-\s+\*\*Confidence:|\Z)",
            body,
            re.DOTALL,
        )
        outcomes_text = outcomes_m.group(1).strip() if outcomes_m else ""

        tool_m = re.search(r"-\s+\*\*Build Tool:\*\*\s*([^\n]+)", body)
        build_tool = tool_m.group(1).strip() if tool_m else "Unknown"

        if "NO_TEST_OUTCOMES" in outcomes_text:
            count = 0
        else:
            canons = re.findall(
                r"Canonical `normalize_test_id\(\)`:\s*`([^`]+)`",
                outcomes_text,
            )
            count = len(set(canons))

        fixtures[fname] = {
            "index": num,
            "filename": fname,
            "build_tool": build_tool,
            "expected_count": count,
        }
    return fixtures


def extract_harness_count(body: str) -> tuple[int | None, str, str]:
    """Extract harness-reported failure/error count directly from summary lines.

    Returns (count, summary_type, evidence_line).
    """
    clean_lines = [_ANSI_RE.sub("", l).strip() for l in body.splitlines()]

    # 1. Check for Pytest summary
    for l in reversed(clean_lines):
        m = _PYTEST_SUMMARY_RE.search(l)
        if m:
            failed_count = int(m.group(1))
            return failed_count, "Pytest", l

    # 2. Check for Gradle summary
    for l in reversed(clean_lines):
        m = _GRADLE_SUMMARY_RE.search(l)
        if m:
            failed_count = int(m.group(2))
            return failed_count, "Gradle", l

    # 3. Check for Maven Aggregate summaries [ERROR/WARNING/INFO] Tests run: N, Failures: F, Errors: E
    maven_aggs = []
    for l in clean_lines:
        m = _MAVEN_AGG_RE.search(l)
        if m:
            runs, fails, errs = int(m.group(1)), int(m.group(2)), int(m.group(3))
            maven_aggs.append((fails + errs, l))

    if maven_aggs:
        # If any aggregate has failures/errors, take the max/sum of final module summaries
        non_zero_aggs = [a for a in maven_aggs if a[0] > 0]
        if non_zero_aggs:
            # Last non-zero aggregate represents the failing module summary count
            count, evidence = non_zero_aggs[-1]
            return count, "Maven (Aggregate)", evidence
        else:
            # All modules reported 0 failures/errors
            count, evidence = maven_aggs[-1]
            return count, "Maven (Clean)", evidence

    # 4. Check for Maven per-class summary lines if no aggregate summary appeared
    maven_classes = []
    for l in clean_lines:
        m = _MAVEN_CLASS_RE.search(l)
        if m:
            runs, fails, errs = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if fails + errs > 0:
                maven_classes.append((fails + errs, l))

    if maven_classes:
        total_class_fails = sum(c[0] for c in maven_classes)
        return total_class_fails, "Maven (Class Sum)", maven_classes[0][1]

    return None, "NO_SUMMARY", "No standard summary line found"


def run_audit(
    fixtures_dir: Path = FIXTURES_DIR, expected_md: Path = EXPECTED_MD
) -> list[AuditRow]:
    expected_data = parse_expected_counts(expected_md)
    rows: list[AuditRow] = []

    for fname in sorted(expected_data.keys(), key=lambda k: expected_data[k]["index"]):
        meta = expected_data[fname]
        path = fixtures_dir / fname
        if not path.exists():
            raise FileNotFoundError(f"Fixture file not found: {path}")

        body = path.read_text(encoding="utf-8", errors="replace")
        harness_cnt, sum_type, evidence = extract_harness_count(body)

        rows.append(
            AuditRow(
                index=meta["index"],
                filename=fname,
                build_tool=meta["build_tool"],
                expected_count=meta["expected_count"],
                harness_count=harness_cnt,
                summary_type=sum_type,
                summary_evidence=evidence,
            )
        )
    return rows


def print_audit(rows: list[AuditRow]) -> None:
    print("=" * 115)
    print("BLASTRADIUS EXPECTED.md ARITHMETIC AUDIT (Harness Counts vs Ground Truth)")
    print("=" * 115)
    print(
        f"{'#':<3} | {'Fixture Filename':<48} | {'Exp':<3} | {'Harness':<7} | {'Delta':<6} | {'Detector / Summary Line'}"
    )
    print("-" * 115)

    checked = 0
    exact_matches = 0
    harness_higher = 0
    expected_higher = 0
    no_summary_count = 0

    for r in rows:
        h_str = str(r.harness_count) if r.harness_count is not None else "NO_SUM"
        d_str = f"{r.delta:+d}" if r.delta is not None else "N/A"

        if r.harness_count is None:
            no_summary_count += 1
            status = "NO_SUMMARY"
        elif r.delta == 0:
            checked += 1
            exact_matches += 1
            status = "MATCH"
        elif r.delta > 0:
            checked += 1
            harness_higher += 1
            status = f"HARNESS +{r.delta}"
        else:
            checked += 1
            expected_higher += 1
            status = f"EXPECTED +{-r.delta}"

        print(
            f"{r.index:<3} | {r.filename:<48} | {r.expected_count:<3} | {h_str:<7} | {d_str:<6} | [{status}] {r.summary_type}: {r.summary_evidence[:40]}"
        )

    print("-" * 115)
    print("AUDIT SUMMARY:")
    print(f"  Total Fixtures:               {len(rows)}")
    print(f"  Checkable via Summary Lines:  {checked} / {len(rows)} ({checked / len(rows) * 100:.1f}%)")
    print(f"  Uncheckable (NO_SUMMARY):     {no_summary_count} / {len(rows)} ({no_summary_count / len(rows) * 100:.1f}%)")
    print(f"  Exact Arithmetic Matches:     {exact_matches} / {checked} ({exact_matches / checked * 100:.1f}%)")
    print(f"  Harness > EXPECTED.md:        {harness_higher} (Candidate Omissions / Over-counts in Harness)")
    print(f"  EXPECTED.md > Harness:        {expected_higher} (Candidate Ground-Truth Over-Counts)")
    print("=" * 115)


import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit EXPECTED.md arithmetic against harness summaries")
    parser.add_argument(
        "fixtures_dir",
        nargs="?",
        default=FIXTURES_DIR,
        type=Path,
        help="Path to fixture directory containing logs and EXPECTED.md (default: tests/fixtures/logs)",
    )
    args = parser.parse_args()
    fixtures_dir = args.fixtures_dir
    expected_md = fixtures_dir / "EXPECTED.md"
    rows = run_audit(fixtures_dir=fixtures_dir, expected_md=expected_md)
    print_audit(rows)


if __name__ == "__main__":
    main()

