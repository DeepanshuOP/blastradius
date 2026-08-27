"""BlastRadius — Content-Signature Parser Dispatcher & Cascade.

Per ROADMAP §9.1 (T1.1 Test-result parser suite) and DECISIONS.md (D-09, D-25, D-27).
Inspects build log lifecycle markers to route execution logs directly to their
primary framework parser (Maven, Gradle, or Pytest), falling back to union
only when format signatures are ambiguous.

Lifecyle Signatures:
- Maven: '[INFO] Scanning for projects...' or '[ERROR] --- maven-'
- Gradle: '> Task :'
- Pytest: 'rootdir:' or bare 'path/to/test.py::test_name' node IDs without surrounding build framework markers.

Ambiguous & Unknown Resolution:
- 'ambiguous': Runs all matching framework parsers and merges extracted TestOutcome
  records. Cross-framework duplicates are normalized before comparison. If both
  parsers extract the same test entity, the duplicate collision is tracked and the
  higher-confidence outcome is preserved. If a matched framework yields zero outcomes
  (e.g. Gradle executing a pytest task in fixture 4), this is treated as a clean
  success and NOT a collision.
- 'unknown': Indicates an unrecognized log format or parser capability gap. It returns
  an empty outcome list and increments the unknown counter. This is explicitly distinct
  from 'NO_TEST_OUTPUT' (which confirms a known build ran zero tests).
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

from src.parse.outcome import TestOutcome
from src.parse.log_gradle import (
    classify_gradle_log,
    extract_gradle_failing_test_ids,
    parse_gradle_log_with_stats,
)
from src.parse.log_maven import (
    classify_maven_log,
    extract_maven_failing_test_ids,
    parse_maven_log_with_stats,
)
from src.parse.log_pytest import (
    classify_pytest_log,
    extract_pytest_failing_test_ids,
    parse_pytest_log_with_stats,
)

__all__ = [
    "classify_log_format",
    "DispatchStats",
    "dispatch_parse_log_with_stats",
    "dispatch_parse_log",
    "extract_dispatch_failing_test_ids",
    "classify_dispatch_log",
]

_ANSI_ESCAPE_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
_MAVEN_SCANNING_RE = re.compile(r"\[INFO\]\s+Scanning for projects\.\.\.")
_MAVEN_PLUGIN_ERR_RE = re.compile(r"\[ERROR\]\s+--- maven-")
_GRADLE_TASK_RE = re.compile(r">\s*Task\s+:")
_PYTEST_ROOTDIR_RE = re.compile(r"\brootdir:\s+")
_PYTEST_NODE_RE = re.compile(r"(?:^|\s)[\w./-]+\.py::[\w_]+", re.MULTILINE)
_TRUNCATION_RE = re.compile(
    r"\b(?:Log truncated|Output truncated|Tail of log|The job running on runner .* has exceeded the maximum execution time)\b",
    re.IGNORECASE,
)


def _normalize_comparison_key(raw_id: str) -> str:
    """Normalize a test identifier to a canonical comparison key for duplicate detection.

    Origin & Design Rationale (Amendment 1):
    Derived from the normalization logic in analysis/fixture_score.py:normalize_comparison_id.
    Kept locally in src/parse/dispatch.py to preserve strict unidirectional dependencies
    (analysis/ depends on src/parse/, never the inverse).
    Rules applied:
    1. Strip leading and trailing whitespace.
    2. Strip empty call parentheses '()' at the end of method identifiers (e.g. 'testFoo()' -> 'testFoo').
    3. Convert '#' method separators (used in Java canonicals) to '::'.
    4. Convert ' > ' Gradle hierarchical separators to '::'.
    """
    s = raw_id.strip()
    s = re.sub(r"\(\)$", "", s)
    s = s.replace("#", "::")
    s = re.sub(r"\s*>\s*", "::", s)
    return s


def classify_log_format(
    body: str,
) -> Literal["maven", "gradle", "pytest", "ambiguous", "unknown"]:
    """Classify log format based on framework lifecycle signatures.

    Returns:
        - 'maven': Exclusively matches Maven lifecycle markers.
        - 'gradle': Exclusively matches Gradle lifecycle markers.
        - 'pytest': Exclusively matches pytest lifecycle markers.
        - 'ambiguous': Matches multiple framework lifecycle markers.
        - 'unknown': Contains no recognized lifecycle signatures.
    """
    clean = _ANSI_ESCAPE_RE.sub("", body)
    has_maven = bool(_MAVEN_SCANNING_RE.search(clean) or _MAVEN_PLUGIN_ERR_RE.search(clean))
    has_gradle = bool(_GRADLE_TASK_RE.search(clean))
    has_pytest_root = bool(_PYTEST_ROOTDIR_RE.search(clean))
    has_pytest_node = bool(_PYTEST_NODE_RE.search(clean))

    matched: list[str] = []
    if has_maven:
        matched.append("maven")
    if has_gradle:
        matched.append("gradle")
    if has_pytest_root or (has_pytest_node and not matched):
        matched.append("pytest")

    if len(matched) == 1:
        return matched[0]  # type: ignore[return-value]
    elif len(matched) > 1:
        return "ambiguous"
    return "unknown"


@dataclass
class DispatchStats:
    """Statistics captured during parser dispatch."""

    format_detected: str = ""
    routed_single: int = 0
    routed_ambiguous: int = 0
    unknown: int = 0
    duplicate_collisions: int = 0
    total_outcomes: int = 0


def dispatch_parse_log_with_stats(
    body: str,
    run_id: int | None = None,
    job_id: int | None = None,
    repo: str | None = None,
    head_sha: str | None = None,
) -> tuple[list[TestOutcome], DispatchStats]:
    """Parse raw log text via content-signature cascade with detailed dispatch statistics."""
    stats = DispatchStats()
    fmt = classify_log_format(body)
    stats.format_detected = fmt

    if fmt == "unknown":
        stats.unknown += 1
        return [], stats

    if fmt == "maven":
        stats.routed_single += 1
        outcomes, _ = parse_maven_log_with_stats(
            body, run_id=run_id, job_id=job_id, repo=repo, head_sha=head_sha
        )
        stats.total_outcomes = len(outcomes)
        return outcomes, stats

    if fmt == "gradle":
        stats.routed_single += 1
        outcomes, _ = parse_gradle_log_with_stats(
            body, run_id=run_id, job_id=job_id, repo=repo, head_sha=head_sha
        )
        stats.total_outcomes = len(outcomes)
        return outcomes, stats

    if fmt == "pytest":
        stats.routed_single += 1
        outcomes, _ = parse_pytest_log_with_stats(
            body, run_id=run_id, job_id=job_id, repo=repo, head_sha=head_sha
        )
        stats.total_outcomes = len(outcomes)
        return outcomes, stats

    # 'ambiguous': run all matching parsers and union with duplicate detection
    stats.routed_ambiguous += 1
    clean = _ANSI_ESCAPE_RE.sub("", body)
    has_maven = bool(_MAVEN_SCANNING_RE.search(clean) or _MAVEN_PLUGIN_ERR_RE.search(clean))
    has_gradle = bool(_GRADLE_TASK_RE.search(clean))
    has_pytest_root = bool(_PYTEST_ROOTDIR_RE.search(clean))
    has_pytest_node = bool(_PYTEST_NODE_RE.search(clean))

    collected: list[TestOutcome] = []
    if has_maven:
        m_out, _ = parse_maven_log_with_stats(
            body, run_id=run_id, job_id=job_id, repo=repo, head_sha=head_sha
        )
        collected.extend(m_out)
    if has_gradle:
        g_out, _ = parse_gradle_log_with_stats(
            body, run_id=run_id, job_id=job_id, repo=repo, head_sha=head_sha
        )
        collected.extend(g_out)
    if has_pytest_root or has_pytest_node:
        p_out, _ = parse_pytest_log_with_stats(
            body, run_id=run_id, job_id=job_id, repo=repo, head_sha=head_sha
        )
        collected.extend(p_out)

    # Union with duplicate-collision detection on normalized comparison keys (Amendment 1 & 2)
    merged_map: dict[str, TestOutcome] = {}
    for o in collected:
        comp_key = _normalize_comparison_key(o.test_id)
        if comp_key in merged_map:
            stats.duplicate_collisions += 1
            existing = merged_map[comp_key]
            # Preserve higher confidence record, enriching error message if absent
            if o.parser_confidence > existing.parser_confidence:
                merged_map[comp_key] = o
            elif not existing.failure_message and o.failure_message:
                merged_map[comp_key] = TestOutcome(
                    test_id=existing.test_id,
                    parser_confidence=existing.parser_confidence,
                    run_id=existing.run_id,
                    job_id=existing.job_id,
                    repo=existing.repo,
                    head_sha=existing.head_sha,
                    test_file=existing.test_file or o.test_file,
                    status=existing.status,
                    duration_s=existing.duration_s or o.duration_s,
                    failure_message=o.failure_message,
                    label_source=existing.label_source,
                )
        else:
            merged_map[comp_key] = o

    outcomes = list(merged_map.values())
    stats.total_outcomes = len(outcomes)
    return outcomes, stats


def dispatch_parse_log(
    body: str,
    run_id: int | None = None,
    job_id: int | None = None,
    repo: str | None = None,
    head_sha: str | None = None,
) -> list[TestOutcome]:
    """Parse raw log text into canonical TestOutcome records via parser dispatcher."""
    outcomes, _ = dispatch_parse_log_with_stats(
        body=body, run_id=run_id, job_id=job_id, repo=repo, head_sha=head_sha
    )
    return outcomes


def extract_dispatch_failing_test_ids(body: str) -> set[str]:
    """Extract raw/canonical failing test identifiers via parser dispatcher."""
    outcomes = dispatch_parse_log(body)
    return {o.test_id for o in outcomes}


def classify_dispatch_log(body: str) -> tuple[str, set[str], bool]:
    """Classify a build log per fixture_score.py protocol via parser dispatcher."""
    is_truncated = bool(_TRUNCATION_RE.search(body))
    failing_ids = extract_dispatch_failing_test_ids(body)
    if failing_ids:
        return "TEST_FAILURE", failing_ids, is_truncated

    fmt = classify_log_format(body)
    if fmt == "maven":
        return classify_maven_log(body)
    elif fmt == "gradle":
        return classify_gradle_log(body)
    elif fmt == "pytest":
        return classify_pytest_log(body)

    return "NO_TEST_OUTPUT", set(), is_truncated
