"""BlastRadius — Log Yield & Test Failure Classification Analysis.

Measures how many captured GitHub Actions job logs contain actual test failures
versus clean test runs, compile errors, timeouts, or empty outputs.

Per ROADMAP §21.2, §37.1 (Gate 1 feasibility), and AGENTS.md.
Scans data/raw/ filesystem artefacts for job logs.
"""

from __future__ import annotations

import argparse
import datetime
import gzip
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_RAW_ROOT = Path("data/raw")

FAIL_KEYWORDS = (
    "Tests run:",
    "<<< FAILURE!",
    "<<< ERROR!",
    "tests completed",
    "test completed",
    "> Task :",
    "FAILED",
    "FAIL:",
    "test result: FAILED",
    "Tests:",
    "FAIL ",
    "[ERROR]  ",
)

CLEAN_KEYWORDS = (
    "Tests run:",
    "tests completed",
    "test completed",
    "passed",
    "PASS:",
    "test result: ok",
    "Tests:",
)

# Module-level compiled patterns for log classification.
# "The bare uppercase word FAILED must NOT alone classify a log as TEST_FAILURE. Anchor on line structure."
PATTERNS: dict[str, re.Pattern[str]] = {
    "TEST_FAILURE": re.compile(
        r"Tests run:\s*[0-9]+,\s*Failures:\s*[1-9]"
        r"|Tests run:\s*[0-9]+,\s*Failures:\s*[0-9]+,\s*Errors:\s*[1-9]"
        r"|<<< FAILURE!"
        r"|<<< ERROR!"
        r"|\b[0-9]+\s+tests?\s+completed,\s*[1-9]"
        r"|>\s*Task\s+:[^\n\r]*test[^\n\r]*\s+FAILED"
        r"|FAILED\s+[^\s\n\r:]+\.py::"
        r"|\.py::[^\s\n\r]+\s+FAILED"
        r"|={3,}[^\n\r]*\b[0-9]+\s+failed\b"
        r"|FAILED\s+\((?:failures|errors)="
        r"|---\s*FAIL:"
        r"|test result:\s*FAILED\."
        r"|Tests:[^\n\r]*\b[1-9][0-9]*\s+failed"
        r"|FAIL\s+[^\s\n\r]+\.(?:test|spec)\."
    ),
    "TEST_RAN_CLEAN": re.compile(
        r"Tests run:\s*[1-9][0-9]*,\s*Failures:\s*0,\s*Errors:\s*0"
        r"|\b[1-9][0-9]*\s+tests?\s+completed,\s*0\s+failed"
        r"|={3,}[^\n\r]*\b[1-9][0-9]*\s+passed\b"
        r"|---\s*PASS:"
        r"|test result:\s*ok\."
        r"|Tests:[^\n\r]*\b[1-9][0-9]*\s+passed,\s*0\s+failed"
    ),
}

_ANSI_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Surefire / Maven detail & summary patterns
_SUREFIRE_FORM_A = re.compile(
    r"\[ERROR\]\s+([a-zA-Z_$][a-zA-Z0-9_$]*(?:\.[a-zA-Z_$][a-zA-Z0-9_$]*)+)\.([a-zA-Z_$][a-zA-Z0-9_$]*)(?:\(.*?\))?(?:\[\d+\])?\s+--\s+Time elapsed:.*?(?:<<< FAILURE!|<<< ERROR!)",
    re.IGNORECASE,
)
_SUREFIRE_FORM_B = re.compile(
    r"<<< (?:FAILURE|ERROR)!\s*(?:--|-)?\s*in\s*([a-zA-Z_$][a-zA-Z0-9_$]*(?:\.[a-zA-Z_$][a-zA-Z0-9_$]*)+)",
    re.IGNORECASE,
)
_SUREFIRE_FORM_C = re.compile(
    r"\[ERROR\]\s{2,}([a-zA-Z_$][a-zA-Z0-9_$]*)\.([a-zA-Z_$][a-zA-Z0-9_$]*):[0-9]+",
    re.IGNORECASE,
)
_SUREFIRE_FORM_D = re.compile(
    r"\[ERROR\]\s+([a-zA-Z_$][a-zA-Z0-9_$]*)(?:\(.*?\))?(?:\[\d+\])?\s+Time elapsed:.*?(?:<<< FAILURE!|<<< ERROR!)",
    re.IGNORECASE,
)

