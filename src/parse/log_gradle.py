"""BlastRadius — Gradle Test Execution Log Parser.

Per ROADMAP §9.1 (T1.1 Test-result parser suite) and DECISIONS.md (D-09, D-25, D-27).
Extracts test failure outcomes from raw Gradle build logs into canonical TestOutcome
records.

Supported Gradle Failure Shapes:
- S1 (Multi-line State-Machine Attachment): Class header printed on its own line,
  followed on subsequent lines by indented test outcome:
    org.apache.fineract.integrationtests.cob.CobPartitioningTest
      Test testLoanCOBPartitioningQuery() FAILED (3.1s)
- S2 (Single-line Space-Separated): FQCN and method name on a single line:
    com.diffplug.spotless.rdf.RdfFormatterTest testCoolRdfFormatter_2_0_0_DefaultStyle() FAILED (7.1s)
- S3 (Single-line Chevron 2-Segment): Class and method/narrative separated by ' > ':
    io.sirix.cli.NativeImageSmokeTest > FLWOR expression FAILED
    MemoryMonitorTest > detectGCThrashing FAILED
- S4 (Single-line Chevron 3+ Segments): Hierarchical display names separated by ' > ';
  intermediate context segments are dropped per EXPECTED.md §39:
    WebMvcConfig > addResourceHandlers > registers all five resource handler groups FAILED
    -> test_id: 'WebMvcConfig#registers all five resource handler groups'

Provisional Parser Confidence Values (per Amendment 1):
- CONFIDENCE_S1_MULTILINE = 0.70: Multi-line state-machine attachment across lines
  carries lower confidence because parallel worker execution or unexpected log noise
  can theoretically interleave.
- CONFIDENCE_S2_SINGLE_LINE = 0.85: Single-line match with class and method on the
  same line; self-contained, no multiline state required.
- CONFIDENCE_S3_CHEVRON_2SEG = 0.85: Standard Gradle single-line chevron format;
  self-contained, no multiline state required.
- CONFIDENCE_S4_CHEVRON_3SEG = 0.80: Hierarchical Gradle/JUnit 5 display names with
  intermediate context dropped; self-contained single line.
Note: All confidence scores are PROVISIONAL and uncalibrated against empirical ground truth.

Known Limitations:
1. Display Names vs Class Names (Fixture 39): In hierarchical / narrative Gradle logs,
   the class segment may reflect a display name (e.g. 'WebMvcConfig') rather than the
   underlying Java test class ('WebMvcConfigTest' seen in stack traces). Per D-09 zero-slack
   contract, this parser records raw identifiers without fabricating suffixes. Downstream
   resolve_test_file() must handle display-name to source-file mapping.
2. Scope: Failures only. PASSED and SKIPPED outcomes are deliberately omitted this round
   per scope constraints.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from src.parse.outcome import TestOutcome

__all__ = [
    "MAX_CLASS_HEADER_DISTANCE_LINES",
    "CONFIDENCE_S1_MULTILINE",
    "CONFIDENCE_S2_SINGLE_LINE",
    "CONFIDENCE_S3_CHEVRON_2SEG",
    "CONFIDENCE_S4_CHEVRON_3SEG",
    "GradleParseStats",
    "parse_gradle_log",
    "parse_gradle_log_with_stats",
    "extract_gradle_failing_test_ids",
    "classify_gradle_log",
]

# Named constant per Amendment 2:
# In standard Gradle execution logs, test method lines appear within 1-10 lines of the
# enclosing class header. A 50-line window safely accommodates multiline class annotations
# or setup logs while bounding state lifetime to prevent stale class leakage across
# unrelated tasks or subsequent test suites.
MAX_CLASS_HEADER_DISTANCE_LINES: int = 50

# Provisional confidence constants per Amendment 1:
CONFIDENCE_S1_MULTILINE: float = 0.70
CONFIDENCE_S2_SINGLE_LINE: float = 0.85
CONFIDENCE_S3_CHEVRON_2SEG: float = 0.85
CONFIDENCE_S4_CHEVRON_3SEG: float = 0.80

_ANSI_ESCAPE_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
# Match ISO8601 timestamp prefix and only ONE optional trailing space/tab
_ISO8601_PREFIX_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?[ \t]?"
)
_CHANNEL_PREFIX_RE = re.compile(
    r"^\[(?:backend:build:ci|Test worker|test worker|daemon|pool-\d+-thread-\d+|main)\]\s*",
    re.IGNORECASE,
)

_TRUNCATION_RE = re.compile(
    r"##\[error\]The job running on runner .*? has exceeded the maximum execution time|"
    r"The job running on runner .*? has exceeded the maximum execution time",
    re.IGNORECASE,
)

# Java FQCN / class identifier regex allowing nested class notation ($)
_JAVA_CLASS_RE = re.compile(
    r"^[a-zA-Z_$][a-zA-Z0-9_$]*(?:\.[a-zA-Z_$][a-zA-Z0-9_$]*)+(?:\$[a-zA-Z_$][a-zA-Z0-9_$]*)*$"
)

# Standalone class name (bare class without package, ending with standard test suffix)
_BARE_TEST_CLASS_RE = re.compile(
    r"^[a-zA-Z_$][a-zA-Z0-9_$]*(?:Test|Tests|TestCase|IT|ITCase|Spec|Specification)(?:\$[a-zA-Z_$][a-zA-Z0-9_$]*)*$"
)

# Gradle 'took:' line: org.pkg.Class > method took: 1234ms
_TOOK_LINE_RE = re.compile(
    r"^(?:Test\s+)?([a-zA-Z_$][a-zA-Z0-9_$.$]+)\s+>\s+.*?\s+took:\s+\d+(?:\.\d+)?(?:ms|s)$"
)

# S1: Indented test failure line: "  Test methodName() FAILED (3.1s)" or "  Test narrative FAILED"
_S1_FAIL_RE = re.compile(r"^\s*Test\s+(.+?)\s+FAILED(?:\s+\(([\d.]+[mμ]?s)\))?$")

# S1 passed/skipped line: "  Test methodName() PASSED (3.1s)"
_S1_NON_FAIL_RE = re.compile(r"^\s*Test\s+(.+?)\s+(?:PASSED|SKIPPED|SUCCESSFUL)(?:\s+\(.*?\))?$")

# S2: Single-line FQCN + method: "com.pkg.ClassTest testMethod() FAILED (7.1s)"
_S2_FAIL_RE = re.compile(
    r"^([a-zA-Z_$][a-zA-Z0-9_$.$]+)\s+([a-zA-Z_$][a-zA-Z0-9_$]*\(\))\s+FAILED(?:\s+\(([\d.]+[mμ]?s)\))?$"
)

# S3 / S4: Single-line Chevron failure line: "Class > Method FAILED" or "Class > Ctx > Method FAILED"
_CHEVRON_FAIL_RE = re.compile(r"^(.*?)\s+FAILED(?:\s+\(([\d.]+[mμ]?s)\))?$")


def _parse_duration_s(dur_str: str | None) -> float | None:
    if not dur_str:
        return None
    s = dur_str.strip()
    if s.endswith("ms"):
        try:
            return float(s[:-2]) / 1000.0
        except ValueError:
            return None
    elif s.endswith("s"):
        try:
            return float(s[:-1])
        except ValueError:
            return None
    return None


@dataclass
class GradleParseStats:
    total_outcomes: int = 0
    s1_count: int = 0
    s2_count: int = 0
    s3_count: int = 0
    s4_count: int = 0
    stale_guard_fired_count: int = 0


def _clean_line(line: str) -> str:
    line = _ANSI_ESCAPE_RE.sub("", line)
    line = _ISO8601_PREFIX_RE.sub("", line)
    line = _CHANNEL_PREFIX_RE.sub("", line)
    return line.rstrip()


def parse_gradle_log_with_stats(
    body: str,
    run_id: int | None = None,
    job_id: int | None = None,
    repo: str | None = None,
    head_sha: str | None = None,
) -> tuple[list[TestOutcome], GradleParseStats]:
    """Parse raw Gradle log text into TestOutcome records and execution statistics."""
    stats = GradleParseStats()
    outcomes_dict: dict[str, TestOutcome] = {}

    current_class: str | None = None
    lines_since_class_header: int = 0

    lines = body.splitlines()

    for line_idx, raw_line in enumerate(lines, start=1):
        line = _clean_line(raw_line)

        # 1. State machine distance increment & guard check (Amendment 2)
        if current_class is not None:
            lines_since_class_header += 1
            if lines_since_class_header > MAX_CLASS_HEADER_DISTANCE_LINES:
                current_class = None
                lines_since_class_header = 0
                stats.stale_guard_fired_count += 1

        stripped = line.strip()
        if not stripped:
            continue

        # 2. Check for task boundaries, build status, and lifecycle lines that reset state
        if (
            line.startswith("> Task :")
            or line.startswith("Task :")
            or line.startswith("BUILD ")
            or line.startswith("FAILURE:")
            or line.startswith("##[group]")
            or line.startswith("##[endgroup]")
            or line.startswith("##[error]")
            or line.startswith("Starting process 'command")
            or re.search(r"^\d+\s+tests completed", stripped)
            or re.search(r"^Executed \d+ tests", stripped)
        ):
            current_class = None
            lines_since_class_header = 0
            continue

        # 3. Check for S1: Indented method failure: "  Test methodName() FAILED (3.1s)"
        # Note: Must be evaluated before S2 so that keyword "Test" is not treated as a class name.
        m_s1 = _S1_FAIL_RE.match(stripped)
        if m_s1:
            method_raw = m_s1.group(1).strip()
            dur_str = m_s1.group(2)
            dur_s = _parse_duration_s(dur_str)

            if current_class:
                test_id = f"{current_class}#{method_raw}"
                conf = CONFIDENCE_S1_MULTILINE
            else:
                test_id = method_raw
                conf = CONFIDENCE_S1_MULTILINE * 0.5

            outcomes_dict[test_id] = TestOutcome(
                test_id=test_id,
                parser_confidence=conf,
                run_id=run_id,
                job_id=job_id,
                repo=repo,
                head_sha=head_sha,
                status="fail",
                duration_s=dur_s,
                label_source="log",
            )
            stats.s1_count += 1
            lines_since_class_header = 0
            continue

        # Check for S1 non-failing line (PASSED / SKIPPED): resets distance counter
        m_s1_non_fail = _S1_NON_FAIL_RE.match(stripped)
        if m_s1_non_fail:
            lines_since_class_header = 0
            continue

        # 4. Check for S2: Single-line FQCN + method: ClassName methodName() FAILED (duration)
        m_s2 = _S2_FAIL_RE.match(stripped)
        if m_s2:
            cls_name = m_s2.group(1).strip()
            method_raw = m_s2.group(2).strip()
            dur_str = m_s2.group(3)

            if cls_name not in ("Test", "Tests", "TestCase"):
                test_id = f"{cls_name}#{method_raw}"
                dur_s = _parse_duration_s(dur_str)

                outcomes_dict[test_id] = TestOutcome(
                    test_id=test_id,
                    parser_confidence=CONFIDENCE_S2_SINGLE_LINE,
                    run_id=run_id,
                    job_id=job_id,
                    repo=repo,
                    head_sha=head_sha,
                    status="fail",
                    duration_s=dur_s,
                    label_source="log",
                )
                stats.s2_count += 1
                continue

        # 5. Check for S3 / S4: Single-line Chevron lines: Class > Method FAILED
        if " > " in stripped and (stripped.endswith("FAILED") or re.search(r"\s+FAILED(?:\s+\(.*?\))?$", stripped)):
            m_chev = _CHEVRON_FAIL_RE.match(stripped)
            if m_chev:
                prefix = m_chev.group(1).strip()
                dur_str = m_chev.group(2)
                # Ensure this is not a Gradle task or build failure line
                if (
                    not prefix.startswith("> Task")
                    and not prefix.startswith("Task ")
                    and not prefix.startswith("BUILD")
                    and not prefix.startswith("FAILURE")
                    and " > " in prefix
                ):
                    segments = [s.strip() for s in prefix.split(" > ") if s.strip()]
                    if len(segments) >= 2:
                        cls_name = segments[0]
                        method_raw = segments[-1]
                        test_id = f"{cls_name}#{method_raw}"
                        dur_s = _parse_duration_s(dur_str)

                        if len(segments) == 2:
                            conf = CONFIDENCE_S3_CHEVRON_2SEG
                            stats.s3_count += 1
                        else:
                            conf = CONFIDENCE_S4_CHEVRON_3SEG
                            stats.s4_count += 1

                        outcomes_dict[test_id] = TestOutcome(
                            test_id=test_id,
                            parser_confidence=conf,
                            run_id=run_id,
                            job_id=job_id,
                            repo=repo,
                            head_sha=head_sha,
                            status="fail",
                            duration_s=dur_s,
                            label_source="log",
                        )
                        continue

        # 6. Check if line is a Gradle took line: Class > method took: 1234ms
        m_took = _TOOK_LINE_RE.match(stripped)
        if m_took:
            current_class = m_took.group(1).strip()
            lines_since_class_header = 0
            continue

        # 7. Check if line is a standalone class header line (unindented)
        if not line.startswith(" ") and not line.startswith("\t"):
            if stripped not in ("Test", "Tests", "TestCase") and (
                _JAVA_CLASS_RE.match(stripped) or _BARE_TEST_CLASS_RE.match(stripped)
            ):
                current_class = stripped
                lines_since_class_header = 0
                continue
            elif not stripped.startswith("at ") and not stripped.startswith("Caused by:"):
                # Non-stacktrace unindented line resets current_class
                current_class = None
                lines_since_class_header = 0

    stats.total_outcomes = len(outcomes_dict)
    return list(outcomes_dict.values()), stats


def parse_gradle_log(
    body: str,
    run_id: int | None = None,
    job_id: int | None = None,
    repo: str | None = None,
    head_sha: str | None = None,
) -> list[TestOutcome]:
    """Parse raw Gradle log text into canonical TestOutcome records."""
    outcomes, _ = parse_gradle_log_with_stats(
        body=body, run_id=run_id, job_id=job_id, repo=repo, head_sha=head_sha
    )
    return outcomes


def extract_gradle_failing_test_ids(body: str) -> set[str]:
    """Extract raw/canonical failing test identifiers for fixture scoring."""
    outcomes = parse_gradle_log(body)
    return {o.test_id for o in outcomes}


def classify_gradle_log(body: str) -> tuple[str, set[str], bool]:
    """Classify a Gradle log per fixture_score.py protocol."""
    is_truncated = bool(_TRUNCATION_RE.search(body))
    failing_ids = extract_gradle_failing_test_ids(body)

    if failing_ids:
        return "TEST_FAILURE", failing_ids, is_truncated

    # Check for Gradle clean test execution
    # Must have completed tests with 0 failures and no failed test task
    has_test_completed_zero_fail = bool(
        re.search(r"\b\d+\s+tests completed,\s+0\s+failed\b", body)
    )
    has_failed_test_task = bool(
        re.search(r">\s*Task\s+:[^\n]*:test\s+FAILED", body)
    )

    if has_test_completed_zero_fail and not has_failed_test_task:
        return "TEST_RAN_CLEAN", set(), is_truncated
    else:
        return "NO_TEST_OUTPUT", set(), is_truncated
