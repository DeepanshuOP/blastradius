"""BlastRadius — Fixture Corpus Precision & Recall Scorecard.

Per ROADMAP §25.3, §34.4, §37.1 and AGENTS.md.
Evaluates classification and test-identifier extraction precision/recall
against the hand-labelled ground truth in tests/fixtures/logs/EXPECTED.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.parse.dispatch import (
    classify_dispatch_log,
    extract_dispatch_failing_test_ids,
)

FIXTURES_DIR = Path("tests/fixtures/logs")
EXPECTED_MD = FIXTURES_DIR / "EXPECTED.md"


def parse_expected(expected_path: Path = EXPECTED_MD) -> dict[str, dict]:
    """Parse EXPECTED.md into a map of fixture filename -> metadata dict."""
    content = expected_path.read_text(encoding="utf-8", errors="replace")
    main_doc = content.split("## Analysis of the Four Anomalous Repositories")[0]

    pattern = re.compile(
        r"##\s+(\d+)\.\s+([^\n]+)\n(.*?)(?=\n##\s+\d+\.|\Z)",
        re.DOTALL,
    )
    fixtures: dict[str, dict] = {}
    for m in pattern.finditer(main_doc):
        num_str = m.group(1)
        fname_raw = m.group(2)
        body = m.group(3)
        num = int(num_str.strip())
        fname = fname_raw.strip()

        # Parse Expected Outcomes
        outcomes_m = re.search(
            r"-\s+\*\*Expected Outcomes:\*\*(.*?)(?=\n-\s+\*\*Confidence:|\Z)",
            body,
            re.DOTALL,
        )
        outcomes_text = outcomes_m.group(1).strip() if outcomes_m else ""

        if "NO_TEST_OUTCOMES" in outcomes_text:
            expected_ids = set()
            if "passed clean" in outcomes_text.lower():
                expected_class = "TEST_RAN_CLEAN"
            else:
                expected_class = "NO_TEST_OUTPUT"
        else:
            canons = re.findall(
                r"Canonical `normalize_test_id\(\)`:\s*`([^`]+)`",
                outcomes_text,
            )
            expected_ids = set(canons)
            expected_class = "TEST_FAILURE"

        conf_m = re.search(r"-\s+\*\*Confidence:\*\*\s*([A-Z]+)", body)
        confidence = conf_m.group(1).strip() if conf_m else "CERTAIN"

        fixtures[fname] = {
            "index": num,
            "filename": fname,
            "expected_class": expected_class,
            "expected_ids": expected_ids,
            "confidence": confidence,
        }
    return fixtures


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


@dataclass
class FixtureScore:
    index: int
    filename: str
    confidence: str
    expected_class: str
    actual_class: str
    expected_ids: set[str]
    extracted_ids: set[str]
    true_positives: set[str]
    false_positives: set[str]
    false_negatives: set[str]

    @property
    def class_correct(self) -> bool:
        return self.expected_class == self.actual_class


@dataclass
class Report:
    scores: list[FixtureScore]
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
    no_failure_fps: int


def score_corpus(
    classify_fn: Callable[[str], tuple[str, set[str], bool]] | None = None,
    extract_fn: Callable[[str], set[str]] | None = None,
    fixtures_dir: Path = FIXTURES_DIR,
    expected_md: Path = EXPECTED_MD,
) -> Report:
    """Score an injected classifier and extractor against the fixture corpus."""
    if classify_fn is None:
        classify_fn = classify_dispatch_log
    if extract_fn is None:
        extract_fn = extract_dispatch_failing_test_ids

    expected_data = parse_expected(expected_md)
    scores: list[FixtureScore] = []

    total_tp = 0
    total_fp = 0
    total_fn = 0
    total_exp = 0
    total_ext = 0
    class_matches = 0
    no_failure_fps = 0

    for fname in sorted(expected_data.keys(), key=lambda k: expected_data[k]["index"]):
        meta = expected_data[fname]
        fixture_path = fixtures_dir / fname
        if not fixture_path.exists():
            raise FileNotFoundError(f"Fixture file not found: {fixture_path}")

        body = fixture_path.read_text(encoding="utf-8", errors="replace")

        if classify_fn is not None:
            actual_class, extracted_raw_ids, _ = classify_fn(body)
        else:
            extracted_raw_ids = extract_fn(body) if extract_fn else set()
            actual_class = "TEST_FAILURE" if extracted_raw_ids else "NO_TEST_OUTPUT"

        norm_expected = {normalize_comparison_id(x) for x in meta["expected_ids"]}
        norm_extracted = {normalize_comparison_id(x) for x in extracted_raw_ids}

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

        s = FixtureScore(
            index=meta["index"],
            filename=fname,
            confidence=meta["confidence"],
            expected_class=meta["expected_class"],
            actual_class=actual_class,
            expected_ids=norm_expected,
            extracted_ids=norm_extracted,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
        )
        scores.append(s)

        if s.class_correct:
            class_matches += 1
        if n_exp == 0 and n_ext > 0:
            no_failure_fps += 1

    total_fixtures = len(scores)
    precision = (total_tp / (total_tp + total_fp)) if (total_tp + total_fp) > 0 else 0.0
    recall = (total_tp / (total_tp + total_fn)) if (total_tp + total_fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    class_acc = class_matches / total_fixtures if total_fixtures > 0 else 0.0

    return Report(
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
        no_failure_fps=no_failure_fps,
    )


def print_scorecard(report: Report, show_errors: bool = False) -> None:
    print("=" * 110)
    print("BLASTRADIUS FIXTURE CORPUS SCORECARD (T1.1a Evaluation)")
    print("=" * 110)
    print(
        "Normalization Rule: Strip trailing '()', replace '#' and ' > ' with '::' on both expected and extracted IDs."
    )
    print("-" * 110)
    print(
        f"{'#':<3} | {'Fixture Filename':<48} | {'Exp Class':<11} | {'Act Class':<11} | {'Exp':<3} | {'Ext':<3} | {'TP':<3} | {'FP':<3} | {'FN':<3} | {'Match'}"
    )
    print("-" * 110)

    for s in report.scores:
        n_exp = len(s.expected_ids)
        n_ext = len(s.extracted_ids)
        n_tp = len(s.true_positives)
        n_fp = len(s.false_positives)
        n_fn = len(s.false_negatives)
        match_str = "OK" if (n_fp == 0 and n_fn == 0 and s.class_correct) else "DIFF"
        print(
            f"{s.index:<3} | {s.filename:<48} | {s.expected_class:<11} | {s.actual_class:<11} | {n_exp:<3} | {n_ext:<3} | {n_tp:<3} | {n_fp:<3} | {n_fn:<3} | {match_str}"
        )

    print("-" * 110)
    print("CORPUS TOTALS & METRICS:")
    print(f"  Total Fixtures:              {report.total_fixtures}")
    print(f"  Total Expected Identifiers:  {report.total_expected}")
    print(f"  Total Extracted Identifiers: {report.total_extracted}")
    print(f"  True Positives (TP):         {report.true_positives}")
    print(f"  False Positives (FP):        {report.false_positives}")
    print(f"  False Negatives (FN):        {report.false_negatives}")
    print(f"  Precision:                   {report.precision:.4f} ({report.precision * 100:.2f}%)")
    print(f"  Recall:                      {report.recall:.4f} ({report.recall * 100:.2f}%)")
    print(f"  F1 Score:                    {report.f1:.4f}")
    print(f"  Classification Accuracy:     {report.classification_accuracy:.4f} ({report.classification_accuracy * 100:.2f}%) [{report.class_matches}/{report.total_fixtures}]")
    print(f"  No-Failure Fixtures with FP: {report.no_failure_fps}/20")
    print("=" * 110)

    if show_errors:
        print("\n" + "=" * 110)
        print("DETAILED ERROR BREAKDOWN (FALSE POSITIVES & FALSE NEGATIVES)")
        print("=" * 110)
        error_fixtures = [s for s in report.scores if s.false_positives or s.false_negatives]
        if not error_fixtures:
            print("No extraction errors found!")
        for s in error_fixtures:
            print(f"\n[{s.index}] {s.filename} (Confidence: {s.confidence})")
            print(f"    Expected ({len(s.expected_ids)}):  {sorted(s.expected_ids)}")
            print(f"    Extracted ({len(s.extracted_ids)}): {sorted(s.extracted_ids)}")
            if s.true_positives:
                print(f"    TP ({len(s.true_positives)}):        {sorted(s.true_positives)}")
            if s.false_positives:
                print(f"    FP ({len(s.false_positives)}):        {sorted(s.false_positives)}")
            if s.false_negatives:
                print(f"    FN ({len(s.false_negatives)}):        {sorted(s.false_negatives)}")
        print("=" * 110)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score extractor against fixture corpus.")
    parser.add_argument(
        "--show-errors",
        action="store_true",
        help="Print per-fixture false positive and false negative literal strings.",
    )
    args = parser.parse_args()

    report = score_corpus()
    print_scorecard(report, show_errors=args.show_errors)


if __name__ == "__main__":
    main()