# Standard non-Maven patterns (pytest, gradle test logger, go, rust)
_OTHER_TEST_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"FAILED\s+([^\s\n\r:]+\.py::[^\s\n\r]+)", re.IGNORECASE),
    re.compile(r"([^\s\n\r:]+\.py::[^\s\n\r]+)\s+FAILED", re.IGNORECASE),
    re.compile(r"([a-zA-Z0-9_$.]+\s*>\s*[a-zA-Z0-9_$().]+)\s+FAILED", re.IGNORECASE),
    re.compile(r"---\s*FAIL:\s*([^\s\n\r]+)", re.IGNORECASE),
    re.compile(r"test\s+([^\s\n\r]+)\s+\.\.\.\s+FAILED", re.IGNORECASE),
]

TRUNCATION_PATTERN = re.compile(
    r"(?:Log file size exceeds the limit|Truncated output|Output truncated|Truncation limit reached)",
    re.IGNORECASE,
)


def extract_failing_test_ids(body: str) -> set[str]:
    """Extract distinct failing test identifiers from a log body.

    Applies ANSI escape stripping, extracts Maven Surefire Forms A/B/C/D and
    multilingual test failure patterns, then applies suffix-collapse join rules
    to reconcile short class/method summaries with package FQNs.
    """
    raw_fqn_methods: set[str] = set()
    raw_simple_methods: set[tuple[str, str]] = set()
    raw_fqn_classes: set[str] = set()
    raw_bare_methods: set[str] = set()
    other_ids: set[str] = set()

    for raw_l in body.splitlines():
        # (a) ANSI stripping applied before line filtering and regex matching
        clean_l = _ANSI_RE.sub("", raw_l)
        if not any(k in clean_l for k in FAIL_KEYWORDS):
            continue

        # FORM A: [ERROR] pkg.Class.method(...) -- Time elapsed: ... <<< FAILURE!
        for m in _SUREFIRE_FORM_A.finditer(clean_l):
            cls, meth = m.group(1), m.group(2)
            raw_fqn_methods.add(f"{cls}::{meth}")

        # FORM B: <<< FAILURE! ... in pkg.Class
        for m in _SUREFIRE_FORM_B.finditer(clean_l):
            cls = m.group(1)
            raw_fqn_classes.add(cls)

        # FORM C: [ERROR]   Class.method:LINE » Exception
        for m in _SUREFIRE_FORM_C.finditer(clean_l):
            cls, meth = m.group(1), m.group(2)
            raw_simple_methods.add((cls, meth))

        # FORM D: [ERROR] methodName Time elapsed: ... <<< FAILURE!
        for m in _SUREFIRE_FORM_D.finditer(clean_l):
            meth = m.group(1)
            raw_bare_methods.add(meth)

        # Other languages / frameworks (Pytest, Gradle, Go, Rust)
        for pat in _OTHER_TEST_PATTERNS:
            for m in pat.finditer(clean_l):
                groups = [g for g in m.groups() if g]
                if groups:
                    other_ids.add("::".join(groups).strip())

    # JOIN RULE:
    # 1. Gather all known FQN classes (from FORM B and FORM A)
    known_fqn_classes = set(raw_fqn_classes)
    for fm in raw_fqn_methods:
        c = fm.split("::")[0]
        if "." in c:
            known_fqn_classes.add(c)

    final_ids: set[str] = set(raw_fqn_methods) | other_ids
    consumed_classes: set[str] = set()

    # 2. Reconcile FORM C (Class, Method) with FQN classes
    for cls, meth in raw_simple_methods:
        matching_fqns = [fqn for fqn in known_fqn_classes if fqn.split(".")[-1] == cls]
        if len(matching_fqns) == 1:
            fqn_cls = matching_fqns[0]
            final_ids.add(f"{fqn_cls}::{meth}")
            consumed_classes.add(fqn_cls)
        else:
            # 0 matches (e.g. OTP) or ambiguous (>= 2) -> keep bare Class::method
            final_ids.add(f"{cls}::{meth}")

    # 3. Reconcile FORM D bare methods if exactly one FQN class is known
    for meth in raw_bare_methods:
        if len(known_fqn_classes) == 1:
            fqn_cls = next(iter(known_fqn_classes))
            final_ids.add(f"{fqn_cls}::{meth}")
            consumed_classes.add(fqn_cls)
        else:
            final_ids.add(meth)

    # 4. Retain unconsumed FQN classes where no method was resolved
    for fqn in raw_fqn_classes:
        if fqn not in consumed_classes and not any(id_str.startswith(f"{fqn}::") for id_str in final_ids):
            final_ids.add(fqn)

    return final_ids


