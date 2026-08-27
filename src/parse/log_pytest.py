"""BlastRadius — Pytest Test Execution Log Parser.

Per ROADMAP §9.1 (T1.1 Test-result parser suite) and DECISIONS.md (D-09, D-25).
Extracts test failure outcomes from raw pytest execution logs into canonical
TestOutcome records.

Supported Pytest Output Forms:
- Progress Lines (Verbose Execution):
    apache_beam/yaml/integration_tests.py::FlattenTest::test_Flatten_ExternalJavaProvider_2 FAILED [ 28%]
    apache_beam/yaml/integration_tests.py::DatadogTest::test_only FAILED     [ 50%]
    tests/test_calc.py::test_add[2-3-5] FAILED [ 75%]
    tests/test_service.py::test_init ERROR [ 10%]
    tests/test_mod.py FAILED [ 100%]
- Summary Lines (Short Test Summary Info):
    FAILED apache_beam/yaml/integration_tests.py::FlattenTest::test_Flatten_ExternalJavaProvider_2 - ValueError: Error applying transform...
    FAILED tests/test_calc.py::test_add[2-3-5] - AssertionError: assert 5 == 6
    FAILED tests/test_foo.py::TestFoo::test_bar (setup) - RuntimeError: fixture failed
    ERROR tests/test_mod.py - ImportError: No module named foo

Deduplication & Enrichment Rule:
When a test appears in both progress and summary form, the summary line enriches
the existing progress record with the failure error message and elevates confidence
to CONFIDENCE_PYTEST_SUMMARY. Neither form is dropped.

Parameterised Test Identifiers:
Parameterised test IDs keep their parameter brackets '[...]' and do NOT collapse
(unlike Surefire execution indices), because pytest parameterised instances are
independently addressable test node CLI targets.

XFAIL / XPASS Status:
XFAIL and XPASS are NOT-SUPPORTED. Pytest's strict xfail mode (xfail_strict=true)
causes unexpected passes (XPASS) to fail the test suite, making XPASS handling
a real gap when strict mode is active.

Provisional Confidence Values:
- CONFIDENCE_PYTEST_SUMMARY = 0.90
- CONFIDENCE_PYTEST_PROGRESS = 0.85
- merged = max(existing.parser_confidence, CONFIDENCE_PYTEST_SUMMARY)
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

from src.parse.outcome import TestOutcome

__all__ = [
    "CONFIDENCE_PYTEST_SUMMARY",
    "CONFIDENCE_PYTEST_PROGRESS",
    "PytestParseStats",
    "parse_pytest_log_with_stats",
    "parse_pytest_log",
    "extract_pytest_failing_test_ids",
    "classify_pytest_log",
]

CONFIDENCE_PYTEST_SUMMARY: float = 0.90
CONFIDENCE_PYTEST_PROGRESS: float = 0.85

_ANSI_ESCAPE_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
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

_PYTEST_CLEAN_SUMMARY_RE = re.compile(
    r"=+\s*(?:(?:\d+\s+(?:passed|skipped|xfailed|warnings?)[,\s]*)+)\s+in\s+[\d.]+",
    re.IGNORECASE,
)
_PYTEST_FAIL_WORD_RE = re.compile(r"\b\d+\s+(?:failed|errors?)\b", re.IGNORECASE)

# Summary line: FAILED/ERROR node_id [(phase)] [- msg]
_SUMMARY_LINE_RE = re.compile(
    r"^(FAILED|ERROR|XFAIL|XPASS)\s+(\S.*?)(?:\s+\((?:setup|call|teardown)\))?(?:\s+-\s+(.*))?$"
)

# Progress line: node_id FAILED/ERROR/PASSED/SKIPPED/XFAIL/XPASS [ xx%]
_PROGRESS_LINE_RE = re.compile(
    r"^(\S.*?)\s+(FAILED|ERROR|PASSED|SKIPPED|XFAIL|XPASS)(?:\s+\[\s*\d+%\s*\])?\s*$"
)

# Pytest-timeout interrupted progress line: node_id +++ Timeout +++
_PYTEST_TIMEOUT_LINE_RE = re.compile(
    r"^(\S.*?)\s+\+{3,}\s*Timeout\s*\+{3,}\s*$",
    re.IGNORECASE,
)

# Pytest-timeout closing banner line: +++ Timeout +++
_PYTEST_TIMEOUT_CLOSING_RE = re.compile(
    r"^\+{3,}\s*Timeout\s*\+{3,}\s*$",
    re.IGNORECASE,
)

# Standalone progress status line after timeout stack dump: FAILED/ERROR [ xx%]
_STANDALONE_PROGRESS_STATUS_RE = re.compile(
    r"^(FAILED|ERROR)(?:\s+\[\s*\d+%\s*\])?\s*$"
)

# Major section separator line (e.g. === FAILURES ===, === short test summary info ===)
_PYTEST_SECTION_HEADER_RE = re.compile(r"^={3,}.*={3,}$")


@dataclass
class PytestParseStats:
    """Statistics collected during pytest log parsing."""

    total_outcomes: int = 0
    summary_fail_count: int = 0
    summary_error_count: int = 0
    progress_fail_count: int = 0
    progress_error_count: int = 0
    dedup_merged_count: int = 0


def _clean_line(line: str) -> str:
    line = _ANSI_ESCAPE_RE.sub("", line)
    line = _ISO8601_PREFIX_RE.sub("", line)
    line = _CHANNEL_PREFIX_RE.sub("", line)
    return line.strip()


def _is_valid_pytest_node_id(node_id: str) -> bool:
    """Check whether a candidate string is a plausible pytest node identifier."""
    if not node_id:
        return False
    # Reject obvious build system banners, Gradle tasks, Maven lines
    if node_id.startswith(("[", ">", "Task ", "BUILD ", "FAILURE:", "ERROR:", "INFO:")):
        return False
    # Reject Gradle-style chevron tests
    if " > " in node_id:
        return False
    # Standard pytest node IDs contain '::'
    if "::" in node_id:
        return True
    # Module-level test file targets
    if node_id.endswith((".py", ".rst", ".md")):
        return True
    # File with line number, e.g. tests/test_foo.py:42: TestFoo.test_bar
    if re.match(r"^[a-zA-Z0-9_./\\-]+\.py:\d+", node_id):
        return True
    return False


def parse_pytest_log_with_stats(
    body: str,
    run_id: int | None = None,
    job_id: int | None = None,
    repo: str | None = None,
    head_sha: str | None = None,
) -> tuple[list[TestOutcome], PytestParseStats]:
    """Parse raw pytest log text into canonical TestOutcome records with extraction statistics."""
    stats = PytestParseStats()
    outcomes_dict: dict[str, TestOutcome] = {}
    pending_timeout_node_id: str | None = None

    lines = body.splitlines()
    for raw_line in lines:
        line = _clean_line(raw_line)
        if not line:
            continue

        # 0a. Closing timeout banner line with no node ID prefix - neither arm nor disarm
        if _PYTEST_TIMEOUT_CLOSING_RE.match(line):
            continue

        # 0b. Pytest-timeout interrupted progress line: node_id +++ Timeout +++
        m_timeout = _PYTEST_TIMEOUT_LINE_RE.match(line)
        if m_timeout:
            raw_node_id = m_timeout.group(1).strip()
            if _is_valid_pytest_node_id(raw_node_id):
                pending_timeout_node_id = raw_node_id
                continue

        # 0c. Standalone status marker (e.g. FAILED [ 99%]) following a timeout stack dump
        m_stand = _STANDALONE_PROGRESS_STATUS_RE.match(line)
        if m_stand:
            if pending_timeout_node_id is not None:
                raw_node_id = pending_timeout_node_id
                pending_timeout_node_id = None
                status_tag = m_stand.group(1).upper()
                status: Literal["fail", "error"] = "fail" if status_tag == "FAILED" else "error"
                if status == "fail":
                    stats.progress_fail_count += 1
                else:
                    stats.progress_error_count += 1

                if raw_node_id in outcomes_dict:
                    existing = outcomes_dict[raw_node_id]
                    stats.dedup_merged_count += 1
                    outcomes_dict[raw_node_id] = TestOutcome(
                        test_id=existing.test_id,
                        parser_confidence=max(existing.parser_confidence, CONFIDENCE_PYTEST_PROGRESS),
                        run_id=existing.run_id or run_id,
                        job_id=existing.job_id or job_id,
                        repo=existing.repo or repo,
                        head_sha=existing.head_sha or head_sha,
                        status=existing.status,
                        duration_s=existing.duration_s,
                        failure_message=existing.failure_message,
                        label_source="log",
                    )
                else:
                    outcomes_dict[raw_node_id] = TestOutcome(
                        test_id=raw_node_id,
                        parser_confidence=CONFIDENCE_PYTEST_PROGRESS,
                        run_id=run_id,
                        job_id=job_id,
                        repo=repo,
                        head_sha=head_sha,
                        status=status,
                        duration_s=None,
                        failure_message=None,
                        label_source="log",
                    )
            continue

        # 0d. Disarm pending timeout state on major section headers (e.g. === FAILURES ===)
        if _PYTEST_SECTION_HEADER_RE.match(line):
            pending_timeout_node_id = None
            continue

        # 1. Try matching short summary lines (FAILED/ERROR node_id - msg)
        m_sum = _SUMMARY_LINE_RE.match(line)
        if m_sum:
            status_tag = m_sum.group(1).upper()
            raw_node_id = m_sum.group(2).strip()
            msg = m_sum.group(3).strip() if m_sum.group(3) else None

            # XFAIL and XPASS stay NOT-SUPPORTED. Pytest's strict xfail mode
            # (xfail_strict=true) causes unexpected passes (XPASS) to fail the test suite,
            # making XPASS handling a real gap when strict mode is active.
            if status_tag in ("XFAIL", "XPASS"):
                continue

            if _is_valid_pytest_node_id(raw_node_id):
                pending_timeout_node_id = None
                status: Literal["fail", "error"] = "fail" if status_tag == "FAILED" else "error"
                if status == "fail":
                    stats.summary_fail_count += 1
                else:
                    stats.summary_error_count += 1

                if raw_node_id in outcomes_dict:
                    existing = outcomes_dict[raw_node_id]
                    stats.dedup_merged_count += 1
                    outcomes_dict[raw_node_id] = TestOutcome(
                        test_id=existing.test_id,
                        parser_confidence=max(existing.parser_confidence, CONFIDENCE_PYTEST_SUMMARY),
                        run_id=existing.run_id or run_id,
                        job_id=existing.job_id or job_id,
                        repo=existing.repo or repo,
                        head_sha=existing.head_sha or head_sha,
                        status=existing.status,
                        duration_s=existing.duration_s,
                        failure_message=msg if msg is not None else existing.failure_message,
                        label_source="log",
                    )
                else:
                    outcomes_dict[raw_node_id] = TestOutcome(
                        test_id=raw_node_id,
                        parser_confidence=CONFIDENCE_PYTEST_SUMMARY,
                        run_id=run_id,
                        job_id=job_id,
                        repo=repo,
                        head_sha=head_sha,
                        status=status,
                        duration_s=None,
                        failure_message=msg,
                        label_source="log",
                    )
                continue

        # 2. Try matching progress lines (node_id FAILED/ERROR [ xx%])
        m_prog = _PROGRESS_LINE_RE.match(line)
        if m_prog:
            raw_node_id = m_prog.group(1).strip()
            status_tag = m_prog.group(2).upper()

            # If this is a valid pytest node ID, disarm any prior pending timeout
            if _is_valid_pytest_node_id(raw_node_id):
                pending_timeout_node_id = None

            # XFAIL and XPASS stay NOT-SUPPORTED. Pytest's strict xfail mode
            # (xfail_strict=true) causes unexpected passes (XPASS) to fail the test suite,
            # making XPASS handling a real gap when strict mode is active.
            if status_tag in ("PASSED", "SKIPPED", "XFAIL", "XPASS"):
                continue

            if _is_valid_pytest_node_id(raw_node_id):
                status: Literal["fail", "error"] = "fail" if status_tag == "FAILED" else "error"
                if status == "fail":
                    stats.progress_fail_count += 1
                else:
                    stats.progress_error_count += 1

                if raw_node_id in outcomes_dict:
                    existing = outcomes_dict[raw_node_id]
                    stats.dedup_merged_count += 1
                    outcomes_dict[raw_node_id] = TestOutcome(
                        test_id=existing.test_id,
                        parser_confidence=max(existing.parser_confidence, CONFIDENCE_PYTEST_PROGRESS),
                        run_id=existing.run_id or run_id,
                        job_id=existing.job_id or job_id,
                        repo=existing.repo or repo,
                        head_sha=existing.head_sha or head_sha,
                        status=existing.status,
                        duration_s=existing.duration_s,
                        failure_message=existing.failure_message,
                        label_source="log",
                    )
                else:
                    outcomes_dict[raw_node_id] = TestOutcome(
                        test_id=raw_node_id,
                        parser_confidence=CONFIDENCE_PYTEST_PROGRESS,
                        run_id=run_id,
                        job_id=job_id,
                        repo=repo,
                        head_sha=head_sha,
                        status=status,
                        duration_s=None,
                        failure_message=None,
                        label_source="log",
                    )
                continue

    stats.total_outcomes = len(outcomes_dict)
    return list(outcomes_dict.values()), stats


def parse_pytest_log(
    body: str,
    run_id: int | None = None,
    job_id: int | None = None,
    repo: str | None = None,
    head_sha: str | None = None,
) -> list[TestOutcome]:
    """Parse raw pytest log text into canonical TestOutcome records."""
    outcomes, _ = parse_pytest_log_with_stats(
        body=body, run_id=run_id, job_id=job_id, repo=repo, head_sha=head_sha
    )
    return outcomes


def extract_pytest_failing_test_ids(body: str) -> set[str]:
    """Extract raw/canonical failing test identifiers for fixture scoring."""
    outcomes = parse_pytest_log(body)
    return {o.test_id for o in outcomes}


def classify_pytest_log(body: str) -> tuple[str, set[str], bool]:
    """Classify a pytest log per fixture_score.py protocol."""
    is_truncated = bool(_TRUNCATION_RE.search(body))
    failing_ids = extract_pytest_failing_test_ids(body)

    if failing_ids:
        return "TEST_FAILURE", failing_ids, is_truncated

    # Check for pytest clean test execution
    # Must match pytest summary footer with passed/skipped/xfailed/warnings and no failed/error counts
    has_clean_summary = bool(_PYTEST_CLEAN_SUMMARY_RE.search(body))
    has_fail_words = bool(_PYTEST_FAIL_WORD_RE.search(body))

    if has_clean_summary and not has_fail_words:
        return "TEST_RAN_CLEAN", set(), is_truncated
    else:
        return "NO_TEST_OUTPUT", set(), is_truncated
