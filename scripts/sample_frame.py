"""Draw the seeded, language-stratified BR frame sample plus reserve list.

T0.7/T0.8/T14 (ROADMAP §23.3 attrition funnel, §23.4 language balance).
Reads the frozen kept-repo set (data/frame/repos.csv) and the per-stage
verdict log (data/frame/attrition_stage.csv), draws a stratified 150-Java +
150-Python sample for frame_v1.csv, writes the remaining kept repos to
frame_v1_reserve.csv in the order they would be promoted under T14 frame
widening, and writes the attrition funnel to ATTRITION.json.
"""

from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

# Published seed for the frame_v1 draw (T0.8 frame-freeze protocol). Do not
# change without bumping the frame version and re-running affected analyses.
SEED = 20261110

FRAME_DIR = Path("data/frame")
REPOS_PATH = FRAME_DIR / "repos.csv"
ATTRITION_STAGE_PATH = FRAME_DIR / "attrition_stage.csv"
FRAME_V1_PATH = FRAME_DIR / "frame_v1.csv"
RESERVE_PATH = FRAME_DIR / "frame_v1_reserve.csv"
ATTRITION_JSON_PATH = FRAME_DIR / "ATTRITION.json"

EXPECTED_KEPT_COUNT = 2333
SAMPLE_PER_LANGUAGE = 150
LANGUAGES = ("Java", "Python")