def classify_log(path: Path) -> tuple[str, set[str], bool]:
    """Classify a single gzipped JSONL log file into one bucket.

    Returns (bucket_name, distinct_failing_test_ids, is_truncated).
    Buckets: TEST_FAILURE, TEST_RAN_CLEAN, NO_TEST_OUTPUT, UNREADABLE.
    """
    try:
        raw = path.read_bytes()
        decomp = gzip.decompress(raw)
        line = decomp.split(b"\n", 1)[0]
        rec = json.loads(line)
        body = rec.get("body", "")
        if not isinstance(body, str):
            return "NO_TEST_OUTPUT", set(), False
    except Exception:
        return "UNREADABLE", set(), False

    is_truncated = bool(TRUNCATION_PATTERN.search(body))

    if any(k in body for k in FAIL_KEYWORDS) and PATTERNS["TEST_FAILURE"].search(body):
        failing_ids = extract_failing_test_ids(body)
        return "TEST_FAILURE", failing_ids, is_truncated
    elif any(k in body for k in CLEAN_KEYWORDS) and PATTERNS["TEST_RAN_CLEAN"].search(body):
        return "TEST_RAN_CLEAN", set(), is_truncated
    else:
        return "NO_TEST_OUTPUT", set(), is_truncated


@dataclass
class RepoYieldStats:
    repo: str
    total_logs: int = 0
    test_failure: int = 0
    test_ran_clean: int = 0
    no_test_output: int = 0
    unreadable: int = 0
    truncated: int = 0
    failing_test_ids: set[str] = field(default_factory=set)
    failing_tests_per_log_sum: int = 0


@dataclass
class CorpusYieldSummary:
    timestamp_utc: str
    total_logs: int = 0
    test_failure: int = 0
    test_ran_clean: int = 0
    no_test_output: int = 0
    unreadable: int = 0
    truncated: int = 0
    all_failing_test_ids: set[str] = field(default_factory=set)
    failing_tests_per_log_sum: int = 0
    repo_stats: dict[str, RepoYieldStats] = field(default_factory=dict)


def scan_corpus(
    root: Path = DEFAULT_RAW_ROOT, limit: int | None = None
) -> CorpusYieldSummary:
    """Scan the job log files in data/raw and compile classification yield summary."""
    paths = sorted(root.glob("*/job/*/*/*.jsonl.gz"))
    if limit is not None and limit > 0:
        paths = paths[:limit]

    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    summary = CorpusYieldSummary(timestamp_utc=now_utc, total_logs=len(paths))

    for path in paths:
        # Path structure: data/raw/<owner__repo>/job/<shard>/<unit>/logs.jsonl.gz
        parts = path.parts
        raw_idx = parts.index(root.name) if root.name in parts else -1
        if raw_idx >= 0 and len(parts) > raw_idx + 1:
            repo_folder = parts[raw_idx + 1]
            repo_name = repo_folder.replace("__", "/")
        else:
            repo_name = "unknown"

        if repo_name not in summary.repo_stats:
            summary.repo_stats[repo_name] = RepoYieldStats(repo=repo_name)
        rstats = summary.repo_stats[repo_name]

        rstats.total_logs += 1
        bucket, failing_ids, is_trunc = classify_log(path)

        if is_trunc:
            summary.truncated += 1
            rstats.truncated += 1

        if bucket == "TEST_FAILURE":
            summary.test_failure += 1
            rstats.test_failure += 1
            rstats.failing_test_ids.update(failing_ids)
            rstats.failing_tests_per_log_sum += len(failing_ids)
            summary.all_failing_test_ids.update(failing_ids)
            summary.failing_tests_per_log_sum += len(failing_ids)
        elif bucket == "TEST_RAN_CLEAN":
            summary.test_ran_clean += 1
            rstats.test_ran_clean += 1
        elif bucket == "NO_TEST_OUTPUT":
            summary.no_test_output += 1
            rstats.no_test_output += 1
        elif bucket == "UNREADABLE":
            summary.unreadable += 1
            rstats.unreadable += 1

    return summary


