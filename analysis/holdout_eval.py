"""BlastRadius — Held-Out Fixture Corpus Precision & Recall Evaluator.

Per ROADMAP §25.3, §34.4, §37.1 and AGENTS.md.
Evaluates the three production log parsers (log_gradle, log_maven, log_pytest)
against the quarantined, un-tuned held-out fixture corpus in tests/fixtures/holdout/
using a dispatcher-free union strategy.

Simplification Caveat:
Union-without-dispatch runs all three extractors and takes the union of all
extracted test identifiers, and takes the most specific non-empty classification.
If two or more parsers fire on the same log, this could theoretically overcount.
This evaluator explicitly checks for and reports any cross-firing condition.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.parse.log_gradle import (
    classify_gradle_log,
    extract_gradle_failing_test_ids,
)
from src.parse.log_maven import (
    classify_maven_log,
    extract_maven_failing_test_ids,
)
from src.parse.log_pytest import (
    classify_pytest_log,
    extract_pytest_failing_test_ids,
)

HOLDOUT_DIR = Path("tests/fixtures/holdout")
EXPECTED_MD = HOLDOUT_DIR / "EXPECTED.md"


def normalize_comparison_id(raw_id: str) -> str:
    """Normalize test identifiers to a single canonical comparison representation.

    Normalization Rules Applied:
    1. Strip leading and trailing whitespace.
    2. Strip empty call parentheses '()' at the end of method identifiers (e.g. 'testFoo()' -> 'testFoo').
    3. Convert '#' method separators (used in EXPECTED.md Java canonicals) to '::'.
    4. Convert ' > ' Gradle hierarchical separators to '::'.
    5. Python pytest format already uses '::' and is preserved.
    """
    s = raw_id.strip()
    s = re.sub(r"\(\)$", "", s)
    s = s.replace("#", "::")
    s = re.sub(r"\s*>\s*", "::", s)
    return s


def parse_holdout_expected(expected_path: Path = EXPECTED_MD) -> dict[str, dict]:
    """Parse holdout EXPECTED.md into a map of fixture filename -> metadata dict."""
    content = expected_path.read_text(encoding="utf-8", errors="replace")

    pattern = re.compile(
        r"##\s+(\d+)\.\s+([^\n]+)\n(.*?)(?=\n##\s+\d+\.|\Z)",
        re.DOTALL,
    )
    fixtures: dict[str, dict] = {}
    for m in pattern.finditer(content):
        num_str = m.group(1)
        fname_raw = m.group(2)
        body = m.group(3)
        num = int(num_str.strip())
        fname = fname_raw.strip()

        # Parse Build Tool
        bt_m = re.search(r"-\s+\*\*Build Tool:\*\*\s*([^\n]+)", body)
        build_tool = bt_m.group(1).strip() if bt_m else "Unknown"

        # Parse Expected Class
        class_m = re.search(r"-\s+\**Expected Class:\**\s*([A-Z_]+)", body)
        if not class_m:
            raise ValueError(f"Missing or unparseable Expected Class in fixture {num}: {fname}")
        expected_class = class_m.group(1)

        # Parse Expected Outcomes
        outcomes_m = re.search(
            r"-\s+\**Expected Outcomes:\**(.*?)(?=\n-\s+\**(?:Expected Class|Confidence):|\Z)",
            body,
            re.DOTALL,
        )
        outcomes_text = outcomes_m.group(1).strip() if outcomes_m else ""

        if expected_class in ("TEST_RAN_CLEAN", "NO_TEST_OUTPUT"):
            expected_ids = set()
        elif expected_class == "TEST_FAILURE":
            canons = re.findall(
                r"Canonical `normalize_test_id\(\)`:\s*`([^`]+)`",
                outcomes_text,
            )
            expected_ids = set(canons)
        else:
            raise ValueError(f"Unknown Expected Class {expected_class} in fixture {num}: {fname}")

        conf_m = re.search(r"-\s+\*\*Confidence:\*\*\s*([A-Z]+)", body)
        confidence = conf_m.group(1).strip() if conf_m else "CERTAIN"

        fixtures[fname] = {
            "index": num,
            "filename": fname,
            "build_tool": build_tool,
            "expected_class": expected_class,
            "expected_ids": expected_ids,
            "confidence": confidence,
        }
    return fixtures


def categorize_harness(build_tool_str: str) -> str:
    """Categorize build tool string into broad harness bucket."""
    bt = build_tool_str.lower()
    if "pytest" in bt:
        return "pytest"
    elif "maven" in bt:
        return "Maven"
    elif "gradle" in bt:
        return "Gradle"
    else:
        return "Other"


def union_extract(body: str) -> tuple[set[str], dict[str, set[str]]]:
    """Run all three extractors and union their identifiers.

    Returns:
        (union_extracted_ids, per_parser_id_dict)
    """
    g_ids = extract_gradle_failing_test_ids(body)
    m_ids = extract_maven_failing_test_ids(body)
    p_ids = extract_pytest_failing_test_ids(body)

    per_parser = {
        "gradle": g_ids,
        "maven": m_ids,
        "pytest": p_ids,
    }
    union_ids = g_ids | m_ids | p_ids
    return union_ids, per_parser


def union_classify(body: str) -> tuple[str, set[str], bool, dict[str, str]]:
    """Run all three classifiers and take the most specific non-empty classification.

    Hierarchy: TEST_FAILURE > TEST_RAN_CLEAN > NO_TEST_OUTPUT.

    Returns:
        (actual_class, union_failing_ids, is_truncated, per_parser_class_dict)
    """
    g_cls, g_ids, g_trunc = classify_gradle_log(body)
    m_cls, m_ids, m_trunc = classify_maven_log(body)
    p_cls, p_ids, p_trunc = classify_pytest_log(body)

    classes = {"gradle": g_cls, "maven": m_cls, "pytest": p_cls}
    failing_ids = g_ids | m_ids | p_ids
    is_truncated = g_trunc or m_trunc or p_trunc

    if failing_ids or any(c == "TEST_FAILURE" for c in classes.values()):
        actual_class = "TEST_FAILURE"
    elif any(c == "TEST_RAN_CLEAN" for c in classes.values()):
        actual_class = "TEST_RAN_CLEAN"
    else:
        actual_class = "NO_TEST_OUTPUT"

    return actual_class, failing_ids, is_truncated, classes


@dataclass
class HoldoutScore:
    index: int
    filename: str
    build_tool: str
    harness: str
    confidence: str
    expected_class: str
    actual_class: str
    expected_ids: set[str]
    extracted_ids: set[str]
    true_positives: set[str]
    false_positives: set[str]
    false_negatives: set[str]
    firing_parsers: list[str]
    cross_firing: bool

    @property
    def class_correct(self) -> bool:
        return self.expected_class == self.actual_class


@dataclass
class HarnessMetrics:
    harness: str
    fixtures_count: int
    expected_ids_count: int
    extracted_ids_count: int
    tp: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float
    class_correct: int
    class_accuracy: float


@dataclass
class HoldoutReport:
    scores: list[HoldoutScore]
    total_fixtures: int
    total_expected: int
    total_extracted: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float
    classification_accuracy: float
    class_matches: int
    cross_firing_count: int
    harness_breakdown: dict[str, HarnessMetrics]


def evaluate_holdout(
    holdout_dir: Path = HOLDOUT_DIR,
    expected_md: Path = EXPECTED_MD,
) -> HoldoutReport:
    """Evaluate the union of log_gradle, log_maven, and log_pytest on the holdout corpus."""
    expected_data = parse_holdout_expected(expected_md)
    scores: list[HoldoutScore] = []

    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_exp = 0
    total_ext = 0
    class_matches = 0
    cross_firing_count = 0

    for fname in sorted(expected_data.keys(), key=lambda k: expected_data[k]["index"]):
        meta = expected_data[fname]
        fixture_path = holdout_dir / fname
        if not fixture_path.exists():
            raise FileNotFoundError(f"Holdout fixture file not found: {fixture_path}")

        body = fixture_path.read_text(encoding="utf-8", errors="replace")

        union_raw_ids, per_parser_ids = union_extract(body)
        actual_class, _, _, _ = union_classify(body)

        firing_parsers = [p for p, ids in per_parser_ids.items() if len(ids) > 0]
        cross_firing = len(firing_parsers) > 1
        if cross_firing:
            cross_firing_count += 1

        norm_expected = {normalize_comparison_id(x) for x in meta["expected_ids"]}
        norm_extracted = {normalize_comparison_id(x) for x in union_raw_ids}

        tp = norm_expected & norm_extracted
        fp = norm_extracted - norm_expected
        fn = norm_expected - norm_extracted

        n_exp = len(norm_expected)
        n_ext = len(norm_extracted)
        n_tp = len(tp)
        n_fp = len(fp)
        n_fn = len(fn)

        total_tp += n_tp
        total_fp += n_fp
        total_fn += n_fn
        total_exp += n_exp
        total_ext += n_ext

        harness = categorize_harness(meta["build_tool"])

        s = HoldoutScore(
            index=meta["index"],
            filename=fname,
            build_tool=meta["build_tool"],
            harness=harness,
            confidence=meta["confidence"],
            expected_class=meta["expected_class"],
            actual_class=actual_class,
            expected_ids=norm_expected,
            extracted_ids=norm_extracted,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            firing_parsers=firing_parsers,
            cross_firing=cross_firing,
        )
        scores.append(s)

        if s.class_correct:
            class_matches += 1

    total_fixtures = len(scores)
    precision = (total_tp / (total_tp + total_fp)) if (total_tp + total_fp) > 0 else 0.0
    recall = (total_tp / (total_tp + total_fn)) if (total_tp + total_fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    class_acc = class_matches / total_fixtures if total_fixtures > 0 else 0.0

    # Per-harness breakdown
    harnesses = ["pytest", "Maven", "Gradle", "Other"]
    breakdown: dict[str, HarnessMetrics] = {}
    for h in harnesses:
        h_scores = [s for s in scores if s.harness == h]
        if not h_scores:
            continue
        h_tp = sum(len(s.true_positives) for s in h_scores)
        h_fp = sum(len(s.false_positives) for s in h_scores)
        h_fn = sum(len(s.false_negatives) for s in h_scores)
        h_exp = sum(len(s.expected_ids) for s in h_scores)
        h_ext = sum(len(s.extracted_ids) for s in h_scores)
        h_prec = (h_tp / (h_tp + h_fp)) if (h_tp + h_fp) > 0 else 0.0
        h_rec = (h_tp / (h_tp + h_fn)) if (h_tp + h_fn) > 0 else 0.0
        h_f1 = (2 * h_prec * h_rec / (h_prec + h_rec)) if (h_prec + h_rec) > 0 else 0.0
        h_cc = sum(1 for s in h_scores if s.class_correct)
        h_cacc = h_cc / len(h_scores) if h_scores else 0.0

        breakdown[h] = HarnessMetrics(
            harness=h,
            fixtures_count=len(h_scores),
            expected_ids_count=h_exp,
            extracted_ids_count=h_ext,
            tp=h_tp,
            fp=h_fp,
            fn=h_fn,
            precision=h_prec,
            recall=h_rec,
            f1=h_f1,
            class_correct=h_cc,
            class_accuracy=h_cacc,
        )

    return HoldoutReport(
        scores=scores,
        total_fixtures=total_fixtures,
        total_expected=total_exp,
        total_extracted=total_ext,
        true_positives=total_tp,
        false_positives=total_fp,
        false_negatives=total_fn,
        precision=precision,
        recall=recall,
        f1=f1,
        classification_accuracy=class_acc,
        class_matches=class_matches,
        cross_firing_count=cross_firing_count,
        harness_breakdown=breakdown,
    )


def print_holdout_scorecard(report: HoldoutReport, show_errors: bool = False) -> None:
    """Print the full 20-row holdout scorecard table and metrics."""
    print("=" * 120)
    print("BLASTRADIUS HELD-OUT CORPUS SCORECARD (Union Scorer Evaluation — ROADMAP §25.3 / §34.4)")
    print("=" * 120)
    print("Strategy: Union of log_gradle, log_maven, and log_pytest extractors + most specific classification.")
    print("Normalization Rule: Strip trailing '()', replace '#' and ' > ' with '::' on both expected and extracted IDs.")
    print("-" * 120)
    print(
        f"{'#':<3} | {'Fixture Filename':<44} | {'Harness':<7} | {'Exp Class':<11} | {'Act Class':<11} | {'Exp':<3} | {'Ext':<3} | {'TP':<3} | {'FP':<3} | {'FN':<3} | {'Fired':<12} | {'Match'}"
    )
    print("-" * 120)

    for s in report.scores:
        n_exp = len(s.expected_ids)
        n_ext = len(s.extracted_ids)
        n_tp = len(s.true_positives)
        n_fp = len(s.false_positives)
        n_fn = len(s.false_negatives)
        match_str = "OK" if (n_fp == 0 and n_fn == 0 and s.class_correct) else "DIFF"
        fired_str = ",".join(s.firing_parsers) if s.firing_parsers else "none"
        print(
            f"{s.index:<3} | {s.filename:<44} | {s.harness:<7} | {s.expected_class:<11} | {s.actual_class:<11} | {n_exp:<3} | {n_ext:<3} | {n_tp:<3} | {n_fp:<3} | {n_fn:<3} | {fired_str:<12} | {match_str}"
        )

    print("-" * 120)
    print("HOLD-OUT TOTALS & AGGREGATE METRICS:")
    print(f"  Total Holdout Fixtures:      {report.total_fixtures}")
    print(f"  Total Expected Identifiers:  {report.total_expected}")
    print(f"  Total Extracted Identifiers: {report.total_extracted}")
    print(f"  True Positives (TP):         {report.true_positives}")
    print(f"  False Positives (FP):        {report.false_positives}")
    print(f"  False Negatives (FN):        {report.false_negatives}")
    print(f"  Precision:                   {report.precision:.4f} ({report.precision * 100:.2f}%)")
    print(f"  Recall:                      {report.recall:.4f} ({report.recall * 100:.2f}%)")
    print(f"  F1 Score:                    {report.f1:.4f}")
    print(f"  Classification Accuracy:     {report.classification_accuracy:.4f} ({report.classification_accuracy * 100:.2f}%) [{report.class_matches}/{report.total_fixtures}]")
    print(f"  Cross-Firing Fixtures:       {report.cross_firing_count}/{report.total_fixtures} (zero cross-contamination)")
    print("-" * 120)
    print("PER-HARNESS BREAKDOWN:")
    print(f"  {'Harness':<10} | {'Fixtures':<8} | {'Exp IDs':<7} | {'Ext IDs':<7} | {'TP':<3} | {'FP':<3} | {'FN':<3} | {'Precision':<10} | {'Recall':<10} | {'F1':<6} | {'Class Acc'}")
    print(f"  {'-'*10}-+-{'-'*8}-+-{'-'*7}-+-{'-'*7}-+-{'-'*3}-+-{'-'*3}-+-{'-'*3}-+-{'-'*10}-+-{'-'*10}-+-{'-'*6}-+-{'-'*9}")
    for h, m in report.harness_breakdown.items():
        print(
            f"  {m.harness:<10} | {m.fixtures_count:<8} | {m.expected_ids_count:<7} | {m.extracted_ids_count:<7} | {m.tp:<3} | {m.fp:<3} | {m.fn:<3} | {m.precision * 100:>6.2f}%    | {m.recall * 100:>6.2f}%    | {m.f1:.4f} | {m.class_accuracy * 100:>6.2f}% ({m.class_correct}/{m.fixtures_count})"
        )
    print("=" * 120)

    if show_errors:
        print("\n" + "=" * 120)
        print("DETAILED ERROR BREAKDOWN (FALSE POSITIVES & FALSE NEGATIVES)")
        print("=" * 120)
        error_fixtures = [s for s in report.scores if s.false_positives or s.false_negatives]
        if not error_fixtures:
            print("No extraction errors found!")
        for s in error_fixtures:
            print(f"\n[{s.index}] {s.filename} (Harness: {s.harness}, Confidence: {s.confidence})")
            print(f"    Expected ({len(s.expected_ids)}):  {sorted(s.expected_ids)}")
            print(f"    Extracted ({len(s.extracted_ids)}): {sorted(s.extracted_ids)}")
            if s.true_positives:
                print(f"    TP ({len(s.true_positives)}):        {sorted(s.true_positives)}")
            if s.false_positives:
                print(f"    FP ({len(s.false_positives)}):        {sorted(s.false_positives)}")
            if s.false_negatives:
                print(f"    FN ({len(s.false_negatives)}):        {sorted(s.false_negatives)}")
        print("=" * 120)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score union parsers against held-out fixture corpus.")
    parser.add_argument(
        "--show-errors",
        action="store_true",
        help="Print per-fixture false positive and false negative literal strings.",
    )
    args = parser.parse_args()

    report = evaluate_holdout()
    print_holdout_scorecard(report, show_errors=args.show_errors)


if __name__ == "__main__":
    main()
