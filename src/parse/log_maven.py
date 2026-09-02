"""BlastRadius — Maven Test Execution Log Parser.

Per ROADMAP §9.1 (T1.1 Test-result parser suite) and DECISIONS.md (D-09, D-25, D-27).
Extracts test failure outcomes from raw Maven Surefire / Failsafe build logs into
canonical TestOutcome records.

Supported Maven Failure Shapes:
- FORM A (Self-Contained FQCN + Method): Fully qualified class name and test method
  on a single line with execution duration:
    [ERROR] org.apache.flink.test.checkpointing.SavepointITCase.testStopWithSavepointFailsOverToSavepoint -- Time elapsed: 3.335 s <<< FAILURE!
    [ERROR] io.airlift.api.maven.tests.OpenApiGenerationTest.testApiIdSupportsLookupSucceeds()[1] -- Time elapsed: 0.250 s <<< FAILURE!
- FORM B (Class-Only Summary Line): Class-level failure header indicating failure in FQCN:
    [ERROR] Tests run: 19, Failures: 1, Errors: 0, Skipped: 1, Time elapsed: 25.72 s <<< FAILURE! -- in org.apache.flink.test.checkpointing.SavepointITCase
- FORM C (Surefire 3.x / Summary Failure Line): Indented simple class name, method,
  and line number, optionally followed by failure exception / message:
    [ERROR]   SavepointITCase.testStopWithSavepointFailsOverToSavepoint:326
    [ERROR]   ScooterRentalGeofencingTest.arriveByAdjacentNoDropOffZonesDropsOutsideBothZones:398 » IllegalArgument Unexpected...
- FORM D (Bare Method Name): Single-line method failure without class prefix:
    [ERROR] testEmrServerlessSuccessWorkflowInstance  Time elapsed: 0.345 s  <<< FAILURE!

Provisional Parser Confidence Values:
- CONFIDENCE_FORM_A_FQCN = 0.90: Single-line self-contained match with full package, class,
  and method name; highest confidence.
- CONFIDENCE_FORM_C_JOINED = 0.75: FORM C simple class + method successfully reconciled with
  a unique known FQCN class from the same log.
- CONFIDENCE_FORM_C_BARE = 0.60: FORM C simple class + method where no FQCN package is
  available (e.g. Surefire 3.x with no prior FORM B header) or ambiguous match.
- CONFIDENCE_FORM_D_JOINED = 0.60: FORM D bare method name successfully reconciled with a
  single known FQCN class from the same log.
- CONFIDENCE_FORM_D_BARE = 0.40: FORM D bare method name where no FQCN package could be
  determined or multiple candidates exist.
Note: All confidence scores are PROVISIONAL and uncalibrated against empirical ground truth.

Amendment 1 (Class-Only Records):
FORM B lines report failures at the class level (e.g. '@BeforeClass' or initialization failures).
A class name is not a test case / test method identifier. Emitting class names as test outcomes
pollutes test identifier sets and causes false positives. Therefore, unattached FORM B class
headers are dropped from TestOutcome emission and counted in 'MavenParseStats.dropped_class_only_count'.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from src.parse.outcome import TestOutcome

__all__ = [
    "CONFIDENCE_FORM_A_FQCN",
    "CONFIDENCE_FORM_C_JOINED",
    "CONFIDENCE_FORM_C_BARE",
    "CONFIDENCE_FORM_D_JOINED",
    "CONFIDENCE_FORM_D_BARE",
    "MavenParseStats",
    "parse_maven_log_with_stats",
    "parse_maven_log",
    "extract_maven_failing_test_ids",
    "classify_maven_log",
]

# Provisional confidence constants
CONFIDENCE_FORM_A_FQCN: float = 0.90
CONFIDENCE_FORM_C_JOINED: float = 0.75
CONFIDENCE_FORM_C_BARE: float = 0.60
CONFIDENCE_FORM_D_JOINED: float = 0.60
CONFIDENCE_FORM_D_BARE: float = 0.40

_ANSI_ESCAPE_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
_ISO8601_PREFIX_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?[ \t]?"
)
_SYSLOG_DATE_RE = re.compile(
    r"^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?\s*"
)
_TIME_ONLY_RE = re.compile(r"^\d{2}:\d{2}:\d{2}(?:\.\d+)?\s*")
_CHANNEL_PREFIX_RE = re.compile(
    r"^\[(?:backend:build:ci|Test worker|test worker|daemon|pool-\d+-thread-\d+|main)\]\s*",
    re.IGNORECASE,
)

_TRUNCATION_RE = re.compile(
    r"##\[error\]The job running on runner .*? has exceeded the maximum execution time|"
    r"The job running on runner .*? has exceeded the maximum execution time|"
    r"(?:Log file size exceeds the limit|Truncated output|Output truncated|Truncation limit reached)",
    re.IGNORECASE,
)

_CLEAN_TEST_RE = re.compile(
    r"Tests run:\s*[1-9]\d*,\s*Failures:\s*0,\s*Errors:\s*0\b"
)

# Java method identifier regex
_JAVA_METHOD_IDENT_RE = re.compile(r"^[a-zA-Z_$][a-zA-Z0-9_$]*$")

# Surefire / Failsafe Regex Patterns:
# FORM A: [ERROR] pkg.Class.method(params)[idx] -- Time elapsed: ... <<< FAILURE!
_SUREFIRE_FORM_A = re.compile(
    r"\[ERROR\]\s+([a-zA-Z_$][a-zA-Z0-9_$]*(?:\.[a-zA-Z_$][a-zA-Z0-9_$]*)+)\.([a-zA-Z_$][a-zA-Z0-9_$]*)(?:\(.*?\))?(?:\[\d+\])?\s+(--\s+)?Time elapsed:\s*([0-9.]+\s*[mμ]?s)?.*?(?:<<< FAILURE!|<<< ERROR!)",
    re.IGNORECASE,
)

# FORM B: <<< FAILURE! - in pkg.Class
_SUREFIRE_FORM_B = re.compile(
    r"<<< (?:FAILURE|ERROR)!\s*(?:--|-)?\s*in\s+([a-zA-Z_$][a-zA-Z0-9_$]*(?:\.[a-zA-Z_$][a-zA-Z0-9_$]*)+(?:\$[a-zA-Z0-9_$]+)*)",
    re.IGNORECASE,
)

# FORM C: [ERROR]   Class.method:LINE » Exception or expected: ...
_SUREFIRE_FORM_C = re.compile(
    r"\[ERROR\]\s{2,}([a-zA-Z_$][a-zA-Z0-9_$]*(?:\$[a-zA-Z0-9_$]+)*)\.([a-zA-Z_$][a-zA-Z0-9_$]*):[0-9]+(?:->[a-zA-Z_$][a-zA-Z0-9_$]*:[0-9]+)*\s*(.*)$",
    re.IGNORECASE,
)

# FORM D: [ERROR] methodName Time elapsed: ... <<< FAILURE!
_SUREFIRE_FORM_D = re.compile(
    r"\[ERROR\]\s+([a-zA-Z_$][a-zA-Z0-9_$]*)(?:\(.*?\))?(?:\[\d+\])?\s+Time elapsed:\s*([0-9.]+\s*[mμ]?s)?\s*<<<\s+(?:FAILURE!|ERROR!)",
    re.IGNORECASE,
)

# JUnit 4 Surefire: [ERROR] method(pkg.Class) [idx] -- Time elapsed: ... <<< FAILURE!/ERROR!
_SUREFIRE_FORM_JUNIT4 = re.compile(
    r"\[ERROR\]\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\(([a-zA-Z_$][a-zA-Z0-9_$]*(?:\.[a-zA-Z_$][a-zA-Z0-9_$]*)+(?:\$[a-zA-Z0-9_$]+)*)\)(?:\[\d+\])?\s+(?:--\s+)?Time elapsed:\s*([0-9.]+\s*[mμ]?s)?.*?(?:<<<\s*(?:FAILURE!|ERROR!))",
    re.IGNORECASE,
)


def _parse_duration_s(dur_str: str | None) -> float | None:
    if not dur_str:
        return None
    s = dur_str.strip()
    if s.endswith("ms"):
        try:
            return float(s[:-2].strip()) / 1000.0
        except ValueError:
            return None
    elif s.endswith("s"):
        try:
            return float(s[:-1].strip())
        except ValueError:
            return None
    return None


@dataclass
class MavenParseStats:
    total_outcomes: int = 0
    form_a_count: int = 0
    form_b_count: int = 0
    form_c_count: int = 0
    form_d_count: int = 0
    form_junit4_count: int = 0
    dropped_class_only_count: int = 0
    ambiguous_join_count: int = 0
    class_level_events_suppressed: int = 0


def _clean_line(line: str) -> str:
    line = _ANSI_ESCAPE_RE.sub("", line)
    line = _ISO8601_PREFIX_RE.sub("", line)
    line = _SYSLOG_DATE_RE.sub("", line)
    line = _TIME_ONLY_RE.sub("", line)
    line = _CHANNEL_PREFIX_RE.sub("", line)
    return line.rstrip()


def has_stack_frame(log_text: str, class_name: str, method_name: str) -> bool:
    """Check if the log contains a stack frame matching 'at <class_name>.<method_name>('.

    Provides positive evidence that a candidate method identifier is a real method on the class.
    """
    pattern = rf"\bat\s+{re.escape(class_name)}\.{re.escape(method_name)}\s*\("
    return re.search(pattern, log_text) is not None


# Deferred extraction point: src/parse/common.py — trigger when a second parser requires the same suffix-reconciliation logic.
def _reconcile_maven_outcomes(
    raw_form_a: list[tuple[str, str, float | None]],
    form_b_classes: list[str],
    raw_form_c: list[tuple[str, str, str | None]],
    raw_form_d: list[tuple[str, float | None]],
    stats: MavenParseStats,
    run_id: int | None = None,
    job_id: int | None = None,
    repo: str | None = None,
    head_sha: str | None = None,
) -> list[TestOutcome]:
    """Reconcile extracted Maven Surefire shapes into canonical TestOutcome records."""
    outcomes_dict: dict[str, TestOutcome] = {}
    known_fqcn_classes: set[str] = set(form_b_classes)
    consumed_classes: set[str] = set()

    for cls, meth, _ in raw_form_a:
        if "." in cls:
            known_fqcn_classes.add(cls)

    # 1. Process FORM A (Self-Contained FQCN + Method)
    for cls, meth, dur_s in raw_form_a:
        test_id = f"{cls}#{meth}"
        consumed_classes.add(cls)
        if test_id not in outcomes_dict:
            outcomes_dict[test_id] = TestOutcome(
                test_id=test_id,
                parser_confidence=CONFIDENCE_FORM_A_FQCN,
                run_id=run_id,
                job_id=job_id,
                repo=repo,
                head_sha=head_sha,
                status="fail",
                duration_s=dur_s,
                label_source="log",
            )
        else:
            existing = outcomes_dict[test_id]
            dur = dur_s if dur_s is not None else existing.duration_s
            conf = max(existing.parser_confidence, CONFIDENCE_FORM_A_FQCN)
            outcomes_dict[test_id] = TestOutcome(
                test_id=test_id,
                parser_confidence=conf,
                run_id=run_id,
                job_id=job_id,
                repo=repo,
                head_sha=head_sha,
                status="fail",
                duration_s=dur,
                failure_message=existing.failure_message,
                label_source="log",
            )

    # 2. Process FORM C (Simple Class + Method)
    for cls, meth, msg in raw_form_c:
        matching_fqns = [
            fqn for fqn in known_fqcn_classes if fqn.split(".")[-1] == cls or fqn == cls
        ]
        if len(matching_fqns) == 1:
            fqn_cls = matching_fqns[0]
            test_id = f"{fqn_cls}#{meth}"
            conf = CONFIDENCE_FORM_C_JOINED
            consumed_classes.add(fqn_cls)
        else:
            if len(matching_fqns) >= 2:
                stats.ambiguous_join_count += 1
            test_id = f"{cls}#{meth}"
            conf = CONFIDENCE_FORM_C_BARE

        clean_msg = msg[:2000] if msg else None

        if test_id not in outcomes_dict:
            outcomes_dict[test_id] = TestOutcome(
                test_id=test_id,
                parser_confidence=conf,
                run_id=run_id,
                job_id=job_id,
                repo=repo,
                head_sha=head_sha,
                status="fail",
                failure_message=clean_msg,
                label_source="log",
            )
        else:
            existing = outcomes_dict[test_id]
            merged_msg = clean_msg if clean_msg else existing.failure_message
            merged_conf = max(existing.parser_confidence, conf)
            outcomes_dict[test_id] = TestOutcome(
                test_id=test_id,
                parser_confidence=merged_conf,
                run_id=run_id,
                job_id=job_id,
                repo=repo,
                head_sha=head_sha,
                status="fail",
                duration_s=existing.duration_s,
                failure_message=merged_msg,
                label_source="log",
            )

    # 3. Process FORM D (Bare Method Name)
    for meth, dur_s in raw_form_d:
        if len(known_fqcn_classes) == 1:
            fqn_cls = next(iter(known_fqcn_classes))
            test_id = f"{fqn_cls}#{meth}"
            conf = CONFIDENCE_FORM_D_JOINED
            consumed_classes.add(fqn_cls)
        else:
            if len(known_fqcn_classes) >= 2:
                stats.ambiguous_join_count += 1
            test_id = meth
            conf = CONFIDENCE_FORM_D_BARE

        if test_id not in outcomes_dict:
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
        else:
            existing = outcomes_dict[test_id]
            dur = dur_s if dur_s is not None else existing.duration_s
            merged_conf = max(existing.parser_confidence, conf)
            outcomes_dict[test_id] = TestOutcome(
                test_id=test_id,
                parser_confidence=merged_conf,
                run_id=run_id,
                job_id=job_id,
                repo=repo,
                head_sha=head_sha,
                status="fail",
                duration_s=dur,
                failure_message=existing.failure_message,
                label_source="log",
            )

    # 4. Amendment 1: Check for unattached FORM B class headers and count them as dropped
    for fqn in form_b_classes:
        if fqn not in consumed_classes and not any(
            o.test_id.startswith(f"{fqn}#") for o in outcomes_dict.values()
        ):
            stats.dropped_class_only_count += 1

    stats.total_outcomes = len(outcomes_dict)
    return list(outcomes_dict.values())


def parse_maven_log_with_stats(
    body: str,
    run_id: int | None = None,
    job_id: int | None = None,
    repo: str | None = None,
    head_sha: str | None = None,
) -> tuple[list[TestOutcome], MavenParseStats]:
    """Parse raw Maven log text into TestOutcome records and execution statistics."""
    stats = MavenParseStats()
    raw_form_a: list[tuple[str, str, float | None]] = []
    form_b_classes: list[str] = []
    raw_form_c: list[tuple[str, str, str | None]] = []
    raw_form_d: list[tuple[str, float | None]] = []

    lines = body.splitlines()

    for raw_line in lines:
        line = _clean_line(raw_line)
        if "[ERROR]" not in line and "<<<" not in line:
            continue

        # Check FORM A: [ERROR] pkg.Class.method(...) -- Time elapsed: ... <<< FAILURE!
        m_a = _SUREFIRE_FORM_A.search(line)
        if m_a:
            cls_name = m_a.group(1).strip()
            method_name = m_a.group(2).strip()
            has_separator = bool(m_a.group(3))
            dur_str = m_a.group(4)
            dur_s = _parse_duration_s(dur_str)

            if (
                _JAVA_METHOD_IDENT_RE.match(method_name)
                and method_name != "classMethod"
                and (has_separator or has_stack_frame(body, cls_name, method_name))
            ):
                raw_form_a.append((cls_name, method_name, dur_s))
                stats.form_a_count += 1
            else:
                stats.class_level_events_suppressed += 1
            continue

        # Check FORM B: <<< FAILURE! - in pkg.Class
        m_b = _SUREFIRE_FORM_B.search(line)
        if m_b:
            cls_name = m_b.group(1).strip()
            form_b_classes.append(cls_name)
            stats.form_b_count += 1

        # Check FORM C: [ERROR]   Class.method:LINE » Exception
        m_c = _SUREFIRE_FORM_C.search(line)
        if m_c:
            cls_name = m_c.group(1).strip()
            method_name = m_c.group(2).strip()
            msg = m_c.group(3).strip() if m_c.group(3) else None
            raw_form_c.append((cls_name, method_name, msg))
            stats.form_c_count += 1
            continue

        # Check JUnit 4 Surefire: [ERROR] method(pkg.Class) Time elapsed: ... <<< FAILURE!/ERROR!
        m_j4 = _SUREFIRE_FORM_JUNIT4.search(line)
        if m_j4:
            method_name = m_j4.group(1).strip()
            cls_name = m_j4.group(2).strip()
            if method_name == "classMethod":
                stats.class_level_events_suppressed += 1
                continue
            dur_str = m_j4.group(3)
            dur_s = _parse_duration_s(dur_str)
            raw_form_a.append((cls_name, method_name, dur_s))
            stats.form_junit4_count += 1
            continue

        # Check FORM D: [ERROR] methodName Time elapsed: ... <<< FAILURE!
        m_d = _SUREFIRE_FORM_D.search(line)
        if m_d:
            method_name = m_d.group(1).strip()
            dur_str = m_d.group(2)
            dur_s = _parse_duration_s(dur_str)
            raw_form_d.append((method_name, dur_s))
            stats.form_d_count += 1
            continue

    outcomes = _reconcile_maven_outcomes(
        raw_form_a=raw_form_a,
        form_b_classes=form_b_classes,
        raw_form_c=raw_form_c,
        raw_form_d=raw_form_d,
        stats=stats,
        run_id=run_id,
        job_id=job_id,
        repo=repo,
        head_sha=head_sha,
    )

    return outcomes, stats


def parse_maven_log(
    body: str,
    run_id: int | None = None,
    job_id: int | None = None,
    repo: str | None = None,
    head_sha: str | None = None,
) -> list[TestOutcome]:
    """Parse raw Maven log text into canonical TestOutcome records."""
    outcomes, _ = parse_maven_log_with_stats(
        body=body, run_id=run_id, job_id=job_id, repo=repo, head_sha=head_sha
    )
    return outcomes


def extract_maven_failing_test_ids(body: str) -> set[str]:
    """Extract raw/canonical failing test identifiers for fixture scoring."""
    outcomes = parse_maven_log(body)
    return {o.test_id for o in outcomes}


def classify_maven_log(body: str) -> tuple[str, set[str], bool]:
    """Classify a Maven log per fixture_score.py protocol."""
    is_truncated = bool(_TRUNCATION_RE.search(body))
    failing_ids = extract_maven_failing_test_ids(body)

    if failing_ids:
        return "TEST_FAILURE", failing_ids, is_truncated
    elif _CLEAN_TEST_RE.search(body):
        return "TEST_RAN_CLEAN", set(), is_truncated
    else:
        return "NO_TEST_OUTPUT", set(), is_truncated