def generate_report(summary: CorpusYieldSummary) -> str:
    """Generate deterministic Markdown report from the yield summary."""
    denom = summary.total_logs
    pct = lambda n: (n / denom * 100.0) if denom > 0 else 0.0

    mean_per_fail_log = (
        (summary.failing_tests_per_log_sum / summary.test_failure)
        if summary.test_failure > 0
        else 0.0
    )

    lines: list[str] = []
    lines.append("# BlastRadius — Captured Log Yield Analysis")
    lines.append("")
    lines.append(f"**Generated:** {summary.timestamp_utc}  ")
    lines.append(f"**Total Logs Examined (Denominator):** {summary.total_logs:,}  ")
    lines.append(f"**Repositories Represented:** {len(summary.repo_stats):,}  ")
    lines.append("")
    lines.append("## 1. Corpus Classification Summary")
    lines.append("")
    lines.append("| Classification Bucket | Count | Percentage | Description |")
    lines.append("| :--- | :---: | :---: | :--- |")
    lines.append(
        f"| **TEST_FAILURE** | **{summary.test_failure:,}** | **{pct(summary.test_failure):.2f}%** | Log contains a non-zero test failure or error line |"
    )
    lines.append(
        f"| **TEST_RAN_CLEAN** | **{summary.test_ran_clean:,}** | **{pct(summary.test_ran_clean):.2f}%** | Tests ran and passed completely (job failed at build/lint/packaging step) |"
    )
    lines.append(
        f"| **NO_TEST_OUTPUT** | **{summary.no_test_output:,}** | **{pct(summary.no_test_output):.2f}%** | No test execution output detected (compile failure, cancelled, timeout) |"
    )
    lines.append(
        f"| **UNREADABLE** | **{summary.unreadable:,}** | **{pct(summary.unreadable):.2f}%** | File corrupted or unparseable gzip/JSON |"
    )
    lines.append(
        f"| **Total** | **{summary.total_logs:,}** | **100.00%** | Full captured job log corpus |"
    )
    lines.append("")
    lines.append("## 2. Failing Test Identifiers")
    lines.append("")
    lines.append(
        f"- **Distinct Failing Test Identifiers (Corpus-Wide):** {len(summary.all_failing_test_ids):,}"
    )
    lines.append(
        f"- **Total Failing Test Occurrences Across Logs:** {summary.failing_tests_per_log_sum:,}"
    )
    lines.append(
        f"- **Mean Distinct Failing Tests per `TEST_FAILURE` Log:** {mean_per_fail_log:.2f}"
    )
    lines.append(
        f"- **Truncated Logs Detected:** {summary.truncated:,} ({pct(summary.truncated):.2f}%)"
    )
    lines.append("")
    lines.append("## 3. Per-Repository Breakdown")
    lines.append("")
    lines.append(
        "| Repository | Total Logs | TEST_FAILURE | TEST_RAN_CLEAN | NO_TEST_OUTPUT | UNREADABLE | Distinct Failing Tests | Failure Yield (%) |"
    )
    lines.append(
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    )

    for repo_name in sorted(summary.repo_stats.keys()):
        r = summary.repo_stats[repo_name]
        yield_pct = (
            (r.test_failure / r.total_logs * 100.0) if r.total_logs > 0 else 0.0
        )
        lines.append(
            f"| `{repo_name}` | {r.total_logs:,} | {r.test_failure:,} | "
            f"{r.test_ran_clean:,} | {r.no_test_output:,} | {r.unreadable:,} | "
            f"{len(r.failing_test_ids):,} | {yield_pct:.1f}% |"
        )

    lines.append("")
    return "\n".join(lines) + "\n"


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure how many captured logs actually contain test failures."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of logs to process (default: all)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Path to write Markdown output (default: stdout)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_RAW_ROOT,
        help=f"Root directory of raw captures (default: {DEFAULT_RAW_ROOT})",
    )
    return parser.parse_args(args)


def main() -> None:
    args = parse_args()
    summary = scan_corpus(root=args.root, limit=args.limit)
    report = generate_report(summary)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)


if __name__ == "__main__":
    main()
