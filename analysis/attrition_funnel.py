"""Regenerate the BlastRadius attrition funnel table from disk artefacts.

Per ROADMAP §23.3 and T0.7.
Reads ONLY:
  - data/frame/ATTRITION.json
  - data/frame/attrition_stage.csv
  - data/frame/frame_v1.csv
  - data/frame/frame_v1_reserve.csv

Emits paper/generated/attrition_funnel.md and prints the markdown table to stdout.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

FRAME_DIR = Path("data/frame")
ATTRITION_JSON_PATH = FRAME_DIR / "ATTRITION.json"
ATTRITION_STAGE_PATH = FRAME_DIR / "attrition_stage.csv"
FRAME_V1_PATH = FRAME_DIR / "frame_v1.csv"
FRAME_V1_RESERVE_PATH = FRAME_DIR / "frame_v1_reserve.csv"

OUTPUT_DIR = Path("paper/generated")
OUTPUT_MD_PATH = OUTPUT_DIR / "attrition_funnel.md"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def generate_funnel() -> str:
    # 1. Read input artefacts
    attrition_stage_rows = _read_csv(ATTRITION_STAGE_PATH)
    frame_v1_rows = _read_csv(FRAME_V1_PATH)
    reserve_rows = _read_csv(FRAME_V1_RESERVE_PATH)

    with ATTRITION_JSON_PATH.open("r", encoding="utf-8") as fh:
        attrition_json = json.load(fh)

    # 2. Compute counts dynamically from attrition_stage.csv
    total_raw = len(attrition_stage_rows)
    raw_java = sum(1 for r in attrition_stage_rows if r.get("lang") == "Java")
    raw_python = sum(1 for r in attrition_stage_rows if r.get("lang") == "Python")

    verdicts = Counter(r.get("verdict", "") for r in attrition_stage_rows)
    verdict_by_lang: dict[str, Counter[str]] = {}
    for r in attrition_stage_rows:
        v = r.get("verdict", "")
        lang = r.get("lang", "")
        verdict_by_lang.setdefault(v, Counter())[lang] += 1

    # Drops for CI liveness
    no_ci_count = verdicts.get("no_ci", 0)
    api_error_count = verdicts.get("api_error", 0)
    ci_removed_total = no_ci_count + api_error_count

    ci_removed_java = verdict_by_lang.get("no_ci", Counter())["Java"] + verdict_by_lang.get("api_error", Counter())["Java"]
    ci_removed_python = verdict_by_lang.get("no_ci", Counter())["Python"] + verdict_by_lang.get("api_error", Counter())["Python"]

    ci_survivors_total = total_raw - ci_removed_total
    ci_survivors_java = raw_java - ci_removed_java
    ci_survivors_python = raw_python - ci_removed_python

    # Drops for test workflow classification
    no_test_count = verdicts.get("no_test_workflow", 0)
    test_removed_java = verdict_by_lang.get("no_test_workflow", Counter())["Java"]
    test_removed_python = verdict_by_lang.get("no_test_workflow", Counter())["Python"]

    test_survivors_total = ci_survivors_total - no_test_count
    test_survivors_java = ci_survivors_java - test_removed_java
    test_survivors_python = ci_survivors_python - test_removed_python

    # Frame sampling (frame_v1 vs reserve)
    f1_java = sum(1 for r in frame_v1_rows if r.get("lang") == "Java")
    f1_python = sum(1 for r in frame_v1_rows if r.get("lang") == "Python")
    f1_total = len(frame_v1_rows)

    reserve_java = sum(1 for r in reserve_rows if r.get("lang") == "Java")
    reserve_python = sum(1 for r in reserve_rows if r.get("lang") == "Python")
    reserve_total = len(reserve_rows)

    # 3. Format Markdown Table
    # Drop reason breakdown formatted from dynamic counts
    ci_drop_str = f"{ci_removed_total:,} ({no_ci_count:,} no_ci, {api_error_count:,} api_error)"

    lines: list[str] = []
    lines.append("# BlastRadius Repository Frame Attrition Funnel")
    lines.append("")
    lines.append("Per ROADMAP §23.3 and T0.7. Generated deterministically by `analysis/attrition_funnel.py`.")
    lines.append("")
    lines.append("| Stage | Filter | Input | Removed | Survivors | Java | Python | Status |")
    lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |")

    # Stage 0: SEART export
    lines.append(
        f"| **0. SEART Export** | Stars ≥500, Commits ≥1000, not a fork, pushed in last 60d, has license[^1] | — | — | **{total_raw:,}** | {raw_java:,} | {raw_python:,} | Measured |"
    )

    # Stage 1: CI liveness
    lines.append(
        f"| **1. CI Liveness** | ≥100 GitHub Actions workflow runs in trailing 90 days | {total_raw:,} | {ci_drop_str} | **{ci_survivors_total:,}** | {ci_survivors_java:,} | {ci_survivors_python:,} | Measured |"
    )

    # Stage 2: Test intent workflow
    lines.append(
        f"| **2. Test Intent** | ≥1 workflow classified as test-intent (`test|ci|build|pytest|mvn|gradle`) | {ci_survivors_total:,} | {no_test_count:,} | **{test_survivors_total:,}** | {test_survivors_java:,} | {test_survivors_python:,} | Measured |"
    )

    # Stage 3: Stratified frame sample draw
    seed = attrition_json.get("seed", 20261110)
    lines.append(
        f"| **3. Sample Draw** | Seeded language-stratified draw (150 Java + 150 Python; Seed {seed})[^2] | {test_survivors_total:,} | {reserve_total:,} | **{f1_total:,}** | {f1_java:,} | {f1_python:,} | Measured |"
    )

    # Stages 5-8: Unmeasured pipeline stages
    lines.append(
        "| **4. Parseable Outcomes** | Produces parseable test outcomes (ROADMAP §23.3 stage 5)[^3] | 300 | not yet measured | not yet measured | not yet measured | not yet measured | Pending harvest |"
    )
    lines.append(
        "| **5. Fault-Revealing** | Produces ≥1 fault-revealing instance (ROADMAP §23.3 stage 6)[^4] | not yet measured | not yet measured | not yet measured | not yet measured | not yet measured | Pending curation |"
    )
    lines.append(
        "| **6. Graph Budget** | Graph builds within time and memory budget (ROADMAP §23.3 stage 7)[^5] | not yet measured | not yet measured | not yet measured | not yet measured | not yet measured | Pending graph build |"
    )
    lines.append(
        "| **7. Test-Node Binding** | Test-node binding rate ≥70% (ROADMAP §23.3 stage 8, T8)[^6] | not yet measured | not yet measured | not yet measured | not yet measured | not yet measured | Pending evaluation |"
    )

    lines.append("")
    lines.append("### Footnotes & Explanatory Notes")
    lines.append("")
    lines.append("[^1]: **SEART Export**: Java (1,123) and Python (2,548) candidate queries merged from `data/frame/seart_a.csv` and `data/frame/seart_b.csv`. Criterion 7 (≥50 PRs in 90 days) was deferred because SEART only indexes lifetime PR counts (`data/frame/QUERY.md` §2 row 7).")
    lines.append(f"[^2]: **Reserve Pool**: The {reserve_total:,} remaining eligible repositories ({reserve_java:,} Java, {reserve_python:,} Python) are retained in `data/frame/frame_v1_reserve.csv` for replacement and widening under T14.")
    lines.append("[^3]: **Stage 5 (Parseable Outcomes)**: Measured during Stage 1 harvest and log-parsing phase (T1).")
    lines.append("[^4]: **Stage 6 (Fault-Revealing Instances)**: Measured during instance curation and flaky-test filtering (T2).")
    lines.append("[^5]: **Stage 7 (Graph Build Budget)**: Measured during code graph construction under time and memory caps (§19.4, T4).")
    lines.append("[^6]: **Stage 8 (Test-Node Binding Rate)**: Measured during static test binding evaluation against ground-truth suites (T8).")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    content = generate_funnel()

    # Write output markdown
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD_PATH.write_text(content, encoding="utf-8")

    # Print exact content to stdout
    print(content)


if __name__ == "__main__":
    main()