# ROADMAP §23.3 stages 5-8: not measurable from repos.csv / attrition_stage.csv
# alone. Listed so the funnel shows they exist without inventing a count.
NOT_YET_MEASURED_STAGES = (
    ("produces_parseable_outcomes", "ROADMAP §23.3 stage 5 — produces parseable test outcomes"),
    ("fault_revealing_instance", "ROADMAP §23.3 stage 6 — produces ≥1 fault-revealing instance"),
    ("graph_builds_in_budget", "ROADMAP §23.3 stage 7 — graph builds within budget (§19.4)"),
    ("test_node_binding_rate", "ROADMAP §23.3 stage 8 — test-node binding rate ≥70% (T8)"),
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        header = list(reader.fieldnames or [])
        rows = list(reader)
    return header, rows


def write_csv(path: Path, header: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def draw_sample(
    rows: list[dict[str, str]], seed: int = SEED
) -> tuple[list[dict], list[dict]]:
    """Split kept rows into a language-stratified sample and reserve.

    Rows are sorted by (owner, repo) before drawing so the result does not
    depend on input file order, then permuted with a seeded RNG per
    language. The first SAMPLE_PER_LANGUAGE of the permutation become the
    sample (sample_rank 1..N); the rest become the reserve (reserve_rank
    1..M) in the order they would be promoted under T14 frame widening.
    """
    rng = random.Random(seed)
    sample_rows: list[dict] = []
    reserve_rows: list[dict] = []

    for lang in LANGUAGES:
        lang_rows = sorted(
            (row for row in rows if row["lang"] == lang),
            key=lambda row: (row["owner"], row["repo"]),
        )
        if len(lang_rows) < SAMPLE_PER_LANGUAGE:
            raise ValueError(
                f"{lang} has only {len(lang_rows)} kept repos, fewer than the "
                f"required sample size of {SAMPLE_PER_LANGUAGE} — refusing "
                "to silently under-sample"
            )
        shuffled = rng.sample(lang_rows, len(lang_rows))
        drawn = shuffled[:SAMPLE_PER_LANGUAGE]
        remaining = shuffled[SAMPLE_PER_LANGUAGE:]
        for rank, row in enumerate(drawn, start=1):
            sample_rows.append({**row, "sample_rank": rank})
        for rank, row in enumerate(remaining, start=1):
            reserve_rows.append({**row, "reserve_rank": rank})

    return sample_rows, reserve_rows


def build_attrition(attrition_rows: list[dict[str, str]]) -> dict:
    """Build the ATTRITION.json funnel object from attrition_stage rows."""
    by_verdict: dict[str, list[dict]] = {}
    for row in attrition_rows:
        by_verdict.setdefault(row["verdict"], []).append(row)

    total = len(attrition_rows)
    n_no_ci = len(by_verdict.get("no_ci", []))
    n_api_error = len(by_verdict.get("api_error", []))
    n_no_test_workflow = len(by_verdict.get("no_test_workflow", []))

    ci_live_output = total - n_no_ci - n_api_error
    has_test_workflow_output = ci_live_output - n_no_test_workflow

    stages = [
        {
            "stage": "seart_export",
            "filter": "SEART GitHub Search query, Java+Python merged (data/frame/QUERY.md)",
            "input_count": None,
            "output_count": total,
            "removed_count": None,
            "status": "measured",
        },
        {
            "stage": "ci_live",
            "filter": "≥100 GitHub Actions workflow runs in the trailing 90 days (src/harvest/frame.py)",
            "input_count": total,
            "output_count": ci_live_output,
            "removed_count": total - ci_live_output,
            "status": "measured",
        },
        {
            "stage": "has_test_workflow",
            "filter": "≥1 workflow classified as test-intent (src/harvest/frame.py:classify_workflows)",
            "input_count": ci_live_output,
            "output_count": has_test_workflow_output,
            "removed_count": ci_live_output - has_test_workflow_output,
            "status": "measured",
        },
        {
            "stage": "sampled",
            "filter": (
                f"Seeded language-stratified draw of {SAMPLE_PER_LANGUAGE} Java + "
                f"{SAMPLE_PER_LANGUAGE} Python from verdict==kept "
                f"(scripts/sample_frame.py, SEED={SEED})"
            ),
            "input_count": has_test_workflow_output,
            "output_count": 2 * SAMPLE_PER_LANGUAGE,
            "removed_count": has_test_workflow_output - 2 * SAMPLE_PER_LANGUAGE,
            "status": "measured",
        },
    ]
    for stage_name, filter_desc in NOT_YET_MEASURED_STAGES:
        stages.append(
            {
                "stage": stage_name,
                "filter": filter_desc,
                "input_count": None,
                "output_count": None,
                "removed_count": None,
                "status": "not_yet_measured",
            }
        )

    exclusions = [
        {
            "stage": "ci_live",
            "reason": row["verdict"],
            "owner": row["owner"],
            "repo": row["repo"],
            "failing_call": row["failing_call"],
            "status": row["status"],
            "exception_class": row["exception_class"],
        }
        for row in by_verdict.get("api_error", [])
    ]

    return {"seed": SEED, "stages": stages, "exclusions": exclusions}


def _fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    header, repo_rows = read_csv(REPOS_PATH)
    print(f"Read {len(repo_rows)} rows from {REPOS_PATH}")
    if len(repo_rows) != EXPECTED_KEPT_COUNT:
        _fail(
            f"expected exactly {EXPECTED_KEPT_COUNT} kept repos in {REPOS_PATH}, "
            f"found {len(repo_rows)} — the input frame has changed, stopping "
            "rather than sampling a different frame silently"
        )

    sample_rows, reserve_rows = draw_sample(repo_rows, seed=SEED)

    sample_keys = {(r["owner"], r["repo"]) for r in sample_rows}
    reserve_keys = {(r["owner"], r["repo"]) for r in reserve_rows}
    kept_keys = {(r["owner"], r["repo"]) for r in repo_rows}
    if not sample_keys.isdisjoint(reserve_keys):
        _fail("frame_v1 and frame_v1_reserve overlap")
    if sample_keys | reserve_keys != kept_keys:
        _fail("frame_v1 + frame_v1_reserve does not cover the full kept set")
    if len(sample_rows) != 2 * SAMPLE_PER_LANGUAGE:
        _fail(f"expected {2 * SAMPLE_PER_LANGUAGE} sampled repos, got {len(sample_rows)}")

    write_csv(FRAME_V1_PATH, header + ["sample_rank"], sample_rows)
    write_csv(RESERVE_PATH, header + ["reserve_rank"], reserve_rows)
    print(f"Wrote {len(sample_rows)} rows to {FRAME_V1_PATH}")
    print(f"Wrote {len(reserve_rows)} rows to {RESERVE_PATH}")

    _, attrition_rows = read_csv(ATTRITION_STAGE_PATH)
    attrition = build_attrition(attrition_rows)
    ATTRITION_JSON_PATH.write_text(json.dumps(attrition, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {ATTRITION_JSON_PATH}")

    java_sample = sum(1 for r in sample_rows if r["lang"] == "Java")
    python_sample = sum(1 for r in sample_rows if r["lang"] == "Python")
    java_reserve = sum(1 for r in reserve_rows if r["lang"] == "Java")
    python_reserve = sum(1 for r in reserve_rows if r["lang"] == "Python")
    print()
    print("=== Sample summary ===")
    print(f"frame_v1: Java={java_sample} Python={python_sample} total={len(sample_rows)}")
    print(f"reserve:  Java={java_reserve} Python={python_reserve} total={len(reserve_rows)}")


if __name__ == "__main__":
    main()
